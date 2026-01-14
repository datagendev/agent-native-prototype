"""
Node: B2B Classifier

Classify companies as B2B (business-to-business) or B2C (business-to-consumer)
based on company description and industry using AI-powered analysis.

Outputs:
- is_b2b: Boolean classification
- b2b_confidence: Confidence score (0.0-1.0)
- classification_reason: Brief explanation

Classification Heuristics:
- B2B signals: APIs, SaaS, enterprise, developer tools, infrastructure, business software
- B2C signals: consumer apps, marketplace, e-commerce, gaming, social media, direct-to-consumer
- Mixed: Platforms serving both (marked with lower confidence)
"""

import sys
from pathlib import Path

# Add scripts to path for primitive imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives import extract_structured
from primitives.base import Graph


class B2BClassifier(Graph):
    """Classify companies as B2B or B2C using AI analysis."""

    output_prefix = ""

    @property
    def input_cols(self) -> list[str]:
        return ["description", "industry"]

    @property
    def output_cols(self) -> list[str]:
        prefix = self.output_prefix
        if prefix:
            return [f"{prefix}_is_b2b", f"{prefix}_b2b_confidence", f"{prefix}_classification_reason"]
        return ["is_b2b", "b2b_confidence", "classification_reason"]

    def __init__(self, output_prefix: str = ""):
        """
        Initialize B2B classifier.

        Args:
            output_prefix: Prefix for output columns (e.g., "market" -> "market_is_b2b")
        """
        self.output_prefix = output_prefix

    def run(self, row: dict) -> tuple[dict, str]:
        """
        Classify company as B2B or B2C.

        Args:
            row: Dictionary with 'description' and 'industry' fields

        Returns:
            (result_dict, error_string) tuple
        """
        prefix = self.output_prefix
        description = row.get("description", "").strip()
        industry = row.get("industry", "").strip()

        # Handle empty inputs
        if not description and not industry:
            return self._empty_result(), "no description or industry provided"

        # Build analysis context
        context_text = f"Company description: {description}"
        if industry:
            context_text += f"\nIndustry: {industry}"

        # Define extraction schema
        schema = {
            "is_b2b": {
                "type": "boolean",
                "description": "True if company is B2B (business-to-business), False if B2C (business-to-consumer)"
            },
            "confidence": {
                "type": "number",
                "description": "Confidence score from 0.0 (not confident) to 1.0 (very confident)"
            },
            "reason": {
                "type": "string",
                "description": "Brief 1-2 sentence explanation of why this company is B2B or B2C"
            }
        }

        # Use extract_structured primitive with classification prompt
        extraction_context = """Classify this company based on these guidelines:

B2B indicators (business-to-business):
- Sells to other businesses (APIs, SaaS, enterprise software)
- Developer tools, infrastructure, business operations software
- Words like: "for teams", "enterprise", "B2B", "businesses", "API", "platform for developers"

B2C indicators (business-to-consumer):
- Sells directly to consumers (apps, games, marketplace, e-commerce)
- Consumer-facing products, entertainment, social media
- Words like: "users", "consumers", "marketplace", "e-commerce", "gaming", "social"

Mixed/Platform:
- Serves both businesses and consumers (mark with confidence 0.5-0.7)
- Example: Marketplace platforms, payment processors

Provide a clear, decisive classification with high confidence (0.8+) when signals are clear."""

        extracted, err = extract_structured(
            text=context_text,
            schema=schema,
            context=extraction_context
        )

        if err:
            return self._empty_result(), f"classification failed: {err}"

        # Parse extracted data
        data = extracted.get("extracted", {})
        is_b2b = data.get("is_b2b")
        confidence = data.get("confidence")
        reason = data.get("reason", "")

        # Validate and normalize outputs
        if is_b2b is None:
            return self._empty_result(), "classification returned no result"

        # Normalize confidence to 0.0-1.0
        if confidence is None:
            confidence = 0.5
        else:
            confidence = max(0.0, min(1.0, float(confidence)))

        # Build result
        result = {}
        if prefix:
            result[f"{prefix}_is_b2b"] = bool(is_b2b)
            result[f"{prefix}_b2b_confidence"] = confidence
            result[f"{prefix}_classification_reason"] = reason
        else:
            result["is_b2b"] = bool(is_b2b)
            result["b2b_confidence"] = confidence
            result["classification_reason"] = reason

        return result, ""

    def _empty_result(self) -> dict:
        """Return empty result structure."""
        prefix = self.output_prefix
        if prefix:
            return {
                f"{prefix}_is_b2b": False,
                f"{prefix}_b2b_confidence": 0.0,
                f"{prefix}_classification_reason": ""
            }
        return {
            "is_b2b": False,
            "b2b_confidence": 0.0,
            "classification_reason": ""
        }


# Pre-configured instances
b2b_classifier = B2BClassifier()
