# CLAUDE.md - Agent-Native Prototype

## Setup

**CRITICAL: Complete first-time setup before running any enrichment commands.**

### First-Time Setup

**→ [Complete Setup Guide](docs/setup/first-time-setup.md)**

The setup guide covers:
- Installing UV (recommended) or traditional Python
- Creating virtual environment
- Installing dependencies
- DataGen CLI installation and authentication
- MCP server configuration
- Verification and troubleshooting

### Quick Start (If Already Set Up)

```bash
# Activate virtual environment
source .venv/bin/activate

# Verify setup
python scripts/graph_enrich.py --lead example-leads --list
```

### Environment Variables

Required in `.env` file:
```bash
DATAGEN_API_KEY=your_api_key_here
```

## Agent-Native Architecture Principles

We're building agent-native apps. In agent-native architecture:
- **Traditional**: Code defines what happens. Computer executes instructions.
- **Agent-native**: Outcomes defined in natural language. Agent figures out how to achieve them.

### Core Characteristics

1. **Parity**: Anything the user can do in the app, the agent can do
2. **Granularity**: Features are prompts, not tools. Tools are atomic; features compose multiple tool calls
3. **Composability**: Agent combines tool calls in new ways, enabling emergent capability

### Filesystem as Intermediate Context

Use `./tmp/<workflow-name>/` for intermediate data between script steps:

```
/tmp/heyreach-report-2026-01-09/
├── campaigns.json           # Raw data from API
├── conversations/           # Per-campaign conversation data
│   ├── 291852.json
│   └── 210501.json
├── metrics.json             # Calculated metrics
└── report.md                # Final output
```

**Why:**
- **Fault tolerance**: If step 3 fails, steps 1-2 don't need to rerun
- **Modularity**: Claude can orchestrate scripts, inspect intermediate state
- **Debuggability**: Intermediate data is human-readable
- **Composability**: Scripts can be reordered, combined, or skipped

### Script Design for Agent Manipulation

Scripts should be:
- **Stateless**: Read from file, write to file (no hidden state)
- **Atomic**: Do one thing well (fetch, transform, or output)
- **Composable**: Output of one is input for another
- **Inspectable**: Use JSON/markdown for intermediate data
- **Error-first**: Return `(result, error)` tuple, check error before using result

### Error-First Pattern (SDK Functions)

Functions should return `(result, error)` tuple. Always check error before using result:

```python
def fetch_campaigns(output_path: str) -> tuple[dict, str]:
    """Returns (result, error). Check error first."""
    try:
        result = client.execute_tool("mcp_Heyreach_get_all_campaigns", {...})
        with open(output_path, "w") as f:
            json.dump(result, f)
        return result, ""  # Success: empty error string
    except Exception as e:
        return {}, f"fetch_campaigns failed: {e}"  # Failure: error message

# Usage - always check error first
campaigns, err = fetch_campaigns("/tmp/report/campaigns.json")
if err:
    print(f"Step 1 failed: {err}")
    return

conversations, err = fetch_conversations(campaigns, "./tmp/report/conversations/")
if err:
    print(f"Step 2 failed: {err}")
    return

# Safe to continue - no errors
metrics, err = calculate_metrics("./tmp/report/conversations/")
```

**Why error-first:**
- Explicit: Claude sees exactly what can fail
- No hidden exceptions: Control flow is visible
- Chainable: Stop pipeline at first failure
- Debuggable: Error message in variable, not stack trace

**Example pipeline:**
```bash
# Step 1: Fetch campaigns to intermediate storage
python scripts/fetch_campaigns.py --output /tmp/report/campaigns.json

# Step 2: Fetch conversations (reads campaigns.json)
python scripts/fetch_conversations.py --input ./tmp/report/campaigns.json --output /tmp/report/conversations/

# Step 3: Calculate metrics (reads conversations/)
python scripts/calculate_metrics.py --input ./tmp/report/conversations/ --output /tmp/report/metrics.json

# Step 4: Generate report (reads metrics.json)
python scripts/generate_report.py --input ./tmp/report/metrics.json --output reports/campaign-report.md
```

Claude can now:
- Skip step 1 if `./tmp/report/campaigns.json` exists
- Re-run only step 3 if metrics calculation needs adjustment
- Inspect any intermediate file to debug issues

## Research Resources

**Consult these sources when building commands, agents, and skills:**

- **Every.to** (https://every.to) - Agent-native architecture frameworks, AI product design patterns
  - Key article: `useful-resources/agent-native-every-to.md`
  - Topics: parity, granularity, composability, emergent capability, files as universal interface
  - **Use when:** Designing new skills, structuring agent workflows, deciding tool granularity, building composable pipelines


## Skill Architecture: MCP / SDK / Claude Pattern

When building skills that involve data fetching, processing, and analysis, use this three-tier pattern:

### MCP Layer (Interactive Operations)

Use `executeTool(mcp_<Provider>_<tool_name>)` for:
- Simple, single-call operations (list, filter, fetch one item)
- User-facing discovery (showing options, asking for selection)
- Operations needing immediate response for interaction

```json
{
  "tool_alias_name": "mcp_Heyreach_get_all_campaigns",
  "parameters": { "statuses": ["FINISHED"], "limit": 100 }
}
```

### SDK Layer (Data Pipelines)

Use Python scripts with DataGen SDK for:
- Multi-step data processing (fetch -> transform -> aggregate)
- Operations involving loops or iteration over multiple items
- Heavy data manipulation (calculations, filtering, sorting)
- Deterministic pipelines where reliability matters
- Saving structured output to files (markdown, JSON, CSV)

```bash
source .venv/bin/activate && python scripts/heyreach_campaign_report.py --campaigns 291852
# Outputs: reports/heyreach/campaign-report-2026-01-09.md
```

### Claude Layer (Intelligent Analysis)

Have Claude read the generated output for:
- Understanding and interpreting results
- Strategic recommendations and insights
- Pattern recognition across data
- Nuanced suggestions requiring AI reasoning

```
Read: reports/heyreach/campaign-report-2026-01-09.md
Edit: Append "## AI Strategic Analysis" section with insights
```

### Decision Matrix

| Task | Layer |
|------|-------|
| List/filter items for user selection | MCP |
| Fetch single item details | MCP |
| Process data across multiple items | SDK |
| Calculate metrics, aggregate data | SDK |
| Generate structured reports | SDK |
| Interpret results, provide recommendations | Claude |
| Strategic analysis, pattern recognition | Claude |

### Why This Pattern Works

1. **Token Efficiency**: SDK scripts handle data-heavy loops without consuming Claude tokens
2. **Reliability**: Deterministic scripts produce consistent, testable outputs
3. **Best AI Output**: Claude's analysis is best when reading complete, structured data
4. **Separation of Concerns**: Each layer does what it's best at


## Subagent Configuration

Subagents are defined in `.claude/agents/` with YAML frontmatter.

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (lowercase, hyphens) |
| `description` | Yes | When Claude should delegate to this agent |
| `model` | No | `sonnet`, `opus`, `haiku`, or `inherit` |
| `tools` | No | Tools the agent can use (inherits all if omitted) |
| `skills` | No | Skills to auto-load into agent context at startup |
| `color` | No | Background color for UI identification |

### Skills Field

The `skills` field **injects full skill content** into the agent's context at startup:

```yaml
---
name: daily-reporter
description: Generate and email daily reports
model: sonnet
skills:
  - user-activity-tracker
  - generate-report
---
```

**Key points:**
- Skills are **injected**, not just "available" - full content loaded at startup
- Subagents **don't inherit** skills from parent - must list explicitly
- Keeps agent files clean by referencing skills instead of duplicating content
- Agent body describes workflow; skills provide the details (queries, templates, etc.)

### Example Structure

```
.claude/
├── agents/
│   └── daily-reporter.md      # Agent config + workflow
└── skills/
    ├── user-activity-tracker/
    │   └── SKILL.md            # Data queries (PostHog, Neon)
    └── generate-report/
        ├── SKILL.md            # Template instructions
        └── templates/
            └── user-activity.html
```

**Reference:** [Claude Code Subagents Docs](https://code.claude.com/docs/en/sub-agents)


## When saving articles or post. following follow front matter standard
## Frontmatter Standard

**CRITICAL**: Every markdown file MUST include YAML frontmatter on line 1.

### Base Template
```yaml
---
title: "Concise Title"
description: "One-liner describing purpose"
category: "use-cases|linkedin|gtm|research"
tags: ["tag1", "tag2", "tag3"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: "active|draft|archived"
priority: "high|medium|low"
reference: [] # Optional: External URLs only (published posts, docs)
based_on: [] # Optional: Source files this content is based on (for Obsidian backlinks)
---
```

### Category-Specific Fields

**Use Cases**: Add `audience`, `gtm-focus`, `value-prop`
**LinkedIn**: Add `campaign-type`, `target-audience`
**Research**: Add `research-type`, `sources`
**GTM**: Add `asset-type`, `target-persona`

### Examples

```yaml
# Use Case
---
title: "LinkedIn Prospecting with AI"
description: "Automated prospecting with AI personalization"
category: "use-cases"
tags: ["prospecting", "linkedin", "automation"]
audience: "sales-teams"
gtm-focus: "prospecting-at-scale"
value-prop: "From CSV to CRM-ready signals in one session"
status: "active"
priority: "high"
created: 2026-01-04
updated: 2026-01-04
reference: ["https://docs.datagen.dev/use-cases/prospecting"]
based_on: ["[[competitor-analysis]]", "[[market-research]]"]
---
```
## Rules

1. Frontmatter MUST start line 1 (no blank lines before `---`)
2. Use YAML format with spaces (not tabs)
3. Dates in `YYYY-MM-DD` format
4. Update `updated` field when modifying files
5. Use kebab-case filenames: `linkedin-outreach-strategy.md`
6. `reference` field is optional but recommended for external URLs only (published posts, docs, external resources)
7. `based_on` field is optional but recommended for tracking internal source files (use Obsidian wikilink format `"[[filename]]"`)

## Obsidian Integration

### Wikilinks for Source Attribution
Use the `based_on` field in frontmatter with Obsidian wikilinks to track internal sources. This enables automatic backlinks in Obsidian.

**Example**:
```yaml
---
title: "LinkedIn Post Title"
reference: ["https://linkedin.com/posts/xyz"]
based_on: ["[[what_is_datagen]]", "[[automation_tool]]", "[[api_vs_sdks]]"]
---
```

### Wikilink Syntax in Frontmatter
- Use wikilink format: `"[[filename]]"` (with double brackets, quoted in YAML)
- Without .md extension: `"[[what_is_datagen]]"` not `"[[what_is_datagen.md]]"`
- With folders: `"[[folder/filename]]"`
- Obsidian will create automatic backlinks for all files in the `based_on` field

### When to Use What
- **`based_on` field**: Internal knowledge base files that informed this content (enables Obsidian backlinks)
- **`reference` field**: External URLs only (published posts, documentation, external articles)
- **Both together**: Track both source materials (based_on) and published outputs (reference)
