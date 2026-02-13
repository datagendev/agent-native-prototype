#!/usr/bin/env python3
"""
Generate comprehensive Instantly Email Infrastructure Health Report.

This script:
1. Fetches data via DataGen SDK + Instantly MCP tools
2. Analyzes domain health, campaign performance, inbox status
3. Generates branded HTML report with benchmarks and AI recommendations
4. Emails the report
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
from datagen_sdk import DatagenClient

# Initialize client
client = DatagenClient()

# Date range (last 30 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")
date_cutoff_ts = int(start_date.timestamp())

print(f"Fetching Instantly data for {start_date_str} to {end_date_str}...")

# ===== STEP 1: Fetch All Data =====

# 1.1 Fetch all accounts (with pagination)
print("Fetching accounts...")
all_accounts = []
next_cursor = None
page = 0

while page < 20:  # Safety limit
    params = {"limit": 100}
    if next_cursor:
        params["starting_after"] = next_cursor

    result = client.execute_tool("mcp_Instantly_list_accounts", {"params": params})

    # Handle response structure
    if isinstance(result, list) and len(result) > 0:
        data = result[0]
        items = data.get("items", [])
        all_accounts.extend(items)
        next_cursor = data.get("next_starting_after")
        page += 1
        if not next_cursor:
            break
    else:
        break

print(f"  → Fetched {len(all_accounts)} accounts")

# 1.2 Fetch campaign analytics
print("Fetching campaign analytics...")
campaign_analytics = client.execute_tool("mcp_Instantly_get_campaign_analytics", {
    "params": {"exclude_total_leads_count": True}
})
if isinstance(campaign_analytics, dict) and "campaigns" in campaign_analytics:
    campaigns = campaign_analytics["campaigns"]
else:
    campaigns = campaign_analytics if isinstance(campaign_analytics, list) else []

print(f"  → Fetched {len(campaigns)} campaigns")

# 1.3 Fetch replies (received emails)
print("Fetching replies...")
all_replies = []
next_cursor = None
page = 0

while page < 100:  # Safety limit
    params = {
        "email_type": "received",
        "mode": "emode_focused",
        "limit": 100,
        "preview_only": True
    }
    if next_cursor:
        params["starting_after"] = next_cursor

    result = client.execute_tool("mcp_Instantly_list_emails", {"params": params})

    if isinstance(result, list) and len(result) > 0:
        data = result[0]
        items = data.get("items", [])
        all_replies.extend(items)
        next_cursor = data.get("next_starting_after")
        page += 1
        if not next_cursor:
            break
    else:
        break

# Filter replies to last 30 days
replies_30d = [r for r in all_replies if r.get("timestamp_created_unix", 0) >= date_cutoff_ts]
print(f"  → Fetched {len(all_replies)} total replies, {len(replies_30d)} in last 30 days")

# 1.4 Fetch daily campaign analytics (for sent/bounced data)
print("Fetching daily campaign analytics...")
daily_analytics = client.execute_tool("mcp_Instantly_get_daily_campaign_analytics", {
    "params": {
        "start_date": start_date_str,
        "end_date": end_date_str,
        "campaign_status": -99  # All statuses
    }
})

print(f"  → Fetched daily analytics")

# ===== STEP 2: Process Data =====

print("\nProcessing data...")

# 2.1 Build domain-level stats
domain_stats = defaultdict(lambda: {
    "sent": 0,
    "bounced": 0,
    "replies": 0,
    "accounts": set()
})

# Aggregate sent/bounced from campaigns
for campaign in campaigns:
    sent = campaign.get("sent", 0)
    bounced = campaign.get("bounced", 0)

    # We don't have per-domain breakdowns from campaign analytics
    # So we'll use account-level inference

# Better approach: aggregate from accounts
for account in all_accounts:
    email = account.get("email", "")
    domain = email.split("@")[1] if "@" in email else "unknown"
    domain_stats[domain]["accounts"].add(email)

# Add sent/bounced from campaign analytics by inferring sending domains
# This is approximate - we'll use campaign analytics totals
total_campaign_sent = sum(c.get("sent", 0) for c in campaigns)
total_campaign_bounced = sum(c.get("bounced", 0) for c in campaigns)

# Count replies per domain
for reply in replies_30d:
    from_email = reply.get("from_email", "")
    domain = from_email.split("@")[1] if "@" in from_email else "unknown"
    domain_stats[domain]["replies"] += 1

# For sent/bounced, we need to use campaign data
# Let's build per-campaign stats first
campaign_data = []
for campaign in campaigns:
    sent = campaign.get("sent", 0)
    replied = campaign.get("replied", 0)
    bounced = campaign.get("bounced", 0)

    campaign_data.append({
        "name": campaign.get("name", "Unknown"),
        "id": campaign.get("id"),
        "status": campaign.get("status"),
        "sent": sent,
        "replied": replied,
        "reply_rate": round((replied / sent * 100) if sent > 0 else 0, 2),
        "bounced": bounced,
        "bounce_rate": round((bounced / sent * 100) if sent > 0 else 0, 2),
        "opportunities": campaign.get("opportunities", 0)
    })

# Sort campaigns by sent desc
campaign_data.sort(key=lambda x: x["sent"], reverse=True)

# 2.2 Build inbox status by domain
inbox_by_domain = []
for domain, stats in domain_stats.items():
    accounts = list(stats["accounts"])
    account_details = [a for a in all_accounts if a.get("email", "").endswith(f"@{domain}")]

    total_accounts = len(accounts)
    active_accounts = sum(1 for a in account_details if a.get("status") == 1)
    errored_accounts = sum(1 for a in account_details if a.get("status", 0) < 0)

    warmup_scores = [a.get("stat_warmup_score", 0) for a in account_details if a.get("stat_warmup_score")]
    avg_warmup = sum(warmup_scores) / len(warmup_scores) if warmup_scores else 0

    daily_limits = [a.get("daily_limit", 0) for a in account_details]
    total_limit = sum(daily_limits)

    # Determine status
    replies = stats["replies"]
    if replies > 0:
        status = "sending"
    elif avg_warmup > 0:
        status = "active_warmup"
    else:
        status = "inactive"

    inbox_by_domain.append({
        "domain": domain,
        "status": status,
        "accounts": total_accounts,
        "active": active_accounts,
        "errored": errored_accounts,
        "warmup_health": round(avg_warmup, 1),
        "daily_limit": total_limit,
        "replies": replies
    })

# Sort by accounts desc
inbox_by_domain.sort(key=lambda x: x["accounts"], reverse=True)

# 2.3 Calculate summary stats
total_sent = sum(c["sent"] for c in campaign_data)
total_replies = sum(c["replied"] for c in campaign_data)
total_bounced = sum(c["bounced"] for c in campaign_data)
overall_reply_rate = round((total_replies / total_sent * 100) if total_sent > 0 else 0, 2)
overall_bounce_rate = round((total_bounced / total_sent * 100) if total_sent > 0 else 0, 2)

sending_domains = [d for d in inbox_by_domain if d["status"] == "sending"]
warmup_domains = [d for d in inbox_by_domain if d["status"] == "active_warmup"]

# ===== STEP 3: Generate HTML Report =====

print("\nGenerating HTML report...")

report_date = datetime.now().strftime("%Y-%m-%d")

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email Infrastructure Health Report - {report_date}</title>
<style>
:root {{
  --primary: #005047;
  --secondary: #00795e;
  --success: #219653;
  --danger: #D34053;
  --warning: #FFA70B;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-900: #111827;
}}

body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  background: #f9fafb;
  color: var(--gray-900);
  line-height: 1.6;
}}

.header {{
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: white;
  padding: 32px;
  border-radius: 8px;
  margin-bottom: 32px;
}}

.header h1 {{
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
}}

.header p {{
  margin: 0;
  opacity: 0.9;
  font-size: 16px;
}}

.summary-cards {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}}

.card {{
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--gray-200);
}}

.card-label {{
  font-size: 13px;
  color: var(--gray-500);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}}

.card-value {{
  font-size: 32px;
  font-weight: 700;
  color: var(--gray-900);
}}

.card-subtitle {{
  font-size: 14px;
  color: var(--gray-600);
  margin-top: 4px;
}}

.section {{
  background: white;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid var(--gray-200);
  margin-bottom: 24px;
}}

.section-header {{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--gray-100);
}}

.section-icon {{
  font-size: 24px;
  padding: 8px;
  border-radius: 8px;
}}

.section-title {{
  font-size: 20px;
  font-weight: 700;
  color: var(--gray-900);
  margin: 0;
}}

table {{
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}}

th {{
  background: var(--gray-50);
  padding: 12px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: var(--gray-600);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--gray-200);
}}

td {{
  padding: 12px;
  border-bottom: 1px solid var(--gray-100);
  font-size: 14px;
}}

tr:hover {{
  background: var(--gray-50);
}}

.badge {{
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}}

.badge-success {{
  background: rgba(33, 150, 83, 0.1);
  color: var(--success);
}}

.badge-warning {{
  background: rgba(255, 167, 11, 0.1);
  color: var(--warning);
}}

.badge-action {{
  background: rgba(211, 64, 83, 0.1);
  color: var(--danger);
}}

.badge-primary {{
  background: rgba(0, 80, 71, 0.1);
  color: var(--primary);
}}

.footer {{
  text-align: center;
  padding: 24px;
  color: var(--gray-500);
  font-size: 13px;
  margin-top: 32px;
}}

.footer a {{
  color: var(--primary);
  text-decoration: none;
}}
</style>
</head>
<body>

<div class="header">
  <h1>Email Infrastructure Health Report</h1>
  <p>{start_date_str} to {end_date_str} | Generated {report_date}</p>
</div>

<div class="summary-cards">
  <div class="card">
    <div class="card-label">Total Domains</div>
    <div class="card-value">{len(inbox_by_domain)}</div>
    <div class="card-subtitle">{len(sending_domains)} sending, {len(warmup_domains)} warming</div>
  </div>

  <div class="card">
    <div class="card-label">Total Accounts</div>
    <div class="card-value">{len(all_accounts)}</div>
    <div class="card-subtitle">{sum(d['active'] for d in inbox_by_domain)} active</div>
  </div>

  <div class="card">
    <div class="card-label">Emails Sent</div>
    <div class="card-value">{total_sent:,}</div>
    <div class="card-subtitle">{len(campaign_data)} campaigns</div>
  </div>

  <div class="card">
    <div class="card-label">Reply Rate</div>
    <div class="card-value">{overall_reply_rate}%</div>
    <div class="card-subtitle">{total_replies} replies</div>
  </div>
</div>

<div class="section">
  <div class="section-header">
    <div class="section-icon" style="background: rgba(0, 80, 71, 0.1);">📊</div>
    <h2 class="section-title">Executive Summary</h2>
  </div>
  <p>Infrastructure is {"healthy" if overall_bounce_rate < 2 and overall_reply_rate > 1 else "at risk" if overall_bounce_rate < 5 else "critical"}.
  {len(sending_domains)} of {len(inbox_by_domain)} domains are actively sending.
  Overall reply rate is {overall_reply_rate}% with a bounce rate of {overall_bounce_rate}%.
  {len(warmup_domains)} domains are in warmup and ready for activation.</p>
</div>

<div class="section">
  <div class="section-header">
    <div class="section-icon" style="background: rgba(33, 150, 83, 0.1);">📬</div>
    <h2 class="section-title">Inbox Status by Domain</h2>
  </div>
  <table>
    <tr>
      <th>Domain</th>
      <th>Status</th>
      <th>Accounts</th>
      <th>Active</th>
      <th>Warmup Health</th>
      <th>Daily Limit</th>
      <th>Replies (30d)</th>
    </tr>
"""

for domain_info in inbox_by_domain:
    status_badge = "success" if domain_info["status"] == "sending" else "warning" if domain_info["status"] == "active_warmup" else "primary"
    warmup_badge = "success" if domain_info["warmup_health"] >= 95 else "warning" if domain_info["warmup_health"] >= 80 else "action"

    html += f"""    <tr>
      <td><strong>{domain_info["domain"]}</strong></td>
      <td><span class="badge badge-{status_badge}">{domain_info["status"]}</span></td>
      <td>{domain_info["accounts"]}</td>
      <td>{domain_info["active"]}</td>
      <td><span class="badge badge-{warmup_badge}">{domain_info["warmup_health"]}</span></td>
      <td>{domain_info["daily_limit"]}</td>
      <td>{domain_info["replies"]}</td>
    </tr>
"""

html += f"""  </table>
</div>

<div class="section">
  <div class="section-header">
    <div class="section-icon" style="background: rgba(0, 80, 71, 0.1);">📈</div>
    <h2 class="section-title">Campaign Performance</h2>
  </div>
  <table>
    <tr>
      <th>Campaign</th>
      <th>Sent</th>
      <th>Replied</th>
      <th>Reply Rate</th>
      <th>Bounced</th>
      <th>Bounce Rate</th>
      <th>Opps</th>
    </tr>
"""

# Show top 15 campaigns by sent volume
for campaign in campaign_data[:15]:
    reply_badge_class = "success" if campaign["reply_rate"] >= 1.0 else "warning"
    bounce_badge_class = "success" if campaign["bounce_rate"] < 2.0 else "warning" if campaign["bounce_rate"] < 5.0 else "action"

    html += f"""    <tr>
      <td><strong>{campaign["name"][:50]}</strong></td>
      <td>{campaign["sent"]:,}</td>
      <td>{campaign["replied"]}</td>
      <td><span class="badge badge-{reply_badge_class}">{campaign["reply_rate"]}%</span></td>
      <td>{campaign["bounced"]}</td>
      <td><span class="badge badge-{bounce_badge_class}">{campaign["bounce_rate"]}%</span></td>
      <td>{campaign["opportunities"]}</td>
    </tr>
"""

html += """  </table>
</div>

<div class="section">
  <div class="section-header">
    <div class="section-icon" style="background: rgba(255, 167, 11, 0.1);">🎯</div>
    <h2 class="section-title">Strategic Recommendations</h2>
  </div>
  <ul style="list-style: none; padding: 0; margin: 0;">
"""

# Generate recommendations based on data
recommendations = []

# Recommendation 1: Warmup domains ready to activate
if len(warmup_domains) > 0:
    high_health_warmup = [d for d in warmup_domains if d["warmup_health"] >= 95]
    if high_health_warmup:
        total_capacity = sum(d["daily_limit"] for d in high_health_warmup)
        domains_list = ", ".join([d["domain"] for d in high_health_warmup[:3]])
        recommendations.append(
            f"<strong>Activate high-health warmup domains</strong> — {len(high_health_warmup)} domains "
            f"({domains_list}{', ...' if len(high_health_warmup) > 3 else ''}) have warmup health ≥95 and represent "
            f"{total_capacity:,} daily sending capacity. Add them to top-performing campaigns to scale volume."
        )

# Recommendation 2: Top performing campaigns to scale
top_campaigns = [c for c in campaign_data if c["reply_rate"] >= 2.0 and c["sent"] >= 100]
if top_campaigns:
    top_3 = top_campaigns[:3]
    recommendations.append(
        f"<strong>Scale high-performing campaigns</strong> — {top_3[0]['name']} ({top_3[0]['reply_rate']}% reply rate) "
        f"and {len(top_campaigns)-1} other campaigns are performing above 2% reply rate. Increase sending volume and daily limits."
    )

# Recommendation 3: Campaigns with high bounce rates
high_bounce_campaigns = [c for c in campaign_data if c["bounce_rate"] > 5.0 and c["sent"] >= 50]
if high_bounce_campaigns:
    recommendations.append(
        f"<strong>Address bounce rate issues</strong> — {len(high_bounce_campaigns)} campaigns have bounce rates >5%. "
        f"Review list quality, verify email addresses, and consider pausing until lists are cleaned."
    )

# Recommendation 4: Low reply rate campaigns
low_reply_campaigns = [c for c in campaign_data if c["reply_rate"] < 0.5 and c["sent"] >= 100]
if low_reply_campaigns:
    recommendations.append(
        f"<strong>Optimize low-performing campaigns</strong> — {len(low_reply_campaigns)} campaigns have <0.5% reply rate "
        f"despite significant volume. Test new messaging, improve targeting, or pause and reallocate capacity."
    )

# Recommendation 5: Inactive domains
inactive_domains = [d for d in inbox_by_domain if d["status"] == "inactive"]
if inactive_domains:
    recommendations.append(
        f"<strong>Review inactive domains</strong> — {len(inactive_domains)} domains have no recent activity. "
        f"Consider reactivating with warmup or retiring to simplify infrastructure management."
    )

for rec in recommendations:
    html += f"    <li style='padding: 12px 0; border-bottom: 1px solid var(--gray-100);'>{rec}</li>\n"

html += """  </ul>
</div>

<div class="footer">
  <p>Generated by DataGen Email Infrastructure Health Agent</p>
  <p><a href="https://datagen.dev">datagen.dev</a></p>
</div>

</body>
</html>
"""

# Save report
output_path = f"/home/user/repo/reports/instantly/health-report-{report_date}.html"
import os
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    f.write(html)

print(f"\n✓ Report saved to: {output_path}")

# ===== STEP 4: Email Report =====

print("\nSending email to david@automatedemand.com...")

try:
    email_result = client.execute_tool("mcp_Gmail_Yusheng_gmail_send_email", {
        "params": {
            "to": ["david@automatedemand.com"],
            "subject": f"Email Infrastructure Health Report - {report_date}",
            "body": "Your weekly email infrastructure health report is attached. View in an HTML-capable email client for full formatting.",
            "htmlBody": html,
            "mimeType": "multipart/alternative"
        }
    })
    print("✓ Email sent successfully!")
except Exception as e:
    print(f"✗ Email failed: {e}")
    print("  Report is still available locally.")

print("\n" + "="*60)
print("REPORT SUMMARY")
print("="*60)
print(f"Period: {start_date_str} to {end_date_str}")
print(f"Total Domains: {len(inbox_by_domain)} ({len(sending_domains)} sending, {len(warmup_domains)} warmup)")
print(f"Total Accounts: {len(all_accounts)}")
print(f"Total Sent: {total_sent:,}")
print(f"Reply Rate: {overall_reply_rate}%")
print(f"Bounce Rate: {overall_bounce_rate}%")
print(f"Top Recommendations: {len(recommendations)}")
print("="*60)
