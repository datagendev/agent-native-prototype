"""
Graph: Profile Enrichment

Enrich LinkedIn profiles with headline, company, location, and follower count.

This is a simple graph that wraps a single primitive, but adds:
- Declared output columns
- Error handling with fallbacks
- Data validation
"""

import sys
from pathlib import Path

# Add scripts to path for primitive imports
# From: leads/example-leads/graph/nodes/ -> linkedin-outreach/scripts/
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives import linkedin_profile
from primitives.base import Graph


class ProfileEnrichment(Graph):
    """Enrich with LinkedIn profile data (headline, company, location, followers)."""

    @property
    def input_cols(self) -> list[str]:
        return ["linkedin_url"]

    @property
    def output_cols(self) -> list[str]:
        return ["headline", "current_company", "location", "follower_count"]

    def run(self, row: dict) -> tuple[dict, str]:
        # Fetch profile (primitive)
        profile, err = linkedin_profile(linkedin_url=row["linkedin_url"])
        if err:
            # Return empty values on error, don't fail the row
            return {
                "headline": "",
                "current_company": "",
                "location": "",
                "follower_count": 0
            }, f"profile fetch failed: {err}"

        # Return relevant fields (graph decides which fields to keep)
        return {
            "headline": profile.get("headline", ""),
            "current_company": profile.get("current_company", ""),
            "location": profile.get("location", ""),
            "follower_count": profile.get("follower_count", 0)
        }, ""
