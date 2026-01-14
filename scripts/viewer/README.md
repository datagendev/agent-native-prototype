# Enrichment Data Viewer

Interactive web-based viewer for enriched CSV data built with Bun + React + TypeScript.

## Features

### 📋 Table View
- Interactive data grid with sorting
- Search across all columns
- Filter columns (all/enriched/original)
- Pagination (25 rows per page)
- Export to CSV

### 🔄 Workflow View
- Visual pipeline diagram
- Integration statistics
- Success/error metrics
- Performance breakdown

## Quick Start

```bash
# Auto-detect latest enriched CSV and open browser
bun run start --open

# Specify file
bun run start --file ../../lead-list/prospects_enriched.csv

# Development mode with hot reload
bun run dev --open
```

## Usage

### Command-Line Options

- `--file <path>` - Path to enriched CSV file (default: auto-detect latest)
- `--port <number>` - Port to run server on (default: 3001)
- `--open` - Automatically open browser

### Examples

```bash
# Development with hot reload
bun run dev --file ../../lead-list/gtm-influencers_enriched.csv --open

# Production mode on custom port
bun run start --file ../../lead-list/prospects_enriched.csv --port 3000

# Auto-detect latest enriched file
bun run start --open
```

## Integration with Batch Enrichment

After running `batch_enrich.py`:

```bash
# 1. Enrich leads
python scripts/batch_enrich.py \
  --input lead-list/prospects.csv \
  --integrations linkedin_profile,heyreach_engagement

# 2. View results
cd scripts/viewer
bun run start --open
```

The viewer will automatically detect the latest `*_enriched.csv` file.

## Tech Stack

- **Bun**: JavaScript runtime and bundler
- **React 19**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling (via CDN)

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3001
lsof -ti:3001 | xargs kill -9

# Or use a different port
bun run start --port 3002
```

### CSV Not Found

Ensure enriched CSV exists in `../../lead-list/` with `_enriched` in filename, or specify with `--file`.
