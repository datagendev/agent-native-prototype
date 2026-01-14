#!/usr/bin/env python3
"""
Generate personalized outreach messages for campaign prospects.
Uses messaging templates and prospect comment context.
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from datagen_sdk import DatagenClient

# Load environment variables
load_dotenv("../.env")

# Verify API key
if not os.getenv("DATAGEN_API_KEY"):
    print("ERROR: DATAGEN_API_KEY not found in ../.env")
    sys.exit(1)

# Initialize DataGen client
client = DatagenClient()

# Campaign to generate messages for
CAMPAIGN_TABLE = "campaign_jordan_crawford_gtm_session_link_requests"

# Messaging angle templates (Angle 3: Speed)
SPEED_OPENERS = [
    "Hey {first_name}, have you used Claude Code to speed up your prospecting workflow yet?",
    "Hey {first_name}, are you building ICP signals faster with Claude Code or still figuring it out?",
    "Hey {first_name}, how long does it take you to research a new account right now?",
]

SPEED_WITH_EXCHANGE = [
    """Hey {first_name}, I've been cutting my ICP research time down to minutes with Claude Code.

Building tools to make it even faster. Looking for people to try it and give feedback. Interested?""",

    """Hey {first_name}, most GTM folks I talk to are still spending hours on account research.

I've got a setup that does it in minutes. Want to see how it works and tell me what's missing?""",
]

def get_campaign_prospects():
    """Fetch all pending prospects from the campaign with their comments."""

    query = f"""
    SELECT
        ct.id as campaign_entry_id,
        p.id as prospect_id,
        p.name,
        p.linkedin_url,
        p.headline,
        p.company,
        ct.comment_text,
        ct.urgency_level,
        ct.status
    FROM {CAMPAIGN_TABLE} ct
    JOIN prospects p ON p.id = ct.prospect_id
    WHERE ct.status = 'pending'
    ORDER BY ct.urgency_level DESC, ct.id;
    """

    print(f"Fetching prospects from {CAMPAIGN_TABLE}...")

    result = client.execute_tool(
        "mcp_Neon_execute_sql",
        {
            "project_id": "blue-tree-25780810",
            "branch_id": "br-cool-leaf-afau0ra8",
            "database": "neondb",
            "query": query
        }
    )

    return result.get("results", [])


def extract_first_name(full_name):
    """Extract first name from full name."""
    if not full_name:
        return "there"

    # Remove common emojis and split
    clean_name = full_name.replace("🦾", "").replace("👨‍💻", "").strip()
    first = clean_name.split()[0] if clean_name else "there"
    return first


def generate_message_for_prospect(prospect):
    """Generate personalized message based on prospect data."""

    first_name = extract_first_name(prospect.get("name", ""))
    comment = prospect.get("comment_text", "")
    headline = prospect.get("headline", "")
    company = prospect.get("company", "")

    # Select template based on context
    # Use the "honest exchange" version since we saw the link request comment
    template = SPEED_WITH_EXCHANGE[0]  # First honest exchange template

    # Format the message
    message = template.format(first_name=first_name)

    # Add context-aware note for internal use
    context_note = f"""
--- CONTEXT FOR THIS PROSPECT ---
Name: {prospect.get('name')}
Headline: {headline}
Company: {company}
Comment: {comment[:100]}{'...' if len(comment) > 100 else ''}
Urgency: {prospect.get('urgency_level')}
LinkedIn: {prospect.get('linkedin_url')}
---
"""

    return {
        "prospect_id": prospect.get("prospect_id"),
        "campaign_entry_id": prospect.get("campaign_entry_id"),
        "name": prospect.get("name"),
        "first_name": first_name,
        "linkedin_url": prospect.get("linkedin_url"),
        "headline": headline,
        "company": company,
        "comment": comment,
        "urgency_level": prospect.get("urgency_level"),
        "message": message,
        "context_note": context_note,
        "generated_at": datetime.utcnow().isoformat()
    }


def save_messages(messages, output_file):
    """Save generated messages to JSON file."""

    with open(output_file, 'w') as f:
        json.dump(messages, f, indent=2)

    print(f"\nSaved {len(messages)} messages to {output_file}")


def print_summary(messages):
    """Print a summary of generated messages."""

    print(f"\n{'='*80}")
    print(f"GENERATED {len(messages)} MESSAGES")
    print(f"{'='*80}\n")

    for i, msg in enumerate(messages[:5], 1):  # Show first 5
        print(f"--- Message {i}/{len(messages)} ---")
        print(f"To: {msg['name']} ({msg['first_name']})")
        print(f"Company: {msg['company']}")
        print(f"Headline: {msg['headline'][:60]}...")
        print(f"Comment snippet: {msg['comment'][:80]}...")
        print(f"\nMESSAGE:")
        print(msg['message'])
        print(f"\n{'-'*80}\n")

    if len(messages) > 5:
        print(f"... and {len(messages) - 5} more messages")
        print(f"\nView all messages in: messages_generated.json")


def main():
    print("="*80)
    print("CAMPAIGN MESSAGE GENERATOR")
    print("="*80)
    print(f"\nCampaign: {CAMPAIGN_TABLE}")
    print(f"Message Angle: Speed (Angle 3)")
    print(f"Template: Honest Exchange - ICP research in minutes\n")

    # Fetch prospects
    prospects = get_campaign_prospects()

    if not prospects:
        print("No pending prospects found in campaign.")
        sys.exit(0)

    print(f"Found {len(prospects)} pending prospects\n")

    # Generate messages
    print("Generating personalized messages...")
    messages = [generate_message_for_prospect(p) for p in prospects]

    # Save to file
    output_file = f"../linkedin-messages/campaign_messages_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    save_messages(messages, output_file)

    # Print summary
    print_summary(messages)

    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review the messages in: linkedin-messages/campaign_messages_*.json")
    print("2. Customize individual messages if needed")
    print("3. Upload to HeyReach or send manually")
    print("4. Track responses in the messages table")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
