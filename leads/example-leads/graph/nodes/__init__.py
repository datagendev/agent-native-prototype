"""
Nodes: Reusable enrichment components.

Each node is a Python class that:
- Takes specific inputs
- Produces specific outputs
- Can be configured via parameters

Nodes are composed into workflows via graph.yaml
"""

from .keyword_mentions import KeywordMentions
from .profile_enrichment import ProfileEnrichment
from .find_ceo import FindCEO

# Registry of available nodes
NODES = {
    "keyword_mentions": KeywordMentions,
    "profile_enrichment": ProfileEnrichment,
    "find_ceo": FindCEO,
}

__all__ = ["NODES", "KeywordMentions", "ProfileEnrichment", "FindCEO"]
