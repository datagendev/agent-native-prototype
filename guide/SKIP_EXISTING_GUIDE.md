---
title: "Skip Existing Integrations Guide"
description: "How to efficiently re-run enrichments on partially enriched data"
created: 2026-01-10
updated: 2026-01-10
---

# Skip Existing Integrations Guide

## Overview

The `--skip-existing` flag allows you to intelligently skip integrations that have already been run on a row, saving API calls and time when:
- Adding new integrations to already-enriched data
- Re-running enrichment after fixing errors
- Incrementally enriching large datasets

## How It Works

### Detection Logic

For each row and integration, the system checks:

1. **Do ALL output columns exist in the row?**
2. **Do ALL output columns have non-empty values?**

If **both are true**, the integration is skipped for that row.

### Example

```csv
# Input: lead-list/prospects_enriched.csv
name,linkedin_url,headline,current_company,location,follower_count
Eric,https://...,Growth Expert,Company X,SF,48000
Jordan,https://...,,,0                      # ← Empty values
```

Running with `--skip-existing`:
```bash
python batch_enrich.py \
  --input lead-list/prospects_enriched.csv \
  --integrations linkedin_profile \
  --skip-existing
```

**Result**:
- Eric: **SKIPPED** (all columns populated)
- Jordan: **RUN** (columns empty, needs enrichment)

## Use Cases

### Use Case 1: Add New Integrations

You've already enriched with `linkedin_profile`, now want to add `heyreach_engagement`:

```bash
# Step 1: Initial enrichment (23s)
python batch_enrich.py \
  --input leads.csv \
  --integrations linkedin_profile

# Output: leads_enriched.csv with 4 new columns

# Step 2: Add heyreach without re-running linkedin (6s)
python batch_enrich.py \
  --input leads_enriched.csv \
  --integrations linkedin_profile,heyreach_engagement \
  --skip-existing

# linkedin_profile skipped (already done)
# heyreach_engagement runs (new integration)
```

**Time saved**: 17 seconds (73% faster)

### Use Case 2: Retry Failed Rows

Some rows failed due to rate limits. Re-run only the failed ones:

```bash
# First run: 97/100 succeeded, 3 failed
python batch_enrich.py \
  --input leads.csv \
  --integrations linkedin_profile

# Wait for rate limit to reset, then retry
python batch_enrich.py \
  --input leads_enriched.csv \
  --integrations linkedin_profile \
  --skip-existing

# Only the 3 failed rows (with empty values) will be enriched
```

**Benefit**: Avoids re-calling API for 97 successful rows.

### Use Case 3: Incremental Enrichment

Process a large dataset in batches:

```bash
# Day 1: Enrich first 1000 rows
python batch_enrich.py \
  --input big-list.csv \
  --integrations linkedin_profile \
  --output progress.csv

# Day 2: Add more integrations (linkedin_profile skipped automatically)
python batch_enrich.py \
  --input progress.csv \
  --integrations linkedin_profile,linkedin_post_activity \
  --skip-existing \
  --output progress.csv

# Day 3: Add even more
python batch_enrich.py \
  --input progress.csv \
  --integrations linkedin_profile,linkedin_post_activity,heyreach_engagement \
  --skip-existing \
  --output progress.csv
```

Each run only executes new/missing integrations.

## CLI Usage

### Basic Syntax

```bash
python batch_enrich.py \
  --input <csv-file> \
  --integrations <integration1,integration2,...> \
  --skip-existing
```

### Examples

**Skip if already populated:**
```bash
python batch_enrich.py \
  --input leads_enriched.csv \
  --integrations linkedin_profile,heyreach_engagement \
  --skip-existing
```

**Force re-run (ignore existing data):**
```bash
python batch_enrich.py \
  --input leads_enriched.csv \
  --integrations linkedin_profile \
  # (no --skip-existing flag)
```

**Multiple integrations with skip:**
```bash
python batch_enrich.py \
  --input leads.csv \
  --integrations linkedin_profile,linkedin_post_activity,linkedin_claude_mentions \
  --skip-existing \
  --parallel 10
```

## Terminal UI Indicators

When `--skip-existing` is enabled, you'll see:

### 1. Configuration Table
```
   Input File           leads_enriched.csv
   Integrations         linkedin_profile
   Parallel Workers     4
   Skip Existing        Yes - will skip integrations with existing data
```

### 2. Progress Bar
```
  Enriching rows (3 ✓ / 1 ✗ ⊘ 3 skipped) ━━━━━━━━━━━━━━ 100%
                              ^^^^^^^^^^
                          Skip indicator (yellow)
```

### 3. Skipped Integrations Table
```
ℹ️  Skipped integrations (already populated):

  Row          Skipped
  ───────────────────────────
  Eric         linkedin_profile
  Brady        linkedin_profile
  Hannah       linkedin_profile
```

### 4. Summary Stats
```
╭─────────────────────────────┬────────────────────────────────╮
│  ✅ Successfully Enriched   │  3/4 rows                      │
│  ⊘ Integrations Skipped     │  3 (already populated)         │
│  📊 New Columns Added       │  0                             │
│  ⏱️  Time Elapsed            │  6.2s                          │
╰─────────────────────────────┴────────────────────────────────╯
```

## When to Use vs Not Use

### ✅ Use `--skip-existing` When:

1. **Adding new integrations** to already-enriched data
2. **Retrying failures** without re-processing successes
3. **Incrementally enriching** large datasets over multiple sessions
4. **Testing integrations** on already-enriched samples
5. **Saving API costs** when re-running the same command

### ❌ Don't Use When:

1. **Data has changed** and you need fresh values
2. **First enrichment** (nothing to skip yet)
3. **Debugging issues** with specific integrations (want to force re-run)
4. **Columns partially filled** by manual editing (may skip incorrectly)

## Performance Impact

### Time Savings

| Rows | Integrations | Without Skip | With Skip | Savings |
|------|--------------|--------------|-----------|---------|
| 4    | 1 (re-run)   | 23.4s        | 6.2s      | 73%     |
| 100  | 1 (re-run)   | ~583s        | ~155s     | 73%     |
| 100  | 2 (1 new)    | ~1166s       | ~583s     | 50%     |

### API Call Savings

Example: 100 rows, 3 integrations, 2 already run

- **Without skip**: 100 × 3 = 300 API calls
- **With skip**: 100 × 1 = 100 API calls
- **Savings**: 200 API calls (67% reduction)

## Edge Cases

### Empty String Values

Empty strings (`""`) are treated as "missing":

```csv
name,headline,current_company
Eric,Growth Expert,Company X    # ← SKIP (all populated)
Jordan,,                         # ← RUN (empty values)
Brady,Product Lead,              # ← RUN (current_company empty)
```

### Zero Values

Numeric zero (`0`) is considered "populated":

```csv
name,follower_count
Eric,48000        # ← SKIP (has value)
Jordan,0          # ← SKIP (zero is a valid value)
Hannah,           # ← RUN (empty/missing)
```

### Partial Integration Output

If an integration has 4 output columns, but only 3 are populated:

```csv
name,headline,current_company,location,follower_count
Eric,Expert,Company,SF,         # ← RUN (follower_count missing)
```

The integration will **run** because not all output columns are populated.

### Multiple Integrations

Each integration is evaluated independently:

```bash
--integrations linkedin_profile,heyreach_engagement
```

- `linkedin_profile` checks: `headline`, `current_company`, `location`, `follower_count`
- `heyreach_engagement` checks: `reply_rate`, `meeting_booked`, `last_interaction`

If Row 5 has LinkedIn data but no HeyReach data:
- `linkedin_profile`: **SKIPPED**
- `heyreach_engagement`: **RUN**

## Technical Details

### Implementation

```python
def should_skip_integration(row, integration, skip_existing):
    if not skip_existing:
        return False  # Always run if flag not set

    # Check all output columns
    for col in integration["output_cols"]:
        value = row.get(col)
        # Missing or empty string = need to run
        if not value or (isinstance(value, str) and value.strip() == ""):
            return False

    # All columns populated = skip
    return True
```

### Per-Row Decision

Skipping happens **per row**, not per batch:

- Row 1: Skip linkedin_profile (has data)
- Row 2: Run linkedin_profile (missing data)
- Row 3: Skip linkedin_profile (has data)

### Statistics Tracking

The system tracks:
- `skipped_count`: Total integrations skipped across all rows
- `all_skipped`: Dict mapping row_idx → {integration_name: True}

Example: 4 rows × 2 integrations, 3 rows skip integration 1:
- `skipped_count = 3`
- `all_skipped = {0: {"linkedin_profile": True}, 1: {"linkedin_profile": True}, 2: {"linkedin_profile": True}}`

## Best Practices

### 1. Always Use Same Input/Output Pattern

```bash
# ✅ Good: Explicit output path, consistent naming
python batch_enrich.py --input leads.csv --output progress.csv --integrations linkedin_profile
python batch_enrich.py --input progress.csv --output progress.csv --integrations linkedin_profile,heyreach --skip-existing

# ❌ Bad: Auto-generated output names get nested
python batch_enrich.py --input leads.csv --integrations linkedin_profile
# Creates leads_enriched.csv
python batch_enrich.py --input leads_enriched.csv --integrations linkedin_profile,heyreach --skip-existing
# Creates leads_enriched_enriched.csv (confusing!)
```

### 2. Check Columns Before Adding Integrations

```bash
# Verify what columns already exist
head -n 1 leads_enriched.csv

# Then decide which integrations to run
python batch_enrich.py --input leads_enriched.csv \
  --integrations <only-new-integrations> \
  --skip-existing
```

### 3. Use Skip for Production, Not for Testing

When testing new integrations, run **without** `--skip-existing` to ensure they work correctly. Once validated, use `--skip-existing` for production runs.

### 4. Monitor Skip Counts

If skip count is unexpectedly high/low:
- **Too high**: May be skipping integrations you wanted to re-run
- **Too low**: Output columns might not be properly named

Check the skipped integrations table to verify behavior.

## Troubleshooting

### Problem: Integration Not Skipping When Expected

**Cause**: One or more output columns are empty

**Solution**: Check the CSV for empty values:
```bash
# Find rows with empty headline column
grep ',,.*,,.*headline' leads_enriched.csv
```

### Problem: Integration Skipping When It Shouldn't

**Cause**: `--skip-existing` flag is set, but you want to force re-run

**Solution**: Remove the `--skip-existing` flag:
```bash
python batch_enrich.py --input leads.csv --integrations linkedin_profile
# (no --skip-existing)
```

### Problem: All Integrations Skipped, No Work Done

**Cause**: All output columns already populated

**Solution**: This is expected behavior! If you need to refresh data, either:
1. Remove the `--skip-existing` flag to force re-run
2. Delete the output columns from the CSV before re-running

### Problem: Partial Skip (Some Rows Skip, Some Don't)

**Cause**: Some rows have empty values from previous failures

**Solution**: This is correct behavior! Only rows with complete data are skipped. Failed rows (empty values) will be re-processed.

## FAQ

**Q: Does skip-existing check data freshness?**
A: No. It only checks if columns exist and have non-empty values. It doesn't care if the data is stale.

**Q: Can I skip specific integrations manually?**
A: Not directly. But you can omit them from `--integrations` list:
```bash
# Only run heyreach, not linkedin
--integrations heyreach_engagement
```

**Q: What happens if I add new output columns to an integration?**
A: Old rows won't have the new columns, so the integration will run again to populate them.

**Q: Does this work with the class-based integration API?**
A: Yes! The skip logic works with both class-based and module-level integration APIs.

**Q: Can I force re-run just one integration?**
A: Not with `--skip-existing`. Workaround: Run that integration separately without the flag, then merge CSVs.

## See Also

- [TERMINAL_UI_GUIDE.md](./TERMINAL_UI_GUIDE.md) - Terminal UI features
- [HANDOFF.md](./HANDOFF.md) - Integration system architecture
- [batch_enrich.py](./scripts/batch_enrich.py) - Source code
