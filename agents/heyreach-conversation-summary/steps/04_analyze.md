# Step 4: AI Analysis

## Contract

| Field | Value |
|-------|-------|
| step_id | `04_analyze` |
| Producer | Claude (inline analysis) |
| Output path | `/tmp/heyreach-summary-{date}/analysis.md` |
| Output format | `md` |
| Downstream | Step 05 (generate report) |

## Process

1. Read `/tmp/heyreach-summary-{date}/digest.json`
2. Analyze conversation content across all conversations with replies
3. Write analysis to `/tmp/heyreach-summary-{date}/analysis.md`

## Analysis Framework

Your analysis should cover these sections:

### Conversation Themes
- Group conversations by topic/theme
- What subjects come up repeatedly?
- Which value props or features generate the most interest?

### Noteworthy Signals
- Who showed the strongest buying signals?
- Any explicit meeting requests or demo interest?
- Conversations with high engagement (3+ replies)
- Positive sentiment or enthusiasm indicators

### Objections & Patterns
- Common reasons for not engaging
- Pushback themes (timing, budget, already have solution, etc.)
- Ghost patterns (replied once then went silent)

### Today's Contact List
- **Who to message today**: A prioritized list of 3-7 people to contact right now
- For each person, provide:
  - **Name & company**
  - **Last message date** and who sent it (you or them)
  - **Why today**: What makes today the right time (e.g., promised follow-up window expired, they went quiet after high engagement, time-sensitive opportunity, meeting not yet booked)
  - **Suggested message**: A ready-to-send 2-3 sentence message tailored to where the conversation left off
- Prioritize: (1) people who replied but you haven't followed up, (2) promised follow-ups whose window is now, (3) high-engagement ghosts ripe for reactivation, (4) meeting logistics that need closing

### Recommended Actions
- **Priority follow-ups**: Name specific people to follow up with and why
- **Messaging adjustments**: What's resonating vs. what's falling flat
- **Campaign suggestions**: Which campaigns to iterate on, pause, or double down on

## Output Format

Write clean markdown. Be specific:
- Name people and companies
- Reference actual message content when relevant
- Quantify where possible ("3 of 8 respondents mentioned...")
- Keep it actionable - every insight should suggest a next step

## Validation

- analysis.md exists and is non-empty
- Contains all 5 sections (Themes, Noteworthy, Objections, Today's Contact List, Actions)
- References specific conversations from the digest
- Recommendations are concrete, not generic

## Error Recovery

- If digest.json is incomplete, note gaps in analysis
- Re-read digest.json and regenerate if analysis needs improvement
