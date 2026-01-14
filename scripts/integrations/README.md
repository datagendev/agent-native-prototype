# Integration-Based Enrichment System

A scalable, agent-native enrichment system inspired by Clay's table enrichment, built for Claude Code to orchestrate multi-integration data enrichment at scale.

## Architecture

### Design Principles

Based on [agent-native architecture](../../useful-resources/agent-native-every-to.md) principles:

1. **Atomic Integrations**: Each integration is a micro-tool that does one thing well
2. **Explicit Dependencies**: Input/output columns define data flow
3. **Error-First Pattern**: All integrations return `(result, error)` tuples
4. **Agent Orchestration**: Claude reads registry and chains integrations
5. **Parallel Execution**: ThreadPoolExecutor for I/O-bound operations

### Components

```
scripts/integrations/
├── __init__.py           # Integration registry (Claude reads this)
├── linkedin_profile.py   # LinkedIn profile enrichment
├── web_research.py       # AI-powered web research
├── find_ceo.py          # CEO finder
└── README.md            # This file

scripts/
└── batch_enrich.py      # Orchestrator (runs integrations in parallel)
```

## Integration Contract

Each integration module follows this standard:

```python
# === CONTRACT ===
INPUT_COLS = ["required_column"]
OUTPUT_COLS = ["produced_column1", "produced_column2"]

def enrich(row: dict) -> tuple[dict, str]:
    """
    Enrich a single row.

    Returns:
        (enriched_fields, error) tuple:
        - Success: ({"column": "value"}, "")
        - Failure: ({}, "error message")
    """
```

### Why This Pattern?

- **Claude can introspect**: Read `__init__.py` to see available integrations
- **No hidden dependencies**: Input/output columns are explicit
- **Error isolation**: One row failure doesn't crash the batch
- **Composable**: Agent chains integrations by matching columns

## Available Integrations

### `linkedin_profile`

**Input**: `linkedin_url`
**Output**: `headline`, `current_company`, `location`, `follower_count`

Fetches LinkedIn profile data using DataGen's `get_linkedin_person_data` tool.

### `web_research`

**Input**: `company_domain`
**Output**: `company_description`, `tech_stack`, `employee_count`

Uses AI-powered web research (`chatgpt_webresearch`) to gather company information.

### `find_ceo`

**Input**: `company_domain`
**Output**: `ceo_name`, `ceo_linkedin_url`

Finds CEO information using web research.

## Usage

### For Claude

When user says: "Enrich lead-list/founders.csv with LinkedIn profile"

1. Read `scripts/integrations/__init__.py` → see available integrations
2. Read CSV headers → validate columns exist
3. Run: `python scripts/batch_enrich.py --input lead-list/founders.csv --integrations linkedin_profile`

### For Humans

```bash
# Single integration
source .venv/bin/activate && python scripts/batch_enrich.py \
  --input lead-list/founders.csv \
  --integrations linkedin_profile

# Multiple integrations
source .venv/bin/activate && python scripts/batch_enrich.py \
  --input lead-list/founders.csv \
  --integrations linkedin_profile,web_research \
  --parallel 10

# Custom output
source .venv/bin/activate && python scripts/batch_enrich.py \
  --input lead-list/founders.csv \
  --integrations linkedin_profile \
  --output enriched_founders.csv
```

## Dependency Chaining

Claude can chain integrations when dependencies exist:

**Example**: User wants CEO email but CSV only has `company_domain`

```
CSV columns: [name, company_domain]

User: "Enrich with CEO email"

Claude sees:
  1. ceo_email needs: ceo_name, company_domain
  2. find_ceo needs: company_domain → produces: ceo_name

Claude chains:
  Step 1: Run find_ceo (adds ceo_name column)
  Step 2: Run ceo_email (uses new ceo_name column)
```

Dependency resolution happens in Claude's reasoning, not in code.

## Adding New Integrations

### 1. Create integration module

```bash
touch scripts/integrations/my_integration.py
```

### 2. Implement contract

```python
"""
Integration: My Custom Enrichment

Input columns: input_col
Output columns: output_col1, output_col2
"""

import os
from pathlib import Path
from datagen_sdk import DatagenClient
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

if not os.getenv("DATAGEN_API_KEY"):
    raise RuntimeError("DATAGEN_API_KEY not set")

client = DatagenClient()

INPUT_COLS = ["input_col"]
OUTPUT_COLS = ["output_col1", "output_col2"]

def enrich(row: dict) -> tuple[dict, str]:
    input_val = row.get("input_col")
    if not input_val:
        return {}, "missing input_col"

    try:
        # Your enrichment logic here
        result = client.execute_tool("your_tool", {"param": input_val})

        return {
            "output_col1": result.get("field1"),
            "output_col2": result.get("field2")
        }, ""
    except Exception as e:
        return {}, f"my_integration error: {str(e)}"
```

### 3. Register in `__init__.py`

```python
INTEGRATIONS = {
    # ... existing integrations ...
    "my_integration": {
        "input": ["input_col"],
        "output": ["output_col1", "output_col2"],
        "description": "Brief description"
    }
}
```

### 4. Test

```bash
source .venv/bin/activate && python scripts/batch_enrich.py \
  --input test.csv \
  --integrations my_integration \
  --parallel 2
```

## Performance Tuning

### Parallel Workers

Default: 5 workers. Adjust based on:
- **API rate limits**: Lower workers if hitting limits
- **Dataset size**: More workers for large datasets (but max 16 per agent-native guidelines)
- **I/O vs CPU**: More workers for I/O-bound operations

```bash
# Conservative (avoid rate limits)
--parallel 2

# Balanced
--parallel 5

# Aggressive (large dataset, no rate limits)
--parallel 10
```

### Error Handling

The system continues processing even if some rows fail:
- Errors logged per row
- Failed rows still output (with empty enrichment columns)
- Stats show success/error counts

## Example Workflows

### Workflow 1: LinkedIn Profile Enrichment

```
Input: founders.csv
Columns: [name, company, linkedin_url]

Command:
python scripts/batch_enrich.py \
  --input founders.csv \
  --integrations linkedin_profile

Output: founders_enriched.csv
Columns: [name, company, linkedin_url, headline, current_company, location, follower_count]
```

### Workflow 2: Multi-Integration

```
Input: companies.csv
Columns: [company_name, company_domain]

Command:
python scripts/batch_enrich.py \
  --input companies.csv \
  --integrations web_research,find_ceo

Output: companies_enriched.csv
Columns: [company_name, company_domain, company_description, tech_stack,
          employee_count, ceo_name, ceo_linkedin_url]
```

### Workflow 3: Dependency Chain (Claude-orchestrated)

```
Input: leads.csv
Columns: [name, company_domain]

User: "Enrich with CEO LinkedIn profile"

Claude:
  Step 1: python scripts/batch_enrich.py --input leads.csv --integrations find_ceo
  Step 2: python scripts/batch_enrich.py --input leads_enriched.csv --integrations linkedin_profile

Output: leads_enriched_enriched.csv
Columns: [name, company_domain, ceo_name, ceo_linkedin_url, headline, current_company, location, follower_count]
```

## Troubleshooting

### "Integration not found"

Check `scripts/integrations/__init__.py` - integration must be registered.

### "Required column missing"

Input CSV must have all columns listed in integration's `INPUT_COLS`.

### "Tool not found"

DataGen tool name might be wrong. Use DataGen MCP to search for correct tool:
```
searchTools({query: "linkedin profile"})
getToolDetails({tool_name: "get_linkedin_person_data"})
```

### All rows failing

1. Check `DATAGEN_API_KEY` is set in `../.env`
2. Check MCP server is connected in DataGen dashboard
3. Test tool directly: `python -c "from datagen_sdk import DatagenClient; client = DatagenClient(); print(client.execute_tool('tool_name', {}))"`

## Design Philosophy

This system follows the **MCP / SDK / Claude pattern** from CLAUDE.md:

| Layer | Purpose | This System |
|-------|---------|-------------|
| **MCP** | Interactive discovery | User discovers tools via DataGen MCP |
| **SDK** | Data pipelines | Integrations use DataGen SDK for tool calls |
| **Claude** | Orchestration | Claude reads registry, chains integrations |

**Why this works:**
- **Token efficient**: Integrations run in Python, not consuming Claude tokens
- **Reliable**: Deterministic data processing with error handling
- **Agent-native**: Claude orchestrates by reading integration contracts
- **Composable**: New integrations add emergent capability

## Next Steps

**More Integrations to Build:**
- `ceo_email`: Find CEO email from name + domain
- `company_linkedin`: Find company LinkedIn from domain
- `apollo_enrich`: Enrich with Apollo API
- `clearbit_enrich`: Enrich with Clearbit API

**Improvements:**
- Structured extraction for web research results
- Caching layer for repeated lookups
- Progress persistence (resume failed batches)
- Integration versioning
