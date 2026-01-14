"""
Node: Find CEO

Find CEO name and LinkedIn URL from company domain.
Composes web_research + extract_structured primitives.

This is a NODE (not a primitive) because:
- It declares specific output columns (ceo_name, ceo_linkedin_url)
- It composes multiple primitives
- It contains domain-specific logic (searching for CEO)

But it's CONFIGURABLE - you can search for any role!
"""

import sys
from pathlib import Path

# Add scripts to path for primitive imports
# From: leads/example-leads/graph/nodes/ -> linkedin-outreach/scripts/
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives import web_research, extract_structured
from primitives.base import Graph


class FindCEO(Graph):
    """Find executive name and LinkedIn from company domain."""

    # Configuration - can be overridden
    role = "CEO"
    output_prefix = "ceo"

    @property
    def input_cols(self) -> list[str]:
        return ["company_domain"]

    @property
    def output_cols(self) -> list[str]:
        prefix = self.output_prefix
        return [f"{prefix}_name", f"{prefix}_linkedin_url"]

    def __init__(self, role: str = None, output_prefix: str = None):
        """
        Initialize with optional custom role and prefix.

        Args:
            role: Executive role to search for (default: "CEO")
            output_prefix: Prefix for output columns (default: "ceo")

        Examples:
            FindCEO()  # Find CEO
            FindCEO(role="CTO", output_prefix="cto")  # Find CTO
            FindCEO(role="VP Engineering", output_prefix="vp_eng")
        """
        if role is not None:
            self.role = role
        if output_prefix is not None:
            self.output_prefix = output_prefix

    def run(self, row: dict) -> tuple[dict, str]:
        prefix = self.output_prefix
        domain = row["company_domain"]

        # Step 1: Web research (primitive)
        query = f"Who is the {self.role} of {domain}? Include their full name and LinkedIn profile URL."
        research, err = web_research(query=query)
        if err:
            return {}, f"research failed: {err}"

        result_text = research.get("result", "")
        if not result_text:
            return {
                f"{prefix}_name": "",
                f"{prefix}_linkedin_url": ""
            }, "empty research result"

        # Step 2: Extract structured data (primitive)
        extracted, err = extract_structured(
            text=result_text,
            schema={
                "name": {
                    "type": "string",
                    "description": f"Full name of the {self.role}"
                },
                "linkedin_url": {
                    "type": "string",
                    "description": "LinkedIn profile URL"
                }
            },
            context=f"Looking for {self.role} of {domain}"
        )
        if err:
            return {}, f"extraction failed: {err}"

        data = extracted.get("extracted", {})

        # Step 3: Validation and cleanup
        linkedin_url = data.get("linkedin_url") or ""
        if linkedin_url and not linkedin_url.startswith("http"):
            # Try to fix partial URLs
            if "linkedin.com" in linkedin_url:
                linkedin_url = "https://" + linkedin_url
            elif linkedin_url.startswith("in/"):
                linkedin_url = f"https://linkedin.com/{linkedin_url}"
            else:
                linkedin_url = ""  # Invalid, clear it

        return {
            f"{prefix}_name": data.get("name") or "",
            f"{prefix}_linkedin_url": linkedin_url
        }, ""


# Pre-configured instances for common roles
find_ceo = FindCEO()
find_cto = FindCEO(role="CTO", output_prefix="cto")
find_cfo = FindCEO(role="CFO", output_prefix="cfo")
find_founder = FindCEO(role="Founder", output_prefix="founder")
