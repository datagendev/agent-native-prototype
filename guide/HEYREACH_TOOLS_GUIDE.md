---
title: "HeyReach Campaign Analysis Tools - Quick Start Guide"
description: "How to use DataGen-powered HeyReach analysis tools for campaign optimization"
category: "documentation"
tags: ["heyreach", "tools", "automation", "campaign-analysis"]
created: 2026-01-09
updated: 2026-01-09
status: "active"
priority: "high"
---

# HeyReach Campaign Analysis Tools

Automate your HeyReach campaign analysis and optimization using DataGen's MCP integration.

## Quick Start

### Prerequisites

1. **DataGen API Key**: Set in `../.env`
2. **HeyReach MCP Connected**: Connect HeyReach to DataGen dashboard
3. **Virtual Environment**: Activate with `source .venv/bin/activate`

---

## Tool 1: Campaign Performance Report

### What It Does
Generates comprehensive performance reports for all or specific HeyReach campaigns with AI-powered insights.

### Command Options

```bash
# Analyze all active campaigns
/heyreach-campaign-report

# Or run the script directly:
source .venv/bin/activate && python scripts/heyreach_campaign_report.py
```

```bash
# Analyze specific campaigns by ID
/heyreach-campaign-report --campaigns 12345,67890

# Filter by campaign status
/heyreach-campaign-report --status IN_PROGRESS
/heyreach-campaign-report --status PAUSED

# Search by keyword (for client-specific reports)
/heyreach-campaign-report --keyword "Acme Corp"
/heyreach-campaign-report --keyword "VPs Engineering"

# Combine filters
/heyreach-campaign-report --status IN_PROGRESS --keyword "Q1-2026"

# Custom date range
/heyreach-campaign-report --days 7   # Last 7 days
/heyreach-campaign-report --days 90  # Last 90 days
```

### What You Get

**Markdown report with:**
- 📊 Executive summary (total leads, acceptance rates, meetings booked)
- 🚨 Campaigns needing attention (underperformers, paused campaigns)
- 🏆 Top performers (ranked by acceptance rate)
- 📈 Performance table for all campaigns
- 💡 AI-powered recommendations
- 📋 Action checklist

**Saved to**: `reports/heyreach/campaign-report-{date}.md`

---

## Use Cases

### 1. Weekly Client Review
```bash
# Every Monday morning
/heyreach-campaign-report --status IN_PROGRESS

# Review report, address alerts, update clients
```

### 2. Client-Specific Reports
```bash
# Generate report for specific client
/heyreach-campaign-report --keyword "Acme Corp"

# Send markdown report to client
```

### 3. Find Forgotten Campaigns
```bash
# Check for paused campaigns
/heyreach-campaign-report --status PAUSED

# Review and decide: resume, optimize, or archive
```

### 4. Identify Scaling Opportunities
```bash
# Find top performers
/heyreach-campaign-report

# Look for 🏆 campaigns with >60% acceptance
# Extract templates and replicate to other campaigns
```

### 5. Emergency Troubleshooting
```bash
# Check if any campaigns are underperforming
/heyreach-campaign-report --days 7

# Pause campaigns with <40% acceptance rate immediately
```

---

## Performance Benchmarks

The tool uses these benchmarks to rate campaigns:

| Metric | Underperforming | Good | Excellent |
|--------|----------------|------|-----------|
| Acceptance Rate | <40% | 40-60% | >60% |
| Reply Rate | <10% | 10-20% | >20% |
| Meeting Rate | <3% | 3-7% | >7% |

---

## Workflow Example

### Monday Morning Routine (10 minutes)

```bash
# 1. Generate weekly report
/heyreach-campaign-report --status IN_PROGRESS

# 2. Review alerts (🚨)
#    - Pause underperformers immediately
#    - Note campaigns needing optimization

# 3. Check top performers (🏆)
#    - Extract winning message templates
#    - Consider scaling (add more leads)

# 4. Review action checklist
#    - Complete high-priority items
#    - Schedule medium-priority for later

# 5. Client follow-ups
#    - Generate client-specific reports
#    - Schedule review calls as needed
```

**Time saved**: 5-10 hours/week vs. manual dashboard review

---

## Advanced Usage

### Automation Options

#### Option 1: Scheduled Reports (Cron)
```bash
# Add to crontab for weekly Monday 9am reports
0 9 * * 1 cd ~/linkedin-outreach && source .venv/bin/activate && python scripts/heyreach_campaign_report.py
```

#### Option 2: Slack Notifications
```python
# Extend script to send Slack alerts for critical issues
# When acceptance rate <30%, send Slack message immediately
```

#### Option 3: Custom Tool in DataGen
```python
# Deploy as DataGen custom tool
# Run via API, webhooks, or Claude Code
```

---

## Troubleshooting

### Error: "DATAGEN_API_KEY not set"
**Solution**: Check `../.env` file has your API key
```bash
export DATAGEN_API_KEY="your-key-here"
```

### Error: "No campaigns found"
**Check**:
- HeyReach MCP is connected in DataGen dashboard
- Campaign filters aren't too restrictive
- HeyReach account has active campaigns

### Error: "ModuleNotFoundError: datagen_sdk"
**Solution**: Activate virtual environment first
```bash
source .venv/bin/activate
```

---

## Coming Soon

### Additional Tools

- `/heyreach-conversation-insights` - Analyze winning message patterns
- `/heyreach-lead-analysis` - Deep dive on lead segments
- `/heyreach-optimization-plan` - Generate optimization roadmap

---

## ROI for "The Mister Brady Method"

### Time Savings
- **Before**: 10-15 hrs/week manual campaign review
- **After**: 2-3 hrs/week automated + strategic decisions
- **Savings**: 7-12 hrs/week (80% reduction)

### Scale Impact
- **Current capacity**: 10-15 clients
- **With automation**: 30-50 clients
- **Revenue multiplier**: 3-5x

### Client Value
- Real-time campaign monitoring
- Data-driven optimization
- Professional weekly reports
- Proactive issue detection

---

## Questions?

Contact DataGen team or check:
- [HeyReach MCP Tool Documentation](../BRADY_HEYREACH_MCP_OPPORTUNITY_ANALYSIS.md)
- [DataGen SDK Guide](../CLAUDE.md)

---

*Built for Steven Brady (misterbrady) by DataGen*
*Part of "The Mister Brady Method AI+" toolkit*
