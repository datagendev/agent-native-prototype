"""
Node: YC Founder Lookup

Find founder/CEO information from YC company page.
Extracts founder name, LinkedIn URL, title, and company domain.
"""

import sys
from pathlib import Path

# Add scripts to path for primitive imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives import web_research, extract_structured, linkedin_search
from primitives.base import Graph


class YCFounderLookup(Graph):
    """Find founder/CEO info from YC company page."""

    def __init__(self, output_prefix: str = ""):
        """
        Initialize with optional output prefix.

        Args:
            output_prefix: Prefix for output columns (default: "")
        """
        self.output_prefix = output_prefix

    @property
    def input_cols(self) -> list[str]:
        return ["name", "yc_url"]

    @property
    def output_cols(self) -> list[str]:
        prefix = f"{self.output_prefix}_" if self.output_prefix else ""
        return [
            f"{prefix}founder_name",
            f"{prefix}founder_linkedin_url",
            f"{prefix}founder_title",
            f"{prefix}company_domain"
        ]

    def run(self, row: dict) -> tuple[dict, str]:
        prefix = f"{self.output_prefix}_" if self.output_prefix else ""
        company_name = row["name"]
        yc_url = row["yc_url"]

        # Step 1: Web research for founder info
        query = f"From {yc_url}, who is the founder or CEO? Include their full name, title, LinkedIn profile URL, and company website domain."
        research, err = web_research(query=query)
        if err:
            return {
                f"{prefix}founder_name": "",
                f"{prefix}founder_linkedin_url": "",
                f"{prefix}founder_title": "",
                f"{prefix}company_domain": ""
            }, f"research failed: {err}"

        result_text = research.get("result", "")
        if not result_text:
            return {
                f"{prefix}founder_name": "",
                f"{prefix}founder_linkedin_url": "",
                f"{prefix}founder_title": "",
                f"{prefix}company_domain": ""
            }, "empty research result"

        # Step 2: Extract basic info (name, title, domain)
        extracted, err = extract_structured(
            text=result_text,
            schema={
                "founder_name": {
                    "type": "string",
                    "description": "Full name of the founder or CEO"
                },
                "founder_title": {
                    "type": "string",
                    "description": "Title (CEO, Co-founder, Founder, etc.)"
                },
                "company_domain": {
                    "type": "string",
                    "description": "Company website domain (e.g., stripe.com)"
                }
            },
            context=f"Looking for founder/CEO of {company_name} from YC page {yc_url}"
        )
        if err:
            return {
                f"{prefix}founder_name": "",
                f"{prefix}founder_linkedin_url": "",
                f"{prefix}founder_title": "",
                f"{prefix}company_domain": ""
            }, f"extraction failed: {err}"

        data = extracted.get("extracted", {})
        founder_name = data.get("founder_name") or ""
        founder_title = data.get("founder_title") or ""

        # Clean up company domain (remove http/https, www, trailing slashes)
        domain = data.get("company_domain") or ""
        if domain:
            domain = domain.replace("https://", "").replace("http://", "")
            domain = domain.replace("www.", "")
            domain = domain.rstrip("/")

        # Step 3: Search for LinkedIn URL using Parallel Search
        linkedin_url = ""
        if founder_name:
            linkedin_result, linkedin_err = linkedin_search(
                name=founder_name,
                company=company_name,
                title=founder_title
            )
            if not linkedin_err:
                linkedin_url = linkedin_result.get("linkedin_url", "")

        return {
            f"{prefix}founder_name": founder_name,
            f"{prefix}founder_linkedin_url": linkedin_url,
            f"{prefix}founder_title": founder_title,
            f"{prefix}company_domain": domain
        }, ""


# Pre-configured instance
yc_founder_lookup = YCFounderLookup()
