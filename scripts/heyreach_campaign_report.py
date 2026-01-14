#!/usr/bin/env python3
"""
HeyReach Campaign Report Generator

Generates comprehensive performance reports for HeyReach campaigns with AI-powered
insights and recommendations.

Usage:
    python heyreach_campaign_report.py
    python heyreach_campaign_report.py --campaigns 12345,67890
    python heyreach_campaign_report.py --status IN_PROGRESS
    python heyreach_campaign_report.py --keyword "VPs Engineering"
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from datagen_sdk import DatagenClient

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Verify API key
if not os.getenv("DATAGEN_API_KEY"):
    raise RuntimeError("DATAGEN_API_KEY not set")

client = DatagenClient()

# Performance benchmarks
BENCHMARKS = {
    "acceptance": {"low": 40, "high": 60},
    "reply": {"low": 10, "high": 20},
    "meeting": {"low": 3, "high": 7}
}


def get_campaigns(
    campaign_ids: Optional[List[int]] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Fetch campaigns from HeyReach"""

    print("📥 Fetching campaigns from HeyReach...")

    # Build filters
    statuses = [status] if status else []
    account_ids = []  # Empty = all accounts

    result = client.execute_tool(
        "mcp_Heyreach_get_all_campaigns",
        {
            "statuses": statuses,
            "accountIds": account_ids,
            "keyword": keyword or "",
            "limit": 100,
            "offset": 0
        }
    )

    # Parse response - HeyReach returns list with one object containing items
    if isinstance(result, list) and len(result) > 0:
        campaigns = result[0].get("items", [])
    else:
        campaigns = result.get("campaigns", []) if isinstance(result, dict) else []

    # Filter by specific campaign IDs if provided
    if campaign_ids:
        campaigns = [c for c in campaigns if c.get("id") in campaign_ids]

    print(f"✓ Found {len(campaigns)} campaigns")
    return campaigns


def get_campaign_conversations(
    campaign_ids: List[int],
    account_ids: List[int]
) -> Dict[int, List[Dict[str, Any]]]:
    """Fetch conversations for campaigns to get real engagement data"""

    print(f"💬 Fetching conversations for {len(campaign_ids)} campaigns...")

    conversations_by_campaign = {}

    for campaign_id in campaign_ids:
        try:
            result = client.execute_tool(
                "mcp_Heyreach_get_conversations_v2",
                {
                    "linkedInAccountIds": account_ids if account_ids else [],
                    "campaignIds": [campaign_id],
                    "limit": 100,
                    "offset": 0,
                    "searchString": "",
                    "seen": None,
                    "leadLinkedInId": None,
                    "leadProfileUrl": None
                }
            )

            # Parse response
            if isinstance(result, list) and len(result) > 0:
                conversations = result[0].get("items", []) if isinstance(result[0], dict) else result
            elif isinstance(result, dict):
                conversations = result.get("items", result.get("conversations", []))
            else:
                conversations = []

            conversations_by_campaign[campaign_id] = conversations
            print(f"  ✓ Campaign {campaign_id}: {len(conversations)} conversations")

        except Exception as e:
            print(f"  ⚠️ Campaign {campaign_id}: Failed to fetch conversations - {e}")
            conversations_by_campaign[campaign_id] = []

    total_conversations = sum(len(convs) for convs in conversations_by_campaign.values())
    print(f"✓ Fetched {total_conversations} total conversations")

    return conversations_by_campaign


def analyze_conversations(conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze conversations to extract engagement counts

    Note: Reply rate will be calculated as replies / connection requests sent,
    not replies / conversations (since we don't have acceptance data)
    """

    if not conversations:
        return {
            "replies": 0,
            "meetings_booked": 0,
            "avg_messages_per_reply": 0
        }

    replied_convos = 0
    meeting_booked = 0
    total_messages_in_replied_convos = 0

    # Keywords that indicate meeting booking (crude detection)
    # TODO: Improve with webhook tracking or better NLP
    meeting_keywords = [
        "book", "calendar", "meeting", "schedule", "call",
        "zoom", "calendly", "available", "time slot",
        "appointment", "confirm", "yes please", "let's talk"
    ]

    for conv in conversations:
        messages = conv.get("messages", [])

        # Check if correspondent replied (they sent at least one message)
        has_reply = any(msg.get("sender") == "CORRESPONDENT" for msg in messages)
        if has_reply:
            replied_convos += 1
            total_messages_in_replied_convos += len(messages)

        # Check for meeting bookings in message content
        all_text = " ".join(msg.get("body", "").lower() for msg in messages if msg.get("body"))
        if any(keyword in all_text for keyword in meeting_keywords):
            meeting_booked += 1

    # Calculate average messages per replied lead (engagement depth)
    avg_messages_per_reply = round(total_messages_in_replied_convos / replied_convos, 1) if replied_convos > 0 else 0

    return {
        "replies": replied_convos,
        "meetings_booked": meeting_booked,
        "avg_messages_per_reply": avg_messages_per_reply
    }


def analyze_campaign_performance(
    campaign: Dict[str, Any],
    conversation_analytics: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze single campaign performance using conversation data"""

    # Get progressStats from campaign data
    progress = campaign.get("progressStats", {})

    # Extract metrics from progressStats
    leads_contacted = progress.get("totalUsers", 0)
    finished = progress.get("totalUsersFinished", 0)
    failed = progress.get("totalUsersFailed", 0)
    in_progress = progress.get("totalUsersInProgress", 0)

    # Get real engagement metrics from conversations
    replies = conversation_analytics.get("replies", 0)
    meetings_booked = conversation_analytics.get("meetings_booked", 0)
    avg_messages_per_reply = conversation_analytics.get("avg_messages_per_reply", 0)

    # Calculate reply rate as: replies / connection requests sent
    # Note: We don't have acceptance data (would need CONNECTION_REQUEST_ACCEPTED webhook)
    reply_rate = round((replies / leads_contacted * 100), 1) if leads_contacted > 0 else 0
    meeting_rate = round((meetings_booked / leads_contacted * 100), 1) if leads_contacted > 0 else 0

    # Determine performance level based on reply rate and meeting rate
    # Use industry benchmarks: reply rate >10% good, >20% excellent
    if campaign.get("status") == "FINISHED":
        if reply_rate >= 20 or meeting_rate >= 5:
            performance = "excellent"
            emoji = "🏆"
        elif reply_rate >= 10 or meeting_rate >= 3:
            performance = "good"
            emoji = "✅"
        elif replies > 0:
            performance = "underperforming"
            emoji = "⚠️"
        else:
            performance = "no_data"
            emoji = "❓"
    elif campaign.get("status") == "CANCELED":
        performance = "canceled"
        emoji = "❌"
    elif campaign.get("status") == "IN_PROGRESS":
        performance = "in_progress"
        emoji = "▶️"
    else:
        performance = "unknown"
        emoji = "❓"

    return {
        "campaign_id": campaign.get("id"),
        "campaign_name": campaign.get("name", "Untitled"),
        "status": campaign.get("status", "UNKNOWN"),
        "leads_contacted": leads_contacted,
        "finished": finished,
        "failed": failed,
        "in_progress": in_progress,
        "replies": replies,
        "reply_rate": reply_rate,
        "meetings_booked": meetings_booked,
        "meeting_rate": meeting_rate,
        "avg_messages_per_reply": avg_messages_per_reply,
        "performance": performance,
        "emoji": emoji,
        "created": campaign.get("creationTime", ""),
        "list_name": campaign.get("linkedInUserListName", "")
    }


def generate_insights(analyzed_campaigns: List[Dict[str, Any]]) -> List[str]:
    """Generate AI-powered insights and recommendations"""

    insights = []

    # Find patterns
    underperformers = [c for c in analyzed_campaigns if c["performance"] == "underperforming"]
    top_performers = [c for c in analyzed_campaigns if c["performance"] == "excellent"]
    paused = [c for c in analyzed_campaigns if c["status"] == "PAUSED"]

    # Critical issues first - based on reply rate
    if underperformers:
        for campaign in underperformers:
            if campaign["reply_rate"] < BENCHMARKS["reply"]["low"]:
                insights.append({
                    "priority": "high",
                    "action": f"Pause \"{campaign['campaign_name']}\" immediately",
                    "reason": f"Reply rate {campaign['reply_rate']}% is below {BENCHMARKS['reply']['low']}% threshold",
                    "recommendation": "Revise messaging to include social intent signals, test on 20 leads before resuming"
                })

    # Paused campaigns
    if paused:
        insights.append({
            "priority": "high",
            "action": f"Review {len(paused)} paused campaign(s)",
            "reason": "Campaigns paused and potentially forgotten",
            "recommendation": "Decide: resume, optimize, or archive"
        })

    # Success replication - based on reply rate and meeting rate
    if top_performers:
        best_reply = max(top_performers, key=lambda x: x["reply_rate"], default=None)
        if best_reply:
            insights.append({
                "priority": "medium",
                "action": f"Replicate \"{best_reply['campaign_name']}\" success",
                "reason": f"Campaign achieving {best_reply['reply_rate']}% reply rate and {best_reply['meeting_rate']}% meeting rate",
                "recommendation": "Extract message template and personalization strategy to apply to other campaigns"
            })

    return insights


def generate_report(
    campaigns: List[Dict[str, Any]],
    analyzed_campaigns: List[Dict[str, Any]],
    insights: List[str],
    days: int
) -> str:
    """Generate markdown report"""

    # Calculate summary stats
    total_leads = sum(c["leads_contacted"] for c in analyzed_campaigns)
    total_finished = sum(c["finished"] for c in analyzed_campaigns)
    total_failed = sum(c["failed"] for c in analyzed_campaigns)
    total_in_progress = sum(c["in_progress"] for c in analyzed_campaigns)
    total_replies = sum(c["replies"] for c in analyzed_campaigns)
    total_meetings = sum(c["meetings_booked"] for c in analyzed_campaigns)

    # Calculate aggregated rates (based on connection requests sent, not accepted)
    avg_reply_rate = (total_replies / total_leads * 100) if total_leads > 0 else 0
    avg_meeting_rate = (total_meetings / total_leads * 100) if total_leads > 0 else 0

    # Calculate overall avg messages per replied lead
    campaigns_with_replies = [c for c in analyzed_campaigns if c["replies"] > 0]
    if campaigns_with_replies:
        total_avg_messages = sum(c["avg_messages_per_reply"] * c["replies"] for c in campaigns_with_replies)
        overall_avg_messages = round(total_avg_messages / total_replies, 1) if total_replies > 0 else 0
    else:
        overall_avg_messages = 0

    # Count by performance
    underperformers = [c for c in analyzed_campaigns if c["performance"] == "underperforming"]
    good_performers = [c for c in analyzed_campaigns if c["performance"] == "good"]
    top_performers = [c for c in analyzed_campaigns if c["performance"] == "excellent"]

    # Generate report
    report = f"""# HeyReach Campaign Performance Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M %Z')}
**Campaigns Analyzed**: {len(analyzed_campaigns)}

---

## 📊 Executive Summary

### Volume Metrics
- **Connection Requests Sent**: {total_leads:,}
- **Successfully Completed**: {total_finished:,}
- **Failed**: {total_failed:,}
- **Still In Progress**: {total_in_progress:,}

### Engagement Metrics (as % of connection requests sent)
- **Reply Rate**: {avg_reply_rate:.1f}% ({total_replies} replies)
- **Avg Messages per Replied Lead**: {overall_avg_messages} messages
- **Meeting Booking Rate**: {avg_meeting_rate:.1f}% ({total_meetings} meetings booked)

**Note**: Acceptance rate requires CONNECTION_REQUEST_ACCEPTED webhook tracking

### Campaign Status Distribution
- ✅ Finished: {len([c for c in analyzed_campaigns if c['status'] == 'FINISHED'])} campaigns
- ❌ Canceled: {len([c for c in analyzed_campaigns if c['status'] == 'CANCELED'])} campaigns
- ▶️ In Progress: {len([c for c in analyzed_campaigns if c['status'] == 'IN_PROGRESS'])} campaigns

---

## 🚨 Campaigns Needing Attention
"""

    # Underperformers and canceled
    canceled = [c for c in analyzed_campaigns if c["status"] == "CANCELED"]
    if canceled:
        for campaign in canceled:
            report += f"""
### Campaign: "{campaign['campaign_name']}" {campaign['emoji']}
- **Status**: {campaign['status']}
- **Leads**: {campaign['leads_contacted']} total
- **Progress**: {campaign['in_progress']} in progress, {campaign['failed']} failed
- **List**: {campaign['list_name']}
- **Recommendation**: Review cancellation reason, decide whether to resume or archive
"""

    if underperformers:
        for campaign in underperformers:
            report += f"""
### Campaign: "{campaign['campaign_name']}" {campaign['emoji']}
- **Status**: {campaign['status']}
- **Connection Requests**: {campaign['leads_contacted']}
- **Reply Rate**: {campaign['reply_rate']}% ({campaign['replies']} replies)
- **Meeting Rate**: {campaign['meeting_rate']}% ({campaign['meetings_booked']} meetings)
- **Recommendation**: Reply rate below {BENCHMARKS['reply']['low']}% - revise messaging and personalization
"""

    if not canceled and not underperformers:
        report += "\n*No campaigns currently need immediate attention* ✅\n"

    # Top Performers
    report += "\n---\n\n## 🏆 Top Performing Campaigns\n"

    finished = [c for c in analyzed_campaigns if c["status"] == "FINISHED"]
    if finished:
        sorted_finished = sorted(finished, key=lambda x: x["reply_rate"], reverse=True)
        for i, campaign in enumerate(sorted_finished[:3], 1):
            report += f"""
### {i}. "{campaign['campaign_name']}" {campaign['emoji']}
- **Connection Requests Sent**: {campaign['leads_contacted']}
- **Reply Rate**: {campaign['reply_rate']}% ({campaign['replies']} replies)
- **Avg Messages per Reply**: {campaign['avg_messages_per_reply']} messages
- **Meeting Rate**: {campaign['meeting_rate']}% ({campaign['meetings_booked']} meetings)
- **List**: {campaign['list_name']}
- **Created**: {campaign['created'][:10]}
"""
    else:
        report += "\n*No finished campaigns*\n"

    # All campaigns table
    report += """
---

## 📈 All Campaigns Overview

| Campaign Name | Status | Requests | Replies | Reply % | Avg Msgs | Meetings | Rating |
|--------------|--------|----------|---------|---------|----------|----------|--------|
"""

    sorted_campaigns = sorted(analyzed_campaigns, key=lambda x: x["reply_rate"], reverse=True)
    for campaign in sorted_campaigns:
        report += f"| {campaign['campaign_name']} | {campaign['status']} | {campaign['leads_contacted']} | {campaign['replies']} | {campaign['reply_rate']}% | {campaign['avg_messages_per_reply']} | {campaign['meetings_booked']} | {campaign['emoji']} |\n"

    # Recommendations
    report += "\n---\n\n## 💡 Recommendations\n"

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
    report += """
---

## 📋 Action Checklist

"""

    for insight in insights[:5]:  # Top 5 actions
        report += f"- [ ] {insight['action']}\n"

    if len(insights) > 5:
        report += f"- [ ] Review {len(insights) - 5} additional recommendations above\n"

    report += """
---

*Report generated by DataGen HeyReach Campaign Analyzer*
*Next scheduled report: {next_week}*
""".format(next_week=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))

    return report


def main():
    parser = argparse.ArgumentParser(description="Generate HeyReach campaign performance report")
    parser.add_argument("--campaigns", type=str, help="Comma-separated campaign IDs")
    parser.add_argument("--status", type=str, choices=["DRAFT", "IN_PROGRESS", "PAUSED", "FINISHED", "CANCELED", "FAILED", "STARTING"], help="Filter by campaign status")
    parser.add_argument("--keyword", type=str, help="Search campaigns by keyword")
    parser.add_argument("--days", type=int, default=30, help="Date range for stats (default: 30 days)")
    parser.add_argument("--output", type=str, help="Output file path")

    args = parser.parse_args()

    # Parse campaign IDs
    campaign_ids = None
    if args.campaigns:
        campaign_ids = [int(x.strip()) for x in args.campaigns.split(",")]

    print("="*80)
    print("HEYREACH CAMPAIGN PERFORMANCE REPORT")
    print("="*80)

    # Fetch campaigns
    campaigns = get_campaigns(
        campaign_ids=campaign_ids,
        status=args.status,
        keyword=args.keyword
    )

    if not campaigns:
        print("\n❌ No campaigns found matching your criteria")
        sys.exit(1)

    # Get conversations for all campaigns
    all_campaign_ids = [c.get("id") for c in campaigns]
    all_account_ids = []  # Empty = all accounts

    conversations_by_campaign = get_campaign_conversations(
        campaign_ids=all_campaign_ids,
        account_ids=all_account_ids
    )

    # Analyze each campaign
    print("\n🔍 Analyzing campaign performance...")
    analyzed_campaigns = []
    for campaign in campaigns:
        campaign_id = campaign.get("id")
        conversations = conversations_by_campaign.get(campaign_id, [])
        conversation_analytics = analyze_conversations(conversations)

        analyzed = analyze_campaign_performance(campaign, conversation_analytics)
        analyzed_campaigns.append(analyzed)

    print(f"✓ Analyzed {len(analyzed_campaigns)} campaigns")

    # Generate insights
    print("\n💡 Generating AI insights...")
    insights = generate_insights(analyzed_campaigns)
    print(f"✓ Generated {len(insights)} recommendations")

    # Generate report
    print("\n📝 Creating report...")
    report = generate_report(campaigns, analyzed_campaigns, insights, args.days)

    # Save report
    if args.output:
        output_path = Path(args.output)
    else:
        reports_dir = Path(__file__).parent.parent / "reports" / "heyreach"
        reports_dir.mkdir(parents=True, exist_ok=True)
        output_path = reports_dir / f"campaign-report-{datetime.now().strftime('%Y-%m-%d')}.md"

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"✓ Report saved to: {output_path}")

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    underperformers = [c for c in analyzed_campaigns if c["performance"] == "underperforming"]
    top_performers = [c for c in analyzed_campaigns if c["performance"] == "excellent"]

    print(f"\n📊 {len(analyzed_campaigns)} campaigns analyzed")
    print(f"🚨 {len(underperformers)} campaigns need attention")
    print(f"🏆 {len(top_performers)} top performers")
    print(f"💡 {len(insights)} recommendations generated")

    print(f"\n📄 Full report: {output_path}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
