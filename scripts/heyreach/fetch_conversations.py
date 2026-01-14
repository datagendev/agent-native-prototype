#!/usr/bin/env python3
"""
Fetch HeyReach conversations for campaigns.

Step 2 of the HeyReach report pipeline.
Reads: /tmp/heyreach-{date}/campaigns.json
Outputs: /tmp/heyreach-{date}/conversations/{campaign_id}.json

Usage:
    python fetch_conversations.py
    python fetch_conversations.py --input-dir /tmp/heyreach-2026-01-10
    python fetch_conversations.py --campaign-ids 291852,210501
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


def load_campaigns(input_dir: Path) -> tuple[list[dict], str]:
    """
    Load campaigns from JSON file.

    Returns (campaigns, error). Check error first.
    """
    campaigns_path = input_dir / "campaigns.json"

    if not campaigns_path.exists():
        return [], f"campaigns.json not found in {input_dir}"

    try:
        campaigns = json.loads(campaigns_path.read_text())
        return campaigns, ""
    except Exception as e:
        return [], f"Failed to load campaigns.json: {e}"


def fetch_conversations_for_campaign(
    client: DatagenClient,
    campaign_id: int,
    account_ids: list[int] | None = None,
) -> tuple[list[dict], str]:
    """
    Fetch conversations for a single campaign.

    Returns (conversations, error). Check error first.
    """
    try:
        result = client.execute_tool(
            "mcp_Heyreach_get_conversations_v2",
            {
                "linkedInAccountIds": account_ids or [],
                "campaignIds": [campaign_id],
                "limit": 100,
                "offset": 0,
                "searchString": "",
                "seen": None,
                "leadLinkedInId": None,
                "leadProfileUrl": None,
            }
        )

        # Parse response
        if isinstance(result, list) and len(result) > 0:
            conversations = result[0].get("items", []) if isinstance(result[0], dict) else result
        elif isinstance(result, dict):
            conversations = result.get("items", result.get("conversations", []))
        else:
            conversations = []

        return conversations, ""

    except Exception as e:
        return [], f"fetch_conversations failed for campaign {campaign_id}: {e}"


def save_conversations(
    conversations: list[dict],
    campaign_id: int,
    output_dir: Path,
) -> tuple[Path, str]:
    """
    Save conversations to JSON file.

    Returns (output_path, error). Check error first.
    """
    try:
        conversations_dir = output_dir / "conversations"
        conversations_dir.mkdir(parents=True, exist_ok=True)

        output_path = conversations_dir / f"{campaign_id}.json"
        output_path.write_text(json.dumps(conversations, indent=2, ensure_ascii=False))

        return output_path, ""

    except Exception as e:
        return Path(), f"save_conversations failed: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch HeyReach conversations")
    parser.add_argument("--input-dir", type=str, help="Input directory with campaigns.json")
    parser.add_argument("--campaign-ids", type=str, help="Override: comma-separated campaign IDs to fetch")
    parser.add_argument("--skip-existing", action="store_true", help="Skip campaigns with existing conversation files")

    args = parser.parse_args()

    # Load environment
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)

    if not os.getenv("DATAGEN_API_KEY"):
        print("ERROR: DATAGEN_API_KEY not set", file=sys.stderr)
        return 1

    # Determine directories
    output_dir = Path(args.input_dir) if args.input_dir else get_output_dir()

    # Get campaign IDs to fetch
    if args.campaign_ids:
        # Override: use provided IDs
        campaign_ids = [int(x.strip()) for x in args.campaign_ids.split(",")]
        print(f"Using provided campaign IDs: {campaign_ids}")
    else:
        # Load from campaigns.json
        campaigns, err = load_campaigns(output_dir)
        if err:
            print(f"ERROR: {err}", file=sys.stderr)
            return 1
        campaign_ids = [c.get("id") for c in campaigns if c.get("id")]
        print(f"Loaded {len(campaign_ids)} campaign IDs from campaigns.json")

    if not campaign_ids:
        print("ERROR: No campaign IDs to process", file=sys.stderr)
        return 1

    # Fetch conversations for each campaign
    client = DatagenClient()
    conversations_dir = output_dir / "conversations"
    total_conversations = 0
    errors = []

    print(f"\nFetching conversations for {len(campaign_ids)} campaigns...")

    for campaign_id in campaign_ids:
        # Skip if exists and flag set
        existing_file = conversations_dir / f"{campaign_id}.json"
        if args.skip_existing and existing_file.exists():
            print(f"  {campaign_id}: skipped (already exists)")
            continue

        conversations, err = fetch_conversations_for_campaign(client, campaign_id)

        if err:
            print(f"  {campaign_id}: ERROR - {err}")
            errors.append((campaign_id, err))
            continue

        output_path, err = save_conversations(conversations, campaign_id, output_dir)

        if err:
            print(f"  {campaign_id}: ERROR - {err}")
            errors.append((campaign_id, err))
            continue

        total_conversations += len(conversations)
        print(f"  {campaign_id}: {len(conversations)} conversations")

    # Summary
    print(f"\nConversations fetched: {total_conversations}")
    print(f"Output directory: {conversations_dir}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for campaign_id, err in errors:
            print(f"  - {campaign_id}: {err}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
