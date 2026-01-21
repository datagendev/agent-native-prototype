"""
Node: Harvard Detection

Detect if a founder attended Harvard based on their education history.
This is a pure logic node that parses school names and checks for Harvard attendance.

Inputs:
- school_names: Comma-separated list of school names from linkedin_education node

Outputs:
- went_to_harvard: Boolean indicating Harvard attendance
- harvard_school_name: The exact Harvard school name if found (e.g., "Harvard Business School", "Harvard University")
"""

import sys
from pathlib import Path

# Add scripts to path for primitive imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives.base import Graph


class HarvardDetection(Graph):
    """Detect Harvard attendance from education history."""

    def __init__(self, output_prefix: str = ""):
        """
        Initialize with optional output prefix.

        Args:
            output_prefix: Prefix for output columns (default: "")
        """
        self.output_prefix = output_prefix

    @property
    def input_cols(self) -> list[str]:
        return ["school_names"]

    @property
    def output_cols(self) -> list[str]:
        return ["went_to_harvard", "harvard_school_name"]

    def run(self, row: dict) -> tuple[dict, str]:
        """
        Execute Harvard detection on a single row.

        Args:
            row: Dict with school_names (comma-separated string)

        Returns:
            (result_dict, error_string) tuple:
            - Success: ({"went_to_harvard": bool, "harvard_school_name": str}, "")
            - Failure: ({}, "error message")
        """
        school_names = row.get("school_names", "").strip()

        # Handle empty or missing school_names
        if not school_names:
            return {
                "went_to_harvard": False,
                "harvard_school_name": ""
            }, ""

        # Parse comma-separated school names
        schools = [school.strip() for school in school_names.split(",") if school.strip()]

        if not schools:
            return {
                "went_to_harvard": False,
                "harvard_school_name": ""
            }, ""

        # Check each school for Harvard (case-insensitive)
        for school in schools:
            if "harvard" in school.lower():
                # Found Harvard - return the exact school name
                return {
                    "went_to_harvard": True,
                    "harvard_school_name": school
                }, ""

        # No Harvard found
        return {
            "went_to_harvard": False,
            "harvard_school_name": ""
        }, ""


# Pre-configured instance
harvard_detection = HarvardDetection()
