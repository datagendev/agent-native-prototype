---
name: product-analysis
description: Analyze user failures, platform issues, and product health using multi-source data investigation
---

# Product Analysis Skill

Investigate user issues by querying multiple data sources, separating user code problems from platform infrastructure issues.

## Core Process

### 1. Identify Data Sources

Query schema first to understand available tables:

```json
{
  "tool_alias_name": "mcp_Neon_run_sql",
  "parameters": {
    "sql": "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'",
    "databaseName": "datagen",
    "projectId": "rough-base-02149126"
  }
}
```

**Key tables:**
- `fastapi_tool_executions` - Individual tool calls (granular)
- `fastapi_run` - Workflow-level runs (infrastructure failures)
- `fastapi_code_execution` - Code sandbox executions
- `wasp_user` - User accounts, credits
- `fastapi_user` - User ID mappings

### 2. Query ALL Relevant Sources

**Don't build narrative from single table.** Query all sources before concluding:

```sql
-- Tool-level failures
SELECT tool_name, error_type, COUNT(*)
FROM fastapi_tool_executions
WHERE user_id = X AND status = 'failed'
GROUP BY tool_name, error_type;

-- Workflow-level failures
SELECT LEFT(run_error_log, 200), COUNT(*)
FROM fastapi_run
WHERE user_id = X AND run_state = 'failed'
GROUP BY run_error_log;

-- MCP usage check
SELECT tool_type, COUNT(*)
FROM fastapi_tool_executions
WHERE user_id = X
GROUP BY tool_type;
```

### 3. Separate Infrastructure from User Issues

**Infrastructure Issues (Platform's fault):**
- API timeouts (`Read timed out`)
- Modal sandbox failures (`rc=137`, `rc=-1`)
- False credit checks (user has credits but fails)
- Missing environment variables in sandbox
- Rate limit errors without retry logic
- Breaking API changes without deprecation

**User Issues (User's fault):**
- Invalid parameters in user code
- Logic errors in custom workflows
- Misconfigured API keys (user-provided)
- Incorrect data format from user

### 4. Verify Assumptions with Data

**Before concluding "User is experiencing X":**

```sql
-- Check if user actually uses the tool
SELECT COUNT(*) FROM fastapi_tool_executions
WHERE user_id = X AND tool_name LIKE '%suspected_tool%';

-- If 0 results: User doesn't use this tool!
```

**Common mistakes:**
- ❌ Assuming your debugging errors = user's production errors
- ❌ Assuming "Modal failure" = specific tool failure
- ❌ Building narrative before checking all data sources
- ❌ Not verifying tool usage before diagnosing issues

### 5. Categorize Failures by Root Cause

**Template for failure analysis:**

| Error Type | Count | % | Category | Owner |
|------------|-------|---|----------|-------|
| API timeout | X | Y% | Infrastructure | Platform |
| False credit check | X | Y% | Bug | Platform |
| Rate limit (no retry) | X | Y% | Missing feature | Platform |
| Invalid user params | X | Y% | User error | User |

**Target:** >85% of failures should be categorized

---

## Analysis Workflow

### Step 1: User Overview

```sql
-- Get user stats
SELECT
  w.email,
  w.credits,
  COUNT(CASE WHEN t.status = 'success' THEN 1 END) as successes,
  COUNT(CASE WHEN t.status = 'failed' THEN 1 END) as failures,
  ROUND(100.0 * COUNT(CASE WHEN t.status = 'success' THEN 1 END) / COUNT(*), 1) as success_rate
FROM fastapi_tool_executions t
JOIN fastapi_user f ON t.user_id::integer = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE w.email = 'user@example.com'
GROUP BY w.email, w.credits;
```

### Step 2: Tool Usage Breakdown

```sql
-- What tools does user actually use?
SELECT
  tool_type,
  tool_name,
  COUNT(*) as uses,
  COUNT(CASE WHEN status = 'success' THEN 1 END) as successes,
  ROUND(100.0 * COUNT(CASE WHEN status = 'success' THEN 1 END) / COUNT(*), 1) as success_rate
FROM fastapi_tool_executions t
JOIN fastapi_user f ON t.user_id::integer = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE w.email = 'user@example.com'
GROUP BY tool_type, tool_name
ORDER BY uses DESC
LIMIT 20;
```

### Step 3: Error Pattern Analysis

```sql
-- Top error types (tool level)
SELECT
  error_type,
  COUNT(*) as occurrences
FROM fastapi_tool_executions t
JOIN fastapi_user f ON t.user_id::integer = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE w.email = 'user@example.com'
  AND t.status = 'failed'
  AND t.created_at >= NOW() - INTERVAL '7 days'
GROUP BY error_type
ORDER BY occurrences DESC;

-- Top error patterns (workflow level)
SELECT
  LEFT(run_error_log, 200) as error_preview,
  COUNT(*) as occurrences
FROM fastapi_run r
JOIN fastapi_user f ON r.user_id = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE w.email = 'user@example.com'
  AND r.run_state = 'failed'
  AND r.created_at >= NOW() - INTERVAL '7 days'
GROUP BY error_preview
ORDER BY occurrences DESC
LIMIT 20;
```

### Step 4: Timeline Analysis

```sql
-- Daily success/failure trend
SELECT
  t.created_at::date as day,
  COUNT(*) as total,
  COUNT(CASE WHEN t.status = 'success' THEN 1 END) as successes,
  COUNT(CASE WHEN t.status = 'failed' THEN 1 END) as failures,
  ROUND(100.0 * COUNT(CASE WHEN t.status = 'success' THEN 1 END) / COUNT(*), 1) as success_rate
FROM fastapi_tool_executions t
JOIN fastapi_user f ON t.user_id::integer = f.id
JOIN wasp_user w ON f.wasp_user_id = w.id
WHERE w.email = 'user@example.com'
GROUP BY day
ORDER BY day DESC
LIMIT 30;
```

---

## Key Learnings from Analysis Process

### Don't Assume, Verify

**Bad Process:**
1. Hit error while debugging
2. Assume user has same error
3. Build narrative around assumption
4. ❌ Wrong conclusion

**Good Process:**
1. Query what tools user actually uses
2. Get error logs from all sources
3. Categorize by root cause
4. ✅ Accurate diagnosis

### Separate Debugging from User Experience

**Your errors ≠ User's errors**

- You hitting Neon MCP failures while analyzing ≠ User hitting Neon MCP failures
- You experiencing tool parameter issues ≠ User experiencing same issues
- Always check: Does user even use this tool?

### Multiple Data Sources Tell Different Stories

| Source | What It Shows |
|--------|---------------|
| `fastapi_tool_executions` | Individual tool call success/failure |
| `fastapi_run` | Workflow execution, infrastructure failures |
| `fastapi_code_execution` | Code sandbox issues, dependency problems |

**Workflow can fail even if all tools succeed** (infrastructure issue)

---

## Output Format

### Analysis Document Structure

```markdown
# User Failure Analysis: [User Email]
**Date:** YYYY-MM-DD
**Data Sources:** fastapi_tool_executions, fastapi_run

## Executive Summary
- Total executions: X
- Success rate: Y%
- Top failure category: Z (infrastructure/user/third-party)

## Data Source Comparison
| Metric | Tool Level | Workflow Level |
|--------|-----------|----------------|
| Total | X | Y |
| Success Rate | X% | Y% |

## Failure Breakdown
| Error | Count | % | Category | Owner |
|-------|-------|---|----------|-------|

## Tool Usage Analysis
- MCP vs Default: X% vs Y%
- Top tools: [list]
- MCP providers: [if any]

## Root Cause Analysis
1. Infrastructure issues (X%)
2. User code issues (Y%)
3. Third-party API issues (Z%)

## Recommended Actions
[Prioritized list]

## Verification Queries Run
[List of SQL queries used for verification]
```

---

## Database Connection Details

| Field | Value |
|-------|-------|
| **Project ID** | `rough-base-02149126` |
| **Database** | `datagen` |
| **Region** | aws-us-east-2 |

---

## Common Pitfalls

1. **Premature Conclusion** - Building narrative before all data gathered
2. **Single Source Analysis** - Only checking one table
3. **Projection Bias** - Assuming your debug experience = user experience
4. **No Tool Usage Verification** - Not checking if user even uses suspected tool
5. **Ignoring Data Source Differences** - Not understanding tool vs workflow level

---

## Case Studies

See `case-studies/` folder for detailed analysis examples with lessons learned.
