# Async Agent Deployment — Complaint/Signal Sources

Updated: 2026-01-21

This doc collects public threads/projects where people describe pains that map cleanly to:

- Current state: Claude Code / Claude Desktop are often **interactive + local**
- Our solution: **deploy once**, trigger via **webhook/cron/events**, run **async** (24/7) with logs/state

---

## 1) “I have to keep my laptop/terminal open”

Signals:
- Fear of closing the window mid-run
- Running inside `tmux` / remote boxes just to keep sessions alive
- Long-running sessions break over time (temp files, auth, etc.)

Sources:
- Reddit: “Claude Code Fear” (closing the window kills the session) — https://www.reddit.com/r/ClaudeAI/comments/1ldvb7c/
- Reddit: “[BUG REPORT] Shell snapshot file deletion issue in long-running sessions” (running for days, breaks when macOS cleans temp files) — https://www.reddit.com/r/ClaudeAI/comments/1lnk57d/
- Reddit: “How I run dev servers in claude code without blocking the chat” (background processes via `tmux`) — https://www.reddit.com/r/ClaudeAI/comments/1l9f0jm/
- Reddit: “Claude Code on the go” (remote/tmux workflows so Claude keeps running) — https://www.reddit.com/r/ClaudeAI/comments/1lmd084/

---

## 2) “It works but I can’t schedule it”

Signals:
- Manual CLI trigger every time
- People building wrappers around cron/launchd just to run tasks overnight

Sources:
- Reddit: “A scheduler for Claude Code - runCLAUDErun” (explicitly: “didn't want to keep running the command manually every night”) — https://www.reddit.com/r/ClaudeAI/comments/1nwpgmi/
- Website: runCLAUDErun (macOS scheduler app) — https://runclauderun.com/

---

## 3) “I built something great but can’t share it (or keep it in sync)”

Signals:
- Claude config/skills live in `~/.claude/…` or scattered across projects
- Pain syncing CLAUDE.md / skills / settings across machines or worktrees
- “GitHub hunt” for skills and no good install/sync story

Sources:
- Reddit: “Are you keeping your Claude dotfiles in the repo?” (separate repo + symlinks to propagate config across worktrees) — https://www.reddit.com/r/ClaudeAI/comments/1p70y95/
- Reddit: “Remember the Skillhub… turning feedback into a desktop” (skill discovery + sync focus) — https://www.reddit.com/r/ClaudeAI/comments/1qhxsar/
- Reddit: “TIL Claude, Cursor, VS Code Copilot, and Codex all share the same ‘Skills’ format now” (skills portability discussion) — https://www.reddit.com/r/ClaudeAI/comments/1pqqful/

---

## 4) “My workflow breaks when I close the terminal” (persistence/session management)

Signals:
- People inventing session managers, tmux dashboards, remote UIs
- Indicates demand for “runs without me” + state/resume + observability

Sources:
- Reddit: “I got tired of managing 15 terminal tabs for my Claude sessions…” (multi-session management via tmux) — https://www.reddit.com/r/ClaudeCode/comments/1pxyn37/
- Reddit: “I built CCManager - A tmux-free way to manage multiple Claude Code sessions” — https://www.reddit.com/r/ClaudeAI/comments/1l80jd4/
- Reddit: “Claude code session management” (save/retrieve sessions; resume pain) — https://www.reddit.com/r/ClaudeCode/comments/1ng7zqg/

---

## 5) “I can’t trigger a Claude agent from other systems (webhook/API)”

Signals:
- People asking for “trigger from API/script” + “send result to webhook”
- Workarounds: Discord/Telegram/email UIs, GitHub webhooks, custom daemons

Sources:
- Reddit: “Can I trigger Claude Desktop remotely and send results to a webhook?” — https://www.reddit.com/r/ClaudeAI/comments/1qed8zi/
- Reddit (cross-post): “Can I trigger Claude Desktop remotely and send results to a webhook?” — https://www.reddit.com/r/webdev/comments/1qed9yw/
- GitHub: `claude-hub` (GitHub webhook service that runs Claude Code in containers) — https://github.com/claude-did-this/claude-hub
- Reddit: “Built a Discord bot that runs Claude Code sessions…” (remote control via phone) — https://www.reddit.com/r/ClaudeAI/comments/1lcf0v3/
- GitHub: `Claude-Code-Remote` (remote control via email/Discord/Telegram; tmux injection + webhooks) — https://github.com/JessyTsui/Claude-Code-Remote
- Reddit: “Claude Code API: OpenAI-compatible gateway…” (explicitly: “call it as API endpoint”; automation framing) — https://www.reddit.com/r/ClaudeAI/comments/1ef9ljb/
- GitHub: `claude-code-api` (OpenAI-compatible API gateway over Claude Code) — https://github.com/kscalelabs/claude-code-api
- Anthropic docs: “Claude Code GitHub Actions” (run on PR/issue/comment events) — https://docs.anthropic.com/en/docs/claude-code/github-actions
- Anthropic docs: “Claude Code SDK” (programmatic/headless usage patterns) — https://docs.anthropic.com/en/docs/claude-code/sdk
- Anthropic docs: “Claude Code Slack integration” (trigger flows via Slack + approvals) — https://docs.anthropic.com/en/docs/claude-code/slack
- Anthropic Agent SDK docs: “Deploy and manage agents” (hosting, endpoints, ops) — https://docs.anthropic.com/en/docs/agents/overview
- Claude Control (community tool): “One-click Claude Code … via Webhook URL” — https://claudecontrol.com/

---

## Search queries to find more (copy/paste)

- `site:reddit.com Claude Code keep terminal open`
- `site:reddit.com Claude Code tmux session`
- `site:reddit.com Claude Code schedule cron launchd`
- `site:reddit.com Claude Desktop trigger webhook`
- `site:reddit.com Claude Code API endpoint`
- `site:reddit.com Claude Code webhook`
- `site:news.ycombinator.com Claude Code webhook`
- `site:github.com claude-code-api`
- `site:github.com claude-hub claude`
- `site:reddit.com Claude Code skills sync repo symlink`
- `site:github.com Claude Code webhook`
