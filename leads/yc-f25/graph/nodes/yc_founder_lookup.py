"""
Node: YC Founder Lookup

Find founder/CEO information from YC company page.
Extracts founder name, LinkedIn URL, title, and company domain.
"""

import sys
from pathlib import Path

# Add scripts to path for primitive imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives import firecrawl_scrape, extract_structured, linkedin_search
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

        # Step 1: Scrape YC company page directly with Firecrawl
        scrape_result, err = firecrawl_scrape(
            url=yc_url,
            onlyMainContent=True,
            maxAge=172800000  # 48h cache
        )
        if err:
            return {
                f"{prefix}founder_name": "",
                f"{prefix}founder_linkedin_url": "",
                f"{prefix}founder_title": "",
                f"{prefix}company_domain": ""
            }, f"scrape failed: {err}"

        markdown_content = scrape_result.get("markdown", "")
        if not markdown_content:
            return {
                f"{prefix}founder_name": "",
                f"{prefix}founder_linkedin_url": "",
                f"{prefix}founder_title": "",
                f"{prefix}company_domain": ""
            }, "empty scrape result"

        # Step 2: Extract structured data (founder info + company website)
        extracted, err = extract_structured(
            text=markdown_content,
            schema={
                "founder_name": {
                    "type": "string",
                    "description": "Full name of the founder or CEO"
                },
                "founder_title": {
                    "type": "string",
                    "description": "Title (CEO, Co-founder, Founder, etc.)"
                },
                "company_website": {
                    "type": "string",
                    "description": "Company website URL (the actual company domain, not the YC page)"
                }
            },
            context=f"Extract founder/CEO info and company website for {company_name} from their YC company page"
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

        # Clean up company website URL to get just the domain
        website_url = data.get("company_website") or ""
        domain = ""
        if website_url:
            # Remove protocol (http://, https://)
            domain = website_url.replace("https://", "").replace("http://", "")
            # Remove www.
            domain = domain.replace("www.", "")
            # Remove trailing slashes and paths
            domain = domain.split("/")[0]
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
