## Claude Code Research: William Lee (AIPO Labs)
**Date:** 2025-11-12
**Participant:** William Lee, Co-founder @ AIPO Labs (will@aipolabs.xyz)
**Duration:** 58 minutes

### User Profile
- **Role:** Co-founder at AIPO Labs, former decentralized exchange founder, venture studio operator
- **Experience Level:** Advanced developer, infrastructure builder
- **Primary Use Cases:** Building agent infrastructure, middleware evaluation, MCP protocol assessment

### Usage Patterns
- Evaluating MCP as middleware/gateway for agent tooling
- Building customer support agents with RAG pipelines for internal documentation
- Using CI/CD workflows to trigger embedding updates when documentation changes
- Implementing SOP (Standard Operating Procedures) as markdown files fed to agents via tool calls
- Not redesigning databases for agents - using existing infrastructure with retrieval patterns

### Pain Points

**MCP Protocol Limitations:**
> "Real developer like agent developer won't use MCP. It just doesn't make a lot of sense on demand configuration."

- **Authentication Gap**: No built-in authentication in MCP protocol itself, even though the protocol could support it
- **Developer Adoption**: Professional agent developers find it more valuable to build fully optimized, custom tooling rather than use MCP
- **Value Proposition Unclear**: Hard to position - not quite a developer tool (devs will build their own), not quite enterprise (who pays?), not quite vendor-facing

**Middleware Business Model Challenges:**
> "It's so hard to prove ROI. Once you measure it, everyone and their grandmother wants a slice of the metric."

- Difficult to demonstrate clear ROI for middleware/productivity tools
- Attribution problem: PMs and directors will claim credit for productivity gains
- Market validation challenge: Too early for mainstream adoption
- Requires long-term endurance to wait for ecosystem to mature

**Ecosystem Maturity:**
- Vendors (Notion, Linear, etc.) aren't investing effort in their MCP implementations
- First-party MCP servers exist but have minimal effort/features
- Timing is critical - may be a "tarpit" phase currently

### Success Stories

**Customer Support Agent (Their Implementation):**
- Built custom support agent with RAG pipeline to internal docs
- SOP retrieval via tool calls (markdown files as source of truth)
- Documentation updates trigger automated chunking/embedding via CI/CD
- Agent Operating Procedures (AOPs) stored as markdown, retrieved as tools
- No need for specialized "agent databases" - existing infra works fine

**Agent Memory Approach:**
> "It should be up to the agent designer to decide. It depends on the kind of agent you're designing."

- For coding/chat agents: Ephemeral memory, fresh conversations make sense
- For personal assistants: Rolling persistence over X hours
- Memory solutions (like MEM0) haven't landed yet - still just retrieval
- Prefer developer flexibility over opinionated memory systems

### Feature Requests / Suggestions

**Code Execution Environment:**
- Debate: Should code interpreter be a tool or part of the agent environment?
- Conclusion: "It should be both" - depends on use case
- Security perspective: Sandbox as environment makes sense
- For production: Can call as a tool

**Middleware Strategy:**
> "You want to be as neutral as possible while still maintaining developer experience."

- Be opinionated about some things (DX) but flexible where it matters
- Provide tools/primitives, let agent developers decide how to compose them
- Don't force specific patterns (memory, persistence, etc.)

**Vertical Integration Opportunity:**
- Suggests building AI data analyst for specific, difficult analysis types
- Leverage existing infrastructure/learning to solve narrow, high-value problems
- Easier to validate (reach out to 12 companies, get feedback in 3 days)
- Reusable components within a niche industry

### Interesting Quotes

> "Spec driven development makes a lot of sense. You just need to make sure that it works a thousand times with a 99.99 probability."

> "The winner will be someone who emerged this wave - someone who stays around long enough to eventually crack it."

> "Timing is critical. The winner might not be the first one - someone who directly feels the pain and comes out with the solution."

> "Personal agents will really come mainstream when MCP is combined with entertainment - when your agent can collect content it knows you'll be interested in."

### Key Insights

**1. MCP is in "Tarpit Phase"**
- Too early for mainstream adoption
- Requires ecosystem maturity (vendors need to invest in their MCP servers)
- Success requires psychological endurance and long runway
- Historical parallel: ML Ops had no big unicorns, agent ops may follow similar path

**2. Developer vs. Consumer Split**
- Early MCP adopters are workaholics/developers (biased sample)
- Average consumers have no use case for personal assistants yet
- Real use case: Entertainment + content curation (when platforms offer MCP endpoints)
- Professional use cases are narrow: research assistant, PowerPoint assistant (not general assistant)

**3. Infrastructure Philosophy**
- Don't over-engineer: Use existing databases, CI/CD, markdown files
- Retrieval > specialized databases for most agent use cases
- Natural language specs work for low-repetition tasks; code for deterministic, high-repetition tasks
- Agent ops can leverage existing DevOps patterns (no need to reinvent)

**4. Business Model Warnings**
- Middleware is "hard to crack" - Postman succeeded but it's rare
- Integration software (like Mulesoft) took 10 years to IPO
- Need vertical application or clear ROI metric (e.g., "I sold 200k tickets for you")
- Avoid becoming consultant/studio - find reusable components in a niche

**5. Future Vision**
> "Entertainment is when the big blow up will happen. Platforms are restricted to per-platform algorithms to get you addicted. If your personal agent can collect content across platforms..."

- Personal agents will go mainstream when combined with entertainment/content
- Current problem: No use case for average person
- Future state: Agent curates cross-platform content based on your interests
- Dopamine optimization + agent curation = mainstream adoption

### Strategic Recommendations for DataGen

1. **Don't Over-Invest in MCP Gateway Yet**: William's team is "proactively dogfooding" MCP but admits "it's a good feature but not a major feature at all."

2. **Focus on Vertical Use Cases**: Consider pivoting to specific data analysis problems or narrow agent applications with clear ROI.

3. **Embrace Existing Infrastructure**: Don't build specialized agent databases or memory systems - show how to use existing tools (Postgres, CI/CD, markdown) effectively.

4. **Wait for Ecosystem or Build Vertical**: Either have endurance for multi-year middleware play, or pivot to vertical agent application with immediate value.

5. **Target Real Pain Points**: Find users who "directly feel the pain" rather than trying to create/anticipate pain points.
