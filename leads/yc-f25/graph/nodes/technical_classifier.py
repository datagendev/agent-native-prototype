"""
Node: Technical Founder Classifier

Classify founders as technical vs non-technical based on LinkedIn profile data.
Uses AI-powered analysis of job titles, education, and profile content to identify
technical backgrounds (engineering, CS) vs business/product/design backgrounds.

Outputs:
- is_technical_founder: Boolean classification (True if technical background)
- founder_role_type: String classification ("technical", "non-technical", or "hybrid")
- classification_signals: Comma-separated list of key signals used for classification

Classification Logic:
- Technical: CTO, Engineer, Developer, CS/Engineering degrees, coding-related keywords
- Non-technical: CEO (pure biz), Designer, PM, Marketing, MBA, Liberal Arts
- Hybrid: Mix of both (e.g., CS degree but now CEO, or MBA with engineering background)
"""

import sys
from pathlib import Path

# Add scripts to path for primitive imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

from primitives import extract_structured
from primitives.base import Graph


class TechnicalClassifier(Graph):
    """Classify founders as technical vs non-technical using AI analysis."""

    output_prefix = ""

    @property
    def input_cols(self) -> list[str]:
        return [
            "founder_name",
            "founder_headline",
            "founder_summary",
            "founder_top_role",
            "founder_education_field"
        ]

    @property
    def output_cols(self) -> list[str]:
        prefix = self.output_prefix
        if prefix:
            return [
                f"{prefix}_is_technical_founder",
                f"{prefix}_founder_role_type",
                f"{prefix}_classification_signals"
            ]
        return [
            "is_technical_founder",
            "founder_role_type",
            "classification_signals"
        ]

    def __init__(self, output_prefix: str = ""):
        """
        Initialize technical founder classifier.

        Args:
            output_prefix: Prefix for output columns (e.g., "tech" -> "tech_is_technical_founder")
        """
        self.output_prefix = output_prefix

    def run(self, row: dict) -> tuple[dict, str]:
        """
        Classify founder as technical vs non-technical.

        Args:
            row: Dictionary with founder profile fields

        Returns:
            (result_dict, error_string) tuple
        """
        prefix = self.output_prefix

        # Extract input fields
        name = row.get("founder_name", "").strip()
        headline = row.get("founder_headline", "").strip()
        summary = row.get("founder_summary", "").strip()
        top_role = row.get("founder_top_role", "").strip()
        education_field = row.get("founder_education_field", "").strip()

        # Handle empty inputs - need at least some data to classify
        if not any([headline, summary, top_role, education_field]):
            return self._empty_result(), "no profile data available for classification"

        # Build analysis context
        context_parts = []
        if name:
            context_parts.append(f"Name: {name}")
        if headline:
            context_parts.append(f"Headline: {headline}")
        if summary:
            context_parts.append(f"Summary: {summary}")
        if top_role:
            context_parts.append(f"Current/Recent Role: {top_role}")
        if education_field:
            context_parts.append(f"Education Field: {education_field}")

        context_text = "\n".join(context_parts)

        # Define extraction schema
        schema = {
            "is_technical": {
                "type": "boolean",
                "description": "True if founder has technical background (engineering, development, CS), False otherwise"
            },
            "role_type": {
                "type": "string",
                "description": "Classification as 'technical', 'non-technical', or 'hybrid'"
            },
            "signals": {
                "type": "string",
                "description": "Comma-separated list of key signals used for classification (e.g., 'CTO title, CS degree, engineering experience')"
            }
        }

        # Use extract_structured primitive with classification prompt
        extraction_context = """Classify this founder's background based on these guidelines:

TECHNICAL indicators (is_technical = true, role_type = "technical"):
- Job titles: CTO, VP Engineering, Tech Lead, Software Engineer, Developer, Data Scientist, ML Engineer, Architect, Programmer
- Education: Computer Science, Software Engineering, Electrical Engineering, Math, Physics, Data Science
- Keywords in headline/summary: "building", "coding", "developer", "engineer", "technical", "programming", "software development"
- Examples: "CTO at X", "Full-stack developer", "CS from MIT", "Built backend systems"

NON-TECHNICAL indicators (is_technical = false, role_type = "non-technical"):
- Job titles: CEO/Founder (without technical context), Designer, Product Manager, Marketing, Sales, Operations, Growth
- Education: Business, MBA, Design, Liberal Arts, Social Sciences, Humanities, Communications
- Keywords: "founder", "CEO", "building companies" (without technical context), "product strategy", "growth", "marketing", "sales", "design"
- Examples: "CEO building next-gen platform", "Product Designer", "MBA from Harvard", "Growth expert"

HYBRID indicators (role_type = "hybrid"):
- Mix of both technical and non-technical signals
- Examples: "CS degree but now pure CEO role", "Engineer turned founder/CEO", "MBA with engineering background", "Technical PM"
- Set is_technical based on which side is stronger (more recent technical = true, more recent business = false)

IMPORTANT:
1. Focus on CURRENT role and MOST RECENT experience for primary classification
2. If founder was technical but is now pure CEO/business focused, lean towards non-technical UNLESS they emphasize technical work
3. "Founder" or "CEO" alone is NOT technical unless combined with technical keywords/context
4. List specific signals found in the data (titles, degrees, keywords) in the signals field
5. Be decisive: only use "hybrid" when there's genuine mix of technical and business backgrounds"""

        extracted, err = extract_structured(
            text=context_text,
            schema=schema,
            context=extraction_context
        )

        if err:
            return self._empty_result(), f"classification failed: {err}"

        # Parse extracted data
        data = extracted.get("extracted", {})
        is_technical = data.get("is_technical")
        role_type = data.get("role_type", "").lower().strip()
        signals = data.get("signals", "")

        # Validate and normalize outputs
        if is_technical is None:
            return self._empty_result(), "classification returned no result"

        # Validate role_type
        if role_type not in ["technical", "non-technical", "hybrid"]:
            # Default based on is_technical
            role_type = "technical" if is_technical else "non-technical"

        # Build result
        result = {}
        if prefix:
            result[f"{prefix}_is_technical_founder"] = bool(is_technical)
            result[f"{prefix}_founder_role_type"] = role_type
            result[f"{prefix}_classification_signals"] = signals
        else:
            result["is_technical_founder"] = bool(is_technical)
            result["founder_role_type"] = role_type
            result["classification_signals"] = signals

        return result, ""

    def _empty_result(self) -> dict:
        """Return empty result structure."""
        prefix = self.output_prefix
        if prefix:
            return {
                f"{prefix}_is_technical_founder": False,
                f"{prefix}_founder_role_type": "non-technical",
                f"{prefix}_classification_signals": ""
            }
        return {
            "is_technical_founder": False,
            "founder_role_type": "non-technical",
            "classification_signals": ""
        }


# Pre-configured instances
technical_classifier = TechnicalClassifier()
