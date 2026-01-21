# Webhook-Triggered Agents — Non-Coding Use Cases (Agent-Shaped)

Updated: 2026-01-21

This doc captures **non-coding**, **high-intent** use cases where people need:
- a long-running agent that works without a laptop/terminal open, and
- a way to trigger it from other systems (alerts, CRMs, email, forms) via **webhook/API**.

The goal is to describe **agent-shaped problems** (no fixed “workflow path”) where “best practices + investigation” is the work.

---

## Use Case 1 — Website Traffic Spike Investigator (open-ended incident investigation)

### The problem (non-coding)
“Traffic spiked—what happened, is it good, and what should we do next?”

This is rarely a deterministic flow. The right next step depends on evidence:
- campaign launch vs SEO win vs bot/referral spam vs tracking bug vs outage recovery
- which pages, sources, geos, devices, and conversion events changed

### Who is “in need”
- Growth marketer / demand gen lead (owns channels + site performance)
- Founder/PM on a small team (no analytics engineer on call)
- RevOps / marketing ops (needs reliable alerts + routing + summaries)

### Trigger surfaces (why webhook matters)
- GA4/Mixpanel anomaly alert → webhook POST
- Cloudflare/WAF alert (“request rate anomaly”, “bot score change”) → webhook POST
- Slack command (“/investigate-spike”) → webhook POST
- Scheduled check (hourly/daily) → cron/event-triggered execution

### Inputs (what the trigger payload can include)
- `time_window`: “last 60m” + baseline window (“same hour last 7 days”)
- `metric`: sessions / signups / checkout starts / revenue / 500 errors
- `filters`: domain, hostname, country, device, landing page prefix
- `context`: “we launched campaign X”, “site deploy at 14:10”, “press mention”

### What the agent does (best-practice investigation loop)
1) Pull time-series and compare to baseline (quantify delta + confidence).
2) Slice the change:
   - landing pages, referrers/UTMs, channels, geos, devices, new vs returning
3) Validate “is it real”:
   - tag health, sampling, duplicate events, sudden bounce changes
4) Classify likely cause(s):
   - paid campaign / email / influencer
   - SEO ranking change / referral spike
   - bot/referral spam / scraping / DDOS-ish traffic
   - app outage recovery or deploy regression
5) Propose next actions:
   - pause/adjust spend, update landing page, add bot mitigations,
   - post internal update, open an incident, notify stakeholders

### Outputs (what makes it valuable)
- A short “incident brief” delivered to Slack/email:
  - What changed (numbers + charts/links)
  - Where it changed (top slices)
  - Most likely explanation (ranked hypotheses + evidence)
  - Recommended next actions (with owner + urgency)
- Optional: create a ticket (Linear/Jira) and attach supporting links/artifacts.

### Guardrails (non-coding teams care about safety)
- Default to **read-only** access (analytics, logs, dashboards).
- No “auto-change spend/config” without an explicit approval step.
- Always include “unknown/needs human check” when evidence is weak.

### Why our async Claude Code agent is a strong fit
Maps directly to the #5 pain (“can’t trigger Claude agent from other systems”):
- **Deploy once** → you get a stable webhook endpoint.
- An alerting system triggers the endpoint → agent runs **async** (no laptop/terminal).
- Execution is **stateful + auditable** (inputs, outputs, logs, replay).
- It’s a true agent: can investigate, branch, gather evidence, and produce a brief.

### Where to find people asking for this (search language)
Look for posts that mention:
- “anomaly detection” + “tell me why”
- “traffic spike” + “root cause”
- “bot traffic” + “sudden surge”
- “I wish this could run automatically” / “I need a webhook” / “trigger from Slack”

