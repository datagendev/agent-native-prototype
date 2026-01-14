#!/usr/bin/env python3
"""
Fetch Eric Osiu's recent LinkedIn posts and save to posts/ directory
"""

import json
import os
from datetime import datetime
from pathlib import Path
from datagen_sdk import DatagenClient

# Ensure API key is set
if not os.getenv("DATAGEN_API_KEY"):
    raise RuntimeError("DATAGEN_API_KEY not set")

client = DatagenClient()

# Eric Osiu's LinkedIn profile
LINKEDIN_URL = "https://linkedin.com/in/ericosiu"

print("Fetching Eric Osiu's recent posts...")

# Get posts using get_linkedin_person_posts tool
result = client.execute_tool(
    "get_linkedin_person_posts",
    {"linkedin_url": LINKEDIN_URL}
)

# Extract posts
posts = result.get("posts", [])
print(f"Found {len(posts)} posts")

# Create posts/ directory if it doesn't exist
posts_dir = Path("posts")
posts_dir.mkdir(exist_ok=True)

# Save to JSON file with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = posts_dir / f"eric_osiu_posts_{timestamp}.json"

with open(output_file, 'w') as f:
    json.dump({
        "profile_url": LINKEDIN_URL,
        "fetched_at": datetime.now().isoformat(),
        "total_posts": len(posts),
        "posts": posts
    }, f, indent=2, default=str)

print(f"\n✓ Saved {len(posts)} posts to {output_file}")

# Print summary
if posts:
    print("\nRecent posts:")
    for i, post in enumerate(posts[:5], 1):
        text_preview = post.get("text", "")[:100] + "..." if len(post.get("text", "")) > 100 else post.get("text", "")
        reactions = post.get("reactionsCount", 0)
        comments = post.get("commentsCount", 0)
        print(f"  {i}. {text_preview}")
        print(f"     → {reactions} reactions, {comments} comments")
