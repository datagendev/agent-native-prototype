#!/usr/bin/env bun
/**
 * Enrichment Data Viewer Server
 *
 * Bun server with React frontend for enriched CSV visualization.
 * 
 * Features:
 * - API to list available CSV files
 * - API to lazy load CSV data
 * - On-the-fly bundling of React frontend
 */

import { readdir, stat } from "fs/promises";
import { join, resolve, basename } from "path";

// Configuration
const args = Bun.argv.slice(2);
const portArgIdx = args.indexOf("--port");
const PORT = parseInt(
  (portArgIdx !== -1 && args[portArgIdx + 1])
    ? args[portArgIdx + 1]
    : (process.env.PORT || "3001")
);
const LEAD_LIST_DIR = resolve(__dirname, "../../lead-list");
const LEADS_DIR = resolve(__dirname, "../../leads");
const PUBLIC_DIR = resolve(__dirname, "./public");
const SRC_DIR = resolve(__dirname, "./src");

// File source tracking
type FileSource = "lead-list" | "leads";
interface FileInfo {
  name: string;
  displayName: string;
  size: string;
  mtime: Date;
  source: FileSource;
  path: string; // Full path for loading
}

// ------------------------------------------------------------------
// 1. Build Frontend
// ------------------------------------------------------------------
console.log("📦 Bundling frontend...");
const buildResult = await Bun.build({
  entrypoints: [join(SRC_DIR, "index.tsx")],
  outdir: join(PUBLIC_DIR, "build"),
  minify: false, // Keep it readable for debug, enable if needed
  sourcemap: "inline",
});

if (!buildResult.success) {
  console.error("❌ Build failed!");
  console.error(buildResult.logs);
  process.exit(1);
}
console.log("✅ Build successful!");

// ------------------------------------------------------------------
// 2. Data Logic
// ------------------------------------------------------------------

// Parse SQLite database
async function parseSQLite(dbPath: string): Promise<Array<Record<string, string>>> {
  try {
    // Use bun:sqlite with proper error handling
    const { Database } = await import("bun:sqlite");
    const db = new Database(dbPath);
    try {
      const rows = db.query("SELECT * FROM leads").all() as Record<string, any>[];
      // Convert all values to strings for consistency with CSV
      return rows.map(row => {
        const result: Record<string, string> = {};
        for (const [key, value] of Object.entries(row)) {
          result[key] = value === null ? "" : String(value);
        }
        return result;
      });
    } finally {
      db.close();
    }
  } catch (e) {
    console.error(`Failed to open SQLite: ${dbPath}`, e);
    throw new Error(`Cannot open database: ${dbPath}`);
  }
}

// Parse CSV
async function parseCSV(filePath: string): Promise<Array<Record<string, string>>> {
  const file = Bun.file(filePath);
  if (!(await file.exists())) throw new Error("File not found");

  const content = await file.text();
  const lines = content.trim().split("\n");
  // Handle CSV parsing better (basic regex for quoted strings)
  // Note: This is a simple parser. For production, use a library like csv-parser.
  const parseLine = (line: string) => {
    const result = [];
    let current = "";
    let inQuote = false;
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        inQuote = !inQuote;
      } else if (char === ',' && !inQuote) {
        result.push(current.trim().replace(/^"|"$/g, ""));
        current = "";
      } else {
        current += char;
      }
    }
    result.push(current.trim().replace(/^"|"$/g, ""));
    return result;
  };

  const headers = parseLine(lines[0]);
  return lines.slice(1).map(line => {
    const values = parseLine(line);
    const row: Record<string, string> = {};
    headers.forEach((header, i) => {
      row[header] = values[i] || "";
    });
    return row;
  });
}

// Save CSV
async function saveCSV(filePath: string, data: Array<Record<string, string>>): Promise<void> {
  if (data.length === 0) return;
  const headers = Object.keys(data[0]);

  const escape = (val: string) => {
    if (val === null || val === undefined) return "";
    const str = String(val);
    if (str.includes(",") || str.includes("\n") || str.includes('"')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  const csvContent = [
    headers.join(","),
    ...data.map(row => headers.map(h => escape(row[h])).join(","))
  ].join("\n");

  await Bun.write(filePath, csvContent);
}

// Save SQLite
async function saveSQLite(dbPath: string, data: Array<Record<string, string>>): Promise<void> {
  if (data.length === 0) return;

  const { Database } = await import("bun:sqlite");
  const db = new Database(dbPath);

  // infer columns from first row
  const columns = Object.keys(data[0]);

  const transaction = db.transaction(() => {
    // 1. Drop existing table to ensure schema matches new data
    //    We assume the main table is always named 'leads' based on parseSQLite
    db.run("DROP TABLE IF EXISTS leads");

    // 2. Create table
    //    We treat everything as TEXT to match the Viewer's string-based nature
    const colDefs = columns.map(c => `"${c}" TEXT`).join(", ");
    db.run(`CREATE TABLE leads (${colDefs})`);

    // 3. Insert data
    const placeholders = columns.map(() => "?").join(", ");
    const insert = db.prepare(`INSERT INTO leads (${columns.map(c => `"${c}"`).join(", ")}) VALUES (${placeholders})`);

    for (const row of data) {
      const values = columns.map(col => row[col]);
      insert.run(...values);
    }
  });

  try {
    transaction();
  } finally {
    db.close();
  }
}

// Analyze workflow (same logic as before)
function analyzeWorkflow(data: Array<Record<string, string>>) {
  const headers = Object.keys(data[0] || {});
  const originalCols = ["name", "email", "linkedin_url", "company", "source"];
  const enrichedCols = headers.filter(h => !originalCols.includes(h));

  const integrations: Record<string, any> = {};
  const integrationSignatures: Record<string, string[]> = {
    linkedin_profile: ["headline", "current_company", "location", "follower_count"],
    linkedin_post_activity: ["posts_last_30_days", "posts_last_90_days", "total_posts"],
    linkedin_claude_mentions: ["claude_mentions_count", "claude_mention_urls"],
    heyreach_engagement: ["heyreach_conversations_count", "heyreach_messages_sent"],
    heyreach_campaigns: ["heyreach_campaign_count", "heyreach_campaign_names"],
    heyreach_network: ["heyreach_is_connection", "heyreach_connection_degree"],
  };

  Object.entries(integrationSignatures).forEach(([name, signature]) => {
    const matchedCols = signature.filter(col => headers.includes(col));
    if (matchedCols.length > 0) {
      let populated = 0;
      data.forEach(row => {
        const hasData = matchedCols.some(col => {
          const val = row[col];
          return val && val.trim() !== "" && val !== "0" && val !== "False";
        });
        if (hasData) populated++;
      });
      integrations[name] = {
        columns: matchedCols,
        populated,
        empty: data.length - populated,
        total: data.length,
        successRate: ((populated / data.length) * 100).toFixed(1),
        category: name.startsWith("linkedin_") ? "LinkedIn" :
                  name.startsWith("heyreach_") ? "HeyReach" : "Other"
      };
    }
  });

  return {
    totalRows: data.length,
    totalColumns: headers.length,
    originalColumns: originalCols.length,
    enrichedColumns: enrichedCols.length,
    integrations
  };
}

// ------------------------------------------------------------------
// 3. Server
// ------------------------------------------------------------------

Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);

    // API: List Files (from both lead-list/ and leads/)
    if (url.pathname === "/api/files") {
      try {
        const fileList: FileInfo[] = [];

        // 1. Scan lead-list/ for all CSVs
        try {
          const leadListFiles = await readdir(LEAD_LIST_DIR);
          for (const name of leadListFiles) {
            if (name.endsWith(".csv")) {
              const filePath = join(LEAD_LIST_DIR, name);
              const stats = await stat(filePath);
              fileList.push({
                name: `lead-list/${name}`,
                displayName: name,
                size: (stats.size / 1024).toFixed(1) + " KB",
                mtime: stats.mtime,
                source: "lead-list",
                path: filePath
              });
            }
          }
        } catch (e) {
          console.log("No lead-list/ directory or empty");
        }

        // 2. Scan leads/ for SQLite databases
        try {
          const leadsDirs = await readdir(LEADS_DIR);
          for (const dir of leadsDirs) {
            const dbPath = join(LEADS_DIR, dir, "table.db");
            const dbFile = Bun.file(dbPath);
            if (await dbFile.exists()) {
              const stats = await stat(dbPath);
              fileList.push({
                name: `leads/${dir}/table.db`,
                displayName: `${dir} (SQLite)`,
                size: (stats.size / 1024).toFixed(1) + " KB",
                mtime: stats.mtime,
                source: "leads",
                path: dbPath
              });
            }
          }
        } catch (e) {
          console.log("No leads/ directory or empty");
        }

        fileList.sort((a, b) => b.mtime.getTime() - a.mtime.getTime());
        return Response.json(fileList);
      } catch (e) {
        return Response.json({ error: "Failed to list files" }, { status: 500 });
      }
    }

    // API: Get Data (supports both CSV and SQLite)
    if (url.pathname === "/api/data") {
      const fileName = url.searchParams.get("file");
      if (!fileName) return Response.json({ error: "Missing file param" }, { status: 400 });

      try {
        let data: Array<Record<string, string>>;

        // Handle leads/ SQLite databases
        if (fileName.startsWith("leads/") && fileName.endsWith(".db")) {
          const dbPath = join(LEADS_DIR, fileName.replace("leads/", ""));
          data = await parseSQLite(dbPath);
        }
        // Handle lead-list/ CSVs
        else if (fileName.startsWith("lead-list/") && fileName.endsWith(".csv")) {
          const csvPath = join(LEAD_LIST_DIR, fileName.replace("lead-list/", ""));
          data = await parseCSV(csvPath);
        }
        else {
          return Response.json({ error: "Invalid file path" }, { status: 400 });
        }

        return Response.json(data);
      } catch (e) {
        console.error("Error loading data:", e);
        return Response.json({ error: "File not found or invalid" }, { status: 404 });
      }
    }

    // API: Get Workflow (supports both CSV and SQLite)
    if (url.pathname === "/api/workflow") {
      const fileName = url.searchParams.get("file");
      if (!fileName) return Response.json({ error: "Missing file param" }, { status: 400 });

      try {
        let data: Array<Record<string, string>>;

        if (fileName.startsWith("leads/") && fileName.endsWith(".db")) {
          const dbPath = join(LEADS_DIR, fileName.replace("leads/", ""));
          data = await parseSQLite(dbPath);
        } else if (fileName.startsWith("lead-list/") && fileName.endsWith(".csv")) {
          const csvPath = join(LEAD_LIST_DIR, fileName.replace("lead-list/", ""));
          data = await parseCSV(csvPath);
        } else {
          return Response.json({ error: "Invalid file path" }, { status: 400 });
        }

        const workflow = analyzeWorkflow(data);
        return Response.json(workflow);
      } catch (e) {
        return Response.json({ error: "File not found or invalid" }, { status: 404 });
      }
    }

    // API: Save Data (CSV only for now)
    if (url.pathname === "/api/save" && req.method === "POST") {
      try {
        const body = await req.json();
        const { file, data } = body;

        if (!file || !data || !Array.isArray(data)) {
          return Response.json({ error: "Invalid payload" }, { status: 400 });
        }

        if (file.startsWith("lead-list/") && file.endsWith(".csv")) {
          const csvPath = join(LEAD_LIST_DIR, file.replace("lead-list/", ""));
          await saveCSV(csvPath, data);
          return Response.json({ success: true });
        } else if (file.startsWith("leads/") && file.endsWith(".db")) {
          const dbPath = join(LEADS_DIR, file.replace("leads/", ""));
          await saveSQLite(dbPath, data);
          return Response.json({ success: true });
        } else {
          return Response.json({ error: "Only CSV and SQLite (.db) saving is currently supported" }, { status: 400 });
        }
      } catch (e) {
        console.error("Save failed", e);
        return Response.json({ error: "Save failed" }, { status: 500 });
      }
    }

    // Serve Built JS
    // The build output is likely 'index.js' inside 'public/build' because entrypoint was 'index.tsx'
    if (url.pathname.startsWith("/build/")) {
      const filePath = join(PUBLIC_DIR, url.pathname);
      return new Response(Bun.file(filePath));
    }

    // Serve Static Assets from Public (e.g. styles, or if index.html requests other things)
    if (url.pathname !== "/" && !url.pathname.startsWith("/api")) {
       const publicFile = Bun.file(join(PUBLIC_DIR, url.pathname));
       if (await publicFile.exists()) return new Response(publicFile);
    }

    // Serve Index HTML (SPA Fallback)
    const indexFile = Bun.file(join(PUBLIC_DIR, "index.html"));
    let html = await indexFile.text();
    
    // HACK: Replace the source to point to the built file
    // Original: src="/src/index.tsx"
    // New: src="/build/index.js"
    html = html.replace('src="/src/index.tsx"', 'src="/build/index.js"');
    
    return new Response(html, {
      headers: { "Content-Type": "text/html" },
    });
  },
});

console.log(`✅ Server running at http://localhost:${PORT}`);
console.log(`\n📁 Scanning directories:`);
console.log(`   - lead-list/  (CSV files)`);
console.log(`   - leads/      (SQLite databases)`);
console.log(`\n🔗 Open: http://localhost:${PORT}`);