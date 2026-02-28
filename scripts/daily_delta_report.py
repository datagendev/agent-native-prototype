#!/usr/bin/env python3
"""
Daily Delta Report Generator

Generates 24-hour delta reports showing only NEW activity:
- New signups and their behavior (PostHog)
- UI blockers: rage clicks, JS exceptions (PostHog)
- New deployments (Neon)
- Failed runs with categorized errors (Neon)
- Tool execution patterns (Neon)
- New agents created (Neon)

Saves results to tmp/daily-delta-report-{date}/ for AI summarization.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple

from datagen_sdk import DatagenClient, DatagenToolError

# Initialize DataGen client
client = DatagenClient()

# Error categories for classification
ERROR_PATTERNS = {
    "infrastructure": [
        r"rc=137",  # Modal OOM
        r"oom",
        r"timeout",
        r"timed out",
        r"rate limit",
        r"502 bad gateway",
        r"503 service unavailable",
        r"connection refused",
        r"api timeout"
    ],
    "platform_bug": [
        r"view '.*' not found",
        r"relation \".*\" does not exist",
        r"name 'input_vars' is not defined",
        r"credits check failed",
        r"missing env var",
        r"DATAGEN_API_KEY not found",
        r"modal.*environment variable"
    ],
    "mcp_issue": [
        r"mcp server.*not connected",
        r"oauth.*expired",
        r"mcp tool.*not found",
        r"remote mcp.*failed",
        r"authentication.*failed.*mcp"
    ],
    "user_code": [
        r"syntaxerror",
        r"typeerror",
        r"nameerror",
        r"attributeerror",
        r"indentationerror",
        r"keyerror",
        r"indexerror",
        r"valueerror"
    ],
    "third_party": [
        r"hubspot.*error",
        r"linkedin.*error",
        r"gmail.*error",
        r"airtable.*error",
        r"400 bad request",
        r"401 unauthorized",
        r"403 forbidden",
        r"404 not found"
    ]
}


def categorize_error(error_log: str) -> str:
    """
    Categorize error into one of five categories based on pattern matching.

    Categories:
    - infrastructure: Modal OOM, timeouts, rate limits
    - platform_bug: DataGen bugs (missing views, env vars)
    - mcp_issue: MCP connection/OAuth failures
    - user_code: User script errors
    - third_party: External API errors
    - unknown: No pattern match
    """
    if not error_log:
        return "unknown"

    error_lower = error_log.lower()

    # Check each category
    for category, patterns in ERROR_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, error_lower):
                return category

    return "unknown"


def fetch_posthog_24h(output_path: Path) -> Tuple[Dict, str]:
    """
    Fetch PostHog data for last 24 hours.
    Returns (result, error) tuple.
    """
    print("📊 Fetching PostHog 24h data...")

    try:
        # Query 1: New signups with behavior
        signup_query = """
        SELECT
          person.properties.email as email,
          count() as pageviews,
          groupArray(DISTINCT properties.$pathname) as pages_visited,
          min(timestamp) as first_seen,
          max(timestamp) as last_seen,
          dateDiff('minute', min(timestamp), max(timestamp)) as session_duration_minutes
        FROM events
        WHERE event = '$pageview'
          AND timestamp > now() - INTERVAL 1 DAY
          AND person.properties.email NOT LIKE '%@datagen.dev'
          AND person.properties.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
        GROUP BY email
        HAVING count() > 0
        ORDER BY first_seen DESC
        """

        signups_result = client.execute_tool("mcp_Posthog_insight_create_from_query", {
            "data": {
                "name": "New Signups 24h",
                "query": {
                    "kind": "DataVisualizationNode",
                    "source": {"kind": "HogQLQuery", "query": signup_query}
                },
                "favorited": False
            }
        })

        # Query 2: UI blockers (rage clicks + exceptions)
        ui_blockers_query = """
        SELECT
          person.properties.email as email,
          event,
          properties.$pathname as page,
          properties.$exception_message as error_msg,
          properties.$exception_type as error_type,
          timestamp,
          properties.$current_url as url
        FROM events
        WHERE event IN ('$rageclick', '$exception')
          AND timestamp > now() - INTERVAL 1 DAY
          AND person.properties.email NOT LIKE '%@datagen.dev'
          AND person.properties.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
        ORDER BY timestamp DESC
        LIMIT 100
        """

        ui_blockers_result = client.execute_tool("mcp_Posthog_insight_create_from_query", {
            "data": {
                "name": "UI Blockers 24h",
                "query": {
                    "kind": "DataVisualizationNode",
                    "source": {"kind": "HogQLQuery", "query": ui_blockers_query}
                },
                "favorited": False
            }
        })

        # Query 3: MCP connect clicks
        mcp_clicks_query = """
        SELECT
          person.properties.email as email,
          properties.template_name as mcp_server,
          properties.template_id as template_id,
          properties.has_oauth as requires_oauth,
          count() as clicks,
          min(timestamp) as first_click,
          max(timestamp) as last_click
        FROM events
        WHERE event = 'mcp_connect_clicked'
          AND timestamp > now() - INTERVAL 1 DAY
          AND person.properties.email NOT LIKE '%@datagen.dev'
          AND person.properties.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
        GROUP BY email, mcp_server, template_id, requires_oauth
        ORDER BY first_click DESC
        """

        mcp_clicks_result = client.execute_tool("mcp_Posthog_insight_create_from_query", {
            "data": {
                "name": "MCP Clicks 24h",
                "query": {
                    "kind": "DataVisualizationNode",
                    "source": {"kind": "HogQLQuery", "query": mcp_clicks_query}
                },
                "favorited": False
            }
        })

        # Combine results
        posthog_data = {
            "new_signups": signups_result.get("results", []),
            "ui_blockers": ui_blockers_result.get("results", []),
            "mcp_clicks": mcp_clicks_result.get("results", [])
        }

        # Save to file
        with open(output_path, "w") as f:
            json.dump(posthog_data, f, indent=2)

        print(f"  ✓ {len(posthog_data['new_signups'])} new signups")
        print(f"  ✓ {len(posthog_data['ui_blockers'])} UI blockers")
        print(f"  ✓ {len(posthog_data['mcp_clicks'])} MCP connect clicks")

        return posthog_data, ""

    except Exception as e:
        error_msg = f"PostHog fetch failed: {str(e)}"
        print(f"  ✗ {error_msg}")
        return {}, error_msg


def fetch_neon_fastapi_24h(output_path: Path) -> Tuple[Dict, str]:
    """
    Fetch Neon FastAPI data for last 24 hours.
    Returns (result, error) tuple.
    """
    print("🗄️  Fetching Neon FastAPI 24h data...")

    try:
        # Query 4: New deployments
        deployments_query = """
        SELECT
          w.email,
          d.id as deployment_id,
          d.name as deployment_name,
          d.description,
          d.created_at,
          d.updated_at,
          LENGTH(d.final_code) as code_length,
          d.deployment_type
        FROM fastapi_deployment d
        JOIN fastapi_user f ON d.user_id = f.id
        JOIN wasp_user w ON f.wasp_user_id = w.id
        WHERE d.created_at > NOW() - INTERVAL '24 hours'
          AND w.email NOT LIKE '%@datagen.dev'
          AND w.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
        ORDER BY d.created_at DESC
        """

        deployments = client.execute_tool("mcp_Neon_run_sql", {
            "projectId": "rough-base-02149126",
            "databaseName": "datagen",
            "sql": deployments_query
        })

        # Query 5: Failed runs with error logs
        failed_runs_query = """
        SELECT
          w.email,
          r.id as run_id,
          r.run_state,
          r.created_at,
          r.run_error_log,
          LENGTH(r.run_error_log) as error_length,
          d.name as deployment_name
        FROM fastapi_run r
        JOIN fastapi_user f ON r.user_id = f.id
        JOIN wasp_user w ON f.wasp_user_id = w.id
        LEFT JOIN fastapi_deployment d ON r.deployment_id = d.id
        WHERE r.created_at > NOW() - INTERVAL '24 hours'
          AND r.run_state = 'failed'
          AND w.email NOT LIKE '%@datagen.dev'
          AND w.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
        ORDER BY r.created_at DESC
        LIMIT 100
        """

        failed_runs = client.execute_tool("mcp_Neon_run_sql", {
            "projectId": "rough-base-02149126",
            "databaseName": "datagen",
            "sql": failed_runs_query
        })

        # Query 6: Tool executions by user
        tool_executions_query = """
        SELECT
          w.email,
          t.tool_name,
          t.tool_provider,
          t.tool_type,
          COUNT(*) as execution_count,
          COUNT(CASE WHEN t.status = 'success' THEN 1 END) as successes,
          COUNT(CASE WHEN t.status = 'failed' THEN 1 END) as failures,
          ROUND(AVG(t.execution_duration_ms)) as avg_duration_ms,
          MIN(t.created_at) as first_execution,
          MAX(t.created_at) as last_execution
        FROM fastapi_tool_executions t
        JOIN fastapi_user f ON t.user_id::integer = f.id
        JOIN wasp_user w ON f.wasp_user_id = w.id
        WHERE t.created_at > NOW() - INTERVAL '24 hours'
          AND w.email NOT LIKE '%@datagen.dev'
          AND w.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
        GROUP BY w.email, t.tool_name, t.tool_provider, t.tool_type
        ORDER BY execution_count DESC
        LIMIT 100
        """

        tool_executions = client.execute_tool("mcp_Neon_run_sql", {
            "projectId": "rough-base-02149126",
            "databaseName": "datagen",
            "sql": tool_executions_query
        })

        # Query 7: Failed tool executions
        failed_tools_query = """
        SELECT
          w.email,
          t.tool_name,
          t.tool_provider,
          t.status,
          t.error_type,
          t.error_message,
          t.created_at,
          t.execution_duration_ms
        FROM fastapi_tool_executions t
        JOIN fastapi_user f ON t.user_id::integer = f.id
        JOIN wasp_user w ON f.wasp_user_id = w.id
        WHERE t.created_at > NOW() - INTERVAL '24 hours'
          AND t.status = 'failed'
          AND w.email NOT LIKE '%@datagen.dev'
          AND w.email NOT IN ('ravi@fulllist.ai', 'catecean20@gmail.com')
        ORDER BY t.created_at DESC
        LIMIT 100
        """

        failed_tools = client.execute_tool("mcp_Neon_run_sql", {
            "projectId": "rough-base-02149126",
            "databaseName": "datagen",
            "sql": failed_tools_query
        })

        # Combine results
        neon_fastapi_data = {
            "new_deployments": deployments.get("rows", []),
            "failed_runs": failed_runs.get("rows", []),
            "tool_executions": tool_executions.get("rows", []),
            "failed_tools": failed_tools.get("rows", [])
        }

        # Save to file
        with open(output_path, "w") as f:
            json.dump(neon_fastapi_data, f, indent=2)

        print(f"  ✓ {len(neon_fastapi_data['new_deployments'])} new deployments")
        print(f"  ✓ {len(neon_fastapi_data['failed_runs'])} failed runs")
        print(f"  ✓ {len(neon_fastapi_data['tool_executions'])} tool execution patterns")
        print(f"  ✓ {len(neon_fastapi_data['failed_tools'])} failed tool executions")

        return neon_fastapi_data, ""

    except Exception as e:
        error_msg = f"Neon FastAPI fetch failed: {str(e)}"
        print(f"  ✗ {error_msg}")
        return {}, error_msg


def fetch_neon_wasp_24h(output_path: Path) -> Tuple[Dict, str]:
    """
    Fetch Neon Wasp agent data for last 24 hours.
    Returns (result, error) tuple.
    """
    print("🤖 Fetching Neon Wasp 24h data...")

    try:
        # Query 8: New agents created/deployed
        new_agents_query = """
        SELECT
          ae.id as execution_id,
          ae.agent_id,
          ae.status,
          LEFT(ae.entry_prompt, 200) as entry_prompt_preview,
          LEFT(ae.result, 200) as result_preview,
          ae.duration_ms,
          ae.started_at,
          ae.completed_at,
          LENGTH(ae.entry_prompt) as prompt_length,
          LENGTH(ae.result) as result_length
        FROM wasp_agentexecution ae
        WHERE ae.started_at > NOW() - INTERVAL '24 hours'
        ORDER BY ae.started_at DESC
        LIMIT 50
        """

        new_agents = client.execute_tool("mcp_Neon_run_sql", {
            "projectId": "rough-base-02149126",
            "databaseName": "datagen",
            "sql": new_agents_query
        })

        # Combine results
        neon_wasp_data = {
            "new_agents": new_agents.get("rows", [])
        }

        # Save to file
        with open(output_path, "w") as f:
            json.dump(neon_wasp_data, f, indent=2)

        print(f"  ✓ {len(neon_wasp_data['new_agents'])} new agents")

        return neon_wasp_data, ""

    except Exception as e:
        error_msg = f"Neon Wasp fetch failed: {str(e)}"
        print(f"  ✗ {error_msg}")
        return {}, error_msg


def categorize_all_errors(failed_runs: List[Dict], failed_tools: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group errors by category for reporting.
    Combines failed runs and failed tool executions.
    """
    print("🏷️  Categorizing errors...")

    categorized = {
        "infrastructure": [],
        "platform_bug": [],
        "mcp_issue": [],
        "user_code": [],
        "third_party": [],
        "unknown": []
    }

    # Categorize failed runs
    for run in failed_runs:
        error_log = run.get("run_error_log", "")
        category = categorize_error(error_log)
        categorized[category].append({
            "type": "run",
            "email": run.get("email"),
            "run_id": run.get("run_id"),
            "deployment_name": run.get("deployment_name"),
            "error_preview": error_log[:200] if error_log else "",
            "error_full": error_log,
            "created_at": run.get("created_at")
        })

    # Categorize failed tool executions
    for tool in failed_tools:
        error_msg = tool.get("error_message", "")
        category = categorize_error(error_msg)
        categorized[category].append({
            "type": "tool",
            "email": tool.get("email"),
            "tool_name": tool.get("tool_name"),
            "tool_provider": tool.get("tool_provider"),
            "error_type": tool.get("error_type"),
            "error_message": error_msg,
            "created_at": tool.get("created_at")
        })

    # Print summary
    for category, errors in categorized.items():
        if errors:
            print(f"  ✓ {category}: {len(errors)} errors")

    return categorized


def load_previous_day_data(date: str) -> Tuple[Dict, str]:
    """
    Load previous day's data for delta comparison.
    Returns (result, error) tuple.
    """
    prev_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    prev_path = Path(f"tmp/daily-delta-report-{prev_date}")

    if not prev_path.exists():
        return {}, f"No previous day data found at {prev_path}"

    print(f"📂 Loading previous day data ({prev_date})...")

    try:
        previous_data = {}

        # Load each file if it exists
        for filename in ["posthog_24h.json", "neon_fastapi_24h.json", "neon_wasp_24h.json", "errors_categorized.json"]:
            filepath = prev_path / filename
            if filepath.exists():
                with open(filepath, "r") as f:
                    previous_data[filename.replace(".json", "")] = json.load(f)

        print(f"  ✓ Loaded {len(previous_data)} files from previous day")
        return previous_data, ""

    except Exception as e:
        return {}, f"Failed to load previous day data: {str(e)}"


def calculate_deltas(current: Dict, previous: Dict) -> Dict:
    """
    Calculate what's NEW vs recurring vs resolved.
    """
    print("📊 Calculating deltas...")

    deltas = {
        "meta": {
            "has_previous_data": bool(previous),
            "comparison_available": bool(previous)
        }
    }

    if not previous:
        print("  ℹ️  No previous data - showing all as new")
        return deltas

    # Compare new signups
    current_emails = set([s.get("email") for s in current.get("posthog_24h", {}).get("new_signups", [])])
    previous_emails = set([s.get("email") for s in previous.get("posthog_24h", {}).get("new_signups", [])])
    new_emails = current_emails - previous_emails

    deltas["new_signups"] = {
        "today": len(current_emails),
        "yesterday": len(previous_emails),
        "delta": len(current_emails) - len(previous_emails),
        "new_emails": list(new_emails)
    }

    print(f"  ✓ Signups: {len(current_emails)} today, {len(previous_emails)} yesterday (Δ {deltas['new_signups']['delta']:+d})")

    # Compare error categories
    current_errors = current.get("errors_categorized", {})
    previous_errors = previous.get("errors_categorized", {})

    deltas["errors_by_category"] = {}

    for category in ["infrastructure", "platform_bug", "mcp_issue", "user_code", "third_party", "unknown"]:
        current_count = len(current_errors.get(category, []))
        previous_count = len(previous_errors.get(category, []))
        delta = current_count - previous_count

        status = "unchanged"
        if delta > 0:
            status = "worsening"
        elif delta < 0:
            status = "improving"

        deltas["errors_by_category"][category] = {
            "today": current_count,
            "yesterday": previous_count,
            "delta": delta,
            "status": status
        }

        if current_count > 0:
            print(f"  ✓ {category}: {current_count} today, {previous_count} yesterday (Δ {delta:+d}, {status})")

    return deltas


def main():
    """Main orchestration function."""
    date = datetime.now().strftime("%Y-%m-%d")
    tmp_dir = Path(f"tmp/daily-delta-report-{date}")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🚀 Daily Delta Report Generator - {date}")
    print("=" * 60)

    # Step 1: Fetch PostHog 24h data
    posthog_data, err = fetch_posthog_24h(tmp_dir / "posthog_24h.json")
    if err:
        # Save error but continue
        with open(tmp_dir / "errors.json", "a") as f:
            json.dump({"step": "posthog", "error": err, "timestamp": datetime.now().isoformat()}, f)
            f.write("\n")

    # Step 2: Fetch Neon FastAPI 24h data
    neon_fastapi_data, err = fetch_neon_fastapi_24h(tmp_dir / "neon_fastapi_24h.json")
    if err:
        with open(tmp_dir / "errors.json", "a") as f:
            json.dump({"step": "neon_fastapi", "error": err, "timestamp": datetime.now().isoformat()}, f)
            f.write("\n")

    # Step 3: Fetch Neon Wasp 24h data
    neon_wasp_data, err = fetch_neon_wasp_24h(tmp_dir / "neon_wasp_24h.json")
    if err:
        with open(tmp_dir / "errors.json", "a") as f:
            json.dump({"step": "neon_wasp", "error": err, "timestamp": datetime.now().isoformat()}, f)
            f.write("\n")

    # Step 4: Categorize errors
    categorized = categorize_all_errors(
        neon_fastapi_data.get("failed_runs", []),
        neon_fastapi_data.get("failed_tools", [])
    )
    with open(tmp_dir / "errors_categorized.json", "w") as f:
        json.dump(categorized, f, indent=2)

    # Step 5: Load previous day for comparison
    previous_data, err = load_previous_day_data(date)
    if err:
        print(f"  ℹ️  {err}")
        previous_data = {}

    # Step 6: Calculate deltas
    deltas = calculate_deltas(
        current={
            "posthog_24h": posthog_data,
            "neon_fastapi_24h": neon_fastapi_data,
            "neon_wasp_24h": neon_wasp_data,
            "errors_categorized": categorized
        },
        previous=previous_data
    )

    with open(tmp_dir / "deltas.json", "w") as f:
        json.dump(deltas, f, indent=2)

    print("=" * 60)
    print(f"✅ 24h delta data saved to {tmp_dir}")
    print(f"\nFiles generated:")
    for file in tmp_dir.iterdir():
        print(f"  - {file.name} ({file.stat().st_size} bytes)")
    print()


if __name__ == "__main__":
    main()
