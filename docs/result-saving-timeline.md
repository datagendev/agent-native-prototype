# Result Saving Timeline - When Does Data Get Written?

## Simple Timeline: Processing 3 Companies

### Initial State: Empty Database
```
CSV loaded into database:
Row 1: JSX Tool
Row 2: Mayflower
Row 3: item
```

---

## Timeline: Running b2b_only Workflow

```
Time 0:00 - Start workflow
  Action: Load all 3 rows from database

Time 0:01 - Process Row 1 (JSX Tool)
  Node: b2b_classifier runs
  Result: is_b2b = 1, confidence = 0.9
  💾 SAVE TO DATABASE ← Results saved immediately!
  Database Row 1 now has: is_b2b = 1

Time 0:02 - Process Row 2 (Mayflower)
  Node: b2b_classifier runs
  Result: is_b2b = 1, confidence = 0.85
  💾 SAVE TO DATABASE ← Results saved immediately!
  Database Row 2 now has: is_b2b = 1

Time 0:03 - Process Row 3 (item)
  Node: b2b_classifier runs
  Result: is_b2b = 0, confidence = 0.7
  💾 SAVE TO DATABASE ← Results saved immediately!
  Database Row 3 now has: is_b2b = 0

Time 0:04 - Workflow Complete
  ✅ Database has is_b2b column for all 3 rows
  ✅ No need to "commit" or "save" - already done!
```

**Key Point**: Each row is saved RIGHT AFTER it's processed, not at the end!

---

## Timeline: Running founder_linkedin Workflow (With WHERE Filter)

```
Time 0:00 - Start workflow
  Action: Load workflow conditions
  Condition: where = "is_b2b = '1'"

Time 0:01 - Apply WHERE Filter
  SQL: SELECT * FROM leads WHERE is_b2b = '1'
  Result: 2 rows (JSX Tool, Mayflower)
  ⚠️  Row 3 (item) NOT IN LIST - will never be processed

Time 0:02 - Process Row 1 (JSX Tool) - Node 1
  Node: yc_founder runs
  Result: founder_name = "John Doe", founder_linkedin_url = "..."
  💾 SAVE TO DATABASE ← Saved immediately!
  Database Row 1 now has: founder_name = "John Doe"

Time 0:15 - Process Row 1 (JSX Tool) - Node 2
  Node: founder_posts runs
  Result: recent_posts_count = 5, latest_post_text = "..."
  💾 SAVE TO DATABASE ← Saved immediately!
  Database Row 1 now has: recent_posts_count = 5

Time 0:30 - Process Row 1 (JSX Tool) - Node 3
  Node: claude_code_check runs
  Result: uses_claude_code = 1
  💾 SAVE TO DATABASE ← Saved immediately!
  Database Row 1 now has: uses_claude_code = 1

Time 0:31 - Process Row 2 (Mayflower) - Node 1
  Node: yc_founder runs
  Result: founder_name = "Jane Smith"
  💾 SAVE TO DATABASE ← Saved immediately!

Time 0:45 - Process Row 2 (Mayflower) - Node 2
  Node: founder_posts runs
  Result: recent_posts_count = 3
  💾 SAVE TO DATABASE ← Saved immediately!

Time 1:00 - Process Row 2 (Mayflower) - Node 3
  Node: claude_code_check runs
  Result: uses_claude_code = 0
  💾 SAVE TO DATABASE ← Saved immediately!

Time 1:01 - Workflow Complete
  ✅ Row 1: Fully enriched with all 3 nodes
  ✅ Row 2: Fully enriched with all 3 nodes
  ❌ Row 3: NOT TOUCHED (filtered out by WHERE clause)
```

**Key Point**: Row 3 (item) was never processed because the WHERE filter excluded it at Time 0:01!

---

## What This Means for You

### 1. You Can Check Progress Mid-Workflow

While the workflow is running, you can query the database:

```bash
# In another terminal while workflow is running
python -c "
import sqlite3
conn = sqlite3.connect('leads/yc-f25/table.db')
cursor = conn.cursor()
cursor.execute('SELECT name, is_b2b, founder_name FROM leads WHERE founder_name IS NOT NULL')
print('Already enriched:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[2]}')
"
```

Output (while still running):
```
Already enriched:
  JSX Tool: John Doe
  (Mayflower is being processed right now...)
```

### 2. You Can Stop and Resume

If the workflow crashes or you stop it (Ctrl+C):

```bash
# First run - processed 50 companies then crashed
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
# Processed: 50/100 companies

# Resume - picks up where it left off
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --skip-existing
# Processes: remaining 50 companies
```

The `--skip-existing` flag skips rows that already have data.

### 3. You Can Chain Workflows

Because results are saved immediately, the next workflow can use them:

```bash
# Workflow 1: Classify all companies (saves is_b2b column)
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only

# Workflow 2: Enrich B2B companies (uses is_b2b column for filtering)
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin

# Workflow 3: Deep analysis on specific companies (uses all previous columns)
python scripts/graph_enrich.py --lead yc-f25 --workflow deep_analysis
```

Each workflow builds on the previous one because data is persistent in the database.

---

## Database State Over Time

### After CSV Import
```sql
SELECT * FROM leads;
```
```
_id  name        location  description
1    JSX Tool    SF        JavaScript framework
2    Mayflower   SF        AI assistant
3    item        SF        Shopping app
```

### After b2b_only Workflow (Immediate Saves)
```sql
SELECT * FROM leads;
```
```
_id  name        is_b2b  b2b_confidence
1    JSX Tool    1       0.9            ← Saved at Time 0:01
2    Mayflower   1       0.85           ← Saved at Time 0:02
3    item        0       0.7            ← Saved at Time 0:03
```

### After founder_linkedin Workflow (Immediate Saves, Filtered)
```sql
SELECT * FROM leads;
```
```
_id  name        is_b2b  founder_name   founder_linkedin_url
1    JSX Tool    1       John Doe       linkedin.com/...     ← Saved at Time 0:02-0:30
2    Mayflower   1       Jane Smith     linkedin.com/...     ← Saved at Time 0:31-1:00
3    item        0       NULL           NULL                 ← NOT PROCESSED
```

Row 3 has NULL founder data because:
1. WHERE filter excluded it (is_b2b = '0')
2. Workflow never processed it
3. No saves happened for Row 3

---

## Key Differences: With vs Without WHERE Filter

### Without WHERE Filter (Full Workflow)
```
Process Row 1 → Save → Process Row 2 → Save → Process Row 3 → Save
Result: All 3 rows enriched
```

### With WHERE Filter (Conditional Workflow)
```
Apply Filter → Process Row 1 → Save → Process Row 2 → Save
                                       ↑
                           Row 3 excluded by filter, never processed
Result: Only 2 rows enriched
```

---

## Summary: When Are Results Saved?

✅ **After each node completes** (not at the end of workflow)
✅ **For each row individually** (not batch saved)
✅ **Before the next node runs** (nodes see updated data)
✅ **Even if workflow crashes** (completed rows are saved)

❌ **NOT saved all at once at the end**
❌ **NOT saved to CSV until you export**
❌ **NOT saved in memory only**

The database is updated **incrementally and immediately** as work completes!
