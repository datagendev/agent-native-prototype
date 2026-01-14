"""
Integration: Find CEO

Finds the CEO name and LinkedIn profile from a company domain.
"""

from .base import Integration


class FindCEO(Integration):
    """Find CEO information from company domain."""

    input_cols = ["company_domain"]
    output_cols = ["ceo_name", "ceo_linkedin_url"]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        query = f"Who is the CEO of {row['company_domain']}? What is their LinkedIn profile URL?"

        result = self.client.execute_tool("chatgpt_webresearch", {"query": query})
        answer = result.get("answer", "")

        return {
            "ceo_name": answer[:100],
            "ceo_linkedin_url": "N/A"
        }, ""


# Backward compatibility
_instance = FindCEO()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
