# WHERE Filter Code Trace - How Company ID 4 Was Skipped

## The Key Question

**Why wasn't Company ID 4 (B2C) enriched, even though it had NO DATA?**

Answer: The WHERE clause filtered it out BEFORE any enrichment happened.

## Code Execution Flow

### Step 1: Load Workflow Conditions

**File**: `scripts/graph_enrich.py` (lines 1358-1365)

```python
# Get workflow conditions (if any)
try:
    from importlib import import_module
    graph_module = import_module(f"{lead_name}.graph")  # Import yc-f25.graph
    get_conditions_fn = getattr(graph_module, "get_workflow_conditions", None)
    conditions = get_conditions_fn(workflow_name) if get_conditions_fn else None
except Exception:
    conditions = None
```

**Result**:
```python
conditions = {
    "where": "is_b2b = '1'"
}
```

### Step 2: Fetch ALL Rows from Database

**File**: `scripts/graph_enrich.py` (lines 1367-1374)

```python
# Get rows from database
rows, err = db.get_rows()
if err:
    console.print(f"[red]Error loading rows: {err}[/red]")
    return False
```

**Result**: `rows` contains ALL 156 companies, including ID 4 (B2C)

```python
rows = [
    {"_id": 1, "name": "JSX Tool", "is_b2b": "1", ...},
    {"_id": 2, "name": "Zephyr Fusion", "is_b2b": "1", ...},
    {"_id": 3, "name": "Mayflower", "is_b2b": "1", ...},
    {"_id": 4, "name": "item", "is_b2b": "0", ...},  # ← B2C company
    # ... 152 more rows
]
```

### Step 3: Apply WHERE Filter 🔍 **THIS IS WHERE ID 4 GETS FILTERED OUT**

**File**: `scripts/graph_enrich.py` (lines 1376-1392)

```python
# Apply workflow conditions (WHERE clause filtering)
if conditions and "where" in conditions:
    where_clause = conditions["where"]  # "is_b2b = '1'"

    # Call database filter method
    filtered_rows, filter_err = db.filter_rows(where_clause)

    if filter_err:
        console.print(f"[yellow]Warning: Failed to apply WHERE filter[/yellow]")
        # Proceed with all rows on error
    else:
        rows = filtered_rows  # ← REPLACE all rows with filtered rows
        console.print(f"[cyan]Applied WHERE filter: {where_clause} ({len(rows)} rows matched)[/cyan]")
```

**File**: `scripts/db.py` (lines 313-340) - The actual SQL filtering

```python
def filter_rows(self, where_clause: str) -> tuple[list[dict], str]:
    """Filter rows using a SQL WHERE clause."""
    if not self.conn:
        return [], "not connected"

    try:
        cursor = self.conn.cursor()

        # Build query with WHERE clause
        query = f"SELECT * FROM leads WHERE {where_clause}"
        # Becomes: SELECT * FROM leads WHERE is_b2b = '1'

        cursor.execute(query)  # SQLite executes the filter
        rows = [dict(row) for row in cursor.fetchall()]

        return rows, ""
    except Exception as e:
        return [], f"filter_rows error: {e}"
```

**SQL Execution**:
```sql
SELECT * FROM leads WHERE is_b2b = '1'
```

**Result**: Only 3 rows returned (IDs 1, 2, 3)

```python
filtered_rows = [
    {"_id": 1, "name": "JSX Tool", "is_b2b": "1", ...},
    {"_id": 2, "name": "Zephyr Fusion", "is_b2b": "1", ...},
    {"_id": 3, "name": "Mayflower", "is_b2b": "1", ...},
    # Company ID 4 NOT in this list! ← Filtered out by WHERE clause
]
```

**Back in graph_enrich.py line 1388**:
```python
rows = filtered_rows  # rows now contains ONLY 3 companies
```

### Step 4: Process ONLY Filtered Rows

**File**: `scripts/graph_enrich.py` (line 1394+)

```python
total = len(rows)  # total = 3, not 156!

# ... later in the workflow execution loop ...

for row in rows:  # Loops through ONLY the 3 filtered rows
    # Process each node (yc_founder, founder_posts, claude_code_check)
    for node in nodes:
        result, err = node.run(row)
        # ...
```

**Result**: Company ID 4 is NOT in the `rows` list, so it never gets processed!

## Visual Code Flow

```
┌────────────────────────────────────────────────────────────┐
│ 1. Load Workflow                                           │
│    conditions = {"where": "is_b2b = '1'"}                  │
└─────────────────────┬──────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────┐
│ 2. Fetch ALL Rows from Database                           │
│    rows = db.get_rows()                                    │
│    → 156 companies (including ID 4)                        │
└─────────────────────┬──────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────┐
│ 3. Apply WHERE Filter (graph_enrich.py:1376-1392) 🔍      │
│    filtered_rows = db.filter_rows("is_b2b = '1'")         │
│                                                             │
│    SQLite executes:                                         │
│    SELECT * FROM leads WHERE is_b2b = '1'                  │
│                                                             │
│    Result:                                                  │
│    ✓ ID 1 (B2B) → INCLUDED                                 │
│    ✓ ID 2 (B2B) → INCLUDED                                 │
│    ✓ ID 3 (B2B) → INCLUDED                                 │
│    ✗ ID 4 (B2C) → EXCLUDED ← This is the key!             │
│    ✗ IDs 5-156  → EXCLUDED                                 │
│                                                             │
│    rows = filtered_rows  # Replace with filtered list      │
└─────────────────────┬──────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────┐
│ 4. Process ONLY Filtered Rows                             │
│    for row in rows:  # Loops 3 times, not 156!            │
│        for node in nodes:                                  │
│            node.run(row)                                   │
│                                                             │
│    Company ID 4 is NOT in rows, so it never executes!     │
└────────────────────────────────────────────────────────────┘
```

## The Proof - Database State

**Before filtering** (line 1368):
```python
rows = [
    {_id: 1, is_b2b: '1'},  # Will be processed
    {_id: 2, is_b2b: '1'},  # Will be processed
    {_id: 3, is_b2b: '1'},  # Will be processed
    {_id: 4, is_b2b: '0'},  # ← B2C company
    # ... 152 more
]
len(rows) = 156
```

**After filtering** (line 1388):
```python
rows = [
    {_id: 1, is_b2b: '1'},
    {_id: 2, is_b2b: '1'},
    {_id: 3, is_b2b: '1'},
]
len(rows) = 3  # Company ID 4 NOT in list!
```

**In the processing loop**:
```python
for row in rows:  # Loops 3 times
    print(f"Processing company ID {row['_id']}")
    # Output:
    # Processing company ID 1
    # Processing company ID 2
    # Processing company ID 3
    # ← Never prints "Processing company ID 4"
```

## Why This Proves the WHERE Filter Works

1. **Company ID 4 had NO DATA** (we cleared `founder_name`, `founder_linkedin_url`, etc.)
2. **Company ID 4 needed enrichment** (same as IDs 1-3)
3. **Company ID 4 was NOT enriched** (confirmed in database)
4. **Only difference**: Company ID 4 has `is_b2b = '0'` (B2C)

**Conclusion**: The WHERE clause `"is_b2b = '1'"` successfully filtered out company ID 4 BEFORE any enrichment happened.

## Key Code Locations

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/graph_enrich.py` | 1358-1365 | Load workflow conditions from YAML |
| `scripts/graph_enrich.py` | 1376-1392 | Apply WHERE filter to rows |
| `scripts/db.py` | 313-340 | Execute SQL WHERE clause |
| `leads/yc-f25/graph/workflows.yaml` | 52-53 | Define WHERE condition |

## The Critical Line

**Line 1388 in `scripts/graph_enrich.py`**:
```python
rows = filtered_rows  # ← This assignment replaces ALL rows with FILTERED rows
```

After this line executes:
- `rows` contains only 3 companies (IDs 1, 2, 3)
- Company ID 4 is completely removed from the processing pipeline
- All subsequent code operates on the filtered list

This is why company ID 4 was never enriched! 🎯
