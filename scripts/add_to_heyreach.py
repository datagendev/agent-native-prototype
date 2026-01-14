#!/usr/bin/env python3
"""
Add campaign prospects to HeyReach lead list.
Creates a new list and adds all prospects with custom fields.
"""

import os
import sys
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

# HeyReach list name
LIST_NAME = "Jordan Crawford GTM - Claude Code Tutorials"

# Message template
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

    print(f"📊 Fetching prospects from {CAMPAIGN_TABLE}...")

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

    # Parse result
    if result and len(result) > 0:
        prospects = result[0]
        print(f"✅ Found {len(prospects)} pending prospects\n")
        return prospects

    return []


def create_heyreach_list():
    """Create a new HeyReach lead list."""

    print(f"📝 Creating HeyReach list: {LIST_NAME}...")

    result = client.execute_tool(
        "mcp_Heyreach_create_empty_list",
        {
            "listName": LIST_NAME,
            "listType": "USER_LIST"
        }
    )
    
    # Parse the result to get list ID
    if result and isinstance(result, list) and len(result) > 0:
        list_data = result[0]
        list_id = list_data.get("id")
        print(f"✅ Created list with ID: {list_id}\n")
        return list_id

    print("❌ Failed to create list")
    print(f"Result: {result}")
    return None


def format_leads_for_heyreach(prospects):
    """Format prospects into HeyReach lead format."""

    leads = []

    for prospect in prospects:
        first_name = extract_first_name(prospect.get("name", ""))

        # Create the personalized message
        message = MESSAGE_TEMPLATE.format(first_name=first_name)

        # Split name into first and last
        name_parts = prospect.get("name", "").replace("🦾", "").replace("👨‍💻", "").replace("🪄", "").strip().split()
        first = name_parts[0] if name_parts else ""
        last = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        lead = {
            "profileUrl": prospect.get("linkedin_url"),
            "firstName": first,
            "lastName": last,
            "companyName": prospect.get("company"),
            "position": prospect.get("headline"),
            "customUserFields": [
                {
                    "name": "message",
                    "value": message
                },
                {
                    "name": "comment_text",
                    "value": prospect.get("comment_text", "")[:200]  # Truncate if too long
                },
                {
                    "name": "campaign_source",
                    "value": "Jordan Crawford GTM Post"
                }
            ]
        }

        leads.append(lead)

    return leads


def add_leads_to_heyreach(list_id, leads):
    """Add leads to HeyReach list in batches of 100."""

    total_leads = len(leads)
    batch_size = 100
    batches = [leads[i:i + batch_size] for i in range(0, total_leads, batch_size)]

    print(f"📤 Adding {total_leads} leads to HeyReach list {list_id}...")
    print(f"   Processing in {len(batches)} batch(es)\n")

    total_added = 0
    total_updated = 0
    total_failed = 0

    for i, batch in enumerate(batches, 1):
        print(f"   Batch {i}/{len(batches)}: Adding {len(batch)} leads...")

        result = client.execute_tool(
            "mcp_Heyreach_add_leads_to_list_v2",
            {
                "listId": list_id,
                "leads": batch
            }
        )

        # Parse result
        if result and isinstance(result, list) and len(result) > 0:
            batch_result = result[0]
            added = batch_result.get("addedCount", 0)
            updated = batch_result.get("updatedCount", 0)
            failed = batch_result.get("failedCount", 0)

            total_added += added
            total_updated += updated
            total_failed += failed

            print(f"   ✅ Batch {i}: Added {added}, Updated {updated}, Failed {failed}")
        else:
            print(f"   ❌ Batch {i} failed")
            print(f"   Result: {result}")

    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"{'='*80}")
    print(f"✅ Total Added: {total_added}")
    print(f"🔄 Total Updated: {total_updated}")
    print(f"❌ Total Failed: {total_failed}")
    print(f"{'='*80}\n")

    return {
        "added": total_added,
        "updated": total_updated,
        "failed": total_failed
    }


def main():
    print("="*80)
    print("ADD PROSPECTS TO HEYREACH")
    print("="*80)
    print(f"\nCampaign: {CAMPAIGN_TABLE}")
    print(f"List Name: {LIST_NAME}\n")

    # Step 1: Fetch prospects
    prospects = fetch_campaign_prospects()

    if not prospects:
        print("❌ No pending prospects found")
        sys.exit(0)

    # Step 2: Create HeyReach list
    list_id = create_heyreach_list()

    if not list_id:
        print("❌ Failed to create HeyReach list")
        sys.exit(1)

    # Step 3: Format leads
    print("🔧 Formatting leads for HeyReach...")
    leads = format_leads_for_heyreach(prospects)
    print(f"✅ Formatted {len(leads)} leads\n")

    # Step 4: Add leads to HeyReach
    result = add_leads_to_heyreach(list_id, leads)

    # Step 5: Next steps
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print(f"1. Go to HeyReach and find list: '{LIST_NAME}'")
    print(f"2. Create a campaign and add this list")
    print(f"3. In campaign message, use: {{{{message}}}} custom field")
    print(f"4. The message is already personalized with first names")
    print(f"5. Track responses and update campaign status in database")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
