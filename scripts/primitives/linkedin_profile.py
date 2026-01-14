"""
Primitive: LinkedIn Profile

Fetch profile data from a LinkedIn URL.
Single API call, returns raw profile data.

This is a TRUE primitive - atomic operation, one API call.
"""

from .base import Primitive, register_primitive


@register_primitive
class LinkedInProfile(Primitive):
    """Fetch profile data from a LinkedIn profile URL."""

    name = "linkedin_profile"
    description = "Get profile data (headline, company, location, followers) from LinkedIn URL"

    input_schema = {
        "linkedin_url": {
            "type": "string",
            "description": "LinkedIn profile URL",
            "required": True
        }
    }

    output_schema = {
        "headline": {
            "type": "string",
            "description": "Profile headline/tagline"
        },
        "current_company": {
            "type": "string",
            "description": "Current company name"
        },
        "location": {
            "type": "string",
            "description": "Location from profile"
        },
        "follower_count": {
            "type": "integer",
            "description": "Number of followers"
        },
        "full_name": {
            "type": "string",
            "description": "Full name from profile"
        },
        "summary": {
            "type": "string",
            "description": "About/summary section"
        }
    }

    def run(self, **inputs) -> tuple[dict, str]:
        linkedin_url = inputs["linkedin_url"]

        if not linkedin_url:
            return {}, "empty linkedin_url"

        result = self.client.execute_tool(
            "get_linkedin_profile",
            {"linkedin_url": linkedin_url}
        )

        if not result:
            return {}, "no result from LinkedIn profile API"

        # Extract relevant fields
        return {
            "headline": result.get("headline", ""),
            "current_company": result.get("companyName", "") or result.get("company", ""),
            "location": result.get("location", ""),
            "follower_count": result.get("followersCount", 0) or result.get("follower_count", 0),
            "full_name": result.get("fullName", "") or result.get("name", ""),
            "summary": result.get("summary", "") or result.get("about", "")
        }, ""


# Module-level instance for convenient imports
linkedin_profile = LinkedInProfile()
