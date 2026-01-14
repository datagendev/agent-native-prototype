---
title: "Terminal UI Guide - Batch Enrichment"
description: "Rich terminal UI improvements for batch_enrich.py"
created: 2026-01-10
updated: 2026-01-10
---

# Terminal UI Guide - Batch Enrichment

## Overview

The `batch_enrich.py` script now includes a rich terminal UI using the `rich` library, providing real-time progress tracking, beautiful formatting, and enhanced user experience.

## Features

### 1. **Animated Progress Bar**
- Shows real-time completion percentage
- Displays success/error counts inline
- Time elapsed and estimated time remaining
- Smooth animations with spinner

### 2. **Configuration Table**
- Clean display of input file, integrations, and parallel workers
- Appears at the start of each run

### 3. **Status Spinners**
- Loading indicators for CSV loading, validation steps
- Non-blocking animations during I/O operations

### 4. **Live Progress Updates**
- Real-time success/error count in progress bar description
- Format: `Enriching rows (3 ✓ / 1 ✗)`
- Updates as each row completes

### 5. **Error Summary Table**
- Formatted table showing failed rows
- Row index and truncated error message
- Shows first 5 errors, counts remaining

### 6. **Final Summary Panel**
- Rounded box with completion statistics
- Success rate, new columns added, throughput
- Output file path
- Total time elapsed

### 7. **Color Coding**
- Green: Success messages and counts
- Red: Errors and failures
- Yellow: Warnings
- Cyan: Informational text and headers
- Blue: Section dividers

## Example Output

```
─────────────────────────────── BATCH ENRICHMENT ───────────────────────────────

   Input File           lead-list/gtm-influencers.csv
   Integrations         linkedin_profile
   Parallel Workers     4

✓ Loaded 4 rows with 4 columns
✓ Loaded 1 integrations
✓ All required columns present

  Enriching rows (3 ✓ / 1 ✗) ━━━━━━━━━━━━━━━━━━━━━━ 100% • 0:00:23 • 0:00:00

✓ Enrichment complete in 23.3s
✓ Saved 4 rows

⚠️  Errors occurred:
  Row          Error
  1            linkedin_profile: LinkedInProfile error: Resource not found

─────────────────────────────────── COMPLETE ───────────────────────────────────

╭─────────────────────────────┬────────────────────────────────────────────────╮
│  ✅ Successfully Enriched   │  3/4 rows                                      │
│  📊 New Columns Added       │  4                                             │
│     Columns                 │  headline, current_company, location, ...      │
│  ⏱️  Time Elapsed            │  23.3s                                         │
│  ⚡ Throughput              │  0.2 rows/sec                                  │
│  📂 Output File             │  lead-list/gtm-influencers_enriched.csv        │
╰─────────────────────────────┴────────────────────────────────────────────────╯
```

## Usage

No changes to command-line usage:

```bash
# Basic usage
source .venv/bin/activate && python scripts/batch_enrich.py \
  --input lead-list/file.csv \
  --integrations linkedin_profile

# Multiple integrations with custom parallel workers
source .venv/bin/activate && python scripts/batch_enrich.py \
  --input lead-list/file.csv \
  --integrations linkedin_profile,linkedin_post_activity,heyreach_engagement \
  --parallel 10

# Custom output path
source .venv/bin/activate && python scripts/batch_enrich.py \
  --input lead-list/file.csv \
  --integrations linkedin_profile \
  --output enriched-leads.csv
```

## Technical Details

### Dependencies

Added to virtual environment:
- `rich` - Terminal UI library (v14.2.0)
- `markdown-it-py` - Markdown rendering (transitive)
- `pygments` - Syntax highlighting (transitive)

### Key Components Used

1. **Progress**: Main progress tracking with multiple columns
   - SpinnerColumn: Animated spinner
   - TextColumn: Custom description text
   - BarColumn: Visual progress bar
   - TaskProgressColumn: Percentage complete
   - TimeElapsedColumn: Time since start
   - TimeRemainingColumn: Estimated time left

2. **Console**: Rich text rendering with markup
   - Color styling with `[color]text[/color]`
   - Bold/italic with `[bold]` and `[italic]`
   - Status spinners with `console.status()`

3. **Table**: Formatted tables with borders
   - Multiple box styles (ROUNDED, SIMPLE)
   - Column styling and width control
   - Header styling

4. **Panel**: Bordered sections for emphasis
   - Used for final summary

## Performance Impact

- **Minimal overhead**: Rich UI adds <100ms to total execution time
- **No slowdown**: Progress updates don't block enrichment threads
- **Memory efficient**: Uses streaming updates, not buffering

## Customization

### Change Colors

Edit the color codes in `batch_enrich.py`:
- `[cyan]` → `[blue]`, `[magenta]`, `[yellow]`
- `[green]` → success color
- `[red]` → error color

### Disable Colors

Set environment variable:
```bash
NO_COLOR=1 python scripts/batch_enrich.py --input file.csv --integrations linkedin_profile
```

### Change Progress Bar Style

Edit line 246-255 in `batch_enrich.py` to add/remove columns:
```python
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    # Add more columns here
    console=console,
) as progress:
```

## Comparison: Before vs After

### Before (Plain Text)
```
================================================================================
BATCH ENRICHMENT
================================================================================

Input: lead-list/gtm-influencers.csv
Integrations: linkedin_profile
Parallel workers: 4

📥 Loading CSV...
✓ Loaded 4 rows with 4 columns

🔍 Validating integrations...
✓ Loaded 1 integrations

📋 Validating columns...
✓ All required columns present

⚙️  Enriching 4 rows with 4 workers...
  Progress: 4/4 rows (3 success, 1 errors)

✓ Enrichment complete: 3 success, 1 errors
```

### After (Rich UI)
- Animated progress bar with live updates
- Color-coded success/error counts
- Formatted tables with borders
- Real-time time tracking
- Professional summary panel
- Better visual hierarchy

## Future Enhancements

Potential additions:
1. **Live table of recent rows** - Show last 5 rows being processed
2. **Per-integration progress** - Separate progress bar for each integration
3. **Detailed error logs** - Expandable error details with rich formatting
4. **Export HTML report** - Save rich output to HTML file
5. **Dashboard mode** - Full-screen TUI with panels for stats, logs, and progress

## Troubleshooting

### Progress bar not updating smoothly
- Check terminal width: `echo $COLUMNS`
- Ensure terminal supports ANSI colors: `tput colors`

### Colors not displaying
- Set `TERM=xterm-256color` in environment
- Or disable colors with `NO_COLOR=1`

### Unicode symbols broken
- Update terminal font to one supporting Unicode
- Or set `TERM=xterm` for ASCII fallback
