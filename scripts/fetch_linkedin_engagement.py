#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

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


def _sql_quote(text: str) -> str:
    """Escape single quotes for SQL."""
    return "'" + text.replace("'", "''") + "'"


def _sql_text(value: Optional[str]) -> str:
    """Convert string to SQL, handling NULL."""
    if value is None:
        return "NULL"
    return _sql_quote(value)


def _sql_jsonb(value: Any) -> str:
    """Convert Python object to SQL JSONB."""
    dumped = json.dumps(value, ensure_ascii=False)
    return f"{_sql_quote(dumped)}::jsonb"


def _clean_linkedin_url(url: str) -> str:
    """
    Clean LinkedIn URL by removing tracking parameters.

    Example:
    Input:  https://linkedin.com/posts/...?utm_source=share&utm_medium=...
    Output: https://linkedin.com/posts/...
    """
    # Remove everything after '?' (query parameters)
    if '?' in url:
        url = url.split('?')[0]

    # Ensure it ends with '/' for consistency
    if not url.endswith('/'):
        url += '/'

    return url


def _extract_activity_id(post_url: str) -> str:
    """
    Extract activity ID from LinkedIn post URL.
    Example: https://...activity-7407257858251141120-BZqe -> 7407257858251141120
    """
    match = re.search(r'activity-(\d+)', post_url)
    if not match:
        raise ValueError(f"Could not extract activity ID from URL: {post_url}")
    return match.group(1)


def fetch_comments(client: DatagenClient, activity_id: str, post_url: str, exclude_author: Optional[str] = None) -> list[dict]:
    """
    Fetch comments using get_linkedin_person_post_comments tool.
    Returns list of engagement records ready for DB insertion.

    Args:
        exclude_author: LinkedIn public identifier to exclude (e.g., "jordancrawford")
    """
    print(f"  Calling get_linkedin_person_post_comments with activity_id={activity_id}...")

    resp = client.execute_tool(
        "get_linkedin_person_post_comments",
        {"activity_id": activity_id}
    )

    # Validate response
    payload = resp if isinstance(resp, dict) else (resp[0] if isinstance(resp, list) and resp else {})
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected response format from get_linkedin_person_post_comments")

    comments = payload.get("comments", [])
    if not isinstance(comments, list):
        comments = []

    records = []
    excluded_count = 0

    for comment in comments:
        if not isinstance(comment, dict):
            continue

        author = comment.get("author", {})
        if not isinstance(author, dict):
            author = {}

        # Check if we should exclude this author
        author_identifier = author.get("authorPublicIdentifier")
        if exclude_author and author_identifier == exclude_author:
            excluded_count += 1
            print(f"  Excluding comment from post author: {author.get('authorName')}")
            continue

        # Build profile enrichment JSON
        profile_data = {
            "name": author.get("authorName"),
            "linkedin_url": author.get("authorLinkedinUrl"),
            "activity_date": datetime.now(timezone.utc).isoformat()
        }

        record = {
            "linkedin_post_url": post_url,
            "engage_type": "comment",
            "comment": comment.get("text"),
            "reaction_type": None,  # Comments don't have reaction types
            "profile_enrichment": profile_data,
            "engager_linkedin_url": author.get("authorLinkedinUrl"),
            "activity_timestamp_ms": comment.get("activityDate")
        }
        records.append(record)

    if excluded_count > 0:
        print(f"  Excluded {excluded_count} comment(s) from author")

    return records


def fetch_reactions(client: DatagenClient, activity_id: str, post_url: str) -> list[dict]:
    """
    Fetch reactions using get_linkedin_person_post_reactions tool.
    Returns list of engagement records ready for DB insertion.
    """
    print(f"  Calling get_linkedin_person_post_reactions with activity_id={activity_id}...")

    resp = client.execute_tool(
        "get_linkedin_person_post_reactions",
        {"activity_id": activity_id}
    )

    payload = resp if isinstance(resp, dict) else (resp[0] if isinstance(resp, list) and resp else {})
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected response format from get_linkedin_person_post_reactions")

    reactions = payload.get("reactions", [])
    if not isinstance(reactions, list):
        reactions = []

    records = []
    for reaction in reactions:
        if not isinstance(reaction, dict):
            continue

        author = reaction.get("author", {})
        if not isinstance(author, dict):
            author = {}

        reaction_type = reaction.get("type", "UNKNOWN")

        # Profile enrichment with reaction data
        profile_data = {
            "name": author.get("authorName"),
            "linkedin_url": author.get("authorUrl"),
            "reaction_type": reaction_type,
            "activity_date": datetime.now(timezone.utc).isoformat()
        }

        record = {
            "linkedin_post_url": post_url,
            "engage_type": "reaction",
            "comment": None,  # Reactions don't have comment text
            "reaction_type": reaction_type,  # Store reaction type separately
            "profile_enrichment": profile_data,
            "engager_linkedin_url": author.get("authorUrl"),  # LinkedIn profile URL
            "activity_timestamp_ms": None  # Reactions don't include timestamp
        }
        records.append(record)

    return records


def save_to_neon(client: DatagenClient, records: list[dict], post_url: str) -> int:
    """
    Insert engagement records into new normalized schema.
    Returns number of engagements inserted.

    Schema:
    - prospects: Central contact database
    - linkedin_posts: Posts being tracked
    - engagements: Links prospects to posts with engagement data
    """
    project_id = "blue-tree-25780810"
    branch_id = "br-cool-leaf-afau0ra8"
    database_name = "neondb"

    if not records:
        return 0

    # Step 1: Upsert the LinkedIn post
    print(f"  Upserting post record...")
    post_sql = f"""
    INSERT INTO linkedin_posts (post_url, last_scraped_at)
    VALUES ({_sql_text(post_url)}, NOW())
    ON CONFLICT (post_url)
    DO UPDATE SET
        last_scraped_at = NOW(),
        updated_at = NOW()
    RETURNING id;
    """

    try:
        result = client.execute_tool(
            "mcp_Neon_run_sql",
            {
                "params": {
                    "projectId": project_id,
                    "branchId": branch_id,
                    "databaseName": database_name,
                    "sql": post_sql
                }
            }
        )
        post_id = result[0][0].get('id') if result and result[0] else None
        if not post_id:
            raise RuntimeError("Failed to get post_id")
        print(f"    ✓ Post ID: {post_id}")
    except Exception as e:
        print(f"  Error upserting post: {e}")
        return 0

    # Step 2: Process each engagement
    inserted = 0
    for i, record in enumerate(records, 1):
        profile_enrichment = record.get('profile_enrichment', {})
        name = profile_enrichment.get('name', 'Unknown')
        linkedin_url = record.get('engager_linkedin_url')

        if not linkedin_url:
            print(f"  Skipping {i}/{len(records)}: No LinkedIn URL")
            continue

        try:
            # Step 2a: Upsert prospect
            prospect_sql = f"""
            INSERT INTO prospects (linkedin_url, name, discovered_via, profile_data, first_seen_at)
            VALUES (
                {_sql_text(linkedin_url)},
                {_sql_text(name)},
                'post_engagement',
                {_sql_jsonb(profile_enrichment)},
                NOW()
            )
            ON CONFLICT (linkedin_url)
            DO UPDATE SET
                name = COALESCE(EXCLUDED.name, prospects.name),
                profile_data = prospects.profile_data || EXCLUDED.profile_data,
                updated_at = NOW()
            RETURNING id;
            """

            result = client.execute_tool(
                "mcp_Neon_run_sql",
                {
                    "params": {
                        "projectId": project_id,
                        "branchId": branch_id,
                        "databaseName": database_name,
                        "sql": prospect_sql
                    }
                }
            )

            prospect_id = result[0][0].get('id') if result and result[0] else None
            if not prospect_id:
                print(f"  Warning: Failed to get prospect_id for {i}/{len(records)}")
                continue

            # Step 2b: Insert engagement
            engagement_sql = f"""
            INSERT INTO engagements (
                prospect_id,
                post_id,
                engage_type,
                comment,
                reaction_type,
                engaged_at
            ) VALUES (
                {prospect_id},
                {post_id},
                {_sql_text(record['engage_type'])},
                {_sql_text(record.get('comment'))},
                {_sql_text(record.get('reaction_type'))},
                NOW()
            )
            ON CONFLICT (prospect_id, post_id, engage_type) DO NOTHING
            RETURNING id;
            """

            result = client.execute_tool(
                "mcp_Neon_run_sql",
                {
                    "params": {
                        "projectId": project_id,
                        "branchId": branch_id,
                        "databaseName": database_name,
                        "sql": engagement_sql
                    }
                }
            )

            if result and result[0]:
                inserted += 1
                print(f"  Inserted {i}/{len(records)}: {name}")
            else:
                print(f"  Skipped {i}/{len(records)}: {name} (duplicate)")

        except Exception as e:
            print(f"  Warning: Failed to process record {i}/{len(records)}: {e}")
            continue

    # Step 3: Update post stats
    update_stats_sql = f"""
    UPDATE linkedin_posts
    SET
        total_comments = (SELECT COUNT(*) FROM engagements WHERE post_id = {post_id} AND engage_type = 'comment'),
        total_reactions = (SELECT COUNT(*) FROM engagements WHERE post_id = {post_id} AND engage_type = 'reaction'),
        updated_at = NOW()
    WHERE id = {post_id};
    """

    try:
        client.execute_tool(
            "mcp_Neon_run_sql",
            {
                "params": {
                    "projectId": project_id,
                    "branchId": branch_id,
                    "databaseName": database_name,
                    "sql": update_stats_sql
                }
            }
        )
    except Exception as e:
        print(f"  Warning: Failed to update post stats: {e}")

    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch LinkedIn post engagement and save to Neon database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to preview comments
  python fetch_linkedin_engagement.py --type comments --dry-run \\
    "https://www.linkedin.com/posts/author_text-activity-123-xyz"

  # Fetch and insert comments
  python fetch_linkedin_engagement.py --type comments \\
    "https://www.linkedin.com/posts/author_text-activity-123-xyz"

  # Fetch and insert reactions
  python fetch_linkedin_engagement.py --type reactions \\
    "https://www.linkedin.com/posts/author_text-activity-123-xyz"
"""
    )
    parser.add_argument(
        "post_url",
        help="LinkedIn post URL (e.g., https://linkedin.com/posts/...activity-123...)"
    )
    parser.add_argument(
        "--type",
        choices=["comments", "reactions"],
        required=True,
        help="Type of engagement to fetch"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch data but don't save to database"
    )
    parser.add_argument(
        "--exclude-author",
        help="LinkedIn public identifier of post author to exclude (e.g., 'jordancrawford')"
    )

    args = parser.parse_args()

    # Load environment
    _ensure_env_loaded()
    client = DatagenClient()

    # Clean the post URL
    clean_url = _clean_linkedin_url(args.post_url)
    if clean_url != args.post_url:
        print(f"Cleaned URL: {clean_url}")

    # Extract activity ID
    try:
        activity_id = _extract_activity_id(clean_url)
        print(f"Extracted activity ID: {activity_id}")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Fetch engagement data
    print(f"Fetching {args.type} for post...")
    try:
        if args.type == "comments":
            records = fetch_comments(client, activity_id, clean_url, args.exclude_author)
        else:
            records = fetch_reactions(client, activity_id, clean_url)
    except Exception as e:
        print(f"Error fetching {args.type}: {e}")
        return

    print(f"Found {len(records)} {args.type}")

    if len(records) == 0:
        print("No engagement data found. Exiting.")
        return

    if args.dry_run:
        print("\n[DRY RUN] Would insert the following records:")
        for i, rec in enumerate(records[:5], 1):
            name = rec['profile_enrichment'].get('name', 'Unknown')
            comment_preview = rec.get('comment', '')
            if comment_preview and len(comment_preview) > 50:
                comment_preview = comment_preview[:50] + "..."
            print(f"\n{i}. {rec['engage_type']}: {name}")
            if comment_preview:
                print(f"   {comment_preview}")
        if len(records) > 5:
            print(f"\n... and {len(records) - 5} more")
        return

    # Save to database
    print("\nSaving to Neon database...")
    inserted = save_to_neon(client, records, clean_url)
    print(f"\nSuccessfully inserted {inserted}/{len(records)} records")


if __name__ == "__main__":
    main()
