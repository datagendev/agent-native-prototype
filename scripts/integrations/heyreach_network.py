"""
Integration: HeyReach Network Data

Enriches leads with network relationship data (connections, mutual connections).
"""

from .base import Integration


class HeyReachNetwork(Integration):
    """Get HeyReach network and connection data."""

    input_cols = ["linkedin_url", "heyreach_sender_id"]
    output_cols = [
        "heyreach_is_connection",
        "heyreach_connection_degree",
        "heyreach_mutual_connections_count"
    ]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        # Get sender's network
        result = self.client.execute_tool(
            "mcp_Heyreach_get_my_network_for_sender",
            {
                "senderId": int(row["heyreach_sender_id"]),
                "limit": 1000,
                "offset": 0
            }
        )

        network = result.get("items", [])

        # Check if lead is in network
        lead_url = row["linkedin_url"]
        is_connection = False
        connection_degree = 3  # Assume 3rd+ degree by default
        mutual_count = 0

        for connection in network:
            if connection.get("profileUrl") == lead_url:
                is_connection = True
                connection_degree = 1
                mutual_count = connection.get("mutualConnectionsCount", 0)
                break

        # If not direct connection, check if 2nd degree (has mutual connections)
        if not is_connection:
            # This would require additional API calls to check mutual connections
            # For now, mark as not a connection
            connection_degree = 3

        return {
            "heyreach_is_connection": is_connection,
            "heyreach_connection_degree": connection_degree,
            "heyreach_mutual_connections_count": mutual_count
        }, ""


# Backward compatibility
_instance = HeyReachNetwork()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
