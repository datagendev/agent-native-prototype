#!/usr/bin/env python3
"""
Generate markdown report from metrics.

Step 4 of the HeyReach report pipeline.
Reads: /tmp/heyreach-{date}/metrics.json
Outputs: /tmp/heyreach-{date}/report.md
         reports/heyreach/campaign-report-{date}.md (copy)

Usage:
    python generate_report.py
    python generate_report.py --input-dir /tmp/heyreach-2026-01-10
    python generate_report.py --output reports/custom-report.md
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_output_dir() -> Path:
    """Get today's output directory."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return Path(f"/tmp/heyreach-{date_str}")


def load_metrics(input_dir: Path) -> tuple[dict, str]:
    """Load metrics from JSON file."""
    metrics_path = input_dir / "metrics.json"

    if not metrics_path.exists():
        return {}, f"metrics.json not found in {input_dir}"

    try:
        metrics = json.loads(metrics_path.read_text())
        return metrics, ""
    except Exception as e:
        return {}, f"Failed to load metrics.json: {e}"


def get_performance_emoji(performance: str) -> str:
    """Get emoji for performance level."""
    return {
        "excellent": "🏆",
        "good": "✅",
        "underperforming": "⚠️",
        "canceled": "❌",
        "in_progress": "▶️",
        "no_data": "❓",
        "unknown": "❓",
    }.get(performance, "❓")


def generate_report(metrics: dict) -> str:
    """Generate markdown report from metrics."""
    summary = metrics.get("summary", {})
    campaigns = metrics.get("campaigns", [])
    insights = metrics.get("insights", [])
    benchmarks = metrics.get("benchmarks", {})

    # Summary stats
    total_leads = summary.get("total_leads_contacted", 0)
    total_replies = summary.get("total_replies", 0)
    total_meetings = summary.get("total_meetings_detected", 0)
    avg_reply_rate = summary.get("avg_reply_rate", 0)
    avg_meeting_rate = summary.get("avg_meeting_rate", 0)
    by_perf = summary.get("by_performance", {})

    # Calculate additional stats from campaigns
    total_finished = sum(c.get("finished", 0) for c in campaigns)
    total_failed = sum(c.get("failed", 0) for c in campaigns)
    total_in_progress = sum(c.get("in_progress", 0) for c in campaigns)

    # Avg messages per reply (weighted)
    campaigns_with_replies = [c for c in campaigns if c.get("replies", 0) > 0]
    if campaigns_with_replies:
        total_weighted = sum(
            c["avg_messages_per_reply"] * c["replies"]
            for c in campaigns_with_replies
        )
        overall_avg_messages = round(total_weighted / total_replies, 1) if total_replies > 0 else 0
    else:
        overall_avg_messages = 0

    # Build report
    report = f"""# HeyReach Campaign Performance Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Campaigns Analyzed**: {len(campaigns)}

---

## Executive Summary

### Volume Metrics
- **Connection Requests Sent**: {total_leads:,}
- **Successfully Completed**: {total_finished:,}
- **Failed**: {total_failed:,}
- **Still In Progress**: {total_in_progress:,}

### Engagement Metrics
- **Reply Rate**: {avg_reply_rate:.1f}% ({total_replies} replies)
- **Avg Messages per Replied Lead**: {overall_avg_messages} messages
- **Meeting Detection Rate**: {avg_meeting_rate:.1f}% ({total_meetings} detected)

### Campaign Performance Distribution
- 🏆 Excellent: {by_perf.get('excellent', 0)} campaigns
- ✅ Good: {by_perf.get('good', 0)} campaigns
- ⚠️ Underperforming: {by_perf.get('underperforming', 0)} campaigns
- ❌ Canceled: {by_perf.get('canceled', 0)} campaigns
- ▶️ In Progress: {by_perf.get('in_progress', 0)} campaigns

---

## Campaigns Needing Attention
"""

    # Underperformers and canceled
    canceled = [c for c in campaigns if c.get("status") == "CANCELED"]
    underperformers = [c for c in campaigns if c.get("performance") == "underperforming"]

    if canceled:
        for c in canceled:
            emoji = get_performance_emoji(c.get("performance", ""))
            report += f"""
### Campaign: "{c['campaign_name']}" {emoji}
- **Status**: {c['status']}
- **Leads**: {c['leads_contacted']} total
- **Progress**: {c['in_progress']} in progress, {c['failed']} failed
- **List**: {c.get('list_name', 'N/A')}
- **Recommendation**: Review cancellation reason, decide whether to resume or archive
"""

    if underperformers:
        for c in underperformers:
            emoji = get_performance_emoji(c.get("performance", ""))
            reply_threshold = benchmarks.get("reply", {}).get("low", 10)
            report += f"""
### Campaign: "{c['campaign_name']}" {emoji}
- **Status**: {c['status']}
- **Connection Requests**: {c['leads_contacted']}
- **Reply Rate**: {c['reply_rate']}% ({c['replies']} replies)
- **Meeting Rate**: {c['meeting_rate']}% ({c['meetings_detected']} detected)
- **Recommendation**: Reply rate below {reply_threshold}% - revise messaging and personalization
"""

    if not canceled and not underperformers:
        report += "\n*No campaigns currently need immediate attention* ✅\n"

    # Top performers
    report += "\n---\n\n## Top Performing Campaigns\n"

    finished = [c for c in campaigns if c.get("status") == "FINISHED"]
    if finished:
        sorted_finished = sorted(finished, key=lambda x: x.get("reply_rate", 0), reverse=True)
        for i, c in enumerate(sorted_finished[:3], 1):
            emoji = get_performance_emoji(c.get("performance", ""))
            created = c.get("created", "")[:10] if c.get("created") else "N/A"
            report += f"""
### {i}. "{c['campaign_name']}" {emoji}
- **Connection Requests Sent**: {c['leads_contacted']}
- **Reply Rate**: {c['reply_rate']}% ({c['replies']} replies)
- **Avg Messages per Reply**: {c['avg_messages_per_reply']} messages
- **Meeting Rate**: {c['meeting_rate']}% ({c['meetings_detected']} detected)
- **List**: {c.get('list_name', 'N/A')}
- **Created**: {created}
"""
    else:
        report += "\n*No finished campaigns*\n"

    # All campaigns table
    report += """
---

## All Campaigns Overview

| Campaign Name | Status | Requests | Replies | Reply % | Avg Msgs | Meetings | Rating |
|--------------|--------|----------|---------|---------|----------|----------|--------|
"""

    sorted_campaigns = sorted(campaigns, key=lambda x: x.get("reply_rate", 0), reverse=True)
    for c in sorted_campaigns:
        emoji = get_performance_emoji(c.get("performance", ""))
        report += f"| {c['campaign_name']} | {c['status']} | {c['leads_contacted']} | {c['replies']} | {c['reply_rate']}% | {c['avg_messages_per_reply']} | {c['meetings_detected']} | {emoji} |\n"

    # Recommendations
    report += "\n---\n\n## Recommendations\n"

    if insights:
        high_priority = [i for i in insights if i.get("priority") == "high"]
        medium_priority = [i for i in insights if i.get("priority") == "medium"]

        if high_priority:
            report += "\n### High Priority\n"
            for i, insight in enumerate(high_priority, 1):
                report += f"""
{i}. **{insight['action']}**
   - Reason: {insight['reason']}
   - Recommendation: {insight['recommendation']}
"""

        if medium_priority:
            report += "\n### Medium Priority\n"
            for i, insight in enumerate(medium_priority, len(high_priority) + 1):
                report += f"""
{i}. **{insight['action']}**
   - Reason: {insight['reason']}
   - Recommendation: {insight['recommendation']}
"""
    else:
        report += "\n*All campaigns performing within acceptable ranges*\n"

    # Action checklist
    report += "\n---\n\n## Action Checklist\n\n"

    for insight in insights[:5]:
        report += f"- [ ] {insight['action']}\n"

    if len(insights) > 5:
        report += f"- [ ] Review {len(insights) - 5} additional recommendations above\n"

    next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    report += f"""
---

*Report generated by DataGen HeyReach Campaign Analyzer*
*Next scheduled report: {next_week}*
"""

    return report


def save_report(report: str, input_dir: Path, output_path: Path | None) -> tuple[Path, str]:
    """Save report to files."""
    try:
        # Save to /tmp/
        tmp_path = input_dir / "report.md"
        tmp_path.write_text(report)

        # Determine final output path
        if output_path:
            final_path = output_path
        else:
            reports_dir = Path(__file__).parent.parent.parent / "reports" / "heyreach"
            reports_dir.mkdir(parents=True, exist_ok=True)
            date_str = datetime.now().strftime("%Y-%m-%d")
            final_path = reports_dir / f"campaign-report-{date_str}.md"

        # Copy to final location
        shutil.copy(tmp_path, final_path)

        return final_path, ""

    except Exception as e:
        return Path(), f"save_report failed: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate HeyReach campaign report")
    parser.add_argument("--input-dir", type=str, help="Input directory with metrics.json")
    parser.add_argument("--output", type=str, help="Custom output file path")

    args = parser.parse_args()

    # Determine directories
    input_dir = Path(args.input_dir) if args.input_dir else get_output_dir()
    output_path = Path(args.output) if args.output else None

    print(f"Generating report from: {input_dir}")

    # Load metrics
    metrics, err = load_metrics(input_dir)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"  Loaded metrics for {len(metrics.get('campaigns', []))} campaigns")

    # Generate report
    report = generate_report(metrics)

    # Save
    final_path, err = save_report(report, input_dir, output_path)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"\nReport saved to:")
    print(f"  Temp: {input_dir / 'report.md'}")
    print(f"  Final: {final_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
