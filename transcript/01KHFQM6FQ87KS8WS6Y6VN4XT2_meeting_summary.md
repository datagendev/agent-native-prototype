---
title: "Prospect Meeting: Chehan Karunaratne - X Growth ABM Agency"
description: "Discovery/demo call with Chehan Karunaratne from X Growth ABM agency"
category: "research"
tags: ["prospect", "abm", "agency", "claude-code", "datagen"]
created: 2026-02-18
updated: 2026-02-18
status: "active"
priority: "medium"
---

## Prospect Meeting: Chehan Karunaratne / X Growth
**Date:** 2026-02-17
**Participant:** Chehan Karunaratne, GTM Engineer, X Growth (ABM Agency)
**Duration:** ~70 minutes
**Meeting Type:** Demo / Discovery

### Prospect Profile
- **Company:** X Growth
- **Role:** GTM Engineer (recently landed via Clay skills)
- **Industry:** Account-Based Marketing (ABM) agency
- **Company size:** Not stated; offices in Melbourne and Singapore
- **Context:** 23 years old, new to Claude Code, came from sales roles, discovered Clay 6-7 months ago, landed GTM role after 4 months

---

### Pain Points

#### Pain Point 1: Token / Usage Limit Constraint on Claude $20 Plan
- **Depth:** qualified
- **Surface symptom:** "I have the $20. Yeah, $20."
- **Business impact:** "The 20 limit is, you know, it runs out really quickly... I don't want to overwhelm it."
- **Personal stake:** "I don't want to overwhelm the cloud like fast." Chehan repeatedly returned to this concern — he is worried that running deployed agents will exhaust his personal Claude subscription before he can build and validate an ABM signal engine.
- **DataGen relevance:** DataGen allows Claude Code OAuth token auth so the $20 subscription covers agent runs, or alternatively lets prospects evaluate using DataGen's own token budget before committing to a higher tier or company plan.
- **Evidence from transcript:**
  > "So there is a certain limit that we can use cloud code for the week. Right. So that is the pro package that I have... So with that when the agent is running, is that going to like take the tokens or anything?"

  > "So I have the $20. Yeah, $20... So I can find on YouTube, right. To figure this out."

  > "So basically what I want to do is like use your API without you know like overwhelming my Claude account, you know like. Yeah, so that I'm able to use it longer because the 20 limit is, you know, it runs out really quickly."

---

#### Pain Point 2: No Scalable ABM Signal Engine Yet
- **Depth:** qualified
- **Surface symptom:** "I'm trying to build something of a signal engine."
- **Business impact:** The signal engine is described as "very important for our whole company and what we do." Without it, Chehan (and X Growth) rely on manual account research with no automated monitoring or triggering.
- **Personal stake:** Chehan said building this is his current primary skill development focus. He is trying to prove this to management. "I see if I like with the free credits and all, if I show it okay this way works properly then you know I can talk to the management and I can get this for the company basically."
- **DataGen relevance:** DataGen's deployed agent platform (webhook triggers, scheduled runs, email notifications) is exactly the infrastructure needed to turn a one-time Claude Code session into a persistent, real-time ABM signal engine.
- **Evidence from transcript:**
  > "I'm trying to build something of a signal engine. So that's through Claude. Because that is very important for our whole company and what we do. So like if I put in an account name, you know, it should just go out and find the relevant signal. So that's basically what I'm trying to build."

---

#### Pain Point 3: Clay is Rigid and Expensive for Complex Research
- **Depth:** surface (shared by Yusheng, validated by Chehan)
- **Surface symptom:** Clay's column-by-column, if/else workflow structure is limiting for sophisticated account research.
- **Business impact:** "One of my friends had nine different tables in Clay because you have to handle all these different if/else condition like a logic." This suggests high build and maintenance overhead as signal complexity grows.
- **Personal stake:** Chehan is actively working with Clay and is evaluating Claude Code/DataGen as a more capable alternative for his agency's ABM work.
- **DataGen relevance:** Claude Code agents can encode domain knowledge and adapt to missing data gracefully — no rigid column mapping needed, unlike Clay.
- **Evidence from transcript:**
  > "I work with clay and you know, a couple of other tools that I integrating with clay and you know like that. But not nothing too complex, but I'm trying to build something of a signal engine."

  > (Yusheng, validated by Chehan) "It's much cheaper actually compared to Clay. Yeah. Because Clay is like you use those APIs and it's a very... most of clay because when he do research it's like a very... It's like each column is a context and then you just summarize the context like the column."

---

### Latent Demand Signals

#### Signal 1: Manually Researching Accounts Without Automation
- **Type:** normalized-pain
- **Evidence:** "So let's say the companies that Shopify is going after expanding into the Australian region... or they are hiring a new marketing manager in APAC... So let's do that first."
- **Inferred need:** Chehan is currently doing this account research manually or using Clay in a limited, manual-trigger fashion. He has not yet built any automated monitoring. The signal engine he wants to build is the solution to a manual research process he hasn't explicitly called a pain point.

#### Signal 2: No MCP Experience
- **Type:** curiosity-question / capability gap
- **Evidence:** "No, not MCP." (when asked if he has used MCP with Claude Code)
- **Inferred need:** Chehan's agent capabilities are limited to basic Claude Code without tool integrations. He is at early stage of building the stack. DataGen's MCP server management and pre-built integrations (LinkedIn, Perplexity/Parallel search, etc.) could dramatically accelerate his setup.

#### Signal 3: No Slash Agent / Agent Creation Experience
- **Type:** capability gap
- **Evidence:** "This I haven't used, no." (when shown /agent command in Claude Code)
- **Inferred need:** Chehan is writing code-centric Claude Code sessions rather than agent-native architectures. He lacks the conceptual framework to build persistent, structured agents. This is a readiness gap DataGen's onboarding and documentation addresses.

#### Signal 4: Concern About Token Cost at Scale
- **Type:** casual-complaint / normalized worry
- **Evidence:** "Because so as we are iterating and you know, as we are prompting it... it's going to learn, right? And at the end it will come to a proper standard."
- **Inferred need:** Chehan expects the iteration process to be expensive and potentially unsustainable at his current plan level. He is willing to pay, but needs a clear cost model before committing.

---

### Current Stack & Workflow

**Tools:**
- Clay: Primary enrichment and outreach workflow tool
- Claude Code (VS Code): Recently started using for ABM agent building
- Signal Base: Mentioned as a tool they use for finding signals
- Shopify, Twilio, Zoom: Current agency clients

**Manual Processes:**
- Account research for target accounts (Shopify, Twilio, Zoom) — currently manual, Chehan is trying to automate this
- Signal identification (hiring, expansion, news) — no automated process yet

**Integration Gaps:**
- No MCP integrations configured yet
- No deployed agents — everything is session-based Claude Code
- No webhook or scheduled triggers for continuous monitoring

**Volume:** Not explicitly stated; X Growth is an ABM agency focused on a small number of large, named accounts (Shopify, Twilio, Zoom as examples)

---

### Buying Signals
- **Timeline:** No hard deadline stated. Chehan wants to build the agent first, then show management. "If I show it okay this way works properly then you know I can talk to the management."
- **Budget:** On personal $20/month Claude plan. Open to DataGen free credits as evaluation. Would need company buy-in for paid deployment.
- **Decision process:** Individual bottom-up — Chehan builds it, proves it, then pitches to management at X Growth.
- **Champion potential:** High. Chehan is motivated, technically curious, and at an agency where this could become a repeatable service. He explicitly said he would contact Yusheng when the agent is ready and is open to DataGen managing the deployment.

---

### Summary

Chehan is a junior GTM engineer at an ABM agency (X Growth, Melbourne/Singapore) trying to build an automated ABM signal engine using Claude Code. His primary friction points are the usage limits of his personal $20 Claude plan and the lack of experience with agent deployment and MCP tooling. He is a motivated early-stage champion who needs hand-holding through the DataGen setup but has clear internal use case (account signal monitoring for clients like Shopify, Twilio, Zoom) and a path to company adoption if he can demonstrate value first. Recommended next action: send GitHub repo + skill documentation as promised, offer free DataGen credits, and check in when he has an agent draft ready.
