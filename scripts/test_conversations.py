#!/usr/bin/env python3
"""Test HeyReach conversations API to get reply data"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datagen_sdk import DatagenClient

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

if not os.getenv("DATAGEN_API_KEY"):
    raise RuntimeError("DATAGEN_API_KEY not set")

client = DatagenClient()

print("="*80)
print("HEYREACH CONVERSATIONS TEST")
print("="*80)

# Campaign IDs from earlier: [291852, 210501, 209470]
# Account ID: 105032

campaign_ids = [291852, 210501, 209470]
account_id = 105032

print(f"\nFetching conversations for campaigns: {campaign_ids}")
print(f"Account ID: {account_id}\n")

try:
    result = client.execute_tool(
        "mcp_Heyreach_get_conversations_v2",
        {
            "linkedInAccountIds": [account_id],
            "campaignIds": campaign_ids,
            "limit": 50,  # Get more conversations
            "offset": 0,
            "searchString": "",
            "seen": None,
            "leadLinkedInId": None,
            "leadProfileUrl": None
        }
    )

    print("✓ Success!")
    print(f"\nRaw response (first 2000 chars):\n{json.dumps(result, indent=2)[:2000]}...")

    # Try to parse structure
    if isinstance(result, list) and len(result) > 0:
        conversations = result[0].get("items", []) if isinstance(result[0], dict) else result
    elif isinstance(result, dict):
        conversations = result.get("items", result.get("conversations", []))
    else:
        conversations = result

    print(f"\n📊 Found {len(conversations) if isinstance(conversations, list) else 'unknown'} conversations")

    # Show first few conversations
    if isinstance(conversations, list) and conversations:
        print("\n📧 Sample conversations:")
        for i, conv in enumerate(conversations[:3], 1):
            print(f"\nConversation {i}:")
            print(json.dumps(conv, indent=2))

except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
