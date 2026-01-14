#!/usr/bin/env python3
"""
Update city column in linkedin_outreach table from HeyReach export data
"""

import csv
import os
from datagen_sdk import DatagenClient

# Ensure API key is set
if not os.getenv("DATAGEN_API_KEY"):
    raise RuntimeError("DATAGEN_API_KEY not set")

client = DatagenClient()

# Read HeyReach CSV export
import os.path
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "../exports/heyreach_contacted_leads_20251221T060840Z.csv")

def normalize_url(url):
    """Normalize LinkedIn URL for matching"""
    if not url:
        return url
    # Remove trailing slash
    url = url.rstrip('/')
    # Add back trailing slash for consistency
    return url + '/'

print("Reading HeyReach export CSV...")
location_map = {}

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        linkedin_url = normalize_url(row['leadProfileUrl'])
        location = row['leadLocation']

        # Store the mapping
        if linkedin_url and location:
            location_map[linkedin_url] = location

print(f"Found {len(location_map)} prospects with location data")

# Update database
print("\nUpdating city column in Neon database...")
updated_count = 0
error_count = 0

for linkedin_url, location in location_map.items():
    try:
        # Update the city column
        sql = f"""
        UPDATE linkedin_outreach
        SET city = '{location.replace("'", "''")}',
            updated_at = now()
        WHERE engager_linkedin_url = '{linkedin_url}'
        """

        result = client.execute_tool(
            "mcp_Neon_run_sql",
            {
                "params": {
                    "projectId": "blue-tree-25780810",
                    "sql": sql
                }
            }
        )

        updated_count += 1
        print(f"✓ Updated: {location}")

    except Exception as e:
        error_count += 1
        print(f"✗ Error updating {linkedin_url}: {e}")

print(f"\n{'='*60}")
print(f"Summary:")
print(f"  Total prospects: {len(location_map)}")
print(f"  Successfully updated: {updated_count}")
print(f"  Errors: {error_count}")
print(f"{'='*60}")

# Show sample of updated data
print("\nSample of updated records:")
result = client.execute_tool(
    "mcp_Neon_run_sql",
    {
        "params": {
            "projectId": "blue-tree-25780810",
            "sql": """
            SELECT
                profile_enrichment->>'name' as name,
                city,
                engager_linkedin_url
            FROM linkedin_outreach
            WHERE city IS NOT NULL
            ORDER BY id
            LIMIT 10;
            """
        }
    }
)

for record in result[0]:
    print(f"  • {record['name']:30} → {record['city']}")
