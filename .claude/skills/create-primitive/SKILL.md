---
name: create-primitive
description: Create enrichment primitives with structured frontmatter following tool selection best practices
---

# Skill: Create Primitive

Create a new enrichment primitive following tool selection best practices with structured frontmatter documentation.

## When to Use

- User wants to create a new primitive (atomic enrichment capability)
- Need to wrap an MCP tool as a primitive
- Building reusable operations for enrichment workflows

## Usage

```bash
# Interactive mode - asks for all details
/create-primitive

# With primitive specification
/create-primitive --name firecrawl_scrape --description "Scrape web page content using Firecrawl"

# With MCP tool to wrap
/create-primitive --name firecrawl_scrape --mcp-tool mcp_Firecrawl_firecrawl_scrape
```

## Parameters

- `--name` (optional): Primitive name in snake_case (e.g., `firecrawl_scrape`, `email_finder`)
- `--description` (optional): One-line description of what the primitive does
- `--mcp-tool` (optional): MCP tool name to wrap (e.g., `mcp_Firecrawl_firecrawl_scrape`)

---

## Step 1: Gather Primitive Specification

If parameters not provided, use `AskUserQuestion` to gather:
1. **Primitive name**: Snake_case identifier (e.g., `firecrawl_scrape`, `email_finder`)
2. **Short description**: One-liner describing what it does
3. **Capability**: What the primitive should accomplish

---

## Step 2: Search for Existing DataGen Integrations

Use `mcp__datagen__searchTools` with the capability/description:

```json
{
  "query": "[capability description]",
  "limit": 10
}
```

### If MCP Tools Found:

Present options to user with `AskUserQuestion`:
- Show tool names and descriptions
- Let user select which tool to wrap
- Get tool details with `mcp__datagen__getToolDetails`

### If No MCP Tools Found:

**Inform the user:**
```
No existing DataGen integration found for [capability].

Let me search for public APIs that provide this functionality...
```

**Search for public APIs** using web search:

```
Search query: "best API for [capability] 2026"
Additional searches:
- "[capability] API comparison"
- "[capability] API pricing"
- "popular [capability] services"
```

**Present API options** to user:

For each API found, show:
1. **API Name** (e.g., Hunter.io, Clearbit, RocketReach)
2. **Description**: What it does
3. **Pricing**: Free tier / paid plans
4. **Documentation**: Link to API docs
5. **Reliability**: User reviews, uptime

Use `AskUserQuestion` to let user:
- Select an API to integrate
- Skip and create custom primitive (no external API)
- Request more research on specific APIs

**If user selects an API:**
1. Fetch API documentation using web search or `WebFetch`
2. Extract key information:
   - Base URL / endpoint
   - Authentication method (API key, OAuth, etc.)
   - Required parameters
   - Response format
3. Create implementation plan:
   ```
   Option A: Add as MCP Server (Recommended)
   - Better: Reusable across all primitives
   - Use: /build-integrations or mcp__datagen__addRemoteMcpServer

   Option B: Direct API calls in primitive
   - Use httpx for HTTP requests
   - Store API key in DataGen secrets
   - Less flexible, but works for simple cases
   ```

---

## Step 3: Design Primitive Structure

Following **Bloomberg ACL 2025** tool description optimization principles (see `reference/tool-naming-principles.md`):

**Frontmatter Documentation (as Python docstring):**
```python
"""
Primitive: [Name]

[One-line description]

METADATA:
  name: [snake_case_name]
  category: [web|linkedin|data|email|research]
  created: [YYYY-MM-DD]
  mcp_tool: [tool_name] (if wrapping MCP tool)

WHEN TO USE:
  - [Specific use case 1]
  - [Specific use case 2]
  - [Trigger keywords that should select this primitive]

WHEN NOT TO USE:
  - [Situation where this is wrong primitive]
  - [Alternative primitive to use instead]
  - [Common mistake to avoid]

INPUT SCHEMA:
  - param1 (type): Description [required/optional]
  - param2 (type): Description with default value

OUTPUT SCHEMA:
  - result1 (type): Description of what this contains
  - result2 (type): Description of what this contains

EXAMPLE USAGE:
  ```python
  result, err = primitive_name(param1="value", param2=123)
  if err:
      print(f"Error: {err}")
      return

  print(result["result1"])
  ```

PERFORMANCE:
  - Latency: ~XXXms typical
  - Cost: $X per call (if applicable)
  - Rate limits: X calls/min (if applicable)

This is a TRUE primitive - no hardcoded columns, works generically.
"""
```

**Key elements from tool-selection-optimization article:**
- `when_to_use` — triggers selection (prevents under-selection)
- `when_not_to_use` — prevents over-selection (reduces false positives)
- Clear input/output schemas (reduces exploratory calls)
- Example usage (improves retrieval matching)
- Performance notes (helps with cost optimization)

---

## Step 4: Generate Primitive Code

Create `scripts/primitives/{name}.py`:

```python
"""
[Structured frontmatter docstring from Step 2]
"""

from .base import Primitive, register_primitive


@register_primitive
class [PascalCaseName](Primitive):
    """[One-line description]"""

    name = "[snake_case_name]"
    description = "[One-line description]"

    input_schema = {
        "param1": {
            "type": "string",
            "description": "Parameter description",
            "required": True
        },
        # ... more parameters
    }

    output_schema = {
        "result1": {
            "type": "string",
            "description": "Result description"
        },
        # ... more outputs
    }

    def run(self, **inputs) -> tuple[dict, str]:
        # Input validation
        param1 = inputs["param1"]

        if not param1 or not param1.strip():
            return {}, "empty param1"

        # Execute MCP tool or custom logic
        try:
            result = self.client.execute_tool(
                "mcp_Tool_name",
                {"param": param1}
            )
        except Exception as e:
            return {}, f"{self.name} failed: {str(e)}"

        # Handle response format (list, dict, etc.)
        if isinstance(result, list):
            if len(result) == 0:
                return {}, "empty result"
            result = result[0]

        # Extract and validate output
        output = result.get("key", "")
        if not output:
            return {}, "empty output"

        return {
            "result1": output,
            "result2": result.get("key2", "")
        }, ""


# Module-level instance for convenient imports
[snake_case_name] = [PascalCaseName]()
```

---

## Step 5: Register in __init__.py

Update `scripts/primitives/__init__.py`:
1. Add import: `from .[name] import [name], [PascalCaseName]`
2. Add to `__all__` list (both instance and class)
3. Update module docstring with new primitive description

---

## Step 6: Create Example Script

Create `scripts/examples/use_{name}.py`:

```python
#!/usr/bin/env python3
"""
Example: Using the [name] primitive
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from primitives import [name]


def main():
    """Demonstrate [name] primitive usage."""

    # Example 1: Basic usage
    result, err = [name](param1="example value")

    if err:
        print(f"Error: {err}")
        return 1

    print(f"✓ Success: {result['result1']}")

    # Example 2: With optional parameters
    result2, err = [name](
        param1="value",
        param2=123
    )

    if err:
        print(f"Error: {err}")
        return 1

    print(f"✓ Result: {result2}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## Step 7: Validate and Test

1. Run the example script to validate syntax
2. Check that primitive is properly registered
3. Test basic functionality with sample inputs

---

## Output Format

Creates three files:

1. **`scripts/primitives/{name}.py`** - The primitive with structured frontmatter
2. **`scripts/primitives/__init__.py`** - Updated with new primitive registration
3. **`scripts/examples/use_{name}.py`** - Example usage script

Print summary:
```
✓ Created primitive: {name}
  Location: scripts/primitives/{name}.py
  Category: {category}
  MCP Tool: {mcp_tool} (if applicable)

✓ Registered in: scripts/primitives/__init__.py

✓ Example script: scripts/examples/use_{name}.py

Next steps:
1. Test the primitive: python scripts/examples/use_{name}.py
2. Import in your workflows: from primitives import {name}
3. Use in graphs: result, err = {name}(param="value")
```

---

## Tool Description Best Practices

Following **Bloomberg ACL 2025** and **tool-selection-optimization** principles:

### 1. Description Quality (40% of tool selection accuracy)
- **Clear "when to use"**: Triggers that should select this primitive
- **Clear "when not to use"**: Prevents over-selection and false positives
- **Example queries**: Improves retrieval matching

### 2. Schema Completeness
- **Detailed input schemas**: Reduces exploratory calls
- **Expected outputs**: Sets clear expectations
- **Default values**: Makes primitives easier to use

### 3. Performance Notes
- **Latency estimates**: Helps with optimization decisions
- **Cost per call**: Enables budget tracking
- **Rate limits**: Prevents API failures

### 4. Naming Conventions
- Use **snake_case** for primitive names
- Use **verb_noun** pattern (e.g., `scrape_webpage`, `find_email`, `enrich_profile`)
- Avoid redundancy (not `firecrawl_scrape_with_firecrawl`)
- Be specific but not verbose

---

## References

- **Bloomberg ACL 2025**: Context optimization for tool calling
- **Tool Selection Optimization**: `reference/tool-selection-principles.md`
- **API Integration Patterns**: `reference/api-integration-patterns.md`
- **Primitive Base Class**: `scripts/primitives/base.py`
- **MCP Example**: `examples/firecrawl_scrape.py`
- **Direct API Example**: `examples/direct_api_primitive.py`
- **Build Integrations Skill**: `/build-integrations`
