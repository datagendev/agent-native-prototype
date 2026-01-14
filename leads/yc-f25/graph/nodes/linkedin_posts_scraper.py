"""
Node: LinkedIn Posts Scraper

Fetch recent posts from a LinkedIn profile and provide summary statistics.
Extracts post count, latest post details, and generates an AI summary.

This node is designed to enrich lead data with founder/executive social signals.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add scripts to path for primitive imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives import linkedin_posts, extract_structured
from primitives.base import Graph


class LinkedInPostsScraper(Graph):
    """Scrape and analyze recent LinkedIn posts from a profile."""

    def __init__(self, max_posts: int = 10, output_prefix: str = None):
        """
        Initialize LinkedIn posts scraper.

        Args:
            max_posts: Maximum number of posts to fetch (default: 10)
            output_prefix: Prefix for output columns (default: None)
        """
        self.max_posts = max_posts
        self.output_prefix = output_prefix

    @property
    def input_cols(self) -> list[str]:
        return ["founder_linkedin_url"]

    @property
    def output_cols(self) -> list[str]:
        prefix = f"{self.output_prefix}_" if self.output_prefix else ""
        return [
            f"{prefix}recent_posts_count",
            f"{prefix}latest_post_text",
            f"{prefix}latest_post_date",
            f"{prefix}posts_summary"
        ]

    def run(self, row: dict) -> tuple[dict, str]:
        linkedin_url = row.get("founder_linkedin_url", "")
        prefix = f"{self.output_prefix}_" if self.output_prefix else ""

        # Default empty results
        default_result = {
            f"{prefix}recent_posts_count": 0,
            f"{prefix}latest_post_text": "",
            f"{prefix}latest_post_date": "",
            f"{prefix}posts_summary": ""
        }

        if not linkedin_url:
            return default_result, "empty founder_linkedin_url"

        # Step 1: Fetch LinkedIn posts using primitive
        posts_result, err = linkedin_posts(
            linkedin_url=linkedin_url,
            limit=self.max_posts
        )

        if err:
            return default_result, f"failed to fetch posts: {err}"

        posts = posts_result.get("posts", [])

        if not posts:
            return default_result, ""

        # Step 2: Extract key information
        posts_count = len(posts)
        latest_post = posts[0] if posts else {}
        latest_text = latest_post.get("text", "")
        latest_date = latest_post.get("date", "")

        # Truncate latest post text to 500 chars for storage
        if len(latest_text) > 500:
            latest_text = latest_text[:497] + "..."

        # Step 3: Generate AI summary of all posts
        posts_summary = ""
        if posts:
            # Prepare text from all posts for summarization
            posts_text = "\n\n".join([
                f"Post {i+1} ({post.get('date', 'unknown date')}):\n{post.get('text', '')[:300]}"
                for i, post in enumerate(posts[:self.max_posts])
            ])

            # Use extract_structured to generate a concise summary
            summary_result, summary_err = extract_structured(
                text=posts_text,
                schema={
                    "summary": {
                        "type": "string",
                        "description": "A 2-3 sentence summary of the main topics, themes, and focus areas across all posts"
                    },
                    "key_topics": {
                        "type": "array",
                        "description": "List of 3-5 key topics or themes mentioned (e.g., ['AI agents', 'startup growth', 'technical leadership'])"
                    }
                },
                context=f"Analyzing {posts_count} recent LinkedIn posts from founder to identify key themes and focus areas"
            )

            if not summary_err:
                extracted = summary_result.get("extracted", {})
                summary_text = extracted.get("summary", "")
                key_topics = extracted.get("key_topics", [])

                # Combine summary and key topics
                if summary_text:
                    posts_summary = summary_text
                if key_topics:
                    topics_str = ", ".join(key_topics)
                    posts_summary = f"{posts_summary} Key topics: {topics_str}" if posts_summary else f"Key topics: {topics_str}"

        return {
            f"{prefix}recent_posts_count": posts_count,
            f"{prefix}latest_post_text": latest_text,
            f"{prefix}latest_post_date": latest_date,
            f"{prefix}posts_summary": posts_summary
        }, ""
