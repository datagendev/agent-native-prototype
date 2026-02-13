---
name: instantly-analytics
description: Analyze Instantly email infrastructure health, campaign performance, and inbox status. Supports 4 report modes - domain health, campaign performance, inbox status, and summary.
---

# Instantly Analytics Skill

Analyzes Instantly email infrastructure using direct API v2 calls with intermediate storage for composability and fault tolerance.

## Architecture: Script -> /tmp/ -> Claude Reads -> Insight

```
Step 1 (Script):  fetch_data.py -> /tmp/instantly-analytics/raw/
Step 2 (Script):  report_*.py   -> /tmp/instantly-analytics/{report}.json
Step 3 (Claude):  Read JSON     -> present table + strategic analysis
```

### Intermediate Storage

```
/tmp/instantly-analytics/
├── raw/
│   ├── accounts.json              # All email accounts (with warmup_status, stat_warmup_score)
│   ├── account_analytics.json     # Daily per-account sent/bounced (date-scoped by --days)
│   ├── campaign_analytics.json    # Per-campaign aggregate metrics (all-time from API)
│   ├── replies.json               # Received campaign emails (all-time from API, filtered by --days in reports)
│   └── warmup.json                # Per-domain warmup health
├── domain_health.json             # Report: deliverability per domain
├── campaign_performance.json      # Report: campaign funnel + sentiment
└── inbox_status.json              # Report: account health + utilization
```

## Usage

```
/instantly-analytics domain-health
/instantly-analytics campaign-performance
/instantly-analytics inbox-status
/instantly-analytics summary
```

If user says just `/instantly-analytics` without a mode, ask which report they want.

## Important: --days Must Be Consistent

The `--days N` parameter controls the lookback window. **Pass the same value to both fetch and report scripts.**

- `fetch_data.py --days N`: scopes `account_analytics.json` (sent/bounced) to last N days
- `report_*.py --days N`: filters `replies.json` by `timestamp_created` to last N days

**Why this matters:** The `/emails` API returns ALL-TIME replies (no date filter param). Without `--days` filtering in reports, reply rates will be inflated -- old replies counted against recent sends. Both sides of the ratio must use the same window.

```bash
# Correct: same --days everywhere
source .venv/bin/activate && python .claude/skills/instantly-analytics/scripts/fetch_data.py --days 14
source .venv/bin/activate && python .claude/skills/instantly-analytics/scripts/report_domain_health.py --days 14
```

## Workflow

### For Every Mode

**Step 1: Fetch raw data (skip if cached)**

Check if `./tmp/instantly-analytics/raw/account_analytics.json` exists:
- If yes: skip fetch (data is cached from earlier in the session)
- If no, or if user says "fresh" / "force" / "refetch": run fetch with `--force`

```bash
source .venv/bin/activate && python .claude/skills/instantly-analytics/scripts/fetch_data.py --days 30
```

Add `--force` if user requests fresh data.

### Mode: `domain-health`

**Step 2: Generate report**
```bash
source .venv/bin/activate && python .claude/skills/instantly-analytics/scripts/report_domain_health.py --days 30
```

**Step 3: Read and present**
Read `./tmp/instantly-analytics/domain_health.json` and present:

1. **Summary line**: period, total domains, total sent, overall reply rate, overall bounce rate
2. **Table** -- only show sending domains (sent > 0), sorted by reply rate desc:

| Domain | Sent | Replies | Reply % | Bounced | Bounce % | Accounts |
|--------|------|---------|---------|---------|----------|----------|

3. **Non-sending domains**: list as a summary line (X domains with 0 sends)
4. **Strategic Analysis**:
   - Which domains have the best reply rates? Any standout performers?
   - Which domains have concerning bounce rates (>2%)?
   - Are there domains with many accounts but low sending (underutilized)?
   - Recommendations: rotate, retire, or scale specific domains

### Mode: `campaign-performance`

**Step 2: Generate report**
```bash
source .venv/bin/activate && python .claude/skills/instantly-analytics/scripts/report_campaign_perf.py --days 30
```

**Step 3: Read and present**
Read `./tmp/instantly-analytics/campaign_performance.json` and present:

1. **Summary line**: total campaigns, total sent, overall reply rate, total opportunities
2. **Table** (sorted by sent volume desc):

| Campaign | Status | Sent | Replied | Reply % | Opps | Opp % | Bounced | Bounce % |
|----------|--------|------|---------|---------|------|-------|---------|----------|

3. **Reply sentiment** (if available): positive / negative / neutral counts per campaign
4. **Top replying domains** for each campaign with replies
5. **Strategic Analysis**:
   - Best and worst performing campaigns by reply rate
   - Campaigns with high opportunity conversion
   - Sentiment patterns across campaigns
   - Which campaigns should be scaled, paused, or iterated on

### Mode: `inbox-status`

**Step 2: Generate report**
```bash
source .venv/bin/activate && python .claude/skills/instantly-analytics/scripts/report_inbox_status.py --days 30
```

**Step 3: Read and present**
Read `./tmp/instantly-analytics/inbox_status.json` and present:

1. **Summary line**: total domains, total accounts, status breakdown (sending / active_warmup / inactive_Nd)
2. **Table** -- group by status, sorted by account count desc:

| Domain | Status | Accounts | Active | Errored | Avg Daily Send | Limit Capacity | Warmup Health |
|--------|--------|----------|--------|---------|----------------|----------------|---------------|

Domain status values:
- `sending`: has campaign sends in the period
- `active_warmup`: zero sends but warmup running on accounts (from API `warmup_status` field)
- `inactive_{N}d`: zero sends AND no warmup active in last N days

3. **Strategic Analysis**:
   - Domains with errored accounts that need attention
   - Utilization rate: daily send vs limit capacity
   - Active warmup domains: ready to activate or still building reputation?
   - Inactive domains: should they be retired or re-warmed?
   - Recommendations for inbox rotation and health

### Mode: `summary`

Run all 3 report scripts, then present a condensed digest:

```bash
source .venv/bin/activate && python .claude/skills/instantly-analytics/scripts/report_domain_health.py --days 30 && python .claude/skills/instantly-analytics/scripts/report_campaign_perf.py --days 30 && python .claude/skills/instantly-analytics/scripts/report_inbox_status.py --days 30
```

Read all 3 JSON files and present:

1. **Infrastructure Health** (from inbox_status): X domains, Y accounts, status breakdown
2. **Deliverability** (from domain_health): overall reply rate, bounce rate, top/bottom domains
3. **Campaign Performance** (from campaign_perf): top campaign by reply rate, total opportunities
4. **Action Items**: Top 3-5 prioritized recommendations across all reports

## Script Reference

All scripts in `.claude/skills/instantly-analytics/scripts/`:

| Script | Input | Output | Purpose |
|--------|-------|--------|---------|
| `fetch_data.py` | Instantly API | `raw/*.json` | Fetch all raw data |
| `report_domain_health.py` | `raw/` | `domain_health.json` | Per-domain deliverability |
| `report_campaign_perf.py` | `raw/` | `campaign_performance.json` | Per-campaign funnel |
| `report_inbox_status.py` | `raw/` | `inbox_status.json` | Account health + utilization |

### Common Args

All report scripts accept:
- `--raw-dir`: Override raw data directory (default: `./tmp/instantly-analytics/raw`)
- `--out-dir`: Override output directory (default: `./tmp/instantly-analytics`)
- `--days N`: Lookback period -- filters replies by timestamp (default: 30)

fetch_data.py additionally accepts:
- `--force`: Force refetch even if cached

## API Gotchas

- **`/emails` has no server-side date filter**: The API request doesn't accept `start_date`/`end_date`, so `fetch_data.py` downloads all replies. Each record has `timestamp_created` -- report scripts filter client-side by `timestamp_created >= now - N days`.
- **`/campaigns/analytics` is all-time**: Sent/reply counts are cumulative, not scoped to a date range. The per-domain reply rate from `domain_health` is more accurate for recent performance because it uses date-filtered reply attribution.
- **`/accounts/analytics/daily` is date-scoped**: This is the only endpoint that respects start_date/end_date. Sent and bounced counts are accurate for the period.
- **Account fields**: Each account has `warmup_status` (1=active), `stat_warmup_score` (0-100), `daily_limit`, and `warmup` config. Used by inbox-status to classify domains.

## Documentation

- **[Email Infrastructure Inventory](docs/email-infrastructure.md)** -- All domains, accounts, personas, providers, capacity, and API endpoint reference

## Requirements

- Virtual environment: `.venv/` in project root
- Environment: `INSTANTLY_API_KEY` in `.env`
- Dependencies: `requests`, `python-dotenv`

## Error Handling

Each script uses the error-first pattern. If a step fails:
1. Check the error message in terminal output
2. Inspect raw files in `./tmp/instantly-analytics/raw/`
3. Fix the issue and re-run only the failed step
4. Errors are also saved to `./tmp/instantly-analytics/errors.json`
