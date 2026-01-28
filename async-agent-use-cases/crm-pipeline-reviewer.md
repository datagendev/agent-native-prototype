---
title: "CRM Pipeline Reviewer"
description: "Auto-analyze pipeline data, identify bottlenecks, and generate contextual outreach"
category: "use-cases"
tags: ["async-agent", "crm", "pipeline-analysis", "sales-ops"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "high"
based_on: ["[[business-ops-agents-jiquan]]"]
---

# CRM Pipeline Reviewer

Review pipeline data, identify bottlenecks, generate contextually appropriate outreach messages.

## Problem

- Pipeline reviews are manual, time-consuming, inconsistent
- Deals stall without anyone noticing until it's too late
- Generic follow-ups don't account for deal context
- Reps focus on easy deals, neglect stuck ones

## Solution

Scheduled async agent that:
1. Analyzes full pipeline for health and bottlenecks
2. Identifies at-risk and stalled deals
3. Generates context-aware outreach for each
4. Provides actionable pipeline report

## Trigger

```
Cron: Daily (7am) before team standup OR
Cron: Weekly (Monday) for full pipeline review
```

## Pipeline

```
1. FETCH pipeline data from CRM
   - All open opportunities
   - Stage, amount, age, last activity, next steps
    ↓
2. ANALYZE pipeline health
   - Stage distribution
   - Velocity by stage
   - Aging deals
   - Coverage vs quota
    ↓
3. IDENTIFY bottlenecks
   - Deals stuck in stage > X days
   - Deals with no recent activity
   - Deals missing next steps
   - High-value deals at risk
    ↓
4. FOR EACH at-risk deal:
   - Review deal history (emails, calls, notes)
   - Understand context and blockers
   - Generate personalized re-engagement message
    ↓
5. GENERATE pipeline report
   - Health summary
   - At-risk deals with actions
   - Suggested outreach messages
    ↓
6. DISTRIBUTE
   - Slack to #sales-pipeline
   - Per-rep summaries via DM
   - Optional: Create CRM tasks
```

## Bottleneck Detection Rules

| Condition | Risk Level | Action |
|-----------|------------|--------|
| No activity in 14+ days | High | Immediate re-engagement |
| Stuck in stage 2x avg time | High | Qualify or disqualify |
| No next step scheduled | Medium | Schedule follow-up |
| Champion went dark | High | Multi-thread or re-engage |
| Close date pushed 2+ times | High | Reality check conversation |
| No recent email opens | Medium | Try different channel |
| Competitor mentioned, no response | High | Competitive positioning |

## Deal Health Schema

```yaml
deal:
  id: string
  name: string
  company: string
  amount: number
  stage: string

  health:
    score: 0-100
    risk_level: healthy|at_risk|critical

  metrics:
    days_in_stage: int
    days_since_activity: int
    total_age: int
    stage_velocity_vs_avg: faster|normal|slower

  blockers:
    - type: no_activity|stuck_stage|no_next_step|champion_dark
      description: string
      days: int

  context:
    last_activity: string
    last_email_subject: string
    key_stakeholders: list[string]
    previous_objections: list[string]

  recommendation:
    action: re_engage|qualify|multi_thread|close_lost
    urgency: today|this_week|monitor
    message: string
```

## Output: Daily Pipeline Report

```markdown
# Pipeline Health Report: {date}

## Summary
| Metric | Value | vs Last Week |
|--------|-------|--------------|
| Total Pipeline | $2.4M | +$150K |
| Deals at Risk | 8 | +2 |
| Avg Days in Stage | 12 | -1 |
| Coverage Ratio | 3.2x | stable |

## Critical: Needs Action Today (3 deals)

### 🚨 Acme Corp - $150K - Demo Stage
**Risk**: No activity in 18 days, champion hasn't responded
**Context**: Demo went well, requested pricing. Sent pricing 18 days ago, no response.
**Last email**: "Following up on the pricing proposal..."

**Suggested Action**: Multi-thread to economic buyer

**Draft Message**:
> Hi Sarah,
>
> I wanted to check in - I know Q1 planning gets hectic. I noticed [CEO name]
> mentioned scaling ops in their recent post. Would it help if I put together
> a quick executive summary for the leadership team?
>
> Also happy to loop in our [relevant role] to discuss [specific concern from demo].

---

### 🚨 Beta Inc - $80K - Negotiation Stage
**Risk**: Close date pushed twice, pricing objection unresolved
**Context**: Liked product, stuck on annual commitment. Asked for monthly, we declined.
**Last activity**: Call 12 days ago, said "checking internally"

**Suggested Action**: Offer creative pricing structure

**Draft Message**:
> Hi Marcus,
>
> Thinking about our conversation on commitment flexibility. What if we
> structured this as a 6-month pilot with annual conversion? That way your
> team gets runway to prove value internally before the full commitment.
>
> Would that work better for your approval process?

---

## At Risk: Action This Week (5 deals)

| Deal | Amount | Risk | Days Stuck | Action |
|------|--------|------|------------|--------|
| TechCo | $60K | No next step | 8 | Schedule follow-up |
| StartupX | $45K | Champion dark | 10 | Find new thread |
| Enterprise Y | $200K | Slow stage velocity | 21 | Executive sponsor |

## Healthy Pipeline (15 deals)
- On track: 12
- Ahead of schedule: 3

## Rep Summary
| Rep | At Risk | Critical | Action Items |
|-----|---------|----------|--------------|
| Alex | 3 | 1 | Re-engage Acme today |
| Jordan | 2 | 1 | Multi-thread Beta Inc |
| Sam | 3 | 1 | Qualify or close TechCo |
```

## Integration Points

- **Input**: CRM (Salesforce, HubSpot, Attio, etc.) via MCP
- **Processing**: DataGen SDK for analysis and message generation
- **Output**: Markdown reports, Slack, CRM tasks
- **Optional**: Calendar integration for scheduling follow-ups

## Success Metrics

- Stalled deals identified: 100% of deals meeting criteria
- Rep action rate on recommendations: 70%+
- Average days-to-close improvement
- Win rate on "at-risk" deals with intervention

## Implementation Notes

### Phase 1: Detection Only
Identify at-risk deals, surface in report. No message generation.

### Phase 2: Context-Aware Messages
Add personalized outreach suggestions based on deal history.

### Phase 3: Auto-Actions
Create CRM tasks, schedule emails, enroll in sequences automatically.

## MCP Requirements

- CRM MCP (pipeline data, deal history, contact info)
- Email MCP (send suggested messages - optional)
- Slack MCP (notifications)
- Calendar MCP (next step scheduling - optional)
