#!/usr/bin/env python3
"""
Generate personalized outreach messages for campaign prospects.
Based on the Lohit template that worked successfully.
"""

import os
import sys
import json
import csv
from datetime import datetime, timezone
from datagen_sdk import DatagenClient

# Verify API key
DATAGEN_API_KEY = os.getenv("DATAGEN_API_KEY")
if not DATAGEN_API_KEY:
    print("ERROR: DATAGEN_API_KEY not found")
    print("Please run: export DATAGEN_API_KEY=your_key")
    sys.exit(1)

# Initialize DataGen client
client = DatagenClient()

# Campaign configuration
CAMPAIGN_TABLE = "campaign_jordan_crawford_gtm_session_link_requests"
PROJECT_ID = "blue-tree-25780810"
BRANCH_ID = "br-cool-leaf-afau0ra8"
DATABASE = "neondb"

# Message template (based on Lohit's successful conversation)
MESSAGE_TEMPLATE = """Hi {first_name},

Would you be interested in learning Claude Code from us? We're offering free 1:1 tutorials to show people how to use it for GTM work. It helps us understand how to better design our onboarding too. Let me know if interested.

Yu-Sheng"""


def extract_first_name(full_name):
    """Extract first name from full name, handling emojis."""
    if not full_name:
        return "there"

    # Remove common emojis
    clean_name = full_name.replace("🦾", "").replace("👨‍💻", "").replace("🪄", "").strip()

    # Split and get first part
    parts = clean_name.split()
    if parts:
        return parts[0]
    return "there"


def fetch_campaign_prospects():
    """Fetch all pending prospects from the campaign."""

    query = f"""
    SELECT
        ct.id as campaign_entry_id,
        p.id as prospect_id,
        p.name,
        p.linkedin_url,
        p.headline,
        p.company,
        ct.comment_text
    FROM {CAMPAIGN_TABLE} ct
    JOIN prospects p ON p.id = ct.prospect_id
    WHERE ct.status = 'pending'
    ORDER BY ct.id;
    """

    print(f"Fetching prospects from {CAMPAIGN_TABLE}...")

    result = client.execute_tool(
        "mcp_Neon_run_sql",
        {
            "params": {
                "projectId": PROJECT_ID,
                "branchId": BRANCH_ID,
                "databaseName": DATABASE,
                "sql": query
            }
        }
    )

    # Parse result - it returns array of arrays
    if result and len(result) > 0:
        prospects = result[0]  # Get first element which contains the results
        print(f"✅ Found {len(prospects)} pending prospects\n")
        return prospects

    return []


def generate_messages(prospects):
    """Generate personalized messages for all prospects."""

    messages = []

    for prospect in prospects:
        first_name = extract_first_name(prospect.get("name", ""))

        message_data = {
            "prospect_id": prospect.get("prospect_id"),
            "campaign_entry_id": prospect.get("campaign_entry_id"),
            "name": prospect.get("name"),
            "first_name": first_name,
            "linkedin_url": prospect.get("linkedin_url"),
            "headline": prospect.get("headline", ""),
            "company": prospect.get("company", ""),
            "comment_text": prospect.get("comment_text", ""),
            "message": MESSAGE_TEMPLATE.format(first_name=first_name),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        messages.append(message_data)

    return messages


def save_to_json(messages, filename):
    """Save messages to JSON file."""

    # Get script directory and construct absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    linkedin_messages_dir = os.path.join(os.path.dirname(script_dir), "linkedin-messages")
    filepath = os.path.join(linkedin_messages_dir, filename)

    with open(filepath, 'w') as f:
        json.dump(messages, f, indent=2)

    print(f"✅ Saved {len(messages)} messages to {filepath}")


def save_to_csv(messages, filename):
    """Save messages to CSV for HeyReach upload."""

    # Get script directory and construct absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    linkedin_messages_dir = os.path.join(os.path.dirname(script_dir), "linkedin-messages")
    filepath = os.path.join(linkedin_messages_dir, filename)

    # HeyReach CSV format
    fieldnames = [
        "Full Name",
        "First Name",
        "LinkedIn URL",
        "Company",
        "Headline",
        "Message",
        "Comment"
    ]

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for msg in messages:
            writer.writerow({
                "Full Name": msg["name"],
                "First Name": msg["first_name"],
                "LinkedIn URL": msg["linkedin_url"],
                "Company": msg["company"] or "",
                "Headline": msg["headline"] or "",
                "Message": msg["message"],
                "Comment": msg["comment_text"][:100] if msg["comment_text"] else ""  # Truncate for readability
            })

    print(f"✅ Saved CSV for HeyReach upload to {filepath}")


def print_preview(messages, limit=5):
    """Print preview of generated messages."""

    print(f"\n{'='*80}")
    print(f"MESSAGE PREVIEW (showing {min(limit, len(messages))} of {len(messages)})")
    print(f"{'='*80}\n")

    for i, msg in enumerate(messages[:limit], 1):
        print(f"--- Message {i} ---")
        print(f"To: {msg['name']} ({msg['first_name']})")
        print(f"LinkedIn: {msg['linkedin_url']}")
        print(f"Comment: {msg['comment_text'][:60]}..." if msg['comment_text'] else "")
        print(f"\n{msg['message']}")
        print(f"\n{'-'*80}\n")

    if len(messages) > limit:
        print(f"... and {len(messages) - limit} more messages\n")


def main():
    print("="*80)
    print("CAMPAIGN MESSAGE GENERATOR")
    print("="*80)
    print(f"\nCampaign: {CAMPAIGN_TABLE}")
    print(f"Template: Lohit's successful format")
    print(f"Message Type: Claude Code tutorial offer\n")

    # Fetch prospects
    prospects = fetch_campaign_prospects()

    if not prospects:
        print("❌ No pending prospects found")
        sys.exit(0)

    # Generate messages
    print("Generating personalized messages...")
    messages = generate_messages(prospects)

    # Create timestamp for filenames
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')

    # Save to JSON (for tracking)
    save_to_json(messages, f"campaign_messages_{timestamp}.json")

    # Save to CSV (for HeyReach)
    save_to_csv(messages, f"campaign_messages_{timestamp}.csv")

    # Print preview
    print_preview(messages, limit=5)

    print(f"{'='*80}")
    print("NEXT STEPS:")
    print(f"{'='*80}")
    print("1. Review messages in: linkedin-messages/campaign_messages_*.json")
    print("2. Upload CSV to HeyReach: linkedin-messages/campaign_messages_*.csv")
    print("3. In HeyReach, use message template with {{Message}} variable")
    print("4. Track responses and update campaign status")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
