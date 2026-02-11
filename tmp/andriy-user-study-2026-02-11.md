# Deep Dive: andriyvovchak15@gmail.com
**Analysis Date**: February 11, 2026
**User Status**: At-Risk / Inactive (Last activity: Feb 9, 2026)

---

## 📊 User Profile

| Attribute | Value |
|-----------|-------|
| **Email** | andriyvovchak15@gmail.com |
| **User ID** | 131 (fastapi), 911832c6-313d-4896-ba21-37fe6c708dfb (wasp) |
| **Signup Date** | January 13, 2026 (29 days ago) |
| **Subscription** | Active |
| **Credits** | 5,000 (never used) |
| **Last Activity** | February 9, 2026 at 11:35 AM (2 days ago) |
| **Days Since Signup** | 29 days |

---

## 🎯 Use Case: Company Research → Buying Committee Mapping

Andriy is using DataGen for a **sophisticated B2B intelligence workflow**:

### Primary Workflow
1. **Company Discovery**: Search for target companies on LinkedIn
2. **Deep Research**: Use AI to research companies (ChatGPT, Perplexity)
3. **People Mapping**: Find key decision-makers at target companies
4. **AI Classification**: Use AI to classify roles and create buying committees

### Use Case Example
His code executions show he's building **"Buying Committee Mappers"**:
- `buying_committee_mapper_ziina` - Mapping Ziina's finance department
- `buying_committee_mapper_tax_star` - Mapping Tax Star's finance department
- He's targeting **Pemo's buying committee roles** (likely competitive intelligence or sales targeting)

**This is an advanced ABM (Account-Based Marketing) use case.**

---

## ✅ What's Working for Andriy

### 1. **LinkedIn Company Search** - 69 Successful Calls
- **Success Rate**: 85% (69 success / 81 total)
- **Average Duration**: 2-8 seconds
- **Peak Usage**: Feb 5-6 (60+ searches in one session)
- **What he's doing**: Batch searching for companies (likely UAE market based on company names)

### 2. **AI Research Tools** - 38 Successful Calls
- **ChatGPT Web Research**: 38 successful calls, avg 2-3 seconds
- **Perplexity Search**: 5 successful calls, avg 3-7 seconds
- **What he's doing**: Enriching company data with web research after finding them on LinkedIn

### 3. **AI Writing** - 4 Successful Calls
- **Success Rate**: 100%
- **What he's doing**: Likely writing summaries or reports from research data

### 4. **Code Execution Workflow** - 5 Successful Executions
All 5 of his code executions completed successfully:
- `buying_committee_mapper_ziina` - 99 seconds (complex workflow)
- `buying_committee_mapper_tax_star` - 50 seconds (twice, refined version)
- `Enrich Pemo customer companies via LinkedIn` - 38 seconds

**Andriy successfully built and deployed working agents!**

---

## ❌ What's Failing for Andriy

### 1. **LinkedIn Person Search Failures** - 7 Failed Attempts
**Error**: `Resource not found` (RuntimeError)
**When**: Feb 9, 11:34-11:35 AM (his last session)
**Impact**: 70% failure rate on person searches (7 failed / 10 total)

**Root Cause**: After successfully mapping companies, he tried to find **specific people** but the search couldn't find them.

**Example Pattern**:
```
11:34:47 - search_linkedin_person - FAILED - "Resource not found"
11:34:55 - search_linkedin_person - SUCCESS
11:35:06 - search_linkedin_person - FAILED - "Resource not found"
11:35:12 - search_linkedin_person - FAILED - "Resource not found"
... 4 more failures
```

This is **frustrating** - he found 1 person successfully but couldn't find 6 others. Likely:
- Searching for people at companies he researched
- Person names might be misspelled or LinkedIn profiles don't exist
- Tool might not handle name variations well

### 2. **Credit Errors on Feb 6** - 5 Failed Attempts
**Error**: `Insufficient credits to perform this operation`
**When**: Feb 6, 11:04 AM and 12:24 PM
**Tools Affected**:
- `search_linkedin_company` - 3 failures
- `perplexity_search` - 2 failures

**What happened**: He ran out of credits mid-session on Feb 6, but **credits were refilled to 5,000**.

**Why this is weird**: He currently has 5,000 credits and never used them since refill. This suggests:
- Credits were manually added by support
- He stopped using the product after this incident

### 3. **One Failed Code Execution**
**What**: "LinkedIn Enrichment - IT Companies Batch 1"
**When**: Feb 6, 10:07 AM
**Duration**: 132ms (failed immediately)
**Error**: Not logged (likely failed during initialization)

This was right after the credit errors, so he might have been blocked from starting the workflow.

---

## 📉 Usage Timeline & Churn Signals

### Activity Pattern
```
Jan 13: Signed up
Jan 28: First tool usage (Rube MCP tools - 3 calls)
Feb 5:  Heavy usage day - 13 LinkedIn searches + 3 ChatGPT calls
Feb 6:  Peak day - 81 LinkedIn searches + 29 ChatGPT calls
        [CREDIT ERRORS] - 5 failures due to insufficient credits
        [FAILED CODE EXECUTION] immediately after
Feb 7:  Light web activity (browsing tools, no executions)
Feb 9:  Final session - 3 successful code executions
        [PERSON SEARCH FAILURES] - 7 out of 10 person searches failed
        Last activity: 11:35 AM
Feb 11: INACTIVE (Today - 2 days since last activity)
```

### 🚨 Churn Risk Signals

1. **Abrupt Stop After Failures**: Last session ended with 7 consecutive person search failures
2. **No Activity for 2 Days**: Previously active daily
3. **Credit Issues**: Experienced credit errors, possibly frustrated
4. **Incomplete Workflow**: Successfully mapped companies but failed to find people (last step of workflow)
5. **5,000 Unused Credits**: Had credits refilled but never used them since

---

## 💡 What Andriy Was Trying to Accomplish (Hypothesis)

Based on code execution names and tool usage:

### Goal: Build a Buying Committee Intelligence System
**Target Market**: UAE/Middle East fintech/finance companies
**Competitor**: Pemo (corporate card/expense management)

**His Workflow**:
1. ✅ Find target companies on LinkedIn (Ziina, Tax Star, etc.)
2. ✅ Research companies using AI (industry, size, focus)
3. ❌ Find specific people at these companies (CFO, finance team)
4. ⚠️ Map people to buying committee roles
5. ⚠️ Export/use this data (unknown - workflow incomplete)

**Blocked**: He got stuck at step 3 - couldn't find the specific people he needed.

---

## 🔍 PostHog Activity Analysis

**Last Web Session**: Feb 9, 2026 at 10:19-11:20 AM

### Pages Visited (Most Recent Session)
1. **Login** → `/login-success` at 10:19:05 AM
2. **MCP Servers** → `/signalgen/mcp-servers` (exploring available tools)
3. **Tools** → `/signalgen/tools` (checking tool availability)
4. **Runs** → `/signalgen/runs` (viewing his workflows)
5. **Agents** → `/signalgen/agents` (managing his buying committee agents)
6. **Agent Logs** → `/signalgen/agent-logs` (checking execution logs)

**Pattern**: He was **actively debugging** - checking tools, runs, and logs. This suggests:
- He encountered issues (the person search failures)
- Tried to understand what went wrong
- Reviewed agent logs to diagnose problems

### Previous Session (Feb 7)
- Similar pattern: Agents → Runs → Tools → MCP Servers
- Just browsing, no executions
- Possibly trying to figure out why his workflow wasn't working

**Interpretation**: After the credit errors on Feb 6 and person search failures on Feb 9, he's been **stuck in investigation mode** rather than active development.

---

## 🎯 Why Andriy Matters (Strategic Value)

### High-Value Use Case
Andriy represents a **sophisticated B2B intelligence user**:
- Building custom agents for competitive intelligence
- Multi-tool orchestration (LinkedIn + AI + classification)
- Real business use case (buying committee mapping)
- Successfully deployed working code

### Market Segment Indicator
His use case suggests DataGen has PMF for:
- **ABM/Sales Intelligence** teams
- **Competitive Intelligence** analysts
- **Market Research** firms
- **VC/Private Equity** due diligence

### Product Gaps Revealed
His failures highlight critical issues:
1. LinkedIn person search reliability (70% failure rate)
2. Credit system confusion (insufficient credits → manual refill → unused)
3. Error handling in workflows (no fallback when person search fails)

---

## 🚀 Recommended Actions

### Immediate (Next 24 Hours)

1. **Personal Outreach**
   - Subject: "Saw you built buying committee mappers - ran into issues?"
   - Acknowledge the person search failures
   - Offer to help debug or provide workarounds
   - Show genuine interest in his use case

2. **Technical Investigation**
   - Why is `search_linkedin_person` failing with "Resource not found"?
   - Is this a LinkedIn API issue or search query problem?
   - Can we implement fuzzy matching or alternative search methods?

### Short-Term (This Week)

3. **Credit System Clarity**
   - Review his credit history - why did he run out on Feb 6?
   - Clarify credit costs for different tools
   - Consider adding credit warnings before operations

4. **Person Search Improvements**
   - Add better error messages (e.g., "Person not found - try searching by company + title")
   - Implement fallback strategies when direct search fails
   - Document best practices for person searches

5. **Workflow Recovery Feature**
   - Allow workflows to continue when some searches fail
   - Add "retry with different query" option
   - Save partial results instead of failing entire workflow

### Long-Term (Next Month)

6. **ABM/Intelligence Templates**
   - Create "Buying Committee Mapper" template based on his workflow
   - Pre-built agents for competitive intelligence
   - Document this use case in marketing

7. **LinkedIn Enrichment Reliability**
   - Monitor LinkedIn tool success rates
   - Add better handling for missing/restricted profiles
   - Consider alternative data sources (Apollo, ZoomInfo)

---

## 📝 Email Outreach Draft

**Subject**: Buying committee mappers - impressive work! Hit any roadblocks?

Hey Andriy,

I noticed you built some really sophisticated buying committee mapping agents last week - super impressive use case for competitive intelligence!

I also saw your Feb 9 session ran into some issues with LinkedIn person searches (7 "Resource not found" errors in a row). That's frustrating, and I want to help get you unblocked.

**Quick question**: Were you searching for specific people by name, or trying to find people by role/title at companies?

The person search works best when you have:
- Full name as it appears on LinkedIn
- Current company confirmation

If you were searching by role (e.g., "CFO at Ziina"), that's a different pattern we can help with. I can show you a workaround or we can improve the tool for your use case.

Also noticed the credit issues on Feb 6 - those should be resolved now (you have 5,000 credits). Let me know if you hit any more blocks.

Your buying committee workflow is exactly the kind of sophisticated intelligence use case DataGen was built for. Would love to understand more about what you're building and make sure you have what you need.

Want to jump on a quick call this week?

Best,
[Your name]

P.S. - Would love to feature your buying committee mapper as a template if you're open to it. Other users would find it valuable.

---

## 📊 Summary Statistics

| Metric | Value | Status |
|--------|-------|--------|
| **Total Tool Executions** | 143 | 🟢 Active User |
| **Success Rate** | 86% (123/143) | 🟡 Below 95% |
| **Unique Tools Used** | 11 | 🟢 Power User |
| **Code Executions** | 5 | 🟢 Builder |
| **Code Success Rate** | 80% (4/5) | 🟡 One failure |
| **Days Since Signup** | 29 | 🟢 Engaged |
| **Days Since Last Activity** | 2 | 🔴 At Risk |
| **Credits Remaining** | 5,000 | 🔴 Never Used |
| **Custom Agents Built** | 2+ | 🟢 Advanced |

**Overall Assessment**: High-value user with advanced use case, currently **blocked by tool reliability issues**. High churn risk but saveable with immediate outreach and technical fixes.

---

## 🎬 Next Steps

1. ✅ Send personalized email (drafted above)
2. 🔧 Investigate LinkedIn person search failures
3. 📊 Review credit system for this user
4. 📞 Schedule call to understand use case better
5. 🛠️ Build "Buying Committee Mapper" template
6. 📈 Monitor for return activity

**Priority**: HIGH - This user represents a valuable market segment and his use case is replicable across other ABM/intelligence users.
