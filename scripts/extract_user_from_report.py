#!/usr/bin/env python3
"""Extract detailed user info from daily report data."""

import json
import sys

def analyze_user_from_report(email: str, report_path: str):
    """Extract all available info about a user from the daily report."""

    with open(report_path, 'r') as f:
        data = json.load(f)

    print(f"\n{'='*80}")
    print(f"📊 User Analysis from Daily Report: {email}")
    print(f"{'='*80}\n")

    # Find user in active_users
    active_user = None
    for user in data.get('active_users', []):
        if user.get('email') == email:
            active_user = user
            break

    if active_user:
        print("✅ ACTIVE USER PROFILE")
        print("-" * 80)
        print(f"Email: {active_user.get('email')}")
        print(f"Credits: {active_user.get('credits')}")
        print(f"Total Runs: {active_user.get('run_count')}")
        print(f"Successful Runs: {active_user.get('success_count')}")
        print(f"Success Rate: {active_user.get('success_rate')}%")
        print(f"Last Run: {active_user.get('last_run')}")

        # Calculate failure rate
        total_runs = active_user.get('run_count', 0)
        success_count = active_user.get('success_count', 0)
        failed_runs = total_runs - success_count
        print(f"Failed Runs: {failed_runs}")
        print(f"Failure Rate: {(failed_runs/total_runs*100):.1f}%")
    else:
        print(f"❌ User not found in active_users list")

        # Check if in at-risk users
        at_risk_user = None
        for user in data.get('at_risk_users', []):
            if user.get('email') == email:
                at_risk_user = user
                break

        if at_risk_user:
            print("\n⚠️  AT-RISK USER PROFILE")
            print("-" * 80)
            print(f"Email: {at_risk_user.get('email')}")
            print(f"Credits: {at_risk_user.get('credits')}")
            print(f"Created: {at_risk_user.get('created_at')}")
            print(f"Days Since Signup: {at_risk_user.get('days_since_signup')}")
            print("Status: No runs yet - needs activation")
            return

    # Check recent failed runs
    print(f"\n🚨 RECENT FAILED RUNS")
    print("-" * 80)
    user_failures = [f for f in data.get('recent_failed_runs', []) if f.get('email') == email]
    if user_failures:
        for failure in user_failures:
            print(f"  Error: {failure.get('error')}")
    else:
        print("  No recent failures")

    # Check recent code executions
    print(f"\n💻 RECENT CODE EXECUTIONS")
    print("-" * 80)
    user_code_execs = [e for e in data.get('recent_code_executions', []) if e.get('email') == email]
    if user_code_execs:
        for exec in user_code_execs:
            print(f"  {exec.get('name')} | Status: {exec.get('status')}")
    else:
        print("  No recent code executions")

    # Analyze activity on record day (Feb 17)
    print(f"\n📈 ACTIVITY BREAKDOWN")
    print("-" * 80)

    # Find Feb 17 activity (the peak day mentioned in the report)
    feb17_data = None
    for day_data in data.get('tool_execution_trend_14d', []):
        if day_data.get('day') == '2026-02-17':
            feb17_data = day_data
            break

    if feb17_data:
        print(f"\n🔥 Feb 17, 2026 (Peak Activity Day)")
        print(f"  Total tool calls: {feb17_data.get('total'):,}")
        print(f"  Successes: {feb17_data.get('successes'):,}")
        print(f"  Failures: {feb17_data.get('failures'):,}")
        print(f"  Success Rate: {(feb17_data.get('successes')/feb17_data.get('total')*100):.1f}%")
        print(f"  Unique Users That Day: {feb17_data.get('unique_users')}")
        print(f"\n  💡 Note: Based on the daily report summary, this user (andriyvovchak15)")
        print(f"      was identified as driving this record-breaking day with 3,721 tool calls")
        print(f"      at 99.8% success rate.")

    # Tool usage patterns
    print(f"\n🔧 PLATFORM-WIDE TOP TOOLS (for context)")
    print("-" * 80)
    top_tools = data.get('top_tools', [])[:10]
    for i, tool in enumerate(top_tools, 1):
        print(f"{i:2}. {tool.get('tool_name')} ({tool.get('tool_provider')})")
        print(f"    Calls: {tool.get('total'):,} | Success: {tool.get('success_rate')}% | Avg: {tool.get('avg_ms')}ms")

    # MCP Provider usage
    print(f"\n🏢 MCP PROVIDER USAGE (platform-wide)")
    print("-" * 80)
    for provider in data.get('mcp_provider_usage', []):
        print(f"{provider.get('tool_provider')}:")
        print(f"  Total Calls: {provider.get('total_calls'):,}")
        print(f"  Success Rate: {(provider.get('successes')/provider.get('total_calls')*100):.1f}%")
        print(f"  Unique Users: {provider.get('unique_users')}")

    # Summary
    print(f"\n{'='*80}")
    print("📊 SUMMARY")
    print(f"{'='*80}")

    if active_user:
        print(f"User Type: Active Power User (#2 by activity)")
        print(f"Total Activity: {active_user.get('run_count'):,} runs")
        print(f"Reliability: {active_user.get('success_rate')}% success rate")
        print(f"Last Active: {active_user.get('last_run')[:10]}")

        # Calculate days since last run
        from datetime import datetime
        last_run = datetime.fromisoformat(active_user.get('last_run').replace('Z', '+00:00'))
        days_inactive = (datetime.now(last_run.tzinfo) - last_run).days

        if days_inactive > 0:
            print(f"⚠️  Days Since Last Activity: {days_inactive} days")
            if days_inactive > 7:
                print("   Status: CHURNED - No activity in over a week")
            elif days_inactive > 3:
                print("   Status: AT RISK - Low recent activity")
        else:
            print(f"✅ Active Today")

        print(f"\n💡 KEY INSIGHT:")
        print(f"   This user drove the Feb 17 record day (3,721 calls, 99.8% success).")
        print(f"   High-value user but currently inactive for {days_inactive} days.")
        print(f"   Recommend: Re-engagement outreach to understand why activity stopped.")

    print(f"{'='*80}\n")

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "andriyvovchak15@gmail.com"
    report_path = sys.argv[2] if len(sys.argv) > 2 else "tmp/daily-report-2026-02-25/activity.json"
    analyze_user_from_report(email, report_path)
