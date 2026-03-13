## Prospect Meeting: David Kwint (AutomateDemand)
**Date:** 2026-03-13
**Participant:** David Kwint, Agency Owner/Clay Partner, AutomateDemand
**Duration:** 47 minutes
**Meeting Type:** Strategic Partner Discussion

### Prospect Profile
- **Company:** AutomateDemand
- **Role:** Agency Owner, Clay Partner
- **Industry:** Marketing/Sales Agency
- **Company size:** Small agency (hosting Clay club events in Germany)

### Pain Points

#### Clay Pricing Model Impact on Agency Economics
- **Depth:** qualified
- **Surface symptom:** "Some of the partners obviously said like we are the ones who have the most usage of clay and will benefit the least of the pricing change because we were paying more at the end."
- **Business impact:** "Especially with the pricing change like you just get burned if you want to enrich like many rows... it's also now since today has become way more expensive to do this and to do it in scale."
- **Personal stake:** David is a Clay partner who now faces pressure from pricing changes affecting his business model
- **DataGen relevance:** DataGen's open-source Clay alternative could provide cost-effective scaling for agency work

#### Clay Platform Lock-in Without API/MCP Access
- **Depth:** qualified
- **Surface symptom:** "The only thing is just it's kind of closed. I hope it will be open very soon."
- **Business impact:** "Because Clay doesn't have the MCP... or like API even API. So we can't do that." (referring to 24/7 agent deployment for pipeline sourcing)
- **Personal stake:** David asked multiple times about Clay's API roadmap during partner meetings, showing this blocks his desired workflows
- **DataGen relevance:** DataGen could enable agent-driven automation that Clay's closed platform prevents

### Latent Demand Signals

#### Normalized High-Touch Manual Enrichment
- **Type:** workaround | normalized-pain
- **Evidence:** "He's not technical but he said he mostly only use clay for salesforce integration because sometimes you just cannot get around with it now but other everything he just go through cloud code directly enrich from cloud code."
- **Inferred need:** Agencies are bypassing Clay's UI for enrichment and doing manual work in Cloud Code because Clay's platform doesn't scale cost-effectively

#### Appetite for Technical Open-Source Alternative
- **Type:** curiosity-question
- **Evidence:** "I think if you can... if we can manage to create something like this I think so many people will migrate from clay to this because like especially with the pricing change like you just get burned"
- **Inferred need:** Strong demand exists for an open-source, self-hostable alternative to Clay that agencies can control

#### Rate Limit Management Pain
- **Type:** workaround
- **Evidence:** "He said he just like if he run into API red limit he would just ask Kauko to fix it. Yeah, yeah. It's quite straightforward."
- **Inferred need:** Manual, reactive handling of rate limits suggests need for built-in orchestration (like Prefect) that handles this automatically

### Current Stack & Workflow

**Tools:**
- Clay: Primary data enrichment platform (heavy usage)
- Salesforce: CRM integration
- Cloud Code: Direct enrichment work (bypassing Clay UI)
- Clavis.ai: Workaround for MCP connectors (Google Calendar, Gmail)
- Deepline: Exploring as Clay alternative

**Manual Processes:**
- Running enrichment through Cloud Code when Clay UI doesn't scale
- Manually handling API rate limits by asking AI to fix errors
- Managing multiple client accounts across different tools

**Integration Gaps:**
- No Clay API/MCP for agent automation
- No 24/7 agent deployment capability for pipeline sourcing
- Multi-table joins and relational data not available in alternatives

**Volume:** Heavy Clay usage (enough to be impacted by pricing changes)

### Buying Signals
- **Timeline:** Immediate - already exploring alternatives (Deepline, open-source)
- **Budget:** Cost-sensitive due to Clay pricing pressure; interested in free/open-source
- **Decision process:** David runs agency independently, appears to be sole decision maker
- **Champion potential:** HIGH - David is hosting Clay clubs, has technical fluency, expressed strong interest: "I will definitely try it out and give you feedback"

### Summary
David represents agencies impacted by Clay's pricing changes and platform lock-in. Primary pain is **qualified urgency** around cost at scale and inability to build agent-driven workflows. Strong latent demand exists for an open-source, self-hostable alternative with proper orchestration. David committed to testing DataGen's Clay-like prototype and providing feedback. Recommended next action: Share cleaned-up open-source package and follow up after trial period.
