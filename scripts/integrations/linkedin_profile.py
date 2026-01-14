"""
Integration: LinkedIn Profile Enrichment

Enriches leads with LinkedIn profile data using profile URL.
"""

from .base import Integration


class LinkedInProfile(Integration):
    """Get LinkedIn profile data from profile URL."""

    input_cols = ["linkedin_url"]
    output_cols = ["headline", "current_company", "location", "follower_count"]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        result = self.client.execute_tool(
            "get_linkedin_person_data",
            {"linkedin_url": row["linkedin_url"]}
        )

        person = result.get("person", {})

        # Get current company from positions
        current_company = ""
        positions = person.get("positions", {})
        if positions and positions.get("positionHistory"):
            current_company = positions["positionHistory"][0].get("companyName", "")

        return {
            "headline": person.get("headline", ""),
            "current_company": current_company,
            "location": person.get("location", ""),
            "follower_count": person.get("followerCount", 0)
        }, ""


# Backward compatibility: Module-level API
_instance = LinkedInProfile()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
