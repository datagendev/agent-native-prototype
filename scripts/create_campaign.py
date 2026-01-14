#!/usr/bin/env python3
"""
Create a new LinkedIn outreach campaign with custom columns.

This script:
1. Creates a campaign registry entry
2. Creates a campaign-specific table with standard + custom columns
3. Optionally populates it from existing engagements
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from datagen_sdk import DatagenClient


def _load_env_file(path: Path) -> None:
    """Load environment variables from a simple KEY=VALUE file."""
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
    """Ensure DATAGEN_API_KEY is loaded from ../.env"""
    _load_env_file(Path("../.env"))
    if not os.getenv("DATAGEN_API_KEY"):
        raise RuntimeError(
            "DATAGEN_API_KEY not set. Load it from ../.env or export it."
        )


def sanitize_table_name(name: str) -> str:
    """Convert campaign name to valid PostgreSQL table name."""
    # Convert to lowercase
    name = name.lower()
    # Replace spaces and special chars with underscores
    name = re.sub(r'[^a-z0-9_]', '_', name)
    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    # Ensure it starts with a letter
    if name and name[0].isdigit():
        name = 'campaign_' + name
    # Prefix with campaign_ if not already
    if not name.startswith('campaign_'):
        name = 'campaign_' + name
    return name


def create_campaign(
    client: DatagenClient,
    name: str,
    description: str,
    custom_columns: dict[str, str],
    campaign_type: str = "post_engagement"
) -> dict[str, Any]:
    """
    Create a new campaign with custom columns.

    Args:
        client: DatagenClient instance
        name: Campaign name (human-readable)
        description: Campaign description
        custom_columns: Dict of column_name -> column_type (e.g., {"comment_text": "TEXT"})
        campaign_type: Type of campaign

    Returns:
        Dict with campaign_id, table_name, and creation status
    """

    # Generate table name
    table_name = sanitize_table_name(name)

    print(f"Creating campaign: {name}")
    print(f"  Table name: {table_name}")
    print(f"  Custom columns: {len(custom_columns)}")

    # Build table schema JSON for registry
    table_schema = {}
    for col_name, col_type in custom_columns.items():
        table_schema[col_name] = {
            "type": col_type,
            "description": f"Custom field: {col_name}"
        }

    # Step 1: Register campaign
    print("\n1. Registering campaign...")
    insert_campaign_sql = f"""
    INSERT INTO campaigns (name, description, status, campaign_type, table_name, table_schema)
    VALUES (
        '{name.replace("'", "''")}',
        '{description.replace("'", "''")}',
        'draft',
        '{campaign_type}',
        '{table_name}',
        '{json.dumps(table_schema)}'::jsonb
    )
    RETURNING id, table_name;
    """

    result = client.execute_tool(
        "mcp_Neon_run_sql",
        {
            "params": {
                "projectId": "blue-tree-25780810",
                "branchId": "br-cool-leaf-afau0ra8",
                "databaseName": "neondb",
                "sql": insert_campaign_sql
            }
        }
    )

    # Parse result
    campaign_data = result[0][0] if result and result[0] else {}
    campaign_id = campaign_data.get('id')

    print(f"  ✓ Campaign registered with ID: {campaign_id}")

    # Step 2: Create campaign table
    print("\n2. Creating campaign table...")

    # Build column definitions
    custom_col_defs = []
    for col_name, col_type in custom_columns.items():
        custom_col_defs.append(f"    {col_name} {col_type}")

    custom_cols_sql = ",\n".join(custom_col_defs) if custom_col_defs else ""
    if custom_cols_sql:
        custom_cols_sql = ",\n" + custom_cols_sql

    # Create table
    create_table_sql = f"""
    CREATE TABLE {table_name} (
        id SERIAL PRIMARY KEY,
        prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
        status TEXT DEFAULT 'pending',
        added_at TIMESTAMPTZ DEFAULT NOW(),
        contacted_at TIMESTAMPTZ,
        responded_at TIMESTAMPTZ{custom_cols_sql},
        UNIQUE(prospect_id)
    )
    """

    client.execute_tool(
        "mcp_Neon_run_sql",
        {
            "params": {
                "projectId": "blue-tree-25780810",
                "branchId": "br-cool-leaf-afau0ra8",
                "databaseName": "neondb",
                "sql": create_table_sql
            }
        }
    )

    # Create indexes separately
    index1_sql = f"CREATE INDEX idx_{table_name}_prospect ON {table_name}(prospect_id)"
    index2_sql = f"CREATE INDEX idx_{table_name}_status ON {table_name}(status)"

    client.execute_tool(
        "mcp_Neon_run_sql",
        {
            "params": {
                "projectId": "blue-tree-25780810",
                "branchId": "br-cool-leaf-afau0ra8",
                "databaseName": "neondb",
                "sql": index1_sql
            }
        }
    )

    client.execute_tool(
        "mcp_Neon_run_sql",
        {
            "params": {
                "projectId": "blue-tree-25780810",
                "branchId": "br-cool-leaf-afau0ra8",
                "databaseName": "neondb",
                "sql": index2_sql
            }
        }
    )

    print(f"  ✓ Table created: {table_name}")

    return {
        "campaign_id": campaign_id,
        "table_name": table_name,
        "custom_columns": list(custom_columns.keys()),
        "status": "created"
    }


def populate_from_post(
    client: DatagenClient,
    table_name: str,
    post_url: str,
    column_mappings: dict[str, str]
) -> int:
    """
    Populate campaign table from engagements on a specific post.

    Args:
        client: DatagenClient instance
        table_name: Campaign table name
        post_url: LinkedIn post URL to filter by
        column_mappings: Dict mapping campaign columns to data source
                        e.g., {"comment_text": "e.comment", "post_url": "lp.post_url"}

    Returns:
        Number of prospects added
    """

    print(f"\n3. Populating {table_name} from post...")
    print(f"   Post: {post_url[:60]}...")

    # Build SELECT clause for custom columns
    custom_selects = []
    for col_name, source in column_mappings.items():
        custom_selects.append(f"    {source} as {col_name}")

    custom_select_sql = ",\n".join(custom_selects) if custom_selects else ""
    if custom_select_sql:
        custom_select_sql = ",\n" + custom_select_sql

    # Build column list for INSERT
    custom_col_names = list(column_mappings.keys())
    insert_cols = ", ".join(["prospect_id"] + custom_col_names)

    populate_sql = f"""
    INSERT INTO {table_name} ({insert_cols})
    SELECT
        p.id{custom_select_sql}
    FROM engagements e
    JOIN prospects p ON p.id = e.prospect_id
    JOIN linkedin_posts lp ON lp.id = e.post_id
    WHERE lp.post_url = '{post_url.replace("'", "''")}'
    ON CONFLICT (prospect_id) DO NOTHING
    RETURNING id;
    """

    result = client.execute_tool(
        "mcp_Neon_run_sql",
        {
            "params": {
                "projectId": "blue-tree-25780810",
                "branchId": "br-cool-leaf-afau0ra8",
                "databaseName": "neondb",
                "sql": populate_sql
            }
        }
    )

    count = len(result[0]) if result and result[0] else 0
    print(f"   ✓ Added {count} prospects")

    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a new LinkedIn outreach campaign with custom columns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create campaign with custom columns
  python create_campaign.py \\
    --name "Jordan Crawford Post Engagement" \\
    --description "Follow up with people who asked for the link" \\
    --columns comment_text:TEXT post_url:TEXT urgency_level:INTEGER

  # Create and populate from a specific post
  python create_campaign.py \\
    --name "Jordan Crawford Post Engagement" \\
    --description "Follow up with people who asked for the link" \\
    --columns comment_text:TEXT post_url:TEXT \\
    --populate-from-post "https://linkedin.com/posts/jordancrawford..." \\
    --map comment_text:e.comment post_url:lp.post_url
"""
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Campaign name (human-readable)"
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Campaign description"
    )
    parser.add_argument(
        "--columns",
        nargs="+",
        required=True,
        help="Custom columns in format: col_name:TYPE (e.g., comment_text:TEXT urgency:INTEGER)"
    )
    parser.add_argument(
        "--campaign-type",
        default="post_engagement",
        help="Campaign type (default: post_engagement)"
    )
    parser.add_argument(
        "--populate-from-post",
        help="Optional: LinkedIn post URL to populate from"
    )
    parser.add_argument(
        "--map",
        nargs="+",
        help="Column mappings for population: col_name:source (e.g., comment_text:e.comment)"
    )

    args = parser.parse_args()

    # Parse custom columns
    custom_columns = {}
    for col_spec in args.columns:
        if ":" not in col_spec:
            print(f"Error: Invalid column spec '{col_spec}'. Use format: name:TYPE")
            return
        col_name, col_type = col_spec.split(":", 1)
        custom_columns[col_name.strip()] = col_type.strip().upper()

    # Load environment
    _ensure_env_loaded()
    client = DatagenClient()

    # Create campaign
    try:
        result = create_campaign(
            client,
            args.name,
            args.description,
            custom_columns,
            args.campaign_type
        )

        print(f"\n✓ Campaign created successfully!")
        print(f"  Campaign ID: {result['campaign_id']}")
        print(f"  Table name: {result['table_name']}")

        # Populate if requested
        if args.populate_from_post:
            if not args.map:
                print("\nError: --map required when using --populate-from-post")
                return

            # Parse column mappings
            column_mappings = {}
            for mapping in args.map:
                if ":" not in mapping:
                    print(f"Error: Invalid mapping '{mapping}'. Use format: col_name:source")
                    return
                col_name, source = mapping.split(":", 1)
                column_mappings[col_name.strip()] = source.strip()

            count = populate_from_post(
                client,
                result['table_name'],
                args.populate_from_post,
                column_mappings
            )

            # Update campaign metrics
            update_sql = f"""
            UPDATE campaigns
            SET total_prospects = {count},
                status = 'active',
                updated_at = NOW()
            WHERE id = {result['campaign_id']};
            """

            client.execute_tool(
                "mcp_Neon_run_sql",
                {
                    "params": {
                        "projectId": "blue-tree-25780810",
                        "branchId": "br-cool-leaf-afau0ra8",
                        "databaseName": "neondb",
                        "sql": update_sql
                    }
                }
            )

            print(f"\n✓ Campaign populated and activated!")

    except Exception as e:
        print(f"\nError creating campaign: {e}")
        return


if __name__ == "__main__":
    main()
