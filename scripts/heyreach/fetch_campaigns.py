#!/usr/bin/env python3
"""
Fetch HeyReach campaigns and save to intermediate storage.

Step 1 of the HeyReach report pipeline.
Outputs: /tmp/heyreach-{date}/campaigns.json

Usage:
    python fetch_campaigns.py
    python fetch_campaigns.py --ids 291852,210501
    python fetch_campaigns.py --status FINISHED
    python fetch_campaigns.py --keyword "Claude"
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from datagen_sdk import DatagenClient


def get_output_dir() -> Path:
    """Get today's output directory."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return Path(f"/tmp/heyreach-{date_str}")


def fetch_campaigns(
    client: DatagenClient,
    campaign_ids: list[int] | None = None,
    status: str | None = None,
    keyword: str | None = None,
) -> tuple[list[dict], str]:
    """
    Fetch campaigns from HeyReach API.

    Returns (campaigns, error). Check error first.
    """
    try:
        statuses = [status] if status else []

        result = client.execute_tool(
            "mcp_Heyreach_get_all_campaigns",
            {
                "statuses": statuses,
                "accountIds": [],
                "keyword": keyword or "",
                "limit": 100,
                "offset": 0,
            }
        )

        # Parse response
        if isinstance(result, list) and len(result) > 0:
            campaigns = result[0].get("items", [])
        elif isinstance(result, dict):
            campaigns = result.get("items", result.get("campaigns", []))
        else:
            campaigns = []

        # Filter by specific IDs if provided
        if campaign_ids:
            campaigns = [c for c in campaigns if c.get("id") in campaign_ids]

        return campaigns, ""

    except Exception as e:
        return [], f"fetch_campaigns failed: {e}"


def save_campaigns(campaigns: list[dict], output_dir: Path) -> tuple[Path, str]:
    """
    Save campaigns to JSON file.

    Returns (output_path, error). Check error first.
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "campaigns.json"

        output_path.write_text(json.dumps(campaigns, indent=2, ensure_ascii=False))

        return output_path, ""

    except Exception as e:
        return Path(), f"save_campaigns failed: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch HeyReach campaigns")
    parser.add_argument("--ids", type=str, help="Comma-separated campaign IDs")
    parser.add_argument("--status", type=str, help="Filter by status (FINISHED, IN_PROGRESS, etc.)")
    parser.add_argument("--keyword", type=str, help="Search by keyword")
    parser.add_argument("--output-dir", type=str, help="Override output directory")

    args = parser.parse_args()

    # Load environment
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)

    if not os.getenv("DATAGEN_API_KEY"):
        print("ERROR: DATAGEN_API_KEY not set", file=sys.stderr)
        return 1

    # Parse campaign IDs
    campaign_ids = None
    if args.ids:
        campaign_ids = [int(x.strip()) for x in args.ids.split(",")]

    # Determine output directory
    output_dir = Path(args.output_dir) if args.output_dir else get_output_dir()

    print(f"Fetching campaigns...")
    print(f"  Status filter: {args.status or 'all'}")
    print(f"  Keyword filter: {args.keyword or 'none'}")
    print(f"  ID filter: {campaign_ids or 'none'}")

    # Fetch campaigns
    client = DatagenClient()
    campaigns, err = fetch_campaigns(
        client,
        campaign_ids=campaign_ids,
        status=args.status,
        keyword=args.keyword,
    )

    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"  Found {len(campaigns)} campaigns")

    # Save to file
    output_path, err = save_campaigns(campaigns, output_dir)

    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"  Saved to: {output_path}")

    # Print summary
    print(f"\nCampaigns fetched: {len(campaigns)}")
    for c in campaigns[:5]:
        print(f"  - {c.get('id')}: {c.get('name')} ({c.get('status')})")
    if len(campaigns) > 5:
        print(f"  ... and {len(campaigns) - 5} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
