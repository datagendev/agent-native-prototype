---
name: daily-delta-tracker
description: Track 24-hour deltas from PostHog and Neon for daily operational reporting
---

# Daily Delta Tracker Skill

Fetches only NEW activity from the last 24 hours across PostHog (behavioral analytics) and Neon (database state). Designed for delta-focused daily reports that show what's changed, not repeating old issues.

## Architecture: 24-Hour Delta Focus

```
PostHog (Last 24h)              Neon (Last 24h)
├── New signups                 ├── New deployments
├── Signup behavior             ├── New failed runs
├── UI blockers                 ├── Tool executions (who/what)
│   ├── Rage clicks             └── New agents created
│   └── JS exceptions
└── MCP connect clicks
         │                              │
         └──────────┬───────────────────┘
                    ▼
            24h Delta Report
            (new issues, new users, new errors)
```

## Usage

```bash
/daily-delta-tracker
```

## Reference Data

### Neon Database

| Field | Value |
|-------|-------|
| **Project ID** | `rough-base-02149126` |
| **Database** | `datagen` |
| **Region** | aws-us-east-2 |

### Key Tables (24h Time Window)

| Table | 24h Filter | Purpose |
|-------|-----------|---------|
| `wasp_user` | `created_at > NOW() - INTERVAL '24 hours'` | New signups |
| `fastapi_deployment` | `created_at > NOW() - INTERVAL '24 hours'` | New custom tools |
| `fastapi_run` | `created_at > NOW() - INTERVAL '24 hours'` | New workflow runs |
| `fastapi_tool_executions` | `created_at > NOW() - INTERVAL '24 hours'` | Tool calls |
| `wasp_agentexecution` | `started_at > NOW() - INTERVAL '24 hours'` | Agent executions |

---

## PostHog Queries (24h Delta)

### Query 1: New Signups with Behavior (Last 24h)

**Purpose**: Identify who signed up in the last 24 hours and what they did

**Query Type**: Custom HogQL via `mcp_Posthog_insight_create_from_query`

```sql
SELECT
  person.properties.email as email,
  count() as pageviews,
  groupArray(DISTINCT properties.$pathname) as pages_visited,
  min(timestamp) as first_seen,
  max(timestamp) as last_seen,
  dateDiff('minute', min(timestamp), max(timestamp)) as session_duration_minutes
FROM events
WHERE event = '$pageview'
  AND timestamp > now() - INTERVAL 1 DAY
  AND person.properties.email NOT LIKE '%@datagen.dev'
  AND person.properties.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
GROUP BY email
HAVING count() > 0
ORDER BY first_seen DESC
```

**Expected Output**:
```json
{
  "results": [
    {
      "email": "user@example.com",
      "pageviews": 15,
      "pages_visited": ["/", "/docs", "/mcp-servers"],
      "first_seen": "2026-02-28T10:30:00Z",
      "last_seen": "2026-02-28T11:15:00Z",
      "session_duration_minutes": 45
    }
  ]
}
```

**Usage**:
```json
{
  "tool_alias_name": "mcp_Posthog_insight_create_from_query",
  "parameters": {
    "query": {
      "kind": "HogQLQuery",
      "query": "<SQL above>"
    }
  }
}
```

---

### Query 2: UI Blockers (Rage Clicks + Exceptions, Last 24h)

**Purpose**: Detect UX frustration and JS errors from last 24 hours

**Query Type**: Custom HogQL

```sql
SELECT
  person.properties.email as email,
  event,
  properties.$pathname as page,
  properties.$exception_message as error_msg,
  properties.$exception_type as error_type,
  timestamp,
  properties.$current_url as url
FROM events
WHERE event IN ('$rageclick', '$exception')
  AND timestamp > now() - INTERVAL 1 DAY
  AND person.properties.email NOT LIKE '%@datagen.dev'
  AND person.properties.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
ORDER BY timestamp DESC
LIMIT 100
```

**Expected Output**:
```json
{
  "results": [
    {
      "email": "user@example.com",
      "event": "$rageclick",
      "page": "/mcp-servers",
      "timestamp": "2026-02-28T14:22:00Z",
      "url": "https://datagen.dev/mcp-servers?tab=oauth"
    },
    {
      "email": "user2@example.com",
      "event": "$exception",
      "page": "/deployments",
      "error_msg": "Cannot read property 'map' of undefined",
      "error_type": "TypeError",
      "timestamp": "2026-02-28T13:45:00Z"
    }
  ]
}
```

---

### Query 3: MCP Connect Activity (Last 24h)

**Purpose**: Track which MCP servers users are trying to connect (interest signals)

**Query Type**: Custom HogQL

```sql
SELECT
  person.properties.email as email,
  properties.template_name as mcp_server,
  properties.template_id as template_id,
  properties.has_oauth as requires_oauth,
  count() as clicks,
  min(timestamp) as first_click,
  max(timestamp) as last_click
FROM events
WHERE event = 'mcp_connect_clicked'
  AND timestamp > now() - INTERVAL 1 DAY
  AND person.properties.email NOT LIKE '%@datagen.dev'
  AND person.properties.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
GROUP BY email, mcp_server, template_id, requires_oauth
ORDER BY first_click DESC
```

**Expected Output**:
```json
{
  "results": [
    {
      "email": "prospect@company.com",
      "mcp_server": "HubSpot",
      "template_id": "hubspot-mcp",
      "requires_oauth": true,
      "clicks": 3,
      "first_click": "2026-02-28T09:15:00Z",
      "last_click": "2026-02-28T09:18:00Z"
    }
  ]
}
```

---

## Neon Queries (24h Delta)

### Query 4: New Deployments (Last 24h)

**Purpose**: Track custom tools deployed in the last 24 hours

**Tool**: `mcp_Neon_run_sql`

```sql
SELECT
  w.email,
  d.id as deployment_id,
  d.name as deployment_name,
  d.description,
  d.created_at,
  d.updated_at,
  LENGTH(d.final_code) as code_length,
  d.deployment_type
FROM fastapi_deployment d
JOIN fastapi_user f ON d.user_id = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE d.created_at > NOW() - INTERVAL '24 hours'
  AND w.email NOT LIKE '%@datagen.dev'
  AND w.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
ORDER BY d.created_at DESC
```

**Expected Output**:
```json
{
  "rows": [
    {
      "email": "user@example.com",
      "deployment_id": 12345,
      "deployment_name": "linkedin_scraper_v2",
      "description": "Scrape LinkedIn profiles and save to Airtable",
      "created_at": "2026-02-28T11:30:00Z",
      "updated_at": "2026-02-28T11:30:00Z",
      "code_length": 2847,
      "deployment_type": "private"
    }
  ]
}
```

**Usage**:
```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "project_id": "rough-base-02149126",
    "database": "datagen",
    "sql": "<SQL above>"
  }
}
```

---

### Query 5: New Failed Runs with Error Logs (Last 24h)

**Purpose**: Identify failed workflow runs and their error messages for categorization

**Tool**: `mcp_Neon_run_sql`

```sql
SELECT
  w.email,
  r.id as run_id,
  r.run_state,
  r.created_at,
  r.run_error_log,
  LENGTH(r.run_error_log) as error_length,
  d.name as deployment_name
FROM fastapi_run r
JOIN fastapi_user f ON r.user_id = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
LEFT JOIN fastapi_deployment d ON r.deployment_id = d.id
WHERE r.created_at > NOW() - INTERVAL '24 hours'
  AND r.run_state = 'failed'
  AND w.email NOT LIKE '%@datagen.dev'
  AND w.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
ORDER BY r.created_at DESC
LIMIT 100
```

**Expected Output**:
```json
{
  "rows": [
    {
      "email": "user@example.com",
      "run_id": 67890,
      "run_state": "failed",
      "created_at": "2026-02-28T13:22:00Z",
      "run_error_log": "Modal sandbox execution failed (rc=137): OOM killed...",
      "error_length": 487,
      "deployment_name": "data_enrichment_pipeline"
    }
  ]
}
```

---

### Query 6: Tool Executions by User (Last 24h)

**Purpose**: Track who used what tools in the last 24 hours

**Tool**: `mcp_Neon_run_sql`

```sql
SELECT
  w.email,
  t.tool_name,
  t.tool_provider,
  t.tool_type,
  COUNT(*) as execution_count,
  COUNT(CASE WHEN t.status = 'success' THEN 1 END) as successes,
  COUNT(CASE WHEN t.status = 'failed' THEN 1 END) as failures,
  ROUND(AVG(t.execution_duration_ms)) as avg_duration_ms,
  MIN(t.created_at) as first_execution,
  MAX(t.created_at) as last_execution
FROM fastapi_tool_executions t
JOIN fastapi_user f ON t.user_id::integer = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE t.created_at > NOW() - INTERVAL '24 hours'
  AND w.email NOT LIKE '%@datagen.dev'
  AND w.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
GROUP BY w.email, t.tool_name, t.tool_provider, t.tool_type
ORDER BY execution_count DESC
LIMIT 100
```

**Expected Output**:
```json
{
  "rows": [
    {
      "email": "power_user@company.com",
      "tool_name": "mcp_HubSpot_search_contacts",
      "tool_provider": "HubSpot",
      "tool_type": "mcp",
      "execution_count": 45,
      "successes": 43,
      "failures": 2,
      "avg_duration_ms": 1247,
      "first_execution": "2026-02-28T08:00:00Z",
      "last_execution": "2026-02-28T17:30:00Z"
    }
  ]
}
```

---

### Query 7: Failed Tool Executions with Errors (Last 24h)

**Purpose**: Identify tool-level failures for error categorization

**Tool**: `mcp_Neon_run_sql`

```sql
SELECT
  w.email,
  t.tool_name,
  t.tool_provider,
  t.status,
  t.error_type,
  t.error_message,
  t.created_at,
  t.execution_duration_ms
FROM fastapi_tool_executions t
JOIN fastapi_user f ON t.user_id::integer = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE t.created_at > NOW() - INTERVAL '24 hours'
  AND t.status = 'failed'
  AND w.email NOT LIKE '%@datagen.dev'
  AND w.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
ORDER BY t.created_at DESC
LIMIT 100
```

**Expected Output**:
```json
{
  "rows": [
    {
      "email": "user@example.com",
      "tool_name": "mcp_Airtable_create_record",
      "tool_provider": "Airtable",
      "status": "failed",
      "error_type": "INVALID_REQUEST_BODY",
      "error_message": "Field 'email' is required but missing",
      "created_at": "2026-02-28T12:15:00Z",
      "execution_duration_ms": 234
    }
  ]
}
```

---

### Query 8: New Agents Created/Deployed (Last 24h)

**Purpose**: Track new agent executions and what they're doing

**Tool**: `mcp_Neon_run_sql`

```sql
SELECT
  ae.id as execution_id,
  ae.agent_id,
  ae.status,
  LEFT(ae.entry_prompt, 200) as entry_prompt_preview,
  LEFT(ae.result, 200) as result_preview,
  ae.duration_ms,
  ae.started_at,
  ae.completed_at,
  LENGTH(ae.entry_prompt) as prompt_length,
  LENGTH(ae.result) as result_length
FROM wasp_agentexecution ae
WHERE ae.started_at > NOW() - INTERVAL '24 hours'
ORDER BY ae.started_at DESC
LIMIT 50
```

**Expected Output**:
```json
{
  "rows": [
    {
      "execution_id": 98765,
      "agent_id": 123,
      "status": "completed",
      "entry_prompt_preview": "Search for CTOs at Series A startups in NYC and extract their LinkedIn profiles...",
      "result_preview": "Found 47 CTOs matching criteria. Saved to leads.csv with enriched data...",
      "duration_ms": 45230,
      "started_at": "2026-02-28T10:00:00Z",
      "completed_at": "2026-02-28T10:00:45Z",
      "prompt_length": 387,
      "result_length": 1247
    }
  ]
}
```

---

## Data Collection Workflow

### Step 1: Fetch PostHog 24h Data

```python
from datagen_sdk import DatagenClient

client = DatagenClient()

# Query 1: New signups
signup_query = """
SELECT person.properties.email as email, count() as pageviews
FROM events WHERE event = '$pageview'
AND timestamp > now() - INTERVAL 1 DAY
AND person.properties.email NOT LIKE '%@datagen.dev'
GROUP BY email ORDER BY first_seen DESC
"""

signups_result = client.execute_tool("mcp_Posthog_insight_create_from_query", {
    "query": {"kind": "HogQLQuery", "query": signup_query}
})

# Query 2: UI blockers
ui_blockers_result = client.execute_tool("mcp_Posthog_insight_create_from_query", {
    "query": {"kind": "HogQLQuery", "query": ui_blockers_query}
})

# Query 3: MCP clicks
mcp_clicks_result = client.execute_tool("mcp_Posthog_insight_create_from_query", {
    "query": {"kind": "HogQLQuery", "query": mcp_clicks_query}
})
```

### Step 2: Fetch Neon 24h Data

```python
# Query 4: New deployments
deployments = client.execute_tool("mcp_Neon_run_sql", {
    "project_id": "rough-base-02149126",
    "database": "datagen",
    "sql": deployments_query
})

# Query 5: Failed runs
failed_runs = client.execute_tool("mcp_Neon_run_sql", {
    "project_id": "rough-base-02149126",
    "database": "datagen",
    "sql": failed_runs_query
})

# Query 6: Tool executions
tool_executions = client.execute_tool("mcp_Neon_run_sql", {
    "project_id": "rough-base-02149126",
    "database": "datagen",
    "sql": tool_executions_query
})

# Query 7: Failed tool executions
failed_tools = client.execute_tool("mcp_Neon_run_sql", {
    "project_id": "rough-base-02149126",
    "database": "datagen",
    "sql": failed_tools_query
})

# Query 8: New agents
new_agents = client.execute_tool("mcp_Neon_run_sql", {
    "project_id": "rough-base-02149126",
    "database": "datagen",
    "sql": new_agents_query
})
```

### Step 3: Save to tmp Directory

```python
import json
from datetime import datetime
from pathlib import Path

date = datetime.now().strftime("%Y-%m-%d")
tmp_dir = Path(f"tmp/daily-delta-report-{date}")
tmp_dir.mkdir(parents=True, exist_ok=True)

# Save PostHog data
posthog_data = {
    "new_signups": signups_result,
    "ui_blockers": ui_blockers_result,
    "mcp_clicks": mcp_clicks_result
}
with open(tmp_dir / "posthog_24h.json", "w") as f:
    json.dump(posthog_data, f, indent=2)

# Save Neon FastAPI data
neon_fastapi_data = {
    "new_deployments": deployments,
    "failed_runs": failed_runs,
    "tool_executions": tool_executions,
    "failed_tools": failed_tools
}
with open(tmp_dir / "neon_fastapi_24h.json", "w") as f:
    json.dump(neon_fastapi_data, f, indent=2)

# Save Neon Wasp data
neon_wasp_data = {
    "new_agents": new_agents
}
with open(tmp_dir / "neon_wasp_24h.json", "w") as f:
    json.dump(neon_wasp_data, f, indent=2)
```

---

## Error Handling

- **MCP tool failures**: Save error to `tmp/daily-delta-report-{date}/errors.json`
- **Empty results**: Return empty arrays, don't fail the pipeline
- **Partial data**: Continue with available data, mark missing sections in report
- **Query timeouts**: Use `LIMIT 100` to prevent overwhelming queries

---

## Notes

- All queries use **24-hour time window** (`NOW() - INTERVAL '24 hours'` or `now() - INTERVAL 1 DAY`)
- **Exclude internal**: `@datagen.dev` emails and test accounts
- **PostHog**: Use two-step approach (create insight + query) since `query_run` is deprecated
- **Neon**: Cast `user_id` to integer where needed: `t.user_id::integer`
- **Time zones**: All timestamps in UTC
