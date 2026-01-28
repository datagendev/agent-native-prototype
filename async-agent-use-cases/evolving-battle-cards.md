---
title: "Evolving Battle Cards"
description: "Auto-update competitor intelligence when mentions detected or on schedule"
category: "use-cases"
tags: ["async-agent", "competitive-intelligence", "battlecards", "automation"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "medium"
based_on: ["[[10-claude-code-use-cases-gtm]]"]
---

# Evolving Battle Cards

Competitor mentions trigger automatic research and battlecard updates.

## Problem

- Battlecards are static snapshots, outdated within weeks
- Competitors ship features, change pricing, pivot messaging
- Sales discovers changes mid-call ("Wait, they have that now?")
- Manual competitive research is expensive and infrequent

## Solution

Dual-trigger async agent:
1. **Event-driven**: Competitor mentioned in call → research + update
2. **Scheduled**: Weekly competitive sweep → refresh all cards

## Triggers

```
Trigger 1: Transcript webhook + competitor mention detected
Trigger 2: Cron: Weekly (Monday morning)
```

## Pipeline: Event-Driven

```
1. RECEIVE transcript with competitor mention
    ↓
2. EXTRACT competitor intel from call
   - What prospect said about competitor
   - Features/pricing mentioned
   - Positioning they used
   - Why prospect is considering them
    ↓
3. RESEARCH competitor (if significant mention)
   - Check competitor website for changes
   - Search recent news/announcements
   - Check G2/Capterra for new reviews
    ↓
4. UPDATE battlecard
   - Add new intel from call
   - Flag any product/pricing changes
   - Update "What they're saying" section
    ↓
5. NOTIFY sales
   - "Battlecard updated: {Competitor}"
   - Key changes highlighted
```

## Pipeline: Scheduled Sweep

```
1. FOR EACH tracked competitor:
    ↓
2. RESEARCH
   - Website changes (pricing, features, messaging)
   - Recent press releases
   - G2/Capterra review trends
   - LinkedIn company updates
   - Job postings (signals strategy)
    ↓
3. COMPARE to last sweep
   - Identify changes
   - Score significance
    ↓
4. UPDATE battlecards
   - Refresh all sections
   - Add "Last verified: {date}"
    ↓
5. GENERATE weekly competitive brief
   - Significant changes across all competitors
   - New entrants detected
   - Market shift signals
```

## Battlecard Schema

```yaml
competitor:
  name: string
  website: url
  last_updated: date

  overview:
    positioning: string
    target_market: string
    company_size: string
    funding: string

  product:
    core_features: list[string]
    recent_releases: list[{feature, date}]
    integrations: list[string]
    limitations: list[string]

  pricing:
    model: per_seat|usage|flat
    tiers: list[{name, price, features}]
    last_verified: date

  win_against:
    when_we_win: list[string]
    key_differentiators: list[string]
    talk_track: string

  lose_against:
    when_they_win: list[string]
    their_strengths: list[string]
    landmines: list[string]  # Topics to avoid

  field_intel:
    recent_mentions: list[{date, context, source_call}]
    prospect_perceptions: list[string]
    objections_they_raise: list[string]

  resources:
    case_studies_vs: list[url]
    comparison_page: url
    internal_analysis: url
```

## Output: Battlecard

```markdown
# Battlecard: Competitor X

**Last Updated**: {date} | **Confidence**: High
**Recent Activity**: Pricing change detected, new feature launched

## Quick Facts
- **Positioning**: "The AI-powered [category] for enterprise"
- **Target**: Enterprise, 1000+ employees
- **Pricing**: $99/seat/month (verified {date})

## When We Win
- Complex integrations required
- Security/compliance priority
- Need for customization
- Multi-team deployments

## When They Win
- Price-sensitive buyers
- Simple use cases
- Strong existing relationship
- Fast deployment priority

## Key Differentiators (Us vs Them)
| Capability | Us | Them |
|------------|----|----|
| API flexibility | Full REST + GraphQL | REST only |
| SOC 2 | Type II | Type I |
| Custom workflows | Unlimited | 5 max |

## Talk Track
> "I see you're also looking at X. They're solid for [simple use case].
> Where customers choose us is when they need [differentiator].
> Quick question - how important is [our strength] for your team?"

## Field Intel (Last 30 Days)
- "They said X has better onboarding" - Call with Acme, Jan 15
- "X's pricing was more predictable" - Call with Beta Corp, Jan 12

## Recent Changes
- **Jan 20**: New "Enterprise" tier announced ($149/seat)
- **Jan 10**: Launched Salesforce integration
- **Dec 15**: Series C announced ($50M)

## Resources
- [Head-to-head comparison](/comparisons/vs-competitor-x)
- [Win story: Acme chose us over X](/case-studies/acme)
```

## Integration Points

- **Input**: Transcript webhooks, web scraping, news APIs
- **Processing**: DataGen SDK for extraction and research
- **Storage**: Markdown battlecards in repo
- **Output**: Updated cards, Slack competitive brief

## Success Metrics

- Battlecard freshness: < 7 days since last update
- Field intel capture rate: 90%+ of competitor mentions
- Sales confidence in battlecards (survey)
- Competitive win rate improvement

## Implementation Notes

### Phase 1: Field Intel Only
Capture competitor mentions from calls, append to battlecards.

### Phase 2: Scheduled Research
Weekly web research sweep, update product/pricing sections.

### Phase 3: Real-Time Monitoring
Continuous competitor monitoring with instant alerts.
