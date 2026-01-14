#!/usr/bin/env python3
"""
Fetch misterbrady's recent LinkedIn posts and save to posts/misterbrady/ directory
with proper frontmatter formatting
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from datagen_sdk import DatagenClient

# Load environment variables from ../.env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Verify API key
if not os.getenv("DATAGEN_API_KEY"):
    raise RuntimeError("DATAGEN_API_KEY not set")

client = DatagenClient()

# misterbrady's LinkedIn profile
LINKEDIN_URL = "https://www.linkedin.com/in/misterbrady/"

print("="*80)
print("FETCHING MISTERBRADY'S LINKEDIN POSTS")
print("="*80)
print(f"\nProfile: {LINKEDIN_URL}\n")

# Get posts using get_linkedin_person_posts tool
print("🔍 Fetching posts...")
result = client.execute_tool(
    "get_linkedin_person_posts",
    {"linkedin_url": LINKEDIN_URL}
)

# Extract posts
posts = result.get("posts", [])
print(f"✓ Found {len(posts)} posts\n")

# Create output directory
output_dir = Path(__file__).parent.parent / "posts" / "misterbrady"
output_dir.mkdir(parents=True, exist_ok=True)

def sanitize_filename(text, max_length=50):
    """Create a safe filename from text"""
    # Remove special characters and replace spaces with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text)
    # Truncate to max length
    return text[:max_length].strip('-')

def create_markdown_post(post, index):
    """Create a markdown file for a single post with frontmatter"""

    # Extract post data
    text = post.get("text", "")
    activity_date = post.get("activityDate", "")
    reactions = post.get("reactionsCount", 0)
    comments = post.get("commentsCount", 0)
    activity_url = post.get("activityUrl", "")
    activity_id = post.get("activityId", "")

    # Parse date
    if activity_date:
        try:
            post_date = datetime.fromisoformat(activity_date.replace('Z', '+00:00'))
            date_str = post_date.strftime("%Y-%m-%d")
        except:
            date_str = datetime.now().strftime("%Y-%m-%d")
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # Create title from first line or snippet
    first_line = text.split('\n')[0] if text else f"Post {index}"
    title = first_line[:60] + "..." if len(first_line) > 60 else first_line

    # Create filename
    filename = f"{date_str}-{sanitize_filename(first_line)}.md"

    # Create frontmatter
    frontmatter = f"""---
title: "{title}"
description: "LinkedIn post by misterbrady"
category: "linkedin"
tags: ["misterbrady", "linkedin-post"]
created: {date_str}
updated: {datetime.now().strftime("%Y-%m-%d")}
status: "active"
priority: "medium"
reference: ["{activity_url}"]
author: "misterbrady"
engagement:
  reactions: {reactions}
  comments: {comments}
activityId: "{activity_id}"
---
"""

    # Create markdown content
    content = f"""{frontmatter}
# {title}

**Posted:** {date_str}
**Engagement:** {reactions} reactions, {comments} comments
**URL:** {activity_url}

---

{text}

---

*Fetched: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

    # Write to file
    output_file = output_dir / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_file, {
        "title": title,
        "date": date_str,
        "reactions": reactions,
        "comments": comments,
        "url": activity_url
    }

# Process each post
print("💾 Saving posts to markdown files...\n")
saved_posts = []

for i, post in enumerate(posts, 1):
    try:
        output_file, summary = create_markdown_post(post, i)
        saved_posts.append(summary)
        print(f"  ✓ {output_file.name}")
    except Exception as e:
        print(f"  ✗ Error processing post {i}: {e}")

# Print summary
print("\n" + "="*80)
print("COMPLETE")
print("="*80)
print(f"\n📂 Saved {len(saved_posts)} posts to: {output_dir}")
print(f"\n📊 Top posts by engagement:")

# Sort by reactions and show top 5
top_posts = sorted(saved_posts, key=lambda x: x["reactions"], reverse=True)[:5]
for i, post in enumerate(top_posts, 1):
    print(f"\n  {i}. {post['title']}")
    print(f"     → {post['reactions']} reactions, {post['comments']} comments")
    print(f"     → {post['url']}")

print("\n" + "="*80 + "\n")
