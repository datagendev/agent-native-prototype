# Workflow Conditional Execution (Option 3)

## Overview

Workflow-level conditional execution allows you to filter which rows are processed by a workflow using SQL WHERE clause conditions. This is useful for:

- **Cost savings**: Only enrich expensive nodes (LinkedIn scraping, AI analysis) on qualified leads
- **Two-step enrichment**: Fast classification first, then deep enrichment on subset
- **Declarative filtering**: Conditions are visible in workflow definition, not hidden in CLI flags

## Architecture

### Implementation Components

1. **Workflow YAML Schema** (`workflows.yaml`):
   - Added optional `conditions` block with `where` field
   - WHERE clause uses SQLite syntax

2. **Loader** (`leads/{name}/graph/loader.py`):
   - Extended `Workflow` dataclass with `conditions` field
   - Added `get_workflow_conditions()` method

3. **Database** (`scripts/db.py`):
   - Added `filter_rows(where_clause)` method to LeadDB class
   - Executes SQLite SELECT with WHERE clause

4. **Enrichment Engine** (`scripts/graph_enrich.py`):
   - Loads workflow conditions after loading nodes
   - Applies WHERE filter after fetching rows from database
   - Falls back to all rows if filter fails (with warning)

## Usage

### 1. Define Conditions in Workflow YAML

```yaml
workflows:
  founder_linkedin:
    description: "Find founder and analyze LinkedIn activity (for B2B companies)"
    conditions:
      where: "is_b2b = '1'"  # SQL WHERE clause
    nodes:
      - yc_founder
      - founder_posts
      - claude_code_check
    connections:
      - from: $input.name
        to: yc_founder.name
      # ... more connections
```

### 2. Two-Step Enrichment Pattern

**Step 1**: Fast classification on all rows
```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only
```

This runs the B2B classifier on all 156 companies (fast, cheap).

**Step 2**: Deep enrichment on qualified subset
```bash
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
```

This runs LinkedIn scraping only on B2B companies (slow, expensive).

### 3. Execution Output

```
Applied WHERE filter: is_b2b = '1' (3 rows matched)
╭──────────────────────────────────╮
│ WORKFLOW BATCH: founder_linkedin │
╰──────────────────────────────────╯
Lead Table: table.db (3 rows)  <-- Note: 3 instead of 156!
Nodes: 3
```

## WHERE Clause Syntax

The WHERE clause uses SQLite syntax. Common patterns:

```yaml
# Equality (string)
where: "is_b2b = '1'"

# Equality (number)
where: "confidence > 0.8"

# Null checks
where: "founder_linkedin_url IS NOT NULL"

# Multiple conditions
where: "is_b2b = '1' AND confidence > 0.7"

# Pattern matching
where: "industry LIKE '%AI%'"

# IN clause
where: "status IN ('qualified', 'active')"
```

**Important**: SQLite columns are TEXT by default, so use string comparisons `'1'` not `1`.

## Example: YC F25 Enrichment

### workflows.yaml
```yaml
workflows:
  # Step 1: Fast B2B classification (all rows)
  b2b_only:
    description: "Classify companies as B2B or B2C"
    nodes:
      - b2b_classifier
    connections:
      - from: $input.description
        to: b2b_classifier.description
      - from: $input.industry
        to: b2b_classifier.industry

  # Step 2: Expensive LinkedIn enrichment (B2B only)
  founder_linkedin:
    description: "Find founder and analyze LinkedIn activity"
    conditions:
      where: "is_b2b = '1'"
    nodes:
      - yc_founder
      - founder_posts
      - claude_code_check
    connections:
      - from: $input.name
        to: yc_founder.name
      - from: $input.yc_url
        to: yc_founder.yc_url
      - from: yc_founder.founder_linkedin_url
        to: founder_posts.founder_linkedin_url
      - from: yc_founder.founder_linkedin_url
        to: claude_code_check.founder_linkedin_url
```

### Execution Flow
```bash
# Classify all 156 companies (fast)
python scripts/graph_enrich.py --lead yc-f25 --workflow b2b_only

# Enrich only B2B companies (conditional)
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin
# Output: "Applied WHERE filter: is_b2b = '1' (45 rows matched)"
```

## Benefits Over Other Approaches

### vs Option 1 (Manual CLI Filtering)
- **Declarative**: Conditions visible in workflow definition
- **No CLI flags**: Just run the workflow, it knows what to filter
- **Self-documenting**: Looking at YAML shows intent

### vs Option 4 (Graph Branching)
- **Simpler**: No DAG complexity, no conditional edges
- **Easier to understand**: WHERE clause vs graph topology
- **Sufficient for 80% of use cases**: Most conditionals are simple filters

## Error Handling

If the WHERE clause fails (syntax error, column doesn't exist):
- Warning message displayed
- Execution continues with all rows (fallback behavior)
- Prevents total failure if column not yet populated

Example:
```
Warning: Failed to apply WHERE filter 'is_b2b = 1': column not found
Proceeding with all rows
```

## Implementation Files Changed

1. `leads/yc-f25/graph/loader.py`:
   - Added `conditions` field to `Workflow` dataclass (line 77)
   - Added `get_workflow_conditions()` method (line 396)
   - Updated `get_workflow_metadata()` to include conditions (line 393)
   - Added module-level convenience function (line 440)

2. `scripts/db.py`:
   - Added `filter_rows(where_clause)` method (line 313)
   - Returns filtered rows using SQL WHERE clause

3. `scripts/graph_enrich.py`:
   - Load workflow conditions after loading nodes (line 1358)
   - Apply filter after fetching rows (line 1376)
   - Display filter results in output (line 1390)

4. `leads/yc-f25/graph/workflows.yaml`:
   - Added `conditions.where` to `founder_linkedin` workflow (line 52)

## Future Enhancements

Possible additions without changing core architecture:

1. **Multiple conditions**: Support OR logic, complex expressions
2. **Column validation**: Check if WHERE columns exist before execution
3. **Condition preview**: Show which rows would match before running
4. **Statistics**: Show filtered vs total row count in summary
5. **Condition templates**: Reusable WHERE snippets (e.g., "qualified_b2b")

## Testing

Test suite for conditional execution:

```python
# Manual test (already verified)
# 1. Create test B2B data
UPDATE leads SET is_b2b = '1' WHERE _id IN (1, 2, 3)

# 2. Run conditional workflow
python scripts/graph_enrich.py --lead yc-f25 --workflow founder_linkedin

# 3. Verify output shows filtered count
# Expected: "Applied WHERE filter: is_b2b = '1' (3 rows matched)"

# 4. Verify database only has enrichment for those 3 rows
SELECT COUNT(*) FROM leads WHERE founder_linkedin_url IS NOT NULL
# Expected: 3
```

## Summary

Option 3 provides a clean, declarative way to conditionally execute workflows based on row attributes:

✅ Declarative (in YAML)
✅ No CLI flags needed
✅ Simple to implement
✅ Backward compatible
✅ Clear intent
✅ Sufficient for most use cases

Perfect for two-step enrichment patterns: fast classification → conditional deep enrichment.
