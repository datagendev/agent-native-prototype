#!/usr/bin/env python3
"""Process Instantly raw data into report summary"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

def main():
    raw_dir = "/home/user/repo/tmp/instantly-analytics/raw"
    output_file = "/home/user/repo/tmp/instantly-analytics/report_summary.json"

    # Load data
    with open(f"{raw_dir}/accounts.json") as f:
        accounts = json.load(f)

    with open(f"{raw_dir}/campaign_analytics.json") as f:
        campaign_analytics = json.load(f)

    with open(f"{raw_dir}/daily_campaign_analytics.json") as f:
        daily_analytics = json.load(f)

    with open(f"{raw_dir}/replies.json") as f:
        replies = json.load(f)

    # Date range for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Process accounts by domain
    domains = defaultdict(lambda: {
        "accounts": [],
        "total_accounts": 0,
        "active_accounts": 0,
        "errored_accounts": 0,
        "warmup_accounts": 0,
        "daily_limit_capacity": 0,
        "avg_warmup_score": 0
    })

    for account in accounts:
        # Extract domain from email
        if "email" in account and "@" in account["email"]:
            domain = account["email"].split("@")[1]
        else:
            domain = "unknown"

        domains[domain]["accounts"].append(account)
        domains[domain]["total_accounts"] += 1

        # Status classification
        status = account.get("status", 0)
        if status == 1:
            domains[domain]["active_accounts"] += 1
        elif status < 0:
            domains[domain]["errored_accounts"] += 1

        # Warmup status
        if account.get("warmup_status") == 1:
            domains[domain]["warmup_accounts"] += 1

        # Daily limit capacity
        daily_limit = account.get("daily_limit", 0)
        domains[domain]["daily_limit_capacity"] += daily_limit

        # Warmup score
        warmup_score = account.get("stat_warmup_score", 0)
        if warmup_score:
            domains[domain]["avg_warmup_score"] += warmup_score

    # Calculate averages
    for domain in domains:
        if domains[domain]["total_accounts"] > 0:
            domains[domain]["avg_warmup_score"] = domains[domain]["avg_warmup_score"] / domains[domain]["total_accounts"]

    # Process campaigns
    campaigns = []
    if isinstance(campaign_analytics, dict) and "data" in campaign_analytics:
        for campaign in campaign_analytics["data"]:
            campaigns.append({
                "name": campaign.get("name", "Unknown"),
                "id": campaign.get("id"),
                "status": campaign.get("status"),
                "sent": campaign.get("sent", 0),
                "replied": campaign.get("replied", 0),
                "bounced": campaign.get("bounced", 0),
                "opened": campaign.get("opened", 0),
                "clicked": campaign.get("clicked", 0),
                "reply_rate": (campaign.get("replied", 0) / campaign.get("sent", 1)) * 100 if campaign.get("sent", 0) > 0 else 0,
                "bounce_rate": (campaign.get("bounced", 0) / campaign.get("sent", 1)) * 100 if campaign.get("sent", 0) > 0 else 0
            })

    # Process daily analytics for trends
    daily_data = []
    if isinstance(daily_analytics, dict) and "data" in daily_analytics:
        for day in daily_analytics["data"]:
            daily_data.append({
                "date": day.get("date"),
                "sent": day.get("sent", 0),
                "opened": day.get("opened", 0),
                "clicked": day.get("clicked", 0),
                "replied": day.get("replied", 0),
                "bounced": day.get("bounced", 0)
            })

    # Filter replies to last 30 days
    recent_replies = []
    for reply in replies:
        if "timestamp_created" in reply:
            try:
                reply_date = datetime.fromtimestamp(reply["timestamp_created"])
                if reply_date >= start_date:
                    recent_replies.append(reply)
            except:
                pass

    # Calculate totals
    total_sent = sum(c["sent"] for c in campaigns)
    total_replied = sum(c["replied"] for c in campaigns)
    total_bounced = sum(c["bounced"] for c in campaigns)

    # Create summary
    summary = {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": 30
        },
        "totals": {
            "accounts": len(accounts),
            "domains": len(domains),
            "campaigns": len(campaigns),
            "sent": total_sent,
            "replied": total_replied,
            "bounced": total_bounced,
            "reply_rate": (total_replied / total_sent * 100) if total_sent > 0 else 0,
            "bounce_rate": (total_bounced / total_sent * 100) if total_sent > 0 else 0,
            "recent_replies_30d": len(recent_replies)
        },
        "domains": {k: {**v, "accounts": None} for k, v in domains.items()},  # Remove full account data
        "campaigns": campaigns,
        "daily_analytics": daily_data[:30]  # Last 30 days
    }

    # Save summary
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Report summary created: {output_file}")
    print(f"\nSummary:")
    print(f"  Period: {start_date.date()} to {end_date.date()}")
    print(f"  Domains: {len(domains)}")
    print(f"  Accounts: {len(accounts)}")
    print(f"  Campaigns: {len(campaigns)}")
    print(f"  Total sent: {total_sent:,}")
    print(f"  Reply rate: {summary['totals']['reply_rate']:.2f}%")
    print(f"  Bounce rate: {summary['totals']['bounce_rate']:.2f}%")

if __name__ == "__main__":
    main()
