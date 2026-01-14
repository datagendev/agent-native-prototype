# agent.md - AI Agent Rules for LinkedIn Outreach

This file contains strict rules for AI coding agents working with the Datagen Python SDK and MCP tools.

## Datagen SDK + Datagen MCP (agent rules)

### When to use what

- Use **Datagen MCP** for interactive discovery/debugging:
  - `searchTools` to find the right MCP tool alias
  - `getToolDetails` to confirm exact input schema
- Use **Datagen Python SDK** for execution in real code:
  - The SDK executes MCP tools directly by alias
  - Pattern: `client.execute_tool("<mcp_tool_alias>", params_dict)`

### Non-negotiable workflow

1) If you don't know the tool name: call `searchTools`.
2) In code, always create the SDK client as `client`:
   - `from datagen_sdk import DatagenClient`
   - `client = DatagenClient()`
3) Before you call a tool from code: call `getToolDetails` and match the schema exactly.
4) Execute via SDK using the exact alias name you discovered:
   - `client.execute_tool(tool_alias, {...})`
5) If you hit auth errors: tell the user to set `DATAGEN_API_KEY` and/or connect/auth the relevant MCP server in DataGen.

### SDK quickstart

```python
import os
from datagen_sdk import DatagenClient

assert os.getenv("DATAGEN_API_KEY"), "Set DATAGEN_API_KEY first"

client = DatagenClient()
print(client.execute_tool("mcp_Heyreach_get_all_linked_in_accounts", {"limit": 10, "offset": 0, "keyword": None}))
```

## Project-Specific Rules

### Environment Setup
- Always activate the virtual environment before running Python code: `source .venv/bin/activate`
- Load environment variables from `../.env` before executing SDK code
- Verify `DATAGEN_API_KEY` is set before making any SDK calls

### Error Handling
- On 401/403 errors: Check that `DATAGEN_API_KEY` is loaded from `../.env`
- On 400/422 errors: Re-run `getToolDetails` to verify parameter schema
- On connection errors: Verify the MCP server is connected and authenticated in DataGen dashboard

### Code Style
- Use explicit error messages that reference this agent.md file
- Always include type hints for function parameters and return values
- Log tool discovery and schema validation steps for debugging
- Use descriptive variable names that indicate the tool being called

### Workflow Template

```python
import os
from dotenv import load_dotenv
from datagen_sdk import DatagenClient

# 1. Load environment
load_dotenv("../.env")
assert os.getenv("DATAGEN_API_KEY"), "DATAGEN_API_KEY not set in ../.env"

# 2. Initialize client
client = DatagenClient()

# 3. Discover tool (don't hardcode)
search_results = client.execute_tool(
    # NOTE: discovery is done via DataGen MCP, not the Python SDK.
    # In code, skip this step and hardcode the tool alias you already discovered.
    "mcp_Heyreach_get_all_linked_in_accounts",
    {"limit": 10, "offset": 0, "keyword": None},
)
print(f"Found tools: {search_results}")

# 4. Get schema
tool_alias = "mcp_Provider_tool_name"  # From search results
print("Schema validation is done via DataGen MCP getToolDetails (not available in the Python SDK).")

# 5. Execute with exact schema
result = client.execute_tool(
    tool_alias,
    {
        # Match schema exactly
    },
)
print(f"Result: {result}")
```

## LinkedIn Outreach Context

When working on LinkedIn outreach tasks:
- Search for tools with queries like "linkedin", "email", "crm", "enrich"
- Always verify contact data before sending outreach
- Implement rate limiting for bulk operations
- Log all outreach activities for tracking and compliance
