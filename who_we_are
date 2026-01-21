---
title: "Building Agentic Claude Code with DataGen"
description: "Reference guide for MCP/SDK/Claude pattern with agent-native principles"
category: "research"
tags: ["agent-native", "claude-code", "datagen", "skills", "architecture"]
created: 2026-01-10
updated: 2026-01-10
status: "active"
priority: "high"
based_on: ["[[agent-native-every-to]]", "[[CLAUDE]]"]
---

# Building Agentic Claude Code with DataGen

A reference guide for building composable, agent-native workflows using the MCP/SDK/Claude pattern.

## Core Architecture: Three-Tier Pattern

```
┌─────────────────────────────────────────────────────────────┐
│  MCP Layer     │  Interactive operations, user discovery   │
├─────────────────────────────────────────────────────────────┤
│  SDK Layer     │  Data pipelines, loops, file I/O          │
├─────────────────────────────────────────────────────────────┤
│  Claude Layer  │  Analysis, recommendations, orchestration │
└─────────────────────────────────────────────────────────────┘
```

### When to Use Each Layer

| Task | Layer | Why |
|------|-------|-----|
| List items for user selection | MCP | Interactive, immediate response |
| Fetch single item details | MCP | Simple, one-shot operation |
| Process multiple items in loop | SDK | Avoid token waste on iteration |
| Calculate metrics, aggregate | SDK | Deterministic, testable |
| Generate structured files | SDK | Reliable file I/O |
| Interpret results | Claude | Requires reasoning |
| Strategic recommendations | Claude | Pattern recognition |
| Orchestrate multi-step workflow | Claude | Decision-making |

---

## MCP Layer: Interactive Operations

Use `executeTool` for single-call, user-facing operations:

```python
# Via DataGen MCP
result = executeTool(
    "mcp_Heyreach_get_all_campaigns",
    {"statuses": ["FINISHED"], "limit": 100}
)
```

**Best for:**
- Listing options for user to select
- Fetching single item details
- Quick lookups needing immediate response

---

## SDK Layer: Data Pipelines

Use Python scripts with DataGen SDK for data-heavy operations:

```python
from datagen_sdk import DatagenClient

client = DatagenClient()
result = client.execute_tool("mcp_Heyreach_get_all_campaigns", {...})
```

**Best for:**
- Multi-step processing (fetch → transform → aggregate)
- Loops and iteration over items
- File I/O (JSON, markdown, CSV)
- Deterministic pipelines

### Script Design Principles

Scripts should be:

1. **Atomic** - Do one thing well
2. **Stateless** - Read from file, write to file
3. **Composable** - Output of one is input for another
4. **Inspectable** - Use JSON/markdown for data
5. **Error-first** - Return `(result, error)` tuple

### Error-First Pattern

```python
def fetch_campaigns(output_path: str) -> tuple[dict, str]:
    """Returns (result, error). Check error first."""
    try:
        result = client.execute_tool("mcp_Heyreach_get_all_campaigns", {...})
        Path(output_path).write_text(json.dumps(result, indent=2))
        return result, ""
    except Exception as e:
        return {}, f"fetch_campaigns failed: {e}"

# Usage
campaigns, err = fetch_campaigns("/tmp/report/campaigns.json")
if err:
    print(f"Failed: {err}")
    return
```

---

## Claude Layer: Intelligent Analysis

Claude reads structured output and provides:
- Pattern recognition across data
- Strategic recommendations
- Nuanced insights requiring reasoning
- Workflow orchestration decisions

```
1. Read: /tmp/report/metrics.json
2. Analyze holistically
3. Append: "## AI Strategic Analysis" section
```

---

## Bridging Tools with /tmp/ Files

Use `/tmp/<workflow-name>/` for intermediate data between steps:

```
/tmp/heyreach-2026-01-10/
├── campaigns.json              # Step 1: Raw API data
├── conversations/
│   ├── 291852.json            # Step 2: Per-item data
│   └── 210501.json
├── metrics.json               # Step 3: Calculated metrics
└── report.md                  # Step 4: Final output
```

### Why Intermediate Files?

| Benefit | Description |
|---------|-------------|
| **Fault tolerance** | If step 3 fails, steps 1-2 don't rerun |
| **Debuggability** | Claude can inspect any intermediate file |
| **Composability** | Scripts can be reordered, combined, skipped |
| **Resumability** | Skip steps if files already exist |

### Example Pipeline

```bash
# Step 1: Fetch to intermediate storage
python scripts/fetch_campaigns.py --output /tmp/report/campaigns.json

# Step 2: Process (reads step 1 output)
python scripts/fetch_conversations.py --input /tmp/report/campaigns.json

# Step 3: Calculate (reads step 2 output)
python scripts/calculate_metrics.py --input /tmp/report/conversations/

# Step 4: Generate (reads step 3 output)
python scripts/generate_report.py --input /tmp/report/metrics.json
```

Claude can:
- Skip step 1 if `campaigns.json` exists
- Re-run only step 3 if metrics need adjustment
- Inspect any file to debug issues

---

## Agent-Native Principles

From Every.to's agent-native architecture framework:

### 1. Parity
Anything the user can do, the agent can do through tools.

### 2. Granularity
Tools are atomic primitives. Features are prompts that compose multiple tool calls. Decision-making belongs in prompts, not bundled into tools.

### 3. Composability
With atomic tools + parity, new features emerge by writing new prompts, not new code. Users ask for unanticipated things, agent composes existing tools.

### 4. Emergent Capability
Build capable foundation → observe what users ask → formalize patterns. Don't guess needs; discover them through agent usage.

### 5. Files as Universal Interface
Agents know `cat`, `grep`, `mkdir`. Files are:
- Inspectable (users see agent work)
- Portable (export/backup trivial)
- Self-documenting (`/projects/acme/notes/` > `SELECT * FROM notes`)

---

## Building Skills

A skill combines all three layers:

```
Step 1 (MCP):    Fetch data via executeTool
Step 2 (Claude): AskUserQuestion → user selects options
Step 3 (SDK):    Run atomic scripts with /tmp/ storage
Step 4 (Claude): Read output → Append AI analysis
```

### Skill File Structure

```
.claude/skills/my-skill/
└── SKILL.md          # Workflow instructions
```

### SKILL.md Template

```markdown
---
name: my-skill
description: What this skill does
---

# My Skill

## Architecture
Step 1 (MCP): ...
Step 2 (Claude): ...
Step 3 (SDK): ...

## Workflow
### Step 1: Fetch Data
[MCP tool call]

### Step 2: User Selection
[AskUserQuestion with options]

### Step 3: Run Pipeline
[SDK scripts with /tmp/ storage]

### Step 4: AI Analysis
[Read and enhance output]
```

---

## Script Organization

```
scripts/
└── workflow-name/
    ├── fetch_data.py           # Step 1: API → /tmp/
    ├── process_data.py         # Step 2: Transform
    ├── calculate_metrics.py    # Step 3: Aggregate
    └── generate_report.py      # Step 4: Output
```

Each script:
- Has CLI interface (`--input`, `--output`)
- Uses error-first returns
- Writes to `/tmp/<workflow>/<step>.json`
- Is independently runnable

---

## Quick Reference

### DataGen SDK Setup

```python
import os
from datagen_sdk import DatagenClient

if not os.getenv("DATAGEN_API_KEY"):
    raise RuntimeError("DATAGEN_API_KEY not set")

client = DatagenClient()
result = client.execute_tool("mcp_<Provider>_<tool>", {...})
```

### Virtual Environment

```bash
# Always activate before running scripts
source .venv/bin/activate && python scripts/my_script.py
```

### AskUserQuestion Pattern

```json
{
  "questions": [{
    "question": "Which items should I process?",
    "header": "Selection",
    "multiSelect": true,
    "options": [
      {"label": "Item A", "description": "Details about A"},
      {"label": "Item B", "description": "Details about B"},
      {"label": "All items", "description": "Process everything"}
    ]
  }]
}
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Instead |
|--------------|--------------|---------|
| Agent-as-router | Wastes agent intelligence | Let agent compose tools |
| Over-constrained tools | Blocks emergent use | Keep tools atomic |
| Logic in code | Prevents agent judgment | Move decisions to prompts |
| Monolithic scripts | Can't skip/retry steps | Break into atomic pieces |
| No intermediate files | Re-run everything on failure | Use /tmp/ storage |
| Guessing tool names | Wrong tool calls | Use searchTools first |

---

## Resources

- **Every.to Agent-Native Guide**: `useful-resources/agent-native-every-to.md`
- **DataGen SDK Docs**: `mcp__datagen__datagen-sdk-doc`
- **Example Skill**: `.claude/skills/heyreach-campaign-report/SKILL.md`
