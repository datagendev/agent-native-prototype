"""
Primitive: Aggregate

Aggregate an array into summary metrics.
Generic aggregation - computes counts, extracts fields, finds min/max dates.

This is a TRUE primitive - returns raw metrics, Claude decides what to do with them.
"""

from .base import Primitive, register_primitive


@register_primitive
class Aggregate(Primitive):
    """Aggregate array items into summary metrics."""

    name = "aggregate"
    description = "Compute summary metrics from an array (count, urls, dates)"

    input_schema = {
        "items": {
            "type": "array",
            "description": "Array of objects to aggregate",
            "required": True
        },
        "count_as": {
            "type": "string",
            "description": "Name for count field in output (default: 'count')",
            "required": False
        },
        "collect_field": {
            "type": "string",
            "description": "Field to collect into array (e.g., 'url')",
            "required": False
        },
        "collect_limit": {
            "type": "integer",
            "description": "Max items to collect (default: 5)",
            "required": False
        },
        "date_field": {
            "type": "string",
            "description": "Field to find first/last dates from (e.g., 'date')",
            "required": False
        }
    }

    output_schema = {
        "count": {
            "type": "integer",
            "description": "Number of items"
        },
        "collected": {
            "type": "array",
            "description": "Collected field values (if collect_field specified)"
        },
        "first_date": {
            "type": "string",
            "description": "Earliest date (if date_field specified)"
        },
        "last_date": {
            "type": "string",
            "description": "Latest date (if date_field specified)"
        }
    }

    def run(self, **inputs) -> tuple[dict, str]:
        items = inputs["items"]
        count_as = inputs.get("count_as", "count")
        collect_field = inputs.get("collect_field")
        collect_limit = inputs.get("collect_limit", 5)
        date_field = inputs.get("date_field")

        result = {
            count_as: len(items) if items else 0
        }

        if not items:
            return result, ""

        # Collect field values
        if collect_field:
            values = []
            for item in items[:collect_limit]:
                val = item.get(collect_field)
                if val:
                    values.append(val)
            result["collected"] = values

        # Find date range
        if date_field:
            dates = []
            for item in items:
                date = item.get(date_field)
                if date:
                    dates.append(date)

            if dates:
                dates_sorted = sorted(dates)
                result["first_date"] = dates_sorted[0]
                result["last_date"] = dates_sorted[-1]

        return result, ""


# Module-level instance for convenient imports
aggregate = Aggregate()
