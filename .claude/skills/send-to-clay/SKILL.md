---
name: send-to-clay
description: Send lead list to a designated Clay table via webhook
---

# Skill: Send to Clay

Send enriched leads from your lead list to a Clay table via webhook integration.

## Overview

Clay tables accept data through **webhook URLs**. This skill:
1. Accepts a lead list reference or CSV file
2. Sends each row to your Clay table webhook
3. Handles batching and error recovery
4. Provides success/failure reporting

## When to Use This Skill

Use when you want to:
- Push enriched leads to Clay for prospecting workflows
- Sync leads from DataGen enrichment to Clay
- Integrate with Clay's workspace for further processing
- Batch upload leads with progress tracking

**Usage:**
```
/send-to-clay [lead_list_name] [--webhook-url URL] [--batch-size 10] [--dry-run]
```

## Interactive Workflow

Just invoke `/send-to-clay` and the skill will guide you through the process:

### Step 1: Select Lead List

You'll be asked which lead list to send:

```
Which lead list would you like to send to Clay?
• gtm-engineers-series-a (45 leads)
• example-leads (120 leads)
• Other: [enter custom path]
```

The skill scans `leads/` directory and shows available lead lists with row counts.

### Step 2: Provide Clay Webhook URL

You'll be asked for the Clay table webhook URL:

```
Enter the Clay table webhook URL.

Where to find it:
1. Open the Clay table in your workspace
2. Go to Settings → Integrations or Webhooks
3. Copy the webhook URL (starts with https://api.clay.com/webhooks/)

Webhook URL:
```

### Step 3: Preview & Confirm

The skill loads your leads and shows a preview:

```
Lead list: gtm-engineers-series-a
Total leads: 45
Source: SQLite database (completed rows only)

Preview (first 3 rows):
  1. John Doe (john@example.com)
  2. Jane Smith (jane@example.com)
  3. Bob Johnson (bob@example.com)

Send to Clay: https://api.clay.com/webhooks/abc123?
• Yes, send now
• No, cancel
• Dry-run (preview only)
```

### Step 4: Monitor Progress

The skill sends in batches and displays:
- ✓ Batch 1 (rows 1-10): SUCCESS
- ✓ Batch 2 (rows 11-20): SUCCESS
- ✗ Batch 3 (rows 21-30): FAILED - Rate limit exceeded
- Summary: X/Y rows sent successfully

## How It Works

### Data Mapping

Clay tables expect JSON objects. The skill automatically:
1. **Reads your lead list** (CSV or SQLite database)
2. **Converts each row to JSON** with column headers as keys
3. **Sends via POST to webhook** with proper formatting
4. **Handles batching** to avoid rate limits (default: 10 rows at a time)
5. **Retries failed rows** up to 3 times

**Example payload sent to Clay:**
```json
{
  "URL": "https://linkedin.com/in/example",
  "name": "John Doe",
  "company": "Acme Corp",
  "posts_last_30_days": 5,
  "claude_mentions_count": 2,
  ...
}
```

### Error Handling

If a row fails:
- ✗ Displays error message (e.g., "Invalid JSON", "Rate limit exceeded")
- Retries up to 3 times with exponential backoff
- Marks row as failed after final retry
- Continues with remaining rows

## Implementation Details

The skill is implemented as a Python script: `scripts/send_to_clay.py`

Usage:
```bash
source .venv/bin/activate && python scripts/send_to_clay.py \
  --lead-list gtm-engineers-series-a \
  --webhook-url https://api.clay.com/webhooks/abc123 \
  [--batch-size 10] \
  [--dry-run] \
  [--max-retries 3]
```

### Script Features

- **CSV loading**: Reads from `leads/{name}/table.csv`
- **SQLite loading**: Reads from `leads/{name}/table.db` (completed rows only)
- **Webhook batching**: Sends 10 rows per request (configurable)
- **Retry logic**: Up to 3 retries with exponential backoff (1s, 2s, 4s)
- **Progress tracking**: Live updates as rows are sent
- **Dry run mode**: Preview without sending

### Example Script Output

```
Send to Clay: gtm-engineers-series-a
Webhook: https://api.clay.com/webhooks/abc123
Mode: dry-run (preview only)

Loading leads...
Found 45 leads in leads/gtm-engineers-series-a/table.csv

Preview (first 3 rows):
  1. John Doe (john@example.com)
  2. Jane Smith (jane@example.com)
  3. Bob Johnson (bob@example.com)

Ready to send 45 rows in batches of 10.

Use --dry-run=false to actually send data.
```

### Real Run Output

```
Send to Clay: gtm-engineers-series-a
Webhook: https://api.clay.com/webhooks/abc123

Sending in batches of 10...

Batch 1 (rows 1-10): ✓ SUCCESS
Batch 2 (rows 11-20): ✓ SUCCESS
Batch 3 (rows 21-30): ✓ SUCCESS
Batch 4 (rows 31-40): ✓ SUCCESS
Batch 5 (rows 41-45): ✓ SUCCESS

Summary:
  Total rows: 45
  Sent: 45 ✓
  Failed: 0 ✗
  Success rate: 100%

All leads sent to Clay successfully!
```

## Webhook URL Security

**Important**: Never commit webhook URLs to git.

Store in environment variables:
```bash
# In .env (not committed)
CLAY_WEBHOOK_URL="https://api.clay.com/webhooks/abc123"

# Use in script
export $(cat ../.env | xargs)
/send-to-clay gtm-engineers-series-a --webhook-url $CLAY_WEBHOOK_URL
```

Or pass directly (not recommended in production):
```bash
/send-to-clay gtm-engineers-series-a --webhook-url https://api.clay.com/webhooks/abc123
```

## Troubleshooting

**"Webhook URL not found"**
- Copy the full webhook URL from Clay table settings
- Verify URL starts with `https://api.clay.com/webhooks/`
- Check that URL is not truncated

**"Lead list not found"**
- Use exact lead list name: `gtm-engineers-series-a`
- Check folder exists: `leads/gtm-engineers-series-a/`
- Try CSV path: `leads/gtm-engineers-series-a/table.csv`

**"Rate limit exceeded"**
- Clay API has rate limits (typically 100 req/min)
- Reduce batch size: `--batch-size 5`
- Increase delay between batches (script auto-handles with backoff)

**"Invalid JSON"**
- Some column values may not be JSON-serializable
- Script automatically converts to strings
- Contact support if issue persists

**"Column mismatch"**
- Your CSV columns may not match Clay table schema
- Use `--dry-run` first to see what will be sent
- Adjust column names in lead list if needed

## Next Steps

After sending to Clay:
1. Check Clay table for incoming leads
2. Set up Clay enrichment workflows
3. Configure Clay-to-CRM sync (HubSpot, Salesforce, etc.)
4. Monitor outreach performance

## Resources

- [Clay Webhook Documentation](https://university.clay.com/docs/webhooks)
- [Clay HTTP API Guide](https://university.clay.com/docs/http-api-integration-overview)
- [DataGen Lead Enrichment Skill](/send-to-clay#see-also)

## Related Skills

- `/enrichment` - Enrich leads before sending
- `/build-integrations` - Create custom integrations
