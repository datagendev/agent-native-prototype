# HeyReach Conversation Summary - Orchestration Guide

## Purpose

Summarize HeyReach outreach conversations from the last 2 weeks:
- **Who** you've been talking to (people, companies, roles)
- **Themes** across conversations (what topics resonate, common objections)
- **Noteworthy** signals (meeting interest, high engagement, positive sentiment)

## Pipeline Overview

```
[1] fetch_recent_conversations.py  -->  conversations.json
[2] fetch_threads.py (optional)    -->  threads/{id}.json
[3] compile_digest.py              -->  digest.json
[4] Read digest.json, write        -->  analysis.md
[5] generate_conversation_summary  -->  report.html
[6] Gmail MCP send                 -->  email delivered
```

All artifacts persist to `/tmp/heyreach-summary-{YYYY-MM-DD}/`.
Any step can resume from persisted artifacts.

## Execution Steps

### Step 1: Fetch Conversations

```bash
source .venv/bin/activate && python scripts/heyreach/fetch_recent_conversations.py --days 14
```

**Produces:** `/tmp/heyreach-summary-{date}/conversations.json`
**Validation:** Check script output for conversation count and error summary.

See: `steps/01_fetch_conversations.md`

### Step 2: Fetch Threads (Optional)

Run only if Step 1 conversations have truncated or missing message bodies.

```bash
source .venv/bin/activate && python scripts/heyreach/fetch_threads.py --skip-existing
```

**Produces:** `/tmp/heyreach-summary-{date}/threads/{id}.json`

See: `steps/02_fetch_threads.md`

### Step 3: Compile Digest

```bash
source .venv/bin/activate && python scripts/heyreach/compile_digest.py --days 14
```

**Produces:** `/tmp/heyreach-summary-{date}/digest.json`
**Validation:** Check conversation count, reply count, meeting signals.

See: `steps/03_compile_digest.md`

### Step 4: AI Analysis

Read `digest.json` and write analysis to `/tmp/heyreach-summary-{date}/analysis.md`.

**Your analysis should cover:**

1. **Conversation Themes** - What topics keep coming up across conversations? Group by theme.
2. **Noteworthy Signals** - Who showed the strongest interest? Any meeting requests, positive responses, or high engagement?
3. **Objections & Concerns** - What pushback patterns emerged? Common reasons for not engaging?
4. **Today's Contact List** - A prioritized list of 3-7 people to message today with ready-to-send messages. Based on: unanswered replies, expired follow-up windows, high-engagement ghosts, and open meeting logistics.
5. **Recommended Actions** - Specific follow-up actions: who to prioritize, what messaging to adjust, which campaigns to iterate on.

**Format:** Write clean markdown with headers. Be specific - name people, reference actual message content. Prioritize actionable insights over generic observations.

See: `steps/04_analyze.md`

### Step 5: Generate HTML Report

```bash
source .venv/bin/activate && python scripts/heyreach/generate_conversation_summary.py
```

**Produces:** `reports/heyreach/conversation-summary-{date}.html`
**Validation:** Open the HTML file and verify sections render correctly.

See: `steps/05_generate_report.md`

### Step 6: Email Report

Send the HTML report via Gmail MCP:

```
Tool: mcp_Gmail_Yusheng_gmail_send_email
Parameters:
  to: (ask user for recipient)
  subject: "HeyReach Conversation Summary - {start_date} to {end_date}"
  body: (read the HTML file content)
```

See: `steps/06_email.md`

## Error Recovery

| Failure Point | Recovery |
|--------------|----------|
| Step 1 fails | Check DATAGEN_API_KEY, retry. Partial results saved to conversations.json |
| Step 2 fails | Skip - Step 3 works without threads |
| Step 3 fails | Re-run with existing conversations.json |
| Step 4 fails | Re-read digest.json, regenerate analysis |
| Step 5 fails | Check template path, re-run with --template flag |
| Step 6 fails | Read HTML file, send manually via Gmail MCP |

## Configuration

| Parameter | Default | Override |
|-----------|---------|----------|
| Look-back period | 14 days | `--days N` on scripts |
| Output directory | `/tmp/heyreach-summary-{date}` | `--output-dir` on Step 1 |
| HTML template | `agents/heyreach-conversation-summary/templates/conversation-summary.html` | `--template` on Step 5 |
| Report output | `reports/heyreach/conversation-summary-{date}.html` | `--output` on Step 5 |
