---
name: generate-report
description: Generate branded HTML reports with DataGen styling for email delivery
---

# Generate Report Skill

Creates professionally styled HTML reports using DataGen brand colors and components. Designed for email delivery via Gmail MCP.

## Usage

```bash
/generate-report
```

## Brand Colors

```css
:root {
  /* Primary palette */
  --primary: #005047;      /* Dark teal - headers, buttons, primary text */
  --secondary: #00795e;    /* Light teal - accents, hover states */

  /* Status colors */
  --success: #219653;      /* Green - positive metrics, completed */
  --danger: #D34053;       /* Red - action needed, errors, critical */
  --warning: #FFA70B;      /* Orange - warnings, at-risk */

  /* Dark mode / backgrounds */
  --boxdark: #24303F;      /* Dark background */
  --boxdark-2: #1A222C;    /* Darker background */

  /* Grays */
  --gray-50: #f9fafb;      /* Lightest - table headers */
  --gray-100: #f3f4f6;     /* Light - backgrounds */
  --gray-200: #e5e7eb;     /* Borders */
  --gray-500: #6b7280;     /* Secondary text */
  --gray-600: #4b5563;     /* Body text */
  --gray-700: #374151;     /* Strong text */
  --gray-900: #111827;     /* Headings */
}
```

## Component Library

### Section Icons

Use these emoji + background color combinations for section headers:

| Section Type | Icon | Background Class |
|--------------|------|------------------|
| Action needed | Target | `rgba(211, 64, 83, 0.1)` |
| Active/Success | Lightning | `rgba(33, 150, 83, 0.1)` |
| Warning/At-risk | Warning | `rgba(255, 167, 11, 0.1)` |
| Info/Neutral | Magnifier | `rgba(0, 80, 71, 0.1)` |

### Badges

```html
<!-- Action needed (red) -->
<span class="badge badge-action">Needs Outreach</span>

<!-- Success (green) -->
<span class="badge badge-success">12 runs</span>

<!-- Warning (orange) -->
<span class="badge badge-warning">7 days</span>

<!-- Primary (teal) -->
<span class="badge badge-primary">Gmail</span>
```

### Metrics Bar

```html
<div class="metrics-bar">
  <div class="metric">
    <div class="metric-dot green"></div>
    <span class="metric-value">156</span>
    <span class="metric-label">Total Runs</span>
  </div>
  <div class="metric">
    <div class="metric-dot blue"></div>
    <span class="metric-value">85%</span>
    <span class="metric-label">Success Rate</span>
  </div>
</div>
```

### Trend Indicators

```html
<span class="trend up">+12%</span>
<span class="trend down">-5%</span>
```

## Report Structure

Standard report layout:

```
1. Header (gradient background with title + date)
2. Summary Cards (4-column grid with key metrics)
3. Sections (each with icon, title, subtitle, and table/content)
4. Footer (branding + links)
```

## Templates

### Available Templates

| Template | Purpose | Location |
|----------|---------|----------|
| `base-email.html` | Base HTML email structure | `templates/base-email.html` |
| `user-activity.html` | User activity report | `templates/user-activity.html` |

### Template Placeholders

Use double-brace syntax for variables:

```html
{{REPORT_DATE}}         <!-- 2026-01-25 -->
{{TOTAL_USERS}}         <!-- 156 -->
{{NEW_USERS_7D}}        <!-- 12 -->

<!-- Loops use #/^ syntax -->
{{#HIGH_INTENT_PROSPECTS}}
<tr>
  <td>{{EMAIL}}</td>
  <td>{{MCP_SERVER}}</td>
</tr>
{{/HIGH_INTENT_PROSPECTS}}

<!-- Empty state -->
{{^HIGH_INTENT_PROSPECTS}}
<tr><td colspan="5">No data</td></tr>
{{/HIGH_INTENT_PROSPECTS}}
```

## Sending via Gmail MCP

```json
{
  "tool_alias_name": "mcp_Gmail_Yusheng_gmail_send_email",
  "parameters": {
    "to": ["recipient@example.com"],
    "subject": "Report Title - {DATE}",
    "body": "Plain text fallback for non-HTML clients.",
    "htmlBody": "<full HTML content>",
    "mimeType": "multipart/alternative"
  }
}
```

**Gmail MCP Parameters:**
- `htmlBody`: Full HTML content for rich formatting
- `mimeType`: Set to `multipart/alternative` for HTML + plain text fallback
- `to`: Array of recipient emails

## Workflow

### Step 1: Gather Data
Use data-focused skills (like `/user-activity-tracker`) to collect metrics.

### Step 2: Read Template
```
Read: .claude/skills/generate-report/templates/{template-name}.html
```

### Step 3: Replace Placeholders
Replace `{{VARIABLE}}` placeholders with actual data.

### Step 4: Save Report
```
Save to: reports/{report-type}/report-{YYYY-MM-DD}.html
```

### Step 5: Send Email
Use Gmail MCP with `htmlBody` parameter.

## Email Best Practices

1. **Inline CSS**: Email clients strip `<style>` tags - use inline styles
2. **Max width 700px**: Optimal for email reading
3. **Table-based layout**: More reliable than flexbox/grid in email
4. **Test fallback**: Always include plain `body` text
5. **Image alt text**: Many clients block images by default

## File Structure

```
.claude/skills/generate-report/
├── SKILL.md                    # This file
└── templates/
    ├── base-email.html         # Base HTML structure
    └── user-activity.html      # User activity report template
```
