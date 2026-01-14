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

# Registry of available nodes
NODES = {
    "yc_founder_lookup": YCFounderLookup,
    "linkedin_posts_scraper": LinkedInPostsScraper,
    "claude_code_detector": ClaudeCodeDetector,
    "b2b_classifier": B2BClassifier,
}

__all__ = ["NODES", "YCFounderLookup", "LinkedInPostsScraper", "ClaudeCodeDetector", "B2BClassifier"]
