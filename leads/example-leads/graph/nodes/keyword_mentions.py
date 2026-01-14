"""
Graph: Keyword Mentions

Find posts from a LinkedIn profile that mention specific keywords.
Replaces the hardcoded linkedin_claude_mentions with a configurable graph.

This is a GRAPH (not a primitive) because:
- It declares specific output columns (mentions_count, mention_urls, etc.)
- It composes multiple primitives (linkedin_posts + filter_by + aggregate)
- It contains logic specific to this enrichment need
"""

import sys
from pathlib import Path

# Add scripts to path for primitive imports
# From: leads/example-leads/graph/nodes/ -> linkedin-outreach/scripts/
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives import linkedin_posts, filter_by, aggregate
from primitives.base import Graph


class KeywordMentions(Graph):
    """Find posts mentioning specific keywords from LinkedIn profile."""

    # Configuration - can be overridden in subclass or init
    keywords = ["claude code", "claude-code", "claudecode"]
    output_prefix = "claude"  # Used for column names

    @property
    def input_cols(self) -> list[str]:
        return ["linkedin_url"]

    @property
    def output_cols(self) -> list[str]:
        prefix = self.output_prefix
        return [
            f"{prefix}_mentions_count",
            f"{prefix}_mention_urls",
            f"{prefix}_first_mention_date"
        ]

    def __init__(self, keywords: list[str] = None, output_prefix: str = None):
        """
        Initialize with optional custom keywords and prefix.

        Args:
            keywords: List of keywords to search for (OR logic)
            output_prefix: Prefix for output columns (e.g., "claude" -> "claude_mentions_count")
        """
        if keywords is not None:
            self.keywords = keywords
        if output_prefix is not None:
            self.output_prefix = output_prefix

    def run(self, row: dict) -> tuple[dict, str]:
        prefix = self.output_prefix

        # Step 1: Fetch posts (primitive)
        posts_result, err = linkedin_posts(linkedin_url=row["linkedin_url"])
        if err:
            return {}, f"failed to fetch posts: {err}"

        posts = posts_result.get("posts", [])
        if not posts:
            return {
                f"{prefix}_mentions_count": 0,
                f"{prefix}_mention_urls": "",
                f"{prefix}_first_mention_date": ""
            }, ""

        # Step 2: Filter by keywords (primitive)
        filtered_result, err = filter_by(
            items=posts,
            field="text",
            keywords=self.keywords,
            case_sensitive=False
        )
        if err:
            return {}, f"failed to filter posts: {err}"

        filtered = filtered_result.get("filtered", [])
        if not filtered:
            return {
                f"{prefix}_mentions_count": 0,
                f"{prefix}_mention_urls": "",
                f"{prefix}_first_mention_date": ""
            }, ""

        # Step 3: Aggregate results (primitive)
        agg_result, err = aggregate(
            items=filtered,
            count_as="count",
            collect_field="url",
            collect_limit=5,
            date_field="date"
        )
        if err:
            return {}, f"failed to aggregate: {err}"

        # Step 4: Format for output columns
        urls = agg_result.get("collected", [])
        urls_string = ", ".join(urls) if urls else ""

        return {
            f"{prefix}_mentions_count": agg_result.get("count", 0),
            f"{prefix}_mention_urls": urls_string,
            f"{prefix}_first_mention_date": agg_result.get("first_date", "")
        }, ""


# Convenience: Pre-configured instances for common use cases
claude_mentions = KeywordMentions(
    keywords=["claude code", "claude-code", "claudecode", "@claude"],
    output_prefix="claude"
)

datagen_mentions = KeywordMentions(
    keywords=["datagen", "data gen", "datagen.dev"],
    output_prefix="datagen"
)

ai_agent_mentions = KeywordMentions(
    keywords=["ai agent", "ai agents", "agentic", "agent framework"],
    output_prefix="ai_agent"
)
