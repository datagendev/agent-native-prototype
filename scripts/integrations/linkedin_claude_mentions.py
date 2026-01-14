"""
Integration: LinkedIn Claude Code Mentions

Finds LinkedIn posts where the person mentioned "Claude Code".
"""

from .base import Integration


class LinkedInClaudeMentions(Integration):
    """Find posts mentioning Claude Code."""

    input_cols = ["linkedin_url"]
    output_cols = ["claude_mentions_count", "claude_mention_urls", "first_claude_mention_date"]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        # Get all posts
        result = self.client.execute_tool(
            "get_linkedin_person_posts",
            {"linkedin_url": row["linkedin_url"]}
        )

        posts = result.get("posts", [])

        # Search for Claude Code mentions
        claude_posts = []
        search_terms = ["claude code", "claude-code", "@claude", "claudecode"]

        for post in posts:
            text = post.get("text", "").lower()
            activity_url = post.get("activityUrl", "")
            activity_date = post.get("activityDate", "")

            # Check if any search term appears in post
            if any(term in text for term in search_terms):
                claude_posts.append({
                    "url": activity_url,
                    "date": activity_date
                })

        # Sort by date (most recent first)
        claude_posts.sort(key=lambda x: x["date"], reverse=True)

        # Get URLs (limit to 5 most recent)
        urls = [post["url"] for post in claude_posts[:5]]
        urls_string = ", ".join(urls) if urls else ""

        # Get first mention date
        first_mention_date = claude_posts[-1]["date"] if claude_posts else ""

        return {
            "claude_mentions_count": len(claude_posts),
            "claude_mention_urls": urls_string,
            "first_claude_mention_date": first_mention_date
        }, ""


# Backward compatibility
_instance = LinkedInClaudeMentions()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
