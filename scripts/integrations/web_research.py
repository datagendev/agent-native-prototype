"""
Integration: Web Research Company Enrichment

Enriches leads with company data using AI-powered web research.
"""

from .base import Integration


class WebResearch(Integration):
    """Research company information from domain."""

    input_cols = ["company_domain"]
    output_cols = ["company_description", "tech_stack", "employee_count"]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        query = f"What does {row['company_domain']} do? What is their tech stack? How many employees do they have? Provide concise answers."

        result = self.client.execute_tool("chatgpt_webresearch", {"query": query})
        answer = result.get("answer", "")

        return {
            "company_description": answer[:200],
            "tech_stack": "N/A",
            "employee_count": "N/A"
        }, ""


# Backward compatibility
_instance = WebResearch()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
