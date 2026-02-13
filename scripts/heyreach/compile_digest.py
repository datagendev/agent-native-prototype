#!/usr/bin/env python3
"""
Compile conversation data into a structured digest for Claude analysis.

Step 3 of the conversation summary pipeline.
Reads: /tmp/heyreach-summary-{date}/conversations.json
       /tmp/heyreach-summary-{date}/threads/ (optional, used if available)
Outputs: /tmp/heyreach-summary-{date}/digest.json

Usage:
    python compile_digest.py
    python compile_digest.py --input-dir /tmp/heyreach-summary-2026-02-13
    python compile_digest.py --days 14
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MEETING_KEYWORDS = [
    "book",
    "calendar",
    "meeting",
    "schedule",
    "call",
    "zoom",
    "calendly",
    "available",
    "time slot",
    "appointment",
    "confirm",
    "let's talk",
    "lets talk",
    "demo",
    "walkthrough",
    "15 min",
    "30 min",
    "quick chat",
]


def get_output_dir() -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d")
    return Path(f"/tmp/heyreach-summary-{date_str}")


def parse_date(date_str: str) -> datetime | None:
    """Parse ISO date string, return None if unparseable."""
    if not date_str:
        return None
    try:
        # Handle various ISO formats
        cleaned = date_str.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except (ValueError, TypeError):
        return None


def has_meeting_signal(text: str) -> bool:
    """Check if message text contains meeting-related keywords."""
    lower = text.lower()
    return any(kw in lower for kw in MEETING_KEYWORDS)


def extract_person_info(conversation: dict) -> dict:
    """Extract person name and details from conversation data."""
    # HeyReach API returns correspondentProfile with lead info
    cp = conversation.get("correspondentProfile", {}) or {}
    lead = conversation.get("lead", {}) or {}
    correspondent = conversation.get("correspondent", {}) or {}

    first = cp.get("firstName", "")
    last = cp.get("lastName", "")
    full_from_cp = f"{first} {last}".strip() if (first or last) else ""

    name = (
        full_from_cp
        or lead.get("fullName")
        or lead.get("name")
        or correspondent.get("fullName")
        or conversation.get("leadName")
        or "Unknown"
    )

    headline = (
        cp.get("headline")
        or cp.get("summary")
        or lead.get("headline")
        or lead.get("title")
        or ""
    )

    linkedin_url = (
        cp.get("profileUrl")
        or lead.get("linkedInUrl")
        or lead.get("profileUrl")
        or ""
    )

    company = cp.get("companyName") or lead.get("companyName") or ""
    position = cp.get("position") or lead.get("position") or ""

    return {
        "name": name,
        "headline": headline,
        "linkedin_url": linkedin_url,
        "company": company,
        "position": position,
    }


def process_conversation(
    conversation: dict, cutoff: datetime, threads_dir: Path | None
) -> dict | None:
    """
    Process a single conversation into digest format.

    Returns None if conversation has no activity in the date range.
    """
    conversation_id = conversation.get("conversationId", conversation.get("id", ""))

    # Try to load enriched thread data if available
    thread_data = None
    if threads_dir and conversation_id:
        thread_path = threads_dir / f"{conversation_id}.json"
        if thread_path.exists():
            try:
                thread_data = json.loads(thread_path.read_text())
            except Exception:
                pass

    # Use thread messages if available, otherwise conversation messages
    messages = []
    raw_messages = (
        thread_data.get("messages", []) if thread_data else conversation.get("messages", [])
    )

    for msg in raw_messages:
        # HeyReach API uses createdAt; older data may use sentAt
        date_str = msg.get("createdAt", msg.get("sentAt", msg.get("sent_at", "")))
        sent_at = parse_date(date_str)
        messages.append(
            {
                "sender": msg.get("sender", "UNKNOWN"),
                "body": msg.get("body", msg.get("text", "")),
                "date": sent_at.isoformat() if sent_at else "",
                "_parsed_date": sent_at,
            }
        )

    # Filter to messages within date range
    recent_messages = [
        m
        for m in messages
        if m["_parsed_date"] and m["_parsed_date"].replace(tzinfo=None) >= cutoff.replace(tzinfo=None)
    ]

    if not recent_messages:
        # Check if ANY message is recent (conversation might span the period)
        all_dates = [m["_parsed_date"] for m in messages if m["_parsed_date"]]
        if not all_dates or max(d.replace(tzinfo=None) for d in all_dates) < cutoff.replace(tzinfo=None):
            return None

    # Use all messages for context (not just recent ones)
    display_messages = [
        {"sender": m["sender"], "body": m["body"], "date": m["date"]}
        for m in messages
        if m["body"]  # Skip empty messages
    ]

    if not display_messages:
        return None

    # Extract person info
    person = extract_person_info(conversation)

    # Calculate metrics
    correspondent_msgs = [m for m in display_messages if m["sender"] == "CORRESPONDENT"]
    my_msgs = [m for m in display_messages if m["sender"] == "ME"]

    # Check for meeting signals in correspondent messages
    meeting_signal = any(has_meeting_signal(m["body"]) for m in correspondent_msgs)

    # Last activity date
    all_dates = [m["_parsed_date"] for m in messages if m["_parsed_date"]]
    last_activity = max(all_dates).isoformat() if all_dates else ""

    return {
        "person": person,
        "campaign_name": conversation.get("_campaign_name", ""),
        "campaign_id": conversation.get("_campaign_id", ""),
        "messages": display_messages,
        "message_count": len(display_messages),
        "my_message_count": len(my_msgs),
        "reply_count": len(correspondent_msgs),
        "last_activity": last_activity,
        "has_meeting_signal": meeting_signal,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile HeyReach conversation digest"
    )
    parser.add_argument("--input-dir", type=str, help="Input directory")
    parser.add_argument(
        "--days", type=int, default=14, help="Look back N days (default: 14)"
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir) if args.input_dir else get_output_dir()
    conversations_path = input_dir / "conversations.json"

    if not conversations_path.exists():
        print(f"ERROR: {conversations_path} not found", file=sys.stderr)
        return 1

    conversations = json.loads(conversations_path.read_text())
    print(f"Loaded {len(conversations)} conversations")

    cutoff = datetime.now() - timedelta(days=args.days)
    threads_dir = input_dir / "threads" if (input_dir / "threads").exists() else None

    # Process each conversation
    digest_entries = []
    skipped = 0

    for conv in conversations:
        entry = process_conversation(conv, cutoff, threads_dir)
        if entry:
            digest_entries.append(entry)
        else:
            skipped += 1

    # Sort by last activity (most recent first)
    digest_entries.sort(key=lambda x: x.get("last_activity", ""), reverse=True)

    # Separate conversations with replies from outreach-only
    with_replies = [e for e in digest_entries if e["reply_count"] > 0]
    outreach_only = [e for e in digest_entries if e["reply_count"] == 0]

    # Collect unique campaigns
    campaigns = list({e["campaign_name"] for e in digest_entries if e["campaign_name"]})

    # Build digest
    digest = {
        "generated_at": datetime.now().isoformat(),
        "period": {
            "start": cutoff.strftime("%Y-%m-%d"),
            "end": datetime.now().strftime("%Y-%m-%d"),
        },
        "summary": {
            "total_conversations": len(digest_entries),
            "with_replies": len(with_replies),
            "outreach_only": len(outreach_only),
            "total_messages": sum(e["message_count"] for e in digest_entries),
            "total_replies": sum(e["reply_count"] for e in digest_entries),
            "meeting_signals": sum(1 for e in digest_entries if e["has_meeting_signal"]),
            "campaigns_active": len(campaigns),
            "campaigns": campaigns,
        },
        "conversations_with_replies": with_replies,
        "outreach_only_count": len(outreach_only),
    }

    # Save digest
    digest_path = input_dir / "digest.json"
    digest_path.write_text(json.dumps(digest, indent=2, ensure_ascii=False))

    print(f"\nDigest compiled:")
    print(f"  Period: {digest['period']['start']} to {digest['period']['end']}")
    print(f"  Conversations: {len(digest_entries)} ({skipped} skipped - no recent activity)")
    print(f"  With replies: {len(with_replies)}")
    print(f"  Meeting signals: {digest['summary']['meeting_signals']}")
    print(f"  Active campaigns: {len(campaigns)}")
    print(f"  Output: {digest_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
