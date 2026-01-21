# Founder “Signal Triage” Agent (Webhook + Claude Code)

Updated: 2026-01-21

This use case is inspired by the “Personal OS for founders” concept: a lightweight file-based system with daily/weekly/quarterly/annual reflection templates.across too many inputs (CRM, Slack, email, calendar, analytics, finances, hiring, customers).

This agent turns “incoming chaos” into a small set of **prioritized, explainable** actions and updates your Personal OS files automatically.

---

## The job-to-be-done

“I want an agent that watches everything happening around me and surfaces what’s important, without me constantly checking 12 tools.”

Key constraint: founders don’t want a new UI.
- They want a **daily brief**, **alerts when it’s urgent**, and **automatic updates** to their existing artifacts (markdown, Notion, tickets, CRM notes).

---

## What “important” means (a founder-readable rule)

Important = anything that is:
- time-sensitive (deadline, meeting, escalation, renewal window),
- revenue-impacting (deal risk, pipeline movement, churn risk, high-intent visitor),
- customer-critical (VIP complaint, outage, security, broken onboarding),
- team-blocking (approval needed, decision stuck, hiring stall),
- goal-aligned (moves the quarter’s top objective),
- pattern-revealing (same issue appearing repeatedly).

The agent’s job is not to be perfect — it’s to reduce scanning and prevent misses.

---

## Triggers (why webhook deployment matters)

The agent runs **async**, triggered by events or schedules:

Business signals:
- CRM event: new inbound lead, stage change, deal stale, “no next step”
- Email event: VIP reply, urgent keyword, invoice, renewal notice
- Calendar event: meeting ended → transcript ready
- Support event: new P1 ticket, spike in complaints
- Analytics event: traffic/conversion anomaly, pricing page spike
- Finance event: large expense, failed payment, cash threshold crossed

Personal OS cadence:
- daily at 7am: “today brief”
- weekly: “what moved the needle vs noise”
- quarterly: “alignment check + course correction”

---

## Inputs (the webhook payloads)

Normalize every event into a single “signal” shape:
- `source`: gmail | slack | hubspot | salesforce | ga4 | stripe | zendesk | gong
- `type`: lead | deal_risk | vip_email | meeting | outage | anomaly | payment
- `timestamp`
- `summary`
- `entities`: company, person, deal_id, ticket_id, campaign, page_url
- `raw_link`: deep link back to the system of record

Store each signal as a file (so the agent has durable context):
- `signals/2026-01-21T13-55-00Z_hubspot_deal_stale.md`

---

## What the agent does (high-level loop)

1) Ingest: write the new signal file (or append to today’s log).
2) Classify: map to a domain (career/relationships/health/meaning/finances/fun) + business domain (GTM/product/ops/people).
3) Score importance (explainable):
   - urgency (0–5), impact (0–5), confidence (0–5), reversibility (0–5), effort (0–5)
4) Decide routing:
   - alert now (P0/P1) vs include in daily brief vs “noise/archive”
5) Produce outputs:
   - **daily brief** (top 3–5 focus items + why)
   - draft responses (email/Slack) where safe
   - create/update tasks (Linear/Jira/Trello) when needed
   - update Personal OS templates with facts + prompts for reflection

---

## Outputs (what the founder gets)

### A) Daily “Founder Brief” (markdown + Slack/email)
Contains:
- Today’s top priorities (3–5), each with:
  - why it’s important (impact/urgency),
  - what to do next (one concrete action),
  - link to source of truth.

### B) “Don’t miss this” alerts (only when warranted)
- Example: “VIP customer unhappy + renewal in 14 days”
- Example: “Conversion rate dropped 40% vs baseline”

### C) Personal OS updates
Instead of asking the founder to remember everything:
- append the day’s key signals to `daily/2026-01-21.md`
- generate “one win / one friction / one priority” suggestions
- queue questions the founder should answer (to keep the OS reflective, not robotic)

---

## Guardrails (so it doesn’t become spammy or scary)

- Default to **read + draft**, not “auto-send”.
- Require explicit approval for:
  - sending emails/messages,
  - changing spend/campaign settings,
  - editing CRM stages/amounts,
  - making irreversible actions.
- Always include “why this was ranked important” (auditability).
- Maintain a strict “alert budget” (e.g., max 2/day unless P0).

---

## Why this is a strong fit for “async webhook + Claude Code”

This is exactly the “many moving pieces” problem:
- the agent only works if it runs while the founder is not watching,
- it must be triggerable from other systems,
- it must maintain state across many small events,
- and it must write outputs back to the tools where work happens.

Deploy once → webhook endpoint(s) → async runs with logs/state/replay.

