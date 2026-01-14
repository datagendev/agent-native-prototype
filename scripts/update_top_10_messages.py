#!/usr/bin/env python3
"""
Update the top 10 RevOps/GTM prospects with the new detailed message.
"""

import os
import sys
from datagen_sdk import DatagenClient

# Verify API key
DATAGEN_API_KEY = os.getenv("DATAGEN_API_KEY")
if not DATAGEN_API_KEY:
    print("ERROR: DATAGEN_API_KEY not found")
    sys.exit(1)

# Initialize DataGen client
client = DatagenClient()

# List ID from previous creation
LIST_ID = 467598

# New message template (more detailed, honest exchange)
NEW_MESSAGE_TEMPLATE = """Hey {first_name}, would you be interested in learning Claude Code for GTM? We're providing free 1:1s to show how we're using Claude Code. We believe it helps us learn how to better onboard users (we're an MCP gateway) and better understand the problem space while providing our learnings on how we believe is the effective way to use Claude Code.

Let me know if interested.

Yu-Sheng"""

# Top 10 RevOps/GTM-focused prospects (ordered by relevance)
TOP_10_PROFILES = [
    "https://www.linkedin.com/in/jackileahy",        # Fractional RevOps
    "https://www.linkedin.com/in/jim-holben",        # Building GTM programs
    "https://www.linkedin.com/in/habibbangash",      # GTM & Growth systems
    "https://www.linkedin.com/in/davidkwint",        # Agentic GTM Systems
    "https://www.linkedin.com/in/thescholarbaniya",  # AI Agents strategist
    "https://www.linkedin.com/in/briennapinnow",     # Fractional CMO & Growth
    "https://www.linkedin.com/in/scottmlincoln",     # Enterprise Sales & AI
    "https://www.linkedin.com/in/mavlonbek",         # Salesfinity (GTM tools)
    "https://www.linkedin.com/in/martin-valencia",   # Strategic Accounts
    "https://www.linkedin.com/in/alex-waiman-90a96b6" # VP Sales
]


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


def get_leads_from_list():
    """Get all leads from the HeyReach list."""

    print(f"📊 Fetching leads from HeyReach list {LIST_ID}...")

    result = client.execute_tool(
        "mcp_Heyreach_get_leads_from_list",
        {
            "listId": LIST_ID,
            "limit": 30,
            "offset": 0
        }
    )

    if result and isinstance(result, list) and len(result) > 0:
        leads = result[0].get("items", [])
        print(f"✅ Found {len(leads)} total leads\n")
        return leads

    return []


def filter_top_10(all_leads):
    """Filter to get only the top 10 RevOps/GTM prospects."""

    top_10_leads = []

    for profile_url in TOP_10_PROFILES:
        for lead in all_leads:
            if lead.get("profileUrl") == profile_url:
                top_10_leads.append(lead)
                break

    print(f"✅ Filtered to {len(top_10_leads)} top GTM/RevOps prospects:\n")

    for i, lead in enumerate(top_10_leads, 1):
        name = f"{lead.get('firstName', '')} {lead.get('lastName', '')}".strip()
        headline = lead.get('headline', 'No headline')[:60]
        print(f"   {i}. {name} - {headline}...")

    print()
    return top_10_leads


def update_lead_messages(leads):
    """Update the custom message field for each lead."""

    print(f"📝 Updating messages for {len(leads)} leads...\n")

    updated_count = 0
    failed_count = 0

    for i, lead in enumerate(leads, 1):
        first_name = extract_first_name(f"{lead.get('firstName', '')} {lead.get('lastName', '')}".strip())
        profile_url = lead.get("profileUrl")

        # Generate new message
        new_message = NEW_MESSAGE_TEMPLATE.format(first_name=first_name)

        # Get existing custom fields
        custom_fields = lead.get("customFields", [])

        # Update the message field
        updated_fields = []
        message_updated = False

        for field in custom_fields:
            if field.get("name") == "message":
                updated_fields.append({
                    "name": "message",
                    "value": new_message
                })
                message_updated = True
            else:
                updated_fields.append(field)

        # If message field didn't exist, add it
        if not message_updated:
            updated_fields.append({
                "name": "message",
                "value": new_message
            })

        # Update the lead
        try:
            result = client.execute_tool(
                "mcp_Heyreach_add_leads_to_list_v2",
                {
                    "listId": LIST_ID,
                    "leads": [{
                        "profileUrl": profile_url,
                        "firstName": lead.get("firstName"),
                        "lastName": lead.get("lastName"),
                        "companyName": lead.get("companyName"),
                        "position": lead.get("headline"),
                        "customUserFields": updated_fields
                    }]
                }
            )

            print(f"   ✅ {i}. Updated: {first_name}")
            updated_count += 1

        except Exception as e:
            print(f"   ❌ {i}. Failed: {first_name} - {str(e)}")
            failed_count += 1

    print(f"\n{'='*80}")
    print(f"UPDATE SUMMARY:")
    print(f"{'='*80}")
    print(f"✅ Successfully updated: {updated_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"{'='*80}\n")


def preview_new_message():
    """Show a preview of the new message."""

    sample_message = NEW_MESSAGE_TEMPLATE.format(first_name="Jacki")

    print("="*80)
    print("NEW MESSAGE PREVIEW:")
    print("="*80)
    print(sample_message)
    print("="*80 + "\n")


def main():
    print("="*80)
    print("UPDATE TOP 10 REVOPS/GTM PROSPECTS")
    print("="*80)
    print(f"\nList ID: {LIST_ID}")
    print("Target: Top 10 RevOps/GTM-focused prospects\n")

    # Step 1: Preview new message
    preview_new_message()

    # Step 2: Get all leads
    all_leads = get_leads_from_list()

    if not all_leads:
        print("❌ No leads found in list")
        sys.exit(1)

    # Step 3: Filter to top 10
    top_10 = filter_top_10(all_leads)

    if not top_10:
        print("❌ Could not find top 10 prospects")
        sys.exit(1)

    # Step 4: Update messages
    update_lead_messages(top_10)

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Go to HeyReach and check the list")
    print("2. Create a campaign with these 10 leads")
    print("3. Use {{message}} in your campaign template")
    print("4. The message now explains MCP gateway and mutual learning")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
