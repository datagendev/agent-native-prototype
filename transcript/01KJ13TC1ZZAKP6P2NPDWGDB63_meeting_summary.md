---
title: "Prospect Meeting: Alex Waiman - AI Enablement / Chief of Staff Agent"
description: "Discovery call with Alex Waiman, sales professional building AI-powered Chief of Staff agent for agency use"
category: "research"
tags: ["prospect", "ai-enablement", "chief-of-staff", "sales", "agent-building"]
created: 2026-02-23
updated: 2026-02-23
status: "active"
priority: "high"
---

## Prospect Meeting: Alex Waiman
**Date:** 2026-02-23
**Participant:** Alex Waiman, Sales professional / AI early adopter, Dataloop (transitioning to own agency)
**Duration:** ~29 minutes
**Meeting Type:** Discovery / Knowledge exchange

### Prospect Profile
- **Company:** Dataloop (current employer, going through Dell merger) + founding new agency with former colleague
- **Role:** Sales enablement, transitioning to agency founder
- **Industry:** Sales / Marketing / AI enablement
- **Company size:** Not specified; agency is pre-launch at time of meeting

---

### Pain Points

#### Pain Point 1: Context Engineering Loop - Can't Get Consistent Quality Output from LLMs
- **Depth:** qualified
- **Surface symptom:** "I'm still not managing to get the right output which would suggest that the context isn't right and the engineering isn't right."
- **Business impact:** "And then I'm stuck in the same endless loop of back and forth and then how do I then go and dump that? And like you saw what the Frankenstein of my V1 OS was. Because I kept on like going like back and forth and I'm like, oh, amazing stuff. And like dump it back in the OS and like fix it. And it's like Frankenstein."
- **Personal stake:** "I've invested all of this time in building the context and engineering the context in the right way." Alex is hypercritical of himself and frustrated by the gap between effort invested and quality of output.
- **DataGen relevance:** DataGen's agent architecture patterns (skills, commands, primitives) and the context OS framework directly address this — structured agent design prevents the "Frankenstein" iteration spiral.

#### Pain Point 2: Confusion About Agent Architecture - Commands vs. Skills vs. Plugins
- **Depth:** surface
- **Surface symptom:** "I'm struggling very much with this demand still. Aging versus plugin versus. Yeah, skill. I don't know. I don't. I'm struggling to understand when to use what and how."
- **Business impact:** Confusion is slowing down Alex's ability to productize his Chief of Staff agent and extend it for his agency. Without clear architecture understanding, he cannot reliably build or hand off the system to his partner.
- **Personal stake:** "I'm not entirely clear. I believe, like this is how unclear I am. I believe that the Chief of Staff is a command." (Expressed with visible uncertainty during screen share.)
- **DataGen relevance:** DataGen's skill/command framework and documentation directly solves this. Yusheng clarified on the call: commands are deterministic callers of skills (capabilities). This is exactly the mental model DataGen builds around.

#### Pain Point 3: Calendar Integration Blocked - No Real-Time Context for Chief of Staff Agent
- **Depth:** qualified
- **Surface symptom:** "I tried connecting the calendar. I don't know what. Like I've tried going on to the Google Calendar API. Tried connecting it. I spent half an hour trying to."
- **Business impact:** Chief of Staff agent currently operates without calendar data, limiting its ability to act as a true daily assistant. Alex cannot use it for scheduling, meeting prep, or time management automation.
- **Personal stake:** "I don't handle calendar at the moment. Truthfully, for the purposes of now, it wasn't important enough for me to debug." (Resigned acceptance - normalized pain.)
- **DataGen relevance:** Klavis MCP and Cloud AI MCP integrations Yusheng mentioned are directly relevant. DataGen could facilitate this integration for Alex's agent stack.

#### Pain Point 4: Partner Not Yet Using the System - Collaboration Gap
- **Depth:** surface
- **Surface symptom:** "He doesn't really know how to use it yet. Like I kind of wowed him with, you know, a bit of Jacob, Jacob Diettle, that stuff."
- **Business impact:** The agency is starting with a shared Git repo OS but only Alex can operate it. The partner (more marketing-focused) cannot contribute or benefit from the system yet.
- **Personal stake:** Alex is further along and carrying the technical knowledge load alone. Onboarding his partner is a near-term blocker to scaling the agency.
- **DataGen relevance:** DataGen's agent-native approach lowers the technical bar for non-technical users - relevant for enabling the partner.

---

### Latent Demand Signals

#### Signal 1: Job Security Anxiety in AI Era
- **Type:** casual-complaint / normalized-pain
- **Evidence:** "I'm, I have a naturally pessimistic nature and I'm very nervous that I could very as easily be out of a job. But, but I hope you're right."
- **Inferred need:** Alex is building his AI capabilities partly as career self-preservation. This is a strong motivator for adoption urgency - he is not exploring casually. Tools that demonstrably increase his competitive advantage as a sales professional have personal, not just professional, value.

#### Signal 2: Manual Research Process for Chief of Staff Build
- **Type:** workaround
- **Evidence:** "I started looking at all of the Chief of Staff repository and I looked at the ones which were receiving the highest, the most amount of stars. I said, go and have a look at these handful of repos, start to get an understanding of what a Chief of Staff is and come back to me."
- **Inferred need:** Alex is stitching together agent-building methodology from scattered GitHub repos and social posts. There is latent demand for a structured, opinionated framework for building agents - exactly what DataGen's OS and skills system provides.

#### Signal 3: Algorithm-Driven Information Overload
- **Type:** normalized-pain / casual-complaint
- **Evidence:** "I clicked on one link and then all of a sudden it's like, yeah. And I'm completely overwhelmed."
- **Inferred need:** Alex is struggling to filter signal from noise in the AI space. A trusted advisor relationship (like Yusheng) or a curated learning path has high value. DataGen's community / expert guidance angle could be a wedge.

#### Signal 4: Context OS Described as "Frankenstein"
- **Type:** workaround
- **Evidence:** "And like you saw what the Frankenstein of my V1 OS was. Because I kept on like going like back and forth and I'm like, oh, amazing stuff. And like dump it back in the OS and like fix it."
- **Inferred need:** Without a structured methodology for iterative agent improvement, Alex accumulates technical debt in his OS. DataGen's opinionated architecture and version-controlled skill/command patterns directly address this.

---

### Current Stack and Workflow

**Tools:**
- Claude Code: Primary agent-building environment and Chief of Staff runtime
- Cursor: Downloaded but unclear on purpose; not using meaningfully
- Visual Studio Code: Also downloaded; no clear preference over Cursor
- Git repository: Stores OS/context files; shared access intended for agency partner
- Google Calendar API: Attempted integration, currently blocked (free Gmail account limitation)
- Gmail (free): Current account limiting some API integrations

**Manual Processes:**
- Alex manually interviews himself using Claude to populate context files -- ongoing, iterative
- Manually researches GitHub repos and X posts to learn agent-building best practices -- daily, no fixed duration
- Manually manages task list via Chief of Staff command (no calendar sync yet)

**Integration Gaps:**
- Google Calendar not connected to Chief of Staff (technical blocker, free vs paid account)
- Partner not yet onboarded to shared Git OS -- knowledge handoff is manual and informal
- No automated feedback loop for evaluating agent output quality -- entirely subjective, human judgment

**Volume:** Single user currently; agency pre-launch, aiming for 2-person shared OS when partner onboards

---

### Buying Signals
- **Timeline:** Agency launch imminent (buying domain now); planning Google Suite upgrade soon, which unlocks calendar integration. Follow-up session booked for Wednesday.
- **Budget:** No explicit budget discussion. Mentioned $10k/year enrichment data in context of agency economics -- suggests awareness of tool costs at agency scale.
- **Decision process:** Alex is sole decision-maker for his own stack. Agency is a 2-person founding team; partner will need to be onboarded.
- **Champion potential:** High. Alex is already using Claude Code, building on the same OS framework DataGen uses, and sharing his workflow publicly. He is well-positioned as an internal advocate and potential case study.

---

### Summary

Alex Waiman is a non-technical sales professional in the top 0.001% of AI adopters, actively building a Claude Code-based Chief of Staff agent for a new sales/marketing agency. His primary pain is the "Frankenstein" iteration problem -- investing heavily in context engineering without achieving consistent, satisfying output -- compounded by architectural confusion around commands vs. skills vs. plugins. He is a natural fit for DataGen's structured agent-building framework and is motivated by both professional upside and genuine career-preservation urgency. Recommended next action: follow-up session (already scheduled for Wednesday) should focus on demonstrating DataGen's skill/command architecture and how it prevents the Frankenstein spiral, with a secondary goal of unblocking his calendar integration via Klavis MCP.
