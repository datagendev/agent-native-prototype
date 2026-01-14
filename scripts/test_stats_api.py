#!/usr/bin/env python3
"""Test HeyReach overall_stats API"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from datagen_sdk import DatagenClient

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

if not os.getenv("DATAGEN_API_KEY"):
    raise RuntimeError("DATAGEN_API_KEY not set")

client = DatagenClient()

print("="*80)
print("HEYREACH STATS API TEST")
print("="*80)

# First get campaign IDs
print("\n1. Getting campaigns...")
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

campaigns = campaigns_result[0].get("items", []) if isinstance(campaigns_result, list) else []
campaign_ids = [c["id"] for c in campaigns]
account_ids = [105032]  # From the test data we saw earlier

print(f"Campaign IDs: {campaign_ids}")
print(f"Account IDs: {account_ids}")

# Now try get_overall_stats with different date ranges
print("\n2. Testing get_overall_stats...")

# Test 1: No date filter
print("\nTest 1: No date filter (should include all)")
try:
    result = client.execute_tool(
        "mcp_Heyreach_get_overall_stats",
        {
            "campaignIds": campaign_ids,
            "accountIds": account_ids,
            "startDate": None,
            "endDate": None
        }
    )
    print("✓ Success!")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2: With date range (last 90 days)
print("\nTest 2: Last 90 days")
try:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    result = client.execute_tool(
        "mcp_Heyreach_get_overall_stats",
        {
            "campaignIds": campaign_ids,
            "accountIds": account_ids,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat()
        }
    )
    print("✓ Success!")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3: Empty arrays (should return all)
print("\nTest 3: Empty campaign and account arrays")
try:
    result = client.execute_tool(
        "mcp_Heyreach_get_overall_stats",
        {
            "campaignIds": [],
            "accountIds": [],
            "startDate": None,
            "endDate": None
        }
    )
    print("✓ Success!")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 4: Just one campaign
print(f"\nTest 4: Single campaign ID {campaign_ids[0]}")
try:
    result = client.execute_tool(
        "mcp_Heyreach_get_overall_stats",
        {
            "campaignIds": [campaign_ids[0]],
            "accountIds": account_ids,
            "startDate": None,
            "endDate": None
        }
    )
    print("✓ Success!")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n" + "="*80)
