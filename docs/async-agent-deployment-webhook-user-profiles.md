# Webhook/API Trigger Pain — Real User Posts + Profiles

Updated: 2026-01-21

Goal: collect *specific* public posts where someone explicitly asks for (or builds) “trigger Claude from another system” so we can:
- profile the user,
- name the exact job-to-be-done,
- and mirror their language in our landing page/outreach.

---

## Profile 1 — “Trigger Claude Desktop remotely + send results to a webhook”

Source:
- Reddit (r/ClaudeAI): “Can I trigger Claude Desktop remotely and send results to a webhook?” (2026-01-16) — https://www.reddit.com/r/ClaudeAI/comments/1qed8zi/
- Reddit (r/webdev cross-post): same question (2026-01-16) — https://www.reddit.com/r/webdev/comments/1qed9yw/

What they want (their workflow):
- Trigger Claude **from an API/script**
- Send Claude’s response **to a webhook**
- Keep using **MCP tools**, but in an **automated** (non-manual) way

Who they likely are (hypothesis):
- Technical builder doing automation (dev / growth engineer / ops-y founder)
- Already succeeded with “interactive Claude” enough to want production automation

Very specific use case to write to:
- **Inbound event → Claude does tool-using work → webhook callback**
  - Example triggers: inbound email reply, lead form submit, CRM stage change, GitHub issue
  - Output: structured JSON summary + recommended next action + drafted response

How our async agent fits:
- We replace “Desktop + manual chat” with **deploy once → webhook URL → async runs + logs**
- Pitch line: “You already have the agent + MCP config. Now make it callable.”

---

## Profile 2 — “Expose Claude Code as an API (OpenAI-compatible gateway)”

Source:
- Reddit (r/ClaudeAI): “Claude Code API” (2025-06-23) — https://www.reddit.com/r/ClaudeAI/comments/1lipqwq/
- GitHub: `codingworkflow/claude-code-api` — https://github.com/codingworkflow/claude-code-api

What they want (their workflow):
- Turn Claude Code into an **HTTP API**
- Use it from other clients that expect **OpenAI-compatible endpoints** (Cline/Roo/Cursor/OpenWebUI)

Who they likely are (hypothesis):
- Power user / tool builder who wants “Claude Code as infrastructure”
- Already comfortable running servers, reverse proxies, Docker, etc.

Very specific use case to write to:
- “I want to call my Claude Code agent from *anything* that can do HTTP.”
  - Web app button → POST → agent runs → stream/log results → callback
  - Dev tool → call `/v1/chat/completions` → get response

How our async agent fits:
- We provide the missing “production semantics” they’re rebuilding:
  - auth, audit logs, retries/idempotency, concurrency limits, alerts, replay

---

## Profile 3 — “GitLab webhook → Claude Code runs autonomously for QA”

Source:
- Reddit (r/ClaudeCode): “I Built a $0/month Autonomous QA Agent… Using Claude Code + Self-Hosted GitLab” (2025-11-12) — https://www.reddit.com/r/ClaudeCode/comments/1oun4gp/

What they want (their workflow):
- GitLab events (MR/issue) trigger a server that runs Claude Code
- Post results back to GitLab / comment / open MR / etc.

Who they likely are (hypothesis):
- Platform/DevOps-ish engineer (or a founder) with self-hosted CI/CD
- Cares about uptime, cost control, and reproducibility

Very specific use case to write to:
- “When a merge request is opened, run a Claude agent that writes/updates tests and posts a PR comment.”

How our async agent fits:
- Same architecture but “deploy once” instead of maintaining Flask/systemd/webhook plumbing

---

## Profile 4 — “Run Claude Code behind an API on a server (multi-user, concurrent requests)”

Source:
- Reddit (r/ClaudeAI): “Possible to run Claude Code behind an API on a server for multiple users?” (2025-08-22) — https://www.reddit.com/r/ClaudeAI/comments/1mx6vgx/

What they want (their workflow):
- Put Claude Code “behind an API” so their app can call it for **task-based** work
- Avoid pay-per-call API costs by using a **subscription** model
- Handle **multiple concurrent requests**
- Return “success/failure” instead of streaming a full chat transcript

Who they likely are (hypothesis):
- Founder/solo dev shipping an app with “AI features”
- Already has a backend (mentions “my API”) and is thinking in request/response semantics

Very specific use case to write to:
- “User clicks a button in my product → my backend POSTs to an agent endpoint → agent edits/generates code/scripts → my backend returns a simplified result.”

How our async agent fits:
- This is exactly “deploy once → webhook URL → async execution” but with production needs:
  - concurrency controls, isolation per request, logs, retries/idempotency, and replay

---

## Profile 5 — “I want Claude Desktop features + API access”

Source:
- Reddit (r/ClaudeAI): “I want the Claude Desktop GUI + API access = HOW?” (2025-01-09) — https://www.reddit.com/r/ClaudeAI/comments/1hxchl7/

What they want (their workflow):
- Keep the Desktop experience (MCP + Projects + Google Doc sync) but also:
- “Connect everything to the API” so it can be automated / integrated

Who they likely are (hypothesis):
- Power user who built real workflows inside Desktop (already using MCP + Projects)
- Now wants the same capability in a programmable surface area (API/webhooks)

Very specific use case to write to:
- “My CRM/email/helpdesk triggers an agent, but I still want it to use my Desktop project context and tools.”

How our async agent fits:
- “Your Desktop workflows become callable endpoints (webhook/API) with audit logs + safe tool access.”

---

## Profile 6 — “I built a self-hosted webhook that launches Claude Code (GitHub bot)”

Source:
- Reddit (r/ClaudeAI): “I built a self-hosted webhook service that launches Claude Code in YOLO mode…” (2025-06-03) — https://www.reddit.com/r/ClaudeAI/comments/1l2m2go/
- GitHub: `claude-did-this/claude-hub` — https://github.com/claude-did-this/claude-hub

What they want (their workflow):
- GitHub mention triggers a webhook
- Claude Code runs inside isolated containers with repo access and “does the work”

Who they likely are (hypothesis):
- Extremely high-intent builder who already proved the model
- Now paying the infra/ops tax (containers, auth, logs, security boundaries)

Very specific use case to write to:
- “@agent in PR/issue → agent runs long-horizon fixes/reviews and posts back automatically.”

How our async agent fits:
- They’re literally building “async agent deployment” by hand. Our pitch:
  - “Stop maintaining the webhook runner. Deploy your agent and get a webhook in minutes.”

---

## Profile 7 — “Run Claude Code headless without API costs (and call it from other systems)”

Source:
- LinkedIn: “Today I learned how to run Claude Code headless without API costs…” (2025-11-13) — https://www.linkedin.com/posts/dmcaulay_today-i-learned-how-to-run-claude-code-headless-activity-7394989951257333761-5FLQ

What they want (their workflow):
- Run Claude Code programmatically/headless (often to automate)
- Avoid pay-per-call costs; prefer subscription/token flows

Very specific use case to write to:
- “I want an always-on agent runner (CI/server) that’s triggered via HTTP/webhooks and uses my Claude Code setup.”

How our async agent fits:
- “Headless is step 1. Deployment + triggers + observability is step 2 (us).”

---

## ICP tags these profiles imply

- “Wants Claude in automation, not chat”
- “Already using MCP tools”
- “Building wrappers (gateway/bot/CI integration) = highest intent”
