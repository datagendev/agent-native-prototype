#!/usr/bin/env python3
"""
Calculate campaign metrics from conversations.

Step 3 of the HeyReach report pipeline.
Reads: /tmp/heyreach-{date}/campaigns.json
       /tmp/heyreach-{date}/conversations/{campaign_id}.json
Outputs: /tmp/heyreach-{date}/metrics.json

Usage:
    python calculate_metrics.py
    python calculate_metrics.py --input-dir /tmp/heyreach-2026-01-10
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


# Performance benchmarks
BENCHMARKS = {
    "reply": {"low": 10, "high": 20},
    "meeting": {"low": 3, "high": 7},
}

# Keywords indicating meeting bookings
MEETING_KEYWORDS = [
    "book", "calendar", "meeting", "schedule", "call",
    "zoom", "calendly", "available", "time slot",
    "appointment", "confirm", "yes please", "let's talk",
]


def get_output_dir() -> Path:
    """Get today's output directory."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return Path(f"/tmp/heyreach-{date_str}")


def load_campaigns(input_dir: Path) -> tuple[list[dict], str]:
    """Load campaigns from JSON file."""
    campaigns_path = input_dir / "campaigns.json"

    if not campaigns_path.exists():
        return [], f"campaigns.json not found in {input_dir}"

    try:
        campaigns = json.loads(campaigns_path.read_text())
        return campaigns, ""
    except Exception as e:
        return [], f"Failed to load campaigns.json: {e}"


def load_conversations(input_dir: Path, campaign_id: int) -> tuple[list[dict], str]:
    """Load conversations for a campaign."""
    conversations_path = input_dir / "conversations" / f"{campaign_id}.json"

    if not conversations_path.exists():
        return [], ""  # Not an error, just no conversations

    try:
        conversations = json.loads(conversations_path.read_text())
        return conversations, ""
    except Exception as e:
        return [], f"Failed to load conversations for {campaign_id}: {e}"


def analyze_conversations(conversations: list[dict]) -> dict:
    """Analyze conversations to extract engagement metrics."""
    if not conversations:
        return {
            "replies": 0,
            "meetings_detected": 0,
            "avg_messages_per_reply": 0,
            "total_messages": 0,
        }

    replied_convos = 0
    meeting_detected = 0
    total_messages_in_replied = 0
    total_messages = 0

    for conv in conversations:
        messages = conv.get("messages", [])
        total_messages += len(messages)

        # Check if correspondent replied
        has_reply = any(msg.get("sender") == "CORRESPONDENT" for msg in messages)
        if has_reply:
            replied_convos += 1
            total_messages_in_replied += len(messages)

        # Detect meeting keywords in messages
        all_text = " ".join(
            msg.get("body", "").lower()
            for msg in messages
            if msg.get("body")
        )
        if any(kw in all_text for kw in MEETING_KEYWORDS):
            meeting_detected += 1

    avg_messages_per_reply = (
        round(total_messages_in_replied / replied_convos, 1)
        if replied_convos > 0 else 0
    )

    return {
        "replies": replied_convos,
        "meetings_detected": meeting_detected,
        "avg_messages_per_reply": avg_messages_per_reply,
        "total_messages": total_messages,
    }


def calculate_campaign_metrics(campaign: dict, conversation_analytics: dict) -> dict:
    """Calculate metrics for a single campaign."""
    progress = campaign.get("progressStats", {})

    leads_contacted = progress.get("totalUsers", 0)
    finished = progress.get("totalUsersFinished", 0)
    failed = progress.get("totalUsersFailed", 0)
    in_progress = progress.get("totalUsersInProgress", 0)

    replies = conversation_analytics.get("replies", 0)
    meetings_detected = conversation_analytics.get("meetings_detected", 0)
    avg_messages_per_reply = conversation_analytics.get("avg_messages_per_reply", 0)

    # Calculate rates
    reply_rate = round((replies / leads_contacted * 100), 1) if leads_contacted > 0 else 0
    meeting_rate = round((meetings_detected / leads_contacted * 100), 1) if leads_contacted > 0 else 0

    # Determine performance level
    status = campaign.get("status", "UNKNOWN")
    if status == "FINISHED":
        if reply_rate >= BENCHMARKS["reply"]["high"] or meeting_rate >= BENCHMARKS["meeting"]["high"]:
            performance = "excellent"
        elif reply_rate >= BENCHMARKS["reply"]["low"] or meeting_rate >= BENCHMARKS["meeting"]["low"]:
            performance = "good"
        elif replies > 0:
            performance = "underperforming"
        else:
            performance = "no_data"
    elif status == "CANCELED":
        performance = "canceled"
    elif status == "IN_PROGRESS":
        performance = "in_progress"
    else:
        performance = "unknown"

    return {
        "campaign_id": campaign.get("id"),
        "campaign_name": campaign.get("name", "Untitled"),
        "status": status,
        "list_name": campaign.get("linkedInUserListName", ""),
        "created": campaign.get("creationTime", ""),
        # Volume metrics
        "leads_contacted": leads_contacted,
        "finished": finished,
        "failed": failed,
        "in_progress": in_progress,
        # Engagement metrics
        "replies": replies,
        "reply_rate": reply_rate,
        "meetings_detected": meetings_detected,
        "meeting_rate": meeting_rate,
        "avg_messages_per_reply": avg_messages_per_reply,
        # Performance assessment
        "performance": performance,
    }


def generate_insights(campaign_metrics: list[dict]) -> list[dict]:
    """Generate rule-based insights from metrics."""
    insights = []

    underperformers = [c for c in campaign_metrics if c["performance"] == "underperforming"]
    top_performers = [c for c in campaign_metrics if c["performance"] == "excellent"]
    paused = [c for c in campaign_metrics if c["status"] == "PAUSED"]

    # Underperforming campaigns
    for campaign in underperformers:
        if campaign["reply_rate"] < BENCHMARKS["reply"]["low"]:
            insights.append({
                "priority": "high",
                "campaign_id": campaign["campaign_id"],
                "action": f"Pause \"{campaign['campaign_name']}\" immediately",
                "reason": f"Reply rate {campaign['reply_rate']}% is below {BENCHMARKS['reply']['low']}% threshold",
                "recommendation": "Revise messaging to include social intent signals, test on 20 leads before resuming",
            })

    # Paused campaigns
    if paused:
        insights.append({
            "priority": "high",
            "action": f"Review {len(paused)} paused campaign(s)",
            "reason": "Campaigns paused and potentially forgotten",
            "recommendation": "Decide: resume, optimize, or archive",
        })

    # Success replication
    if top_performers:
        best = max(top_performers, key=lambda x: x["reply_rate"], default=None)
        if best:
            insights.append({
                "priority": "medium",
                "campaign_id": best["campaign_id"],
                "action": f"Replicate \"{best['campaign_name']}\" success",
                "reason": f"Campaign achieving {best['reply_rate']}% reply rate and {best['meeting_rate']}% meeting rate",
                "recommendation": "Extract message template and personalization strategy to apply to other campaigns",
            })

    return insights


def save_metrics(metrics: dict, output_dir: Path) -> tuple[Path, str]:
    """Save metrics to JSON file."""
    try:
        output_path = output_dir / "metrics.json"
        output_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
        return output_path, ""
    except Exception as e:
        return Path(), f"save_metrics failed: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate HeyReach campaign metrics")
    parser.add_argument("--input-dir", type=str, help="Input directory with campaigns.json and conversations/")

    args = parser.parse_args()

    # Determine directory
    input_dir = Path(args.input_dir) if args.input_dir else get_output_dir()

    print(f"Calculating metrics from: {input_dir}")

    # Load campaigns
    campaigns, err = load_campaigns(input_dir)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"  Loaded {len(campaigns)} campaigns")

    # Calculate metrics for each campaign
    campaign_metrics = []
    for campaign in campaigns:
        campaign_id = campaign.get("id")
        if not campaign_id:
            continue

        conversations, err = load_conversations(input_dir, campaign_id)
        if err:
            print(f"  WARNING: {err}")
            conversations = []

        analytics = analyze_conversations(conversations)
        metrics = calculate_campaign_metrics(campaign, analytics)
        campaign_metrics.append(metrics)

        print(f"  {campaign_id}: {metrics['replies']} replies, {metrics['reply_rate']}% rate")

    # Generate insights
    insights = generate_insights(campaign_metrics)
    print(f"\n  Generated {len(insights)} insights")

    # Calculate aggregates
    total_leads = sum(c["leads_contacted"] for c in campaign_metrics)
    total_replies = sum(c["replies"] for c in campaign_metrics)
    total_meetings = sum(c["meetings_detected"] for c in campaign_metrics)
    avg_reply_rate = round((total_replies / total_leads * 100), 1) if total_leads > 0 else 0
    avg_meeting_rate = round((total_meetings / total_leads * 100), 1) if total_leads > 0 else 0

    # Build output
    output = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "campaigns_analyzed": len(campaign_metrics),
            "total_leads_contacted": total_leads,
            "total_replies": total_replies,
            "total_meetings_detected": total_meetings,
            "avg_reply_rate": avg_reply_rate,
            "avg_meeting_rate": avg_meeting_rate,
            "by_performance": {
                "excellent": len([c for c in campaign_metrics if c["performance"] == "excellent"]),
                "good": len([c for c in campaign_metrics if c["performance"] == "good"]),
                "underperforming": len([c for c in campaign_metrics if c["performance"] == "underperforming"]),
                "canceled": len([c for c in campaign_metrics if c["performance"] == "canceled"]),
                "in_progress": len([c for c in campaign_metrics if c["performance"] == "in_progress"]),
            },
        },
        "campaigns": campaign_metrics,
        "insights": insights,
        "benchmarks": BENCHMARKS,
    }

    # Save
    output_path, err = save_metrics(output, input_dir)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"\nMetrics saved to: {output_path}")
    print(f"\nSummary:")
    print(f"  Campaigns: {len(campaign_metrics)}")
    print(f"  Total leads: {total_leads}")
    print(f"  Reply rate: {avg_reply_rate}%")
    print(f"  Meeting rate: {avg_meeting_rate}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
