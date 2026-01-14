"""
Primitive: Web Research

Generic web research capability. Takes any query, returns raw result text.
This is a TRUE primitive - no hardcoded columns, no domain-specific logic.
"""

from .base import Primitive, register_primitive


@register_primitive
class WebResearch(Primitive):
    """Perform web research on any query and return raw result."""

    name = "web_research"
    description = "Search the web for information on any topic"

    input_schema = {
        "query": {
            "type": "string",
            "description": "The search query or question to research",
            "required": True
        }
    }

    output_schema = {
        "result": {
            "type": "string",
            "description": "Raw research result text"
        }
    }

    def run(self, **inputs) -> tuple[dict, str]:
        query = inputs["query"]

        if not query or not query.strip():
            return {}, "empty query"

        result = self.client.execute_tool(
            "chatgpt_webresearch",
            {"query": query}
        )

        if not result:
            return {}, "no result from web research"

        answer = result.get("answer", "")
        if not answer:
            return {}, "empty answer from web research"

        return {"result": answer}, ""


# Module-level instance for convenient imports
web_research = WebResearch()
