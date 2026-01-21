"""
Nodes: Reusable enrichment components for YC F25 leads.

Each node is a Python class that:
- Takes specific inputs
- Produces specific outputs
- Can be configured via parameters

Nodes are composed into workflows via graph.yaml
"""

from .yc_founder_lookup import YCFounderLookup
from .linkedin_posts_scraper import LinkedInPostsScraper
from .claude_code_detector import ClaudeCodeDetector
from .b2b_classifier import B2BClassifier
from .linkedin_education import LinkedInEducation
from .harvard_detection import HarvardDetection
from .linkedin_profile_enrichment import LinkedInProfileEnrichment
from .technical_classifier import TechnicalClassifier

# Registry of available nodes
NODES = {
    "yc_founder_lookup": YCFounderLookup,
    "linkedin_posts_scraper": LinkedInPostsScraper,
    "claude_code_detector": ClaudeCodeDetector,
    "b2b_classifier": B2BClassifier,
    "linkedin_education": LinkedInEducation,
    "harvard_detection": HarvardDetection,
    "linkedin_profile_enrichment": LinkedInProfileEnrichment,
    "technical_classifier": TechnicalClassifier,
}

__all__ = ["NODES", "YCFounderLookup", "LinkedInPostsScraper", "ClaudeCodeDetector", "B2BClassifier", "LinkedInEducation", "HarvardDetection", "LinkedInProfileEnrichment", "TechnicalClassifier"]
