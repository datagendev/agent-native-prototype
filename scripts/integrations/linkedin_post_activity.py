"""
Integration: LinkedIn Post Activity

Enriches leads with LinkedIn posting activity metrics.
"""

from .base import Integration
from datetime import datetime, timedelta


class LinkedInPostActivity(Integration):
    """Get LinkedIn posting activity metrics (post counts, recency)."""

    input_cols = ["linkedin_url"]
    output_cols = ["posts_last_30_days", "posts_last_90_days", "total_posts", "last_post_date"]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        # Get all posts
        result = self.client.execute_tool(
            "get_linkedin_person_posts",
            {"linkedin_url": row["linkedin_url"]}
        )

        posts = result.get("posts", [])

        # Calculate date thresholds (timezone-aware)
        from datetime import timezone
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        ninety_days_ago = now - timedelta(days=90)

        # Count posts by timeframe
        posts_30d = 0
        posts_90d = 0
        last_post_date = None

        for post in posts:
            activity_date = post.get("activityDate")
            if activity_date:
                try:
                    post_date = datetime.fromisoformat(activity_date.replace('Z', '+00:00'))

                    # Track most recent post
                    if not last_post_date or post_date > last_post_date:
                        last_post_date = post_date

                    # Count by timeframe
                    if post_date > thirty_days_ago:
                        posts_30d += 1
                    if post_date > ninety_days_ago:
                        posts_90d += 1
                except ValueError:
                    # Skip posts with invalid dates
                    continue

        return {
            "posts_last_30_days": posts_30d,
            "posts_last_90_days": posts_90d,
            "total_posts": len(posts),
            "last_post_date": last_post_date.isoformat() if last_post_date else ""
        }, ""


# Backward compatibility
_instance = LinkedInPostActivity()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
