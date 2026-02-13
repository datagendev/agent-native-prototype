#!/usr/bin/env python3
"""
Generate HTML conversation summary report.

Step 5 of the conversation summary pipeline.
Reads: /tmp/heyreach-summary-{date}/digest.json
       /tmp/heyreach-summary-{date}/analysis.md
Outputs: reports/heyreach/conversation-summary-{date}.html

Usage:
    python generate_conversation_summary.py
    python generate_conversation_summary.py --input-dir /tmp/heyreach-summary-2026-02-13
    python generate_conversation_summary.py --template path/to/template.html
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from html import escape


def get_input_dir() -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d")
    return Path(f"/tmp/heyreach-summary-{date_str}")


def load_template(template_path: Path) -> tuple[str, str]:
    """Load HTML template. Returns (template, error)."""
    if not template_path.exists():
        return "", f"Template not found: {template_path}"
    try:
        return template_path.read_text(), ""
    except Exception as e:
        return "", f"Failed to load template: {e}"


def badge_html(text: str, badge_class: str = "badge-primary") -> str:
    return f'<span class="badge {badge_class}">{escape(text)}</span>'


def build_summary_cards(summary: dict) -> str:
    return f"""
    <div class="summary-grid">
      <div class="summary-card">
        <div class="number">{summary.get('with_replies', 0)}</div>
        <div class="label">Active Conversations</div>
      </div>
      <div class="summary-card">
        <div class="number">{summary.get('total_replies', 0)}</div>
        <div class="label">Replies Received</div>
      </div>
      <div class="summary-card">
        <div class="number">{summary.get('meeting_signals', 0)}</div>
        <div class="label">Meeting Signals</div>
      </div>
      <div class="summary-card">
        <div class="number">{summary.get('campaigns_active', 0)}</div>
        <div class="label">Active Campaigns</div>
      </div>
    </div>"""


def build_noteworthy_section(conversations: list[dict]) -> str:
    """Build the noteworthy conversations section (meeting signals + high engagement)."""
    noteworthy = [
        c
        for c in conversations
        if c.get("has_meeting_signal") or c.get("reply_count", 0) >= 3
    ]

    if not noteworthy:
        return ""

    rows = ""
    for conv in noteworthy[:10]:
        person = conv.get("person", {})
        name = escape(person.get("name", "Unknown"))
        headline = escape(person.get("headline", ""))
        campaign = escape(conv.get("campaign_name", ""))
        replies = conv.get("reply_count", 0)
        linkedin_url = person.get("linkedin_url", "")

        signals = []
        if conv.get("has_meeting_signal"):
            signals.append(badge_html("Meeting Signal", "badge-success"))
        if replies >= 3:
            signals.append(badge_html(f"{replies} replies", "badge-primary"))

        name_cell = f'<a href="{escape(linkedin_url)}" style="color: var(--primary); text-decoration: none;">{name}</a>' if linkedin_url else name

        rows += f"""
        <tr>
          <td class="email-cell">{name_cell}<br><span style="font-size: 12px; color: var(--gray-500);">{headline}</span></td>
          <td>{campaign}</td>
          <td>{"".join(signals)}</td>
        </tr>"""

    return f"""
    <div class="section">
      <div class="section-header">
        <div class="section-icon action">!</div>
        <div>
          <h2>Noteworthy Conversations</h2>
          <p class="section-subtitle">Meeting signals and high engagement</p>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr><th>Person</th><th>Campaign</th><th>Signals</th></tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>"""


def build_analysis_section(analysis_md: str) -> str:
    """Build the AI analysis section from markdown."""
    if not analysis_md.strip():
        return ""

    # Simple markdown-to-html for the analysis
    lines = analysis_md.strip().split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<br>")
        elif stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3 style='margin-top: 16px; margin-bottom: 8px; font-size: 15px; color: var(--gray-700);'>{escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2 style='margin-top: 20px; margin-bottom: 10px;'>{escape(stripped[3:])}</h2>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul style='margin: 8px 0; padding-left: 20px;'>")
                in_list = True
            content = stripped[2:]
            # Bold text between **
            import re
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            html_lines.append(f"<li style='margin-bottom: 6px; color: var(--gray-600);'>{content}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p style='color: var(--gray-600); margin-bottom: 8px;'>{escape(stripped)}</p>")

    if in_list:
        html_lines.append("</ul>")

    return f"""
    <div class="section">
      <div class="section-header">
        <div class="section-icon info">i</div>
        <div>
          <h2>AI Analysis</h2>
          <p class="section-subtitle">Themes, patterns, and recommendations</p>
        </div>
      </div>
      {"".join(html_lines)}
    </div>"""


def build_conversations_table(conversations: list[dict]) -> str:
    """Build the full conversations table."""
    if not conversations:
        return """
        <div class="section">
          <div class="empty-state">
            <div class="empty-state-icon">--</div>
            <p>No conversations with replies in this period.</p>
          </div>
        </div>"""

    rows = ""
    for conv in conversations:
        person = conv.get("person", {})
        name = escape(person.get("name", "Unknown"))
        headline = escape(person.get("headline", ""))[:50]
        campaign = escape(conv.get("campaign_name", ""))
        msg_count = conv.get("message_count", 0)
        reply_count = conv.get("reply_count", 0)
        last_activity = conv.get("last_activity", "")[:10]
        linkedin_url = person.get("linkedin_url", "")

        name_cell = f'<a href="{escape(linkedin_url)}" style="color: var(--primary); text-decoration: none;">{name}</a>' if linkedin_url else name

        # Status badge
        if conv.get("has_meeting_signal"):
            status = badge_html("Hot", "badge-success")
        elif reply_count >= 3:
            status = badge_html("Engaged", "badge-primary")
        elif reply_count > 0:
            status = badge_html("Replied", "badge-warning")
        else:
            status = badge_html("Outreach", "badge-action")

        rows += f"""
        <tr>
          <td class="email-cell">{name_cell}<br><span style="font-size: 12px; color: var(--gray-500);">{headline}</span></td>
          <td>{campaign}</td>
          <td style="text-align: center;">{msg_count}</td>
          <td style="text-align: center;">{reply_count}</td>
          <td>{last_activity}</td>
          <td>{status}</td>
        </tr>"""

    return f"""
    <div class="section">
      <div class="section-header">
        <div class="section-icon active">+</div>
        <div>
          <h2>All Conversations</h2>
          <p class="section-subtitle">Conversations with replies in this period</p>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Person</th>
              <th>Campaign</th>
              <th style="text-align: center;">Messages</th>
              <th style="text-align: center;">Replies</th>
              <th>Last Active</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>"""


def generate_report(
    digest: dict, analysis_md: str, template: str
) -> tuple[str, str]:
    """
    Generate HTML report from digest and analysis.

    Returns (html, error). Check error first.
    """
    try:
        summary = digest.get("summary", {})
        period = digest.get("period", {})
        conversations = digest.get("conversations_with_replies", [])

        # Build content sections
        content_parts = [
            build_summary_cards(summary),
            build_noteworthy_section(conversations),
            build_analysis_section(analysis_md),
            build_conversations_table(conversations),
        ]

        content = "".join(content_parts)

        # Fill template
        title = "HeyReach Conversation Summary"
        date_range = f"{period.get('start', '')} to {period.get('end', '')}"

        html = template.replace("{{REPORT_TITLE}}", title)
        html = html.replace("{{REPORT_DATE}}", date_range)
        html = html.replace("{{CONTENT}}", content)

        return html, ""

    except Exception as e:
        return "", f"generate_report failed: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate HeyReach conversation summary HTML report"
    )
    parser.add_argument("--input-dir", type=str, help="Input directory")
    parser.add_argument("--template", type=str, help="Override HTML template path")
    parser.add_argument("--output", type=str, help="Override output path")
    args = parser.parse_args()

    input_dir = Path(args.input_dir) if args.input_dir else get_input_dir()

    # Load digest
    digest_path = input_dir / "digest.json"
    if not digest_path.exists():
        print(f"ERROR: {digest_path} not found", file=sys.stderr)
        return 1

    digest = json.loads(digest_path.read_text())

    # Load analysis (optional)
    analysis_path = input_dir / "analysis.md"
    analysis_md = analysis_path.read_text() if analysis_path.exists() else ""

    # Load template
    if args.template:
        template_path = Path(args.template)
    else:
        # Default template location
        project_root = Path(__file__).parent.parent.parent
        template_path = (
            project_root
            / "agents"
            / "heyreach-conversation-summary"
            / "templates"
            / "conversation-summary.html"
        )
        # Fallback to base template
        if not template_path.exists():
            template_path = (
                project_root
                / ".claude"
                / "skills"
                / "generate-report"
                / "templates"
                / "base-email.html"
            )

    template, err = load_template(template_path)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    # Generate report
    html, err = generate_report(digest, analysis_md, template)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    # Save report
    if args.output:
        output_path = Path(args.output)
    else:
        project_root = Path(__file__).parent.parent.parent
        reports_dir = project_root / "reports" / "heyreach"
        reports_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = reports_dir / f"conversation-summary-{date_str}.html"

    output_path.write_text(html)

    period = digest.get("period", {})
    summary = digest.get("summary", {})
    print(f"Report generated:")
    print(f"  Period: {period.get('start')} to {period.get('end')}")
    print(f"  Conversations: {summary.get('with_replies', 0)} with replies")
    print(f"  Meeting signals: {summary.get('meeting_signals', 0)}")
    print(f"  Output: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
