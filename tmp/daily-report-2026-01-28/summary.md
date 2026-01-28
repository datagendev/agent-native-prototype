# Daily Activity Report Status - January 28, 2026

## Workflow Completion

**Date**: 2026-01-28
**Activity Tracking**: ✅ Completed
**Report Generated**: ✅ Completed
**Email Sent**: ✅ Sent to yusheng.kuo@datagen.dev

---

## Key Findings

### User Metrics
- **Total Users**: 78
- **New Users (7d)**: 0
- **Active Users**: 26 (33% of total)
- **Unique Visitors (30d)**: 150
- **Average Credits**: 317.3

### Traffic Overview
- **DAU Today**: 5 unique users
- **Top Referrer**: Direct traffic (497 visits, 150 unique visitors)
- **Geographic**: 80% traffic from US (484 visits)
- **MCP Connect Clicks**: 20 in past 7 days

### User Segments

#### Active Power Users (5)
1. **jeremy.scott.ross@gmail.com** - 995 runs, 86.2% success rate (Power user)
2. **ravi@fulllist.ai** - 416 runs, 0.0% success rate (CRITICAL: All runs failing)
3. **catecean20@gmail.com** - 42 runs, 47.6% success rate (Needs support)
4. **felixjon2000@gmail.com** - 8 runs, 75.0% success rate
5. **steve@misterbrady.com** - 2 runs, 100.0% success rate

#### At-Risk Users (7)
Users with no run activity, 100 credits remaining:
- ben@beneficial-intelligence.com (14 days inactive)
- andriyvovchak15@gmail.com (14 days inactive)
- akil@leadle.in (15 days inactive)
- anand.mridul3@gmail.com (16 days inactive)
- team@oneaway.io (16 days inactive)
- alex@talenthaul.com (17 days inactive)
- david@automatedemand.com (21 days inactive)

#### Recent Failures (3)
1. **ravi@fulllist.ai** - No error details (latest: 2026-01-27)
2. **catecean20@gmail.com** - f-string syntax error
3. **jeremy.scott.ross@gmail.com** - Modal image build failed

### UX Issues
- 1 rage click detected on homepage (david@automatedemand.com on 2026-01-23)

---

## Action Items

### High Priority
1. **Investigate ravi@fulllist.ai** - 416 runs with 0% success rate indicates systematic issue
2. **Support catecean20@gmail.com** - 42 runs with 47.6% success rate suggests code quality issues
3. **Re-engage 7 at-risk users** - All signed up 14-21 days ago but never ran workflows

### Medium Priority
1. Monitor jeremy.scott.ross@gmail.com build failures
2. Follow up on homepage rage click incident
3. Analyze why no new signups in past 7 days

---

## Data Sources

### PostHog Queries Executed
- Event overview (7 days)
- MCP connect clicks (30 days)
- DAU trend (14 days)
- Traffic sources (30 days)
- Traffic by country (30 days)
- Page breakdown (30 days)
- UX issues (7 days)

### Neon Queries Executed
- User overview stats
- Users with run activity
- Users with no runs (at-risk)
- Recent failed runs

### Query Errors
- Custom tools created query failed (NeonDbError: column d.name does not exist)

---

## Files Generated

- Activity data: `/home/user/repo/tmp/daily-report-2026-01-28/activity.json`
- HTML report: `/home/user/repo/tmp/daily-report-2026-01-28/report.html`
- This summary: `/home/user/repo/tmp/daily-report-2026-01-28/summary.md`

---

## Email Details

- **Recipient**: yusheng.kuo@datagen.dev
- **Subject**: Daily Activity Report - January 28, 2026
- **Format**: HTML with plain text fallback
- **Message ID**: 19c04eba1e507765
- **Status**: Successfully sent
