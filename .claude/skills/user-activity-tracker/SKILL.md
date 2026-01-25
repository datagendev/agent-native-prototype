---
name: user-activity-tracker
description: Track user activity across PostHog and Neon to identify high-value prospects, churned users, and actionable insights
---

# User Activity Tracker Skill

Combines PostHog behavioral analytics with Neon database records to surface actionable user insights.

## Architecture: Dual-Source Analytics

```
PostHog (Behavior)              Neon (State)
├── Page views                  ├── wasp_user (credits, subscription)
├── MCP connect clicks          ├── fastapi_user (account link)
├── MCP URL copied              ├── fastapi_run (executions)
├── Rage clicks                 ├── fastapi_code_execution (usage)
├── Exceptions                  └── fastapi_deployment (custom tools)
└── Referral sources
         │                              │
         └──────────┬───────────────────┘
                    ▼
            Combined User Profile
                    │
                    ▼
            Actionable Segments
```

## Usage

```bash
/user-activity-tracker
```

## Reference Data

### Neon Database

| Field | Value |
|-------|-------|
| **Project ID** | `rough-base-02149126` |
| **Database** | `datagen` |
| **Region** | aws-us-east-2 |

### Key Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `wasp_user` | User accounts | id, email, credits, subscription_status, last_active_timestamp |
| `fastapi_user` | Backend link | wasp_user_id, id (for joins) |
| `fastapi_run` | Execution history | user_id, run_state, created_at |
| `fastapi_code_execution` | Code runs | user_id, status, execution_time_ms |
| `fastapi_deployment` | Custom tools | user_id, name, final_code |

### PostHog Events

| Event | Purpose | Key Properties |
|-------|---------|----------------|
| `mcp_connect_clicked` | MCP interest | template_name, template_id, has_oauth |
| `mcp_url_copied` | Setup completion | - |
| `$rageclick` | UX frustration | $pathname |
| `$exception` | JS errors | $exception_message |
| `$pageview` | Traffic | $pathname, $referrer |

## Workflow

### Step 1: Query PostHog (MCP Layer)

Run these queries to get behavioral data:

**1a. Key events last 7 days (excluding internal)**
```json
{
  "tool_alias_name": "mcp_Posthog_query_run",
  "parameters": {
    "query": {
      "kind": "DataVisualizationNode",
      "source": {
        "kind": "HogQLQuery",
        "query": "SELECT event, count() as count FROM events WHERE timestamp > now() - INTERVAL 7 DAY AND person.properties.email NOT LIKE '%@datagen.dev' GROUP BY event ORDER BY count DESC"
      }
    }
  }
}
```

**1b. MCP connect clicks with user details**
```json
{
  "tool_alias_name": "mcp_Posthog_query_run",
  "parameters": {
    "query": {
      "kind": "DataVisualizationNode",
      "source": {
        "kind": "HogQLQuery",
        "query": "SELECT person.properties.email as email, count() as click_count, any(properties.template_name) as mcp_server, any(properties.$referring_domain) as referrer, min(timestamp) as first_click, max(timestamp) as last_click FROM events WHERE event = 'mcp_connect_clicked' AND person.properties.email NOT LIKE '%@datagen.dev' AND timestamp > now() - INTERVAL 30 DAY GROUP BY email ORDER BY click_count DESC"
      }
    }
  }
}
```

**1c. Daily unique users trend**
```json
{
  "tool_alias_name": "mcp_Posthog_query_run",
  "parameters": {
    "query": {
      "kind": "InsightVizNode",
      "source": {
        "kind": "TrendsQuery",
        "series": [{"kind": "EventsNode", "event": "$pageview", "custom_name": "DAU", "math": "dau"}],
        "interval": "day",
        "dateRange": {"date_from": "-14d", "date_to": "now"},
        "filterTestAccounts": true
      }
    }
  }
}
```

**1d. Rage clicks and errors (UX issues)**
```json
{
  "tool_alias_name": "mcp_Posthog_query_run",
  "parameters": {
    "query": {
      "kind": "DataVisualizationNode",
      "source": {
        "kind": "HogQLQuery",
        "query": "SELECT person.properties.email as email, event, properties.$pathname as page, timestamp FROM events WHERE event IN ('$rageclick', '$exception') AND person.properties.email NOT LIKE '%@datagen.dev' AND timestamp > now() - INTERVAL 7 DAY ORDER BY timestamp DESC LIMIT 20"
      }
    }
  }
}
```

### Step 2: Query Neon (MCP Layer)

**2a. User overview stats**
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT COUNT(*) as total_users, COUNT(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN 1 END) as new_users_7d, COUNT(CASE WHEN credits < 100 THEN 1 END) as users_with_usage, ROUND(AVG(credits)::numeric, 1) as avg_credits FROM wasp_user WHERE email NOT LIKE '%@datagen.dev'",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

**2b. Users with run activity**
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT w.email, w.credits, COUNT(r.id) as run_count, MAX(r.created_at) as last_run FROM wasp_user w LEFT JOIN fastapi_user f ON w.id = f.wasp_user_id LEFT JOIN fastapi_run r ON f.id = r.user_id WHERE w.email NOT LIKE '%@datagen.dev' GROUP BY w.email, w.credits HAVING COUNT(r.id) > 0 ORDER BY run_count DESC LIMIT 20",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

**2c. Users with no runs but have account**
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT w.email, w.credits, w.created_at, w.last_active_timestamp FROM wasp_user w LEFT JOIN fastapi_user f ON w.id = f.wasp_user_id LEFT JOIN fastapi_run r ON f.id = r.user_id WHERE w.email NOT LIKE '%@datagen.dev' AND r.id IS NULL ORDER BY w.created_at DESC LIMIT 20",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

**2d. Recent failed runs**
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT w.email, r.run_state, r.created_at, LEFT(r.run_error_log, 200) as error_preview FROM fastapi_run r JOIN fastapi_user f ON r.user_id = f.id JOIN wasp_user w ON f.wasp_user_id = w.id WHERE r.run_state = 'failed' AND w.email NOT LIKE '%@datagen.dev' ORDER BY r.created_at DESC LIMIT 10",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### Step 3: Combine & Analyze (Claude Layer)

After running the queries, identify these user segments:

#### Segment 1: High-Intent Prospects (ACTION: Outreach)
- Clicked MCP connect but credits = 100 (no usage)
- Cross-reference PostHog `mcp_connect_clicked` with Neon `wasp_user.credits = 100`
- Priority: Users who clicked multiple times or specific high-value MCPs (Gmail, Slack)

#### Segment 2: Active Power Users (ACTION: Nurture)
- Multiple runs, credit consumption
- From Neon: `run_count > 5` or `credits < 50`
- Consider for case studies, testimonials, premium upsell

#### Segment 3: At-Risk Users (ACTION: Re-engage)
- Signed up but no activity in 7+ days
- From Neon: `created_at < NOW() - 7 days` AND no runs
- Send re-engagement email with use case

#### Segment 4: Frustrated Users (ACTION: Fix UX)
- Rage clicks or exceptions
- From PostHog: `$rageclick` or `$exception` events
- Investigate pages with issues, prioritize fixes

#### Segment 5: Failed Runs (ACTION: Support)
- Users with failed executions
- From Neon: `run_state = 'failed'`
- Proactive support outreach

### Step 4: Generate Report (Claude Layer)

Output a markdown report with:

```markdown
# User Activity Report - {YYYY-MM-DD}

## Summary
- Total users: X
- New users (7d): X
- Users with usage: X
- Avg credits: X

## Traffic (PostHog)
- DAU trend: [sparkline or numbers]
- Top pages: [list]
- Referral sources: [list]

## High-Intent Prospects (Outreach Needed)
| Email | MCP Interest | Clicks | Referrer | Credits | Action |
|-------|--------------|--------|----------|---------|--------|
| ... | Gmail | 14 | LinkedIn | 100 | Reach out about Gmail automation |

## Active Users
| Email | Runs | Credits Used | Last Active |
|-------|------|--------------|-------------|
| ... | 25 | 75 | 2026-01-24 |

## At-Risk Users
| Email | Signed Up | Days Inactive | Credits |
|-------|-----------|---------------|---------|
| ... | 2026-01-10 | 14 | 100 |

## UX Issues
| User | Issue Type | Page | Timestamp |
|------|------------|------|-----------|
| ... | Rage click | /signalgen/mcp-servers | 2026-01-23 |

## Failed Runs (Support Needed)
| User | Error | Timestamp |
|------|-------|-----------|
| ... | API timeout | 2026-01-22 |

## Recommendations
1. [Specific action items based on data]
```

## Deep Dive Queries

### Get full journey for specific user
```json
{
  "tool_alias_name": "mcp_Posthog_query_run",
  "parameters": {
    "query": {
      "kind": "DataVisualizationNode",
      "source": {
        "kind": "HogQLQuery",
        "query": "SELECT event, properties.$pathname as page, timestamp FROM events WHERE person.properties.email = '{EMAIL}' AND timestamp > now() - INTERVAL 30 DAY ORDER BY timestamp DESC LIMIT 100"
      }
    }
  }
}
```

### Get MCP servers a user clicked
```json
{
  "tool_alias_name": "mcp_Posthog_query_run",
  "parameters": {
    "query": {
      "kind": "DataVisualizationNode",
      "source": {
        "kind": "HogQLQuery",
        "query": "SELECT properties.template_name as mcp_server, properties.template_id, count() as clicks, min(timestamp) as first_click FROM events WHERE event = 'mcp_connect_clicked' AND person.properties.email = '{EMAIL}' GROUP BY mcp_server, properties.template_id ORDER BY clicks DESC"
      }
    }
  }
}
```

### Check user's Neon records
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT w.*, (SELECT COUNT(*) FROM fastapi_run r JOIN fastapi_user f ON r.user_id = f.id WHERE f.wasp_user_id = w.id) as run_count FROM wasp_user w WHERE w.email = '{EMAIL}'",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

## Key Metrics to Track

| Metric | Source | Good | Excellent |
|--------|--------|------|-----------|
| DAU | PostHog | >10 | >50 |
| MCP Connect Rate | PostHog | 5% of visitors | >10% |
| Signup to First Run | Neon | <7 days | <1 day |
| Run Success Rate | Neon | >80% | >95% |
| Credit Utilization | Neon | >20% using | >50% using |

## Step 5: Generate HTML Report (Claude Layer)

After gathering data, generate HTML report from template:

1. Read template: `.claude/skills/user-activity-tracker/templates/report-email.html`
2. Replace placeholders with actual data
3. Save to `reports/user-activity/report-{YYYY-MM-DD}.html`

## Step 6: Send via Email (MCP Layer)

Send the report via Gmail with HTML body:

```json
{
  "tool_alias_name": "mcp_Gmail_Yusheng_gmail_send_email",
  "parameters": {
    "to": ["yusheng.kuo@datagen.dev"],
    "subject": "DataGen User Activity Report - {DATE}",
    "body": "Your daily user activity report is attached. View in HTML-enabled email client.",
    "htmlBody": "<full HTML content here>",
    "mimeType": "multipart/alternative"
  }
}
```

**Gmail MCP supports:**
- `htmlBody`: Full HTML content for rich formatting
- `mimeType`: Set to `multipart/alternative` for HTML + plain text fallback
- `to`: Array of recipients

## Brand Colors Reference

```css
--primary: #005047;      /* Dark teal - headers, buttons */
--secondary: #00795e;    /* Light teal - accents */
--success: #219653;      /* Green - positive metrics */
--danger: #D34053;       /* Red - action needed */
--warning: #FFA70B;      /* Orange - warnings */
--boxdark: #24303F;      /* Dark mode background */
```

## File Structure

```
.claude/skills/user-activity-tracker/
├── SKILL.md                         # This file
├── templates/
│   ├── report-email.html            # HTML template with placeholders
│   └── sample-report.html           # Example with real data
└── scripts/                         # Future: Python scripts for automation
```

## Notes

- Always exclude `@datagen.dev` emails from analysis
- PostHog has `filterTestAccounts: true` option for queries
- Neon project ID: `rough-base-02149126`, database: `datagen`
- User ID links: `wasp_user.id` = `fastapi_user.wasp_user_id`
