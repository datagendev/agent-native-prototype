# Lead Enrichment Workflow with SQLite

## Overview

The lead enrichment system uses a **SQLite database** as the primary storage backend, with CSV files for initial input and exports. This provides durability, transactional updates, and queryable state while keeping the workflow simple.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Lead Enrichment Flow                         │
└─────────────────────────────────────────────────────────────────┘

  CSV Input                SQLite Database           CSV Export
  (Git-tracked)            (Git-ignored)            (Git-ignored)
      │                           │                        │
      ▼                           ▼                        ▼
┌──────────┐            ┌─────────────────┐      ┌─────────────┐
│table.csv │ ─Import──▶ │   table.db      │ ─┐   │enriched.csv │
│          │    (once)  │                 │  │   │             │
│linkedin_ │            │ • leads table   │  │   │linkedin_url │
│url, etc. │            │ • executions    │  └──▶│headline     │
└──────────┘            │ • row tracking  │       │company      │
                        │ • dynamic cols  │       │followers    │
                        └─────────────────┘       └─────────────┘
                               │ ▲
                               │ │
                    ┌──────────┘ └──────────┐
                    │                       │
                    ▼                       │
            ┌────────────────┐    ┌────────────────┐
            │  Enrichment    │    │  Update DB     │
            │  (Primitives   │───▶│  (per-row,     │
            │   + Nodes)     │    │   transactional)│
            └────────────────┘    └────────────────┘
```

## Directory Structure

```
leads/{lead-name}/
├── table.csv              # Source CSV (git-tracked)
├── table.db               # SQLite database (git-ignored, auto-created)
├── table.db-shm           # SQLite shared memory (git-ignored)
├── table.db-wal           # Write-ahead log (git-ignored)
├── table_enriched_*.csv   # Timestamped exports (git-ignored)
└── graph/
    ├── graph.yaml         # Workflow definition
    ├── __init__.py        # Node loader
    └── nodes/
        ├── __init__.py
        ├── profile_enrichment.py
        ├── keyword_mentions.py
        └── find_ceo.py
```

## Complete Workflow

### Phase 0: Discovery (Before Setup)

**CRITICAL**: Before creating any workflow, explore available capabilities and identify gaps.

**Step 0.1: Review Available Primitives**

Primitives are atomic capabilities (raw, multi-purpose tools). Check what's available:

```bash
# List all primitives
ls linkedin-outreach/scripts/primitives/

# Available primitives (as of now):
# - web_research.py       - Generic web search and research
# - extract_structured.py - Extract structured data from text using schema
# - linkedin_profile.py   - Fetch LinkedIn profile data
# - linkedin_posts.py     - Fetch LinkedIn posts
# - filter_by.py          - Filter arrays by keywords
# - aggregate.py          - Aggregate filtered results
```

**Review primitive signatures:**
```python
# Example: web_research
web_research(query: str) -> ({"result": str}, error)

# Example: extract_structured
extract_structured(text: str, schema: dict, context: str) -> ({"extracted": dict}, error)

# Example: linkedin_profile
linkedin_profile(linkedin_url: str) -> ({"headline": str, "current_company": str, ...}, error)
```

**Step 0.2: Review Available Integrations**

Integrations are tool providers (API wrappers). Check what's available:

```bash
# List integrations
ls linkedin-outreach/scripts/integrations/

# Available integrations:
# - linkedin_profile.py   - LinkedIn profile API
# - datagen tools         - Via DataGen SDK (check with searchTools)
```

**Search DataGen tools:**
```python
from datagen_client import DataGenClient

client = DataGenClient()
# Search for tools
tools = client.search_tools(query="linkedin enrichment")
tools = client.search_tools(query="company data")
tools = client.search_tools(query="email finder")
```

**Step 0.3: Identify Gaps**

Based on your enrichment needs, identify what's **missing**:

**Example gap analysis:**
```
Needs:
✅ LinkedIn profile data - AVAILABLE (linkedin_profile primitive)
✅ LinkedIn posts - AVAILABLE (linkedin_posts primitive)
✅ Web research - AVAILABLE (web_research primitive)
❌ Company firmographic data - NOT AVAILABLE → Need to create
❌ Email finder - NOT AVAILABLE → Check DataGen or create integration
❌ Social media presence - NOT AVAILABLE → Create if needed
```

**Step 0.4: Create Missing Primitives/Integrations**

If capabilities are missing, create them **before** building workflows:

**Option A: Create new primitive** (generic, reusable)
```python
# linkedin-outreach/scripts/primitives/company_data.py
from primitives.base import Primitive

class CompanyData(Primitive):
    """Fetch company firmographic data from API."""

    name = "company_data"
    input_schema = {
        "domain": {"type": "string", "description": "Company domain"}
    }
    output_schema = {
        "company_name": {"type": "string"},
        "industry": {"type": "string"},
        "employee_count": {"type": "integer"}
    }

    def run(self, **inputs) -> tuple[dict, str]:
        domain = inputs["domain"]
        # Call API, return data
        return result, error
```

**Option B: Use DataGen custom tool**
```bash
# Search for suitable tool
python -c "from datagen_client import DataGenClient; \
  client = DataGenClient(); \
  tools = client.search_tools('company data'); \
  print(tools)"

# Use tool in primitive
```

**Option C: Create integration wrapper**
```python
# linkedin-outreach/scripts/integrations/clearbit.py
# Wrap external API as integration
```

**Step 0.5: Document Your Plan**

Before implementing, document what you'll use:
```yaml
# Enrichment plan for my-leads

Input columns:
- linkedin_url
- company_domain

Enrichment needs:
1. LinkedIn profile data
   → Primitive: linkedin_profile ✅

2. LinkedIn posts mentioning "AI"
   → Primitives: linkedin_posts + filter_by ✅

3. Company firmographic data
   → Need to create: company_data primitive ❌
   → Action: Use DataGen Clearbit tool

4. Find CEO contact
   → Primitives: web_research + extract_structured ✅
   → Will create node: find_ceo (composes primitives)
```

### Phase 1: Setup (One-time)

**Step 1.1: Create Lead Table Directory**
```bash
mkdir -p leads/my-leads/graph/nodes
```

**Step 1.2: Add Source CSV**
```bash
# Create or copy CSV with input data
cat > leads/my-leads/table.csv << EOF
linkedin_url,company_domain,notes
https://linkedin.com/in/user1,company1.com,Prospect A
https://linkedin.com/in/user2,company2.com,Prospect B
EOF
```

This CSV is **git-tracked** (the source of truth for input data).

**Step 1.3: Define Enrichment Workflow** (After completing Phase 0 discovery)

Create `leads/my-leads/graph/graph.yaml`:
```yaml
name: my-leads
description: My lead enrichment table
source: table.csv

columns:
  inputs:
    linkedin_url:
      type: string
      description: LinkedIn profile URL
  outputs:
    headline:
      type: string
      source: profile_enrichment
      description: LinkedIn headline

nodes:
  profile_enrichment:
    description: Fetch LinkedIn profile data
    file: nodes/profile_enrichment.py
    class: ProfileEnrichment
    input_cols: [linkedin_url]
    output_cols: [headline, current_company, location, follower_count]

workflows:
  basic:
    description: Basic profile enrichment
    nodes:
      - profile_enrichment
```

**Step 1.4: Implement Nodes** (if not using existing ones)

Nodes are in `graph/nodes/*.py` and extend the `Graph` base class.

### Phase 2: First Enrichment Run

**Step 2.1: Run Enrichment Command**
```bash
cd linkedin-outreach
python3 scripts/graph_enrich.py --lead my-leads --workflow basic
```

**What happens:**
1. ✅ Checks if `leads/my-leads/table.db` exists
2. ✅ **Database doesn't exist** → Creates `table.db`
3. ✅ **Auto-imports CSV** → Copies all rows from `table.csv` to database
   ```
   Imported 2 rows from CSV to database
   ```
4. ✅ Loads workflow nodes from `graph.yaml`
5. ✅ Processes each row in parallel:
   - Calls enrichment node(s)
   - Updates database **immediately per row** (transactional)
   - Tracks status: `pending` → `processing` → `completed`/`failed`
6. ✅ Exports enriched data to timestamped CSV:
   ```
   leads/my-leads/table_enriched_basic_20260111_133045.csv
   ```

**Database created:**
- `table.db` (40KB+) with 4 tables: leads, columns, executions, row_executions
- All data persists for future runs

### Phase 3: Subsequent Runs

**Step 3.1: Add More Rows to CSV**
```bash
# Add new prospects to table.csv
echo "https://linkedin.com/in/user3,company3.com,Prospect C" >> leads/my-leads/table.csv
```

**Step 3.2: Re-import CSV**

Since the database already exists, you need to manually trigger re-import:
```bash
# Option A: Delete database and re-import
rm leads/my-leads/table.db
python3 scripts/graph_enrich.py --lead my-leads --workflow basic

# Option B: Use CSV mode (processes CSV without database)
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --use-csv
```

> **Note**: In the current implementation, SQLite doesn't auto-merge new CSV rows. If you add rows to CSV, delete the `.db` file to trigger fresh import.

**Step 3.3: Run Different Workflows**
```bash
# Run different enrichment workflow
python3 scripts/graph_enrich.py --lead my-leads --workflow full_enrichment

# Run single node
python3 scripts/graph_enrich.py --lead my-leads --graph profile_enrichment
```

**What happens:**
1. ✅ Database already exists → **Skips CSV import**
2. ✅ Loads rows from database (only processes `pending` or `failed` rows by default)
3. ✅ Updates database per row
4. ✅ Exports to new timestamped CSV

### Phase 4: Incremental Updates

**Scenario**: Some rows failed enrichment, you want to retry them.

**Step 4.1: Query Database to See Status**
```bash
# Use SQLite CLI to inspect
sqlite3 leads/my-leads/table.db "SELECT _id, _status, linkedin_url FROM leads;"
```

**Step 4.2: Retry Failed Rows**
```python
# Custom script to retry only failed rows
from db import LeadDB
from pathlib import Path

db = LeadDB(Path("leads/my-leads/table.db"))
db.connect()

# Get only failed rows
failed_rows, err = db.get_rows(status="failed")
print(f"Found {len(failed_rows)} failed rows")

# Re-process them...
```

**Step 4.3: Add New Columns**

The database schema is **dynamic**. When you run a new workflow with different nodes, new columns are automatically added:

```bash
# First run: adds headline, company, location, follower_count
python3 scripts/graph_enrich.py --lead my-leads --workflow basic

# Second run: adds claude_mentions_count, claude_mention_urls, etc.
python3 scripts/graph_enrich.py --lead my-leads --workflow claude_mentions
```

Each enrichment adds columns without destroying existing data.

### Phase 5: Export & Analysis

**Step 5.1: Export Current State**
```bash
# Run any workflow to trigger export
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --output my_export.csv
```

Or programmatically:
```python
from db import LeadDB
from pathlib import Path

db = LeadDB(Path("leads/my-leads/table.db"))
db.connect()
db.init_schema()

# Export all rows (excludes internal _id, _status columns)
rows, err = db.export_to_csv()

# Now rows is a list of dicts with only data columns
```

**Step 5.2: Query Database Directly**
```bash
# Check enrichment stats
sqlite3 leads/my-leads/table.db << EOF
SELECT
  _status,
  COUNT(*) as count
FROM leads
GROUP BY _status;
EOF
```

**Step 5.3: View Execution History**
```bash
sqlite3 leads/my-leads/table.db << EOF
SELECT
  workflow_name,
  started_at,
  success_count,
  failed_count,
  output_path
FROM executions
ORDER BY started_at DESC;
EOF
```

## Modes: SQLite vs CSV

### Default Mode: SQLite (Recommended)

```bash
# Uses database for storage and tracking
python3 scripts/graph_enrich.py --lead my-leads --workflow basic
```

**Benefits:**
- ✅ Durable: Data persists between runs
- ✅ Transactional: Updates are atomic
- ✅ Incremental: Can resume failed enrichments
- ✅ Queryable: Use SQL to inspect state
- ✅ Tracked: Execution history preserved
- ✅ No git bloat: Database excluded from version control

### Legacy Mode: CSV-only

```bash
# Uses only CSV files (no database)
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --use-csv
```

**Behavior:**
- Loads entire CSV into memory
- Processes all rows
- Saves to new timestamped CSV
- No state persistence
- No execution tracking

**Use when:**
- Testing workflows without database overhead
- One-time batch processing
- Exporting to different systems

## Preview Mode

Test your workflow on first N rows without database:

```bash
# Preview first 3 rows
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --preview --limit 3

# Preview shows:
# - Input values for each row
# - Output from each node in workflow
# - Success/failure status per row
```

Preview mode **always reads from CSV** (not database), so it's safe for testing.

## Common Commands

### List Available Workflows
```bash
python3 scripts/graph_enrich.py --lead my-leads --list
```

### Show Graph Definition
```bash
python3 scripts/graph_enrich.py --lead my-leads --show-graph
```

### Validate Workflow
```bash
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --validate
```

### Run with Custom Config
```bash
python3 scripts/graph_enrich.py --lead my-leads \
  --graph keyword_mentions \
  --config '{"keywords": ["datagen"], "output_prefix": "datagen"}'
```

### Control Parallelism
```bash
# Use 10 parallel workers (default: 5)
python3 scripts/graph_enrich.py --lead my-leads --workflow basic --parallel 10
```

## Database Schema

### Tables

**1. `leads` - Main data table**
```sql
CREATE TABLE leads (
    _id INTEGER PRIMARY KEY,           -- Auto-increment row ID
    _source_row_index INTEGER,         -- Original CSV row number
    _created_at TEXT,                  -- When row was imported
    _updated_at TEXT,                  -- Last enrichment time
    _status TEXT DEFAULT 'pending',    -- pending/processing/completed/failed
    _error TEXT,                       -- Error message if failed
    -- Dynamic columns added here:
    linkedin_url TEXT,                 -- From CSV
    company_domain TEXT,               -- From CSV
    headline TEXT,                     -- From enrichment
    current_company TEXT,              -- From enrichment
    ...
);
```

**2. `columns` - Column metadata**
```sql
CREATE TABLE columns (
    column_name TEXT PRIMARY KEY,
    column_type TEXT,                  -- text/integer/real/blob
    source TEXT,                       -- 'csv' or node name
    created_at TEXT,
    description TEXT
);
```

**3. `executions` - Workflow history**
```sql
CREATE TABLE executions (
    execution_id INTEGER PRIMARY KEY,
    workflow_type TEXT,                -- 'graph' or 'workflow'
    workflow_name TEXT,
    started_at TEXT,
    completed_at TEXT,
    total_rows INTEGER,
    success_count INTEGER,
    failed_count INTEGER,
    config TEXT,                       -- JSON config
    output_path TEXT                   -- Exported CSV path
);
```

**4. `row_executions` - Per-row tracking**
```sql
CREATE TABLE row_executions (
    id INTEGER PRIMARY KEY,
    execution_id INTEGER,              -- Links to executions table
    row_id INTEGER,                    -- Links to leads table
    node_name TEXT,                    -- Which node ran
    started_at TEXT,
    completed_at TEXT,
    status TEXT,                       -- success/failed/partial
    error TEXT
);
```

## Error Handling

All operations use **error-first pattern**:
```python
result, error = function()
if error:
    # Handle error
    return
# Use result
```

**Common errors:**

1. **CSV not found**: Ensure `table.csv` exists in lead directory
2. **Node not found**: Check graph.yaml and node files exist
3. **Column missing**: Node expects input column not in CSV or database
4. **Database locked**: Close other connections to the database

## Best Practices

### 1. Version Control
- ✅ **Commit**: `table.csv` (input data)
- ✅ **Commit**: `graph.yaml` (workflow definition)
- ✅ **Commit**: `nodes/*.py` (enrichment logic)
- ❌ **Don't commit**: `table.db`, `table_enriched_*.csv` (git-ignored)

### 2. Workflow Design
- Start with **simple workflows** (1-2 nodes)
- Use **preview mode** to test before full run
- **Validate** workflows before executing

### 3. Data Management
- Keep original `table.csv` clean and minimal
- Use database for all enrichment state
- Export to CSV for external systems

### 4. Error Recovery
- Check `_status` column in database
- Retry failed rows with custom scripts
- Review `executions` table for run history

### 5. Performance
- Use `--parallel` for faster processing (default: 5 workers)
- Monitor with `sqlite3` for real-time status
- Export only when needed (exports create new CSV files)

## Troubleshooting

### Database is empty after import
**Check:** Ensure CSV has data and headers
```bash
head -3 leads/my-leads/table.csv
```

### Enrichment always processes all rows
**Issue:** Current implementation doesn't filter by status
**Workaround:** Use custom script to process only `pending` rows

### CSV changes not reflected in database
**Solution:** Delete database to trigger re-import
```bash
rm leads/my-leads/table.db
python3 scripts/graph_enrich.py --lead my-leads --workflow basic
```

### Database file is large
**Check size:**
```bash
ls -lh leads/my-leads/table.db
```
**Solution:** SQLite is efficient, but you can vacuum:
```bash
sqlite3 leads/my-leads/table.db "VACUUM;"
```

## Next Steps

1. **Create your first lead table** with CSV + graph.yaml
2. **Run preview** to test workflow: `--preview --limit 3`
3. **Run full enrichment** with SQLite backend
4. **Query database** to inspect results
5. **Export to CSV** for external use

The database provides durability and auditability while keeping the workflow simple and git-friendly.
