# Simple Answer: WHERE Filter with No B2B Data Yet

## Your Question

> "What if my original CSV has no b2b/b2c column yet? How does the WHERE filter handle it?"

## Simple Answer

**If your CSV has no `is_b2b` column, you must run TWO workflows in order:**

### Workflow 1: Create the B2B Column (Run First!)
```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
```

This workflow:
- Processes ALL 156 companies
- Creates the `is_b2b` column
- Saves results immediately after each company is classified

**Result**: Database now has `is_b2b` column populated.

### Workflow 2: Use the B2B Column (Run Second!)
```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

This workflow:
- Loads the condition: `where: "is_b2b = '1'"`
- Filters to only B2B companies
- Processes ONLY the filtered companies
- Saves results immediately after each company is enriched

**Result**: Only B2B companies get founder data.

---

## What If You Run Them in Wrong Order?

### Wrong Order: Run founder_linkedin FIRST (Before b2b_only)

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

**Output**:
```
Applied WHERE filter: is_b2b = '1' (0 rows matched)
Lead Table: table.db (0 rows)
Completed: 0 / 0 rows
```

**What happened**:
- WHERE filter tried to find rows where `is_b2b = '1'`
- Column doesn't exist yet (or all values are NULL)
- 0 companies matched
- Nothing got processed

**Solution**: Run `b2b_only` workflow first!

---

## When Are Results Saved?

**Results are saved IMMEDIATELY after each node completes.**

### Example: Processing 3 Companies

**Workflow 1: b2b_only**
```
Time 0:01 - Classify Company 1 → is_b2b = 1 → 💾 SAVE TO DATABASE
Time 0:02 - Classify Company 2 → is_b2b = 1 → 💾 SAVE TO DATABASE
Time 0:03 - Classify Company 3 → is_b2b = 0 → 💾 SAVE TO DATABASE
Done! Database has is_b2b column.
```

**Workflow 2: founder_linkedin (with WHERE filter)**
```
Time 0:00 - Apply filter: where is_b2b = '1'
            Result: Companies 1 and 2 (Company 3 excluded!)

Time 0:01 - Enrich Company 1 → founder_name = "John" → 💾 SAVE TO DATABASE
Time 0:15 - Enrich Company 1 → recent_posts = 5 → 💾 SAVE TO DATABASE
Time 0:30 - Enrich Company 2 → founder_name = "Jane" → 💾 SAVE TO DATABASE
Time 0:45 - Enrich Company 2 → recent_posts = 3 → 💾 SAVE TO DATABASE
Done! Only Companies 1 and 2 enriched. Company 3 never touched.
```

**Key Point**: Each result is saved RIGHT AWAY, not at the end of the workflow!

---

## Quick Reference

| Scenario | What Happens | Solution |
|----------|--------------|----------|
| CSV has no `is_b2b` column | WHERE filter returns 0 rows | Run `b2b_only` workflow first |
| CSV has `is_b2b = NULL` | WHERE filter returns 0 rows | Run `b2b_only` workflow first |
| CSV has `is_b2b = '1'` for some rows | WHERE filter works! Returns those rows | No problem, just run the workflow |
| Workflow crashes mid-execution | Already-processed rows are saved | Resume with `--skip-existing` flag |

---

## Complete Example: Starting from Scratch

### Step 0: Your Starting CSV (No B2B Column)
```csv
name,location,description
JSX Tool,SF,JavaScript framework
Mayflower,SF,AI assistant
item,SF,Shopping app
```

### Step 1: Load CSV into Database
```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
```

Database after Step 1:
```
name        | is_b2b | b2b_confidence
------------|--------|---------------
JSX Tool    | 1      | 0.9           ← SAVED after classification
Mayflower   | 1      | 0.85          ← SAVED after classification
item        | 0      | 0.7           ← SAVED after classification
```

### Step 2: Enrich B2B Companies
```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

**Output**:
```
Applied WHERE filter: is_b2b = '1' (2 rows matched)
Processing 2 companies...
```

Database after Step 2:
```
name        | is_b2b | founder_name | founder_linkedin_url
------------|--------|--------------|---------------------
JSX Tool    | 1      | John Doe     | linkedin.com/...     ← SAVED
Mayflower   | 1      | Jane Smith   | linkedin.com/...     ← SAVED
item        | 0      | NULL         | NULL                 ← NOT PROCESSED
```

### Step 3: Export Final Results
```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --output final.csv
```

**final.csv**:
```csv
name,is_b2b,founder_name,founder_linkedin_url
JSX Tool,1,John Doe,linkedin.com/in/johndoe
Mayflower,1,Jane Smith,linkedin.com/in/janesmith
item,0,,
```

---

## One-Sentence Summary

**Results are saved to the database immediately after each company is processed, so you must run the classification workflow BEFORE running the filtered enrichment workflow.**
