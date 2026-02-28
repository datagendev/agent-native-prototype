---
title: "Clay Run Issues - Jeremy Ross Meeting"
description: "External meeting discussing Clay integration pain points, custom tool QA, and DataGen product feedback"
category: "research"
tags: ["clay", "custom-tools", "jeremy-ross", "product-feedback", "qa", "slack-bot"]
created: 2026-02-28
updated: 2026-02-28
status: "active"
priority: "high"
---

## Prospect Meeting: Jeremy Ross
**Date:** 2026-02-28
**Participant:** Jeremy Ross, Agency Owner/Operator, Independent (jeremy.scott.ross@gmail.com)
**Duration:** ~55 minutes
**Meeting Type:** Product feedback / Discovery

### Prospect Profile
- **Company:** Independent Agency / Freelance
- **Role:** Agency operator building automations for clients (CRM, HubSpot, outreach workflows)
- **Industry:** GTM automation / RevOps agencies
- **Company size:** Small agency (solo or small team)

---

### Pain Points

#### Pain Point 1: Silent Failures and Lack of Observability in Cloud-Run Custom Tools
- **Depth:** qualified
- **Surface symptom:** "I mean it's because, yeah, if it gets a result at the end, even if it's a partial result, like it's hard to debug something that's running in the cloud unless you have access to wherever it's running."
- **Business impact:** "There were at least like 10% that did not have that final company association step complete. And then there were a few that just had like a fragment." -- Jeremy had to manually go in and fix records after running a batch job, wasting significant cleanup time after deployment.
- **Personal stake:** "Dude, I'm so, so far beyond all that at this point. Like I've gone in and fix things manually and then like different ways and like flipped it upside down." -- Implicit frustration of already having moved past the problem by brute-force fixing, with no clean audit trail.
- **DataGen relevance:** A QA mode or agent-assisted log review step post-deployment would surface these silent partial failures before they compound at scale.

#### Pain Point 2: No QA Layer When Deploying Custom Tools to Clay
- **Depth:** qualified
- **Surface symptom:** "It's really different when you use the SDK just when you develop things locally and then you push it to datagen because then you get to see all of those things and then it's like, hey, 5% of the tool of the clay tools that you submitted actually have X, Y and Z issues."
- **Business impact:** Errors discovered only after running at scale. By that point, records are polluted and cleanup is manual and time-consuming.
- **Personal stake:** "Here are some things that would be hard for you to notice that I want to propose some code changes for." -- Jeremy has to catch these himself after the fact with no automated safety net.
- **DataGen relevance:** A QA bot/agent that runs the tool once, reads all logs, and proposes code fixes before full deployment would directly address this.

#### Pain Point 3: Async 202 Response Breaking Clay Retries
- **Depth:** urgent
- **Surface symptom:** "Actually so one thing that I mentioned in chat briefly was the 202, you know that up for the async calls so for clay they don't do retries on the 202."
- **Business impact:** "Dude, it was a huge headache trying to do async retries, you know, balance. It's a 202 plus." -- Clay treats 202 as a success and moves on, so async jobs that haven't resolved yet produce empty or missing data downstream with no automatic retry.
- **Personal stake:** "It was a huge headache." -- Framed with visible frustration. Jeremy explicitly raised it as something that could "help sway people" in DataGen's favor if fixed. Compared it to Apollo's API being "dreaded in the clay community" as a cautionary example.
- **DataGen relevance:** Returning a 4xx error instead of 202 when results aren't ready would allow Clay's native retry logic to handle async jobs without custom workarounds.

#### Pain Point 4: Workflow Complexity in Clay vs. Speed of Development in Claude Code
- **Depth:** surface
- **Surface symptom:** "He said he can do something really quick in cloud code in 30 minutes and get a pretty decent result. But like it turns out have to be like a nine connected table in clay."
- **Business impact:** Not personally quantified in this call, but referenced as a recurring complaint from multiple contacts: "At least two or three people I talk to always ask me like how do I do this in Claude Code, they really want to get out of clay."
- **DataGen relevance:** The ability to develop custom tools fast in Claude Code and run them at scale in Clay is the core value prop Jeremy sees for DataGen's custom tool feature.

#### Pain Point 5: No Easy Multi-Instance Agent Configuration
- **Depth:** surface
- **Surface symptom:** "I can tell you at least one thing that came up for me was just being able to have multiple iterations of the same agent just running slightly different prompts. So that to me didn't seem obvious on datagen."
- **Business impact:** Jeremy wants to run the same agent for different HubSpot clients with different configurations (different users, permissions, prompt variants) without duplicating the entire agent setup.
- **DataGen relevance:** Parameterized agent runs or multi-instance agent deployment would unlock this use case.

---

### Latent Demand Signals

#### Manual Record Cleanup After Batch Jobs
- **Type:** normalized-pain
- **Evidence:** "I'm so, so far beyond all that at this point. Like I've gone in and fix things manually and then like different ways and like flipped it upside down. There's no way I can unwrap that."
- **Inferred need:** Jeremy has internalized post-run manual data cleanup as part of his workflow. He doesn't frame it as a solvable problem -- he's accepted it. This is a strong signal of normalized pain around observability and error recovery in batch pipelines.

#### Template Uselessness in Clay
- **Type:** casual-complaint
- **Evidence:** "I do hear, I do hear people like, one guy told me like yeah, I mean they, everyone knows the template. No one use template in clay like almost no one."
- **Inferred need:** Teams waste time rebuilding similar workflows from scratch every engagement because Clay templates don't generalize well. DataGen's custom tool approach (fast build + reuse) is a latent unlock here.

#### Apollo API as a Cautionary Reference
- **Type:** curiosity-question (framed as competitive intelligence)
- **Evidence:** "Apollo is a massive tool, super popular and its API is dreaded in the clay industry or the clay community. And it's because they have very low bandwidth for API calls. You have to sit there and babysit the API like over and over and over again."
- **Inferred need:** Jeremy is actively benchmarking DataGen's API reliability and DX against the worst-case experience (Apollo). Fixing the 202/async issue would meaningfully differentiate DataGen in Clay's ecosystem.

#### Slack Multiplayer for Client-Facing Agents
- **Type:** curiosity-question
- **Evidence:** "I had a call with them today and they were saying that they're okay with the idea of starting in Claude code and like the terminal and everything but they really need to get to something that's more multiplayer and like user friendly."
- **Inferred need:** Jeremy's clients (like Litec) need a UI layer -- they can't live in the terminal. The DataGen Slack bot directly addresses this, but Jeremy wasn't fully aware of how it worked before this call.

---

### Current Stack & Workflow

**Tools:**
- Clay: Parallel data enrichment and outbound pipeline orchestration
- HubSpot: CRM; contacts, companies, associations
- Slack: Client communication and agent notification delivery
- DataGen: Custom tools + agent deployment (active user, building on it)
- Google Sheets: Upstream data source for client workflows (CSV export -> webhook -> Clay -> HubSpot)
- Sumble: Mentioned as a data intelligence tool with strong GTM insights (Kaggle founder; Jeremy sees it as better than Parallel for GTM-specific signals)

**Manual Processes:**
- Post-run record cleanup after partial failures in HubSpot -- manual, ad hoc, no tooling
- QA of custom tool output by manually inspecting HubSpot records after API calls
- Slack app deletion to work around 10-app free plan limit -- friction in onboarding DataGen Slack bot

**Integration Gaps:**
- DataGen async (202) responses not compatible with Clay's retry behavior -- requires manual retry babysitting
- No in-platform QA step when deploying custom tools from Claude Code to DataGen
- Slack bot setup flow has too many steps and lacks discoverability (UI doesn't surface "Agents / Slack Bot" clearly)

**Volume:** Running weekly recurring agents for at least one active client (Codex); processing CSV -> webhook -> Clay -> HubSpot pipelines at regular cadence.

---

### Buying Signals
- **Timeline:** Active user already deployed agents for clients. Exploring how to scale. No explicit deadline, but cadence suggests near-term decision on deepening DataGen use.
- **Budget:** Paying DataGen customer (implied). Paying for Slack. Aware of Clay's pricing as a competitive factor.
- **Decision process:** Solo operator. Likely makes his own tooling decisions. Advises clients on tooling.
- **Champion potential:** High. Jeremy is deeply engaged, providing specific product feedback, referencing conversations with multiple other contacts who share the same frustrations. He named a specific prospect (Eric Nowski) and suggested building a video walkthrough together -- a classic champion behavior.

---

### Summary

Jeremy is an active DataGen user and agency operator who ran into compounding issues with silent failures, async compatibility with Clay, and lack of observability when running custom tools at scale. His highest-priority ask is a QA agent or mode that surfaces partial failures and log anomalies before they reach production at scale. He is a strong product champion candidate and his pain points are highly actionable: fixing the 202/async behavior and adding a QA step to the custom tool deployment flow would directly address his top two frictions.
