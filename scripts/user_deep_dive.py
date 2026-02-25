#!/usr/bin/env python3
"""Deep dive analysis for a specific user across custom runs, tool executions, and agent usage."""

import os
import sys
import json
from datetime import datetime
from collections import defaultdict
from datagen_sdk import DatagenClient

def analyze_user(email: str):
    """Analyze user activity across all dimensions."""
    client = DatagenClient()

    print(f"\n{'='*80}")
    print(f"🔍 Deep Dive Analysis: {email}")
    print(f"{'='*80}\n")

    # 1. User Profile
    print("📊 USER PROFILE")
    print("-" * 80)
    user_query = f"""
    SELECT
        email,
        created_at,
        last_sign_in_at,
        sign_in_count,
        EXTRACT(DAY FROM (NOW() - created_at)) as days_active
    FROM auth.users
    WHERE email = '{email}'
    LIMIT 1;
    """

    try:
        user_info = client.execute_tool("mcp_Neon_run_sql", {
            "sql": user_query,
            "projectId": "late-sunset-16688092"
        })

        if user_info and len(user_info) > 0:
            user = user_info[0]
            print(f"Email: {user.get('email')}")
            print(f"Account Created: {user.get('created_at')}")
            print(f"Days Active: {user.get('days_active')}")
            print(f"Last Sign In: {user.get('last_sign_in_at')}")
            print(f"Total Sign Ins: {user.get('sign_in_count')}")
        else:
            print(f"❌ User not found: {email}")
            return
    except Exception as e:
        print(f"❌ Error fetching user info: {e}")
        return

    # 2. Custom Tool Runs
    print(f"\n🔧 CUSTOM TOOL RUNS")
    print("-" * 80)
    custom_runs_query = f"""
    SELECT
        cr.run_uuid,
        cr.status,
        cr.created_at,
        cr.completed_at,
        d.deployment_name,
        d.description,
        EXTRACT(EPOCH FROM (COALESCE(cr.completed_at, NOW()) - cr.created_at)) as duration_seconds
    FROM public.custom_runs cr
    JOIN public.deployments d ON cr.deployment_uuid = d.deployment_uuid
    JOIN auth.users u ON cr.user_id = u.id
    WHERE u.email = '{email}'
    ORDER BY cr.created_at DESC;
    """

    try:
        custom_runs = client.execute_tool("mcp_Neon_run_sql", {
            "sql": custom_runs_query,
            "projectId": "late-sunset-16688092"
        })

        if custom_runs and len(custom_runs) > 0:
            print(f"Total Custom Tool Runs: {len(custom_runs)}")

            # Aggregate stats
            by_status = defaultdict(int)
            by_tool = defaultdict(int)
            total_duration = 0

            for run in custom_runs:
                status = run.get('status', 'unknown')
                by_status[status] += 1

                tool_name = run.get('deployment_name', 'unknown')
                by_tool[tool_name] += 1

                duration = run.get('duration_seconds')
                if duration is not None:
                    total_duration += float(duration)

            print(f"\n📊 By Status:")
            for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
                pct = (count / len(custom_runs)) * 100
                print(f"  {status}: {count} ({pct:.1f}%)")

            print(f"\n🔨 Top Custom Tools (by usage):")
            for tool, count in sorted(by_tool.items(), key=lambda x: x[1], reverse=True)[:10]:
                pct = (count / len(custom_runs)) * 100
                print(f"  {tool}: {count} ({pct:.1f}%)")

            print(f"\n⏱️  Total Execution Time: {total_duration:.0f}s ({total_duration/60:.1f} min / {total_duration/3600:.1f} hrs)")

            print(f"\n📅 Recent Activity (Last 5 Runs):")
            for run in custom_runs[:5]:
                created = run.get('created_at', '')[:19]
                print(f"  {created} | {run.get('deployment_name')} | {run.get('status')}")

            print(f"\n📅 First Run: {custom_runs[-1].get('created_at')}")
            print(f"📅 Latest Run: {custom_runs[0].get('created_at')}")
        else:
            print("No custom tool runs found")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 3. Tool Executions
    print(f"\n⚙️  TOOL EXECUTIONS")
    print("-" * 80)
    tool_exec_query = f"""
    SELECT
        te.id,
        te.tool_name,
        te.status,
        te.created_at,
        te.completed_at,
        EXTRACT(EPOCH FROM (COALESCE(te.completed_at, NOW()) - te.created_at)) as duration_seconds
    FROM public.tool_executions te
    JOIN auth.users u ON te.user_id = u.id
    WHERE u.email = '{email}'
    ORDER BY te.created_at DESC;
    """

    try:
        tool_execs = client.execute_tool("mcp_Neon_run_sql", {
            "sql": tool_exec_query,
            "projectId": "late-sunset-16688092"
        })

        if tool_execs and len(tool_execs) > 0:
            print(f"Total Tool Executions: {len(tool_execs)}")

            # Aggregate stats
            by_status = defaultdict(int)
            by_tool = defaultdict(int)
            by_provider = defaultdict(int)
            total_duration = 0

            for exec in tool_execs:
                status = exec.get('status', 'unknown')
                by_status[status] += 1

                tool_name = exec.get('tool_name', 'unknown')
                by_tool[tool_name] += 1

                # Extract provider from tool name (mcp_Provider_tool format)
                if tool_name.startswith('mcp_'):
                    parts = tool_name.split('_')
                    if len(parts) >= 2:
                        provider = parts[1]
                        by_provider[provider] += 1
                else:
                    by_provider['default'] += 1

                duration = exec.get('duration_seconds')
                if duration is not None:
                    total_duration += float(duration)

            print(f"\n📊 By Status:")
            for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
                pct = (count / len(tool_execs)) * 100
                print(f"  {status}: {count} ({pct:.1f}%)")

            print(f"\n🔧 Most Used Tools (Top 20):")
            for tool, count in sorted(by_tool.items(), key=lambda x: x[1], reverse=True)[:20]:
                pct = (count / len(tool_execs)) * 100
                print(f"  {tool}: {count} ({pct:.1f}%)")

            print(f"\n🏢 By Provider:")
            for provider, count in sorted(by_provider.items(), key=lambda x: x[1], reverse=True):
                pct = (count / len(tool_execs)) * 100
                print(f"  {provider}: {count} ({pct:.1f}%)")

            print(f"\n⏱️  Total Execution Time: {total_duration:.0f}s ({total_duration/60:.1f} min / {total_duration/3600:.1f} hrs)")

            print(f"\n📅 Activity Timeline:")
            print(f"  First execution: {tool_execs[-1].get('created_at')}")
            print(f"  Latest execution: {tool_execs[0].get('created_at')}")
        else:
            print("No tool executions found")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 4. Agent Executions
    print(f"\n🤖 AGENT EXECUTIONS")
    print("-" * 80)
    agent_exec_query = f"""
    SELECT
        ae.id,
        ae.agent_name,
        ae.status,
        ae.created_at,
        ae.completed_at,
        EXTRACT(EPOCH FROM (COALESCE(ae.completed_at, NOW()) - ae.created_at)) as duration_seconds
    FROM public.agent_executions ae
    JOIN auth.users u ON ae.user_id = u.id
    WHERE u.email = '{email}'
    ORDER BY ae.created_at DESC;
    """

    try:
        agent_execs = client.execute_tool("mcp_Neon_run_sql", {
            "sql": agent_exec_query,
            "projectId": "late-sunset-16688092"
        })

        if agent_execs and len(agent_execs) > 0:
            print(f"Total Agent Executions: {len(agent_execs)}")

            # Aggregate stats
            by_status = defaultdict(int)
            by_agent = defaultdict(int)
            total_duration = 0

            for exec in agent_execs:
                status = exec.get('status', 'unknown')
                by_status[status] += 1

                agent_name = exec.get('agent_name', 'unknown')
                by_agent[agent_name] += 1

                duration = exec.get('duration_seconds')
                if duration is not None:
                    total_duration += float(duration)

            print(f"\n📊 By Status:")
            for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
                pct = (count / len(agent_execs)) * 100
                print(f"  {status}: {count} ({pct:.1f}%)")

            print(f"\n🤖 By Agent Type:")
            for agent, count in sorted(by_agent.items(), key=lambda x: x[1], reverse=True):
                pct = (count / len(agent_execs)) * 100
                print(f"  {agent}: {count} ({pct:.1f}%)")

            print(f"\n⏱️  Total Execution Time: {total_duration:.0f}s ({total_duration/60:.1f} min / {total_duration/3600:.1f} hrs)")

            print(f"\n📅 Recent Runs (Last 5):")
            for exec in agent_execs[:5]:
                created = exec.get('created_at', '')[:19]
                print(f"  {created} | {exec.get('agent_name')} | {exec.get('status')}")

            print(f"\n📅 First Run: {agent_execs[-1].get('created_at')}")
            print(f"📅 Latest Run: {agent_execs[0].get('created_at')}")
        else:
            print("No agent executions found")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 5. Summary
    total_custom = len(custom_runs) if custom_runs else 0
    total_tools = len(tool_execs) if tool_execs else 0
    total_agents = len(agent_execs) if agent_execs else 0

    print(f"\n{'='*80}")
    print(f"📈 GRAND TOTAL")
    print(f"{'='*80}")
    print(f"Custom Tool Runs:  {total_custom:>6}")
    print(f"Tool Executions:   {total_tools:>6}")
    print(f"Agent Executions:  {total_agents:>6}")
    print(f"{'─'*80}")
    print(f"Total Actions:     {total_custom + total_tools + total_agents:>6}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "andriyvovchak15@gmail.com"
    analyze_user(email)
