#!/usr/bin/env python3
"""
Add commenters from Jacob Dietle's GTM Context OS post to linkedin_outreach table
"""

import json
import os
from datetime import datetime
from datagen_sdk import DatagenClient

# Ensure API key is set
if not os.getenv("DATAGEN_API_KEY"):
    raise RuntimeError("DATAGEN_API_KEY not set")

client = DatagenClient()

# Jacob Dietle's post URL
POST_URL = "https://www.linkedin.com/posts/jacob-dietle_who-wants-a-gtm-context-os-quickstart-guide-activity-7403874809065234432-rzuz"
ACTIVITY_ID = "7403874809065234432"

print("Fetching comments from Jacob Dietle's post...")

# Get comments
result = client.execute_tool(
    "get_linkedin_person_post_comments",
    {"activity_id": ACTIVITY_ID}
)

comments = result.get("comments", [])
print(f"Found {len(comments)} commenters")

# Check existing prospects to avoid duplicates
print("\nChecking for existing prospects...")
existing_result = client.execute_tool(
    "mcp_Neon_run_sql",
    {
        "params": {
            "projectId": "blue-tree-25780810",
            "sql": "SELECT engager_linkedin_url FROM linkedin_outreach;"
        }
    }
)

existing_urls = set()
for row in existing_result[0]:
    if row.get('engager_linkedin_url'):
        existing_urls.add(row['engager_linkedin_url'].rstrip('/') + '/')

print(f"Found {len(existing_urls)} existing prospects")

# Add new commenters
added_count = 0
skipped_count = 0
error_count = 0

print("\nAdding new commenters...")

for comment in comments:
    author = comment.get("author", {})
    author_name = author.get("authorName", "")
    author_linkedin_url = author.get("authorLinkedinUrl", "")
    comment_text = comment.get("text", "")

    # Normalize URL
    normalized_url = author_linkedin_url.rstrip('/') + '/' if author_linkedin_url else ""

    # Skip if already exists
    if normalized_url in existing_urls:
        skipped_count += 1
        print(f"⊘ Skipped (already exists): {author_name}")
        continue

    try:
        # Escape single quotes in strings
        safe_comment = comment_text.replace("'", "''")
        safe_name = author_name.replace("'", "''")
        safe_url = normalized_url.replace("'", "''")

        # Create profile enrichment JSON
        profile_enrichment = json.dumps({
            "name": author_name,
            "linkedin_url": author_linkedin_url,
            "activity_date": datetime.now().strftime("%Y-%m-%d")
        })

        # Insert into database
        sql = f"""
        INSERT INTO linkedin_outreach (
            linkedin_post_url,
            engage_type,
            comment,
            profile_enrichment,
            engager_linkedin_url,
            messages_sent,
            if_respond
        ) VALUES (
            '{POST_URL}',
            'comment',
            '{safe_comment}',
            '{profile_enrichment}'::jsonb,
            '{safe_url}',
            '[]'::jsonb,
            false
        );
        """

        client.execute_tool(
            "mcp_Neon_run_sql",
            {
                "params": {
                    "projectId": "blue-tree-25780810",
                    "sql": sql
                }
            }
        )

        added_count += 1
        print(f"✓ Added: {author_name}")

    except Exception as e:
        error_count += 1
        print(f"✗ Error adding {author_name}: {e}")

print(f"\n{'='*80}")
print(f"Summary:")
print(f"  Total commenters: {len(comments)}")
print(f"  New prospects added: {added_count}")
print(f"  Already existed (skipped): {skipped_count}")
print(f"  Errors: {error_count}")
print(f"{'='*80}")

# Show summary of new additions
if added_count > 0:
    print("\nVerifying new additions...")
    result = client.execute_tool(
        "mcp_Neon_run_sql",
        {
            "params": {
                "projectId": "blue-tree-25780810",
                "sql": f"""
                SELECT
                    profile_enrichment->>'name' as name,
                    comment,
                    city,
                    created_at
                FROM linkedin_outreach
                WHERE linkedin_post_url = '{POST_URL}'
                ORDER BY created_at DESC
                LIMIT 10;
                """
            }
        }
    )

    print("\nSample of newly added prospects:")
    for row in result[0][:5]:
        comment_preview = row['comment'][:50] + "..." if len(row['comment']) > 50 else row['comment']
        print(f"  • {row['name']:30} → \"{comment_preview}\"")
