# Troubleshooting

## Common Issues

| Issue | Solution |
|-------|----------|
| CSV not found | Ensure `table.csv` exists in `leads/{name}/` |
| No module named 'yaml' | `pip install pyyaml` |
| Database locked | Close other SQLite connections |
| CSV changes not reflected | Delete `.db` file to trigger re-import |
| Preview shows no rows | Check CSV has data rows (not just headers) |
| Workflow not found | Verify name in `graph.yaml` workflows section |
| Node not found | Check node is registered in `graph.yaml` nodes section |
| Import errors | Verify `sys.path.insert` in node file |

## Retrying Failed Rows

```bash
# View failed rows
sqlite3 leads/{name}/table.db \
  "SELECT _id, linkedin_url, _error FROM leads WHERE _status='failed'"

# Reset failed rows to pending
sqlite3 leads/{name}/table.db \
  "UPDATE leads SET _status='pending', _error=NULL WHERE _status='failed'"

# Re-run workflow
python3 scripts/graph_enrich.py --lead {name} --workflow {workflow}
```

## Database Queries

```bash
# Check enrichment status
sqlite3 leads/{name}/table.db \
  "SELECT _status, COUNT(*) FROM leads GROUP BY _status"

# View recent executions
sqlite3 leads/{name}/table.db \
  "SELECT workflow_name, success_count, failed_count, started_at FROM executions ORDER BY started_at DESC LIMIT 5"

# Check column sources
sqlite3 leads/{name}/table.db \
  "SELECT column_name, source FROM columns"
```

## Reset Database

If data is corrupted or you want a fresh start:

```bash
# Delete database
rm leads/{name}/table.db

# Re-run (will import from CSV)
python3 scripts/graph_enrich.py --lead {name} --workflow basic
```

## Debugging Nodes

Add print statements to nodes for debugging:

```python
def run(self, row: dict) -> tuple[dict, str]:
    url = row.get("linkedin_url", "")
    print(f"Processing: {url}")  # Debug output

    result, err = fetch_linkedin_profile(url)
    print(f"Result: {result}, Error: {err}")  # Debug output

    # ...
```

Run preview to see debug output:

```bash
python3 scripts/graph_enrich.py --lead {name} --workflow basic --preview --limit 1
```
