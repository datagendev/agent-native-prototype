# WHERE Filter Proof - Conditional Workflow Execution

## Test Setup

**Database**: `leads/yc-f25/table.db` with 156 companies

**Test Configuration**:
- 3 companies marked as B2B (`is_b2b = '1'`)
- 8 companies marked as B2C (`is_b2b = '0'`)
- 145 companies unclassified (`is_b2b = NULL`)

**Workflow Configuration** (`workflows.yaml`):
```yaml
founder_linkedin:
  description: "Find founder and analyze LinkedIn activity (for B2B companies)"
  conditions:
    where: "is_b2b = '1'"  # ← Filter to only B2B companies
  nodes:
    - yc_founder
    - founder_posts
    - claude_code_check
```

## Execution Output

```bash
$ python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin

Applied WHERE filter: is_b2b = '1' (3 rows matched)
╭──────────────────────────────────╮
│ WORKFLOW BATCH: founder_linkedin │
╰──────────────────────────────────╯
Lead Table: table.db (3 rows)  # ← Only 3 rows, not 156!
Nodes: 3
Parallel Workers: 1
```

## Proof 1: Row Processing Log

From `row_executions` table (tracks which rows were processed):

```
Rows processed in last workflow run: 3 rows

  • ID   1 (B2B ✓): JSX Tool
  • ID   2 (B2B ✓): Zephyr FusionSan Diego, CA, USA
  • ID   3 (B2B ✓): MayflowerSan Francisco, CA, USA
```

**Evidence**: Only 3 rows attempted, all with `is_b2b = '1'`

## Proof 2: Comparison Test

Cleared founder data for both B2B and B2C companies before workflow:

| ID  | Type | Company Name                     | Processed? |
|-----|------|----------------------------------|------------|
| 1   | B2B  | JSX Tool                         | ✓ YES      |
| 2   | B2B  | Zephyr Fusion                    | ✓ YES      |
| 3   | B2B  | Mayflower                        | ✓ YES      |
| 4   | B2C  | item                             | ✗ NO       |

**Evidence**: B2C company (ID 4) was completely skipped, even though it also needed enrichment

## Proof 3: Execution Statistics

From `executions` table:

```
Most Recent Execution:
  Workflow: founder_linkedin
  Total Rows Planned: 3
  Actual Rows Processed: 3
  Skipped by WHERE filter: 153 rows

  Processed Rows:
    • ID 1: JSX Tool (is_b2b=1)
    • ID 2: Zephyr FusionSan Diego, CA, USA (is_b2b=1)
    • ID 3: MayflowerSan Francisco, CA, USA (is_b2b=1)
```

**Evidence**:
- Execution planned for exactly 3 rows (not 156)
- All processed rows have `is_b2b = '1'`
- 153 rows (98%) were skipped by filter

## Visual Proof

```
Total Database: 156 companies
                 │
                 ├─ is_b2b = '1' → 3 companies  ✓ PROCESSED by workflow
                 ├─ is_b2b = '0' → 8 companies  ✗ SKIPPED by WHERE filter
                 └─ is_b2b = NULL → 145 companies ✗ SKIPPED by WHERE filter

WHERE clause "is_b2b = '1'" filtered:
  156 rows → 3 rows (98% reduction)
```

## Cost Savings Calculation

**Without WHERE filter** (full_enrichment workflow):
- 156 companies × 3 nodes (yc_founder, founder_posts, claude_code_check)
- 468 node executions
- Estimated: ~50 seconds per company × 156 = 130 minutes

**With WHERE filter** (founder_linkedin workflow):
- 3 companies × 3 nodes
- 9 node executions
- Estimated: ~50 seconds per company × 3 = 2.5 minutes

**Savings**: 98% reduction in processing time and API calls

## Conclusion

✅ **WHERE clause filtering works correctly**

The `conditions.where` feature successfully:
1. Filtered 156 rows down to 3 matching rows
2. Only processed rows where `is_b2b = '1'`
3. Skipped all non-matching rows (B2C and unclassified)
4. Saved 98% of processing time and costs

**Evidence sources**:
- CLI output showing "3 rows matched"
- `row_executions` table showing only 3 rows processed
- Database state showing B2C companies untouched
- `executions` table showing planned row count of 3

## Implementation Files

The working implementation is in:
- `leads/yc-f25/graph/loader.py` (conditions support)
- `scripts/db.py` (`filter_rows()` method)
- `scripts/graph_enrich.py` (WHERE clause application)
- `leads/yc-f25/graph/workflows.yaml` (workflow definition)
