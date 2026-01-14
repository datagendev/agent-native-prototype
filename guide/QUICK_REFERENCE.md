# Lead Enrichment Quick Reference

## File Structure
```
leads/{lead-name}/
├── table.csv              ← Input (git-tracked)
├── table.db               ← Database (auto-created, git-ignored)
└── graph/
    ├── graph.yaml         ← Workflow definition
    └── nodes/*.py         ← Enrichment logic
```

## Common Commands

### Setup & Discovery
```bash
# List available workflows
python3 scripts/graph_enrich.py --lead my-leads --list

# Show graph definition
python3 scripts/graph_enrich.py --lead my-leads --show-graph

# Validate workflow
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --validate
```

### Testing
```bash
# Preview first 3 rows (reads CSV, no database)
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --preview --limit 3

# Preview specific node with custom config
python3 scripts/graph_enrich.py --lead my-leads \
  --graph keyword_mentions \
  --config '{"keywords": ["datagen"]}' \
  --preview
```

### Running Enrichment

**Default (SQLite mode):**
```bash
# Run workflow (creates table.db on first run, auto-imports CSV)
python3 scripts/graph_enrich.py --lead my-leads --workflow basic

# Run single node
python3 scripts/graph_enrich.py --lead my-leads --graph profile_enrichment

# Custom output path
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --output my_export.csv

# More parallel workers (default: 5)
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --parallel 10
```

**Legacy (CSV-only mode):**
```bash
# Process CSV without database
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --use-csv
```

## Database Operations

### Inspect Database
```bash
# Enter SQLite CLI
sqlite3 leads/my-leads/table.db

# Common queries:
sqlite> SELECT * FROM leads LIMIT 5;                    # View first 5 rows
sqlite> SELECT _status, COUNT(*) FROM leads GROUP BY _status;  # Count by status
sqlite> SELECT * FROM executions ORDER BY started_at DESC;     # View run history
sqlite> SELECT column_name, source FROM columns;               # View all columns
sqlite> .schema leads                                          # View table schema
sqlite> .quit                                                  # Exit
```

### Reset Database
```bash
# Delete and re-import from CSV
rm leads/my-leads/table.db
python3 scripts/graph_enrich.py --lead my-leads --workflow basic
```

## Python API

### Direct Database Access
```python
from db import LeadDB
from pathlib import Path

# Connect to database
db = LeadDB(Path("leads/my-leads/table.db"))
db.connect()
db.init_schema()

# Get all rows
rows, err = db.get_rows()
if err:
    print(f"Error: {err}")
else:
    print(f"Got {len(rows)} rows")

# Get only failed rows
failed_rows, err = db.get_rows(status="failed")

# Update a row
updates = {"new_column": "new_value"}
err = db.update_row(row_id=1, updates=updates, status="completed")

# Get stats
stats, err = db.get_stats()
print(stats)
# {'total_rows': 100, 'status_counts': {'completed': 95, 'failed': 5}, ...}

# Export to CSV (excludes internal _columns)
export_rows, err = db.export_to_csv()
```

### Load Workflows Programmatically
```python
from pathlib import Path
import sys

# Add lead directory to path
sys.path.insert(0, str(Path("leads").absolute()))

# Import graph module
from leads.my_leads.graph import load_workflow, load_node

# Load workflow
workflow_nodes = load_workflow("basic")  # Returns list of node objects

# Load single node
node = load_node("profile_enrichment", config={"custom": "param"})

# Execute node
row = {"linkedin_url": "https://linkedin.com/in/user"}
result, error = node.run(row)
if error:
    print(f"Error: {error}")
else:
    print(f"Result: {result}")
    # Result: {'headline': '...', 'current_company': '...', ...}
```

## Data Flow

```
1. CSV Input (table.csv)
   ↓
2. Auto-import to SQLite (first run only)
   ↓
3. Load from database
   ↓
4. Process with workflow nodes
   ↓
5. Update database per-row (transactional)
   ↓
6. Export to timestamped CSV
```

## Key Concepts

### Modes
- **SQLite (default)**: Durable, tracked, resumable
- **CSV-only (`--use-csv`)**: Legacy, stateless, one-shot

### Workflow Structure
- **Primitive**: Atomic capability (web_research, extract_structured)
- **Node**: Composed workflow with declared I/O (ProfileEnrichment, FindCEO)
- **Workflow**: Named sequence of nodes (basic, full_enrichment)

### Database Columns
- **Internal** (`_id`, `_status`, `_error`): System columns, not exported
- **Input** (from CSV): `linkedin_url`, `company_domain`, etc.
- **Output** (from enrichment): `headline`, `current_company`, etc.

### Status Values
- `pending`: Not yet processed
- `processing`: Currently running
- `completed`: Successfully enriched
- `failed`: Enrichment error

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CSV not found | Ensure `table.csv` exists in lead directory |
| No module named 'yaml' | Install: `pip install pyyaml` |
| Database locked | Close other connections to `.db` file |
| CSV changes not reflected | Delete `.db` file to trigger re-import |
| Preview shows no rows | Check CSV has data with headers |
| Workflow not found | Verify name in `graph.yaml` workflows section |

## Environment

### Required
- Python 3.8+
- SQLite3 (built-in)

### Optional
- `rich` - Enhanced terminal UI (`pip install rich`)
- `pyyaml` - YAML parsing (`pip install pyyaml`)

## .gitignore Patterns

Already configured in `linkedin-outreach/.gitignore`:
```gitignore
# Exclude databases
leads/**/table.db
leads/**/table.db-shm
leads/**/table.db-wal

# Exclude enriched CSVs
leads/**/table_enriched_*.csv

# Keep source CSVs
!leads/**/table.csv
```

## Best Practices

✅ **DO:**
- Commit `table.csv` (source data)
- Commit `graph.yaml` and `nodes/*.py` (workflow)
- Use preview mode before full run
- Query database for status during enrichment
- Export to CSV for external systems

❌ **DON'T:**
- Commit `.db` files (git-ignored)
- Commit enriched CSVs (git-ignored)
- Manually edit database (use Python API)
- Run multiple enrichments concurrently on same database

## Examples

### Example 1: Basic Setup
```bash
# 1. Create directory structure
mkdir -p leads/my-leads/graph/nodes

# 2. Add CSV
echo "linkedin_url" > leads/my-leads/table.csv
echo "https://linkedin.com/in/user1" >> leads/my-leads/table.csv

# 3. Copy example graph
cp -r leads/example-leads/graph/* leads/my-leads/graph/

# 4. Run enrichment
python3 scripts/graph_enrich.py --lead my-leads --workflow profile_only --preview
```

### Example 2: Custom Workflow
```yaml
# leads/my-leads/graph/graph.yaml
workflows:
  my_custom:
    description: Custom enrichment workflow
    nodes:
      - profile_enrichment
      - node: keyword_mentions
        config:
          keywords: ["AI", "ML", "automation"]
          output_prefix: "ai_topics"
      - find_ceo
```

```bash
# Run custom workflow
python3 scripts/graph_enrich.py --lead my-leads --workflow my_custom
```

### Example 3: Retry Failed Rows
```python
from db import LeadDB
from pathlib import Path

# Load database
db = LeadDB(Path("leads/my-leads/table.db"))
db.connect()

# Get failed rows
failed, err = db.get_rows(status="failed")
print(f"Found {len(failed)} failed rows")

# Reset status to retry
for row in failed:
    db.update_row(row["_id"], {}, status="pending", error=None)

print("Reset failed rows to pending - ready to retry")
```

## Getting Help

- **Full Documentation**: [ENRICHMENT_WORKFLOW.md](ENRICHMENT_WORKFLOW.md)
- **Graph Schema**: [leads/example-leads/graph/graph_schema.md](leads/example-leads/graph/graph_schema.md)
- **Enrichment Skill**: [.claude/skills/enrichment/SKILL.md](.claude/skills/enrichment/SKILL.md)
