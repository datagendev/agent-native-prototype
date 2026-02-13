# Step 1: Fetch Recent Conversations

## Contract

| Field | Value |
|-------|-------|
| step_id | `01_fetch_conversations` |
| Producer | `datagen_sdk` (Python script) |
| Output path | `/tmp/heyreach-summary-{date}/conversations.json` |
| Output format | `json` |
| Downstream | Step 02 (fetch_threads) or Step 03 (compile_digest) |

## Command

```bash
source .venv/bin/activate && python scripts/heyreach/fetch_recent_conversations.py --days 14
```

## What It Does

1. Fetches all campaigns with status IN_PROGRESS, PAUSED, or FINISHED
2. For each campaign, fetches conversations with pagination (100 per page)
3. Tags each conversation with `_campaign_id` and `_campaign_name`
4. Saves combined output to `conversations.json`

## Input

None (fetches from HeyReach API directly).

## Output Schema

```json
[
  {
    "conversationId": "string",
    "accountId": 123,
    "messages": [
      { "sender": "ME|CORRESPONDENT", "body": "string", "sentAt": "ISO-8601" }
    ],
    "_campaign_id": 291852,
    "_campaign_name": "campaign-name"
  }
]
```

## Validation

- Script prints conversation count per campaign
- Script prints total conversations and count with replies
- Check for errors in output (non-zero exit code)
- Verify `conversations.json` exists and is non-empty

## Error Recovery

- If DATAGEN_API_KEY is missing, script exits with error
- If a campaign fetch fails, error is logged and other campaigns continue
- Errors saved to `/tmp/heyreach-summary-{date}/errors.json`
- Re-run is safe (overwrites previous output)
