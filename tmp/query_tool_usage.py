#!/usr/bin/env python3
"""Query fastapi_tool_execution table to analyze tool usage patterns."""

import os
import sys
from datagen_sdk import DatagenClient
import json

def main():
    client = DatagenClient()

    # Query 1: User activity overview (last 7 days)
    print("=" * 80)
    print("TOOL USAGE BY USER (Last 7 Days)")
    print("=" * 80)

    usage_query = """
    SELECT
        user_id,
        COUNT(*) as total_executions,
        COUNT(DISTINCT tool_name) as unique_tools,
        COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as successful,
        COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed,
        ROUND(100.0 * COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) / COUNT(*), 1) as success_rate,
        MIN(created_at) as first_execution,
        MAX(created_at) as last_execution
    FROM fastapi_tool_execution
    WHERE created_at >= NOW() - INTERVAL '7 days'
    GROUP BY user_id
    ORDER BY total_executions DESC
    LIMIT 20
    """

    try:
        usage_result = client.execute_tool('mcp_Supabase_query', {'query': usage_query})
        print(json.dumps(usage_result, indent=2, default=str))
    except Exception as e:
        print(f"Error querying usage: {e}")
        return

    print("\n" + "=" * 80)
    print("MOST POPULAR TOOLS (Last 7 Days)")
    print("=" * 80)

    # Query 2: Most popular tools
    tools_query = """
    SELECT
        tool_name,
        COUNT(*) as execution_count,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as successful,
        ROUND(100.0 * COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) / COUNT(*), 1) as success_rate
    FROM fastapi_tool_execution
    WHERE created_at >= NOW() - INTERVAL '7 days'
    GROUP BY tool_name
    ORDER BY execution_count DESC
    LIMIT 20
    """

    try:
        tools_result = client.execute_tool('mcp_Supabase_query', {'query': tools_query})
        print(json.dumps(tools_result, indent=2, default=str))
    except Exception as e:
        print(f"Error querying tools: {e}")
        return

    print("\n" + "=" * 80)
    print("USER DETAILS")
    print("=" * 80)

    # Query 3: Get user emails
    users_query = """
    SELECT
        u.id,
        u.email,
        u.credits,
        COUNT(t.id) as executions_7d
    FROM users u
    LEFT JOIN fastapi_tool_execution t ON u.id = t.user_id
        AND t.created_at >= NOW() - INTERVAL '7 days'
    WHERE u.id IN (
        SELECT DISTINCT user_id
        FROM fastapi_tool_execution
        WHERE created_at >= NOW() - INTERVAL '7 days'
    )
    GROUP BY u.id, u.email, u.credits
    ORDER BY executions_7d DESC
    """

    try:
        users_result = client.execute_tool('mcp_Supabase_query', {'query': users_query})
        print(json.dumps(users_result, indent=2, default=str))
    except Exception as e:
        print(f"Error querying users: {e}")

if __name__ == "__main__":
    main()
