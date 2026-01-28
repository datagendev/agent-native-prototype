---
title: "Lead Enrichment and Routing"
description: "New lead arrives, auto-enrich with data, score, route to right rep, notify"
category: "use-cases"
tags: ["async-agent", "sales", "leads", "crm", "routing"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "high"
based_on: ["[[claude-code-for-business]]"]
reference: ["https://www.francescatabor.com/articles/2025/11/15/claude-code-for-business-run-your-entire-company-with-ai-team"]
---

# Lead Enrichment and Routing

New lead → enrich → score → route → notify. Under 60 seconds.

## Problem

- Leads sit unworked while SDRs manually research
- Routing rules are basic (round-robin misses context)
- Enrichment data scattered across tools
- Hot leads get cold waiting for assignment

## Solution

Async agent triggered by new lead that:
1. Enriches with company and contact data
2. Scores based on ICP fit
3. Routes to best-fit rep
4. Notifies with full context

## Trigger

```
Webhook: Form submission, demo request, trial signup
CRM: New lead created
Integration: Lead from partner, event, or import
```

## Pipeline

```
1. RECEIVE new lead
   - Email, company (if provided)
   - Source, UTM parameters
    ↓
2. ENRICH company data
   - Company size, industry, location
   - Funding, revenue signals
   - Tech stack (if detectable)
   - Recent news
    ↓
3. ENRICH contact data
   - Title, seniority
   - LinkedIn profile
   - Previous companies
    ↓
4. SCORE lead
   - ICP fit score (0-100)
   - Intent signals
   - Timing indicators
    ↓
5. ROUTE to rep
   - Match by segment, territory, capacity
   - Consider rep expertise
    ↓
6. UPDATE CRM
   - All enriched fields
   - Score and routing rationale
   - Suggested talking points
    ↓
7. NOTIFY rep
   - Slack DM with lead summary
   - Why they got this lead
   - Suggested first touch
```

## Enrichment Schema

```yaml
enriched_lead:
  # Original data
  original:
    email: string
    company_provided: string
    source: string
    form_data: object

  # Company enrichment
  company:
    name: string
    domain: string
    industry: string
    size: 1-10|11-50|51-200|201-500|501-1000|1000+
    location:
      city: string
      country: string
    funding:
      total: number
      last_round: string
      last_round_date: date
    tech_stack: list[string]
    recent_news: list[{headline, date, url}]

  # Contact enrichment
  contact:
    name: string
    title: string
    seniority: c_level|vp|director|manager|ic
    department: string
    linkedin_url: string
    tenure_months: int

  # Scoring
  score:
    total: 0-100
    breakdown:
      company_fit: 0-40
      contact_fit: 0-30
      intent_signals: 0-20
      timing: 0-10
    tier: hot|warm|nurture

  # Routing
  routing:
    assigned_to: string
    reason: string
    territory: string
    segment: enterprise|mid_market|smb
```

## Scoring Rubric

```yaml
scoring:
  company_fit:  # Max 40 points
    industry_match: 0-15
    size_match: 0-15
    location_match: 0-10

  contact_fit:  # Max 30 points
    seniority_match: 0-15
    department_match: 0-10
    title_keywords: 0-5

  intent_signals:  # Max 20 points
    demo_request: +15
    pricing_page: +10
    multiple_visits: +5
    content_download: +3

  timing:  # Max 10 points
    recent_funding: +5
    hiring_signal: +3
    tech_change: +2
```

## Routing Logic

```yaml
routing_rules:
  # Segment assignment
  segment:
    - if: company.size >= 500
      then: enterprise
    - if: company.size >= 50
      then: mid_market
    - else: smb

  # Rep assignment
  assignment:
    - if: segment == enterprise AND territory == west
      then: alex@company.com
    - if: segment == enterprise AND territory == east
      then: jordan@company.com
    - if: segment == mid_market
      then: round_robin(mm_team)
    - else: round_robin(smb_team)

  # Capacity check
  capacity:
    - if: rep.open_leads > 50
      then: next_rep_in_queue
```

## Output: Rep Notification

```markdown
## New Lead: Sarah Chen @ TechCorp

**Score**: 87/100 (Hot) | **Segment**: Enterprise | **Source**: Demo Request

### Why You
- Your territory (West Coast)
- You closed similar company (DataCo) last quarter
- You have capacity (38 open leads)

### Company Snapshot
- **TechCorp** | SaaS | 850 employees | San Francisco
- **Funding**: $45M Series C (6 months ago)
- **Tech Stack**: Salesforce, Snowflake, dbt
- **Recent News**: "TechCorp expands sales team by 40%"

### Contact
- **Sarah Chen** | VP Revenue Operations
- 2 years at TechCorp, previously at DataCo
- [LinkedIn](url)

### Intent Signals
- Visited pricing page 3x this week
- Downloaded "ROI Calculator" guide
- Demo request: "Looking to automate pipeline reporting"

### Suggested First Touch

> Hi Sarah,
>
> Saw your demo request about pipeline reporting automation. With TechCorp's
> growth (congrats on the expansion!), I imagine keeping pipeline visibility
> gets harder as the team scales.
>
> We helped DataCo solve a similar challenge - happy to share what worked
> for them. Would Thursday work for a quick call?

---

*[View in CRM](link) | [Skip this lead](action) | [Reassign](action)*
```

## Integration Points

- **Input**: Form webhooks, CRM triggers
- **Enrichment**: Clearbit, Apollo, LinkedIn, web scraping
- **Output**: CRM update, Slack notification
- **Optional**: Auto-sequence enrollment for warm leads

## Success Metrics

- Time from lead creation to rep notification: < 60 seconds
- Enrichment completion rate: 90%+ of fields populated
- Routing accuracy: Rep accepts 95%+ of assigned leads
- Speed to first touch improvement

## Implementation Notes

### Phase 1: Enrich + Notify
Basic enrichment, simple routing, Slack notification.

### Phase 2: Smart Routing
Segment-based routing, capacity balancing, territory matching.

### Phase 3: Personalized Outreach
Generate first-touch suggestions based on enriched context.

## MCP Requirements

- CRM MCP (Salesforce, HubSpot, Attio)
- Enrichment MCP (Clearbit, Apollo)
- LinkedIn MCP (profile data)
- Slack MCP (notifications)
