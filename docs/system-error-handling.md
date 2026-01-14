# System Error Handling - Does It Handle Wrong Order?

## Your Question

> "Does our system handle it?" (running workflows in wrong order)

## Answer: YES, with Graceful Fallback

Our system **DOES handle it** - it won't crash, but the behavior depends on the situation:

---

## Scenario 1: Column Doesn't Exist Yet

### What Happens
You run the filtered workflow BEFORE creating the column:

```bash
# Oops! Running founder_linkedin first (is_b2b column doesn't exist)
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

### System Response

**Step 1: Load WHERE condition**
```
conditions = {"where": "is_b2b = '1'"}
```

**Step 2: Try to apply filter**
```python
# In db.filter_rows()
query = "SELECT * FROM leads WHERE is_b2b = '1'"
cursor.execute(query)
# SQLite raises: OperationalError: no such column: is_b2b
```

**Step 3: Catch error and fallback**
```python
# In graph_enrich.py (lines 1380-1386)
if filter_err:
    print("Warning: Failed to apply WHERE filter 'is_b2b = 1': no such column")
    print("Proceeding with all rows")
    # Uses original 'rows' list (all 156 companies)
```

### User Experience
```
Warning: Failed to apply WHERE filter 'is_b2b = '1'': filter_rows error: no such column: is_b2b
Proceeding with all rows
╭──────────────────────────────────╮
│ WORKFLOW BATCH: founder_linkedin │
╰──────────────────────────────────╯
Lead Table: table.db (156 rows)  ← Processes ALL rows!
```

**Result**:
- ⚠️  Shows warning
- ✅ Doesn't crash
- ⚠️  Processes ALL 156 companies (expensive!)
- ❌ Doesn't filter to B2B only

---

## Scenario 2: Column Exists But All NULL

### What Happens
You imported CSV, but haven't run classification yet:

```bash
# is_b2b column exists but all values are NULL
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

### System Response

**Step 1: Apply filter**
```sql
SELECT * FROM leads WHERE is_b2b = '1'
-- Result: 0 rows (no rows have is_b2b = '1', all are NULL)
```

**Step 2: No error, but empty result**
```python
# In graph_enrich.py (line 1388)
rows = filtered_rows  # filtered_rows is empty list []
total = len(rows)  # total = 0
```

### User Experience
```
Applied WHERE filter: is_b2b = '1' (0 rows matched)
╭──────────────────────────────────╮
│ WORKFLOW BATCH: founder_linkedin │
╰──────────────────────────────────╯
Lead Table: table.db (0 rows)  ← Nothing to process!
Completed: 0 / 0 rows
```

**Result**:
- ✅ No error
- ✅ Doesn't crash
- ✅ Doesn't waste money processing rows
- ❌ But also doesn't enrich anything

---

## Scenario 3: Column Partially Populated

### What Happens
Some companies classified, some not:

```bash
# 45 companies have is_b2b = '1'
# 111 companies have is_b2b = NULL or '0'
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

### System Response

**Filter result**:
```sql
SELECT * FROM leads WHERE is_b2b = '1'
-- Result: 45 rows
```

### User Experience
```
Applied WHERE filter: is_b2b = '1' (45 rows matched)
╭──────────────────────────────────╮
│ WORKFLOW BATCH: founder_linkedin │
╰──────────────────────────────────╯
Lead Table: table.db (45 rows)
Nodes: 3
```

**Result**:
- ✅ Works perfectly!
- ✅ Processes only B2B companies
- ✅ Skips unclassified companies

---

## Code That Handles This

### Error Catching (scripts/graph_enrich.py lines 1376-1392)

```python
# Apply workflow conditions (WHERE clause filtering)
if conditions and "where" in conditions:
    where_clause = conditions["where"]

    # Try to filter
    filtered_rows, filter_err = db.filter_rows(where_clause)

    if filter_err:  # ← ERROR HANDLING
        # Show warning but don't crash
        console.print(f"[yellow]Warning: Failed to apply WHERE filter '{where_clause}': {filter_err}[/yellow]")
        console.print("[yellow]Proceeding with all rows[/yellow]")
        # 'rows' stays as original list (all companies)
    else:
        # Success - use filtered rows
        rows = filtered_rows
        console.print(f"[cyan]Applied WHERE filter: {where_clause} ({len(rows)} rows matched)[/cyan]")
```

### SQLite Error Handling (scripts/db.py lines 329-340)

```python
def filter_rows(self, where_clause: str) -> tuple[list[dict], str]:
    try:
        cursor = self.conn.cursor()
        query = f"SELECT * FROM leads WHERE {where_clause}"
        cursor.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]
        return rows, ""  # Success
    except Exception as e:  # ← CATCHES SQLite errors
        return [], f"filter_rows error: {e}"  # Return error message
```

---

## Summary Table

| Situation | System Behavior | User Impact |
|-----------|----------------|-------------|
| **Column doesn't exist** | Shows warning, processes ALL rows | ⚠️  Expensive! Processes everything |
| **Column exists, all NULL** | No error, processes 0 rows | ✅ Safe, but nothing happens |
| **Column partially populated** | No error, processes matching rows | ✅ Perfect! Works as intended |
| **Invalid SQL syntax** | Shows warning, processes ALL rows | ⚠️  Expensive! Processes everything |

---

## Does the System Prevent Wrong Order?

### ❌ No Automatic Prevention

The system does NOT:
- Check if required columns exist before starting
- Automatically run prerequisite workflows
- Force you to run workflows in order
- Stop you from running workflows in wrong order

### ✅ But It Handles Errors Gracefully

The system DOES:
- Catch SQL errors from missing columns
- Show clear warning messages
- Provide fallback behavior (process all rows)
- Not crash or lose data

---

## Best Practice: Manual Workflow Ordering

You need to run workflows in the correct order manually:

```bash
# Step 1: Create the classification column
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only

# Step 2: Use the classification column for filtering
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

**Why manual?**
- Simple and explicit
- You control the flow
- Easy to understand what's happening
- Can run workflows multiple times
- Can skip steps if data already exists

---

## Recommended: Check Before Running

Before running a filtered workflow, check if the column exists:

```bash
# Quick check
python -c "
import sqlite3
conn = sqlite3.connect('leads/yc-f25/table.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM leads WHERE is_b2b = \"1\"')
count = cursor.fetchone()[0]
print(f'B2B companies ready: {count}')
if count == 0:
    print('⚠️  Run b2b_only workflow first!')
else:
    print('✅ Ready to run founder_linkedin workflow')
conn.close()
"
```

---

## Future Enhancement Ideas

We COULD add these features (not implemented yet):

### 1. Prerequisite Checking
```yaml
founder_linkedin:
  conditions:
    where: "is_b2b = '1'"
  requires:  # ← New field
    - workflow: b2b_only
      columns: [is_b2b]
```

### 2. Auto-Run Prerequisites
```bash
# Automatically runs b2b_only if is_b2b column missing
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --auto-deps
```

### 3. Validation Mode
```bash
# Check if ready to run (dry run)
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --validate
# Output: "Error: Column 'is_b2b' required but not found. Run 'b2b_only' first."
```

But for now, you manage workflow order manually.

---

## Final Answer

**Q: Does our system handle running workflows in wrong order?**

**A: YES, it handles errors gracefully:**
- ✅ Doesn't crash
- ✅ Shows warning messages
- ✅ Has fallback behavior
- ⚠️  But may process more rows than intended
- ❌ Doesn't automatically fix the order

**Recommendation**: Run workflows in correct order manually for best results.
