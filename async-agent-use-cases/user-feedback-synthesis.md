---
title: "User Feedback Synthesis"
description: "Auto-analyze survey responses, extract themes, generate insights report"
category: "use-cases"
tags: ["async-agent", "product", "research", "feedback"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "medium"
based_on: ["[[product-think-subagents]]"]
reference: ["https://www.producttalk.org/how-to-use-claude-code-features/"]
---

# User Feedback Synthesis

Analyze hundreds of survey responses, extract themes, generate actionable insights.

## Problem

- Survey data sits unanalyzed for weeks
- Manual coding of open-ended responses is tedious
- Themes are subjective, inconsistent across analysts
- Leadership wants insights, not raw data

## Solution

Async agent that:
1. Ingests feedback data (CSV, form responses)
2. Codes responses into themes
3. Quantifies sentiment and priority
4. Generates executive insights report

## Trigger

```
Scheduled: Weekly survey batch processing
Webhook: Survey closes, export ready
Manual: "Analyze this feedback file"
```

## Pipeline

```
1. INGEST feedback data
   - CSV, JSON, or form export
   - Clean and normalize text
    ↓
2. INITIAL SCAN
   - Sample 50-100 responses
   - Identify emerging themes
   - Create theme taxonomy
    ↓
3. BATCH PROCESS all responses
   - Assign each to 1-3 themes
   - Score sentiment (-1 to +1)
   - Extract representative quotes
    ↓
4. AGGREGATE results
   - Theme frequency counts
   - Sentiment distribution
   - Segment breakdowns (if metadata available)
    ↓
5. SYNTHESIZE insights
   - Top themes by volume
   - Sentiment drivers
   - Emerging vs. recurring issues
   - Segment differences
    ↓
6. GENERATE report
   - Executive summary
   - Theme deep-dives
   - Recommended actions
   - Raw data appendix
    ↓
7. DISTRIBUTE
   - Email to stakeholders
   - Save to insights library
   - Update product dashboard
```

## Theme Taxonomy

```yaml
theme_categories:
  product:
    - UI/UX
    - Performance
    - Features - Existing
    - Features - Requested
    - Reliability/Bugs
    - Integrations

  experience:
    - Onboarding
    - Documentation
    - Support
    - Pricing/Value

  sentiment:
    - Praise
    - Complaint
    - Suggestion
    - Question

  urgency:
    - Blocker (can't use product)
    - Friction (slows them down)
    - Nice-to-have (would improve)
    - FYI (no action needed)
```

## Response Coding Schema

```yaml
coded_response:
  id: string
  original_text: string

  themes:
    primary: string
    secondary: list[string]

  sentiment:
    score: -1.0 to 1.0
    label: positive|neutral|negative

  urgency: blocker|friction|nice_to_have|fyi

  extracted_quote: string  # Most representative excerpt

  metadata:
    respondent_segment: string
    date: date
    source: survey_name
```

## Output: Feedback Insights Report

```markdown
# Feedback Synthesis: [Survey Name]

**Period**: Jan 1-15, 2025 | **Responses**: 487
**Overall Sentiment**: 0.42 (Moderately Positive)

---

## Executive Summary

Users are generally satisfied with core functionality but frustrated by **performance issues** (mentioned in 34% of responses) and requesting **better integrations** (28%). New onboarding flow received positive feedback (+0.7 sentiment).

### Top 3 Action Items
1. **Address dashboard loading speed** - 89 mentions, -0.6 sentiment
2. **Add Salesforce integration** - 72 mentions, neutral sentiment, high request frequency
3. **Improve error messages** - 45 mentions, -0.4 sentiment

---

## Theme Analysis

### Performance (34% of responses)
**Sentiment**: -0.3 | **Urgency**: High

**Key Issues**:
- Dashboard takes 10+ seconds to load (52 mentions)
- Report exports timing out (31 mentions)
- Mobile app crashes (6 mentions)

**Representative Quotes**:
> "Love the product but I spend half my day waiting for pages to load."
> "Export feature worked great until our data grew. Now it times out every time."

**Recommended Action**: Performance audit of dashboard and export functions

---

### Feature Requests (28% of responses)
**Sentiment**: +0.2 | **Urgency**: Medium

**Top Requests**:
| Feature | Mentions | Sentiment |
|---------|----------|-----------|
| Salesforce integration | 72 | +0.3 |
| Custom dashboards | 48 | +0.4 |
| API access | 35 | +0.2 |
| Mobile improvements | 29 | -0.1 |

---

### Onboarding (15% of responses)
**Sentiment**: +0.7 | **Urgency**: Low (positive feedback)

Users praising new onboarding flow launched Dec 15:
> "Setup took 10 minutes instead of the hour I expected."
> "Tutorial videos were actually helpful!"

---

## Segment Comparison

| Segment | Response Count | Avg Sentiment | Top Theme |
|---------|---------------|---------------|-----------|
| Enterprise | 124 | +0.5 | Integrations |
| Mid-Market | 203 | +0.4 | Performance |
| SMB | 160 | +0.3 | Pricing |

---

## Appendix

### Theme Distribution
[Bar chart data]

### Sentiment Over Time
[Trend data if longitudinal]

### Full Theme Breakdown
[Detailed counts]

---

*Generated: {timestamp} | Responses analyzed: 487 | Processing time: 8 min*
```

## Integration Points

- **Input**: Survey platforms (Typeform, SurveyMonkey, Google Forms), CSV uploads
- **Processing**: DataGen SDK batch analysis
- **Output**: Markdown report, email, dashboard update
- **Optional**: Jira/Linear ticket creation for action items

## Success Metrics

- Processing time per 100 responses
- Theme consistency (inter-rater reliability proxy)
- Actionability: % of insights leading to product changes
- Stakeholder satisfaction with reports

## Implementation Notes

### Phase 1: Theme Extraction
Basic theme coding and frequency counts. Manual theme taxonomy.

### Phase 2: Sentiment + Segmentation
Add sentiment analysis and segment breakdowns.

### Phase 3: Longitudinal Tracking
Compare themes and sentiment over time. Trend detection.
