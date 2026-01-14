#!/usr/bin/env python3
"""
Test HeyReach Campaign Looping

Tests if looping through campaigns to get conversations works in DataGen SDK.
This replicates the Make.com scenario:
1. Get all campaigns
2. Loop through each campaign
3. Get conversations for each campaign
4. Aggregate results
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datagen_sdk import DatagenClient

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

if not os.getenv("DATAGEN_API_KEY"):
    raise RuntimeError("DATAGEN_API_KEY not set")

client = DatagenClient()

print("="*60)
print("TESTING HEYREACH LOOPING IN SDK")
print("="*60)

# Step 1: Get all campaigns
print("\n[Step 1] Fetching all campaigns...")
try:
    campaigns_result = client.execute_tool(
        "mcp_Heyreach_get_all_campaigns",
        {
            "statuses": [],
            "accountIds": [],
            "keyword": "",
            "limit": 10,
            "offset": 0
        }
    )

    # Parse campaigns
    if isinstance(campaigns_result, list) and len(campaigns_result) > 0:
        campaigns = campaigns_result[0].get("items", [])
    else:
        campaigns = []

    print(f"✓ Found {len(campaigns)} campaigns")
    for c in campaigns:
        print(f"  - {c['name']} (ID: {c['id']})")

except Exception as e:
    print(f"✗ Failed to get campaigns: {e}")
    sys.exit(1)

# Step 2: Loop through campaigns and get conversations
print(f"\n[Step 2] Looping through {len(campaigns)} campaigns...")

campaign_data = []
total_conversations = 0
total_replies = 0
errors = []

for i, campaign in enumerate(campaigns, 1):
    campaign_id = campaign['id']
    campaign_name = campaign['name']

    print(f"\n  [{i}/{len(campaigns)}] Fetching conversations for: {campaign_name}")

    try:
        # Get conversations for this campaign
        conv_result = client.execute_tool(
            "mcp_Heyreach_get_conversations_v2",
            {
                "linkedInAccountIds": [],
                "campaignIds": [campaign_id],
                "limit": 100,
                "offset": 0,
                "searchString": ""
            }
        )

        # Parse conversations
        if isinstance(conv_result, list) and len(conv_result) > 0:
            convs = conv_result[0].get("items", [])
            total_count = conv_result[0].get("totalCount", 0)
        else:
            convs = conv_result.get("items", []) if isinstance(conv_result, dict) else []
            total_count = len(convs)

        # Count replies (where last message sender is CORRESPONDENT)
        replies = [c for c in convs if c.get('lastMessageSender') == 'CORRESPONDENT']

        campaign_data.append({
            "id": campaign_id,
            "name": campaign_name,
            "total_conversations": total_count,
            "replies_received": len(replies),
            "reply_rate": round(len(replies) / total_count * 100, 1) if total_count > 0 else 0
        })

        total_conversations += total_count
        total_replies += len(replies)

        print(f"    ✓ {total_count} conversations, {len(replies)} replies")

    except Exception as e:
        error_msg = str(e)
        errors.append({
            "campaign": campaign_name,
            "error": error_msg
        })
        print(f"    ✗ Error: {error_msg}")

# Step 3: Aggregate results
print("\n" + "="*60)
print("RESULTS")
print("="*60)

print(f"\n📊 Summary:")
print(f"  Total campaigns: {len(campaigns)}")
print(f"  Campaigns processed: {len(campaign_data)}")
print(f"  Total conversations: {total_conversations}")
print(f"  Total replies: {total_replies}")
if total_conversations > 0:
    print(f"  Overall reply rate: {round(total_replies / total_conversations * 100, 1)}%")
print(f"  Errors: {len(errors)}")

print(f"\n📈 Per-Campaign Breakdown:")
for data in campaign_data:
    print(f"  {data['name']}:")
    print(f"    - Conversations: {data['total_conversations']}")
    print(f"    - Replies: {data['replies_received']}")
    print(f"    - Reply rate: {data['reply_rate']}%")

if errors:
    print(f"\n❌ Errors:")
    for err in errors:
        print(f"  - {err['campaign']}: {err['error']}")

# Final verdict
success = len(errors) == 0 and len(campaign_data) > 0
print(f"\n{'✅ LOOPING SUCCEEDED - All campaigns processed!' if success else '❌ LOOPING FAILED - Some campaigns had errors'}")

sys.exit(0 if success else 1)
