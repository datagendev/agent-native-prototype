"""
Graph: Claude Code Detector

Scan a LinkedIn profile for posts mentioning Claude Code.
Returns mention count, post URLs, and a boolean flag indicating usage.

This is a GRAPH (not a primitive) because:
- It declares specific output columns (claude_code_mentions, uses_claude_code)
- It composes multiple primitives (linkedin_posts + filter_by + aggregate)
- It contains logic specific to Claude Code detection
"""

import sys
from pathlib import Path

# Add scripts to path for primitive imports
# From: leads/yc-f25/graph/nodes/ -> agent-native-prototype/scripts/
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives import linkedin_posts, filter_by, aggregate
from primitives.base import Graph


class ClaudeCodeDetector(Graph):
    """Detect Claude Code mentions in LinkedIn posts."""

    # Default configuration
    keywords = ["claude code", "claude-code", "claudecode"]
    max_posts = 50
    output_prefix = ""

    @property
    def input_cols(self) -> list[str]:
        return ["founder_linkedin_url"]

    @property
    def output_cols(self) -> list[str]:
        prefix = self.output_prefix
        sep = "_" if prefix else ""
        return [
            f"{prefix}{sep}claude_code_mentions",
            f"{prefix}{sep}claude_code_urls",
            f"{prefix}{sep}uses_claude_code"
        ]

    def __init__(
        self,
        keywords: list[str] = None,
        max_posts: int = None,
        output_prefix: str = None
    ):
        """
        Initialize Claude Code detector.

        Args:
            keywords: List of keywords to search for (OR logic)
            max_posts: Maximum number of posts to scan
            output_prefix: Prefix for output columns (e.g., "founder")
        """
        if keywords is not None:
            self.keywords = keywords
        if max_posts is not None:
            self.max_posts = max_posts
        if output_prefix is not None:
            self.output_prefix = output_prefix

    def run(self, row: dict) -> tuple[dict, str]:
        """
        Scan LinkedIn profile for Claude Code mentions.

        Returns:
            tuple: (output_dict, error_message)
        """
        prefix = self.output_prefix
        sep = "_" if prefix else ""

        # Column names
        mentions_col = f"{prefix}{sep}claude_code_mentions"
        urls_col = f"{prefix}{sep}claude_code_urls"
        uses_col = f"{prefix}{sep}uses_claude_code"

        # Empty result
        empty_result = {
            mentions_col: 0,
            urls_col: "",
            uses_col: False
        }

        # Step 1: Fetch posts from LinkedIn profile
        linkedin_url = row.get("founder_linkedin_url", "")
        if not linkedin_url:
            return empty_result, "missing founder_linkedin_url"

        posts_result, err = linkedin_posts(
            linkedin_url=linkedin_url,
            max_posts=self.max_posts
        )
        if err:
            return empty_result, f"failed to fetch posts: {err}"

        posts = posts_result.get("posts", [])
        if not posts:
            return empty_result, ""

        # Step 2: Filter posts by Claude Code keywords
        filtered_result, err = filter_by(
            items=posts,
            field="text",
            keywords=self.keywords,
            case_sensitive=False
        )
        if err:
            return empty_result, f"failed to filter posts: {err}"

        filtered = filtered_result.get("filtered", [])
        if not filtered:
            return empty_result, ""

        # Step 3: Aggregate results
        agg_result, err = aggregate(
            items=filtered,
            count_as="count",
            collect_field="url",
            collect_limit=5,
            date_field="date"
        )
        if err:
            return empty_result, f"failed to aggregate: {err}"

        # Step 4: Format output
        mention_count = agg_result.get("count", 0)
        urls = agg_result.get("collected", [])
        urls_string = ", ".join(urls) if urls else ""

        return {
            mentions_col: mention_count,
            urls_col: urls_string,
            uses_col: mention_count > 0
        }, ""
