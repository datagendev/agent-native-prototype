# Complete Workflow Progression: From Raw CSV to Enriched Data

## Starting Point: Just a Raw Lead List

You have a simple CSV file:

**File**: `leads/yc-f25/table.csv`
```csv
name,location,description,yc_url
JSX Tool,San Francisco,JavaScript framework,https://yc.com/jsx
Mayflower,San Francisco,AI assistant,https://yc.com/mayflower
item,San Francisco,Shopping app,https://yc.com/item
... (153 more companies)
```

**No enrichment columns yet** - just basic info.

---

## System Initialization: CSV → Database

When you run ANY workflow for the first time:

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
```

### Step 1: Load CSV into Database

**File**: `scripts/graph_enrich.py` (around line 1340)

```python
# Initialize database
db, err = init_lead_db(lead_name, csv_path)
```

This does:
1. Creates `leads/yc-f25/table.db` (SQLite database)
2. Imports ALL CSV rows
3. Creates columns from CSV headers: `name`, `location`, `description`, `yc_url`

**Database after init**:
```sql
SELECT * FROM leads;
```
```
_id  name        location          description           yc_url
1    JSX Tool    San Francisco     JavaScript framework  https://yc.com/jsx
2    Mayflower   San Francisco     AI assistant          https://yc.com/mayflower
3    item        San Francisco     Shopping app          https://yc.com/item
```

Only CSV columns exist - **no enrichment columns yet**.

---

## Scenario 1: You Run Workflow with WHERE Condition FIRST

### What You Run
```bash
# Oops! Running founder_linkedin workflow FIRST
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

### What the System Does

**Step 1: Load workflow definition**
```python
# System reads: leads/yc-f25/graph/workflows.yaml
workflow = {
    "description": "Find founder and analyze LinkedIn activity",
    "conditions": {"where": "is_b2b = '1'"},  # ← Needs is_b2b column!
    "nodes": ["yc_founder", "founder_posts"]
}
```

**Step 2: Get ALL rows from database**
```python
rows = db.get_rows()  # Gets all 156 companies
```

**Step 3: Try to apply WHERE filter**
```python
# graph_enrich.py line 1379
filtered_rows, filter_err = db.filter_rows("is_b2b = '1'")

# In db.filter_rows() - line 333
query = "SELECT * FROM leads WHERE is_b2b = '1'"
cursor.execute(query)
# SQLite raises: OperationalError: no such column: is_b2b
```

**Step 4: Catch error and fallback**
```python
# graph_enrich.py lines 1380-1386
if filter_err:
    print(f"Warning: Failed to apply WHERE filter: {filter_err}")
    print("Proceeding with all rows")
    # Uses original 'rows' list (all 156 companies)
else:
    rows = filtered_rows
```

### What You See

```
Warning: Failed to apply WHERE filter 'is_b2b = '1'': no such column: is_b2b
Proceeding with all rows
╭──────────────────────────────────╮
│ WORKFLOW BATCH: founder_linkedin │
╰──────────────────────────────────╯
Lead Table: table.db (156 rows)  ← Processes ALL rows!
Nodes: 2

  Running workflow ━━━━━━━━━━━━━━━━━ 100% * 2:30:00
```

**Result**:
- ⚠️  WHERE filter fails (no `is_b2b` column)
- ⚠️  System processes ALL 156 companies
- 💰 Expensive! Does LinkedIn lookups for everyone
- ⚠️  No filtering applied

**Database after**:
```
_id  name        yc_url              founder_name   founder_linkedin_url
1    JSX Tool    https://yc.com/jsx  John Doe       linkedin.com/...
2    Mayflower   https://yc.com/...  Jane Smith     linkedin.com/...
3    item        https://yc.com/...  Bob Jones      linkedin.com/...
... (all 156 rows enriched)
```

---

## Scenario 2: Correct Workflow Progression

### Step 1: Run Classification Workflow FIRST

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
```

**Workflow definition** (no WHERE condition):
```yaml
b2b_only:
  description: "Classify ALL companies as B2B or B2C"
  # NO conditions - processes all rows
  nodes:
    - b2b_classifier
  connections:
    - from: $input.description
      to: b2b_classifier.description
```

**What happens**:
1. Load all 156 rows from database
2. No WHERE filter (no conditions block)
3. Process ALL 156 companies through `b2b_classifier` node
4. Save results immediately after each company

**Processing timeline**:
```
Time 0:01 - Classify Company 1
            Result: is_b2b=1, b2b_confidence=0.9
            💾 SAVE to database (adds is_b2b column)

Time 0:02 - Classify Company 2
            Result: is_b2b=1, b2b_confidence=0.85
            💾 SAVE to database

Time 0:03 - Classify Company 3
            Result: is_b2b=0, b2b_confidence=0.7
            💾 SAVE to database

... (continues for all 156 companies)
```

**Database after Step 1**:
```sql
SELECT * FROM leads;
```
```
_id  name        description           is_b2b  b2b_confidence
1    JSX Tool    JavaScript framework  1       0.9
2    Mayflower   AI assistant          1       0.85
3    item        Shopping app          0       0.7
```

Now you have the `is_b2b` column populated! ✅

---

### Step 2: Run Filtered Enrichment Workflow

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

**Workflow definition** (WITH WHERE condition):
```yaml
founder_linkedin:
  description: "Enrich ONLY B2B companies"
  conditions:
    where: "is_b2b = '1'"  # ← Now this column exists!
  nodes:
    - yc_founder
    - founder_posts
```

**What happens**:

**Step 1: Get ALL rows**
```python
rows = db.get_rows()  # Gets all 156 companies
```

**Step 2: Apply WHERE filter**
```python
filtered_rows, filter_err = db.filter_rows("is_b2b = '1'")

# In db.filter_rows()
query = "SELECT * FROM leads WHERE is_b2b = '1'"
cursor.execute(query)
# SQLite returns: 45 rows (only B2B companies)
```

**Step 3: Use filtered rows**
```python
if filter_err:
    # No error this time!
else:
    rows = filtered_rows  # ← Now has 45 companies, not 156!
    print(f"Applied WHERE filter: is_b2b = '1' (45 rows matched)")
```

**Step 4: Process ONLY filtered rows**
```python
for row in rows:  # Loops 45 times, not 156!
    for node in nodes:
        result, err = node.run(row)
        db.update_row(row["_id"], result)  # Save immediately
```

### What You See

```
Applied WHERE filter: is_b2b = '1' (45 rows matched)
╭──────────────────────────────────╮
│ WORKFLOW BATCH: founder_linkedin │
╰──────────────────────────────────╯
Lead Table: table.db (45 rows)  ← Only B2B companies!
Nodes: 2

  Running workflow ━━━━━━━━━━━━━━━━━ 100% * 0:37:30
```

**Database after Step 2**:
```sql
SELECT * FROM leads;
```
```
_id  name        is_b2b  founder_name   founder_linkedin_url        recent_posts_count
1    JSX Tool    1       John Doe       linkedin.com/in/johndoe     5
2    Mayflower   1       Jane Smith     linkedin.com/in/janesmith   3
3    item        0       NULL           NULL                        NULL  ← Not enriched!
```

Only B2B companies (45 out of 156) got founder data! ✅

---

## How the System Manages Workflow Continuation

### 1. Database is Persistent

**Between workflow runs**:
- Database file: `leads/yc-f25/table.db` persists
- All results saved: `is_b2b`, `founder_name`, etc.
- Next workflow can read previous results

### 2. Each Workflow Builds on Previous Data

```
Workflow 1 (b2b_only):
  Input: name, description (from CSV)
  Output: is_b2b, b2b_confidence
  Database now has: name, description, is_b2b ✅

Workflow 2 (founder_linkedin):
  Input: name, yc_url (from CSV) + is_b2b (from Workflow 1)
  Filter: WHERE is_b2b = '1'  ← Uses data from Workflow 1!
  Output: founder_name, founder_linkedin_url
  Database now has: name, description, is_b2b, founder_name ✅

Workflow 3 (deep_analysis):
  Input: founder_linkedin_url (from Workflow 2)
  Filter: WHERE uses_claude_code = '1'
  Output: engagement_metrics
  Database now has: everything from previous workflows ✅
```

### 3. Results Save Immediately

**No need to "commit" or "finalize"**:
- After each node completes → SAVE to database
- Next workflow sees updated data immediately
- Can stop/resume workflows anytime

### 4. WHERE Filters Use Existing Columns

**WHERE conditions reference database columns**:
```yaml
conditions:
  where: "is_b2b = '1'"  # Must exist in database
```

If column doesn't exist → Error → Fallback to all rows

---

## Complete Workflow Progression Example

### Starting: Raw CSV

```csv
name,description
JSX Tool,JavaScript framework
Mayflower,AI assistant
item,Shopping app
```

### Progression Timeline

```
┌─────────────────────────────────────────────────────────────┐
│ Initial State: CSV loaded into database                     │
│ Columns: name, description                                  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Workflow 1: b2b_only                                        │
│ - No WHERE filter (processes all 156 rows)                  │
│ - Adds: is_b2b, b2b_confidence                              │
│ - Duration: 2 minutes                                       │
│ - Cost: $2                                                  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
            Database now has: is_b2b column ✅
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Workflow 2: founder_linkedin                                │
│ - WHERE filter: is_b2b = '1' (processes 45 rows)            │
│ - Adds: founder_name, founder_linkedin_url                  │
│ - Duration: 30 minutes                                      │
│ - Cost: $45 (saved $111 by filtering!)                     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
         Database now has: founder data for B2B ✅
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Workflow 3: claude_code_check                               │
│ - WHERE filter: founder_linkedin_url IS NOT NULL            │
│ - Adds: uses_claude_code, claude_code_mentions              │
│ - Duration: 20 minutes                                      │
│ - Cost: $30                                                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Final State: Fully enriched database                        │
│ Columns: name, description, is_b2b, founder_name,           │
│          founder_linkedin_url, uses_claude_code             │
│ Export: leads/yc-f25/enriched.csv                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Insights: How System Manages Continuation

### 1. No Manual "Pipeline" Management

You don't need to:
- ❌ Track which workflows ran
- ❌ Remember what columns exist
- ❌ Manually pass data between workflows
- ❌ Write glue code to connect workflows

System handles it automatically:
- ✅ Database persists all data
- ✅ Each workflow reads/writes to same database
- ✅ WHERE filters use existing columns
- ✅ Missing columns cause graceful fallback

### 2. Workflow Order Matters for Filtering

**Dependencies**:
```
b2b_only → Creates is_b2b column
    ↓
founder_linkedin → Uses is_b2b for filtering
    ↓
deep_analysis → Uses founder_linkedin_url for filtering
```

If you run out of order:
- WHERE filter fails (column missing)
- System processes ALL rows (expensive!)
- But doesn't crash

### 3. Incremental Processing

You can run workflows incrementally:
```bash
# Day 1: Classify companies
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only

# Day 2: Enrich B2B companies
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin

# Day 3: Deep analysis
python scripts/graph_enrich.py --lead yc-f25 --workflow deep_analysis
```

Each workflow builds on previous results in the database.

### 4. Resume Support

If a workflow crashes:
```bash
# First run - crashed after 20 companies
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin

# Resume - skip already completed
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --skip-existing
```

System checks database for existing data and skips those rows.

---

## Summary: System Management

**Q: How does the system manage workflow continuation?**

**A: Through a persistent SQLite database:**

1. **Database is source of truth** - all results stored here
2. **Each workflow adds columns** - results accumulate
3. **WHERE filters use existing columns** - later workflows filter on earlier results
4. **Results save immediately** - no need to "commit"
5. **Graceful fallback** - missing columns cause warnings, not crashes
6. **Manual ordering** - you run workflows in sequence

**Simple rule**: Run classification workflows first, then filtered enrichment workflows second!

---

## Complete Example Commands

```bash
# Step 1: Load CSV and classify (no filtering)
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
# Database now has: is_b2b column

# Step 2: Enrich B2B companies (filtered)
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
# Database now has: founder_name, founder_linkedin_url (B2B only)

# Step 3: Check Claude Code usage (filtered)
python scripts/graph_enrich.py --lead yc-f25 --workflow claude_code_focused
# Database now has: uses_claude_code (B2B with LinkedIn only)

# Step 4: Export final results
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --output final.csv
# Creates: final.csv with all enrichment columns
```

Done! The system manages continuation through database persistence and WHERE filter conditions.
