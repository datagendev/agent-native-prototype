#!/usr/bin/env python3
"""Fetch Instantly data using DataGen SDK"""

import json
import os
from datetime import datetime, timedelta
from datagen_sdk import DatagenClient

def main():
    client = DatagenClient()
    output_dir = "/home/user/repo/tmp/instantly-analytics/raw"
    os.makedirs(output_dir, exist_ok=True)

    # Date range for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    print(f"Fetching data for {start_date.date()} to {end_date.date()}")

    # 1. Fetch all accounts
    print("Fetching accounts...")
    result = client.execute_tool("mcp_Instantly_list_accounts", {"params": {}})
    accounts = result if isinstance(result, list) else result.get("data", [])

    print(f"Found {len(accounts)} accounts")
    with open(f"{output_dir}/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 2. Fetch campaign analytics
    print("Fetching campaign analytics...")
    campaign_analytics = client.execute_tool("mcp_Instantly_get_campaign_analytics", {})

    with open(f"{output_dir}/campaign_analytics.json", "w") as f:
        json.dump(campaign_analytics, f, indent=2)

    # 3. Fetch daily campaign analytics
    print("Fetching daily campaign analytics...")
    daily_analytics = client.execute_tool("mcp_Instantly_get_daily_campaign_analytics", {
        "params": {}
    })

    with open(f"{output_dir}/daily_campaign_analytics.json", "w") as f:
        json.dump(daily_analytics, f, indent=2)

    # 4. Fetch emails (replies) - paginated
    print("Fetching emails...")
    result = client.execute_tool("mcp_Instantly_list_emails", {
        "params": {"email_type": "received"}
    })
    emails = result if isinstance(result, list) else result.get("data", [])

    print(f"Found {len(emails)} emails")
    with open(f"{output_dir}/replies.json", "w") as f:
        json.dump(emails, f, indent=2)

    # 5. Fetch warmup analytics for all accounts
    print("Fetching warmup analytics...")
    account_emails = [acc["email"] for acc in accounts if "email" in acc]

    if account_emails:
        # Batch warmup requests (API may have limits)
        warmup_data = client.execute_tool("mcp_Instantly_get_warmup_analytics", {
            "params": {"emails": account_emails[:100]}  # First 100 accounts
        })

        with open(f"{output_dir}/warmup.json", "w") as f:
            json.dump(warmup_data, f, indent=2)
    else:
        print("No accounts with email addresses found")
        with open(f"{output_dir}/warmup.json", "w") as f:
            json.dump([], f, indent=2)

    print("\nData fetch complete!")
    print(f"Output directory: {output_dir}")
    print(f"Files created:")
    print(f"  - accounts.json ({len(accounts)} accounts)")
    print(f"  - campaign_analytics.json")
    print(f"  - daily_campaign_analytics.json")
    print(f"  - replies.json ({len(emails)} emails)")
    print(f"  - warmup.json")

if __name__ == "__main__":
    main()
