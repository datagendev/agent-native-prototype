---
title: "Catch up with William - AI Agent Economy Discussion"
description: "External catch-up with William Lee (AIPola) on agent marketplace strategy and AI economy dynamics"
category: "research"
tags: ["agent-economy", "marketplace", "strategy", "ai", "gtm"]
created: 2026-03-04
updated: 2026-03-04
status: "active"
priority: "high"
---

## Prospect Meeting: William Lee (AIPola)
**Date:** 2026-03-04
**Participant:** William Lee, Co-founder, AIPola (will@aipolabs.xyz)
**Internal:** Yusheng Kuo (yusheng.kuo@datagen.dev)
**Duration:** ~33 minutes
**Meeting Type:** Strategic catch-up / peer discussion

### Prospect Profile
- **Company:** AIPola (aipolabs.xyz)
- **Role:** Co-founder / AI agent builder
- **Industry:** AI infrastructure / agent development services
- **Company size:** Early-stage startup

---

### Pain Points

#### Pain Point 1: Agent Marketplace Cold Start Problem
- **Depth:** qualified
- **Surface symptom:** "The key problem when it comes to distribution is still can you find the first use case where people are just willing to come to this marketplace for."
- **Business impact:** "In order for people to come to your marketplace and build this and for people to come and use it... you need to have good sellers that actually offer services that matter... And then naturally then you find a way to then incentivize buyers to come and actually buy."
- **Personal stake:** William has direct firsthand experience trying to build in the RevOps/GTM space and pivoting after two months: "We actually looked into the revenue operations and go to market space for the last like two months before, like pivoting."
- **DataGen relevance:** DataGen's agent deployment to client Slack channels and webhook triggers is an early wedge into this problem. The question is whether the initial use cases (GTM agents) are compelling enough to seed the marketplace.

#### Pain Point 2: Thin Value Layer in Custom-Built Agent Tooling
- **Depth:** qualified
- **Surface symptom:** "The value there is like so thin that like it's very hard for anyone to persistently make money by offering that alone as a product."
- **Business impact:** "Any version that you can create using natural language and that can be built in house is going to be worse than off the shelf vendor solution." William cited the example of a Claude Code + Granola MCP + Fireflies API sales coaching tool vs. Gong - the custom version is technically possible but commercially fragile.
- **Personal stake:** William's company AIPola charges 30k-50k/month for bespoke agent work precisely because generic tooling can't handle complex cases: "The reason why people would pay us like 30k, like 50k a month to like build something is because like the stuff they're building is actually not automatable by these like very like low ceiling like agents."
- **DataGen relevance:** DataGen's platform play relies on agents being valuable enough to sustain a marketplace. William's point is that commodity agents (meeting summary, basic outreach) won't support this.

#### Pain Point 3: Platform Risk from Foundation Model Providers
- **Depth:** qualified
- **Surface symptom:** "Every day it's like Telco can just ship one more feature and then just kill everyone. Especially we are doing the tool."
- **Business impact:** William described a firsthand case: "I have friends whose startups were doing very well over the last 6 months. They went from 0 to 600k ARR or whatever. The moment that announcement came out, they're dead, literally their customers... the consultancy just came back to them as like, hey, we're not sure we should buy your product because we can just use Claw for this now."
- **Personal stake:** AIPola is explicitly building in the space where automation is difficult (computer use, legacy plugins, no-API environments) to avoid this risk: "That pocket is kind of like where remaining value is if I'll be very honest."
- **DataGen relevance:** DataGen's position as a tool/platform layer faces the same risk. William's advice: don't worry about it now, make money fast before incumbents catch up.

#### Pain Point 4: Difficulty Unbundling Professional Services for Agent Monetization
- **Depth:** surface
- **Surface symptom:** "The biggest challenge here is like in finding businesses that actually want to unbundle because like from my own experience, I know like quite a lot of businesses... they would not want to unbundle."
- **Business impact:** Using legal as an example: "A lawyer, it's like their billable time is like, I know like some senior lawyers I've worked with like per hour they charge like over like 3k or 5k... if they're signing off on a hundred dollar like legal letter, it takes them five minutes to read it... And now they're on the hook for legal consequences for that. It's actually not even worth their time."
- **DataGen relevance:** DataGen's marketplace thesis depends on service providers being willing to expose modular agent-backed services. William identifies supply-side resistance as the key friction point.

---

### Latent Demand Signals

#### Signal 1: AIPola Is Building Bespoke Agents for Revenue
- **Type:** workaround / normalized-pain
- **Evidence:** "The one we're doing this month right now is like a computer use agent for, for like a legacy like PowerPoint like plugin. You can't automate that using claw code or open claw. Because there's no API to call. And you have to think through like a lot of ways to hack."
- **Inferred need:** AIPola's current revenue model (bespoke, high-touch, $30-50k/month engagements) is inherently unscalable. William hasn't framed this as a problem, but it implies latent demand for tooling that would let them package and resell agent workflows without rebuilding from scratch each time - which is exactly what DataGen's deployment/marketplace layer could offer.

#### Signal 2: Curiosity About Agent Mail Traction
- **Type:** curiosity-question
- **Evidence:** "Is agent mail doing well?" followed by "I really like these guys."
- **Inferred need:** William is actively tracking agent-to-agent communication infrastructure. This suggests AIPola is evaluating whether to build in this layer or partner with players who do - potential collaboration signal.

#### Signal 3: Concern About Circular Agent Economy
- **Type:** casual-complaint framed as philosophical debate
- **Evidence:** "The biggest problem with like the Asian economy right now is like kind of only like humans need things from agents. Agents don't need things from humans. I think that's the biggest asymmetry."
- **Inferred need:** William is wrestling with a fundamental business model question about where durable value accrues in an agent economy. This isn't just philosophy - it signals uncertainty about AIPola's long-term positioning and openness to exploring new models (like DataGen's marketplace) that could create more sustainable value capture.

---

### Current Stack & Workflow

**Tools mentioned by William:**
- Claude Code: Used/evaluated as agent harness
- Gong: Referenced as the expensive incumbent ($60k/year entry) that custom-built sales coaching tools compete against
- Clay: Referenced as a GTM automation tool in competitive landscape
- Adio, Instantly AI, Salesloft-type tools: Mentioned as existing market players in outreach automation

**AIPola's current approach:**
- High-touch bespoke agent builds at $30-50k/month
- Focus on computer use / legacy system automation where APIs don't exist
- Building for cases that Claude Code and off-the-shelf agents cannot handle

**Integration Gaps identified:**
- No clear scalable path from bespoke builds to productized agents
- OAuth/credential management cited by Yusheng as a pain DataGen solves: "Otherwise to deploy the agent with all this oauth potential management is a pain act for even one agent."

**Volume:** Not specified for AIPola's client engagements.

---

### Buying Signals
- **Timeline:** No explicit urgency or buying timeline stated. Exploratory peer discussion.
- **Budget:** Not discussed. AIPola earns revenue ($30-50k/month engagements) but is not evaluating DataGen as a purchase.
- **Decision process:** William is a co-founder/decision maker. Any collaboration or partnership would be co-founder level.
- **Champion potential:** Moderate. William is intellectually aligned with DataGen's marketplace thesis and sees the vision. He's skeptical of execution risk (cold start, thin margins) but not dismissive. Key quote: "I think it's doable. Yeah." He also explicitly encouraged focusing on GTM/marketing workflows as the first wedge.

---

### Summary

William Lee (AIPola co-founder) shares DataGen's long-term marketplace vision but is skeptical about near-term execution - specifically the cold start problem (getting both buyers and sellers onto the platform simultaneously) and the thin commercial value of commodity AI agents. His core advice: pick one verticalized marketing/GTM workflow where DataGen can demonstrate clear ROI, use that to seed the marketplace, and don't worry about platform risk from incumbents until you've captured enough value. The meeting is a peer strategic discussion, not a sales opportunity, but William is a credible validator and potential future partner given AIPola's bespoke agent work.
