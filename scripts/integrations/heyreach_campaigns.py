"""
Integration: HeyReach Campaign Context

Enriches leads with HeyReach campaign history and contact timeline.
"""

from .base import Integration
from datetime import datetime


class HeyReachCampaigns(Integration):
    """Get HeyReach campaign history for a lead."""

    input_cols = ["linkedin_url"]
    output_cols = [
        "heyreach_campaign_count",
        "heyreach_first_contacted_date",
        "heyreach_campaign_names",
        "heyreach_last_campaign_status"
    ]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        # Get all campaigns for this lead
        result = self.client.execute_tool(
            "mcp_Heyreach_get_campaigns_for_lead",
            {"linkedInProfileUrl": row["linkedin_url"]}
        )

        campaigns = result.get("items", [])

        if not campaigns:
            return {
                "heyreach_campaign_count": 0,
                "heyreach_first_contacted_date": "",
                "heyreach_campaign_names": "",
                "heyreach_last_campaign_status": ""
            }, ""

        # Extract campaign data
        campaign_count = len(campaigns)
        campaign_names = [c.get("name", "") for c in campaigns]

        # Find first contacted date (earliest campaign creation)
        dates = []
        for c in campaigns:
            if c.get("creationTime"):
                dates.append(datetime.fromisoformat(c["creationTime"].replace('Z', '+00:00')))

        first_contacted = min(dates) if dates else None

        # Last campaign status
        last_campaign_status = campaigns[0].get("status", "") if campaigns else ""

        return {
            "heyreach_campaign_count": campaign_count,
            "heyreach_first_contacted_date": first_contacted.isoformat() if first_contacted else "",
            "heyreach_campaign_names": ", ".join(campaign_names),
            "heyreach_last_campaign_status": last_campaign_status
        }, ""


# Backward compatibility
_instance = HeyReachCampaigns()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
