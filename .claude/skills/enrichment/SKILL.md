---
name: enrich
description: Enrich leads from CSV or database using graph-based workflows
---

# Skill: Lead Enrichment

Execute lead enrichment workflows using SQLite database backend.

## When to Use

- User wants to enrich leads from CSV or existing lead list
- Needs durable, resumable enrichment with database tracking

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

Based on user's selection:

1. Check if workflow already exists:
   ```bash
   python3 scripts/graph_enrich.py --lead {name} --list
   ```

2. If nodes need to be created, **delegate to enrichment-node-creator agent**.

### Creating Nodes with Agent

For **single node**:
```
Task(subagent_type="enrichment-node-creator", prompt="Create a keyword_mentions node for scanning LinkedIn posts for 'claude code' mentions. Lead: {name}")
```

For **multiple nodes in parallel** (spawn agents concurrently in a single message):
```
Task(subagent_type="enrichment-node-creator", prompt="Create profile_enrichment node for {name}")
Task(subagent_type="enrichment-node-creator", prompt="Create keyword_mentions node for Claude mentions in {name}")
Task(subagent_type="enrichment-node-creator", prompt="Create find_executive node for CEO lookup in {name}")
```

The agent will:
- Create node type definition in `node_types.yaml`
- Create instance in `instances.yaml`
- Implement Python class in `nodes/`
- Register in `nodes/__init__.py`

See [examples/node_templates.md](examples/node_templates.md) for patterns.

3. Once nodes exist, compose workflow in `workflows.yaml`:
   - Reference nodes from instances
   - Define connections between nodes
   - See [examples/workflow_examples.md](examples/workflow_examples.md)

4. Validate the graph:
   ```bash
   python3 scripts/graph_validate.py --lead {name}
   python3 scripts/graph_validate.py --lead {name} --verbose  # Show warnings
   python3 scripts/graph_validate.py --lead {name} --workflow {workflow}  # Specific workflow
   ```

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

After preview completes:

1. **Show summary first:**
   ```bash
   sqlite3 leads/{name}/table.db "SELECT _status, COUNT(*) FROM leads GROUP BY _status"
   ```

2. **Launch table viewer:**
   ```bash
   # Kill any existing viewer, start new one, open browser
   lsof -ti:3002 | xargs kill 2>/dev/null || true
   ~/.bun/bin/bun scripts/viewer/server.ts --port 3002 &
   open http://localhost:3002
   ```

   The viewer reads from both:
   - `leads/` - SQLite databases (shows as "name (SQLite)")
   - `lead-list/` - CSV files

3. **STOP and ask user** with `AskUserQuestion`:
   - "Preview complete. Proceed with full enrichment?"
   - Options: "Yes, run full batch" / "Adjust and re-preview" / "Cancel"

**Do NOT proceed without explicit user confirmation.**

4. **Stop viewer when done:**
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
