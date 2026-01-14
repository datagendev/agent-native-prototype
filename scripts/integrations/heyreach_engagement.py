"""
Integration: HeyReach Engagement Data

Enriches leads with HeyReach conversation and engagement metrics.
"""

from .base import Integration
from datetime import datetime


class HeyReachEngagement(Integration):
    """Get HeyReach engagement data (conversations, replies, meetings)."""

    input_cols = ["linkedin_url"]
    output_cols = [
        "heyreach_conversations_count",
        "heyreach_last_reply_date",
        "heyreach_meeting_booked",
        "heyreach_messages_sent",
        "heyreach_messages_received"
    ]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        # Get all conversations for this lead
        result = self.client.execute_tool(
            "mcp_Heyreach_get_conversations_v2",
            {
                "linkedInAccountIds": [],  # All accounts
                "campaignIds": [],         # All campaigns
                "leadProfileUrl": row["linkedin_url"],
                "searchString": "",
                "limit": 100,
                "offset": 0
            }
        )

        conversations = result.get("items", [])

        # Aggregate metrics
        total_conversations = len(conversations)
        last_reply_date = None
        meeting_booked = False
        messages_sent = 0
        messages_received = 0

        meeting_keywords = ["book", "calendar", "meeting", "schedule", "call",
                           "zoom", "calendly", "available", "time slot", "appointment"]

        for conv in conversations:
            messages = conv.get("messages", [])

            for msg in messages:
                body = msg.get("body", "").lower()
                sender = msg.get("sender")
                sent_at = msg.get("sentAt")

                if sender == "ME":
                    messages_sent += 1
                else:
                    messages_received += 1
                    # Track last reply date
                    if sent_at:
                        reply_date = datetime.fromisoformat(sent_at.replace('Z', '+00:00'))
                        if not last_reply_date or reply_date > last_reply_date:
                            last_reply_date = reply_date

                    # Check for meeting booking
                    if any(keyword in body for keyword in meeting_keywords):
                        meeting_booked = True

        return {
            "heyreach_conversations_count": total_conversations,
            "heyreach_last_reply_date": last_reply_date.isoformat() if last_reply_date else "",
            "heyreach_meeting_booked": meeting_booked,
            "heyreach_messages_sent": messages_sent,
            "heyreach_messages_received": messages_received
        }, ""


# Backward compatibility
_instance = HeyReachEngagement()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
