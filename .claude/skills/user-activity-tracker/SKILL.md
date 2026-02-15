---
name: user-activity-tracker
description: Track user activity across PostHog and Neon to identify high-value prospects, churned users, and actionable insights
---

# User Activity Tracker Skill

Combines PostHog behavioral analytics with Neon database records to surface actionable user insights.

## Architecture: Dual-Source Analytics

```
PostHog (Behavior)              Neon (State + Execution)
├── Page views                  ├── wasp_user (credits, subscription)
├── MCP connect clicks          ├── fastapi_user (account link)
├── MCP URL copied              ├── fastapi_run (workflow executions)
├── Rage clicks                 ├── fastapi_code_execution (code runs)
├── Exceptions                  ├── fastapi_deployment (custom tools)
└── Referral sources            ├── fastapi_tool_executions (every tool call)
                                └── wasp_agentexecution (agent-level runs)
         │                              │
         └──────────┬───────────────────┘
                    ▼
            Combined User Profile
            (who, what tools, when, success rate)
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

| Table | Purpose | Key Columns | What It Shows |
|-------|---------|-------------|---------------|
| `wasp_user` | User accounts | id, email, credits, subscription_status, last_active_timestamp, created_at | User metadata |
| `fastapi_user` | Backend link | wasp_user_id, id (for joins) | Join table |
| `fastapi_tool_executions` | **Individual tool calls** | user_id, tool_name, tool_type, status, error_type, error_message, created_at | **Granular tool-level success/failure** |
| `fastapi_run` | **Workflow executions** | user_id, run_state, created_at, run_error_log | **Workflow-level failures (includes infrastructure)** |
| `fastapi_code_execution` | Code runs | user_id, status, execution_time_ms, script_name | Code sandbox issues |
| `fastapi_deployment` | Custom tools | user_id, name, final_code | User-created tools |

**CRITICAL:** `fastapi_tool_executions` vs `fastapi_run` tell different stories:
- **Tool level** = individual tool call failures (user code, tool bugs)
- **Workflow level** = complete run failures (infrastructure, Modal, API timeouts)

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

> **IMPORTANT**: `mcp_Posthog_query_run` has been removed from the PostHog MCP server.
> Use the two-step approach instead:
> 1. Create an insight with `mcp_Posthog_insight_create_from_query`
> 2. Fetch results with `mcp_Posthog_insight_query`
>
> Alternatively, use existing saved insights by ID with `mcp_Posthog_insight_query`.

### Saved Insights (query by ID)

| Insight ID | Name | Description |
|------------|------|-------------|
| 2625022 | Daily active users (DAUs) | 30-day DAU trend via $pageview |
| 2625023 | Weekly active users (WAUs) | 90-day WAU trend |
| 2625024 | Retention | Weekly retention (first-time) |
| 2625025 | Growth accounting | Lifecycle: new, returning, resurrecting, dormant |
| 2625026 | Referring domain (last 14d) | Traffic sources by referring domain |
| 2625027 | Pageview funnel, by browser | 3-step pageview funnel |
| 6126979 | New signups (last 30d) | user_signed_up events by day |
| 6126980 | MCP connect clicks by template (last 30d) | MCP servers clicked by template |
| 6876824 | MCP connects by user (excl datagen.dev) | Which external users connected which MCPs |

#### Querying a saved insight
```json
{
  "tool_alias_name": "mcp_Posthog_insight_query",
  "parameters": {
    "insightId": "2625022"
  }
}
```

### Creating new ad-hoc queries

Use `mcp_Posthog_insight_create_from_query` to create a new insight, then `mcp_Posthog_insight_query` to fetch results.

#### Step 1: Create insight
```json
{
  "tool_alias_name": "mcp_Posthog_insight_create_from_query",
  "parameters": {
    "data": {
      "name": "Your Insight Name",
      "favorited": false,
      "query": {
        "kind": "DataVisualizationNode",
        "source": {
          "kind": "HogQLQuery",
          "query": "YOUR HOGQL QUERY HERE"
        }
      }
    }
  }
}
```

#### Step 2: Fetch results (use the ID returned from step 1)
```json
{
  "tool_alias_name": "mcp_Posthog_insight_query",
  "parameters": {
    "insightId": "INSIGHT_ID_FROM_STEP_1"
  }
}
```

### Example HogQL Queries (for use in step 1)

**Event Overview (7 days)**
```sql
SELECT event, count() as count FROM events WHERE timestamp > now() - INTERVAL 7 DAY AND person.properties.email NOT LIKE '%@datagen.dev' GROUP BY event ORDER BY count DESC
```

**MCP Connect Clicks (with user details)**
```sql
SELECT person.properties.email as email, count() as click_count, groupArray(properties.template_name) as mcp_servers, any(properties.$referring_domain) as referrer, min(timestamp) as first_click, max(timestamp) as last_click FROM events WHERE event = 'mcp_connect_clicked' AND person.properties.email NOT LIKE '%@datagen.dev' AND timestamp > now() - INTERVAL 30 DAY GROUP BY email ORDER BY click_count DESC
```

**Traffic Sources (by referrer)**
```sql
SELECT properties.$referring_domain as referrer, count() as visits, count(DISTINCT person_id) as unique_visitors FROM events WHERE event = '$pageview' AND timestamp > now() - INTERVAL 30 DAY GROUP BY referrer ORDER BY visits DESC LIMIT 20
```

**Traffic by Country**
```sql
SELECT properties.$geoip_country_code as country, count() as visits, count(DISTINCT person_id) as unique_visitors FROM events WHERE event = '$pageview' AND timestamp > now() - INTERVAL 30 DAY GROUP BY country ORDER BY visits DESC LIMIT 15
```

**UX Issues (rage clicks + errors)**
```sql
SELECT person.properties.email as email, event, properties.$pathname as page, timestamp FROM events WHERE event IN ('$rageclick', '$exception') AND person.properties.email NOT LIKE '%@datagen.dev' AND timestamp > now() - INTERVAL 7 DAY ORDER BY timestamp DESC LIMIT 20
```

**Page Breakdown**
```sql
SELECT properties.$pathname as page, count() as views, count(DISTINCT person_id) as unique_visitors FROM events WHERE event = '$pageview' AND timestamp > now() - INTERVAL 30 DAY GROUP BY page ORDER BY views DESC LIMIT 20
```

### Other Available PostHog Tools

- `mcp_Posthog_event_definitions_list` — List all tracked events
- `mcp_Posthog_properties_list` — List properties for events or persons
- `mcp_Posthog_insights_get_all` — List all saved insights
- `mcp_Posthog_entity_search` — Search insights/dashboards/flags by name
- `mcp_Posthog_list_errors` — List JS errors in the project

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

> For per-user queries, create a new insight via `mcp_Posthog_insight_create_from_query`, then fetch with `mcp_Posthog_insight_query`. Replace `{EMAIL}` with the actual user email.

### Full User Journey (PostHog)
```sql
SELECT event, properties.$pathname as page, timestamp FROM events WHERE person.properties.email = '{EMAIL}' AND timestamp > now() - INTERVAL 30 DAY ORDER BY timestamp DESC LIMIT 100
```

### MCP Servers User Clicked
```sql
SELECT properties.template_name as mcp_server, properties.template_id, count() as clicks, min(timestamp) as first_click FROM events WHERE event = 'mcp_connect_clicked' AND person.properties.email = '{EMAIL}' GROUP BY mcp_server, properties.template_id ORDER BY clicks DESC
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

## Tool Execution Analytics

### Key Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `fastapi_tool_executions` | Every tool call | user_id, tool_name, tool_type, tool_provider, status, execution_duration_ms, error_message, created_at |
| `wasp_agentexecution` | Agent-level runs | agent_id, status, entry_prompt, result, duration_ms, started_at |

### Tool Execution Overview (all users)
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT COUNT(*) as total_tool_executions, COUNT(DISTINCT user_id) as unique_users, COUNT(DISTINCT tool_name) as unique_tools, ROUND(AVG(execution_duration_ms)) as avg_duration_ms, COUNT(CASE WHEN status = 'success' THEN 1 END) as successes, COUNT(CASE WHEN status = 'failed' THEN 1 END) as failures FROM fastapi_tool_executions",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### Top Tools by Usage (with success rate)
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT tool_name, tool_provider, COUNT(*) as total, COUNT(CASE WHEN status = 'success' THEN 1 END) as successes, COUNT(CASE WHEN status = 'failed' THEN 1 END) as failures, ROUND(100.0 * COUNT(CASE WHEN status = 'success' THEN 1 END) / COUNT(*), 1) as success_rate, ROUND(AVG(execution_duration_ms)) as avg_ms FROM fastapi_tool_executions GROUP BY tool_name, tool_provider ORDER BY total DESC LIMIT 25",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### User-Level Tool Usage Summary
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT w.email, COUNT(t.id) as total_executions, COUNT(DISTINCT t.tool_name) as unique_tools, COUNT(CASE WHEN t.status = 'success' THEN 1 END) as successes, COUNT(CASE WHEN t.status = 'failed' THEN 1 END) as failures, ROUND(AVG(t.execution_duration_ms)) as avg_duration_ms, MIN(t.created_at) as first_use, MAX(t.created_at) as last_use FROM fastapi_tool_executions t JOIN fastapi_user f ON t.user_id::integer = f.id JOIN wasp_user w ON f.wasp_user_id = w.id GROUP BY w.email ORDER BY total_executions DESC",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### Per-User Tool Breakdown (replace {EMAIL})
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT t.tool_name, t.tool_provider, COUNT(*) as uses, COUNT(CASE WHEN t.status = 'success' THEN 1 END) as successes, ROUND(100.0 * COUNT(CASE WHEN t.status = 'success' THEN 1 END) / COUNT(*), 1) as success_rate, MIN(t.created_at)::date as first_use, MAX(t.created_at)::date as last_use FROM fastapi_tool_executions t JOIN fastapi_user f ON t.user_id::integer = f.id JOIN wasp_user w ON f.wasp_user_id = w.id WHERE w.email = '{EMAIL}' GROUP BY t.tool_name, t.tool_provider ORDER BY uses DESC LIMIT 20",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### Tool Failure Analysis (most failing tools)
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT tool_name, tool_provider, COUNT(*) as failures, ROUND(AVG(execution_duration_ms)) as avg_ms, COUNT(DISTINCT user_id) as affected_users, MIN(created_at)::date as first_failure, MAX(created_at)::date as last_failure FROM fastapi_tool_executions WHERE status = 'failed' GROUP BY tool_name, tool_provider ORDER BY failures DESC LIMIT 15",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### Tool Error Details (replace {TOOL_NAME})
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT error_type, LEFT(error_message, 200) as error_preview, COUNT(*) as occurrences, MAX(created_at) as latest FROM fastapi_tool_executions WHERE tool_name = '{TOOL_NAME}' AND status = 'failed' GROUP BY error_type, error_preview ORDER BY occurrences DESC LIMIT 10",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### Agent Execution Overview
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT status, COUNT(*) as total, ROUND(AVG(duration_ms)) as avg_duration_ms, MIN(started_at) as earliest, MAX(completed_at) as latest FROM wasp_agentexecution GROUP BY status ORDER BY total DESC",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### Daily Tool Execution Trend (last 14 days)
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT created_at::date as day, COUNT(*) as total, COUNT(CASE WHEN status = 'success' THEN 1 END) as successes, COUNT(CASE WHEN status = 'failed' THEN 1 END) as failures, COUNT(DISTINCT user_id) as unique_users FROM fastapi_tool_executions WHERE created_at > NOW() - INTERVAL '14 days' GROUP BY day ORDER BY day DESC",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

### MCP Provider Usage Summary
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT tool_provider, COUNT(*) as total_calls, COUNT(DISTINCT tool_name) as unique_tools, COUNT(DISTINCT user_id) as unique_users, COUNT(CASE WHEN status = 'success' THEN 1 END) as successes, COUNT(CASE WHEN status = 'failed' THEN 1 END) as failures, ROUND(AVG(execution_duration_ms)) as avg_ms FROM fastapi_tool_executions WHERE tool_type = 'mcp' GROUP BY tool_provider ORDER BY total_calls DESC",
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

## Failure Investigation Process

### Critical: Query Multiple Data Sources

**Don't build analysis from single table.** User failures show differently across tables:

```sql
-- 1. Tool-level failures (granular)
SELECT tool_name, error_type, COUNT(*) as failures
FROM fastapi_tool_executions t
JOIN fastapi_user f ON t.user_id::integer = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE w.email = '{EMAIL}' AND t.status = 'failed'
GROUP BY tool_name, error_type
ORDER BY failures DESC;

-- 2. Workflow-level failures (infrastructure)
SELECT LEFT(run_error_log, 200) as error, COUNT(*) as failures
FROM fastapi_run r
JOIN fastapi_user f ON r.user_id = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE w.email = '{EMAIL}' AND r.run_state = 'failed'
GROUP BY error
ORDER BY failures DESC;
```

### Verify Assumptions

**Before diagnosing "User has X issue":**

```sql
-- Check if user actually uses suspected tool
SELECT tool_name, COUNT(*) as uses
FROM fastapi_tool_executions t
JOIN fastapi_user f ON t.user_id::integer = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE w.email = '{EMAIL}'
  AND tool_name LIKE '%suspected_tool%';

-- If 0 results: User doesn't use this tool!
```

### Categorize Failures

**Separate platform issues from user issues:**

| Category | Indicators | Owner |
|----------|-----------|-------|
| **Infrastructure** | API timeouts, Modal OOM (rc=137), sandbox rate limits | Platform |
| **Platform Bug** | False credit checks (user has credits), missing env vars in Modal | Platform |
| **Missing Feature** | Rate limits without retry, no error recovery | Platform |
| **User Code** | Invalid params in custom code, logic errors | User |
| **Third-party** | External API errors (HubSpot, LinkedIn) | Mixed |

### Common Mistakes to Avoid

1. ❌ **Assuming your debugging errors = user's production errors**
   - You hitting Neon MCP failures while analyzing ≠ User hitting same failures
   - Always verify: Does user even use this tool?

2. ❌ **Building narrative before checking all data sources**
   - Tool level success ≠ Workflow level success
   - Workflows can fail from infrastructure even if tools succeed

3. ❌ **Using vague error categories**
   - Not "Modal failure" (could be 20 different things)
   - Use "API timeout" or "Modal OOM (rc=137)" (specific)

4. ❌ **Ignoring timeline patterns**
   - If user has days with 100% success → likely platform issue, not user code
   - Check: Does failure cluster around specific dates?

### Analysis Checklist

- [ ] Query `fastapi_tool_executions` for tool-level failures
- [ ] Query `fastapi_run` for workflow-level failures
- [ ] Verify tool usage before diagnosing issues
- [ ] Check MCP vs default tool ratio
- [ ] Categorize failures by root cause (infrastructure/platform/user)
- [ ] Look for timeline patterns (clustered failures = platform issue)
- [ ] Read actual error messages (not assumptions)

---

## Notes

- Always exclude `@datagen.dev` emails from analysis
- PostHog has `filterTestAccounts: true` option for trend queries
- Neon project ID: `rough-base-02149126`, database: `datagen`
- User ID links: `wasp_user.id` = `fastapi_user.wasp_user_id`
- Replace `{EMAIL}` placeholder in deep dive queries with actual email
- **See `product-analysis` skill for detailed failure investigation process**
