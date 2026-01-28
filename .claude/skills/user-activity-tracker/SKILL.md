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
| `wasp_user` | User accounts | id, email, credits, subscription_status, last_active_timestamp, created_at |
| `fastapi_user` | Backend link | wasp_user_id, id (for joins) |
| `fastapi_run` | Execution history | user_id, run_state, created_at, run_error_log |
| `fastapi_code_execution` | Code runs | user_id, status, execution_time_ms, script_name |
| `fastapi_deployment` | Custom tools | user_id, name, final_code |

### PostHog Events

| Event | Purpose | Key Properties |
|-------|---------|----------------|
| `mcp_connect_clicked` | MCP interest | template_name, template_id, has_oauth |
| `mcp_url_copied` | Setup completion | - |
| `$rageclick` | UX frustration | $pathname |
| `$exception` | JS errors | $exception_message |
| `$pageview` | Traffic | $pathname, $referrer, $referring_domain, $geoip_country_code |

---

## PostHog Queries

### Event Overview (7 days)
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

### MCP Connect Clicks (with user details)
```json
{
  "tool_alias_name": "mcp_Posthog_query_run",
  "parameters": {
    "query": {
      "kind": "DataVisualizationNode",
      "source": {
        "kind": "HogQLQuery",
        "query": "SELECT person.properties.email as email, count() as click_count, groupArray(properties.template_name) as mcp_servers, any(properties.$referring_domain) as referrer, min(timestamp) as first_click, max(timestamp) as last_click FROM events WHERE event = 'mcp_connect_clicked' AND person.properties.email NOT LIKE '%@datagen.dev' AND timestamp > now() - INTERVAL 30 DAY GROUP BY email ORDER BY click_count DESC"
      }
    }
  }
}
```

### Daily Unique Users (DAU Trend)
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

### Traffic Sources (by referrer)
```json
{
  "tool_alias_name": "mcp_Posthog_query_run",
  "parameters": {
    "query": {
      "kind": "DataVisualizationNode",
      "source": {
        "kind": "HogQLQuery",
        "query": "SELECT properties.$referring_domain as referrer, count() as visits, count(DISTINCT person_id) as unique_visitors FROM events WHERE event = '$pageview' AND timestamp > now() - INTERVAL 30 DAY GROUP BY referrer ORDER BY visits DESC LIMIT 20"
      }
    }
  }
}
```

### Traffic by Country
```json
{
  "tool_alias_name": "mcp_Posthog_query_run",
  "parameters": {
    "query": {
      "kind": "DataVisualizationNode",
      "source": {
        "kind": "HogQLQuery",
        "query": "SELECT properties.$geoip_country_code as country, count() as visits, count(DISTINCT person_id) as unique_visitors FROM events WHERE event = '$pageview' AND timestamp > now() - INTERVAL 30 DAY GROUP BY country ORDER BY visits DESC LIMIT 15"
      }
    }
  }
}
```

### UX Issues (rage clicks + errors)
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

### Page Breakdown
```json
{
  "tool_alias_name": "mcp_Posthog_query_run",
  "parameters": {
    "query": {
      "kind": "DataVisualizationNode",
      "source": {
        "kind": "HogQLQuery",
        "query": "SELECT properties.$pathname as page, count() as views, count(DISTINCT person_id) as unique_visitors FROM events WHERE event = '$pageview' AND timestamp > now() - INTERVAL 30 DAY GROUP BY page ORDER BY views DESC LIMIT 20"
      }
    }
  }
}
```

---

## Neon Queries

### User Overview Stats
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

### Users with Run Activity (with success rate)
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT w.email, w.credits, COUNT(r.id) as run_count, COUNT(CASE WHEN r.run_state = 'completed' THEN 1 END) as success_count, ROUND(100.0 * COUNT(CASE WHEN r.run_state = 'completed' THEN 1 END) / NULLIF(COUNT(r.id), 0), 1) as success_rate, MAX(r.created_at) as last_run FROM wasp_user w LEFT JOIN fastapi_user f ON w.id = f.wasp_user_id LEFT JOIN fastapi_run r ON f.id = r.user_id WHERE w.email NOT LIKE '%@datagen.dev' GROUP BY w.email, w.credits HAVING COUNT(r.id) > 0 ORDER BY run_count DESC LIMIT 20",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### Users with No Runs (churned/at-risk)
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT w.email, w.credits, w.created_at, w.last_active_timestamp, EXTRACT(DAY FROM NOW() - w.created_at) as days_since_signup FROM wasp_user w LEFT JOIN fastapi_user f ON w.id = f.wasp_user_id LEFT JOIN fastapi_run r ON f.id = r.user_id WHERE w.email NOT LIKE '%@datagen.dev' AND r.id IS NULL ORDER BY w.created_at DESC LIMIT 20",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### Recent Failed Runs
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

### Recent Code Executions (what users are building)
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT w.email, ce.name, ce.status, ce.execution_time_ms, ce.created_at FROM fastapi_code_execution ce JOIN fastapi_user f ON ce.user_id = f.id JOIN wasp_user w ON f.wasp_user_id = w.id WHERE w.email NOT LIKE '%@datagen.dev' ORDER BY ce.created_at DESC LIMIT 20",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### Custom Tools Created
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT w.email, d.description, d.created_at, LENGTH(d.final_code) as code_length FROM fastapi_deployment d JOIN fastapi_user f ON d.user_id = f.id JOIN wasp_user w ON f.wasp_user_id = w.id WHERE w.email NOT LIKE '%@datagen.dev' ORDER BY d.created_at DESC LIMIT 20",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

---

## Deep Dive Queries (per user)

### Full User Journey (PostHog)
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

### MCP Servers User Clicked
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

### User's Neon Records
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT w.*, (SELECT COUNT(*) FROM fastapi_run r JOIN fastapi_user f ON r.user_id = f.id WHERE f.wasp_user_id = w.id) as run_count, (SELECT COUNT(*) FROM fastapi_run r JOIN fastapi_user f ON r.user_id = f.id WHERE f.wasp_user_id = w.id AND r.run_state = 'completed') as success_count FROM wasp_user w WHERE w.email = '{EMAIL}'",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

---

## User Segmentation Logic

After running queries, classify users into these segments:

### Segment 1: High-Intent Prospects (ACTION: Outreach)
- Clicked MCP connect but credits = 100 (no usage)
- Cross-reference PostHog `mcp_connect_clicked` with Neon `wasp_user.credits = 100`
- Priority: Users who clicked multiple times or high-value MCPs (Gmail, Slack, Linear)

### Segment 2: Power Users (ACTION: Nurture)
- Multiple runs, credit consumption
- Criteria: `run_count > 5` or `credits < 50`
- Consider for case studies, testimonials, premium upsell

### Segment 3: At-Risk Users (ACTION: Re-engage)
- Signed up but no activity in 7+ days
- Criteria: `created_at < NOW() - 7 days` AND no runs
- Send re-engagement email with use case

### Segment 4: Frustrated Users (ACTION: Fix UX)
- Rage clicks or exceptions
- From PostHog: `$rageclick` or `$exception` events
- Investigate pages with issues, prioritize fixes

### Segment 5: Failing Users (ACTION: Support)
- Users with high failure rate
- Criteria: `success_rate < 50%` with `run_count > 5`
- Proactive support outreach

---

## Key Metrics to Track

| Metric | Source | Good | Excellent |
|--------|--------|------|-----------|
| DAU | PostHog | >10 | >50 |
| MCP Connect Rate | PostHog | 5% of visitors | >10% |
| Signup to First Run | Neon | <7 days | <1 day |
| Run Success Rate | Neon | >80% | >95% |
| Credit Utilization | Neon | >20% using | >50% using |

---

## Notes

- Always exclude `@datagen.dev` emails from analysis
- PostHog has `filterTestAccounts: true` option for trend queries
- Neon project ID: `rough-base-02149126`, database: `datagen`
- User ID links: `wasp_user.id` = `fastapi_user.wasp_user_id`
- Replace `{EMAIL}` placeholder in deep dive queries with actual email
