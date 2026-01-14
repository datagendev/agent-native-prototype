# How and When Results Are Saved

## The Key Question

**Q**: When do results get saved? At the end of the workflow or during execution?

**A**: Results are saved **IMMEDIATELY after each node completes**, not at the end.

## Code Flow: Result Saving

**File**: `scripts/graph_enrich.py` (lines 1416-1492)

```python
def process_row_workflow(row):
    row_id = row["_id"]
    row_data = row.copy()

    for node in nodes:  # Loop through each node
        # 1. Run the node
        result, err = node(input_row)

        # 2. Prepare updates
        updates = {}
        for k, v in result.items():
            updates[k] = v

        # 3. SAVE TO DATABASE IMMEDIATELY (line 1482)
        db.update_row(row_id, updates, status=None, error=None)

        # 4. Next node sees the updated data
        row_data.update(updates)
```

**Key Line 1482**:
```python
db_err = db.update_row(row_id, updates, status=None, error=None)
```

This happens **inside the node loop**, which means:
- After node 1 completes → SAVE to database
- After node 2 completes → SAVE to database
- After node 3 completes → SAVE to database

Results are saved **incrementally**, not all at once at the end.

## Example: Starting with NO B2B Classification

### Scenario: Original CSV Has NO `is_b2b` Column

Your CSV looks like this:
```csv
name,location,description,industry
JSX Tool,SF,JavaScript framework,Developer Tools
Mayflower,SF,AI assistant,AI/ML
item,SF,Shopping app,E-commerce
```

No `is_b2b` column exists yet!

---

### Step 1: Run B2B Classification Workflow

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
```

**What happens**:

1. System loads all 156 companies from CSV into database
2. System runs `b2b_classifier` node on each company
3. **IMMEDIATELY after each company is classified**, results are saved:
   - Company 1: `is_b2b = '1'` → SAVED to database
   - Company 2: `is_b2b = '1'` → SAVED to database
   - Company 3: `is_b2b = '0'` → SAVED to database
   - ... (continues for all 156)

4. Database now has `is_b2b` column populated!

**Database after Step 1**:
```
ID  name        is_b2b  b2b_confidence  classification_reason
1   JSX Tool    1       0.9             Targets developers, B2B SaaS
2   Mayflower   1       0.85            Enterprise AI tool
3   item        0       0.7             Consumer shopping app
```

---

### Step 2: Run Founder Enrichment Workflow (With WHERE Filter)

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

**What happens**:

1. System loads workflow and sees: `conditions: where: "is_b2b = '1'"`
2. System asks database: "Give me companies where is_b2b = '1'"
3. Database returns 45 B2B companies (not all 156)
4. System processes ONLY those 45 companies:
   - Run `yc_founder` node → SAVE results immediately
   - Run `founder_posts` node → SAVE results immediately
   - Run `claude_code_check` node → SAVE results immediately

**Database after Step 2**:
```
ID  name        is_b2b  founder_name   founder_linkedin_url        uses_claude_code
1   JSX Tool    1       John Doe       linkedin.com/in/johndoe     1
2   Mayflower   1       Jane Smith     linkedin.com/in/janesmith   0
3   item        0       NULL           NULL                        NULL  ← NOT enriched
```

Company 3 was NOT processed because `is_b2b = '0'`.

---

## What If You Run founder_linkedin BEFORE b2b_only?

### Scenario: No B2B Data Yet

```bash
# Oops! Running founder_linkedin FIRST (before classification)
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

**What happens**:

1. System loads workflow: `conditions: where: "is_b2b = '1'"`
2. System asks database: "Give me companies where is_b2b = '1'"
3. Database returns: **0 companies** (column doesn't exist or all NULL)
4. System says: "Applied WHERE filter: is_b2b = '1' (0 rows matched)"
5. **Nothing gets processed!**

**Output**:
```
Applied WHERE filter: is_b2b = '1' (0 rows matched)
Lead Table: table.db (0 rows)
Completed: 0 / 0 rows
```

**Solution**: Run `b2b_only` workflow first to populate the `is_b2b` column!

---

## Correct Two-Step Workflow Pattern

### Step 1: Classification (No Filter Needed)

```yaml
# workflows.yaml
b2b_only:
  description: "Classify ALL companies as B2B or B2C"
  # NO conditions - processes all rows
  nodes:
    - b2b_classifier
  connections:
    - from: $input.description
      to: b2b_classifier.description
```

```bash
# Run on all 156 companies
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
# Output: Processed 156 rows
# Result: is_b2b column now populated
```

**After this step**: Database has `is_b2b` column with values.

---

### Step 2: Deep Enrichment (With Filter)

```yaml
# workflows.yaml
founder_linkedin:
  description: "Enrich ONLY B2B companies"
  conditions:
    where: "is_b2b = '1'"  # ← Filter uses results from Step 1
  nodes:
    - yc_founder
    - founder_posts
```

```bash
# Run on filtered subset
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
# Output: Applied WHERE filter (45 rows matched)
# Result: Only B2B companies enriched
```

**After this step**: Only B2B companies have founder data.

---

## Result Persistence

### Database is the Source of Truth

Results are saved to: `leads/yc-f25/table.db` (SQLite database)

**After each node completes**:
```python
# Line 1482 in graph_enrich.py
db.update_row(row_id, updates)  # ← Saves to database immediately
```

**This means**:
- ✅ Results persist between workflow runs
- ✅ You can stop and resume workflows
- ✅ Later workflows can use earlier results
- ✅ Each workflow builds on previous data

### Exporting Results

After all workflows complete, export to CSV:

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --output enriched.csv
```

This creates a CSV with all columns from all workflows:
```csv
name,is_b2b,b2b_confidence,founder_name,founder_linkedin_url,uses_claude_code
JSX Tool,1,0.9,John Doe,linkedin.com/in/johndoe,1
Mayflower,1,0.85,Jane Smith,linkedin.com/in/janesmith,0
item,0,0.7,,,  ← Empty founder fields (not enriched)
```

---

## Key Takeaways

1. **Results saved immediately** after each node (not at end of workflow)
2. **Database is persistent** - results survive between workflow runs
3. **Later workflows can filter** using earlier workflow results
4. **Order matters** - run classification before filtered enrichment
5. **WHERE filter fails gracefully** - returns 0 rows if column doesn't exist

---

## Complete Example: Start to Finish

### Starting Point: Raw CSV

```csv
name,location,description
JSX Tool,SF,JavaScript framework
Mayflower,SF,AI assistant
item,SF,Shopping app
```

### Workflow 1: Classify Everything

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
```

**Result**: `is_b2b` column added:
```
name        → is_b2b (SAVED to database)
JSX Tool    → 1
Mayflower   → 1
item        → 0
```

### Workflow 2: Enrich B2B Only

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

**Result**: Founder columns added for B2B companies:
```
name        is_b2b  → founder_name (SAVED to database)
JSX Tool    1       → John Doe
Mayflower   1       → Jane Smith
item        0       → NULL (skipped by WHERE filter)
```

### Export Final Results

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --output final.csv
```

**Final CSV**:
```csv
name,is_b2b,founder_name,founder_linkedin_url
JSX Tool,1,John Doe,linkedin.com/in/johndoe
Mayflower,1,Jane Smith,linkedin.com/in/janesmith
item,0,,
```

---

## Error Handling: Missing Columns

If you run a workflow with a WHERE clause on a column that doesn't exist:

**What happens**:
```
Warning: Failed to apply WHERE filter 'is_b2b = 1': column not found
Proceeding with all rows
```

**The workflow continues** with all rows (fallback behavior).

**Solution**: Run the prerequisite workflow first to create the column.
