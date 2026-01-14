"""
Integration Registry

This file defines all available enrichment integrations for Claude to discover.
Each integration specifies input columns required and output columns produced.

Now supports both class-based and module-level APIs.
"""

from .linkedin_profile import LinkedInProfile
from .web_research import WebResearch
from .find_ceo import FindCEO
from .heyreach_engagement import HeyReachEngagement
from .heyreach_campaigns import HeyReachCampaigns
from .heyreach_network import HeyReachNetwork
from .heyreach_campaign_stats import HeyReachCampaignStats
from .linkedin_post_activity import LinkedInPostActivity
from .linkedin_claude_mentions import LinkedInClaudeMentions


# Class-based registry (NEW)
INTEGRATION_CLASSES = {
    "linkedin_profile": LinkedInProfile,
    "web_research": WebResearch,
    "find_ceo": FindCEO,
    "heyreach_engagement": HeyReachEngagement,
    "heyreach_campaigns": HeyReachCampaigns,
    "heyreach_network": HeyReachNetwork,
    "heyreach_campaign_stats": HeyReachCampaignStats,
    "linkedin_post_activity": LinkedInPostActivity,
    "linkedin_claude_mentions": LinkedInClaudeMentions,
}


# Module-level registry (BACKWARD COMPATIBLE)
INTEGRATIONS = {
    "linkedin_profile": {
        "input": LinkedInProfile.input_cols,
        "output": LinkedInProfile.output_cols,
        "description": LinkedInProfile.__doc__ or "Get LinkedIn profile data"
    },
    "web_research": {
        "input": WebResearch.input_cols,
        "output": WebResearch.output_cols,
        "description": WebResearch.__doc__ or "Research company information"
    },
    "find_ceo": {
        "input": FindCEO.input_cols,
        "output": FindCEO.output_cols,
        "description": FindCEO.__doc__ or "Find CEO information"
    },
    "heyreach_engagement": {
        "input": HeyReachEngagement.input_cols,
        "output": HeyReachEngagement.output_cols,
        "description": HeyReachEngagement.__doc__ or "Get HeyReach engagement data"
    },
    "heyreach_campaigns": {
        "input": HeyReachCampaigns.input_cols,
        "output": HeyReachCampaigns.output_cols,
        "description": HeyReachCampaigns.__doc__ or "Get HeyReach campaign history"
    },
    "heyreach_network": {
        "input": HeyReachNetwork.input_cols,
        "output": HeyReachNetwork.output_cols,
        "description": HeyReachNetwork.__doc__ or "Get HeyReach network data"
    },
    "heyreach_campaign_stats": {
        "input": HeyReachCampaignStats.input_cols,
        "output": HeyReachCampaignStats.output_cols,
        "description": HeyReachCampaignStats.__doc__ or "Get HeyReach campaign reply rate stats"
    },
    "linkedin_post_activity": {
        "input": LinkedInPostActivity.input_cols,
        "output": LinkedInPostActivity.output_cols,
        "description": LinkedInPostActivity.__doc__ or "Get LinkedIn posting activity metrics"
    },
    "linkedin_claude_mentions": {
        "input": LinkedInClaudeMentions.input_cols,
        "output": LinkedInClaudeMentions.output_cols,
        "description": LinkedInClaudeMentions.__doc__ or "Find posts mentioning Claude Code"
    },
}


def list_integrations():
    """Return all available integrations."""
    return INTEGRATIONS


def get_integration(name: str):
    """Get integration metadata by name."""
    return INTEGRATIONS.get(name)


def get_integration_class(name: str):
    """Get integration class by name (NEW)."""
    return INTEGRATION_CLASSES.get(name)
