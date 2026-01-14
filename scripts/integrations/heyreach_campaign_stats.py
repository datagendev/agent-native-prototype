"""
Integration: HeyReach Campaign Reply Rate

Enriches rows with HeyReach campaign reply rate metrics by campaign name.
"""

from .base import Integration


class HeyReachCampaignStats(Integration):
    """Get HeyReach campaign reply rate and stats by campaign name."""

    input_cols = ["campaign_name"]
    output_cols = [
        "heyreach_campaign_id",
        "heyreach_message_reply_rate",
        "heyreach_inmail_reply_rate",
        "heyreach_total_message_replies",
        "heyreach_total_inmail_replies"
    ]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        """
        Fetch campaign stats from HeyReach by campaign name.

        Workflow:
        1. Search for campaign by name
        2. Get campaign ID
        3. Fetch overall stats for that campaign

        Returns:
            (enriched_fields, error): Dict with reply rate metrics
        """
        campaign_name = row["campaign_name"]

        # Step 1: Search for campaign by name
        campaigns_result = self.client.execute_tool(
            "mcp_Heyreach_get_all_campaigns",
            {
                "statuses": [],
                "accountIds": [],
                "keyword": campaign_name,
                "limit": 10,
                "offset": 0
            }
        )

        # Parse campaigns
        if isinstance(campaigns_result, list) and len(campaigns_result) > 0:
            campaigns = campaigns_result[0].get("items", [])
        else:
            campaigns = []

        if not campaigns:
            return {}, f"Campaign not found: '{campaign_name}'"

        # Find exact match (case-insensitive)
        campaign = None
        for c in campaigns:
            if c.get("name", "").strip().lower() == campaign_name.strip().lower():
                campaign = c
                break

        # If no exact match, use first result
        if not campaign:
            campaign = campaigns[0]

        campaign_id = campaign.get("id")

        # Step 2: Get overall stats for this campaign
        stats_result = self.client.execute_tool(
            "mcp_Heyreach_get_overall_stats",
            {
                "accountIds": [],
                "campaignIds": [campaign_id],
                "startDate": None,
                "endDate": None
            }
        )

        # Parse stats
        if isinstance(stats_result, list) and len(stats_result) > 0:
            stats = stats_result[0].get("overallStats", {})
        else:
            stats = stats_result.get("overallStats", {}) if isinstance(stats_result, dict) else {}

        # Extract metrics
        message_reply_rate = stats.get("messageReplyRate", 0) * 100  # Convert to percentage
        inmail_reply_rate = stats.get("inMailReplyRate", 0) * 100
        total_message_replies = stats.get("totalMessageReplies", 0)
        total_inmail_replies = stats.get("totalInmailReplies", 0)

        return {
            "heyreach_campaign_id": campaign_id,
            "heyreach_message_reply_rate": round(message_reply_rate, 1),
            "heyreach_inmail_reply_rate": round(inmail_reply_rate, 1),
            "heyreach_total_message_replies": total_message_replies,
            "heyreach_total_inmail_replies": total_inmail_replies
        }, ""


# Backward compatibility: Module-level API
_instance = HeyReachCampaignStats()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
