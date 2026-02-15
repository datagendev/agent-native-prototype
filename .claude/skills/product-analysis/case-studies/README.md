# Product Analysis Case Studies

Real-world examples of user failure investigations, including process mistakes and lessons learned.

## Available Case Studies

### [jeremy-feb-2026.md](jeremy-feb-2026.md)
**User:** jeremy.scott.ross@gmail.com
**Issue:** 71.8% workflow success rate
**Root Cause:** 86% infrastructure (API timeouts, credit check bugs)
**Key Lesson:** Don't assume debugging errors = user's production errors

**Process Mistakes:**
- Assumed user had Neon MCP failures (he doesn't use Neon)
- Built narrative before querying all data sources
- Projected debugging experience onto user experience

**Corrected Approach:**
- Query tool usage first
- Check ALL data sources (tool + workflow level)
- Read actual error messages (not assumptions)
- Categorize by root cause before concluding

---

## How to Use Case Studies

1. **Before analyzing a user issue:** Read relevant case study to avoid common mistakes
2. **During analysis:** Follow the corrected process, not initial assumptions
3. **After analysis:** Document your process and mistakes for future reference

## Common Patterns

### Red Flags (You're Making Mistakes)
- ❌ Building narrative before gathering all data
- ❌ Assuming user uses a tool without verification
- ❌ Projecting your debugging errors onto user
- ❌ Only checking one data source
- ❌ Using vague categories ("Modal failure" vs specific error)

### Green Flags (Correct Process)
- ✅ Query tool usage first
- ✅ Check multiple data sources (tool + workflow level)
- ✅ Read actual error messages
- ✅ Categorize failures by root cause (infrastructure vs user vs third-party)
- ✅ Verify every assumption with SQL queries

## Template for New Case Studies

```markdown
---
user: email@example.com
date: YYYY-MM-DD
total_executions: X
success_rate: Y%
primary_issue: infrastructure|user|third-party
---

# Case Study: [Brief Title]

## Summary
[One paragraph overview]

## Key Findings
[Data-driven findings]

## Analysis Process Mistakes
[What went wrong initially]

## Corrected Process
[What should have been done]

## Recommended Actions
[Prioritized fixes]

## Lessons Learned
[Process improvements for next time]

## Impact
[Business value of correct analysis]
```
