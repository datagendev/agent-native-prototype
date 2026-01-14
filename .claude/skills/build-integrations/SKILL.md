---
name: build-integrations
description: Build new DataGen integrations by exploring capabilities, suggesting options, and creating reusable primitives
---

# Build Integrations

Create new DataGen integrations following the agent-native approach. This skill discovers available tools, suggests implementation options, and generates reusable primitives.

## Workflow

### Step 1: Understand the Request

Extract from the user's message:
- **Domain**: What service/API they want to integrate (e.g., "HubSpot", "Slack", "Apollo")
- **Purpose**: What they want to accomplish (e.g., "enrich contacts", "send notifications", "sync data")
- **Input/Output**: What data goes in and comes out

### Step 2: Explore DataGen Capabilities

Use the Task tool with `subagent_type: Explore` to search for existing DataGen tools:

```
Prompt: "Search for DataGen MCP tools related to [DOMAIN].
Look for:
1. Existing MCP tools (mcp_*) that handle this domain
2. Tool schemas and required parameters
3. Example usage patterns

Use searchTools and getToolDetails from DataGen MCP to discover available tools."
```

**What to look for:**
- `mcp_<Provider>_*` tools (e.g., `mcp_HubSpot_*`, `mcp_Slack_*`)
- Tool input/output schemas
- Required authentication or secrets

### Step 3: Search for API Alternatives (if no DataGen tools found)

If Step 2 finds no suitable tools, search for external APIs:

```
Use WebSearch to find:
1. "[DOMAIN] API documentation"
2. "[DOMAIN] REST API endpoints"
3. "[DOMAIN] API authentication"
```

**Gather:**
- API base URL
- Authentication method (API key, OAuth, etc.)
- Relevant endpoints
- Rate limits

### Step 4: Present Options to User

Use AskUserQuestion to let user choose implementation approach:

**Question 1: Data Source**
- Header: "Source"
- Question: "Which data source should the integration use?"
- Options based on Step 2/3 findings:
  - DataGen MCP tool (if available)
  - Direct API call (if API found)
  - Web scraping (fallback)
  - Other (custom)

**Question 2: Output Columns**
- Header: "Output"
- Question: "What data should this integration return?"
- multiSelect: true
- Options: List relevant fields discovered in Step 2/3

**Question 3: Error Handling**
- Header: "Errors"
- Question: "How should the integration handle errors?"
- Options:
  - "Return empty + error message (Recommended)" - Graceful degradation
  - "Raise exception" - Fail fast
  - "Return partial data" - Best effort

### Step 5: Generate the Integration

Create a new integration file following the established pattern:

**File location**: `scripts/integrations/<domain>_<purpose>.py`

**Template:**
```python
"""
Integration: <Domain> <Purpose>

<Description of what this integration does>
"""

from .base import Integration


class <ClassName>(Integration):
    """<One-line description>."""

    input_cols = ["<required_input_1>", "<required_input_2>"]
    output_cols = ["<output_1>", "<output_2>", "<output_3>"]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        """
        <Describe the enrichment logic>

        Returns:
            (enriched_fields, error): Dict with output columns, empty string on success
        """
        # Option A: Use DataGen MCP tool
        result = self.client.execute_tool(
            "mcp_<Provider>_<tool_name>",
            {"param": row["<input_col>"]}
        )

        # Option B: Direct API call (if no MCP tool)
        # import httpx
        # response = httpx.get(f"https://api.example.com/...", headers={"Authorization": f"Bearer {API_KEY}"})
        # result = response.json()

        # Extract and return relevant fields
        return {
            "<output_1>": result.get("<field_1>", ""),
            "<output_2>": result.get("<field_2>", ""),
        }, ""


# Backward compatibility: Module-level API
_instance = <ClassName>()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
```

### Step 6: Register the Integration

Update `scripts/integrations/__init__.py` to include the new integration:

```python
from .<filename> import <ClassName>
```

### Step 7: Test the Integration

Run a quick test to verify it works:

```bash
source .venv/bin/activate && python -c "
from scripts.integrations.<filename> import <ClassName>
integration = <ClassName>()
result, err = integration.enrich({'<input_col>': '<test_value>'})
print(f'Result: {result}')
print(f'Error: {err}')
"
```

### Step 8: Report Results

Tell the user:
- File created: `scripts/integrations/<filename>.py`
- Class name: `<ClassName>`
- Input columns: `[...]`
- Output columns: `[...]`
- How to use in enrichment workflows

## Agent-Native Principles

Follow these principles when creating integrations:

1. **Simple**: One integration = one responsibility
2. **Reusable**: Generic enough to work with any lead table
3. **Composable**: Can be combined with other integrations in workflows
4. **Error-first**: Always return `(result, error)` tuple
5. **Stateless**: No side effects, same input = same output
6. **Documented**: Clear docstrings and type hints

## Example: Creating a HubSpot Contact Integration

**User**: "I want to enrich leads with HubSpot contact data"

**Step 2 - Explore**:
```
Task agent finds: mcp_HubSpot_get_contact, mcp_HubSpot_search_contacts
Tool schema: requires email or contact_id
```

**Step 4 - Ask User**:
- Source: "DataGen MCP (mcp_HubSpot_get_contact)"
- Output: ["hubspot_id", "lifecycle_stage", "last_activity_date"]
- Errors: "Return empty + error message"

**Step 5 - Generate**:
```python
# scripts/integrations/hubspot_contact.py
"""
Integration: HubSpot Contact Enrichment

Enriches leads with HubSpot CRM contact data.
"""

from .base import Integration


class HubSpotContact(Integration):
    """Get HubSpot contact data by email."""

    input_cols = ["email"]
    output_cols = ["hubspot_id", "lifecycle_stage", "last_activity_date"]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        result = self.client.execute_tool(
            "mcp_HubSpot_get_contact",
            {"email": row["email"]}
        )

        if not result or "error" in result:
            return {}, f"HubSpot contact not found: {result.get('error', 'unknown')}"

        return {
            "hubspot_id": result.get("id", ""),
            "lifecycle_stage": result.get("lifecycle_stage", ""),
            "last_activity_date": result.get("last_activity_date", "")
        }, ""


_instance = HubSpotContact()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
```

## Directory Structure

```
scripts/integrations/
├── __init__.py           # Registry of all integrations
├── base.py               # Base Integration class
├── linkedin_profile.py   # LinkedIn profile enrichment
├── linkedin_post_activity.py
├── heyreach_campaigns.py
├── hubspot_contact.py    # NEW: Created by this skill
└── ...
```

## Error Handling

If any step fails:
- **No DataGen tools + No API**: Ask user if they want to use web scraping or provide API details
- **API key missing**: Instruct user to add secret via DataGen dashboard
- **Test fails**: Show error and suggest fixes

## Notes

- Always use the Integration base class for consistency
- Keep integrations focused - one data source per integration
- Use DataGen MCP tools when available (more reliable than direct API calls)
- Test with real data before marking complete
