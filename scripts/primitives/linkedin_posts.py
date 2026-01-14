"""
Primitive: LinkedIn Posts

Fetch posts from a LinkedIn profile.
Returns raw posts array for further processing.

This is a TRUE primitive - no filtering, no aggregation, just fetches data.
"""

from .base import Primitive, register_primitive


@register_primitive
class LinkedInPosts(Primitive):
    """Fetch posts from a LinkedIn profile URL."""

    name = "linkedin_posts"
    description = "Get all posts from a LinkedIn profile"

    input_schema = {
        "linkedin_url": {
            "type": "string",
            "description": "LinkedIn profile URL",
            "required": True
        },
        "limit": {
            "type": "integer",
            "description": "Maximum posts to fetch (default: 100)",
            "required": False
        }
    }

    output_schema = {
        "posts": {
            "type": "array",
            "description": "Array of post objects with text, date, url, etc."
        }
    }

    def run(self, **inputs) -> tuple[dict, str]:
        linkedin_url = inputs["linkedin_url"]
        limit = inputs.get("limit", 100)

        if not linkedin_url:
            return {}, "empty linkedin_url"

        result = self.client.execute_tool(
            "get_linkedin_person_posts",
            {"linkedin_url": linkedin_url}
        )

        if not result:
            return {}, "no result from LinkedIn posts API"

        posts = result.get("posts", [])

        # Normalize post structure
        normalized = []
        for post in posts[:limit]:
            normalized.append({
                "text": post.get("text", ""),
                "date": post.get("activityDate", ""),
                "url": post.get("activityUrl", ""),
                "likes": post.get("likeCount", 0),
                "comments": post.get("commentCount", 0),
                "reposts": post.get("repostCount", 0)
            })

        return {"posts": normalized}, ""


# Module-level instance for convenient imports
linkedin_posts = LinkedInPosts()
