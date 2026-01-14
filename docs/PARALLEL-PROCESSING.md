# Parallel Processing: No, Rows Don't Wait for Each Other!

## Your Question

> "Does each row have to wait for another row to finish to go to the next workflow?"

## Answer: NO! 🚀

**Within a single workflow**: Rows are processed **IN PARALLEL** (multiple rows at the same time)

**Between workflows**: You run them **sequentially** (one workflow finishes, then start the next)

---

## How It Works: Within a Single Workflow

### Parallel Processing (Default)

```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --parallel 5
```

**What happens**:
```
Time 0:00 - Start 5 workers
Time 0:01 - Worker 1: Processing Row 1 (JSX Tool)
            Worker 2: Processing Row 2 (Mayflower)
            Worker 3: Processing Row 3 (item)
            Worker 4: Processing Row 4 (Rivet)
            Worker 5: Processing Row 5 (Openroll)
            ↑ All 5 processing AT THE SAME TIME!

Time 0:15 - Worker 1 finishes Row 1 → 💾 SAVE
            Worker 1 immediately starts Row 6 (next in queue)

Time 0:20 - Worker 3 finishes Row 3 → 💾 SAVE
            Worker 3 immediately starts Row 7

Time 0:30 - Worker 2 finishes Row 2 → 💾 SAVE
            Worker 2 immediately starts Row 8

... (continues until all rows processed)
```

**Key point**: Row 2 does NOT wait for Row 1 to finish! They process in parallel.

---

## The Code That Does This

**File**: `scripts/graph_enrich.py` (lines 1520-1534)

```python
# Process with ThreadPoolExecutor (parallel processing)
with ThreadPoolExecutor(max_workers=parallel) as executor:
    # Submit ALL rows at once to the thread pool
    futures = {
        executor.submit(process_row_workflow, row): row["_id"]
        for row in rows
    }

    # Wait for results as they complete (any order)
    for future in as_completed(futures):
        row_id, has_error = future.result()
        if has_error:
            failed += 1
        else:
            success += 1
        # Continue to next completed row
```

**Key components**:
1. `ThreadPoolExecutor(max_workers=parallel)` - Creates a pool of worker threads
2. `executor.submit(process_row_workflow, row)` - Submits ALL rows at once
3. `as_completed(futures)` - Results come back in ANY order (whoever finishes first)

---

## Visual: Parallel vs Sequential

### ❌ If It Was Sequential (NOT how it works)
```
Row 1 ━━━━━━━━━━━━━━━━━ (30s) → Save
                                    ↓
Row 2                               ━━━━━━━━━━━━━━━━━ (30s) → Save
                                                            ↓
Row 3                                                       ━━━━━━━━━━━━━━━━━ (30s) → Save

Total time: 90 seconds (30s × 3 rows)
```

### ✅ How It Actually Works (Parallel)
```
Row 1 ━━━━━━━━━━━━━━━━━ (30s) → Save
Row 2 ━━━━━━━━━━━━━━━━━ (30s) → Save
Row 3 ━━━━━━━━━━━━━━━━━ (30s) → Save
      ↑ All start at the same time!

Total time: 30 seconds (all process together)
```

---

## Between Workflows: Sequential Execution

**You must run workflows one after another:**

```bash
# Workflow 1: Runs and completes fully
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
# Takes 2 minutes, ALL 156 rows processed in parallel (5 at a time)

# ⏸️  Workflow 1 must finish before starting Workflow 2

# Workflow 2: Starts after Workflow 1 completes
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
# Takes 30 minutes, 45 B2B rows processed in parallel (5 at a time)
```

**Why sequential between workflows?**
- Workflow 2 needs results from Workflow 1 (the `is_b2b` column)
- If you start Workflow 2 while Workflow 1 is still running, some rows won't have `is_b2b` yet
- Database would be in an inconsistent state

---

## Parallel Workers Configuration

### Default: 5 Parallel Workers
```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
# Processes 5 rows at the same time
```

### Increase Parallelism (Faster)
```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --parallel 20
# Processes 20 rows at the same time
# ⚠️  Uses more API rate limits
```

### Decrease Parallelism (Safer)
```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin --parallel 1
# Processes 1 row at a time (fully sequential)
# ✅ Good for debugging or rate-limit concerns
```

---

## Timeline Example: 45 Rows with 5 Workers

```
Workers: [1] [2] [3] [4] [5]

Batch 1 (rows 1-5):
Time 0:00-0:30
  [1] Row 1 ━━━━━━━━━━━━━━━━━ Done → Save
  [2] Row 2 ━━━━━━━━━━━━━━━━━ Done → Save
  [3] Row 3 ━━━━━━━━━━━━━━━━━ Done → Save
  [4] Row 4 ━━━━━━━━━━━━━━━━━ Done → Save
  [5] Row 5 ━━━━━━━━━━━━━━━━━ Done → Save

Batch 2 (rows 6-10):
Time 0:30-1:00
  [1] Row 6 ━━━━━━━━━━━━━━━━━ Done → Save
  [2] Row 7 ━━━━━━━━━━━━━━━━━ Done → Save
  [3] Row 8 ━━━━━━━━━━━━━━━━━ Done → Save
  [4] Row 9 ━━━━━━━━━━━━━━━━━ Done → Save
  [5] Row 10 ━━━━━━━━━━━━━━━━ Done → Save

... (continues for all 45 rows in batches of 5)

Total time: ~4.5 minutes (45 rows ÷ 5 workers × 30s per row)
```

**If it was sequential** (1 worker):
- Total time: 22.5 minutes (45 rows × 30s per row)
- 5x slower!

---

## Important: Saves Happen Immediately

**Even though processing is parallel, saves are thread-safe:**

```python
# Each worker saves independently
Worker 1: Process Row 1 → Save Row 1 ✅
Worker 2: Process Row 2 → Save Row 2 ✅ (at same time!)
Worker 3: Process Row 3 → Save Row 3 ✅ (at same time!)
```

**Database handles concurrent writes:**
- SQLite has WAL mode enabled (Write-Ahead Logging)
- Multiple threads can write safely
- Each row saves independently
- No conflicts

---

## Does Row Order Matter?

### NO! Results Can Complete in Any Order

```
Submitted order: Row 1, Row 2, Row 3, Row 4, Row 5
Completion order: Row 2, Row 5, Row 1, Row 4, Row 3
                  ↑ Depends on API speed, data complexity, etc.
```

**This is fine because**:
- Each row is independent
- Database has `_id` to track which row
- Saves happen in completion order (not submission order)
- Final result is the same

---

## What About Dependencies Between Rows?

**Within a workflow**: No row depends on another row
- Each row processes independently
- Safe to run in parallel

**Between workflows**: Later workflow depends on earlier workflow
- Must run sequentially
- Earlier workflow must complete fully

**Example**:
```bash
# Workflow 1: Classifies ALL rows
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
# Rows 1-156 process in parallel
# Must finish before next workflow

# Workflow 2: Uses classification results
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
# Rows 1-45 process in parallel (only B2B)
# Can start after Workflow 1 completes
```

---

## Summary Table

| Scope | Processing | Waiting? |
|-------|-----------|----------|
| **Within 1 workflow** | Parallel (5 workers default) | ❌ No - rows process together |
| **Within 1 row** | Sequential (node 1 → node 2 → node 3) | ✅ Yes - nodes run in order |
| **Between workflows** | Sequential (workflow 1 → workflow 2) | ✅ Yes - must complete first |
| **Saving results** | Immediate after each node | ❌ No waiting - saves right away |

---

## Key Takeaways

1. **Rows process in PARALLEL within a workflow** (default 5 at a time)
2. **Nodes process SEQUENTIALLY within a row** (one node at a time per row)
3. **Workflows run SEQUENTIALLY** (one finishes before next starts)
4. **Results save IMMEDIATELY** (as soon as each row completes)
5. **Use `--parallel N` to control parallelism** (more workers = faster)

---

## One-Sentence Answer

**Within a single workflow run, rows are processed in parallel (default 5 at a time), so Row 2 does NOT wait for Row 1 to finish - but you must wait for the entire workflow to complete before starting the next workflow.**
