#!/usr/bin/env python3
"""
Update city column in linkedin_outreach table from HeyReach export data
Matches by name since LinkedIn URLs differ between HeyReach and Neon
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

def normalize_name(name):
    """Normalize name for matching - remove emojis, extra spaces, etc."""
    if not name:
        return ""
    # Remove common emojis and special characters
    import re
    name = re.sub(r'[🦾⚙️🥾🧠💬]', '', name)
    # Normalize whitespace
    name = ' '.join(name.split())
    return name.strip().lower()

print("Reading HeyReach export CSV...")
location_map = {}

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        first_name = row['leadFirstName']
        last_name = row['leadLastName']
        location = row['leadLocation']

        if first_name and last_name and location:
            # Create full name
            full_name = f"{first_name} {last_name}"
            normalized = normalize_name(full_name)
            location_map[normalized] = {
                'location': location,
                'original_name': full_name
            }

print(f"Found {len(location_map)} prospects with location data")

# Get all prospects from Neon
print("\nFetching prospects from Neon...")
result = client.execute_tool(
    "mcp_Neon_run_sql",
    {
        "params": {
            "projectId": "blue-tree-25780810",
            "sql": "SELECT id, profile_enrichment->>'name' as name, engager_linkedin_url FROM linkedin_outreach;"
        }
    }
)

prospects = result[0]
print(f"Found {len(prospects)} prospects in database")

# Match and update
print("\nMatching and updating...")
matched_count = 0
updated_count = 0
error_count = 0
not_found = []

for prospect in prospects:
    db_name = prospect['name']
    normalized_db_name = normalize_name(db_name)

    if normalized_db_name in location_map:
        matched_count += 1
        location = location_map[normalized_db_name]['location']
        prospect_id = prospect['id']

        try:
            # Update the city column
            sql = f"""
            UPDATE linkedin_outreach
            SET city = '{location.replace("'", "''")}',
                updated_at = now()
            WHERE id = {prospect_id}
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

            updated_count += 1
            print(f"✓ {db_name:35} → {location}")

        except Exception as e:
            error_count += 1
            print(f"✗ Error updating {db_name}: {e}")
    else:
        not_found.append(db_name)

print(f"\n{'='*80}")
print(f"Summary:")
print(f"  Total in database: {len(prospects)}")
print(f"  Total in HeyReach: {len(location_map)}")
print(f"  Matched: {matched_count}")
print(f"  Successfully updated: {updated_count}")
print(f"  Errors: {error_count}")
print(f"  Not found in HeyReach: {len(not_found)}")
print(f"{'='*80}")

if not_found and len(not_found) <= 10:
    print("\nProspects not found in HeyReach export:")
    for name in not_found[:10]:
        print(f"  • {name}")

# Verify updates
print("\nVerifying updates...")
result = client.execute_tool(
    "mcp_Neon_run_sql",
    {
        "params": {
            "projectId": "blue-tree-25780810",
            "sql": """
            SELECT
                COUNT(*) as total,
                COUNT(city) as with_city,
                COUNT(CASE WHEN city IS NULL THEN 1 END) as without_city
            FROM linkedin_outreach;
            """
        }
    }
)

stats = result[0][0]
print(f"  Total records: {stats['total']}")
print(f"  With city: {stats['with_city']}")
print(f"  Without city: {stats['without_city']}")
