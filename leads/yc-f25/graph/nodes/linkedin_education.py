"""
Node: LinkedIn Education

Fetch education history from LinkedIn profile data.
Extracts school names, degrees, and fields of study from the founder's LinkedIn profile.
"""

import sys
import json
from pathlib import Path

# Add scripts to path for primitive imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives.base import Graph, get_client


class LinkedInEducation(Graph):
    """Extract education history from LinkedIn profile."""

    def __init__(self, output_prefix: str = ""):
        """
        Initialize with optional output prefix.

        Args:
            output_prefix: Prefix for output columns (default: "")
        """
        self.output_prefix = output_prefix

    @property
    def input_cols(self) -> list[str]:
        return ["founder_linkedin_url"]

    @property
    def output_cols(self) -> list[str]:
        return ["education_history", "school_names"]

    def run(self, row: dict) -> tuple[dict, str]:
        """
        Execute enrichment on a single row.

        Args:
            row: Dict with founder_linkedin_url from yc_founder_lookup

        Returns:
            (result_dict, error_string) tuple:
            - Success: ({"education_history": "...", "school_names": "..."}, "")
            - Failure: ({}, "error message")
        """
        linkedin_url = row.get("founder_linkedin_url", "")

        if not linkedin_url:
            return {
                "education_history": "",
                "school_names": ""
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
                    "education_history": "",
                    "school_names": ""
                }, "no result from get_linkedin_person_data"

            # Step 2: Extract education history
            person = result.get("person", {})
            if not person:
                return {
                    "education_history": "",
                    "school_names": ""
                }, "no person data in response"

            schools_data = person.get("schools", {})
            if not schools_data:
                return {
                    "education_history": "[]",
                    "school_names": ""
                }, ""

            education_history = schools_data.get("educationHistory", [])
            if not education_history:
                return {
                    "education_history": "[]",
                    "school_names": ""
                }, ""

            # Step 3: Process education entries
            # Store raw education as JSON
            education_json = json.dumps(education_history, ensure_ascii=False)

            # Step 4: Extract school names as comma-separated string
            school_names = []
            for school in education_history:
                school_name = school.get("schoolName", "")
                if school_name:
                    school_names.append(school_name)

            schools_str = ", ".join(school_names)

            return {
                "education_history": education_json,
                "school_names": schools_str
            }, ""

        except Exception as e:
            return {
                "education_history": "",
                "school_names": ""
            }, f"error fetching education: {str(e)}"


# Pre-configured instance
linkedin_education = LinkedInEducation()
