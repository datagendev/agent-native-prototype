#!/usr/bin/env python3
"""
Convert Eric Osiu's posts JSON to markdown format and search for Claude Code mentions
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def convert_to_markdown(json_file):
    """Convert JSON posts to markdown format"""

    with open(json_file, 'r') as f:
        data = json.load(f)

    profile_url = data.get("profile_url", "")
    fetched_at = data.get("fetched_at", "")
    total_posts = data.get("total_posts", 0)
    posts = data.get("posts", [])

    # Create markdown output
    md_lines = []
    md_lines.append(f"# Eric Osiu's LinkedIn Posts\n")
    md_lines.append(f"**Profile**: {profile_url}\n")
    md_lines.append(f"**Fetched**: {fetched_at}\n")
    md_lines.append(f"**Total Posts**: {total_posts}\n")
    md_lines.append("\n---\n")

    # Search for Claude Code mentions
    claude_code_posts = []

    for i, post in enumerate(posts, 1):
        text = post.get("text", "")
        activity_date = post.get("activityDate", "")
        reactions = post.get("reactionsCount", 0)
        comments = post.get("commentsCount", 0)
        activity_url = post.get("activityUrl", "")

        # Check for Claude Code mentions
        if "claude" in text.lower() and "code" in text.lower():
            claude_code_posts.append({
                "number": i,
                "text": text,
                "url": activity_url,
                "date": activity_date,
                "reactions": reactions,
                "comments": comments
            })

        # Add to markdown
        md_lines.append(f"\n## Post {i}\n")
        md_lines.append(f"**Date**: {activity_date}\n")
        md_lines.append(f"**Engagement**: {reactions} reactions, {comments} comments\n")
        md_lines.append(f"**URL**: {activity_url}\n\n")
        md_lines.append(f"{text}\n")
        md_lines.append("\n---\n")

    # Write markdown file
    output_file = str(json_file).replace('.json', '.md')
    with open(output_file, 'w') as f:
        f.writelines(md_lines)

    print(f"✓ Converted to markdown: {output_file}")

    # Report Claude Code findings
    print(f"\n{'='*80}")
    if claude_code_posts:
        print(f"🎯 Found {len(claude_code_posts)} posts mentioning Claude Code:\n")
        for post in claude_code_posts:
            print(f"Post #{post['number']} ({post['date']})")
            print(f"  URL: {post['url']}")
            print(f"  Engagement: {post['reactions']} reactions, {post['comments']} comments")
            preview = post['text'][:150] + "..." if len(post['text']) > 150 else post['text']
            print(f"  Preview: {preview}")
            print()
    else:
        print("❌ No posts mentioning 'Claude Code' found")
    print(f"{'='*80}")

    return output_file, claude_code_posts

if __name__ == "__main__":
    # Find the most recent Eric posts JSON file
    posts_dir = Path("posts")
    json_files = list(posts_dir.glob("eric_osiu_posts_*.json"))

    if not json_files:
        print("Error: No Eric Osiu posts JSON files found in posts/")
        sys.exit(1)

    # Get most recent file
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Converting: {latest_file}")

    convert_to_markdown(latest_file)
