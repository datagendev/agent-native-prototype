---
title: "Prospect Meeting: Lohit Boruah - Cloud Code & Lead Enrichment Discovery"
description: "Discovery call with Lohit Boruah exploring Cloud Code for replacing Clay in outbound lead workflows"
category: "research"
tags: ["prospect", "cloud-code", "clay", "lead-enrichment", "copywriting", "skills-agents"]
created: 2026-02-24
updated: 2026-02-24
status: "active"
priority: "high"
---

## Prospect Meeting: Lohit Boruah
**Date:** 2026-02-24
**Participant:** Lohit Boruah (role/company not explicitly stated - appears to be a marketing/outbound agency operator)
**Host:** Yusheng Kuo (DataGen)
**Duration:** ~90 minutes
**Meeting Type:** Discovery / Deep-dive session

---

### Prospect Profile
- **Name:** Lohit Boruah
- **Role:** Marketing / outbound agency operator (inferred - manages multiple client ICPs and outbound campaigns)
- **Industry:** B2B marketing / lead generation / outbound sales
- **Company size:** Not mentioned
- **Current tools:** Clay, Cloud Code (Claude Code), external databases (Supabase / Neon explored)

---

### Pain Points

#### Pain Point 1: Clay's Plan Limitations and Cost
- **Depth:** qualified
- **Surface symptom:** "Because HTTP requires all this feature. You need extra plan, you know, which Clay can easily do. Right. Like without upgrading the plan. So that's why..."
- **Business impact:** Clay's pricing and row caps create friction at scale. Lohit is actively looking to replace or supplement Clay with Cloud Code to avoid upgrade costs and row limitations.
- **Personal stake:** Not explicitly stated, but the urgency to replace Clay suggests active cost pressure and operational frustration.
- **DataGen relevance:** DataGen's Cloud Code / SDK layer can replace Clay for data enrichment and lead list processing without per-row pricing constraints.

#### Pain Point 2: Data Structuring in Cloud Code (Multiple Tables Problem)
- **Depth:** qualified
- **Surface symptom:** "I'm just thinking how can I structure this multiple table? Just like in Clay we have multiple tables. How can I have, you know, multiple, you know, for multiple situation, multiple sheets or something, you know, how can I structure that?"
- **Business impact:** Without a clear data modeling pattern for Cloud Code, Lohit cannot migrate his workflows from Clay. This is a direct blocker to scaling his operations.
- **Personal stake:** Lohit is actively experimenting with Cloud Code and needs hands-on guidance to proceed.
- **DataGen relevance:** Yusheng walked Lohit through using external databases (Supabase / Neon) with proper indexing and table design as the solution.

#### Pain Point 3: Managing Multiple API Keys Outside Clay
- **Depth:** surface
- **Surface symptom:** "If you are using Cloud Code to replace Clay, you have to gather many API keys. That's the first thing. Because there's no like [unified interface]..."
- **Business impact:** Clay abstracts API key management. Moving to Cloud Code exposes complexity that slows adoption and increases engineering overhead.
- **Personal stake:** Not explicitly quantified.
- **DataGen relevance:** MCP tool ecosystem wraps multiple APIs under one access point, reducing this friction significantly.

#### Pain Point 4: AI-Generated Copy Sounds Too Generic ("Too AI")
- **Depth:** qualified
- **Surface symptom:** "I'm just thinking how can I reduce that, you know, AI tone..."
- **Business impact:** AI-generated copy that sounds mechanical reduces prospect response rates in outbound campaigns. Lohit manages copywriting for client campaigns and needs personalized, human-sounding outputs.
- **Personal stake:** "Lohit emphasized analyzing outputs before deciding on adoption" - he is cautious about deploying AI copy without quality checks.
- **DataGen relevance:** Prompt engineering techniques (self-critique, iterative tuning, concrete language) discussed as the solution. DataGen's copywriting skill can embed these frameworks.

#### Pain Point 5: Iterative Prompt Tuning is Difficult in Clay's UI
- **Depth:** qualified
- **Surface symptom:** "Challenges of iterative prompt tuning within Clay's UI for copywriting refinements. Emphasized the importance of human review and back-and-forth optimization."
- **Business impact:** Clay's UI makes it hard to rapidly iterate on prompts. Lohit's copywriting refinement cycles are slow, limiting how quickly he can deliver quality outputs for clients.
- **Personal stake:** Not explicitly stated.
- **DataGen relevance:** Cloud Code enables programmatic prompt iteration outside Clay's UI constraints.

#### Pain Point 6: Lack of Deep Cloud Code / Skill Development Resources
- **Depth:** qualified
- **Surface symptom:** "Highlighted lack of dedicated cloud code skill development channels. Identified need for deeper tutorial resources on advanced cloud code skill/agent building and AI prompt engineering."
- **Business impact:** Lohit cannot learn Cloud Code skill development independently - no quality tutorial resources exist. This slows his adoption and limits his ability to build scalable agent workflows for clients.
- **Personal stake:** "Lohit plans to experiment with Cloud Code and share his builds for feedback." He is investing personal time to learn, but lacks good learning materials.
- **DataGen relevance:** DataGen can capture Lohit as a power user and champion by providing direct mentorship, resources, and community access.

---

### Latent Demand Signals

#### Signal 1: Manual Lead Research Workflow (Normalized Pain)
- **Type:** normalized-pain
- **Evidence:** Discussion of "interview-explore-prototype-full-agent development cycle" and needing to "start with 5-10 rows before scaling" implies Lohit currently does this manually or semi-manually.
- **Inferred need:** Lohit has not yet automated his lead research process end-to-end. He knows what he wants but hasn't built it yet. This is a strong latent demand for a pre-built enrichment pipeline.

#### Signal 2: Client Onboarding at Scale
- **Type:** workaround
- **Evidence:** "Lohit aims to automate end-to-end workflows for onboarding multiple clients efficiently." He discussed creating modular lead magnet skills "usable across different clients."
- **Inferred need:** Lohit is managing or planning to manage multiple clients and needs a repeatable, scalable onboarding system. Currently this is likely manual or semi-automated.

#### Signal 3: Curiosity About Video/Creative API Integration
- **Type:** curiosity-question
- **Evidence:** "Explore APIs of Keyframe software for integrating video generation into lead magnet workflows" listed as action item.
- **Inferred need:** Lohit is interested in adding video/creative generation to his lead magnet workflow. This suggests he sees content generation as a future capability gap.

#### Signal 4: Acceptance of AI Copy Limitations
- **Type:** normalized-pain
- **Evidence:** "The team identified that AI-generated copy often sounds too mechanical or generic" framed as a known issue without a complete solution.
- **Inferred need:** Lohit has accepted some level of AI copy quality degradation. He hasn't found a systematic fix - just workarounds (human review, back-and-forth). A copy quality agent with self-critique built in would address this latent need.

---

### Current Stack & Workflow

**Tools:**
- **Clay:** Lead list building, enrichment (primary tool being replaced/supplemented)
- **Cloud Code (Claude Code):** Emerging tool for agent and skill development
- **Supabase / Neon:** Being explored for persistent database storage
- **Keyframe:** Video generation API (being explored for lead magnets)
- **MCP tools:** Being introduced as API abstraction layer

**Manual Processes:**
- Lead list research and filtering -- partially manual, moving toward agent-based
- Copywriting iteration and quality review -- human review loop required
- Client ICP data preparation -- manual input needed before agent can execute
- Prompt tuning for AI copy -- done iteratively by hand in Clay UI

**Integration Gaps:**
- No automated flow from Clay lead list to enrichment database to outreach sequence
- No unified API key management solution yet (moving away from Clay's abstraction)
- No programmatic prompt iteration environment (Clay UI bottleneck)

**Volume:** Not explicitly stated. Context suggests managing multiple client campaigns with lead lists large enough that Clay's row caps and credit costs are prohibitive.

---

### Buying Signals
- **Timeline:** Active -- Lohit is building NOW, not exploring. Multiple action items assigned in the meeting for immediate follow-up.
- **Budget:** Not discussed explicitly. Pain around Clay's upgrade costs suggests budget sensitivity but also willingness to switch for better value.
- **Decision process:** Lohit appears to be a solo decision-maker for his own tooling. No mention of other stakeholders.
- **Champion potential:** HIGH. Lohit is a hands-on builder actively experimenting with Cloud Code. He plans to share builds for feedback and follow up with Yusheng directly. Strong potential to become a power user and advocate.

---

### Summary

Lohit is an outbound/marketing operator actively trying to replace or supplement Clay with Cloud Code to escape plan limitations and per-row costs, while building scalable, modular agent workflows for multiple clients. His primary blockers are data structuring in Cloud Code, API key management overhead, and AI copy quality. He is a high-engagement prospect with strong champion potential -- actively building, seeking mentorship, and planning to follow up with demos of his work.

**Recommended next action:** Provide Lohit with direct resources (skill creation tools, data modeling templates) and schedule a follow-up to review his prototype builds.
