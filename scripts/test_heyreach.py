#!/usr/bin/env python3
"""Test HeyReach MCP tools"""

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
print("HEYREACH MCP TEST")
print("="*80)

# Test 1: Get all campaigns
print("\n1. Fetching campaigns...")
try:
    result = client.execute_tool(
        "mcp_Heyreach_get_all_campaigns",
        {
            "statuses": [],
            "accountIds": [],
            "keyword": "",
            "limit": 10,
            "offset": 0
        }
    )
    print("✓ Success!")
    print(f"\nRaw response:\n{json.dumps(result, indent=2)}")

    # Try to parse campaigns
    campaigns = result if isinstance(result, list) else result.get("campaigns", [])
    print(f"\n✓ Found {len(campaigns)} campaign(s)")

    if campaigns:
        for i, campaign in enumerate(campaigns, 1):
            print(f"\nCampaign {i}:")
            print(f"  ID: {campaign.get('id')}")
            print(f"  Name: {campaign.get('name')}")
            print(f"  Status: {campaign.get('status')}")

except Exception as e:
    print(f"✗ Failed: {e}")

print("\n" + "="*80)
