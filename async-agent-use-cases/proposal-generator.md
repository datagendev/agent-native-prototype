---
title: "Proposal Generator"
description: "Auto-generate customized proposals from deal context and templates"
category: "use-cases"
tags: ["async-agent", "sales", "proposals", "automation"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "medium"
based_on: ["[[claude-code-for-business]]"]
reference: ["https://www.francescatabor.com/articles/2025/11/15/claude-code-for-business-run-your-entire-company-with-ai-team"]
---

# Proposal Generator

Deal reaches proposal stage → gather context → generate customized proposal → notify rep.

## Problem

- Proposal creation takes 2-4 hours per deal
- Reps copy-paste from old proposals (inconsistent)
- Customization is superficial (find-replace company name)
- Delays in proposal delivery cost deals

## Solution

Async agent triggered by deal stage change that:
1. Gathers all deal context from CRM and calls
2. Pulls relevant case studies and proof points
3. Generates customized proposal
4. Delivers for rep review and send

## Trigger

```
CRM: Deal moves to "Proposal" stage
Manual: "Generate proposal for [Deal]"
Slack: "/proposal [Deal ID]"
```

## Pipeline

```
1. RECEIVE trigger
   - Deal ID, company, contacts
    ↓
2. GATHER deal context
   - CRM: deal details, history, contacts
   - Transcripts: pain points, requirements, objections
   - Emails: key discussion points
    ↓
3. SELECT relevant content
   - Case studies (similar industry, size, use case)
   - Testimonials
   - ROI data points
   - Product features to highlight
    ↓
4. CUSTOMIZE pricing
   - Pull pricing from CPQ or calculator
   - Apply any negotiated discounts
   - Structure options if discussed
    ↓
5. GENERATE proposal
   - Executive summary (personalized)
   - Problem/solution fit
   - Proposed solution
   - Relevant proof points
   - Investment and timeline
   - Next steps
    ↓
6. FORMAT and save
   - Apply brand template
   - Generate PDF
   - Save to deal record
    ↓
7. NOTIFY rep
   - Slack with preview
   - Edits needed flagged
   - One-click send option
```

## Context Gathering Schema

```yaml
deal_context:
  # From CRM
  deal:
    name: string
    amount: number
    stage: string
    close_date: date
    products: list[string]
    competitors: list[string]

  company:
    name: string
    industry: string
    size: string
    location: string

  contacts:
    - name: string
      title: string
      role: champion|economic_buyer|influencer

  # From calls/emails
  discovery:
    pain_points: list[string]
    requirements: list[string]
    success_criteria: list[string]
    objections_raised: list[string]
    timeline: string
    budget_discussed: string

  # From research
  company_context:
    recent_news: list[string]
    initiatives: list[string]
    challenges: list[string]
```

## Proposal Structure

```yaml
proposal_sections:
  cover:
    - Company logo + prospect logo
    - Proposal title
    - Date and validity

  executive_summary:
    - Personalized opening (reference their situation)
    - Key challenges identified
    - Proposed solution overview
    - Expected outcomes

  understanding:
    - Their current state (from discovery)
    - Challenges and pain points
    - Impact of status quo

  solution:
    - How we address each challenge
    - Product/service details
    - Implementation approach
    - Timeline

  proof:
    - Relevant case study (similar company)
    - ROI metrics
    - Testimonials
    - Customer logos

  investment:
    - Pricing options
    - What's included
    - Payment terms
    - Any negotiated terms

  next_steps:
    - Clear call to action
    - Process to move forward
    - Contact information
```

## Output: Generated Proposal

```markdown
# Proposal: [Company Name]

*Prepared for Sarah Chen, VP Revenue Operations*
*Prepared by Alex Kim, Account Executive*
*Date: January 27, 2025 | Valid through: February 27, 2025*

---

## Executive Summary

Following our conversations about TechCorp's rapid growth and the challenges of maintaining pipeline visibility at scale, we're excited to present a solution designed specifically for your needs.

**Your Situation**: With 40% sales team growth this quarter, your current manual reporting process can't keep pace. Pipeline meetings are delayed waiting for reports, and leadership lacks real-time visibility into forecast accuracy.

**Our Solution**: [Product] will automate your pipeline reporting, provide real-time dashboards, and integrate seamlessly with your existing Salesforce + Snowflake stack.

**Expected Outcome**: Based on similar implementations, we project:
- 15 hours/week saved on manual reporting
- 95% forecast accuracy (up from current 78%)
- Real-time pipeline visibility for leadership

---

## Understanding Your Needs

Based on our discovery call on January 15, we understand:

### Current Challenges
1. **Manual reporting burden** - Your ops team spends 15+ hours weekly building pipeline reports
2. **Delayed insights** - By the time reports are ready, data is 2-3 days old
3. **Forecast inaccuracy** - Current 78% accuracy creates planning challenges

### Requirements You Shared
- Salesforce integration (no manual exports)
- Real-time dashboards for leadership
- Historical trend analysis
- Role-based access control

### Success Criteria
- Reports generated automatically by Monday 6am
- Leadership dashboard updated in real-time
- Implementation complete before Q2

---

## Proposed Solution

[Detailed solution section...]

---

## Proof Points

### Case Study: DataCo (Similar Company)

**Situation**: 500-person SaaS company, 50-person sales team, similar manual reporting challenges.

**Results after 90 days**:
- Reporting time reduced from 20 hours/week to 2 hours
- Forecast accuracy improved from 75% to 94%
- Pipeline visibility enabled $2M in recovered at-risk deals

> "We can't imagine going back to manual reporting. The time savings alone paid for the investment in the first month."
> — *Jamie Rodriguez, VP Sales Ops, DataCo*

---

## Investment

### Recommended Package: Professional

| Component | Annual Investment |
|-----------|-------------------|
| Platform license (50 users) | $45,000 |
| Implementation | $8,000 |
| Training | Included |
| **Total Year 1** | **$53,000** |
| **Year 2+ renewal** | **$45,000** |

*Payment terms: Annual, Net 30*
*Includes: Unlimited support, quarterly business reviews*

---

## Next Steps

1. **Review this proposal** - Happy to walk through any questions
2. **Technical validation** - 30-min call with your IT team and our solutions engineer
3. **Contract review** - We'll send MSA and order form for legal review
4. **Kick-off** - Implementation begins within 5 business days of signature

**Target go-live**: March 15, 2025 (ahead of Q2)

---

*Questions? Contact Alex Kim: alex@company.com | (555) 123-4567*
```

## Integration Points

- **Input**: CRM deal data, call transcripts, email threads
- **Content**: Case study library, testimonial database, pricing calculator
- **Output**: PDF proposal, CRM attachment, Slack notification
- **Optional**: DocuSign integration for e-signature

## Success Metrics

- Time from trigger to draft: < 30 minutes
- Rep edit time: < 30 minutes (vs 2-4 hours from scratch)
- Proposal quality score (win rate comparison)
- Time from proposal to signature

## Implementation Notes

### Phase 1: Template + Context
Basic proposal from template with deal context inserted.

### Phase 2: Intelligent Content Selection
Auto-select case studies and proof points based on fit.

### Phase 3: Pricing Integration
Pull from CPQ, apply discounts, generate options automatically.

## MCP Requirements

- CRM MCP (deal data, contacts, history)
- Transcript MCP (Fireflies, Gong)
- Email MCP (conversation context)
- Storage MCP (case study library)
- Slack MCP (notifications)
