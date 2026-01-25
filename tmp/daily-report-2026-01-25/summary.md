# Daily User Activity Report - 2026-01-25

## Summary

Successfully generated and emailed the daily user activity report to yusheng.kuo@datagen.dev.

## Key Metrics

### User Overview
- **Total Users**: 78
- **New Users (7d)**: 0
- **Active Users**: 26 (33.3%)
- **Unique Visitors (30d)**: 132
- **Average Credits**: 317.3

### Run Activity
- **Total Runs**: 1,344
- **Average Success Rate**: 69.7%

## Notable Findings

### 1. Power Users (Potential Case Studies)
- **jeremy.scott.ross@gmail.com**: 877 runs, 84.6% success rate (last active: 2026-01-25)
- **steve@misterbrady.com**: 2 runs, 100% success rate (last active: 2026-01-11)

### 2. Users Needing Support
- **ravi@fulllist.ai**: 409 runs with 0% success rate - needs immediate support
- **nocodecanada@gmail.com**: 2 runs with 0% success rate

### 3. At-Risk Users (No Activity, 5 total)
Recent signups (11-13 days ago) with no runs:
- ben@beneficial-intelligence.com
- andriyvovchak15@gmail.com
- akil@leadle.in
- anand.mridul3@gmail.com
- team@oneaway.io

### 4. Failed Runs (Proactive Support)
- **jeremy.scott.ross@gmail.com**: Multiple errors (missing httpx module, undefined variables)
- **ravi@fulllist.ai**: Unknown errors on scheduled runs

### 5. UX Issues
- **david@automatedemand.com**: Rage click on homepage (2026-01-23)
- **Unknown user**: JS exception on homepage (2026-01-18)

### 6. Traffic Sources (30d)
- **Direct**: 406 visits, 132 unique visitors (most significant)
- **LinkedIn**: 27 visits, 25 unique visitors
- **MCP Portal**: 27 visits, 5 unique visitors
- **Google**: 20 visits, 18 unique visitors

## Actionable Insights

1. **No high-intent prospects** - MCP connect clicks query returned empty, meaning no new users clicked MCP servers in the last 30 days with 100 credits remaining

2. **Two critical support cases**:
   - ravi@fulllist.ai has 409 runs with 0% success - likely a systematic issue
   - jeremy.scott.ross@gmail.com is a power user hitting module/variable errors

3. **Re-engagement opportunity**: 5 users signed up 11-13 days ago with no activity

4. **UX investigation needed**: Homepage has rage clicks and exceptions

## Files Generated

- `/home/user/repo/tmp/daily-report-2026-01-25/raw-data.json` - Raw query results
- `/home/user/repo/reports/user-activity/report-2026-01-25.html` - Branded HTML report
- Email sent successfully (Message ID: 19bf578838908f4c)

## Data Sources

- **PostHog**: Behavioral analytics (7-day window for events, 30-day for traffic)
- **Neon Database**: User accounts, run history, execution logs
- Project: rough-base-02149126, Database: datagen

## Next Steps

1. Investigate ravi@fulllist.ai's 0% success rate
2. Contact at-risk users with re-engagement email
3. Fix UX issues on homepage (rage clicks/exceptions)
4. Consider jeremy.scott.ross@gmail.com for case study (power user with high engagement)
