# Step 3: Compile Digest

## Contract

| Field | Value |
|-------|-------|
| step_id | `03_compile_digest` |
| Producer | `datagen_sdk` (Python script) |
| Output path | `/tmp/heyreach-summary-{date}/digest.json` |
| Output format | `json` |
| Downstream | Step 04 (AI analysis) |

## Command

```bash
source .venv/bin/activate && python scripts/heyreach/compile_digest.py --days 14
```

## What It Does

1. Reads `conversations.json` (and optionally `threads/` if available)
2. Filters to conversations with activity in the last N days
3. Extracts person info (name, headline, LinkedIn URL)
4. Detects meeting signals via keyword matching
5. Separates conversations with replies from outreach-only
6. Produces a compact, Claude-readable digest

## Input

- `/tmp/heyreach-summary-{date}/conversations.json` (required)
- `/tmp/heyreach-summary-{date}/threads/` (optional, used if available)

## Output Schema

```json
{
  "generated_at": "ISO-8601",
  "period": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
  "summary": {
    "total_conversations": 25,
    "with_replies": 8,
    "outreach_only": 17,
    "total_messages": 45,
    "total_replies": 12,
    "meeting_signals": 3,
    "campaigns_active": 3,
    "campaigns": ["campaign-a", "campaign-b"]
  },
  "conversations_with_replies": [
    {
      "person": { "name": "...", "headline": "...", "linkedin_url": "..." },
      "campaign_name": "...",
      "campaign_id": 123,
      "messages": [ { "sender": "ME|CORRESPONDENT", "body": "...", "date": "..." } ],
      "message_count": 4,
      "my_message_count": 2,
      "reply_count": 2,
      "last_activity": "ISO-8601",
      "has_meeting_signal": false
    }
  ],
  "outreach_only_count": 17
}
```

## Validation

- Script prints period, conversation count, reply count, meeting signals
- Verify `digest.json` exists and `conversations_with_replies` is populated
- Check that date filtering worked (no conversations outside the period)

## Error Recovery

- Re-run is safe (overwrites previous digest)
- If conversations.json is missing, run Step 1 first
