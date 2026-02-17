---
title: "Prospect Meeting: Andriy Vovchak - DataGen Agent Platform Support Session"
description: "Discovery/support call with Andriy Vovchak on DataGen agent deployment, tool call limits, and CLI tooling"
category: "research"
tags: ["prospect", "agent-deployment", "cli", "tool-limits", "pain-points"]
created: 2026-02-17
updated: 2026-02-17
status: "active"
priority: "high"
---

## Prospect Meeting: Andriy Vovchak
**Date:** 2026-02-17
**Participant:** Andriy Vovchak (Role/Company unknown - external client)
**Duration:** ~19 minutes
**Meeting Type:** Support/Discovery (live debugging session with Yusheng Kuo, DataGen)

### Prospect Profile
- **Company:** Unknown (not stated in transcript)
- **Role:** Developer/builder using DataGen platform
- **Industry:** Sales automation / outbound (referenced Clay as competitor context)
- **Company size:** Not mentioned

---

### Pain Points

#### Pain Point 1: Tool Call Limit Too Low for Production Workflows
- **Depth:** qualified
- **Surface symptom:** "I have this tool limit that is set to 60 tool calls. But I think like we can get around it."
- **Business impact:** The 60 RPM cap prevents Andriy from running the workflows he needs. DataGen confirmed another client has already hit this ceiling and requested 300 RPM. Andriy has had to seek workarounds rather than running his agent natively at scale.
- **Personal stake:** Not explicitly stated, but urgency is implied -- he raised this as the first issue in the call.
- **DataGen relevance:** Code refactor underway to raise cap to 300 RPM. Async workaround (retrieve run ID later) offered as interim solution.

#### Pain Point 2: Repository Dropdown Fails to Refresh -- Blocks Agent Connection
- **Depth:** qualified
- **Surface symptom:** "When I'm here, really, it's. It happens that I'm literally like asking for connected and I see..."
- **Business impact:** Andriy could not connect his repository via the UI because the dropdown did not refresh when no repos were found. This forced a disconnect/reconnect workaround and created confusion about agent state.
- **Personal stake:** Discovered and surfaced this bug live during an active agent setup. Yusheng acknowledged it: "Oh yeah, this is actually a bug because I think if it doesn't see anything, it doesn't get refreshed."
- **DataGen relevance:** Known bug, confirmed for fixing. Currently requires manual disconnect/reconnect workaround.

#### Pain Point 3: Secret/API Key Setup Is Confusing and Error-Prone
- **Depth:** qualified
- **Surface symptom:** Extended back-and-forth confusion about whether to paste the token name vs. the token value, where to enter it, and what naming convention is required.
- **Business impact:** Multiple misunderstandings during setup (entering Anthropic API key instead of Cloud Code OAuth token name, confusion between secret name field and secret value field). This slows onboarding and creates friction before any productive work can begin.
- **Evidence from transcript:**
  > "You couldn't put entropy's dash API key. You should put the all cloud oauth token. That's why I want you to copy the name."

  > "Oh, okay. So I take this one and I do it this way."

  > "I think it's probably another confusing part."
- **DataGen relevance:** UX clarity issue. The distinction between secret name (key) and secret value is not obvious. Yusheng noted CLI will simplify this flow.

#### Pain Point 4: Agent Modification Requires UI Visit -- No Local Dev Loop
- **Depth:** qualified
- **Surface symptom:** "But what if I want to modify this agent, for example... I need to go modify it like on my Claude code and then push it. Right."
- **Business impact:** Andriy wanted to edit agent prompts/copy locally (in Claude Code) and have changes reflected in the deployed agent without visiting the DataGen UI. The current workflow requires manual UI updates, breaking the local development flow he prefers.
- **Evidence from transcript:**
  > "Because you see like it access like all this stuff here and then... I can deploy it actually I can because I can use it within Claude code. But I think I will not able to use it within..."
- **DataGen relevance:** CLI tool shipping "tomorrow" (day after call) that enables full local workflow: sync, deploy, run -- without visiting UI. This directly addresses Andriy's request.

#### Pain Point 5: Agent Has No Reasoning When Using Custom Tools
- **Depth:** surface
- **Surface symptom:** "I tried to do it with the custom tool, which is okay. Like it works, but it's... it doesn't have any reasoning as you can know."
- **Business impact:** Andriy shifted from custom tools to agents specifically to get reasoning capability. Custom tools are deterministic but dumb -- they can't handle nuanced decisions in his workflow.
- **DataGen relevance:** Moving to agent deployment (with Claude reasoning) is the correct solution. Yusheng confirmed this direction.

---

### Latent Demand Signals

#### Signal 1: Comparing Favorably to Clay -- Implies Prior Clay Pain
- **Type:** casual-complaint / comparison
- **Evidence:** Yusheng asked: "How is this different from like a Clay like Clay gen?" Andriy replied: "It's way, way cheaper first of all. And they have like full control of everything that I want."
- **Inferred need:** Andriy has likely used or evaluated Clay and found it too expensive or too rigid. He values control over agent behavior -- suggesting he was previously constrained by Clay's opinionated workflows. DataGen's flexibility is a key reason he's building here.

#### Signal 2: Impressed Mid-Call, Suggesting Unmet Expectations Were Previously Low
- **Type:** curiosity-question / positive surprise
- **Evidence:** "And the agent is also like giving like an inside insane result by the way." + "That's incredible." (in response to CLI demo)
- **Inferred need:** Andriy came in with moderate expectations and was surprised by the capability level. This suggests he has experienced platforms that overpromised and underdelivered. His delight is a signal that the bar set by previous tools was low.

#### Signal 3: Building Wrappers Manually -- DIY Infrastructure
- **Type:** workaround
- **Evidence:** "So I built it here, like some wrappers. Let's try to close that. So I built it here..."
- **Inferred need:** Andriy has been building custom tooling/wrappers on top of the platform, suggesting the native tooling doesn't fully cover his use case yet. This is a latent demand signal for better first-party abstractions or higher-level primitives.

---

### Current Stack & Workflow

**Tools:**
- DataGen: Agent deployment and custom tool execution
- Claude Code (Claude.ai): Local development environment
- GitHub: Repository connection and version control
- Clay (referenced as competitor/prior tool)

**Manual Processes:**
- Manually navigating DataGen UI to update agent prompts (wants to eliminate this)
- Manually copying token names and values between CLI output and DataGen secrets UI

**Integration Gaps:**
- No seamless local-to-cloud development loop (CLI being shipped to fix this)
- Repository dropdown does not auto-refresh -- requires disconnect/reconnect

**Volume:** Not specified

---

### Buying Signals
- **Timeline:** Active builder, live debugging session -- very high engagement. CLI follow-up scheduled for "tomorrow."
- **Budget:** Yusheng offered free usage: "it's free for you to run this agent like other than your cloud code subscription" -- early adopter/design partner relationship implied.
- **Decision process:** Andriy appears to be the decision-maker and primary builder. No mention of other stakeholders.
- **Champion potential:** High. Andriy is enthusiastic ("That's incredible," "insane result"), providing direct feedback on bugs, and willing to test new features (CLI). Yusheng is treating him as a design partner.

---

### Summary

Andriy Vovchak is an active DataGen builder running a sales automation workflow who ran into three concrete friction points: the 60 RPM tool call cap, a UI bug blocking repository connection, and confusing secret/API key setup. His deeper need is a smooth local development loop (CLI will address this) and agent-level reasoning (vs. custom tools). He is a high-value early adopter and potential champion -- his feedback is already driving product fixes, and he was visibly excited by the platform's direction.

**Recommended next action:** Deliver CLI tool as promised, follow up to confirm Andriy successfully connected repo and ran agent locally. Document his workflow as a case study for the "Clay alternative" positioning.
