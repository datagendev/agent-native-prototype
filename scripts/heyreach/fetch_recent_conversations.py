#!/usr/bin/env python3
"""
Fetch HeyReach conversations for all LinkedIn accounts.

Step 1 of the conversation summary pipeline.
Fetches all conversations by account (NOT by campaign - campaignIds filter
causes HeyReach API timeouts). Campaign tagging happens in compile_digest.

Outputs: /tmp/heyreach-summary-{date}/conversations.json

Usage:
    python fetch_recent_conversations.py
    python fetch_recent_conversations.py --days 14
    python fetch_recent_conversations.py --output-dir /tmp/heyreach-summary-2026-02-13
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from datagen_sdk import DatagenClient


def get_output_dir() -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d")
    return Path(f"/tmp/heyreach-summary-{date_str}")


def fetch_account_ids(client: DatagenClient) -> tuple[list[int], str]:
    """
    Fetch LinkedIn account IDs.

    Returns (account_ids, error). Check error first.
    """
    try:
        result = client.execute_tool(
            "mcp_Heyreach_get_all_linked_in_accounts", {}
        )

        if isinstance(result, list) and len(result) > 0:
            items = (
                result[0].get("items", [])
                if isinstance(result[0], dict)
                else result
            )
        elif isinstance(result, dict):
            items = result.get("items", [])
        else:
            items = []

        account_ids = [item["id"] for item in items if "id" in item]
        return account_ids, ""

    except Exception as e:
        return [], f"fetch_account_ids failed: {e}"


def fetch_conversations(
    client: DatagenClient,
    account_ids: list[int],
) -> tuple[list[dict], int, str]:
    """
    Fetch all conversations for given accounts with pagination.
    Does NOT filter by campaignIds (causes HeyReach API timeouts).

    Returns (conversations, total_count, error). Check error first.
    """
    try:
        all_conversations = []
        total_count = 0
        offset = 0

        while True:
            result = client.execute_tool(
                "mcp_Heyreach_get_conversations_v2",
                {
                    "linkedInAccountIds": account_ids,
                    "campaignIds": [],
                    "limit": 100,
                    "offset": offset,
                },
            )

            if isinstance(result, list) and len(result) > 0:
                page = result[0] if isinstance(result[0], dict) else {}
                items = page.get("items", result)
                total_count = page.get("totalCount", total_count)
            elif isinstance(result, dict):
                items = result.get("items", [])
                total_count = result.get("totalCount", total_count)
            else:
                items = []

            all_conversations.extend(items)
            print(f"  Fetched {len(all_conversations)}/{total_count} conversations...")

            if len(items) < 100:
                break
            offset += 100

        return all_conversations, total_count, ""

    except Exception as e:
        return [], 0, f"fetch_conversations failed: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch HeyReach conversations"
    )
    parser.add_argument(
        "--days", type=int, default=14, help="Look back N days (default: 14)"
    )
    parser.add_argument("--output-dir", type=str, help="Override output directory")
    args = parser.parse_args()

    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)

    if not os.getenv("DATAGEN_API_KEY"):
        print("ERROR: DATAGEN_API_KEY not set", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir) if args.output_dir else get_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    client = DatagenClient()

    # Step 1: Get account IDs
    print("Fetching LinkedIn accounts...")
    account_ids, err = fetch_account_ids(client)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"  Found {len(account_ids)} accounts: {account_ids}")

    # Step 2: Fetch ALL conversations (no campaign filter - it causes timeouts)
    print("\nFetching conversations...")
    all_conversations, total_count, err = fetch_conversations(client, account_ids)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    # Save all conversations
    output_path = output_dir / "conversations.json"
    output_path.write_text(
        json.dumps(all_conversations, indent=2, ensure_ascii=False)
    )

    # Summary
    total_with_replies = sum(
        1
        for c in all_conversations
        if any(m.get("sender") == "CORRESPONDENT" for m in c.get("messages", []))
    )

    print(f"\nTotal conversations: {len(all_conversations)}")
    print(f"With replies: {total_with_replies}")
    print(f"Output: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
