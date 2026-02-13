## Prospect Meeting: David Kwint (Automate Demand)
**Date:** 2026-02-13
**Participant:** David Kwint, Agency Owner, Automate Demand (david@automatedemand.com)
**Duration:** 63 minutes
**Meeting Type:** Demo / Product Training

### Prospect Profile
- **Company:** Automate Demand
- **Role:** Agency owner/consultant providing GTM automation services
- **Industry:** B2B sales automation agency
- **Company size:** Solo/small agency serving multiple clients

### Pain Points

#### Pain Point 1: Clay's Cost Structure
- **Depth:** qualified
- **Surface symptom:** "Clay has a 50,000 roll limit, which is sometimes annoying if you have a big list. Then it's also pretty slow sometimes and pretty expensive as well if you want to connect your CRM with it. Like, you need to pay for the 800 plan, which is oftentimes too expensive for some companies."
- **Business impact:** "The Explorer plan, which has all the functionalities that you need, basically is 350. And then if you want to connect your CRM, it's like 450 on top of this, which is like... Doesn't really make sense."
- **DataGen relevance:** David is actively exploring DataGen as a Clay replacement due to cost issues. He sees opportunity to "save $600 a month" with an alternative.

#### Pain Point 2: Clay Performance Issues
- **Depth:** qualified
- **Surface symptom:** "It's pretty slow. It can be pretty slow sometimes. Like especially running Claytons on like 10,000 rolls can sometimes take like half an hour."
- **Business impact:** "Especially like HubSpot lookups. They take like, if you want to do a HubSpot lookup of like contacts or companies for 30,000 rows, then it's like four hours."
- **DataGen relevance:** Performance bottlenecks with large datasets create workflow delays for client deliverables.

#### Pain Point 3: Scalability Concerns with DataGen
- **Depth:** surface
- **Surface symptom:** "I don't know if like running like, like what the typical... Like the size of your... Your league... Like 10,000 companies... Let me try to run it and see how it goes."
- **Business impact:** David wants to run enrichment on 10,000 company datasets but is uncertain about DataGen's performance at scale. This creates hesitation in fully committing to DataGen for client work.
- **DataGen relevance:** Need to prove DataGen can handle 10,000+ row enrichment reliably and quickly to win agency confidence.

### Latent Demand Signals

#### Signal 1: Desire for End-to-End Agent-Native Workflow
- **Type:** curiosity-question
- **Evidence:** "In my ideal world, like I want to just stay in Claude Code basically and don't need to do anything. And like I have all my frameworks in here... Come up with the playbook, come up with the messaging. I approve of the messaging. And then build all the information. Here are like 20 APIs that you will need. Use all of them and create the info and then send this to instantly."
- **Inferred need:** David wants an agent-native client platform where all workflows run through Claude Code instead of stitching together Clay, Instantly, CRM, etc. He sees DataGen as enabling this unified approach.

#### Signal 2: Visualization Layer Gap
- **Type:** workaround
- **Evidence:** "The most important thing is that you need to have this kind of visualization layer which the trigger dev doesn't have. So clay become a very good monitor of like all your data. You can kind of see it, run it."
- **Inferred need:** Even when exploring code-first solutions, agencies need a data grid view to monitor pipeline status and debug issues. This is a gap in pure code alternatives like Trigger.dev.

#### Signal 3: Partner/Agency Model Interest
- **Type:** curiosity-question
- **Evidence:** "I have another client where it's unclear how we are going to work together from here from this point on because most of the workflows and systems already have been done for them... I wanted to ask you if you would be open to [partnering on context system agents]."
- **Inferred need:** David sees opportunity to sell ongoing agent/AI services to clients after initial automation setup is complete. He's exploring partnership model with DataGen for technical support.

### Current Stack & Workflow

**Tools:**
- Clay: Primary enrichment and workflow orchestration
- Instantly: Email outreach platform
- HubSpot: CRM (for multiple clients)
- Claude Code: Emerging center of workflow (wants to centralize here)
- Fireflies/Liro: Meeting intelligence (for client Liro.io)

**Manual Processes:**
- Building custom enrichment workflows for each client in Clay
- Manually configuring API integrations across Clay, CRM, outreach tools
- Manual prompt engineering for each client context

**Integration Gaps:**
- No unified way to deploy agent workflows as scheduled jobs
- No direct webhook/API path from Claude Code agents to client CRMs
- Lack of monitoring/observability for deployed agents

**Volume:** Typically 10,000+ company records per client enrichment project; 6 active campaigns simultaneously

### Current DataGen Usage Context

David is actively testing DataGen during this call:
- Successfully set up Instantly API integration
- Deployed first agent (instantly-domain-reply-rate) with daily schedule
- Connected GitHub repo for agent deployment
- Set up Claude Code OAuth token for agent execution
- Exploring agent-based alternatives to Clay workflows

### Buying Signals
- **Timeline:** Active testing now; needs scale validation before fully committing client work to DataGen
- **Budget:** Cost-sensitive (Clay pricing is a major pain point); looking for alternatives in $200-350/month range vs Clay's $800+ pricing
- **Decision process:** Solo agency owner, makes own tool decisions; clients trust his recommendations
- **Champion potential:** Strong. David is evangelizing agent-native approach and sees DataGen as core to his future service offering. Quote: "In my ideal world, I want to just stay in Claude Code basically."

### Client Context Mentioned

**Liro.io:**
- GDPR-compliant meeting intelligence tool (like Fireflies without meeting bots)
- Uses HubSpot CRM
- David has existing relationship; exploring ongoing agent-based services
- ICP: B2B companies with 20+ person sales teams, selling remotely and on-site
- Manufacturing is a strong vertical
- David has API access to their Liro data and HubSpot

**Immediate opportunity:** Build CRM analysis agent for Liro using HubSpot API

### Summary
David is a qualified prospect with urgent business pain around Clay's cost and performance. He operates an agency serving multiple B2B clients and sees DataGen as enabling an agent-native service model where he builds custom intelligence agents for clients instead of manual workflows. Primary blocker is proving DataGen can handle 10,000+ row enrichment at scale. Strong champion potential if scale concerns are resolved.

**Recommended next action:**
1. Test Instantly reply rate agent with David's API key (shared in call)
2. Build demo HubSpot CRM analysis agent for Liro.io to demonstrate partner model
3. Run performance benchmark on 10,000 row enrichment to prove scalability
