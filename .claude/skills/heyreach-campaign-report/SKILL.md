---
name: heyreach-campaign-report
description: Generate HeyReach campaign performance reports and append AI strategic recommendations
---

# HeyReach Campaign Report Skill

Analyzes HeyReach campaign performance using atomic scripts with intermediate storage for fault tolerance and composability.

## Architecture: Agent-Native Pattern

This skill uses the MCP / SDK / Claude three-tier pattern:

```
Step 1 (MCP):    Fetch campaigns via executeTool
Step 2 (Claude): AskUserQuestion → user selects campaigns
Step 3 (SDK):    4 atomic scripts with /tmp/ intermediate storage
Step 4 (Claude): Read report → Append AI Strategic Analysis
```

### Intermediate Storage

```
/tmp/heyreach-{YYYY-MM-DD}/
├── campaigns.json              # Step 1 output
├── conversations/
│   ├── {campaign_id}.json      # Step 2 output (per campaign)
│   └── ...
├── metrics.json                # Step 3 output
└── report.md                   # Step 4 output
```

**Benefits:**
- Skip steps if intermediate files exist
- Re-run only failed steps
- Claude can inspect any intermediate file
- Mix and match for different analyses

## Usage

```bash
/heyreach-campaign-report
```

## Workflow

### Step 1: Fetch Campaigns (MCP)

First, fetch available campaigns using `executeTool`:

```json
{
  "tool_alias_name": "mcp_Heyreach_get_all_campaigns",
  "parameters": {
    "statuses": [],
    "limit": 100
  }
}
```

### Step 2: Ask User Which Campaigns to Analyze

**IMPORTANT:** Use `AskUserQuestion` to let user select campaigns.

Build options from the fetched campaigns. Example:

```json
{
  "questions": [
    {
      "question": "Which campaigns should I analyze?",
      "header": "Campaigns",
      "multiSelect": true,
      "options": [
        {
          "label": "Claude-code (FINISHED)",
          "description": "ID: 291852 | 27 leads | List: Jordan Crawford GTM"
        },
        {
          "label": "PH_founder (FINISHED)",
          "description": "ID: 210501 | 18 leads | List: PH_July"
        },
        {
          "label": "All finished campaigns",
          "description": "Analyze all campaigns with FINISHED status"
        }
      ]
    }
  ]
}
```

**Option building rules:**
- Include campaign name and status in label
- Include ID, lead count, and list name in description
- Add "All finished campaigns" option for convenience
- Use `multiSelect: true` to allow selecting multiple campaigns

### Step 3: Run Pipeline (SDK)

Based on user selection, execute the 4 atomic scripts. **Always activate venv first.**

```bash
cd /Users/yu-shengkuo/projects/datagendev/marketing/linkedin-outreach
source .venv/bin/activate

# Step 3a: Fetch campaigns (use IDs from user selection)
python scripts/heyreach/fetch_campaigns.py --ids 291852,210501

# Step 3b: Fetch conversations
python scripts/heyreach/fetch_conversations.py

# Step 3c: Calculate metrics
python scripts/heyreach/calculate_metrics.py

# Step 3d: Generate report
python scripts/heyreach/generate_report.py
```

**Mapping user selection to script args:**
- Specific campaigns selected → `--ids 291852,210501`
- "All finished campaigns" selected → `--status FINISHED`
- User typed custom filter → `--keyword "search term"`

**Skip optimization:** Check if intermediate files exist before running:
- Skip `fetch_campaigns.py` if `/tmp/heyreach-{date}/campaigns.json` exists
- Skip `fetch_conversations.py` if `/tmp/heyreach-{date}/conversations/` has files
- Use `--skip-existing` flag in fetch_conversations.py to skip already-fetched campaigns

### Step 4: AI Strategic Analysis (Claude)

After report is generated:

1. Read: `reports/heyreach/campaign-report-{YYYY-MM-DD}.md`
2. Analyze the data holistically
3. Append new section: `## AI Strategic Analysis`
4. Include:
   - Pattern recognition across campaigns
   - Strategic recommendations and prioritization
   - Messaging insights from top vs. underperformers
   - Risk assessment and replication opportunities

## Script Reference

### fetch_campaigns.py

Fetch campaigns from HeyReach API.

```bash
python scripts/heyreach/fetch_campaigns.py
python scripts/heyreach/fetch_campaigns.py --ids 291852,210501
python scripts/heyreach/fetch_campaigns.py --status FINISHED
python scripts/heyreach/fetch_campaigns.py --keyword "Claude"
```

**Input:** None (API call)
**Output:** `/tmp/heyreach-{date}/campaigns.json`

### fetch_conversations.py

Fetch conversations for each campaign.

```bash
python scripts/heyreach/fetch_conversations.py
python scripts/heyreach/fetch_conversations.py --skip-existing
python scripts/heyreach/fetch_conversations.py --campaign-ids 291852,210501
```

**Input:** `/tmp/heyreach-{date}/campaigns.json`
**Output:** `/tmp/heyreach-{date}/conversations/{campaign_id}.json`

### calculate_metrics.py

Calculate reply rates, meeting detection, performance levels.

```bash
python scripts/heyreach/calculate_metrics.py
```

**Input:** `/tmp/heyreach-{date}/campaigns.json`, `/tmp/heyreach-{date}/conversations/`
**Output:** `/tmp/heyreach-{date}/metrics.json`

### generate_report.py

Generate markdown report from metrics.

```bash
python scripts/heyreach/generate_report.py
python scripts/heyreach/generate_report.py --output reports/custom-report.md
```

**Input:** `/tmp/heyreach-{date}/metrics.json`
**Output:** `/tmp/heyreach-{date}/report.md`, `reports/heyreach/campaign-report-{date}.md`

## Error Handling

Each script uses error-first pattern. If a step fails:

1. Check the error message
2. Inspect intermediate files in `/tmp/heyreach-{date}/`
3. Fix the issue
4. Re-run only the failed step (intermediate files preserved)

## Key Metrics

- **Reply Rate**: % of connection requests that received a response
  - Good: 10-20%, Excellent: >20%
- **Avg Messages per Reply**: Conversation depth indicator
  - Higher = more engaged conversations
- **Meeting Detection Rate**: % with meeting-related keywords
  - Good: 3-7%, Excellent: >7%

## Requirements

- Virtual environment: `.venv/` in project directory
- Environment: `DATAGEN_API_KEY` set (from `../.env`)
- MCP Servers: HeyReach connected in DataGen

## Example Session

```
User: /heyreach-campaign-report

Claude: Let me fetch your HeyReach campaigns...
[Calls executeTool: mcp_Heyreach_get_all_campaigns]

Claude: [Uses AskUserQuestion]
┌─────────────────────────────────────────────────────────┐
│ Which campaigns should I analyze?                       │
│                                                         │
│ ○ Claude-code (FINISHED)                               │
│   ID: 291852 | 27 leads | List: Jordan Crawford GTM    │
│                                                         │
│ ○ PH_founder (FINISHED)                                │
│   ID: 210501 | 18 leads | List: PH_July                │
│                                                         │
│ ○ All finished campaigns                               │
│   Analyze all campaigns with FINISHED status           │
└─────────────────────────────────────────────────────────┘

User: [Selects "Claude-code (FINISHED)"]

Claude: Running pipeline for campaign 291852...
  Step 1: Fetching campaign data...
  Step 2: Fetching conversations... (27 found)
  Step 3: Calculating metrics...
  Step 4: Generating report...

Report saved to: reports/heyreach/campaign-report-2026-01-10.md

Now let me add strategic analysis...
[Reads report, appends AI Strategic Analysis section]

Done! Full report with AI insights saved.
```
