# Step 2: Fetch Full Threads (Optional)

## Contract

| Field | Value |
|-------|-------|
| step_id | `02_fetch_threads` |
| Producer | `datagen_sdk` (Python script) |
| Output path | `/tmp/heyreach-summary-{date}/threads/{conversation_id}.json` |
| Output format | `json` |
| Downstream | Step 03 (compile_digest) |

## When to Run

This step is **optional**. Run it only if:
- Conversations from Step 1 have truncated message bodies
- You need full message content for deeper analysis
- Messages appear incomplete (e.g., body field is empty or very short)

If Step 1 conversations already contain full message bodies, skip to Step 3.

## Command

```bash
source .venv/bin/activate && python scripts/heyreach/fetch_threads.py --skip-existing
```

## What It Does

1. Reads `conversations.json` from Step 1
2. Filters to conversations with at least one CORRESPONDENT reply
3. Calls `get_chatroom` for each conversation to get full message thread
4. Saves each thread as `threads/{conversation_id}.json`

## Input

- `/tmp/heyreach-summary-{date}/conversations.json` (from Step 1)

## Output Schema

Per-thread file:
```json
{
  "messages": [
    { "sender": "ME|CORRESPONDENT", "body": "full message text", "sentAt": "ISO-8601" }
  ],
  "_campaign_id": 291852,
  "_campaign_name": "campaign-name"
}
```

## Validation

- Script prints message count per thread
- Check thread files exist in `/tmp/heyreach-summary-{date}/threads/`
- `--skip-existing` flag prevents re-fetching already-saved threads

## Error Recovery

- Individual thread fetch failures are logged but don't stop the pipeline
- Errors saved to `/tmp/heyreach-summary-{date}/thread_errors.json`
- Re-run with `--skip-existing` to retry only failed threads
