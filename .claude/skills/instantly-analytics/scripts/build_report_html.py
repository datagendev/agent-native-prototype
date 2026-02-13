#!/usr/bin/env python3
"""
Build the Email Infrastructure Health Report HTML from JSON data.

Reads the 3 instantly-analytics JSON reports + base template,
applies benchmark thresholds, generates deterministic HTML with
placeholder slots for LLM-generated content.

Usage:
    python build_report_html.py [--data-dir DIR] [--template PATH] [--output PATH]

Outputs HTML with two placeholders for LLM injection:
    {{EXECUTIVE_SUMMARY}} - 2-3 sentence overview
    {{RECOMMENDATIONS}}   - 3-5 strategic recommendations as <li> items
"""

import argparse
import json
import os
import sys
from datetime import datetime


# --- Benchmarks ---

BOUNCE_THRESHOLDS = {"healthy": 2.0, "warning": 5.0}  # < 2% healthy, 2-5% warning, > 5% critical
REPLY_THRESHOLDS = {"below_avg": 1.0, "avg": 5.0, "good": 10.0}  # < 1% below, 1-5% avg, 5-10% good
UTILIZATION_THRESHOLDS = {"under": 10.0, "healthy_low": 20.0, "healthy_high": 60.0, "over": 80.0}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def badge_html(text, style):
    return f'<span class="badge badge-{style}">{text}</span>'


def bounce_badge(rate):
    if rate > BOUNCE_THRESHOLDS["warning"]:
        return badge_html(f"{rate:.1f}%", "action")
    elif rate > BOUNCE_THRESHOLDS["healthy"]:
        return badge_html(f"{rate:.1f}%", "warning")
    else:
        return badge_html(f"{rate:.2f}%", "success")


def reply_badge(rate):
    if rate >= REPLY_THRESHOLDS["avg"]:
        return badge_html(f"{rate:.1f}%", "success")
    elif rate >= REPLY_THRESHOLDS["below_avg"]:
        return badge_html(f"{rate:.1f}%", "primary")
    else:
        return badge_html(f"{rate:.2f}%", "warning")


def overall_bounce_status(rate):
    if rate > BOUNCE_THRESHOLDS["warning"]:
        return "action"
    elif rate > BOUNCE_THRESHOLDS["healthy"]:
        return "warning"
    return "success"


def overall_reply_status(rate):
    if rate >= REPLY_THRESHOLDS["below_avg"]:
        return "success"
    return "warning"


# --- Action Item Builder ---

def build_action_items(domain_health, campaign_perf, inbox_status):
    p0, p1, p2 = [], [], []

    # Precompute totals for cross-data insights
    total_bounced = sum(d.get("bounced", 0) for d in domain_health.get("domains", []))

    # Domain-level checks
    for d in domain_health.get("domains", []):
        if d["sent"] == 0:
            continue
        name = d["domain"]
        bounced = d.get("bounced", 0)
        # P0: bounce > 5%
        if d["bounce_rate"] > BOUNCE_THRESHOLDS["warning"]:
            detail = f"<strong><a href='#' style='color: var(--danger);'>{name}</a> bounce rate at {d['bounce_rate']:.2f}%</strong> -- exceeds 5% threshold. "
            if total_bounced > 0:
                pct_of_total = (bounced / total_bounced) * 100
                detail += f"This domain accounts for {pct_of_total:.0f}% of all bounces in your infrastructure ({bounced} of {total_bounced}). "
            detail += "Pause sending, clean list, and audit domain reputation."
            p0.append(detail)
        # P0: bounce 2-5% on high-reply domains (protect best performers)
        elif d["bounce_rate"] > BOUNCE_THRESHOLDS["healthy"] and d["reply_rate"] >= 1.0:
            detail = f"<strong><a href='#' style='color: var(--danger);'>{name}</a> bounce rate at {d['bounce_rate']:.2f}%</strong> -- exceeds 2% threshold. "
            detail += f"This domain drives the most replies ({d['reply_rate']:.2f}%) but its deliverability is degrading. "
            detail += f"Investigate: is it list quality on specific campaigns, or domain reputation? "
            if total_bounced > 0:
                pct_of_total = (bounced / total_bounced) * 100
                detail += f"{pct_of_total:.0f}% of bounces in your infrastructure come from this single domain ({bounced} of {total_bounced})."
            p0.append(detail)
        # P1: bounce 2-5% on normal domains
        elif d["bounce_rate"] > BOUNCE_THRESHOLDS["healthy"]:
            p1.append(f"<strong>{name}</strong> bounce rate at {d['bounce_rate']:.1f}% (warning 2-5%). Investigate list quality and DNS records.")

    # P1: low reply domains (group together if many)
    low_reply_domains = []
    for d in domain_health.get("domains", []):
        if d["sent"] > 500 and d["reply_rate"] < 0.5:
            low_reply_domains.append(d)
    if len(low_reply_domains) > 3:
        names = ", ".join(d["domain"] for d in sorted(low_reply_domains, key=lambda x: x["reply_rate"])[:3])
        p1.append(f"<strong>{len(low_reply_domains)} domains with sub-0.5% reply rates.</strong> Worst performers: {names}. Review copy/targeting or redistribute volume to higher-performing domains.")
    else:
        for d in low_reply_domains:
            p1.append(f"<strong>{d['domain']}</strong> reply rate only {d['reply_rate']:.2f}% across {d['sent']} sent. Review copy/targeting for this domain.")

    # Inbox status checks
    ready_warmup = []
    for d in inbox_status.get("domains", []):
        name = d["domain"]
        # P0: errored accounts
        if d.get("errored", 0) > 0:
            p0.append(f"<strong>{name}</strong> has {d['errored']} errored account(s). Fix immediately.")
        # P0: warmup score < 95
        if d.get("warmup_health_score") and d["warmup_health_score"] < 95:
            p0.append(f"<strong>{name}</strong> warmup health score dropped to {d['warmup_health_score']}. Domain reputation at risk.")
        # Collect warmup domains ready to activate
        if d.get("status") == "active_warmup" and d.get("warmup_health_score", 0) >= 99.5:
            ready_warmup.append(d)
        # P1: severely underutilized sending domains
        if d.get("status") == "sending" and d.get("daily_limit_capacity", 0) > 0:
            utilization = (d.get("daily_send_volume", 0) / d["daily_limit_capacity"]) * 100
            if utilization < UTILIZATION_THRESHOLDS["under"]:
                p1.append(f"<strong>{name}</strong> using only {utilization:.0f}% of {d['daily_limit_capacity']} daily capacity. Ramp up or reassign.")

    # P1: group warmup domains into one item
    if ready_warmup:
        total_accounts = sum(d.get("total_accounts", 0) for d in ready_warmup)
        names = ", ".join(d["domain"] for d in ready_warmup)
        p1.append(f"<strong>{len(ready_warmup)} warmup domains ready to activate.</strong> {names} ({total_accounts} accounts total, all at 99.5%+ warmup health). Assign to campaigns to increase sending capacity.")

    # Campaign checks
    for c in campaign_perf.get("campaigns", []):
        name = c["campaign_name"]
        if c["sent"] > 500 and c["reply_rate"] < 0.5:
            p1.append(f"Campaign <strong>{name}</strong> has {c['reply_rate']:.2f}% reply rate across {c['sent']} sent. Review copy and targeting.")
        # P2: sentiment
        sentiment = c.get("reply_sentiment", {})
        neg = sentiment.get("negative", 0)
        pos = sentiment.get("positive", 0)
        total_sentiment = neg + pos + sentiment.get("unknown", 0)
        if total_sentiment > 3 and neg > pos:
            p2.append(f"Campaign <strong>{name}</strong> has more negative ({neg}) than positive ({pos}) sentiment. Monitor closely.")

    # P2: general monitoring items
    domains_sending = [d for d in domain_health.get("domains", []) if d["sent"] > 0]
    if len(domains_sending) >= 2:
        reply_rates = sorted(domains_sending, key=lambda d: d["reply_rate"], reverse=True)
        top = reply_rates[0]
        bottom = reply_rates[-1]
        if top["reply_rate"] > 0 and bottom["reply_rate"] > 0:
            ratio = top["reply_rate"] / bottom["reply_rate"]
            if ratio > 5:
                p2.append(f"Reply rate spread is {ratio:.0f}x between top ({top['domain']} at {top['reply_rate']:.2f}%) and bottom ({bottom['domain']} at {bottom['reply_rate']:.2f}%). Investigate what makes top domains perform better.")

    warmup_count = sum(1 for d in inbox_status.get("domains", []) if d.get("status") == "active_warmup")
    if warmup_count > 0:
        p2.append(f"{warmup_count} domain(s) still in warmup. Monitor progress toward activation threshold.")

    return p0, p1, p2


# --- HTML Builders ---

def build_summary_cards(domain_health, inbox_status):
    dh = domain_health["totals"]
    ix = inbox_status["totals"]
    sending_count = ix["by_status"].get("sending", 0)
    total_domains = ix["domains"]
    total_accounts = ix["total_accounts"]

    reply_status = overall_reply_status(dh["overall_reply_rate"])
    bounce_status = overall_bounce_status(dh["overall_bounce_rate"])

    return f"""
    <div class="summary-grid">
      <div class="summary-card">
        <div class="number">{sending_count} / {total_domains}</div>
        <div class="label">Sending Domains</div>
      </div>
      <div class="summary-card">
        <div class="number" style="color: var(--{reply_status})">{dh['overall_reply_rate']:.2f}%</div>
        <div class="label">Reply Rate</div>
      </div>
      <div class="summary-card">
        <div class="number" style="color: var(--{bounce_status})">{dh['overall_bounce_rate']:.2f}%</div>
        <div class="label">Bounce Rate</div>
      </div>
      <div class="summary-card">
        <div class="number">{total_accounts}</div>
        <div class="label">Total Accounts</div>
      </div>
    </div>"""


def build_executive_summary_section():
    return """
    <div class="section">
      <div class="section-header">
        <div class="section-icon info">&#128202;</div>
        <div>
          <h2>Executive Summary</h2>
        </div>
      </div>
      <p style="color: var(--gray-600); line-height: 1.7;">{{EXECUTIVE_SUMMARY}}</p>
    </div>"""


def build_action_items_section(p0, p1, p2):
    items_html = ""

    if p0:
        items_html += '<div style="margin-bottom: 20px;">'
        items_html += f'<div style="margin-bottom: 12px;"><span style="display: inline-block; padding: 4px 12px; background: rgba(211,64,83,0.1); color: var(--danger); border-radius: 100px; font-size: 13px; font-weight: 600;">P0 - Act Now</span></div>'
        for item in p0:
            items_html += f'<div style="padding: 12px 16px; background: rgba(211,64,83,0.04); border-left: 3px solid var(--danger); margin-bottom: 8px; border-radius: 0 6px 6px 0; font-size: 14px; color: var(--gray-700); line-height: 1.6;">{item}</div>'
        items_html += '</div>'

    if p1:
        items_html += '<div style="margin-bottom: 20px;">'
        items_html += f'<div style="margin-bottom: 12px;"><span style="display: inline-block; padding: 4px 12px; background: rgba(255,167,11,0.1); color: #b45309; border-radius: 100px; font-size: 13px; font-weight: 600;">P1 - This Week</span></div>'
        for item in p1:
            items_html += f'<div style="padding: 12px 16px; background: rgba(255,167,11,0.04); border-left: 3px solid var(--warning); margin-bottom: 8px; border-radius: 0 6px 6px 0; font-size: 14px; color: var(--gray-700); line-height: 1.6;">{item}</div>'
        items_html += '</div>'

    if p2:
        items_html += '<div style="margin-bottom: 20px;">'
        items_html += f'<div style="margin-bottom: 12px;"><span style="display: inline-block; padding: 4px 12px; background: rgba(0,80,71,0.1); color: var(--primary); border-radius: 100px; font-size: 13px; font-weight: 600;">P2 - Monitor</span></div>'
        for item in p2:
            items_html += f'<div style="padding: 12px 16px; background: rgba(0,80,71,0.04); border-left: 3px solid var(--primary); margin-bottom: 8px; border-radius: 0 6px 6px 0; font-size: 14px; color: var(--gray-700); line-height: 1.6;">{item}</div>'
        items_html += '</div>'

    if not (p0 or p1 or p2):
        items_html = '<div class="empty-state"><div class="empty-state-icon">&#9989;</div><p>No action items -- all metrics within healthy thresholds.</p></div>'

    return f"""
    <div class="section">
      <div class="section-header">
        <div class="section-icon action">&#127919;</div>
        <div>
          <h2>Action Items</h2>
          <p class="section-subtitle">{len(p0)} critical / {len(p1)} this week / {len(p2)} monitor</p>
        </div>
      </div>
      {items_html}
    </div>"""


def build_domain_table(domain_health):
    sending = [d for d in domain_health["domains"] if d["sent"] > 0]
    sending.sort(key=lambda d: d["reply_rate"], reverse=True)

    rows = ""
    for d in sending:
        rows += f"""
        <tr>
          <td class="email-cell">{d['domain']}</td>
          <td style="text-align:right">{d['sent']:,}</td>
          <td style="text-align:right">{d['replies']}</td>
          <td style="text-align:right">{reply_badge(d['reply_rate'])}</td>
          <td style="text-align:right">{d['bounced']}</td>
          <td style="text-align:right">{bounce_badge(d['bounce_rate'])}</td>
          <td style="text-align:right">{d['account_count']}</td>
        </tr>"""

    return f"""
    <div class="section">
      <div class="section-header">
        <div class="section-icon info">&#128200;</div>
        <div>
          <h2>Domain Performance</h2>
          <p class="section-subtitle">{len(sending)} sending domains, sorted by reply rate</p>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Domain</th>
              <th style="text-align:right">Sent</th>
              <th style="text-align:right">Replies</th>
              <th style="text-align:right">Reply %</th>
              <th style="text-align:right">Bounced</th>
              <th style="text-align:right">Bounce %</th>
              <th style="text-align:right">Accounts</th>
            </tr>
          </thead>
          <tbody>{rows}
          </tbody>
        </table>
      </div>
    </div>"""


def build_campaign_table(campaign_perf):
    campaigns = sorted(campaign_perf["campaigns"], key=lambda c: c["sent"], reverse=True)

    rows = ""
    for c in campaigns:
        sentiment = c.get("reply_sentiment", {})
        pos = sentiment.get("positive", 0)
        neg = sentiment.get("negative", 0)
        unk = sentiment.get("unknown", 0)
        sentiment_str = f"+{pos} / -{neg} / ?{unk}" if (pos + neg + unk) > 0 else "--"

        status_map = {1: "Active", 2: "Active", 3: "Paused"}
        status = status_map.get(c.get("status"), "Unknown")

        rows += f"""
        <tr>
          <td class="email-cell">{c['campaign_name']}</td>
          <td>{badge_html(status, "primary" if status == "Active" else "warning")}</td>
          <td style="text-align:right">{c['sent']:,}</td>
          <td style="text-align:right">{c['replied']}</td>
          <td style="text-align:right">{reply_badge(c['reply_rate'])}</td>
          <td style="text-align:right">{c['opportunities']}</td>
          <td style="text-align:right">{c.get('opportunity_rate', 0):.2f}%</td>
          <td style="text-align:center; font-size:12px">{sentiment_str}</td>
        </tr>"""

    totals = campaign_perf["totals"]

    return f"""
    <div class="section">
      <div class="section-header">
        <div class="section-icon active">&#9889;</div>
        <div>
          <h2>Campaign Performance</h2>
          <p class="section-subtitle">{totals['campaigns']} campaigns / {totals['total_sent']:,} sent / {totals['total_opportunities']} opportunities</p>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Campaign</th>
              <th>Status</th>
              <th style="text-align:right">Sent</th>
              <th style="text-align:right">Replied</th>
              <th style="text-align:right">Reply %</th>
              <th style="text-align:right">Opps</th>
              <th style="text-align:right">Opp %</th>
              <th style="text-align:center">Sentiment</th>
            </tr>
          </thead>
          <tbody>{rows}
          </tbody>
        </table>
      </div>
    </div>"""


def build_infrastructure_table(inbox_status):
    domains = inbox_status["domains"]

    # Group by status
    sending = [d for d in domains if d.get("status") == "sending"]
    warmup = [d for d in domains if d.get("status") == "active_warmup"]

    def domain_rows(domain_list):
        rows = ""
        for d in sorted(domain_list, key=lambda x: x["total_accounts"], reverse=True):
            util = ""
            if d.get("daily_limit_capacity", 0) > 0 and d.get("daily_send_volume", 0) > 0:
                pct = (d["daily_send_volume"] / d["daily_limit_capacity"]) * 100
                util = f"{pct:.0f}%"
            elif d.get("status") == "active_warmup":
                util = "Warmup"
            else:
                util = "--"

            warmup_score = f"{d['warmup_health_score']}" if d.get("warmup_health_score") else "--"

            rows += f"""
            <tr>
              <td class="email-cell">{d['domain']}</td>
              <td style="text-align:right">{d['total_accounts']}</td>
              <td style="text-align:right">{d.get('active', 0)}</td>
              <td style="text-align:right">{d.get('errored', 0)}</td>
              <td style="text-align:right">{d.get('daily_send_volume', 0):.1f}</td>
              <td style="text-align:right">{d.get('daily_limit_capacity', 0):,}</td>
              <td style="text-align:right">{util}</td>
              <td style="text-align:right">{warmup_score}</td>
            </tr>"""
        return rows

    sending_rows = domain_rows(sending)
    warmup_rows = domain_rows(warmup)

    totals = inbox_status["totals"]

    return f"""
    <div class="section">
      <div class="section-header">
        <div class="section-icon warning">&#9888;&#65039;</div>
        <div>
          <h2>Infrastructure Status</h2>
          <p class="section-subtitle">{totals['domains']} domains / {totals['total_accounts']} accounts / {totals.get('errored_accounts', 0)} errored</p>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Domain</th>
              <th style="text-align:right">Accounts</th>
              <th style="text-align:right">Active</th>
              <th style="text-align:right">Errored</th>
              <th style="text-align:right">Avg Daily</th>
              <th style="text-align:right">Capacity</th>
              <th style="text-align:right">Util %</th>
              <th style="text-align:right">Warmup</th>
            </tr>
          </thead>
          <tbody>
            <tr><td colspan="8" style="background: var(--gray-50); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--gray-700); padding: 8px 16px;">Sending ({len(sending)})</td></tr>
            {sending_rows}
            <tr><td colspan="8" style="background: var(--gray-50); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--gray-700); padding: 8px 16px;">Active Warmup ({len(warmup)})</td></tr>
            {warmup_rows}
          </tbody>
        </table>
      </div>
    </div>"""


def build_recommendations_section():
    return """
    <div class="section">
      <div class="section-header">
        <div class="section-icon info">&#128161;</div>
        <div>
          <h2>Recommendations</h2>
          <p class="section-subtitle">Strategic recommendations based on current data</p>
        </div>
      </div>
      <ol style="padding-left: 20px; color: var(--gray-600); line-height: 1.8; font-size: 14px;">
        {{RECOMMENDATIONS}}
      </ol>
    </div>"""


def build_benchmark_reference():
    return """
    <div class="section" style="background: var(--gray-50);">
      <div class="section-header">
        <div class="section-icon info">&#128218;</div>
        <div>
          <h2>Benchmark Reference</h2>
          <p class="section-subtitle">Cold email industry standards</p>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; font-size: 13px;">
        <div>
          <div style="font-weight: 600; color: var(--gray-700); margin-bottom: 8px;">Bounce Rate</div>
          <div style="color: var(--success);">&lt; 2% Healthy</div>
          <div style="color: #b45309;">2-5% Warning</div>
          <div style="color: var(--danger);">&gt; 5% Critical</div>
        </div>
        <div>
          <div style="font-weight: 600; color: var(--gray-700); margin-bottom: 8px;">Reply Rate</div>
          <div style="color: #b45309;">&lt; 1% Below Avg</div>
          <div style="color: var(--primary);">1-5% Average</div>
          <div style="color: var(--success);">5-10% Good</div>
        </div>
        <div>
          <div style="font-weight: 600; color: var(--gray-700); margin-bottom: 8px;">Utilization</div>
          <div style="color: #b45309;">&lt; 10% Under</div>
          <div style="color: var(--success);">20-60% Healthy</div>
          <div style="color: var(--danger);">&gt; 80% Over</div>
        </div>
      </div>
    </div>"""


def build_report(data_dir, template_path, output_path):
    # Load data
    domain_health = load_json(os.path.join(data_dir, "domain_health.json"))
    campaign_perf = load_json(os.path.join(data_dir, "campaign_performance.json"))
    inbox_status = load_json(os.path.join(data_dir, "inbox_status.json"))

    # Load template
    with open(template_path) as f:
        template = f.read()

    today = datetime.now().strftime("%Y-%m-%d")

    # Build action items
    p0, p1, p2 = build_action_items(domain_health, campaign_perf, inbox_status)

    # Build all content sections
    content = ""
    content += build_summary_cards(domain_health, inbox_status)
    content += build_executive_summary_section()
    content += build_action_items_section(p0, p1, p2)
    content += build_domain_table(domain_health)
    content += build_campaign_table(campaign_perf)
    content += build_infrastructure_table(inbox_status)
    content += build_recommendations_section()
    content += build_benchmark_reference()

    # Fill template
    html = template.replace("{{REPORT_TITLE}}", "Email Infrastructure Health Report")
    html = html.replace("{{REPORT_DATE}}", today)
    html = html.replace("{{CONTENT}}", content)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)

    # Print summary for Claude
    summary = {
        "output": output_path,
        "date": today,
        "action_items": {"p0": len(p0), "p1": len(p1), "p2": len(p2)},
        "domains_sending": len([d for d in domain_health["domains"] if d["sent"] > 0]),
        "campaigns": len(campaign_perf["campaigns"]),
        "placeholders": ["{{EXECUTIVE_SUMMARY}}", "{{RECOMMENDATIONS}}"],
    }
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Build Email Health Report HTML")
    parser.add_argument("--data-dir", default="./tmp/instantly-analytics",
                        help="Directory with JSON report files")
    parser.add_argument("--template", default=".claude/skills/generate-report/templates/base-email.html",
                        help="Path to base HTML template")
    parser.add_argument("--output", default=None,
                        help="Output HTML path (default: reports/instantly/health-report-{date}.html)")
    args = parser.parse_args()

    if args.output is None:
        today = datetime.now().strftime("%Y-%m-%d")
        args.output = f"reports/instantly/health-report-{today}.html"

    build_report(args.data_dir, args.template, args.output)


if __name__ == "__main__":
    main()
