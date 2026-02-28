---
name: generate-delta-report
description: Generate HTML delta reports focused on 24-hour changes with error categorization and week-over-week comparison
---

# Generate Delta Report Skill

Creates focused HTML reports showing only 24-hour deltas (what's NEW) with branded DataGen styling. Designed for daily operational monitoring and email delivery via Gmail MCP.

## Usage

```bash
/generate-delta-report
```

## Purpose

Unlike full-state reports, delta reports show:
- **NEW issues** (appeared today)
- **Recurring issues** (seen yesterday and today)
- **Resolved issues** (seen yesterday, gone today)
- **Error categorization** (infrastructure, platform, MCP, user code, third-party)

## Input Files

Read from `tmp/daily-delta-report-{date}/`:
- `posthog_24h.json` - New signups, UI blockers, MCP clicks
- `neon_fastapi_24h.json` - Deployments, runs, tool executions
- `neon_wasp_24h.json` - Agent executions
- `errors_categorized.json` - Errors grouped by category
- `deltas.json` - Comparison with previous day

## Output

Save to `weekly-report/delta-report-{date}.html`

## Report Sections

### 1. Executive Summary
- New signups count
- New deployments count
- Total errors by category
- Delta vs yesterday (↑ worsening, ↓ improving, → unchanged)

### 2. New Signups & Behavior
- Email, first seen, pages visited
- Session duration
- MCP servers clicked
- Fast activators (users who executed tools within 24h)

### 3. UI Blockers
- Rage clicks by page/user
- JS exceptions by error type
- Affected users

### 4. Error Analysis by Category

#### 🔥 Infrastructure Issues
- Modal OOM (rc=137)
- API timeouts
- Rate limits
- 502/503 errors

#### 🐛 Platform Bugs
- Missing Neon views
- `input_vars` not defined
- Credit check failures
- Missing env vars

#### 🔌 MCP Issues
- MCP server not connected
- OAuth expired
- Remote MCP failures

#### 👤 User Code Errors
- SyntaxError, TypeError, NameError
- IndentationError, AttributeError

#### 🌐 Third-party Issues
- HubSpot, LinkedIn, Gmail API errors
- 400/401/403 responses

### 5. Week-over-Week Comparison

Table format:
| Category | Yesterday | Today | Status |
|----------|-----------|-------|--------|
| Infrastructure | 5 | 2 | ✅ Improving (-3) |
| Platform bugs | 0 | 3 | ⚠️ Worsening (+3) |
| MCP issues | 1 | 1 | → Unchanged |

### 6. New Agents Deployed
- Entry prompt preview (what they're trying to do)
- Status, duration
- Use case categorization

### 7. Tool Execution Trends
- Most-used tools (top 10)
- New tool adoptions (first-time tool usage)
- Failure patterns by provider

## DataGen Brand Colors

```css
--primary: #005047;      /* Dark teal */
--secondary: #00795e;    /* Light teal */
--success: #219653;      /* Green */
--danger: #D34053;       /* Red */
--warning: #FFA70B;      /* Orange */
--gray-900: #111827;     /* Headings */
```

## Template Location

`.claude/skills/generate-delta-report/templates/delta-report.html`

## Workflow

1. **Read data files** from `tmp/daily-delta-report-{date}/`
2. **Parse JSON** into report variables
3. **Apply template** with placeholders
4. **Save HTML** to `weekly-report/delta-report-{date}.html`
5. **Return path** for email delivery

## Example Usage in Agent

```python
from datetime import datetime
from pathlib import Path
import json

date = datetime.now().strftime("%Y-%m-%d")
tmp_dir = Path(f"tmp/daily-delta-report-{date}")
output_dir = Path("weekly-report")
output_dir.mkdir(exist_ok=True)

# Load data
with open(tmp_dir / "posthog_24h.json") as f:
    posthog_data = json.load(f)

with open(tmp_dir / "neon_fastapi_24h.json") as f:
    neon_fastapi_data = json.load(f)

with open(tmp_dir / "errors_categorized.json") as f:
    errors_categorized = json.load(f)

with open(tmp_dir / "deltas.json") as f:
    deltas = json.load(f)

# Generate HTML (Claude reads template and fills in data)
# ... template rendering logic ...

# Save output
output_path = output_dir / f"delta-report-{date}.html"
```

## Key Features

- **Mobile-responsive** (< 700px width for email clients)
- **Color-coded categories** for quick scanning
- **Expandable error details** (show first 200 chars, expand for full)
- **Delta indicators** (↑ ↓ → for trend direction)
- **User email links** (mailto: for quick outreach)
