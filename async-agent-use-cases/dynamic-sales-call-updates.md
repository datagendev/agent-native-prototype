---
title: "Dynamic Sales Call Updates"
description: "Auto-update battlecards, ICP docs, and content calendars from sales call transcripts"
category: "use-cases"
tags: ["async-agent", "sales-enablement", "transcripts", "automation"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "high"
based_on: ["[[10-claude-code-use-cases-gtm]]"]
---

# Dynamic Sales Call Updates

Single transcript → multiple document updates, automatically.

## Problem

- Sales calls contain gold: objections, competitor mentions, feature requests, buying signals
- This intel dies in transcript graveyards
- Manual extraction doesn't scale
- Documents go stale within weeks

## Solution

Async agent triggered by new transcript that:
1. Extracts structured insights
2. Updates relevant documents
3. Notifies stakeholders of significant changes

## Trigger

```
Fireflies/Gong webhook → New transcript available
```

## Pipeline

```
1. RECEIVE transcript webhook
    ↓
2. FETCH full transcript from Fireflies API
    ↓
3. EXTRACT structured data:
   - Objections raised
   - Competitors mentioned
   - Feature requests
   - Buying signals
   - Pain points
   - Decision criteria
    ↓
4. UPDATE documents:
   - ICP docs (new pain points, criteria)
   - Battlecards (competitor intel)
   - Objection library (new objections)
   - Feature request log
    ↓
5. NOTIFY via Slack:
   - "Updated 3 docs from call with {Company}"
   - Link to changes
```

## Output Artifacts

| Artifact | Update Type | Location |
|----------|-------------|----------|
| ICP Document | Append new insights | `gtm/icp/{segment}.md` |
| Battlecards | Update competitor sections | `gtm/battlecards/{competitor}.md` |
| Objection Library | Add new objections | `gtm/objections/library.md` |
| Feature Requests | Log with context | `product/feature-requests.md` |
| Content Calendar | Suggest topics | `marketing/content-ideas.md` |

## Extracted Data Schema

```yaml
transcript_analysis:
  call_metadata:
    company: string
    attendees: list
    date: date
    outcome: won|lost|ongoing

  objections:
    - objection: string
      context: string
      response_given: string
      effectiveness: worked|failed|partial

  competitors:
    - name: string
      mentions: list[string]
      positioning: string

  feature_requests:
    - feature: string
      priority_signal: high|medium|low
      context: string

  buying_signals:
    - signal: string
      stage: awareness|consideration|decision
```

## Integration Points

- **Input**: Fireflies, Gong, or any transcript provider with webhooks
- **Processing**: DataGen SDK for extraction and document updates
- **Output**: Markdown docs in repo, Slack notifications
- **Optional**: Notion/Confluence sync, CRM field updates

## Success Metrics

- Time from call → updated docs: < 10 minutes
- Documents updated per call: 2-5
- Manual update time saved: 30-60 min/call
- Intel capture rate: 90%+ of actionable insights

## Implementation Notes

### Phase 1: Single Output
Start with objection extraction only. Validate pipeline works.

### Phase 2: Multi-Output
Add battlecard and ICP updates.

### Phase 3: Intelligence Layer
Pattern detection across accumulated transcripts.
