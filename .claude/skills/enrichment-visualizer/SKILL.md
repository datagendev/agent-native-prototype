# Enrichment Visualizer

## Purpose

Visualize enriched lead data with interactive table and workflow views.

## Features

1. **Table View**: Interactive data grid with:
   - Sorting by any column
   - Filtering and search
   - Column visibility toggle
   - Export to CSV
   - Responsive design

2. **Workflow View**: Visual pipeline showing:
   - Enrichment steps and sequence
   - Success/error/skip statistics
   - Integration dependencies
   - Performance metrics

## Usage

### As a Skill (via Claude)

```
User: "Show me the enriched leads"
Claude: [Invokes enrichment-visualizer skill]
        [Starts Bun server on port 3030]
        [Opens browser to http://localhost:3030]
```

### Manual Usage

```bash
# From project root
cd .claude/skills/enrichment-visualizer

# Start server
~/.bun/bin/bun run server.ts --file ../../../lead-list/gtm-influencers_enriched.csv

# Open browser
open http://localhost:3030
```

## Command-Line Arguments

- `--file <path>`: Path to CSV file (default: latest _enriched.csv in lead-list/)
- `--port <port>`: Port to run server on (default: 3030)
- `--open`: Automatically open browser

## Examples

```bash
# View specific file
bun run server.ts --file lead-list/prospects_enriched.csv --open

# Custom port
bun run server.ts --port 8080

# Auto-detect latest enriched file
bun run server.ts --open
```

## Requirements

- Bun runtime (~/.bun/bin/bun)
- CSV file with enriched data
- Modern web browser

## File Structure

```
.claude/skills/enrichment-visualizer/
├── SKILL.md                 # This file
├── server.ts                # Bun server
├── package.json             # Dependencies
└── public/
    ├── index.html           # Landing page
    ├── table.html           # Table view
    ├── workflow.html        # Workflow view
    └── styles.css           # Shared styles
```

## API Endpoints

- `GET /` - Landing page with navigation
- `GET /api/data` - Get CSV data as JSON
- `GET /api/stats` - Get enrichment statistics
- `GET /api/integrations` - Get available integrations metadata
- `GET /table` - Table view page
- `GET /workflow` - Workflow view page

## Technologies

- **Bun**: Fast JavaScript runtime and bundler
- **Native Web APIs**: No heavy frameworks, just vanilla JS
- **TailwindCSS**: Utility-first CSS (via CDN)
- **Chart.js**: Workflow visualization (via CDN)
