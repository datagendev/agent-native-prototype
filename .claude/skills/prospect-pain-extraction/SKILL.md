---
name: prospect-pain-extraction
description: AI extraction rules for identifying prospect pain points, latent demand, and workflow signals from unstructured discovery/demo call transcripts
---

# Prospect Pain Extraction Rules

Extraction framework for the meeting-summarizer agent. Designed for **unstructured discovery/demo calls** where pain surfaces organically rather than through guided questioning.

## Core Model: Three-Layer Pain Depth

Every pain point must be classified by depth. Most transcripts only reveal Layer 1. Your job is to trace connections between layers when evidence exists.

### Layer 1: Surface Symptom (What they say first)

The stated problem. Often vague, generic, or a proxy for the real issue.

**Linguistic markers:**
- "We need better [X]"
- "We're looking for [X]"
- "Our current [tool/process] doesn't [X]"
- "We want to [automate/improve/fix] [X]"
- "I saw your product can do [X]"

**Example:** "We need better data enrichment for our outbound."

**Extraction rule:** Capture verbatim. Do not interpret or expand. Label as `surface`.

### Layer 2: Business Impact (The measurable cost)

The concrete consequence of the surface symptom. This is where pain becomes quantifiable -- lost revenue, wasted time, missed targets, team strain.

**Linguistic markers:**
- "Because of that, we [lost/missed/can't]..."
- "It takes us [time] to [do thing]"
- "Our reps spend [X hours] on [manual task]"
- "[Number]% of our [leads/data/pipeline] is [bad/stale/wrong]"
- "We tried [X] but it [didn't work because]..."
- "Last quarter we [negative outcome]"
- "Our [metric] is [below target/declining]"

**Example:** "Our reps spend 3 hours a day manually researching accounts before they can even start outreach. We're only getting through half our target list."

**Extraction rule:** Capture with any numbers, timeframes, or metrics mentioned. Label as `impact`. Link to the surface symptom it stems from.

### Layer 3: Personal/Emotional Stake (Why this person cares)

The individual motivation. Career pressure, team morale, credibility with leadership, fear of failure. This is what converts "nice to solve" into "must solve now."

**Linguistic markers:**
- "My [boss/VP/board] is asking why..."
- "I'm on the hook for [target/result]"
- "The team is [frustrated/burned out/losing confidence]"
- "Honestly, it's been [stressful/keeping me up]"
- "If we don't fix this by [date], [consequence]"
- "I've been trying to solve this for [months/quarters]"
- "This is my top priority for [Q/year]"
- Tone shifts: sighing, laughing nervously, long pauses before answering
- Hedging language that implies understated frustration

**Example:** "My VP asked me in our last review why our response time to inbound leads is so slow. I need to show progress on this by end of quarter."

**Extraction rule:** Capture with context about who is applying pressure and any deadlines. Label as `personal`. Link to the business impact it connects to.

### Depth Classification

| Depth | Label | Meaning | Sales Implication |
|-------|-------|---------|-------------------|
| Layer 1 only | `surface` | Prospect is exploring, no urgency | Early stage, needs nurturing |
| Layer 1 + 2 | `qualified` | Real problem with measurable cost | Active evaluation, build business case |
| Layer 1 + 2 + 3 | `urgent` | Personal stake, timeline pressure | High intent, fast-track |


## Latent Demand Detection

Latent demand is pain the prospect hasn't articulated as a "problem" yet. They describe symptoms or workarounds without framing them as something to solve.

### Signals of Latent Demand

**Workaround descriptions** -- they built something manual to cope:
- "We have a spreadsheet where [someone] manually..."
- "Every [morning/week], [person] has to..."
- "We wrote a script that kind of does [X] but..."
- "Our intern/junior [does this by hand]"

**Acceptance of broken status quo** -- they've normalized the pain:
- "That's just how it works here"
- "We've always done it that way"
- "It's not great but it gets the job done"
- "We're used to it"

**Curiosity questions that reveal gaps** -- they ask about features solving problems they didn't explicitly name:
- "Can it also do [Y]?" (where Y is adjacent to the stated need)
- "Does it integrate with [tool]?" (reveals current stack friction)
- "How do other companies handle [X]?"
- "What if we wanted to [new capability]?"

**Casual complaints framed as jokes or asides:**
- "Don't even get me started on [X]" (then moves on)
- "That's a whole other conversation" (topic they're avoiding)
- Laughing while describing a painful process

**Extraction rule:** Flag these as `latent`. Include the verbatim quote. Add a note explaining what underlying pain the signal suggests. Do NOT present latent demand as confirmed pain -- label it clearly as inferred.


## Workflow & Stack Extraction

Capture the prospect's current operational reality. This maps directly to where DataGen can replace manual work or fragmented tooling.

### What to Extract

**Current tools mentioned:**
- CRM (Salesforce, HubSpot, Pipedrive, etc.)
- Enrichment tools (Clearbit, ZoomInfo, Apollo, Lusha, Clay, etc.)
- Outreach tools (Outreach, Salesloft, HeyReach, Lemlist, etc.)
- Data storage (spreadsheets, Airtable, Notion, etc.)
- Custom scripts or internal tools

**Manual processes described:**
- Any step a human does that could be automated
- Copy-paste between tools
- Manual research (LinkedIn browsing, Google searching, reading 10-Ks)
- Data cleaning, deduplication, formatting
- Spreadsheet manipulation

**Handoff points:**
- Where data moves between people or systems
- Where information gets lost or degraded
- Where bottlenecks occur ("then it sits in [place] until [person] gets to it")

**Volume and frequency:**
- How many records/leads/accounts they process
- How often (daily, weekly, per campaign)
- Team size doing this work

### Output Format for Stack/Workflow

```
### Current Stack & Workflow

**Tools:**
- [Tool]: [What they use it for]
- [Tool]: [What they use it for]

**Manual Processes:**
- [Process description] -- [who does it, how often, how long]

**Integration Gaps:**
- [Where data doesn't flow automatically]

**Volume:** [X leads/accounts per week/month]
```


## Output Template for Prospect Meetings

Use this structure for every prospect meeting summary.

```markdown
## Prospect Meeting: [Company/Person]
**Date:** [Date]
**Participant:** [Name, Role, Company]
**Duration:** [Length]
**Meeting Type:** Discovery / Demo / Follow-up

### Prospect Profile
- **Company:** [Name]
- **Role:** [Job function]
- **Industry:** [Vertical]
- **Company size:** [If mentioned]

### Pain Points

#### [Pain Point Title]
- **Depth:** surface | qualified | urgent
- **Surface symptom:** "[Exact quote]"
- **Business impact:** "[Exact quote or paraphrase with numbers]"
- **Personal stake:** "[Exact quote]" (if present)
- **DataGen relevance:** [Brief note on how DataGen addresses this]

[Repeat for each pain point]

### Latent Demand Signals

#### [Signal Title]
- **Type:** workaround | normalized-pain | curiosity-question | casual-complaint
- **Evidence:** "[Exact quote]"
- **Inferred need:** [What underlying pain this suggests]

[Repeat for each signal]

### Current Stack & Workflow

**Tools:**
- [Tool]: [Usage]

**Manual Processes:**
- [Process] -- [who, frequency, duration]

**Integration Gaps:**
- [Gap description]

**Volume:** [Scale of operations]

### Buying Signals
- **Timeline:** [Any deadlines or urgency indicators mentioned]
- **Budget:** [Any budget signals -- allocated, exploring, no mention]
- **Decision process:** [Who else involved, what approval looks like]
- **Champion potential:** [Is this person an internal advocate? Evidence.]

### Summary
[2-3 sentences: primary pain, depth level, and recommended next action]
```


## Extraction Rules Summary

1. **Always quote verbatim.** Do not paraphrase pain points. Use exact words from the transcript as evidence.
2. **Classify depth explicitly.** Every pain point gets a depth label: `surface`, `qualified`, or `urgent`.
3. **Separate confirmed pain from latent signals.** Latent demand goes in its own section, clearly marked as inferred.
4. **Capture the stack.** Every tool, manual process, and integration gap mentioned goes into the workflow section.
5. **Don't invent pain.** If the transcript shows no clear pain points, say "No explicit pain points identified" and focus on latent signals and workflow observations.
6. **Link layers when possible.** If a surface symptom connects to a business impact, draw the line explicitly (e.g., "Surface: 'need better enrichment' -> Impact: 'reps spend 3hr/day researching manually'").
7. **Flag workarounds as gold.** Manual processes and spreadsheet-based workflows are the strongest signals of latent demand for DataGen.
8. **Note what they did NOT say.** If a prospect described a complex manual process but never called it a "problem," flag this as normalized pain under latent demand.
