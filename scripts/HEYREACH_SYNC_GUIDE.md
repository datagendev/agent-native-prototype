# HeyReach Campaign Sync Guide

This guide explains how to sync HeyReach campaign results back to your Neon campaign tables.

## Overview

The sync system consists of two scripts:

1. **`update_campaign_heyreach_link.py`** - Links a Neon campaign to a HeyReach campaign
2. **`sync_heyreach_campaign_results.py`** - Syncs HeyReach results to Neon

## Workflow

### Step 1: Create HeyReach Campaign

1. Go to HeyReach dashboard
2. Create a new campaign (or use existing campaign)
3. Add your leads list to the campaign
4. Launch the campaign
5. **Note the HeyReach campaign ID** (found in the campaign URL or settings)

### Step 2: Link Neon Campaign to HeyReach Campaign

Run the helper script to link your campaigns:

```bash
cd /Users/yu-shengkuo/projects/datagendev/marketing/linkedin-outreach
source .venv/bin/activate

python scripts/update_campaign_heyreach_link.py \
  --campaign-id 5 \
  --heyreach-campaign-id YOUR_HEYREACH_CAMPAIGN_ID
```

**Example:**
```bash
python scripts/update_campaign_heyreach_link.py \
  --campaign-id 5 \
  --heyreach-campaign-id 12345
```

This will update the `campaigns` table with the HeyReach campaign ID.

### Step 3: Run Sync (Dry Run First)

Test the sync with a dry run to preview changes:

```bash
python scripts/sync_heyreach_campaign_results.py \
  --campaign-id 5 \
  --dry-run
```

This will show you what would be updated without making any changes.

### Step 4: Run Actual Sync

If the dry run looks good, run the actual sync:

```bash
python scripts/sync_heyreach_campaign_results.py --campaign-id 5
```

This will:
- Fetch leads from HeyReach campaign
- Fetch conversations for those leads
- Match them to prospects in your campaign table
- Update status, contacted_at, and responded_at fields
- Update aggregate metrics in the campaigns table

## Usage Examples

### Sync Specific Campaign

```bash
# Campaign 5 (Jordan Crawford GTM)
python scripts/sync_heyreach_campaign_results.py --campaign-id 5

# Future campaign 6
python scripts/sync_heyreach_campaign_results.py --campaign-id 6
```

### Sync All Campaigns

Sync all campaigns that have a `heyreach_campaign_id` set:

```bash
python scripts/sync_heyreach_campaign_results.py --all
```

### Manual Override

Override the HeyReach campaign ID (useful for testing):

```bash
python scripts/sync_heyreach_campaign_results.py \
  --campaign-id 5 \
  --heyreach-campaign-id 99999
```

### Dry Run

Preview changes without updating:

```bash
python scripts/sync_heyreach_campaign_results.py --campaign-id 5 --dry-run
```

## Automation with Cron

### Hourly Sync for All Campaigns

Add to your crontab:

```bash
crontab -e
```

Add this line:

```bash
0 * * * * cd /Users/yu-shengkuo/projects/datagendev/marketing/linkedin-outreach && source .venv/bin/activate && python scripts/sync_heyreach_campaign_results.py --all >> logs/sync.log 2>&1
```

### Hourly Sync for Specific Campaign

```bash
0 * * * * cd /Users/yu-shengkuo/projects/datagendev/marketing/linkedin-outreach && source .venv/bin/activate && python scripts/sync_heyreach_campaign_results.py --campaign-id 5 >> logs/sync.log 2>&1
```

### Daily Sync

```bash
0 9 * * * cd /Users/yu-shengkuo/projects/datagendev/marketing/linkedin-outreach && source .venv/bin/activate && python scripts/sync_heyreach_campaign_results.py --all >> logs/sync.log 2>&1
```

## What Gets Synced

### Campaign Table Updates

For each prospect in `campaign_{name}` table:

- **status**: Updated based on activity
  - `pending` → `contacted` (if outbound message sent)
  - `contacted` → `responded` (if inbound message received)
- **contacted_at**: Timestamp of first outbound message
- **responded_at**: Timestamp of first inbound message

### Campaigns Table Updates

Aggregate metrics in `campaigns` table:

- **contacted**: Count of prospects with contacted_at set
- **responded**: Count of prospects with responded_at set
- **last_synced_at**: Timestamp of last sync

## Troubleshooting

### Campaign has no heyreach_campaign_id set

**Error:**
```
❌ Campaign 5 (Jordan Crawford GTM Session - Link Requests) has no heyreach_campaign_id set
```

**Solution:**
Run `update_campaign_heyreach_link.py` first to link the campaigns.

### No LinkedIn accounts found

**Error:**
```
⚠️ No LinkedIn accounts found in HeyReach
```

**Solution:**
Check that your HeyReach MCP integration is connected in DataGen dashboard.

### Unmatched leads

If you see unmatched leads, it means some HeyReach leads don't exist in your Neon campaign table. This can happen if:
- Leads were added directly in HeyReach (not from your Neon campaign)
- LinkedIn URLs don't match exactly

## Finding Your HeyReach Campaign ID

1. Go to HeyReach dashboard
2. Click on your campaign
3. Look at the URL: `https://app.heyreach.io/campaigns/{campaign_id}`
4. Or check the campaign settings page

## Database Schema

### Campaign Tables

Each campaign has its own table: `campaign_{sanitized_name}`

Columns updated by sync:
- `status` (text): pending, contacted, responded, stopped, converted
- `contacted_at` (timestamptz): When first outbound message was sent
- `responded_at` (timestamptz): When first inbound message was received

### Campaigns Table

Central registry table:

- `heyreach_campaign_id` (integer): HeyReach campaign ID
- `heyreach_list_id` (integer): HeyReach list ID
- `contacted` (integer): Count of contacted prospects
- `responded` (integer): Count of responded prospects
- `last_synced_at` (timestamptz): Last sync timestamp
