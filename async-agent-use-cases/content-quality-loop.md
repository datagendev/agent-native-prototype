---
title: "Content Quality Loop"
description: "Auto-generate content, score against rubric, iterate until quality threshold met"
category: "use-cases"
tags: ["async-agent", "content", "marketing", "quality-control"]
created: 2025-01-27
updated: 2025-01-27
status: "draft"
priority: "high"
based_on: ["[[omarsar-custom-workflows]]"]
reference: ["https://www.linkedin.com/posts/omarsar_claude-code-is-more-than-a-coding-agent-activity-7355365816118177792-e0sX"]
---

# Content Quality Loop

Generate content, evaluate against criteria, iterate until quality threshold met.

## Problem

- Content quality inconsistent without review
- Human review creates bottleneck
- No systematic way to enforce brand/quality standards
- "Good enough" varies by person

## Solution

Two-agent async system:
1. **Generator Agent** - Creates content from inputs
2. **Evaluator Agent** - Scores against rubric, provides feedback
3. Loop until score threshold met (e.g., 90+)

## Trigger

```
Manual: "Generate LinkedIn post about [topic]"
Scheduled: Daily content batch for queue
Webhook: New content brief submitted
```

## Pipeline

```
1. RECEIVE content brief
   - Topic, audience, platform, tone
   - Reference materials (optional)
    ↓
2. GENERATOR creates first draft
   - Platform-appropriate format
   - Brand voice applied
    ↓
3. EVALUATOR scores against rubric
   - Clarity: 0-100
   - Engagement: 0-100
   - Brand alignment: 0-100
   - Platform fit: 0-100
   - Overall: weighted average
    ↓
4. IF score < threshold (90):
   - Evaluator provides specific feedback
   - Generator revises based on feedback
   - Return to step 3
   - Max iterations: 3-5
    ↓
5. OUTPUT final content
   - Save to content queue
   - Include score breakdown
   - Flag if max iterations hit without threshold
```

## Evaluation Rubric

```yaml
rubric:
  clarity:
    weight: 25
    criteria:
      - Single clear message
      - No jargon without explanation
      - Scannable structure

  engagement:
    weight: 30
    criteria:
      - Strong hook in first line
      - Creates curiosity or value
      - Clear call-to-action
      - Platform-native format

  brand_alignment:
    weight: 25
    criteria:
      - Matches tone guidelines
      - Consistent terminology
      - Reflects company values

  platform_fit:
    weight: 20
    criteria:
      - Correct length for platform
      - Appropriate hashtags/mentions
      - Visual-friendly formatting
```

## Content Brief Schema

```yaml
brief:
  topic: string
  platform: linkedin|twitter|blog|email
  audience: string
  tone: professional|casual|technical|inspirational
  key_message: string
  cta: string  # Desired action
  references: list[url]  # Source materials
  constraints:
    word_count: {min: int, max: int}
    must_include: list[string]
    must_avoid: list[string]
```

## Output: Content with Score

```markdown
# LinkedIn Post: [Topic]

**Score**: 92/100 | **Iterations**: 2

## Final Content

[Generated post content here]

---

## Score Breakdown
| Criteria | Score | Notes |
|----------|-------|-------|
| Clarity | 95 | Single clear message |
| Engagement | 90 | Strong hook, clear CTA |
| Brand | 92 | Matches tone guidelines |
| Platform | 91 | Good length, scannable |

## Iteration History
1. Draft 1: 78/100 - "Hook too generic, CTA unclear"
2. Draft 2: 92/100 - Passed threshold

## Metadata
- Generated: {timestamp}
- Brief ID: {id}
- Ready for: Human review → Publish queue
```

## Platform-Specific Rules

| Platform | Length | Format | Tone |
|----------|--------|--------|------|
| LinkedIn | 200-300 words | Paragraphs, line breaks | Professional storytelling |
| Twitter/X | 280 chars | Punchy, thread-ready | Concise, provocative |
| Blog | 800-1500 words | Headers, bullets | Educational |
| Email | 150-250 words | Personal, scannable | Direct, value-first |

## Integration Points

- **Input**: Content briefs (form, Slack, Notion)
- **Processing**: Two-agent loop with DataGen SDK
- **Output**: Content queue (Notion, Buffer, spreadsheet)
- **Review**: Human approves before publish

## Success Metrics

- First-draft acceptance rate (no iterations needed)
- Average iterations to threshold
- Human edit rate after approval
- Content performance (engagement, clicks)

## Implementation Notes

### Phase 1: Single Platform
LinkedIn posts only. Validate rubric and iteration logic.

### Phase 2: Multi-Platform
Expand to Twitter, blog, email. Platform-specific rubrics.

### Phase 3: Learning Loop
Track which content performs best, refine rubric weights.

## Token Efficiency Warning

From Omar Saravia's experience: "The system likes to use a lot of tokens and perform unnecessary tasks."

Mitigations:
- Set max iterations (3-5)
- Keep rubric concise
- Use slash commands to enforce workflow structure
- Don't let evaluator re-generate, only score and feedback
