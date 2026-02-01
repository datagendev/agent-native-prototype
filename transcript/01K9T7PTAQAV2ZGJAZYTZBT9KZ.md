# Meeting: Yusheng Kuo and William Lee

**Meeting ID:** 01K9T7PTAQAV2ZGJAZYTZBT9KZ  
**Date:** 2025-11-12

## Summary

Id: 01K9T7PTAQAV2ZGJAZYTZBT9KZ
Title: Yusheng Kuo and William Lee
DateString: 2025-11-12T16:00:00.000Z
Organizer Email: yusheng.kuo@datagen.dev
Summary: Keywords: MCP, spec-driven development, middleware, agent automation, ROI, institutional knowledge, Action Items: 
**William Lee**
Brainstorm perpetual prediction market product and follow up with Yusheng Kuo for collaboration (45:40)
Share opinions on materials and feedback with Yusheng Kuo post-meeting (58:20)
Continue internal pushing and dogfooding of MCP gateways to drive adoption (56:00)

**Yusheng Kuo**
Obtain real user feedback to evaluate product-market fit honestly, disregarding sunk costs (57:50)
Coordinate follow-up discussions with William Lee regarding MCP’s developer experience and pilot opportunities (50:40)
, Shorthand Bullet: 💰 **Funding and Product Viability** (03:00 - 03:30)
Discussed initial funding and venture studio operations related to a decentralized exchange with $600K funding and profits reinvested into the studio.
Explored skepticism around product use case and the need to prove ROI quickly, especially by landing a pilot within a week to secure further interviews.
🔧 **Development Approaches** (10:00 - 15:00)
Delved into spec-driven development versus natural language automation for coding agents, emphasizing deterministic and robust automation flows for repetitive tasks.
Considered sandbox environments versus tool-based execution for agent code to balance security and flexibility depending on use cases.
📈 **Middleware Challenges** (15:30 - 18:30)
Agreed on the difficulty of demonstrating ROI for middleware developer tools like MCP but recognized the importance of measurable developer productivity improvements.
Debated MCP’s positioning challenges, as developers prefer customizing tools themselves and middleware vendors struggle to justify pricing or value.
🏃‍♂️ **Long-term Integration Journey** (18:30 - 23:30)
Reflected on the long and difficult journey of scaling integration and middleware solutions, likened to a 10-year marathon before IPO or exit.
Highlighted institutional knowledge capture challenges in enterprise, emphasizing repetitive patterns and tribal knowledge that are hard to document or version correctly.
📜 **Agent Operating Procedures** (24:00 - 30:00)
Discussed agent operating procedures (AOP), embedding SOPs as markdown-based tool calls updated via continuous integration, avoiding the need for new databases.
Questioned the value and implementation of agent 'memory,' noting current offerings are mainly retrieval rather than true memory, and argued memory should not merely reduce token usage.
💾 **File Systems and Memory Design** (30:00 - 34:50)
Shared that ephemeral and persistent file systems can both be integrated with agents, depending on use cases, to manage code execution and storage.
Stressed that memory design for agents should be neutral but configurable by developers, dependent on agent type such as personal assistants or persistent agents.
🛠️ **Middleware Tools and Emotional Endurance** (36:00 - 41:00)
Acknowledged existing middleware tools like Postman as difficult but valuable, and emotional endurance is critical for persisting in this space as it is currently a 'tarpit.'
Expressed skepticism about personal automation agents achieving mainstream success soon but noted potential in niche assistant types like research or calendar assistants.
🎮 **Integration with Entertainment Platforms** (41:30 - 45:30)
Agreed personal assistants will matter more when integrated with entertainment platforms, where user engagement drives adoption beyond developer interests.
Discussed attention economy aspects of modern UI with simple swipe gestures optimized for dopamine-driven user behavior.
📊 **Perpetual Prediction Market Brainstorm** (45:40 - 48:30)
Brainstormed building a perpetual prediction market with leverage using decentralized perpetual options as a high-potential product with significant revenue opportunity.
Consensus that apps focused solely on improving human willpower or inspiration generally fail, while those that assist with making jobs easier have greater chances of success.
🔄 **MCP Compatibility and Ecosystem Adoption** (48:40 - 55:00)
Debated the vertical versus horizontal stack approach to MCP compatibility and that middleware as a business model might not be optimal for MCP.
Concluded that MCP's success depends on ecosystem adoption, vendor cooperation, and addressing missing features like authentication, stressing timing and persistence as critical.
🐶 **Internal Adoption Strategies** (56:00 - 58:30)
Emphasized importance of dogfooding MCP gateways internally to foster adoption and improve product development with real use cases.
Planned to continue discussions and seek real feedback for product-market fit and potential pivoting strategies.
, Notes: ## **Product-Market Fit and Use Case Validation**

The core challenge identified is the **lack of clear product-market fit for MCP (Middleware for Composable Platforms)**, with consensus that its current use cases do not deliver immediate, measurable value to mainstream users (15:03).

- **William Lee and Yusheng Kuo agreed that proving ROI for MCP remains difficult** because the product mainly improves developer productivity, which is hard to quantify without explicit measurement (15:40).
    - William emphasized that once productivity improvements are measured, multiple stakeholders demand a share of the metric, complicating attribution.
    - Yusheng noted that positioning MCP as a developer tool is challenging since developers prefer building tailored solutions themselves.
    - Both concluded that MCP struggles as a middleware vendor because it sits between vendors and end users, limiting clear value capture.
    - They advised that MCP’s value is better realized when adopted by vendors rather than as a standalone middleware product.

- **The product’s limited appeal to everyday users was highlighted**, with William pointing out that non-developers do not currently find MCP compelling or see ROI from it (41:28).
    - Early adopters were mainly hardcore developers or workaholics, not mainstream consumers.
    - William predicted that MCP could gain traction only when combined with entertainment platforms, leveraging addictive, dopamine-driven user interactions (41:46).
    - The team agreed that MCP's current form lacks consumer engagement and that targeting professional white-collar workers with general personal assistants is premature and unfounded.

- **There is skepticism about the personal assistant use case** because it does not save significant time for most users and lacks a clear pain point to address (38:06).
    - William and Yusheng argued that focused tools like research or PowerPoint assistants have clearer value than broad personal assistants.
    - This reflects a strategic shift towards solving concrete problems over inspirational or generalized automation.

## **Strategic Positioning and Market Outlook**

The discussion framed MCP’s success as dependent on ecosystem maturity and long-term endurance rather than quick wins (53:33).

- **William stressed that MCP is in a “tarpit phase,” requiring psychological endurance and ecosystem readiness** before it can achieve commercial momentum (37:29).
    - He cautioned that widespread adoption depends on vendors and the broader ecosystem agreeing on standards and integrations.
    - The absence of core features like authentication in MCP protocols was noted as a barrier slowing market readiness (54:24).
    - Yusheng echoed that timing is critical, and the ultimate winner will be the one who perseveres through the slow build-up rather than the first mover (54:40).

- **Competitive insights highlighted the difficulty of building middleware unicorns**, with references to Postman’s long journey to success (36:08).
    - William shared that the journey to IPO and market dominance can take a decade or more.
    - This perspective shaped a patient, long-term vision for MCP rather than immediate scale.

- **MCP’s horizontal compatibility challenges and vertical stack integration remain unresolved** (48:59).
    - Yusheng raised concerns about how MCP can stack vertically without losing compatibility.
    - This technical challenge underpins uncertainty about MCP’s business viability (50:04).
    - William and Yusheng agreed that MCP may not be a good standalone business at this stage.

## **Product Architecture and Developer Experience**

The team converged on the approach of providing MCP as a **neutral, opinionated toolset that empowers agent developers to decide key behaviors** (32:21).

- **William argued that MCP should be flexible, letting developers define agent persistence, memory, and execution environments** based on use cases (32:21).
    - Persistent agents can maintain rolling memories; ephemeral agents can start fresh each session.
    - The middleware should avoid over-prescribing defaults to remain broadly useful.
    - This design philosophy balances developer freedom with necessary opinions to keep tools practical.

- **Technical details about agent operation included using markdown files for SOP updates and embedding actions triggered by CI/CD pipelines** (25:02).
    - This system keeps agent operating procedures automatically updated without redesigning backend databases.
    - It enables agents to retrieve the most current instructions as tools, ensuring operational accuracy.

- **Security and sandboxing are critical concerns**, as running agents in isolated VMs increases engineering complexity and risk (51:53).
    - William emphasized that sandboxing is important for security, but it complicates development.
    - The trade-off between integration as a tool versus a self-contained environment depends on agent use cases (14:06).

- **The team agreed that “memory” in agents is still largely a retrieval mechanism rather than true persistent memory** (29:16).
    - Current memory solutions reduce token usage but don’t fundamentally change interaction models.
    - Developers need to build custom memory behaviors depending on agent goals.

## **Product Roadmap and Business Priorities**

The conversation revealed a preference to **focus development on concrete, narrowly defined use cases rather than broad ambitions** like personal assistants or inspirational apps (47:43).

- **William and Yusheng suggested targeting specific industry niches with reusable components that solve real problems** (20:14).
    - This approach allows quick validation by pitching to a dozen companies and pivoting if interest is low.
    - Institutional knowledge capture and scaling beyond consultancy is a key challenge for these niche products.

- **They recommended prioritizing applications that make jobs easier rather than trying to inspire users** (47:43).
    - William noted that apps aiming to inspire people rarely succeed.
    - Practical tools with clear ROI are more likely to gain traction and justify investment.

- **The team debated the scalability of the venture studio model funded by profits from a decentralized exchange that raised $600k** (01:07).
    - William explained that the $600k was insufficient to run a venture studio directly but was supplemented by profits.
    - This contextualizes resource constraints and the need for pragmatic prioritization in product investments.

- **Short-term goals include landing pilot projects quickly to validate MCP’s use cases and deciding whether to continue investing in the platform or pivot** (00:26).
    - The team set a one-week target to secure pilots to enable further interviews and deeper engagement.
    - William emphasized the importance of honest feedback to decide whether to continue or refocus efforts (57:50).

## **Insights on Automation and Agent Development Philosophy**

The team shared nuanced views on **automation approaches, balancing spec-driven development against natural language coding** (10:55).

- **William advocated for spec-driven development as a robust approach for automation**, where deterministic, code-based flows reduce failure rates to near 99.99% (10:55).
    - Spec-driven automation is ideal for repetitive tasks with high reliability needs.
    - Natural language-based approaches offer flexibility but incur higher failure rates and latency.

- **They acknowledged that both approaches will coexist**, with trade-offs depending on brittleness tolerance and latency sensitivity (10:55).
    - Spec-driven flows excel where bugs are costly; natural language suits exploratory or low-stakes tasks.
    - William suggested tooling should allow agent developers to select their preferred model.

- **The concept of sub-agent creation as a future method for coding agents was discussed**, hinting at modular agent architectures that anyone can build (04:52).
    - This may enable more tailored, scalable agent ecosystems.
    - The team recognized this as theoretical but promising for long-term evolution.

- **William emphasized the need for tooling that integrates code execution within the agent environment**, supporting Python or other languages as tools (14:06).
    - This supports secure, sandboxed execution with flexible model calls.
    - The approach aligns with the vision of agents as orchestrators of multiple tool calls.

## **Market and Ecosystem Context**

The team positioned MCP and agent middleware within a broader landscape dominated by platforms focused on **gambling, dating, entertainment, and dopamine-driven products** (42:05).

- **William pointed out that these verticals capture massive revenue ($1 billion+ annual revenue in decentralized exchanges referenced) and user attention** (45:55).
    - He suggested that personal agents will gain mainstream appeal only when integrated with entertainment platforms.
    - The dopamine-driven interaction model (swipe left/right, etc.) is key to user engagement at scale (44:27).

- **They acknowledged that many AI automation startups fail due to lack of clear user pain points or engagement hooks** (37:49).
    - The team remains cautious about personal automation and assistant products without strong ROI.
    - Emphasis is on building tools that solve real, measurable problems in professional workflows.

- **The team recognized the importance of ecosystem standards and first-party support for MCP adoption** (56:12).
    - William pushed for internal dogfooding of MCP gateways to encourage external adoption.
    - Lack of vendor effort in standardizing MCP features like authentication hinders broader ecosystem growth.

- **The conversation concluded with a pragmatic view that the MCP market and product maturity will emerge over years, not months**, requiring patience and aligned ecosystem development (53:33)., Overview: - **Product-Market Fit Challenge:** MCP lacks clear product-market fit; current use cases aren't providing measurable value to mainstream users.

- **Developer Productivity ROI:** Difficulty in quantifying ROI for MCP since it primarily improves developer productivity; attribution complicates metrics sharing. 

- **Target Audience Concerns:** MCP's appeal is limited; non-developers find it uninteresting and don't perceive ROI; need for consumer-oriented engagement highlighted.

- **Strategic Ecosystem Positioning:** Success depends on ecosystem maturity and standards adoption; slow build-up is vital over quick gains.

- **Focus on Concrete Use Cases:** Development should target specific industry niches with practical tools providing clear ROI, avoiding broad ambitions.

- **Ecosystem Standardization Importance:** Internal adoption of MCP standards is crucial for external acceptance; maturity will take years, not months., Bullet Gist: 📉 Product-Market Fit Challenge: MCP lacks clear product-market fit; current use cases aren't providing measurable value to mainstream users.
📊 Developer Productivity ROI: Difficulty in quantifying ROI for MCP since it primarily improves developer productivity; attribution complicates metrics sharing.
🚫 Target Audience Concerns: MCP's appeal is limited; non-developers find it uninteresting and don't perceive ROI; need for consumer-oriented engagement highlighted.
🛠️ Focus on Concrete Use Cases: Development should target specific industry niches with practical tools providing clear ROI, avoiding broad ambitions.
🔄 Ecosystem Standardization Importance: Internal adoption of MCP standards is crucial for external acceptance; maturity will take years, not months., Gist: The meeting focused on evaluating the product-market fit of MCP and discussing strategies for overcoming challenges in its adoption and value delivery., Short Summary: The meeting centered on the challenges faced by MCP (Middleware for Composable Platforms) in achieving product-market fit, with participants William Lee and Yusheng Kuo highlighting the difficulty in demonstrating return on investment (ROI) due to its primary focus on enhancing developer productivity. They noted that MCP's value is better appreciated when integrated as a vendor solution rather than a standalone product, as mainstream users, particularly non-developers, find it unengaging. The conversation emphasized the need for a strategic shift towards concrete use cases and industry-specific applications rather than broad ambitions like personal assistants. Participants acknowledged that ecosystem maturity and standardization are critical for MCP's success, requiring patience and long-term vision as the product navigates its current challenges., Transcript Chapters: No transcript chapters

---

## Transcript

Id: 01K9T7PTAQAV2ZGJAZYTZBT9KZ
DateString: 2025-11-12T16:00:00.000Z
Privacy: link
Speakers: William Lee, yusheng kuo, William Lee
Sentences: William Lee: Coming because the whole night tomyong the weissy partner Toa Clavis just Diana.
yusheng kuo: Okay.
yusheng kuo: Okay.
William Lee: Yeah.
William Lee: That is all.
yusheng kuo: So you need test automation.
William Lee: Gotcha.
William Lee: Co founder.
William Lee: Oh, like yeah.
William Lee: Tell me what you did.
William Lee: Blah blah.
William Lee: Bloomberg decentralized exchange venture studio angel invest to teams to build certain projects.
William Lee: How much did you raise for that?
William Lee: And how 600k for the decentralized exchange.
William Lee: You know 600k is not enough to run a venture studio, right?
William Lee: No, no.
William Lee: Like to explain.
William Lee: The 600k was for our decentralized exchange.
William Lee: And then we made a lot of money from that.
William Lee: And then like the.
William Lee: The profit we made from that, we used it to run a venture studio.
William Lee: Now, have you personally angel invested in anything?
William Lee: Yes.
William Lee: How much have you personally invested?
William Lee: You're letting people know your net worth.
William Lee: No, Diana.
William Lee: Joe, take it as a sign that like he's lying or something.
William Lee: Just so like how much did you angel invest yourself?
William Lee: No, no, no.
William Lee: Hold on.
William Lee: Reluctantly.
William Lee: So how.
William Lee: How much liquidity did you have from crypto overall?
William Lee: Yo, like dude, this is none of your business.
William Lee: Like you shut the up.
William Lee: We really like the team but we're not sure about the use case of the product you're building.
William Lee: If you can land a pilot in one week, we'd love to interview you again next weekend.
William Lee: MCP doesn't exist yet.
William Lee: You're a woman we're building in that space.
William Lee: So like no one knows who composite was.
William Lee: Right, right, right.
yusheng kuo: Yeah.
yusheng kuo: Yeah but it's like infrastructure that eventually everyone expected to exist.
yusheng kuo: Yeah.
yusheng kuo: Hesitate.
yusheng kuo: Yeah.
yusheng kuo: What will be the future Authentication dedicated AI agent I probably wouldn't use mcp.
yusheng kuo: I would just like build rapper like myself like highly tailored like description latency server local client called server okay then support agent coding agent coding agent but same with the tool retrieval tool can deploy on mcp.
yusheng kuo: Would you how code the sub agent creation process could potentially be the future of how agent be created for everyone to create code to create something.
yusheng kuo: Then Kyle co the sub agent how the UI get in the IOR now Theoretical It's a primitive founder Codex Gemini cli and quite abuse when the personal assistant with transient compute milk resistant storage spin out whole VN technical deploy he changed out you got API call HTTP okay need a file system the code environment Sorry the code interpreter need a part of your environment has it should be part of like a tool interpreter Hasika tool has talent environment now.
William Lee: In my opinion the future agent in general and automation clockhole sub agent now just needs to declare the set of tools and what model you use Coding agent that you got going sooner home.
yusheng kuo: How to spell it?
William Lee: What was I.
yusheng kuo: Okay.
William Lee: Just a face on focus on spec driven development in my honest opinion in my honest opinion both will exist anyway.
William Lee: From my perspective it's what do you want to trade off in terms of brittleness Natural language to code automation flow generate this whole bug but it's a one time thing.
William Lee: Once you fix it hypothetically the automation product do you create it should function just as expected deterministically until some API gets deprecated or gets changed or something else breaks then process deterministic robust just had generated an outcome.
yusheng kuo: To me.
William Lee: Spec driven development clock code sub agent do something like maybe in the future it's not even.
William Lee: It's not even code it's just like you just write a piece of natural language to ensure that the agent does this thing for you.
William Lee: It's like an article within your can the article non deterministic temperature you set to zero the guardrail to the two call parameter generation and everything the chances of failure for that particular action is still going to be like orders of magnitude higher than it was executed through code.
William Lee: So exactly to your point when it's something that is like repetitive but it's not like super high repetition repeat.
William Lee: No Judah like the spec driven development Spec driven automation makes a lot of sense.
William Lee: You just need to make sure that it works a thousand times with a 99.99 probability internal.
William Lee: When there's more flexibility latency matters less.
William Lee: Yeah, that makes a ton of sense.
William Lee: No, it's like a sandbox like for the execute for the execution environment.
William Lee: Should that be just part of the agent itself and the environment that the agent is in or should it be like a tool?
William Lee: I think it would be both like to be very honest.
William Lee: Oh yeah, you call it as a tool whatever.
William Lee: No, you can execute the Python code you generate.
William Lee: Yeah, I think that makes sense.
William Lee: Well actually is not a good example Interface with other production software self contained a sandbox so in my opinion security the perspective environment you can call as a tool like anyway.
William Lee: Yeah so I think it just completely depends on the use case.
William Lee: The last thing I wanted to say just she's a woman so you go by your light woman released like a 22 so she's a trading application.
William Lee: So we're actually not where we haven't been dealing that much directly with NCP vertical agent.
yusheng kuo: Eventually need a manifestation agent that eventually will hide out to build an agent so people can feel the value.
yusheng kuo: Otherwise like there's no value.
yusheng kuo: There's no like immediate observable value.
William Lee: Exactly it's so hard to prove roi.
yusheng kuo: Yeah.
William Lee: ROI is so clear.
yusheng kuo: Yeah.
yusheng kuo: Like so straightforward.
yusheng kuo: Yeah.
William Lee: I sold 200,000 tickets for you this year, so you pay me $200,000.
yusheng kuo: Yeah.
William Lee: Doesn't MCP like when you're a middleware.
yusheng kuo: Yeah, we're middleware for sure.
yusheng kuo: Yeah.
William Lee: Oh, it's gonna improve your developer productivity.
William Lee: Do you measure that?
William Lee: No.
William Lee: Once you measure it, everyone and their grandmother wants a slice of the metric.
William Lee: Just its own PM the director of engineering.
William Lee: No, no, no.
William Lee: Like yeah, the MCB helped a bit but it was my policy or my management.
William Lee: Yeah.
yusheng kuo: It's like so hard to position because you couldn't position to dev dev developer tool.
yusheng kuo: Not really.
yusheng kuo: Because like dead people were like, oh I would just like develop my own like MCB tool if it's like only few of them.
yusheng kuo: And then it's also hard to put into the entry price perspective because who am I now?
yusheng kuo: So it's the third enterprise now vendor.
yusheng kuo: The vendor.
yusheng kuo: The Tigong.
yusheng kuo: The MCP level on top of.
yusheng kuo: Doesn't make sense for middleware to do that and then.
yusheng kuo: But what makes sense is actually the vendor needs to like do it.
William Lee: So you're building it from scratch.
William Lee: So like he went through the whole.
William Lee: Whole thing.
William Lee: Same thing.
William Lee: Integration software.
William Lee: Open source is IPO salesforce Billion.
William Lee: So going home.
William Lee: That's what I said.
William Lee: Like was it this difficult for you as well?
William Lee: He said yes.
William Lee: Just like IMO young, like he had to go through the same, you know, kind of.
William Lee: It's a good journey.
William Lee: Just it has to.
yusheng kuo: It should be the same.
yusheng kuo: It should be almost exactly the same.
William Lee: Yeah, it was a 10 year journey for him like before he actually got to got to the IPO and the exit and everything now that's it.
William Lee: So yes, just like building more in the application layer.
William Lee: AI data analyst actually still makes a lot of sense.
William Lee: Specifically like one specific type of data analysis that is like very difficult to do.
William Lee: Like all the stuff that you've already built and all the learning that you've done do that.
William Lee: I think it's like at least.
yusheng kuo: They.
William Lee: Tried Intercom, they tried Decagon Sierra, but that didn't work for them.
William Lee: Custom integration.
William Lee: You said custom domain knowledge something but they want something.
William Lee: It's just like the existing solutions just doesn't work.
William Lee: Now.
yusheng kuo: How do you scale not to be like almost like consultant and studio.
yusheng kuo: How do you draw the line there?
yusheng kuo: Which.
William Lee: Is a specific niche.
William Lee: Just in short, reusable components for other players in this industry doesn't make an industry very limited.
William Lee: But at the same time it also makes it very easy to validate whether you want to do it.
William Lee: Then just reach out to 12 companies.
William Lee: If all of them say off then you can just.
William Lee: Yeah, yeah, yeah, yeah, yeah, yeah, yeah.
William Lee: In three days you can just, you can just move on.
William Lee: It's double edged sword.
William Lee: Long term customer supporting.
William Lee: Starting point going to.
William Lee: How do you operationalize institutional knowledge?
William Lee: No one can replicate it.
William Lee: Institutional knowledge, it's not even written down.
William Lee: You don't even know.
William Lee: You don't even know like this until, until you, you've seen it like on the factory floor.
William Lee: How do you capture that.
yusheng kuo: Repetitive pattern that happens Also they portray as like a tribal knowledge.
William Lee: Right.
yusheng kuo: There's also memory PowerPoint and your record is super messy.
William Lee: Yeah.
yusheng kuo: This is discovery enterprise level.
yusheng kuo: It doesn't make sense to be living in md.
yusheng kuo: Right?
yusheng kuo: Like how diversion control.
yusheng kuo: You give version everything.
yusheng kuo: No.
yusheng kuo: How do you handle the conflict?
yusheng kuo: Right.
William Lee: Management the solution.
William Lee: Like to your point, he's very not bullish on Asian Ops.
William Lee: You only have to look at the historical outcome for ML Ops to see like there was like practically no company in ML Ops that like was like that big unicorn and that like that, that's like.
yusheng kuo: Like big market cicd.
William Lee: Like what does it.
William Lee: Why can't you use existing tools for that Customer support Asian rag pipeline to the internal documentation.
William Lee: Documentation update just embedding and everything.
William Lee: Since it's just running a CI cd.
William Lee: So the moment they trigger an update to their documentation, you also trigger a new set of embedding action.
William Lee: Chunking embedding action.
William Lee: So it took a while.
William Lee: Like okay, like it's trivial.
William Lee: The whole agent operating procedure.
William Lee: Literally the system prom a set of instructions that has to follow retrieve those steps.
William Lee: Existing sop.
William Lee: You should do it this way.
William Lee: You should do it this way.
William Lee: So now the only thing we're doing is we're cleaning it up into a markdown file.
William Lee: Now you're feeding it, we're feeding it as a tool call.
William Lee: So just every time the SOP gets updated, the AOP also gets updated.
William Lee: And then whenever the agent needs an aop it's only retrieving it.
William Lee: It's just retrieving it as a tool.
William Lee: So it just has the most up to date information anyway.
William Lee: The system to us we didn't find the need to redesign a database from the ground up for the agent itself.
William Lee: Baseline system prompt customer query retrieval.
William Lee: There's no relevant aop.
William Lee: Now when you get default behavior for like this is a loop you need to go through.
William Lee: It's also still just like updated directly through md.
William Lee: Under what circumstance would you need a Kind of like living, almost like living document.
William Lee: Like that part can either be done through tool or just like repeated deployment.
William Lee: Like for us we feel like actually most agents it's okay to yo eat the Indian just say like some small break before it's like updated continuously.
William Lee: Asian memory solution they're really focused on like oh bring your context with one existing Asian interaction into your next new agent interaction.
yusheng kuo: Yeah.
William Lee: Then like there are situations that you need that.
William Lee: So like when people use MEM0 like what is the.
William Lee: Like what's the ROI?
William Lee: It reduces your token usage.
William Lee: No, that's the completely wrong logic.
William Lee: When I use a memory solution I don't, I'm not like I shouldn't be.
William Lee: I shouldn't be using a memory solution to reduce token usage priority.
William Lee: I'm not sure that memory hasn't really landed yet.
yusheng kuo: Yeah, I don't think any of Asian memory are a real memory.
yusheng kuo: They are more like just still like a retrieval thing in the end of the day.
yusheng kuo: You know co interpreter context engineering service engineering external persistent storage interaction File system.
William Lee: Can be both like self contained file system.
William Lee: The stuff is like ephemeral long living the file like outside of that can also interact with persistent file storage systems that are online enterprise like infrastructure.
yusheng kuo: Had interrupt now the multi thread.
William Lee: Interrupt some.
yusheng kuo: Movement disappear how long like what's the lifetime Internal memory that has a shorthand.
William Lee: Ultimately we, we think it's depend.
William Lee: It's up to the agent designer to decide middle word design.
William Lee: Some handle to calling the national log as in their home.
William Lee: So the decision we came to was as a piece of dev tool or middleware you want to be as neutral as possible while still maintaining developer experience.
William Lee: You have to be opinionated about some stuff opinionators.
William Lee: So actually it makes your tool very difficult less useful.
William Lee: It should be up to the agent.
William Lee: Development also highly depends on the kind of agent you're designing.
William Lee: Agent persistent agent so you can just start A lot of times you just start a new conversation.
William Lee: So like when you wipe that it like makes a lot of sense.
William Lee: Personal assistant agent it connects with your gmail, connects with your slack, blah blah unifies all your message streams to imessage.
William Lee: So hey here's a summary of like all the messages.
William Lee: Rolling persistence automatically clear something out but you keep like a rolling memory of the last X number of hours or X number of whatever.
William Lee: But it's up to the agent developer to decide how they want to abstract that in my opinion.
William Lee: Right, right.
yusheng kuo: Yeah I think, I think that's a very good point.
yusheng kuo: Like like you provide the tool everything just a tool and then the age like if you do have an access for the developer to kind of decide whether they.
yusheng kuo: How they want to do it and then they kind of play around the limitation you provide.
William Lee: Yeah.
yusheng kuo: Maybe.
yusheng kuo: I. I haven't.
yusheng kuo: I haven't like running into like like a deep deep way more than governance Engineering the tooling context engineering the toolbox.
yusheng kuo: She managed soil MCP.
William Lee: Directionally.
William Lee: That.
William Lee: That definitely makes sense.
William Lee: Existing middleware company postman like middle word unicorn hard to crack.
William Lee: There's definitely a lot of value here and I still think there's a lot of value in middleware.
William Lee: Okay, let's retreat to.
William Lee: That's the sad part.
William Lee: That's the sad part.
yusheng kuo: That's a real developer like agent developer won't use mcp.
William Lee: No.
yusheng kuo: It just doesn't make a lot of sense on demand configuration.
yusheng kuo: It's a worthy investment to invest in the tool to fully optimize.
yusheng kuo: Exactly.
William Lee: To be honest I. I think it's a tarpit at some point it won't be a tar pit but I think it's still in the tarpit phase in my.
William Lee: In my opinion.
yusheng kuo: Enjoy personal automation.
yusheng kuo: None of them work out like Lucha fail cowork.
yusheng kuo: I don't pessimistic on that.
William Lee: Anyway this is my my take.
William Lee: It's the right answer.
William Lee: Vast vast majority of people male no Monk, what the.
William Lee: You need a personal assistant founder Even when we're a pre seed.
William Lee: Hey, we're getting 200k the personal assistant.
William Lee: Like managing the calendar.
William Lee: Yeah.
William Lee: It'S just like why the would you need it?
William Lee: It's like it doesn't actually save you that much time.
William Lee: Oh you're the CEO of Vercel Priorit.
William Lee: Someday.
William Lee: Someday like there will be some like some digital personal assistant good enough for these people to care about.
William Lee: Daily average Joe 9 to 5 Instagram TikTok.
William Lee: Like why the does he need a personal assistant?
William Lee: Like why like what would this person use the personal assistant for?
William Lee: Yeah, like that's actually the main issue with the idea.
William Lee: Even if you're targeting professional white collar consultants, investment bankers, lawyers like personal assistant research.
William Lee: I have a research assistant but it doesn't need to be a general personal assistant.
William Lee: It just has to be a research assistant because it just has to be a PowerPoint assistant organization.
William Lee: It's just like there's no use case for it.
yusheng kuo: Which I don't think that's useful at all.
William Lee: Agree with you then.
William Lee: So mcp like the first early adopters of MCP were developers.
William Lee: Workaholic.
William Lee: The perspective.
yusheng kuo: Yeah.
yusheng kuo: Yeah.
yusheng kuo: We're biased.
William Lee: Yeah yeah.
William Lee: So just A mcp send it all down mainstream.
William Lee: Just your everyday consumer will care about this thing or will see ROI from this.
William Lee: So when MCP is combined with entertainment.
yusheng kuo: Oh okay.
yusheng kuo: Yeah.
William Lee: That's when the big blow up will happen.
William Lee: Entertainment it's very restricted to per platform algorithm.
William Lee: Don't see you get addicted.
William Lee: This is what Instagram does the same thing doing does the same thing the whole.
William Lee: Yeah, we're interested against sex.
William Lee: The opposite of dating.
William Lee: OB whatever the OB just again gambling.
William Lee: Yo Gwenda new experience doesn't just like out of 8.3 billion people.
yusheng kuo: Yeah.
William Lee: The net amount of people.
William Lee: Oh would you just show you guys.
William Lee: Digital art is so fun.
yusheng kuo: It's like I never use me journey personally.
William Lee: Yeah.
William Lee: I mean I never use my advantage.
William Lee: I use other generation software.
William Lee: You know what is the future model?
William Lee: Just like in my opinion just maybe you get to a point where your hodu entertainment site they'll offer external facing MCP now somehow your personal agent can just go and collect the shit that it knows you'll be interested in for when you get off work at 5.
William Lee: Oh no.
William Lee: Like the moment that happens is like personal agents will.
William Lee: Yeah yeah, yeah, yeah yeah.
William Lee: That's just what the hypothesis obviously what an opinion probably that's where personal assistance will really come in like mainstream.
yusheng kuo: Touch swipe left or right?
yusheng kuo: Just swipe up right.
William Lee: Yeah.
yusheng kuo: This is the only signal you can get.
yusheng kuo: The only UI you can day connection.
yusheng kuo: That's how the moderns of society like work.
yusheng kuo: Yeah but like everything is just dopamine.
yusheng kuo: Like optimized like function is dopamine.
William Lee: Just compete for attention.
William Lee: Yeah, yeah yeah exactly.
yusheng kuo: I billboard everything like all the slogan like that's how you win.
William Lee: Prediction market.
William Lee: Prediction market with leverage.
yusheng kuo: Oh so dumb.
William Lee: I'll send you.
William Lee: So maybe what we should build is like a perpetual prediction market.
William Lee: Just perpetual options equity demand making option contractors autosity with defined endpoint options.
William Lee: Okay young Joe.
William Lee: We should do a perpetual prediction market with leverage open your contract.
William Lee: So need to like whether the wind decentralized exchange perpetual decentralization hyper liquid annual revenue over 1 billion.
yusheng kuo: 1 billion.
William Lee: Yeah yeah.
William Lee: $100 million per person is insane.
William Lee: Holy crap.
William Lee: It's like.
William Lee: I don't know.
yusheng kuo: Gambling, dating, like.
yusheng kuo: Like sex.
yusheng kuo: Like.
yusheng kuo: Like a 17.
yusheng kuo: Just focusing on 17 everything is like improving human will not work out.
yusheng kuo: Yeah yeah but.
yusheng kuo: But yeah it's yeah it's well don't do app to inspire people.
yusheng kuo: It never work out people is doing the job and make it job easier.
yusheng kuo: Then that will work out.
yusheng kuo: But inspire people.
yusheng kuo: No, never.
yusheng kuo: Yeah yeah.
yusheng kuo: Okay.
William Lee: Rebrand some Turbo McPoy.
yusheng kuo: Okay everything eventually if you are not a vendor that's the only value provided Area 0 sound again is it gateway but male compatibility.
yusheng kuo: How can your vertical stack the compatibility?
yusheng kuo: Because horizontal compatibility so sometime the gateway now in the gateway the feature middleware Middleware has a vertical.
William Lee: Just depending on the use cases.
yusheng kuo: Maybe MCP is just not a good business to be.
yusheng kuo: It's just going to be honest like just like that's it.
yusheng kuo: Yeah yeah.
William Lee: Since I were into agent building.
yusheng kuo: Okay.
William Lee: Yeah I'll brainstorm the song Joe like ping me on.
William Lee: On what?
William Lee: Oh yeah.
yusheng kuo: Thank you so much.
yusheng kuo: Like you're the first source I was like okay I feel confused here whether I should stick on a brilliant MCP or we should more focusing on providing whole environment.
yusheng kuo: So that's just from the dev experience perspective Develop a good cheer to enjoy experience deployment the production has been doesn't mean MCP use case by use case.
yusheng kuo: It's really hard to tell.
William Lee: Yeah.
yusheng kuo: If you just like a simple chat then yeah.
yusheng kuo: It's like it's not necessary to spin our whole vn.
yusheng kuo: Okay.
yusheng kuo: Everything can be interacted as a tool like a particular vn.
yusheng kuo: Yeah.
William Lee: Live in its own VM actually it makes the engineering harder as well.
yusheng kuo: And then the security is hell.
William Lee: Yeah it's hell as well.
yusheng kuo: Your product market fit no one yeah no one have a problem.
yusheng kuo: No one is like people crazy about that.
William Lee: Well I well I can almost on the market just MCP3 million like in.
yusheng kuo: Aggregate in my opinion Open source developers open source not in the revenue.
William Lee: There will be a day when it happens Marathon now eventually hit the gold mine.
William Lee: Psychological endurance.
yusheng kuo: Yeah too many opportunity out there.
William Lee: Too many opportunities out there distractions.
yusheng kuo: I'm just another just raising another 100 million being a sales AI sales people make another million.
William Lee: It will have its commercial moment like first principle.
William Lee: It just like makes sense.
William Lee: Something happened happens like not even MCP specifically.
William Lee: That's just a 2 falling in the middleware.
William Lee: That's just not now that's a now in my opinion just a pure psychological endurance.
William Lee: And you have to wait for the rest of the ecosystem to catch up as well.
William Lee: So every individual vendor also needs to actually play into the standard first party mcp.
William Lee: Now we have an MCP as well.
William Lee: But it's there's actually they don't have any.
William Lee: They don't put any effort into making them.
William Lee: Yeah.
yusheng kuo: Like authentication for example.
yusheng kuo: Like there's no authentication building.
William Lee: Yeah yeah.
yusheng kuo: Even even protocol itself can support it.
yusheng kuo: Just don't spend time like yeah yeah yeah.
yusheng kuo: It's like kind of it's.
yusheng kuo: It's.
yusheng kuo: Yeah.
yusheng kuo: Timing is.
yusheng kuo: Is critical.
William Lee: Yeah right.
yusheng kuo: Yeah yeah yeah but but at the.
William Lee: Same time the winner will be someone who emerged this wave just for like someone who stays a lot around long enough to eventually cracking you by the.
William Lee: Yeah but maybe not you've seen the Dongsi without baggage.
William Lee: It's I don't know.
yusheng kuo: It's all right.
William Lee: Yeah it's not necessarily who's the first.
yusheng kuo: One being in your wrist.
yusheng kuo: Yeah.
yusheng kuo: Because someone who may actually feel the pain more like more present pain.
yusheng kuo: You know because sometimes you are the builder you try to create a pain.
yusheng kuo: You don't try to fit yourself into the pain.
yusheng kuo: You don't directly feel the pain but someone who like directly feel the pain and then come out with the solution actually that yeah.
William Lee: Co founder is it brought this up a few times.
William Lee: Yo when so the MCP gateways in there how I was like pushing the team to do it.
William Lee: Yeah like proactively dog food like how can we expect like other people to adopt.
William Lee: Yeah yeah.
yusheng kuo: Who doesn't feel the pain like it's just like yeah now oh just genius idea.
yusheng kuo: It's unnecessary for most like 99 of your job validator.
yusheng kuo: We kind of like already passed that.
yusheng kuo: Yeah yeah it's a good feature but it's not like a major feature at all.
William Lee: Cool.
yusheng kuo: Yeah well keep it updated.
yusheng kuo: Yeah sorry I take an hour.
yusheng kuo: It should be supposed to be a 30 minute only.
William Lee: No.
William Lee: Did we take it?
William Lee: I don't think so.
William Lee: I thought we only took 30.
William Lee: Oh it's fine.
William Lee: No worries.
yusheng kuo: Sorry.
yusheng kuo: Yeah thank you.
William Lee: Well yeah.
yusheng kuo: London as soon as possible.
William Lee: Yeah yeah.
William Lee: Will you be an SF anytime soon.
yusheng kuo: Or let's see how how I see.
William Lee: Work out and yeah we'll try to.
yusheng kuo: Try to discuss and I think we really need to get back like some real feedback and be honest with ourselves not because we invest like forget about the same cost.
yusheng kuo: Right right.
yusheng kuo: Yeah.
William Lee: Applied albeit incubator.
yusheng kuo: Now.
William Lee: Applied any opinion on the material just like hit me up.
William Lee: Yeah.
yusheng kuo: Thanks a lot.
William Lee: All good man.
William Lee: Have a good one.
William Lee: Yeah take care.
yusheng kuo: Bye bye.
Title: Yusheng Kuo and William Lee
Host Email: will@aipolabs.xyz
Organizer Email: yusheng.kuo@datagen.dev
Calendar Id: b2bg47jv9j15vs1flk4hpapl44
Fireflies Users: yusheng.kuo@datagen.dev, will@aipolabs.xyz
Participants: will@aipolabs.xyz,yusheng.kuo@datagen.dev, yusheng.kuo@datagen.dev
Date: 1762963200000
Transcript Url: https://app.fireflies.ai/view/01K9T7PTAQAV2ZGJAZYTZBT9KZ
Audio Url: No audio url
Video Url: No video url
Duration: 58.83000183105469
Meeting Attendees: will@aipolabs.xyz, yusheng.kuo@datagen.dev
Cal Id: b2bg47jv9j15vs1flk4hpapl44
Calendar Type: google
Meeting Link: https://meet.google.com/ebd-soox-kpp
