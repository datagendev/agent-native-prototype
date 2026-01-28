---
title: "Living Objection Library"
description: "Auto-capture, categorize, and integrate new objections from sales calls"
category: "use-cases"
tags: ["async-agent", "sales-enablement", "objections", "automation"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "high"
based_on: ["[[10-claude-code-use-cases-gtm]]"]
---

# Living Objection Library

New objections auto-captured, categorized, and integrated into response frameworks.

## Problem

- Objection handling docs are static, outdated within months
- New objections emerge but aren't documented
- Best responses live in top reps' heads
- New hires face objections they've never seen

## Solution

Async agent that:
1. Extracts objections from every call
2. Categorizes by type and severity
3. Captures response effectiveness
4. Updates central objection library

## Trigger

```
Fireflies/Gong webhook → New transcript available
```

## Pipeline

```
1. RECEIVE transcript webhook
    ↓
2. EXTRACT objections
   - Identify objection statements
   - Capture surrounding context
   - Extract rep's response
   - Note outcome (overcome/not/partial)
    ↓
3. CATEGORIZE
   - Match to existing categories OR
   - Flag as new category candidate
    ↓
4. DEDUPLICATE
   - Similar to existing? → Merge/link
   - Novel? → Create new entry
    ↓
5. UPDATE library
   - Add new objections
   - Update frequency counts
   - Add successful response examples
    ↓
6. NOTIFY (if significant)
   - New objection category detected
   - High-frequency objection trending
```

## Objection Schema

```yaml
objection:
  id: string
  category: pricing|competition|timing|authority|need|trust|technical
  subcategory: string

  statement: string  # The actual objection
  variations: list[string]  # Similar phrasings

  context:
    typical_stage: discovery|demo|negotiation|close
    typical_persona: champion|blocker|economic_buyer
    severity: deal_killer|speed_bump|smoke_screen

  frequency:
    total_count: int
    last_30_days: int
    trend: increasing|stable|decreasing

  responses:
    - response: string
      effectiveness: high|medium|low
      source_call: string
      rep: string

  recommended_response: string
  resources: list[string]  # Links to relevant content
```

## Objection Categories

| Category | Examples |
|----------|----------|
| **Pricing** | "Too expensive", "No budget", "Competitor is cheaper" |
| **Competition** | "We're looking at X", "What about Y?", "Already using Z" |
| **Timing** | "Not now", "Next quarter", "After [event]" |
| **Authority** | "Need to check with...", "Not my decision" |
| **Need** | "We're fine with current solution", "Not a priority" |
| **Trust** | "Never heard of you", "Too small/new", "References?" |
| **Technical** | "Does it integrate with...", "Security concerns" |

## Output: Objection Library

```markdown
# Objection Library

Last updated: {timestamp}
Total objections tracked: 47
New this month: 3

## Pricing (12 objections)

### "Your solution is too expensive"
**Frequency**: 23 mentions (last 30 days: 8, trending: stable)
**Stage**: Negotiation
**Severity**: Speed bump

**Recommended Response**:
> "I understand budget is important. Let me ask - when you look at
> the time your team spends on [manual process], what's that costing
> you monthly? Our customers typically see ROI within..."

**Effective Responses**:
1. ROI calculation approach (85% effectiveness)
2. Phased implementation option (70% effectiveness)

**Resources**: [ROI Calculator], [Case Study: Acme saved $X]

---

### "Competitor X is 30% cheaper"
**Frequency**: 15 mentions (last 30 days: 6, trending: increasing)
...
```

## Integration Points

- **Input**: Transcript webhooks (Fireflies, Gong)
- **Processing**: DataGen SDK extraction and categorization
- **Storage**: Markdown in repo OR database for querying
- **Output**: Updated library, Slack alerts for new patterns

## Success Metrics

- Objection capture rate: 95%+
- Time from call → library update: < 5 minutes
- Response effectiveness tracking accuracy
- New hire ramp time reduction

## Implementation Notes

### Phase 1: Capture
Extract objections, store raw. Manual categorization.

### Phase 2: Categorize
Auto-categorize, deduplicate, track frequency.

### Phase 3: Recommend
ML-informed response recommendations based on effectiveness data.
