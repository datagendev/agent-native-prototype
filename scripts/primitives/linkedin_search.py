"""
Primitive: LinkedIn Search

Search for LinkedIn profiles using Parallel Search.
Optimized for finding people's LinkedIn URLs.
"""

from .base import Primitive, register_primitive


@register_primitive
class LinkedInSearch(Primitive):
    """Search for LinkedIn profiles using Parallel Search."""

    name = "linkedin_search"
    description = "Find LinkedIn profile URLs for people"

    input_schema = {
        "name": {
            "type": "string",
            "description": "Person's full name",
            "required": True
        },
        "company": {
            "type": "string",
            "description": "Company name or domain (optional)",
            "required": False
        },
        "title": {
            "type": "string",
            "description": "Job title (optional)",
            "required": False
        }
    }

    output_schema = {
        "linkedin_url": {
            "type": "string",
            "description": "LinkedIn profile URL if found"
        },
        "confidence": {
            "type": "string",
            "description": "Confidence level (high/medium/low)"
        }
    }

    def run(self, **inputs) -> tuple[dict, str]:
        name = inputs["name"]
        company = inputs.get("company", "")
        title = inputs.get("title", "")

        if not name or not name.strip():
            return {}, "empty name"

        # Build search query
        query_parts = [f'"{name}"', "LinkedIn"]
        if company:
            query_parts.append(f'"{company}"')
        if title:
            query_parts.append(f'"{title}"')

        search_query = " ".join(query_parts)

        # Build objective
        objective = f"Find the LinkedIn profile URL for {name}"
        if company:
            objective += f" at {company}"
        if title:
            objective += f" ({title})"

        try:
            # Use Parallel Search with targeted search type
            result = self.client.execute_tool(
                "mcp_Parallel_Search_web_search_preview",
                {
                    "objective": objective,
                    "search_queries": [search_query],
                    "search_type": "targeted",
                    "include_domains": ["linkedin.com"]
                }
            )

            if not result:
                return {"linkedin_url": "", "confidence": "none"}, ""

            # Parse result to extract LinkedIn URL
            result_text = str(result)

            # Look for LinkedIn URLs in the response
            import re
            linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
            matches = re.findall(linkedin_pattern, result_text)

            if matches:
                # Return first match (most relevant)
                linkedin_url = matches[0]
                confidence = "high" if len(matches) == 1 else "medium"
                return {
                    "linkedin_url": linkedin_url,
                    "confidence": confidence
                }, ""

            return {"linkedin_url": "", "confidence": "none"}, ""

        except Exception as e:
            return {"linkedin_url": "", "confidence": "none"}, f"search failed: {str(e)}"


# Module-level instance for convenient imports
linkedin_search = LinkedInSearch()
