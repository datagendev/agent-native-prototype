# Command Reference

## graph_validate.py

Validate graph YAML files before running.

```bash
# List available leads
python3 scripts/graph_validate.py --list

# Validate a lead's graph
python3 scripts/graph_validate.py --lead {name}

# Show warnings
python3 scripts/graph_validate.py --lead {name} --verbose

# Validate specific workflow
python3 scripts/graph_validate.py --lead {name} --workflow {workflow}
```

**Checks:**
- YAML syntax
- References (instances -> types, workflows -> instances)
- Connections (valid nodes and fields)
- Outputs match what nodes produce
- Required parameters provided

---

## graph_enrich.py

Main enrichment executor.

### Basic Usage

```bash
# List workflows
python3 scripts/graph_enrich.py --lead {name} --list

# Preview (first N rows)
python3 scripts/graph_enrich.py --lead {name} --workflow {workflow} --preview --limit 3

# Run full enrichment
python3 scripts/graph_enrich.py --lead {name} --workflow {workflow}
```

### All Options

| Flag | Description | Default |
|------|-------------|---------|
| `--lead NAME` | Lead directory name (required) | - |
| `--graph NODE` | Run single node | - |
| `--workflow NAME` | Run workflow | - |
| `--preview` | Preview mode (no full run) | false |
| `--limit N` | Preview row count | 10 |
| `--parallel N` | Worker threads | 5 |
| `--output PATH` | Custom output CSV path | auto |
| `--config JSON` | Config override | {} |
| `--overwrite` | Overwrite existing values | false |
| `--skip-existing` | Skip computed rows | true |
| `--cache` | Use node cache | true |
| `--use-csv` | Legacy CSV-only mode | false |

### Examples

```bash
# Preview 5 rows
python3 scripts/graph_enrich.py --lead prospects --workflow basic --preview --limit 5

# Run with more workers
python3 scripts/graph_enrich.py --lead prospects --workflow basic --parallel 10

# Custom output path
python3 scripts/graph_enrich.py --lead prospects --workflow basic --output exports/final.csv

# Override config
python3 scripts/graph_enrich.py --lead prospects --workflow keywords \
  --config '{"keywords": ["AI"], "output_prefix": "ai"}'

# Force recompute all rows
python3 scripts/graph_enrich.py --lead prospects --workflow basic --overwrite
```

## Table Viewer

Interactive web viewer for lead data. Reads from both directories:
- `leads/` - SQLite databases (displayed as "name (SQLite)")
- `lead-list/` - All CSV files

```bash
# Kill any existing viewer on port
lsof -ti:3002 | xargs kill 2>/dev/null || true

# Start viewer (run as background task)
~/.bun/bin/bun scripts/viewer/server.ts --port 3002 &

# Open browser
open http://localhost:3002

# Stop viewer when done
lsof -ti:3002 | xargs kill 2>/dev/null || true
```

**Troubleshooting:**
- Port in use: Run the kill command first
- No files shown: Check `leads/*/table.db` or `lead-list/*.csv` exist

## SQLite Operations

Direct database queries.

```bash
# Open SQLite CLI
sqlite3 leads/{name}/table.db

# View rows
sqlite3 leads/{name}/table.db "SELECT * FROM leads LIMIT 5"

# Check status counts
sqlite3 leads/{name}/table.db "SELECT _status, COUNT(*) FROM leads GROUP BY _status"

# View failed rows
sqlite3 leads/{name}/table.db "SELECT _id, linkedin_url, _error FROM leads WHERE _status='failed'"

# View execution history
sqlite3 leads/{name}/table.db "SELECT * FROM executions ORDER BY started_at DESC"

# View columns
sqlite3 leads/{name}/table.db "SELECT column_name, source FROM columns"
```

## Discovery Commands

Find available capabilities.

```bash
# List primitives
ls scripts/primitives/

# List integrations
ls scripts/integrations/

# Search DataGen tools (in Python)
mcp__datagen__searchTools(query="linkedin enrichment")
```

## Database Reset

```bash
# Reset database (re-import from CSV)
rm leads/{name}/table.db
python3 scripts/graph_enrich.py --lead {name} --workflow basic
```
