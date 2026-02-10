---
title: "Prospect Meeting: Lohit Boruah - Cloud Code Agent Automation"
description: "Discovery call with agency builder exploring agent automation and Clay alternatives"
category: "prospect"
tags: ["discovery", "automation", "agent-automation", "clay-alternative"]
created: 2026-02-10
updated: 2026-02-10
status: "active"
priority: "high"
---

## Prospect Meeting: Lohit Boruah
**Date:** 2026-02-10
**Participant:** Lohit Boruah, lohitofficial1@gmail.com (Agency/Automation Builder)
**Duration:** 34 minutes
**Meeting Type:** Discovery / Demo

### Prospect Profile
- **Company:** Agency (not specified)
- **Role:** Building automation agents for clients
- **Industry:** Agency/Automation Services
- **Team size:** 3 people
- **Tech stack:** Cloud Code, n8n (current), exploring DataGen

### Pain Points

#### Pain Point 1: Agent Trigger/Deployment Gap
- **Depth:** qualified
- **Surface symptom:** "Because currently I'm still using n8n but I start soon start. Want to move to this phase. You know, I build this inside cloud code and then whenever something this will run and you know like yeah, it's maybe because I haven't have this in VPS."
- **Business impact:** Manual agent execution in Cloud Code - can't automate agent runs based on triggers. Currently requires n8n as middleware to handle webhook-based automation.
- **Personal stake:** Not explicitly mentioned
- **DataGen relevance:** DataGen solves this with webhook URLs for deployed agents, enabling trigger-based automation without n8n dependency

#### Pain Point 2: Code Stability During Agent Runs
- **Depth:** qualified
- **Surface symptom:** "While doing the output, how you make sure that the oh your code don't get changed while you're running for an input? You know, so how that you're gonna make or you make sure that."
- **Business impact:** "Because sometimes you know, we. When you do a request you sometime your code get changed, right. So instead of without changing the code, how you make sure we get the exact output we were looking for? You know, because sometime cloth code change the code, right? Based on. But I don't want to change it. I just want take this as input. Just give the output. No, without changing any code."
- **Personal stake:** Not explicitly mentioned
- **DataGen relevance:** Tool-based approach prevents code modification - agent can only execute tools, not change underlying code

#### Pain Point 3: Clay Alternative Market Gap
- **Depth:** surface
- **Surface symptom:** "People looking to replace Clay. But. But they not have the technicality. Plus they don't know how to, you know, do that. So I think there's a huge gap in the market suddenly."
- **Business impact:** Market opportunity observation - not a personal pain. Clients want Clay alternatives but lack technical capability.
- **Personal stake:** Not mentioned
- **DataGen relevance:** DataGen positions as Clay complement (not replacement) - different market positioning than what Lohit initially perceived

### Latent Demand Signals

#### Signal 1: Complex Workflow Management
- **Type:** curiosity-question
- **Evidence:** "So you mean like this. The data gen is solving this wave. Uh, you know, web like agent call issue. Which quote code like where we need to manually call the agent. But yeah, using that agent like whenever the trigger happen you it will call the agent. It will do the output and you know it's get that output, right?"
- **Inferred need:** Seeks infrastructure to manage multi-agent workflows with automatic triggers and output handling - beyond just single agent execution

#### Signal 2: LinkedIn Data Scraping Concerns
- **Type:** workaround
- **Evidence:** "So you're just scrapping LinkedIn so they're not blocking your accounts?"
- **Inferred need:** Has experience with LinkedIn scraping challenges and account blocking. Concerned about reliability and account safety when scraping at scale.

#### Signal 3: Education/Positioning Gap
- **Type:** casual-complaint
- **Evidence:** "I can start talking about data gen, like how we are using all this, you know, because I don't think many people know about all this."
- **Inferred need:** Recognizes market awareness gap for DataGen's capabilities. Sees opportunity to educate audience as potential differentiator.

#### Signal 4: Robust Solution Building
- **Type:** normalized-pain
- **Evidence:** "But also with time we need to build a robust solution"
- **Inferred need:** Current solutions (Cloud Code alone) aren't production-ready for client delivery. Needs more reliability/stability before scaling agency offerings.

#### Signal 5: UI Layer for Input Management
- **Type:** curiosity-question
- **Evidence:** "Do you build a like interface like UI where you give this input so it don't change the backend because if you make do a request in float code it will change the code. But if you have a UI it not change the back end because you're just giving the input and give you the output is it?"
- **Inferred need:** Wants abstraction layer between end users and code to prevent accidental modifications. Looking for production-ready interface for clients.

### Current Stack & Workflow

**Tools:**
- **Cloud Code:** Primary agent development environment - builds agents, skills, workflows
- **n8n:** Current trigger/webhook automation middleware (wants to move away from this)
- **DataGen:** Exploring for agent deployment and trigger-based automation

**Manual Processes:**
- Building agents in Cloud Code (fast development)
- Manually triggering agents (no automated webhook support currently)
- Using n8n as bridge between external triggers and Cloud Code agents

**Integration Gaps:**
- Cloud Code agents can't be triggered automatically by external webhooks
- No production deployment layer for Cloud Code agents
- Code stability concerns when running agent workflows programmatically

**Volume:**
- Building "lots of automation agents" for clients (agency model)
- 3-person team

### Buying Signals
- **Timeline:** Immediate exploration - "I plan out whole thing now I'll start executing them"
- **Budget:** Not mentioned, but framed as agency looking to scale client offerings
- **Decision process:** Solo exploration, likely founder/technical decision-maker for 3-person team
- **Champion potential:** Strong - active Cloud Code user, wants to create content about DataGen ("I can start talking about data gen"), sees strategic value in partnership approach

### Partnership Discussion

**Lohit's Proposal:**
"Maybe we can partner. Right? I for agency we start using this and come up with new polar statement where maybe we learn some from you guys then you know. Yeah, implement it. Then it'll let you know how it's working and where we find the bottleneck will let you know so you can improve auto of that. And same time I can talk about this in LinkedIn, right? Hey, we are using this with this."

- Positioned as design partner opportunity
- Offers feedback loop for product improvement
- Willing to create LinkedIn content about DataGen
- Describes himself as "hardcore user of float code" with engaged audience

### Strategic Positioning Clarification

**Initial Perception:** Lohit viewed DataGen as "Clay alternative"

**Corrected Positioning (Yusheng):**
"I was actually. Yeah, that's not something we try to achieve. We see ourselves as a very different product to Clay. We. If anything we probably will complement Clay."

**Value Prop Clarified:**
"What I wanted to say is actually probably the very bottom line is actually like we start to be able to provide people like an email of okay for this account executive, right. What his. His kind of his daily report and he can like ask question about this. So we basically give every a. Every rep and agent their personal agent for pipeline or meeting prep or whatever through this central repository."

**Integration Path:**
"And the etcher Clay could be a part of the like because they still wanted to outreach. They still want to declare and Clay data actually can be fit into this repository."

### Summary
Lohit is an active Cloud Code user building automation agents for agency clients. Primary qualified pain is the agent deployment gap - can't trigger Cloud Code agents via webhooks without n8n middleware. Strong design partner potential with content creation capability and immediate implementation timeline. Initially sought Clay alternative but aligned on DataGen's complementary positioning as agent orchestration layer. Follow-up scheduled.
