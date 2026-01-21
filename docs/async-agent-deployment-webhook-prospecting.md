# Webhook-Triggered Claude Agents — Prospecting Playbook

Updated: 2026-01-21

This doc focuses on one high-intent pain:

> “I want to trigger Claude Code/Claude from another system (webhook/API), not from my laptop.”

---

## What people are trying to do

Common requests:
- Trigger a Claude workflow from **GitHub / Slack / CRM / email / forms**
- Provide inputs as JSON payloads and get **structured outputs**
- Run “headless” (no interactive session) and be able to **retry**, **resume**, and **audit**

Typical DIY workarounds we see:
- GitHub Actions wrappers
- OpenAI-compatible API gateways that proxy to Claude Code
- Discord/Telegram/email “remote control” UIs
- tmux + VPS “always on” setups

---

## Where our async deployment fits (and why it’s compelling)

### The core fit
- **Deploy once** → get a **webhook URL**
- Any external system hits the webhook → the agent runs **async** (24/7)
- Agent has “full context”: files + MCP servers + codebase

### Feature mapping (what to emphasize)
- “Trigger from anywhere” → webhook endpoint with auth + signed requests
- “It must not block” → async execution + queueing + concurrency limits
- “It must be safe” → least-privilege tool access + audit logs + approvals for risky actions
- “It must be debuggable” → run logs, inputs/outputs, trace IDs, and replay
- “It must be reliable” → retries, idempotency keys, timeouts, and dead-letter handling

---

## High-intent pools to mine (people likely to buy)

1) **Builders of “Claude Code as an API”**
- Anyone who built/uses an API gateway around Claude Code
- Strong signal: they want programmatic triggering and integration into other systems

2) **GitHub Actions users automating Claude**
- People wiring Claude to PR/issue/comment events
- Strong signal: they want event-driven execution and reproducibility

3) **Remote-control bot users**
- Discord/Telegram/email-based controllers for Claude Code sessions
- Strong signal: “I want it to run when I’m not at my computer”

4) **Ops-minded devs**
- People discussing queues, retries, idempotency, observability for agent workflows
- Strong signal: they’re past “toy” automation and want production semantics

---

## Keywords that correlate with this pain

Use these exact phrases for search + outreach relevance:
- “Claude Code API”
- “trigger Claude Desktop remotely”
- “Claude Code webhook”
- “headless Claude Code”
- “run Claude Code in GitHub Actions”
- “OpenAI-compatible gateway for Claude”
- “Discord bot that runs Claude Code”

---

## Lead enrichment fields (what to capture)

Person:
- Title: growth engineer / GTM engineer / developer advocate / platform engineer / founder
- Evidence they build automation: repos, posts, “I built X” threads

Company/workflow:
- Primary trigger system: GitHub, Slack, HubSpot/Salesforce, forms, email
- Execution requirements: schedule vs event-driven, expected run volume/day
- Reliability needs: retries, audit trails, approvals, failure notifications

Buying signal:
- They already attempted a workaround (actions/gateway/bot/tmux)
- They’re asking “how do I do this safely/reliably?” not “is this possible?”

---

## Qualification questions (fast)

Ask these in the first conversation:
1) “What system should trigger the agent?” (GitHub/Slack/CRM/email/form)
2) “How many triggers per day?” (volume + burstiness)
3) “Where should the result go?” (Slack, CRM note, email reply, PR comment)
4) “What happens when it fails at 3am?” (ownership + alerting + replay)

If they answer crisply, they’re very likely in the sweet spot.

---

## Source map (starting points)

See `docs/async-agent-deployment-complaint-sources.md` section **5** for a curated set of threads and repos to pull prospects from.

