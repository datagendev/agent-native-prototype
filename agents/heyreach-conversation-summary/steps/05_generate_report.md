# Step 5: Generate HTML Report

## Contract

| Field | Value |
|-------|-------|
| step_id | `05_generate_report` |
| Producer | `datagen_sdk` (Python script) |
| Output path | `reports/heyreach/conversation-summary-{date}.html` |
| Output format | `html` |
| Downstream | Step 06 (email) |

## Command

```bash
source .venv/bin/activate && python scripts/heyreach/generate_conversation_summary.py
```

## What It Does

1. Reads `digest.json` for data and `analysis.md` for AI insights
2. Renders HTML using the conversation-summary template
3. Builds sections: summary cards, noteworthy, AI analysis, conversations table
4. Saves branded HTML report

## Input

- `/tmp/heyreach-summary-{date}/digest.json` (required)
- `/tmp/heyreach-summary-{date}/analysis.md` (optional, included if available)

## Output

HTML report at `reports/heyreach/conversation-summary-{date}.html` with:
- Header with title and date range
- Summary cards (active conversations, replies, meeting signals, campaigns)
- Noteworthy conversations table (meeting signals + high engagement)
- AI analysis section (themes, patterns, recommendations)
- Full conversations table with status badges

## Template

Located at `agents/heyreach-conversation-summary/templates/conversation-summary.html`.
Falls back to `.claude/skills/generate-report/templates/base-email.html` if custom template is missing.

## Validation

- HTML file exists and is non-empty
- Open in browser to verify sections render correctly
- Check that data populates (not all zeros or empty tables)

## Error Recovery

- If template is missing, script falls back to base template
- If analysis.md is missing, report generates without AI analysis section
- Re-run is safe (overwrites previous report)
