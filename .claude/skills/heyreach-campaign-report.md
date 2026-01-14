# HeyReach Campaign Report

Generate performance reports for HeyReach campaigns with real engagement metrics from conversation analysis.

## Description

Analyzes HeyReach campaign performance by fetching actual conversations and extracting metrics: reply rates, message engagement depth, and meeting bookings. Compares campaigns against industry benchmarks to identify top performers and areas for optimization.

## Usage

```bash
# Interactive mode (recommended) - lists campaigns and asks you to select
/heyreach-campaign-report

# Analyze all campaigns (no listing, direct analysis)
/heyreach-campaign-report --analyze-all

# Analyze specific campaigns by ID
/heyreach-campaign-report --campaigns 12345,67890

# Filter by campaign status (lists matching campaigns)
/heyreach-campaign-report --status IN_PROGRESS
/heyreach-campaign-report --status PAUSED

# Filter by keyword (lists matching campaigns)
/heyreach-campaign-report --keyword "VPs Engineering"

# Combine filters
/heyreach-campaign-report --status IN_PROGRESS --keyword "Q1-2026"
```

## Parameters

- `--campaigns` (optional): Comma-separated campaign IDs to analyze
- `--status` (optional): Filter by campaign status (IN_PROGRESS, PAUSED, FINISHED, etc.)
- `--keyword` (optional): Search campaigns by name/keyword
- `--days` (optional): Date range for stats (default: 30 days)
- `--output` (optional): Output location (default: `reports/heyreach-campaign-report-{date}.md`)

## What It Does

### Step 0a: Ask Filter Preference
Asks you how you want to filter campaigns:
- **All campaigns**: Show every campaign in HeyReach
- **By Status**: Filter to FINISHED, IN_PROGRESS, PAUSED, CANCELED, DRAFT, FAILED, STARTING
- **By Keyword**: Search campaigns by name (e.g., "Claude", "Product Hunt", etc.)

### Step 0b: Fetch & Display Campaigns
Calls `executeTool(mcp_Heyreach_get_all_campaigns)` with parameters based on filter choice:
- **All campaigns**: Empty `statuses` and `keyword` arrays
- **By Status**: Populate `statuses` array with chosen status (e.g., `["FINISHED"]`)
- **By Keyword**: Populate `keyword` parameter (e.g., `"Claude"`)
- All calls use `limit: 100, offset: 0`

See "Skill Execution Flow" section below for exact executeTool parameters and format response as table:
- Campaign ID
- Campaign Name
- Status
- Connection Requests Sent
- Created Date

### Step 0c: Select Campaigns to Analyze
Asks you which campaigns to analyze (by specific ID(s), name(s), or all displayed campaigns)

### Steps 1-6: Generate Report and Analysis
Executes Python script: `python scripts/heyreach_campaign_report.py --campaigns <selected_ids>`

1. **Get Conversations**: Calls `mcp_Heyreach_get_conversations_v2` for each selected campaign to extract real engagement data
2. **Analyze Conversations**:
   - Counts replies (messages where correspondent replied)
   - Detects meeting bookings (keyword matching in conversation text)
   - Calculates avg messages per replied lead (engagement depth)
3. **Calculate Metrics**:
   - Reply Rate = replies / connection requests sent
   - Meeting Rate = meetings booked / connection requests sent
   - Avg Messages per Reply = total messages in replied conversations / reply count
4. **Compare Against Benchmarks**:
   - Reply rate: <10% low, 10-20% good, >20% excellent
   - Meeting rate: <3% low, 3-7% good, >7% excellent
5. **Create Report**: Generates markdown report with campaign table, top performers, and action items
6. **AI Strategic Analysis**: Reads generated report and appends comprehensive strategic analysis with portfolio health assessment, performance patterns, and recommendations

## Output Format

The skill generates a markdown report with:

### 📊 Executive Summary
- Connection Requests Sent (total leads contacted)
- Successfully Completed / Failed / In Progress counts
- **Engagement Metrics** (as % of connection requests sent):
  - Reply Rate with total reply count
  - Avg Messages per Replied Lead (engagement depth)
  - Meeting Booking Rate with total meetings booked

### 🚨 Campaigns Needing Attention
- Canceled campaigns (with recommendation to review)
- Low-performing campaigns with reply rates below 10%

### 🏆 Top Performing Campaigns
- Ranked by reply rate
- Shows connection requests, replies, avg messages per reply, meetings booked
- Identifies campaigns exceeding benchmarks

### 📈 All Campaigns Overview Table
| Campaign Name | Status | Requests | Replies | Reply % | Avg Msgs | Meetings | Rating |
|--------------|--------|----------|---------|---------|----------|----------|--------|
| Claude-code  | FINISHED | 27 | 7 | 25.9% | 15.9 | 5 | 🏆 |
| PH_founder | FINISHED | 18 | 0 | 0.0% | 0 | 0 | ❓ |

### 📋 Action Items
- High priority actions (campaigns to pause, urgent reviews)
- Medium priority actions (campaigns to replicate)

## Example Output

```markdown
# HeyReach Campaign Performance Report

**Generated**: 2026-01-09 15:10
**Campaigns Analyzed**: 3

---

## 📊 Executive Summary

### Volume Metrics
- **Connection Requests Sent**: 58
- **Successfully Completed**: 26
- **Failed**: 2
- **Still In Progress**: 23

### Engagement Metrics (as % of connection requests sent)
- **Reply Rate**: 12.1% (7 replies)
- **Avg Messages per Replied Lead**: 15.9 messages
- **Meeting Booking Rate**: 8.6% (5 meetings booked)

**Note**: Acceptance rate requires CONNECTION_REQUEST_ACCEPTED webhook tracking

### Campaign Status Distribution
- ✅ Finished: 2 campaigns
- ❌ Canceled: 1 campaigns
- ▶️ In Progress: 0 campaigns

---

## 🚨 Campaigns Needing Attention

### Campaign: "GTM engineers" ❌
- **Status**: CANCELED
- **Leads**: 13 total
- **Progress**: 6 in progress, 0 failed
- **List**: Clay Bootcamp Prospects - Dec 2025
- **Recommendation**: Review cancellation reason, decide whether to resume or archive

---

## 🏆 Top Performing Campaigns

### 1. "Claude-code " 🏆
- **Connection Requests Sent**: 27
- **Reply Rate**: 25.9% (7 replies)
- **Avg Messages per Reply**: 15.9 messages
- **Meeting Rate**: 18.5% (5 meetings)
- **List**: Jordan Crawford GTM - Claude Code Tutorials
- **Created**: 2025-12-27

### 2. "PH_founder" ❓
- **Connection Requests Sent**: 18
- **Reply Rate**: 0.0% (0 replies)
- **Avg Messages per Reply**: 0 messages
- **Meeting Rate**: 0.0% (0 meetings)
- **List**: PH_July
- **Created**: 2025-09-11

---

## 📈 All Campaigns Overview

| Campaign Name | Status | Requests | Replies | Reply % | Avg Msgs | Meetings | Rating |
|--------------|--------|----------|---------|---------|----------|----------|--------|
| Claude-code  | FINISHED | 27 | 7 | 25.9% | 15.9 | 5 | 🏆 |
| PH_founder | FINISHED | 18 | 0 | 0.0% | 0 | 0 | ❓ |
| GTM engineers | CANCELED | 13 | 0 | 0.0% | 0 | 0 | ❌ |

---

## 💡 Recommendations

### Medium Priority

1. **Replicate "Claude-code " success**
   - Reason: Campaign achieving 25.9% reply rate and 18.5% meeting rate
   - Recommendation: Extract message template and personalization strategy to apply to other campaigns

---

## 📋 Action Checklist

- [ ] Replicate "Claude-code " success

---

*Report generated by DataGen HeyReach Campaign Analyzer*
*Next scheduled report: 2026-01-16*
```

## Technical Implementation

### Script Location
```
scripts/heyreach_campaign_report.py
```

### Skill Execution Flow

**Interactive Campaign Discovery (Option 3 Workflow):**

1. **Step 0a**: Skill asks filter preference
   - All campaigns
   - By Status (FINISHED, IN_PROGRESS, CANCELED, etc.)
   - By Keyword (search campaign names)

2. **Step 0b**: Uses `executeTool(mcp_Heyreach_get_all_campaigns)` to fetch matching campaigns

**executeTool Parameters by Filter Type:**

**All Campaigns:**
```json
{
  "tool_alias_name": "mcp_Heyreach_get_all_campaigns",
  "parameters": {
    "statuses": [],
    "accountIds": [],
    "keyword": "",
    "limit": 100,
    "offset": 0
  }
}
```

**By Status (example: FINISHED):**
```json
{
  "tool_alias_name": "mcp_Heyreach_get_all_campaigns",
  "parameters": {
    "statuses": ["FINISHED"],
    "accountIds": [],
    "keyword": "",
    "limit": 100,
    "offset": 0
  }
}
```

**By Keyword (example: "Claude"):**
```json
{
  "tool_alias_name": "mcp_Heyreach_get_all_campaigns",
  "parameters": {
    "statuses": [],
    "accountIds": [],
    "keyword": "Claude",
    "limit": 100,
    "offset": 0
  }
}
```

**Valid Status Values:** `DRAFT`, `IN_PROGRESS`, `PAUSED`, `FINISHED`, `CANCELED`, `FAILED`, `STARTING`

**Display Results:**
   - Format response as table with: Campaign ID, Campaign Name, Status, Requests, Created date
   - Example output:
     ```
     | Campaign ID | Campaign Name | Status | Requests | Created |
     |-------------|---------------|--------|----------|---------|
     | 291852 | Claude-code | FINISHED | 27 | 2025-12-27 |
     | 210501 | PH_founder | FINISHED | 18 | 2025-09-11 |
     ```

3. **Step 0c**: Skill asks user to select campaigns
   - By specific IDs: `291852,210501`
   - By names: `Claude-code, PH_founder`
   - All displayed campaigns

4. **Step 1-5**: Runs Python script with selected campaign IDs
   ```bash
   source .venv/bin/activate && python scripts/heyreach_campaign_report.py --campaigns 291852,210501
   ```

5. **Step 6**: Appends AI Strategic Analysis to generated report

### Direct Script Execution (Legacy)
```bash
# Activate virtual environment
source .venv/bin/activate

# Run with specific campaigns
python scripts/heyreach_campaign_report.py --campaigns 291852,210501

# Run with filters (note: skill handles discovery instead)
python scripts/heyreach_campaign_report.py --status FINISHED
python scripts/heyreach_campaign_report.py --keyword "Claude"
```

### MCP Tools Used
- `mcp_Heyreach_get_all_campaigns` - Fetch campaign list with filtering
- `mcp_Heyreach_get_conversations_v2` - Get actual conversations for each campaign

### Metrics Calculation
- **Reply Rate**: Count of correspondent replies ÷ total connection requests sent × 100
- **Meeting Rate**: Count of conversations with meeting keywords ÷ total connection requests sent × 100
- **Avg Messages per Reply**: Total messages in replied conversations ÷ number of replied conversations

### Benchmarks
- **Reply Rate**: <10% low, 10-20% good, >20% excellent
- **Meeting Rate**: <3% low, 3-7% good, >7% excellent

### Error Handling
- Graceful fallback if conversations API fails for a campaign
- Reports campaigns with no conversations as having 0% reply rate
- Continues processing even if some campaigns fail

## Save Location

Reports are saved to:
```
reports/heyreach/campaign-report-{YYYY-MM-DD}.md
```

For specific campaigns:
```
reports/heyreach/campaign-{campaign_id}-report-{YYYY-MM-DD}.md
```

## Key Insights from Report

The report focuses on **engagement quality** not just volume:

1. **Reply Rate** shows what % of connection requests get actual responses
2. **Avg Messages per Reply** shows how deep the conversation goes (15+ = strong engagement)
3. **Meeting Rate** is the ultimate goal - % of requests that lead to booked meetings

For Brady's use case:
- Claude-code campaign: 25.9% reply rate is excellent (>20% benchmark)
- 15.9 avg messages per reply means people are having real conversations
- 18.5% meeting rate is strong conversion

## Tips for Brady

1. **Track Engagement Depth**: Focus on "Avg Messages per Reply" - this shows conversation quality
2. **Client-Specific Reports**: Use `--keyword "ClientName"` to generate weekly client reports
3. **Find Underperformers**: Use `--status FINISHED` to see which campaigns need rework
4. **Compare Against Benchmarks**: Campaigns with >20% reply rate are excellent, >10% is good
5. **Meeting Booking Signals**: High avg messages often correlates with meeting bookings - nurture those conversations

## Implementation Notes

- **Webhooks for Better Data**: Currently uses conversation text for meeting detection. Set up `CONNECTION_REQUEST_ACCEPTED` webhook for true acceptance rates
- **Keywords for Meeting Detection**: Currently searches conversation text for keywords like "book", "schedule", "meeting". This is crude but works for basic detection
- **Conversation Depth**: 15+ messages per conversation indicates sustained engagement and likely high-value prospects

## Requirements

- Virtual environment with `datagen_sdk` installed
- `DATAGEN_API_KEY` environment variable set
- `.env` file in parent directory with API key (recommended)
