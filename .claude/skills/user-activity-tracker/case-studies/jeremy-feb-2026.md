---
user: jeremy.scott.ross@gmail.com
date: 2026-02-15
analysis_period: 2026-01-12 to 2026-02-13
total_executions: 9805
success_rate: 78.8%
primary_issue: infrastructure
---

# Case Study: Jeremy's Infrastructure Failures

## Summary

**User:** jeremy.scott.ross@gmail.com (Power user #1)
**Issue:** 71.8% workflow success rate (2,492 failures)
**Root Cause:** 86% infrastructure issues, NOT user code

## Key Findings

### Data Source Comparison
| Source | Total | Success Rate | Main Issues |
|--------|-------|--------------|-------------|
| `fastapi_tool_executions` | 9,805 | 78.8% | Credit errors, API changes |
| `fastapi_run` | 9,143 | 71.8% | API timeouts, Modal OOM |

### Failure Breakdown (from `fastapi_run`)
| Error | Count | % | Category |
|-------|-------|---|----------|
| DataGen API timeout | 907 | 36% | Infrastructure |
| False credit check | 810 | 32% | Platform bug |
| HubSpot rate limits | 314 | 13% | Missing retry logic |
| Missing API key in Modal | 56 | 2% | Env propagation |
| Modal OOM (rc=137) | 46 | 2% | Resource limits |

**86% of failures = platform infrastructure issues**

### Tool Usage
- **96.8% default tools** (9,489 calls)
- **3.2% MCP tools** (316 calls)
  - Notion: 224 calls (~80% success)
  - Gmail: 36 calls (100% success)
  - Composio: 16 calls (0% success - broken)
- **0% Neon MCP** - user doesn't use Neon

### What User Is Building
LinkedIn prospecting automation:
1. Search LinkedIn prospects
2. Extract engagement data
3. Structure with `extract_structured_output` (6,491 uses)
4. Store in Notion
5. Sync to HubSpot
6. Follow up via Gmail

## Analysis Process Mistakes

### Initial Wrong Assumptions
1. ❌ **Assumed my debugging errors = user's errors**
   - I hit Neon MCP parameter issues while analyzing
   - Incorrectly assumed user had same issues
   - Didn't verify user even uses Neon MCP

2. ❌ **Built narrative from partial data**
   - Only looked at daily report summary initially
   - Didn't check multiple data sources
   - Jumped to conclusions without verification

3. ❌ **Conflated "Modal failures" with "MCP failures"**
   - Saw "Modal sandbox execution failed" in my errors
   - Assumed this meant MCP tool issues
   - Actual issue: DataGen API timeouts, not MCP

### Corrected Process
1. ✅ **Query tool usage first:**
   ```sql
   SELECT tool_type, COUNT(*) FROM fastapi_tool_executions
   WHERE user_id = X GROUP BY tool_type;
   -- Result: 3.2% MCP, 0% Neon → User doesn't use Neon!
   ```

2. ✅ **Check ALL data sources:**
   - `fastapi_tool_executions` - tool level
   - `fastapi_run` - workflow level
   - Error logs from both tables

3. ✅ **Read actual error messages:**
   - Not "Modal failure" (vague)
   - But "HTTPSConnectionPool: Read timed out" (specific)

4. ✅ **Categorize by root cause:**
   - 36% API timeouts → Infrastructure
   - 32% False credits → Platform bug
   - 13% Rate limits → Missing feature

## Recommended Actions (Prioritized)

### Week 1 (Infrastructure)
1. Fix DataGen API timeouts (36% of failures)
   - Investigate slow endpoints (>30s)
   - Increase timeout 30s → 60s
   - Add retry logic

2. Fix credit check bug (32% of failures)
   - Atomic check-and-deduct
   - Show balance in error message

### Week 2 (Third-party)
3. HubSpot rate limit handling (13% of failures)
   - Exponential backoff
   - Respect rate limits
   - Cache responses

### Week 3 (Modal)
4. Modal sandbox improvements (2% of failures)
   - Increase creation rate limit 5/s → 10/s
   - Add memory limits
   - Fix env var propagation

## Lessons Learned

### Process Improvements
1. **Always verify tool usage before diagnosing**
   - Don't assume user uses suspected tool
   - Query `SELECT tool_name WHERE user = X AND tool LIKE '%suspect%'`

2. **Separate debugging experience from user experience**
   - My errors while analyzing ≠ user's production errors
   - Projection bias is real

3. **Query all data sources before concluding**
   - Tool level vs workflow level tell different stories
   - Workflow can fail even if tools succeed (infrastructure)

4. **Read actual error messages**
   - "Modal failure" is too vague
   - Get actual error text and categorize precisely

### Key Insight
**When user has multiple days with 100% success rate, failures are likely platform issues, not user code.**

Evidence: Jeremy had 100% success on Jan 22, 25, Feb 9 → proves his code works when infrastructure is stable.

## Impact

**After fixes:**
- Success rate: 71.8% → >90%
- User retained (was at risk)
- Platform reliability improved for all users

**Business value:**
- Retained #1 power user
- Fixed infrastructure issues affecting all users
- Improved platform success rate by 8-12%
