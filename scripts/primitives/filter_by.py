"""
Primitive: Filter By

Filter an array of items by keywords or conditions.
Generic filtering - works with any array and any keywords.

This is a TRUE primitive - no hardcoded keywords like "claude" or "datagen".
"""

from .base import Primitive, register_primitive


@register_primitive
class FilterBy(Primitive):
    """Filter array items by keywords in a text field."""

    name = "filter_by"
    description = "Filter array items by keywords or conditions"

    input_schema = {
        "items": {
            "type": "array",
            "description": "Array of objects to filter",
            "required": True
        },
        "field": {
            "type": "string",
            "description": "Field name to search in (e.g., 'text')",
            "required": True
        },
        "keywords": {
            "type": "array",
            "description": "Keywords to match (OR logic - any match passes)",
            "required": True
        },
        "case_sensitive": {
            "type": "boolean",
            "description": "Whether to match case (default: False)",
            "required": False
        }
    }

    output_schema = {
        "filtered": {
            "type": "array",
            "description": "Items that matched the filter"
        },
        "matched_count": {
            "type": "integer",
            "description": "Number of items that matched"
        }
    }

    def run(self, **inputs) -> tuple[dict, str]:
        items = inputs["items"]
        field = inputs["field"]
        keywords = inputs["keywords"]
        case_sensitive = inputs.get("case_sensitive", False)

        if not items:
            return {"filtered": [], "matched_count": 0}, ""

        if not keywords:
            return {"filtered": items, "matched_count": len(items)}, ""

        # Normalize keywords
        if not case_sensitive:
            keywords = [k.lower() for k in keywords]

        filtered = []
        for item in items:
            text = item.get(field, "")
            if not case_sensitive:
                text = text.lower()

            # Check if any keyword matches
            if any(kw in text for kw in keywords):
                filtered.append(item)

        return {
            "filtered": filtered,
            "matched_count": len(filtered)
        }, ""


# Module-level instance for convenient imports
filter_by = FilterBy()
