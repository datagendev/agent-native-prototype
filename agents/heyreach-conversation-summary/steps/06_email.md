# Step 6: Email Report

## Contract

| Field | Value |
|-------|-------|
| step_id | `06_email` |
| Producer | MCP tool call |
| Output path | N/A (side effect - email sent) |
| Output format | N/A |
| Downstream | None (terminal step) |

## Process

1. Read the markdown analysis from `/tmp/heyreach-summary-{date}/analysis.md`
2. Default recipient: yusheng.kuo@datagen.dev
3. Send via Gmail MCP tool using local DataGen SDK script (to handle large body)

## Send Script

```bash
source .venv/bin/activate && python3 -c "
from datagen_sdk import DatagenClient
from pathlib import Path

client = DatagenClient()
md_content = Path('/tmp/heyreach-summary-{date}/analysis.md').read_text()

result = client.execute_tool('mcp_Gmail_Yusheng_gmail_send_email', {
    'to': ['yusheng.kuo@datagen.dev'],
    'subject': 'HeyReach Conversation Summary - {start_date} to {end_date}',
    'body': md_content
})
print(result)
"
```

## Validation

- Confirm email was sent (check tool response for success status)

## Error Recovery

- If Gmail MCP fails, save file path and suggest manual send
- Retry once if transient error

## Notes

- Send plain markdown (not HTML) -- simpler, more readable in email
- The `to` parameter must be an array: `["email@example.com"]`
- Use local SDK script (not DataGen sandbox) since it needs to read local files
- Default recipient: yusheng.kuo@datagen.dev
- Subject should include the date range from the digest period
