---
title: "Call Transcript to CRM Notes"
description: "Auto-process call transcripts and create structured CRM notes"
category: "use-cases"
tags: ["async-agent", "transcripts", "crm", "automation"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "high"
based_on: ["[[business-ops-agents-jiquan]]"]
---

# Call Transcript to CRM Notes

Automatically locate transcripts, filter for customer interactions, process, and create CRM notes.

## Problem

- Reps spend 15-30 min per call on CRM updates
- Notes are inconsistent, incomplete, or never written
- Key insights lost between call and documentation
- CRM data quality degrades over time

## Solution

Async agent triggered by new transcripts that:
1. Identifies customer-related calls
2. Extracts structured information
3. Creates formatted CRM notes
4. Updates relevant deal fields

## Trigger

```
Fireflies/Gong webhook → New transcript available
```

## Pipeline

```
1. RECEIVE transcript webhook
    ↓
2. FILTER: Is this a customer interaction?
   - Internal meeting? → Skip
   - Vendor call? → Skip
   - Customer/prospect? → Process
    ↓
3. MATCH to CRM record
   - Find contact by email/name
   - Find associated deal/account
    ↓
4. EXTRACT structured data
   - Meeting summary
   - Key discussion points
   - Action items (theirs and ours)
   - Objections/concerns raised
   - Next steps agreed
   - Buying signals
   - Stakeholders mentioned
    ↓
5. GENERATE CRM note
   - Structured format
   - Linked to correct record
    ↓
6. UPDATE CRM fields
   - Next step date
   - Deal stage (if warranted)
   - Key contacts (if new mentioned)
    ↓
7. NOTIFY rep
   - "CRM updated for call with {Company}"
   - Link to note
```

## Call Classification

| Call Type | Action |
|-----------|--------|
| Customer call | Full processing → CRM note |
| Prospect call | Full processing → CRM note |
| Internal meeting | Skip or tag differently |
| Vendor call | Skip |
| Interview | Skip |
| Unknown | Flag for manual review |

## Extracted Data Schema

```yaml
call_summary:
  metadata:
    date: datetime
    duration: minutes
    participants:
      internal: list[string]
      external: list[string]
    company: string
    deal: string  # If matched

  summary:
    one_liner: string  # 1 sentence summary
    key_points: list[string]  # 3-5 bullet points

  discussion:
    topics_covered: list[string]
    questions_asked: list[{who, question}]
    objections: list[string]

  outcomes:
    decisions_made: list[string]
    action_items:
      ours: list[{item, owner, due}]
      theirs: list[{item, owner, due}]
    next_steps: string
    next_meeting: datetime  # If scheduled

  signals:
    buying_signals: list[string]
    risk_signals: list[string]
    stakeholders_mentioned: list[{name, role, sentiment}]
    competitors_mentioned: list[string]

  stage_recommendation:
    current_stage: string
    suggested_stage: string
    rationale: string
```

## Output: CRM Note Format

```markdown
## Call Summary: {date}
**Duration**: 45 min | **Attendees**: Sarah Chen (VP Sales), Mike Lee (IT)

### TL;DR
Positive demo, strong interest in automation features. Main concern is integration timeline. Decision expected by end of month.

### Key Discussion Points
- Walked through automation workflow - Sarah very engaged
- IT needs SOC 2 documentation before security review
- Current process takes 3 hours/day, our solution would cut to 30 min
- Budget approved for Q1, need to move fast

### Action Items
**Us:**
- [ ] Send SOC 2 Type II report → @Alex (by Jan 28)
- [ ] Schedule technical deep-dive with Mike → @Jordan (by Jan 30)
- [ ] Prepare ROI analysis with their numbers → @Alex (by Jan 29)

**Them:**
- [ ] Sarah to get final sign-off from CFO
- [ ] Mike to complete security questionnaire
- [ ] Schedule follow-up for Feb 1

### Signals
✅ **Buying signals**: Budget confirmed, timeline pressure, multiple stakeholders engaged
⚠️ **Risks**: IT security review could delay, CFO not yet involved

### Stakeholders
- Sarah Chen (VP Sales) - Champion, decision maker
- Mike Lee (IT Director) - Technical evaluator, neutral
- *Mentioned*: Jennifer Park (CFO) - Final approver, not yet engaged

### Next Steps
Follow-up call scheduled for Feb 1 to review security docs and discuss implementation timeline.

---
*Auto-generated from Fireflies transcript. [View full transcript]*
```

## CRM Field Updates

| Field | Update Logic |
|-------|--------------|
| Last Activity Date | Call date |
| Last Activity Type | "Call" |
| Next Step | Extracted from action items |
| Next Step Date | If mentioned/scheduled |
| Deal Stage | If stage change warranted |
| Contacts | Add newly mentioned stakeholders |
| Competitors | Tag if mentioned |

## Integration Points

- **Input**: Transcript webhooks (Fireflies, Gong, Otter)
- **Processing**: DataGen SDK for extraction and formatting
- **Output**: CRM notes (Salesforce, HubSpot, Attio, Pipedrive)
- **Notifications**: Slack to rep

## Success Metrics

- Processing time: < 5 min from call end to CRM note
- Field completion rate: 95%+ of required fields populated
- Rep satisfaction: "Notes are as good or better than I'd write"
- CRM data quality score improvement

## Implementation Notes

### Phase 1: Notes Only
Generate structured note, attach to CRM record. No field updates.

### Phase 2: Field Updates
Update next steps, activity dates, contact associations.

### Phase 3: Intelligent Staging
Suggest deal stage changes based on call content.

## MCP Requirements

- Fireflies/Gong MCP (transcript retrieval)
- CRM MCP (record lookup, note creation, field updates)
- Slack MCP (rep notifications)

## Comparison: vs Dynamic Sales Call Updates

| Aspect | Call Transcript to CRM | Dynamic Sales Call Updates |
|--------|------------------------|---------------------------|
| **Focus** | CRM note for single deal | Multiple doc updates |
| **Output** | 1 CRM note + field updates | Battlecards, ICP, objection lib |
| **Scope** | Deal-specific | Cross-deal intelligence |
| **Value** | Rep time savings | Organizational knowledge |

These agents complement each other - this one updates the deal record, the other updates team knowledge bases.
