---
title: "Pattern Detection"
description: "Identify win/loss patterns across 50+ sales calls automatically"
category: "use-cases"
tags: ["async-agent", "analytics", "sales-intelligence", "patterns"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "medium"
based_on: ["[[10-claude-code-use-cases-gtm]]"]
---

# Pattern Detection

Surface real win/loss reasons across 50+ calls vs. relying on incomplete sales memory.

## Problem

- Sales attributes wins/losses to surface-level reasons ("price", "timing")
- Real patterns hidden across dozens of calls
- No one has time to re-read 50 transcripts
- Tribal knowledge = survivorship bias

## Solution

Scheduled async agent that:
1. Analyzes accumulated transcripts
2. Identifies patterns across outcomes
3. Generates actionable insights report

## Trigger

```
Cron: Weekly (Sunday night) OR
Manual: "Analyze last 30 days of calls"
```

## Pipeline

```
1. QUERY transcript database
   - Filter: last 30 days OR last N calls
   - Include: outcome labels (won/lost/stalled)
    ↓
2. BATCH PROCESS transcripts
   - Extract: objections, competitors, pain points, decision criteria
   - Tag: by segment, deal size, outcome
    ↓
3. ANALYZE patterns
   - Win patterns: What's present in wins, absent in losses?
   - Loss patterns: Common objections, competitor presence
   - Stall patterns: Missing buying signals
    ↓
4. GENERATE insights report
   - Top 5 win factors
   - Top 5 loss reasons
   - Emerging objections (new this month)
   - Competitor trend shifts
    ↓
5. DISTRIBUTE
   - Save to `reports/win-loss/weekly-{date}.md`
   - Slack to #sales-insights
   - Optional: Email to leadership
```

## Output: Weekly Insights Report

```markdown
# Win/Loss Patterns: Week of {date}

## Summary
- Calls analyzed: 47
- Win rate: 32% (15/47)
- Top segment: Mid-market (42% win rate)

## Win Patterns
1. **Champion identified early** (present in 80% of wins)
2. **Security review completed** (73% of wins)
3. **Integration demo requested** (67% of wins)

## Loss Patterns
1. **"Need to check with IT"** - 60% of losses
2. **Competitor X mentioned** - 45% of losses
3. **No clear timeline** - 40% of losses

## Emerging Signals
- New objection: "AI governance concerns" (5 mentions, up from 0)
- Competitor Y entering deals more frequently (+30% vs last month)

## Recommendations
1. Develop IT stakeholder enablement content
2. Update Competitor X battlecard with new positioning
3. Create AI governance FAQ for security-conscious buyers
```

## Pattern Categories

### Win Factors
- Champion presence and engagement level
- Multi-threading (contacts engaged)
- Technical validation completed
- Clear timeline established
- Budget confirmed

### Loss Indicators
- Single-threaded deals
- Competitor deep in evaluation
- "We'll get back to you" endings
- Price-focused conversations
- No next steps agreed

### Stall Signals
- Long gaps between touches
- Rescheduled demos
- "Internal alignment" mentions
- Vague timelines

## Data Requirements

Minimum for meaningful patterns:
- 30+ transcripts with outcome labels
- Mix of won/lost/stalled outcomes
- Consistent transcript quality

## Integration Points

- **Input**: Transcript database (Fireflies, Gong, custom)
- **Processing**: DataGen SDK batch analysis
- **Output**: Markdown reports, Slack, optional CRM enrichment

## Success Metrics

- Patterns validated by sales: 70%+ accuracy
- Actionable insights per report: 3-5
- Report read rate: 80%+ of sales team
- Win rate improvement: Track over quarters
