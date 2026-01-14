#!/usr/bin/env python3
"""
Update a Neon campaign record with HeyReach campaign/list IDs.

This script updates the heyreach_campaign_id and heyreach_list_id fields
in the campaigns table so that sync_heyreach_campaign_results.py can link them.
"""

import argparse
import os
import sys
from pathlib import Path

from datagen_sdk import DatagenClient


def _load_env_file(path: Path) -> None:
    """Load environment variables from a file."""
    if not path.exists() or not path.is_file():
        return
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and ((value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _ensure_env_loaded() -> None:
    """Ensure DATAGEN_API_KEY is loaded from environment or ../.env"""
    _load_env_file(Path("../.env"))
    if not os.getenv("DATAGEN_API_KEY"):
        raise RuntimeError(
            "DATAGEN_API_KEY not set. Load it from ../.env or export it."
        )


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Link a Neon campaign to a HeyReach campaign/list."
    )
    parser.add_argument("--neon-project-id", default="blue-tree-25780810")
    parser.add_argument("--neon-database", default="neondb")
    parser.add_argument("--campaign-id", type=int, required=True, help="Neon campaign ID")
    parser.add_argument("--heyreach-campaign-id", type=int, help="HeyReach campaign ID")
    parser.add_argument("--heyreach-list-id", type=int, help="HeyReach list ID")

    args = parser.parse_args()

    if not args.heyreach_campaign_id and not args.heyreach_list_id:
        parser.error("At least one of --heyreach-campaign-id or --heyreach-list-id is required")

    _ensure_env_loaded()
    client = DatagenClient()

    # Build UPDATE statement
    set_clauses = []
    if args.heyreach_campaign_id:
        set_clauses.append(f"heyreach_campaign_id = {args.heyreach_campaign_id}")
    if args.heyreach_list_id:
        set_clauses.append(f"heyreach_list_id = {args.heyreach_list_id}")

    sql = f"""
UPDATE campaigns
SET {', '.join(set_clauses)}
WHERE id = {args.campaign_id}
RETURNING id, name, heyreach_campaign_id, heyreach_list_id;
""".strip()

    print(f"Updating campaign {args.campaign_id}...")
    print(f"SQL: {sql}\n")

    result = client.execute_tool(
        "mcp_Neon_run_sql",
        {"sql": sql, "projectId": args.neon_project_id, "databaseName": args.neon_database},
    )

    if result and isinstance(result, list) and len(result) > 0:
        rows = result[0] if isinstance(result[0], list) else []
        if rows:
            row = rows[0]
            print("✅ Campaign updated successfully:")
            print(f"   ID: {row.get('id')}")
            print(f"   Name: {row.get('name')}")
            print(f"   HeyReach Campaign ID: {row.get('heyreach_campaign_id')}")
            print(f"   HeyReach List ID: {row.get('heyreach_list_id')}")
        else:
            print(f"❌ Campaign {args.campaign_id} not found")
            sys.exit(1)
    else:
        print("❌ Update failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
