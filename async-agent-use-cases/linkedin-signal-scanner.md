---
title: "LinkedIn Signal Scanner"
description: "Auto-scan LinkedIn for customer signals and surface relevant buying intent"
category: "use-cases"
tags: ["async-agent", "linkedin", "signal-detection", "social-selling"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "high"
based_on: ["[[business-ops-agents-jiquan]]"]
---

# LinkedIn Signal Scanner

Scan LinkedIn for customer signals, make contextual judgment calls about relevance.

## Problem

- Buying signals hidden across LinkedIn (job changes, funding, posts, comments)
- Manual monitoring doesn't scale beyond 20-30 accounts
- Sales misses timely outreach windows
- No systematic way to track prospect activity

## Solution

Scheduled async agent that:
1. Monitors target accounts and contacts on LinkedIn
2. Detects relevant signals (job changes, posts, engagement)
3. Scores relevance with contextual judgment
4. Surfaces actionable signals to sales

## Trigger

```
Cron: Daily (6am) OR
Manual: "Scan LinkedIn for signals on [account list]"
```

## Pipeline

```
1. LOAD target accounts/contacts
   - From CRM "Target Accounts" list
   - Or custom watch list
    ↓
2. FOR EACH target:
   - Fetch recent LinkedIn activity
   - Posts, comments, job changes, company updates
    ↓
3. ANALYZE signals
   - Job change? → Timing opportunity
   - Funding announced? → Budget unlocked
   - Pain point post? → Relevant content to share
   - Competitor mention? → Competitive intel
   - Hiring for [role]? → Initiative signal
    ↓
4. SCORE relevance
   - High: Direct buying signal (job change to target role, funding)
   - Medium: Indirect signal (relevant post, industry comment)
   - Low: General activity (likes, minor updates)
    ↓
5. GENERATE signal digest
   - Group by priority
   - Include suggested action
    ↓
6. DISTRIBUTE
   - Slack to #sales-signals
   - Optional: Create CRM tasks for high-priority signals
```

## Signal Categories

| Signal Type | Example | Priority | Suggested Action |
|-------------|---------|----------|------------------|
| Job Change | Target contact promoted to VP | High | Congratulate + re-engage |
| New Hire | Company hiring for [relevant role] | High | Time expansion convo |
| Funding | Series B announced | High | Budget discussion |
| Pain Point Post | Complaining about [problem we solve] | High | Share relevant content |
| Competitor Mention | Evaluating competitor | Medium | Competitive positioning |
| Industry Comment | Engaged with industry content | Medium | Thought leadership share |
| Company News | Office expansion, new market | Medium | Growth conversation |
| General Activity | Likes, generic posts | Low | Passive tracking |

## Signal Schema

```yaml
signal:
  id: string
  detected_at: datetime

  source:
    type: post|comment|profile_change|company_update
    url: string

  target:
    person: string
    company: string
    role: string
    account_tier: strategic|target|general

  signal:
    type: job_change|funding|pain_point|competitor|hiring|engagement
    priority: high|medium|low
    content: string  # The actual signal content
    context: string  # Why this matters

  recommendation:
    action: reach_out|monitor|share_content|add_to_sequence
    message_suggestion: string
    timing: immediate|this_week|when_relevant
```

## Output: Daily Signal Digest

```markdown
# LinkedIn Signals: {date}

## High Priority (Action Today)

### 🔄 Job Change: Sarah Chen → VP Sales at Acme Corp
**Signal**: Promoted from Director to VP
**Why it matters**: Decision-maker for our ICP, previous engagement 6 months ago
**Action**: Congratulate and re-engage
**Suggested message**: "Congrats on the VP role, Sarah! Last time we spoke you mentioned [context]. Now that you're leading the team, would love to share how [company] helped [similar VP] with..."

---

### 💰 Funding: TechStart Inc announces $20M Series B
**Signal**: Series B closed, expanding sales team
**Why it matters**: Target account, now has budget
**Action**: Reach out to [contact] about scaling plans
**Suggested message**: "Saw the news about the Series B - congrats! As you scale the team, [value prop]..."

---

## Medium Priority (This Week)

### 💬 Pain Point: Marcus Lee posted about CRM frustrations
**Signal**: "Spending 2 hours/day on manual data entry..."
**Why it matters**: Exact problem we solve
**Action**: Share automation content
**Link**: [Post URL]

---

## Signals Summary
- High priority: 3
- Medium priority: 7
- Accounts with activity: 12/50 monitored
- New signals vs last week: +5
```

## Integration Points

- **Input**: LinkedIn (via MCP or scraping), CRM account lists
- **Processing**: DataGen SDK for fetching and analysis
- **Output**: Markdown digest, Slack, CRM task creation
- **Optional**: Sequence enrollment for high-priority signals

## Success Metrics

- Signals detected per day: 5-15 high/medium priority
- Signal-to-meeting conversion: Track over time
- Coverage: % of target accounts with recent activity captured
- Timeliness: Signals surfaced within 24 hours of activity

## Implementation Notes

### Phase 1: Manual List
Scan a fixed list of 50 target accounts daily.

### Phase 2: CRM Integration
Pull dynamic target account list from CRM.

### Phase 3: Intelligent Prioritization
ML-informed relevance scoring based on historical conversion data.

## MCP Requirements

- LinkedIn MCP (profile viewing, post fetching)
- CRM MCP (account lists, task creation)
- Slack MCP (notifications)
