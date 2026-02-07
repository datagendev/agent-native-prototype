## Work Meeting Summary: Codex Agent UI/UX Review
**Date:** February 5, 2026
**Participants:** Yusheng Kuo, Jeremy Ross
**Duration:** 73 minutes

### Key Discussion Points
- Reviewed the DataGen agent deployment interface and identified UX improvements needed
- Discussed confusion around entry prompts, payload variables, and webhook vs schedule execution
- Explored OAuth token setup flow and documentation needs
- Discussed product strategy: platform neutrality (supporting skills beyond Claude Code), infrastructure layer positioning, and competitive moat concerns
- Compared Claude Code vs Codex performance and UI patterns
- Reviewed notification system and email formatting options

### TODO Items
| Owner | Task | Priority | Context |
|-------|------|----------|---------|
| Yusheng | Improve "Entry Prompt" labeling with better description (e.g., "this is what will be said to the agent to initiate the call") | High | Users confused about what entry prompt means |
| Yusheng | Rename "Webhook Settings" section to "Configure Secret" or similar - semantically incorrect currently | High | Current naming doesn't match what it does |
| Yusheng | Add hyperlinks to documentation for getting Anthropic API key and Claude Code OAuth token | High | Users need guidance on token setup |
| Yusheng | Add description: "Insert any API keys for tools you want" with note that "at minimum you need Anthropic or Claude Code token" | High | Unclear what secrets are required |
| Yusheng | Change "Create PR" wording to "Write results back to GitHub" with explanation of what pull request means | Medium | Don't assume users know PR terminology |
| Yusheng | Add instructions/screenshots showing `claude setup-token` command flow | High | Token setup is confusing - needs visual guide with note it must be run outside Claude |
| Yusheng | Change "Run Now" button to "Test Run" to avoid confusion with schedule activation | High | Users think "Run Now" triggers the schedule |
| Yusheng | Add validation/error for curly bracket variables - only allow "payload" variable name, show warning if other variables used | Medium | Users confused about variable naming |
| Yusheng | Simplify payload input UI when no payload variable in entry prompt | Medium | Edge case causing confusion when schedule jobs don't need payload |
| Yusheng | Add dropdown for GitHub write permissions: "Never write", "Pull request only", "Auto merge" | Medium | Different use cases need different write behaviors |
| Yusheng | Make branch/PR links optional in notification emails | Medium | Reps don't need GitHub links, only ops teams do |
| Yusheng | Consider building agent creation playground UI in DataGen (vibe coding agents in chat, push to repo) | Low | Future feature - would reduce need for Claude Code for agent creation |
| Jeremy | Schedule meetings with GTM engineers (demand automation freelancer + Avocado agency) for brainstorming session | Medium | Both interested in Clay + Claude Code integration |
| Jeremy | Test agent deployment flow and report any failures | High | First-time user testing to catch issues |

### Decisions Made
- Default to "dangerously skip" permissions for deployed agents (tools execute without approval) since deployment implies trust
- Keep payload variable naming as-is for now but add validation
- Notification emails will render simple markdown (not fancy React)
- Continue focus on Claude Code but plan for platform neutrality (support skills across Cursor, Codex, Gemini)
- Position DataGen as agent infrastructure layer (deployment, tooling, MCP registry, resources, deterministic custom tools)
