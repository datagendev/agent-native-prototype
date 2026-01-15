---
name: enrich
description: Enrich leads from CSV or database using graph-based workflows
---

# Skill: Lead Enrichment

Execute lead enrichment workflows using SQLite database backend.

## When to Use

- User wants to enrich leads from CSV or existing lead list
- Needs durable, resumable enrichment with database tracking

---

## Getting Up to Speed Protocol

**IMPORTANT**: Before starting any enrichment work, check for existing progress.

A PreToolUse hook automatically injects progress context when this skill runs.
If you see "=== Active Enrichment Context ===" in the output, READ IT FIRST.

### Manual Check (if hook didn't run)

```bash
# Check for progress files
ls leads/*/enrichment-progress.txt 2>/dev/null
ls leads/*/node-status.json 2>/dev/null

# Read progress if exists
cat leads/{name}/enrichment-progress.txt
cat leads/{name}/node-status.json
```

### Before Continuing Work

1. Read the progress log to understand current state
2. Run validation to check for broken state:
   ```bash
   python3 scripts/graph_validate.py --lead {name}
   ```
3. Fix any issues before introducing new changes
4. Only then continue with the next task

---

## Progress Tracking Files

### `enrichment-progress.txt` - Session Log

Create/update after each phase:

```
## Session 2026-01-14 10:00
Phase: 2 - Configure Workflow
- User intent: Find Claude Code users in YC batch
- Scouted 3 nodes needed: profile, company_info, keyword_posts
- Created node: company_info (delegated to enrichment-node-creator)
- Next: Create keyword_posts node

## Session 2026-01-14 11:00
Phase: 2 - Configure Workflow (continued)
- Created node: keyword_posts
- Composed workflow: claude_user_detection
- Next: Preview with 5 rows
```

### `node-status.json` - Node Tracking

Track node readiness (only modify `ready` field):

```json
{
  "user_intent": "Find Claude Code users in YC batch",
  "nodes": [
    {"name": "profile_enrichment", "purpose": "LinkedIn profile data", "ready": true},
    {"name": "company_info", "purpose": "Company lookup", "ready": false},
    {"name": "keyword_posts", "purpose": "Post keyword search", "ready": false}
  ]
}
```

---

## Architecture

```
leads/{lead_name}/
  table.csv          # Source data (git-tracked)
  table.db           # SQLite database (auto-created)
  graph/
    node_types.yaml  # Base node definitions (library)
    instances.yaml   # Pre-configured nodes (reusable configs)
    workflows.yaml   # Workflow compositions with connections
    schema.md        # Schema documentation
    loader.py        # Graph loader
    nodes/           # Python node implementations
```

### Three-Level Hierarchy

```
Node Types     ->    Node Instances    ->    Workflow Nodes
(library)            (configured)            (composition)

Defines WHAT         Configures HOW          Defines WHEN/WHERE
a node can do        a node behaves          nodes connect
```

---

## Phase 0: Select Lead List

1. Find existing lead lists:
   ```bash
   python3 scripts/graph_validate.py --list
   ```

2. Or import a new CSV:
   ```bash
   mkdir -p leads/{name}/graph/nodes
   cp path/to/file.csv leads/{name}/table.csv
   ```

3. Show available columns:
   ```bash
   head -1 leads/{name}/table.csv
   ```

---

## Phase 1: Ask What to Enrich (INTERACTIVE)

**Ask the user first before exploring options.**

Use `AskUserQuestion`:
- "What do you want to enrich these leads with?"
- Let user describe in their own words

**Then** search for matching capabilities based on their answer:

```bash
# Local primitives
ls scripts/primitives/

# Integrations
ls scripts/integrations/
```

For external tools, use `mcp__datagen__searchTools`.

Present matching options and confirm with user.

---

## Phase 2: Configure Workflow

### Step 1: Scout Required Nodes

**Before creating anything, scout ALL nodes needed first.**

Based on user's intent, analyze and list all nodes:

| # | Node Purpose | MCP Tool | Exists? | Status |
|---|--------------|----------|---------|--------|
| 1 | LinkedIn profile | mcp_Proxycurl_get_profile | Check node_types.yaml | ? |
| 2 | Company info | mcp_Proxycurl_get_company | Check node_types.yaml | ? |
| 3 | Keyword search | mcp_Proxycurl_search_posts | Check node_types.yaml | ? |

Check existing nodes:
```bash
python3 scripts/graph_enrich.py --lead {name} --list
```

**Create `node-status.json`** with all required nodes:
```bash
cat > leads/{name}/node-status.json << 'EOF'
{
  "user_intent": "{user's enrichment request}",
  "nodes": [
    {"name": "profile_enrichment", "purpose": "LinkedIn profile data", "ready": true},
    {"name": "company_info", "purpose": "Company lookup", "ready": false}
  ]
}
EOF
```

### Step 2: Create Missing Nodes (ONE AT A TIME)

**IMPORTANT**: Create ONE node at a time. Verify before creating next.

For each node where `ready: false`:

1. **Delegate to enrichment-node-creator**:
   ```
   Task(subagent_type="enrichment-node-creator", prompt="Create {node_name} node for {purpose}. Lead: {name}. MCP tool: {tool_name}")
   ```

2. **Verify creation**:
   ```bash
   ls leads/{name}/graph/nodes/{node_name}.py
   python3 scripts/graph_validate.py --lead {name}
   ```

3. **Update node-status.json**: Set `ready: true` for this node

4. **Update enrichment-progress.txt**: Log what was created

5. **Repeat** for next node

### Step 3: Compose Workflow

Once ALL nodes are ready (`ready: true`):

1. Compose workflow in `workflows.yaml`:
   - Reference nodes from instances
   - Define connections between nodes
   - See [examples/workflow_examples.md](examples/workflow_examples.md)

2. Validate the complete graph:
   ```bash
   python3 scripts/graph_validate.py --lead {name}
   python3 scripts/graph_validate.py --lead {name} --verbose  # Show warnings
   python3 scripts/graph_validate.py --lead {name} --workflow {workflow}  # Specific workflow
   ```

3. Update progress log with workflow completion

---

## Phase 3: Preview Configuration (INTERACTIVE)

**Ask user before running preview:**

Use `AskUserQuestion`:
- "How many rows to preview?" (3 / 5 / 10)

Run preview:
```bash
python3 scripts/graph_enrich.py --lead {name} --workflow {workflow} --preview --limit {N}
```

---

## Phase 4: Review Results (MANDATORY STOP)

After preview completes, **ALWAYS show what columns were added and results:**

### Step 1: Show Column Changes

Display a clear summary of what the workflow added:

```
## Preview Results for {workflow}

### Columns Added by This Workflow:
| New Column | Type | Source Node | Description |
|------------|------|-------------|-------------|
| is_b2b | boolean | B2BClassifier | True if B2B company |
| b2b_confidence | number | B2BClassifier | 0.0-1.0 confidence |
| classification_reason | string | B2BClassifier | Why classified |

### Pipeline Summary:
1. B2BClassifier
   - Reads: description, industry
   - Outputs: is_b2b, b2b_confidence, classification_reason
   - Method: AI classification using company description
```

### Step 2: Show Preview Statistics

```bash
sqlite3 leads/{name}/table.db "SELECT _status, COUNT(*) FROM leads GROUP BY _status"
```

### Step 3: Show Sample Results

Display actual enriched values from preview rows:

```bash
sqlite3 leads/{name}/table.db "SELECT name, {new_columns} FROM leads WHERE _status='completed' LIMIT 5" -header -column
```

### Step 4: Launch Table Viewer (Optional)

```bash
# Kill any existing viewer, start new one, open browser
lsof -ti:3002 | xargs kill 2>/dev/null || true
~/.bun/bin/bun scripts/viewer/server.ts --port 3002 &
open http://localhost:3002
```

The viewer reads from both:
- `leads/` - SQLite databases (shows as "name (SQLite)")
- `lead-list/` - CSV files

### Step 5: Confirm with User

**STOP and ask user** with `AskUserQuestion`:
- "Preview added {N} new columns to {M} rows. Proceed with full enrichment?"
- Options: "Yes, run full batch" / "Adjust and re-preview" / "Cancel"

**Do NOT proceed without explicit user confirmation.**

### Step 6: Stop Viewer When Done

```bash
lsof -ti:3002 | xargs kill 2>/dev/null || true
```

---

## Phase 5: Full Run

Only after user confirmation:

```bash
python3 scripts/graph_enrich.py --lead {name} --workflow {workflow}
```

Output: `leads/{name}/table_enriched_{workflow}_{timestamp}.csv`

---

## Links

- [Node Templates](examples/node_templates.md)
- [Workflow Examples](examples/workflow_examples.md)
- [Command Reference](reference/commands.md)
- [Troubleshooting](reference/troubleshooting.md)
