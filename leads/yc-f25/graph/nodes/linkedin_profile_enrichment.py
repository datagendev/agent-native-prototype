"""
Node: LinkedIn Profile Enrichment

Fetch comprehensive LinkedIn profile data including headline, summary, positions, and education.
Extracts the most relevant professional information from a founder's LinkedIn profile.
"""

import sys
from pathlib import Path

# Add scripts to path for primitive imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives.base import Graph, get_client


class LinkedInProfileEnrichment(Graph):
    """Extract comprehensive profile data from LinkedIn."""

    @property
    def input_cols(self) -> list[str]:
        return ["founder_linkedin_url"]

    @property
    def output_cols(self) -> list[str]:
        return [
            "founder_headline",
            "founder_summary",
            "founder_top_role",
            "founder_education_field"
        ]

    def run(self, row: dict) -> tuple[dict, str]:
        """
        Execute enrichment on a single row.

        Args:
            row: Dict with founder_linkedin_url

        Returns:
            (result_dict, error_string) tuple:
            - Success: ({"founder_headline": "...", ...}, "")
            - Failure: ({}, "error message")
        """
        linkedin_url = row.get("founder_linkedin_url", "")

        if not linkedin_url:
            return {
                "founder_headline": "",
                "founder_summary": "",
                "founder_top_role": "",
                "founder_education_field": ""
            }, "empty linkedin_url"

        try:
            # Step 1: Call get_linkedin_person_data MCP tool
            client = get_client()
            result = client.execute_tool(
                "get_linkedin_person_data",
                {"linkedin_url": linkedin_url}
            )

            if not result:
                return {
                    "founder_headline": "",
                    "founder_summary": "",
                    "founder_top_role": "",
                    "founder_education_field": ""
                }, "no result from get_linkedin_person_data"

            # Step 2: Extract person data
            person = result.get("person", {})
            if not person:
                return {
                    "founder_headline": "",
                    "founder_summary": "",
                    "founder_top_role": "",
                    "founder_education_field": ""
                }, "no person data in response"

            # Step 3: Extract headline
            headline = person.get("headline", "")

            # Step 4: Extract and truncate summary to 500 chars
            summary = person.get("summary", "")
            if summary and len(summary) > 500:
                summary = summary[:500]

            # Step 5: Extract most recent position title
            top_role = ""
            positions = person.get("positions", {})
            if positions:
                position_history = positions.get("positionHistory", [])
                if position_history and len(position_history) > 0:
                    # Get the first (most recent) position
                    most_recent = position_history[0]
                    top_role = most_recent.get("title", "")

            # Step 6: Extract most recent education field
            education_field = ""
            schools = person.get("schools", {})
            if schools:
                education_history = schools.get("educationHistory", [])
                if education_history and len(education_history) > 0:
                    # Get the first (most recent) education
                    most_recent_edu = education_history[0]
                    education_field = most_recent_edu.get("fieldOfStudy", "")

            return {
                "founder_headline": headline,
                "founder_summary": summary,
                "founder_top_role": top_role,
                "founder_education_field": education_field
            }, ""

        except Exception as e:
            return {
                "founder_headline": "",
                "founder_summary": "",
                "founder_top_role": "",
                "founder_education_field": ""
            }, f"error fetching profile data: {str(e)}"


# Pre-configured instance
linkedin_profile_enrichment = LinkedInProfileEnrichment()
