# Meeting: Datagen X Alberto

**Meeting ID:** 01KB8EFR4YVD6TVS4B2XZV3S5N

## Summary

Id: 01KB8EFR4YVD6TVS4B2XZV3S5N
Title: Datagen X Alberto
DateString: 2025-12-01T22:45:00.000Z
Organizer Email: yusheng.kuo@datagen.dev
Summary: Keywords: Voice Interface, CRM Input, Field Sales, Data Enrichment, Modular Component Platform (MCP), Conference Sales, Action Items: 
**Yusheng Kuo**
Build a simple MCP integrated with Hotspot CRM to allow voice input for CRM updates and basic auto-enrichment, ready for internal testing and demonstration (58:05)
Develop a visualization/reporting website or dashboard to provide real-time summaries of sales data input via MCP to demonstrate usage impact and encourage adoption (53:10)
Coordinate prototype testing internally and with selected external companies attending upcoming conferences, collecting early feedback on workflow fit and usability (59:16)
After initial build, send documentation and development updates to stakeholders for alignment and feedback (59:36)

**Alberto Campora**
Support identification of potential test companies attending relevant conferences who can trial the MCP voice input tool and provide customer development insights (56:10)
Collaborate on scenario mocking and testing the MCP prototype internally and with small sales teams to validate concept and refine workflow (58:59)
Provide feedback on usability and feature improvements based on client consulting experience and interactions with field sales agents (48:14)
, Shorthand Bullet: 📊 **Market Segment Focus** (00:50 - 05:11)
Discussed market segment focusing on companies relying heavily on face-to-face sales activities where CRM data quality is poor and no GTM engineers are available.
Emphasized a need for faster, easier CRM data input and context extraction via voice interface.
🗣️ **Voice Interface MVP** (05:11 - 29:20)
Voice interface CRM input identified as a minimum viable product (MVP) to reduce admin burden on field sales agents and boost productivity during events.
Proposed MVP approach is to build an MCP integrated with Cloud and CRM enabling voice input to CRM without forcing users to download new apps.
📈 **Competitor Analysis** (10:18 - 12:00)
Existing competitors targeting event-led sales teams offer voice note capture but lack context enrichment and integration that improves data quality and insights directly with the CRM.
A large portion of companies do not fully utilize CRM enrichment tools or integrate external tools well, creating opportunity for a focused solution for field sales teams.
⏱️ **Real-Time Context Importance** (13:57 - 23:30)
Importance of capturing real-time context during conferences, including post-event data management and immediate response capability, highlighted as key to proving ROI to headquarters and sales leadership.
The pain of capturing accurate and timely data during high-contact events was emphasized.
🔍 **MVP Features** (29:20 - 41:58)
MVP would include simple voice interface and output that auto-enriches CRM entries, plus a visualization dashboard or report generator that summarizes sales activity impact daily.
Success hinges on deploying the MVP to selected test companies attending upcoming conferences.
⚠️ **Risks and Challenges** (45:08 - 48:13)
Recognized risks include potential resistance to CRM adoption by field sales agents and ensuring MVP delivers visible benefits quickly to avoid abandonment.
The solution must be easy to use for sales agents who have no time to manage complex tools.
🛠️ **Development Focus** (56:20 - 58:05)
Initial development focus will be building a simple MCP for Hotspot CRM users and testing internally and with selected early users before expanding to an app or more advanced dedicated platform.
Emphasized need for continuous customer development by engaging real sales teams and iterating the solution based on collected user data.
, Notes: ## **Voice-Driven CRM Input for Field Sales Teams**

The meeting concluded that a **voice interface for CRM input** targeting field sales teams can reduce admin burden and enhance data capture quality during events like conferences (00:05).

- **Alberto Campora identified a market segment** of companies with **5 to 10+ field sales agents** who rely heavily on CRM data but lack GTM engineers to manage data quality (00:03).
    - These teams face challenges capturing context while on the move, especially in industries like hospitality, retail, and construction.
    - Sales agents often meet dozens of contacts in a day, making manual data entry impractical.
    - A voice-based solution would allow faster, more accurate CRM updates without distracting from face-to-face selling.
    - This approach targets a less-served segment compared to existing AI tools focused on prospecting or automated data enrichment.

- **The minimal viable product (MVP) agreed upon** is a **simple voice UI** that lets salespeople talk to the CRM system, auto-enrich data lightly, and save it with minimal friction (00:18).
    - Yusheng Kuo and Alberto discussed building this MVP as an MCP (Modular Cloud Platform) component to integrate with existing CRM tools like Hotspot.
    - This MVP can be tested quickly by enabling voice input via MCP without requiring a dedicated app download.
    - Early tests will validate user adoption, workflow fit, and basic accuracy, with plans to evolve based on feedback.

- **Alberto emphasized the importance of real-time impact visibility** for adoption (00:40).
    - Users must see immediate benefits and understand the value of inputting data to avoid CRM adoption resistance.
    - A visualization or reporting tool integrated with MCP should summarize daily activity and impact to motivate consistent use.
    - This feedback loop is crucial because field sales teams face high time pressure and need clear proof that the tool helps them meet targets.

- **Yusheng suggested a phased rollout** starting with companies already using Cloud and Hotspot for easier integration and testing (00:34).
    - Narrowing initial customers who have compatible CRM and connectivity setups reduces friction.
    - Once validated, the team can build dedicated language models and apps to serve broader markets and improve accuracy.
    - Alberto agreed that testing internally and with pilot customers is essential to refine the solution before scaling.

## **Market Position and Competitive Differentiation**

The solution aims to differentiate by focusing on **field sales teams attending conferences and in-person meetings**, unlike competitors who mostly offer voice note recording without data enrichment (00:10).

- Alberto shared insights from conversations with event-organizing companies confirming a gap in the market for tools that both capture and enrich CRM data from voice input.
    - Existing tools focus on recording voice notes or basic CRM input but do not extract context or provide actionable insights.
    - The product would stand out by linking voice input with CRM updates and contextual data enrichment in a seamless workflow.
    - This helps companies measure conference ROI better by tracking leads and conversations in near real-time.

- The team recognized that many companies still rely on manual or fragmented workflows for CRM updates, causing data quality and adoption issues (00:16).
    - The product targets companies that have not fully integrated their CRM with external tools like Clay or ChatGPT.
    - By integrating voice input directly into the CRM ecosystem, the tool reduces overhead and increases timely data availability.
    - This market focus on smaller or less digitally mature sales teams offers competitive advantage as AI adoption grows unevenly.

## **Implementation Strategy and Technology Stack**

The project will begin with an **MCP hosted remotely using OAuth**, enabling quick installation and integration with existing CRM tools without complex onboarding (00:37).

- The MCP will leverage voice-to-text services such as Cloud and ChatGPT for transcription and basic entity recognition (00:19).
    - This approach avoids building a full-fledged app initially, speeding time to market.
    - The solution can be installed via a URL and used immediately by salespeople on mobile devices.
    - The team will develop a dashboard or website for users to visualize daily CRM updates and measure activity impact (00:53).

- Alberto stressed the need for a **robust feedback and reporting mechanism** that standardizes key questions to reduce mental load on sales teams (00:45).
    - This includes generating summaries of daily inputs and performance metrics automatically.
    - The reporting tool will help sales managers track field activity across multiple concurrent conferences or events.
    - It also supports accountability and helps justify conference investments through data-backed stories.

- The team acknowledged risks around CRM adoption and data quality, noting that failure to demonstrate clear benefits could lead to user rejection (00:50).
    - Early pilots and customer development with real field sales teams will inform product adjustments.
    - Alberto recommended offering incentives like lifetime memberships for pilot testers to encourage engagement (00:56).
    - The solution must be easy to use and visibly improve salespeople’s workflow to succeed.

## **Customer Development and Validation Plan**

The plan centers on **testing the voice-to-CRM MVP internally and with pilot customers at upcoming conferences** to gather feedback and validate product-market fit (00:36).

- Alberto proposed mocking conference scenarios to simulate real-world usage and refine user experience before broad rollout (00:38).
    - This allows controlled testing of voice input, data enrichment, and reporting features.
    - Yusheng agreed to build a simple MCP to enable immediate CRM updates via voice and start testing (00:58).
    - Pilot users will provide early feedback on usability, accuracy, and workflow integration.

- The team agreed to focus initial pilots on companies using Cloud and Hotspot to minimize tech barriers (00:39).
    - This targeted approach enables faster iteration cycles and clearer measurement of impact.
    - Insights from pilots will guide development of language-specific models and dedicated apps for wider adoption.

- They emphasized the importance of capturing nuances like accents and languages during testing to improve recognition accuracy (00:56).
    - Real user data will inform iterative improvements and error handling.
    - The team sees this as a long-term evolution from a simple MVP to a highly tailored field sales AI assistant.

- Alberto highlighted the high stakes for users, as failure to capture critical conference data impacts job performance and revenue (00:51).
    - This creates urgency to deliver a reliable, easy-to-use solution.
    - The proposed MVP approach balances risk and reward by starting small and scaling based on real demand and results.

## **Strategic Vision for Augmented Field Sales**

The conversation framed this product as part of a broader shift towards **augmenting, not replacing, human sales efforts with AI** to improve productivity and job satisfaction (00:54).

- Alberto shared that field sales roles are among the most stressful and data-heavy, making them prime candidates for AI augmentation.
    - By removing tedious data entry and enabling instant CRM updates, the solution aims to improve mental health and work-life balance.
    - This focus on human-centered AI aligns with market trends favoring augmented workflows over full automation.

- The product vision includes enabling sales managers to track field activity in real time, improving decision-making and resource allocation (00:30).
    - Providing an end-to-end process that connects offline conversations to CRM insights enhances team coordination.
    - This could transform how companies measure and optimize event-driven sales efforts.

- Alberto stressed that despite AI advances, human creativity and interaction remain essential, especially in industries requiring personal touch like hospitality and retail (00:24).
    - The tool supports these human efforts by reducing admin friction rather than replacing face-to-face selling.
    - This strategic positioning differentiates the product from prospecting tools focused mainly on lead generation.

- The team recognized the need for continuous customer development and iteration to align the product with real user needs and workflows (00:56).
    - They plan to use pilot feedback as the foundation for long-term roadmap decisions.
    - The goal is to build a trusted AI assistant that field sales teams rely on daily, driving adoption and business impact., Overview: - **Voice Interface Benefits:** A voice interface for CRM helps field sales teams update data faster and better during events.

- **Target Market Identified:** Focus on companies with 5 to 10+ field sales agents lacking resources to manage data quality effectively.

- **MVP Development:** A simple voice UI will enable salespeople to input data easily without needing a separate app.

- **Real-Time Visibility:** Users need to see immediate benefits to ensure adoption; a reporting tool will help track usage and ROI.

- **Phased Rollout Strategy:** Start testing with companies using Cloud and Hotspot for smoother integration and faster feedback on the MVP.

- **AI Augmentation Vision:** Product aims to support human sales efforts by reducing admin tasks, enhancing productivity without replacing personal interaction., Bullet Gist: 🗣️ Voice Interface Benefits: A voice interface for CRM helps field sales teams update data faster and better during events.
🎯 Target Market Identified: Focus on companies with 5 to 10+ field sales agents lacking resources to manage data quality effectively.
🚀 MVP Development: A simple voice UI will enable salespeople to input data easily without needing a separate app.
📊 Real-Time Visibility: Users need to see immediate benefits to ensure adoption; a reporting tool will help track usage and ROI.
🔄 Phased Rollout Strategy: Start testing with companies using Cloud and Hotspot for smoother integration and faster feedback on the MVP.
🤖 AI Augmentation Vision: Product aims to support human sales efforts by reducing admin tasks, enhancing productivity without replacing personal interaction., Gist: The meeting focused on developing a voice-driven CRM solution to aid field sales teams in enhancing data capture and reducing administrative tasks., Short Summary: The meeting explored the development of a voice-driven CRM input solution tailored for field sales teams, aiming to alleviate administrative burdens and improve data capture quality. Alberto Campora identified a target market of companies with 5 to 10+ field sales agents who struggle with data quality due to the absence of dedicated engineering resources. The team agreed on creating a minimal viable product (MVP) featuring a simple voice interface to facilitate easy CRM updates, which will be integrated with existing tools like Hotspot. Real-time visibility of data input benefits was emphasized to encourage user adoption, alongside a phased rollout strategy focusing on companies already using compatible CRM systems. The discussion highlighted the importance of augmenting human sales efforts with AI to improve productivity without replacing personal interactions., Transcript Chapters: No transcript chapters

---

## Transcript

Id: 01KB8EFR4YVD6TVS4B2XZV3S5N
DateString: 2025-12-01T22:45:00.000Z
Privacy: link
Speakers: yusheng kuo, Alberto Campora, yusheng kuo
Sentences: yusheng kuo: Forward.
Alberto Campora: Yeah, I mean.
yusheng kuo: So I think it's kind of murky.
yusheng kuo: Yeah, it, I don't know if it's just me, but it seems a bit murky.
Alberto Campora: Can you hear me?
yusheng kuo: Yeah, yeah, that's better.
yusheng kuo: Cool.
yusheng kuo: Better.
Alberto Campora: First.
Alberto Campora: Yeah, I was saying like to you Ellen.
Alberto Campora: Nice to meet you.
Alberto Campora: Nice to meet you.
Alberto Campora: Well, first I mean the reason.
Alberto Campora: Let's set the context.
Alberto Campora: I don't know what context you provided.
Alberto Campora: You should that in terms of like how we end up here is basically from your conversation.
Alberto Campora: We will start to explore some potential use cases based on you know, some charts that we had and you know, for me more observing in terms of like what the the market is is offering.
Alberto Campora: I thought that you know, we, we discussed a few use cases and I thought it would be interesting to buy something very, very specific.
Alberto Campora: I mean this is from a few iterations we had and I thought based on what I've been observing that there is a, there is a segment in the market of companies that have kind of are relying still rely on you know, face to face activities and where sales agent sales individuals don't really have much time first to ensure data quality in the CRM but at the same time they also rely a lot from the CRM in order to do the, you know, their work.
Alberto Campora: And if we think about you know, the rise of GTM engineers, all these things I think out there there is a majority of companies will never have even A lot of companies that have probably even more than five, six, even 10 sales agents will probably will never.
yusheng kuo: Have.
Alberto Campora: GTM engineer but they will still have a group of people that rely on the CRM their data and it's a group of people that will need to benefit from you know, have a faster understanding of context, faster understanding of faster processing of data.
Alberto Campora: And I think by discussing like why a lot of people are focusing on GTM engineering and obviously people that are advanced in terms of how to use AI.
Alberto Campora: I think there's a large portion of companies that are still rely a lot on the data but they probably would never have.
Alberto Campora: They will still they will need to rely on individuals on basically making most of their data without having someone orchestrating everything.
Alberto Campora: So you know, to the question, To the question what can be some interesting use case to solve and how we you know, can be something competitive within the market and kind of different.
Alberto Campora: That's basically that has been my, my insight of kind of moving away from where everybody focus and moving on a certain segment where maybe for a reason but I don't know a lot of cash with Tool don't really focus on.
Alberto Campora: And that's, that's why we are here.
yusheng kuo: Yeah.
yusheng kuo: So I think from at least what.
yusheng kuo: I provided to you and I think overall we want to at least for the first one it would be like.
yusheng kuo: A voice interface, CRM input.
yusheng kuo: Right.
yusheng kuo: In short.
yusheng kuo: And is that correct?
yusheng kuo: Like yeah, that would be the first one.
yusheng kuo: Right.
Alberto Campora: I mean, yeah.
Alberto Campora: Think about this term.
Alberto Campora: Like I think in my, my assumption are, you know, think about these two segments of word where basically in a world where AI will be more and more dominant on everything we do, I think there will, there will be more.
Alberto Campora: You know, on the other hand there will be more and more.
Alberto Campora: Some there are.
Alberto Campora: There was still a lot of industries, a lot of products where they will rely still probably invest more.
Alberto Campora: Including the fact that probably AI will help them to save money.
Alberto Campora: I think they will invest more on people leveraging human interaction.
Alberto Campora: So if you think about it, you know, in the world where like even field agent people going to conferences and have a stand and promoting their product, if before and still now maybe is a big investment for some companies, more we go in the future AI will make them save money, but those money will be spent on human interaction.
Alberto Campora: That's my assumption.
Alberto Campora: So more and more companies will invest in field agent that will have more time for the people and less time to actually do the admin.
Alberto Campora: By the other hand, we still need to capture the context from the human interaction.
Alberto Campora: So even today like, you know, even today like a few, you know, there are a lot of companies where basically people are going think about hospitality, think about you know, the beauty industry, think about the, even like the retailing industry.
Alberto Campora: Like so clothes and stuff like that.
Alberto Campora: Like people are meeting like with the buyers, the people like showing the product.
Alberto Campora: People go, you know, think about hospitality especially maybe in some countries over others, you know, think about like selling wines.
Alberto Campora: Like you're not going to sell wines to a bar through AI you need to have someone going there, show you the wine, tell you the story, tell you why you should have this wine or another and then you know, convince, you know, do you still need to an agent understanding a new restaurant is opening.
Alberto Campora: You need to go to a new restaurant.
Alberto Campora: Like this type of activity.
Alberto Campora: I, I don't think will will disappear.
Alberto Campora: If only they probably will will that there will be more chances to actually smaller team to be more productive through AI but you still need to go to a place.
Alberto Campora: You still have to visit maybe 10 restaurants in six hours including the travel.
Alberto Campora: So you don't really have the time to actually capture the data Capture everything.
Alberto Campora: And then these teams are still relying on very messy data.
Alberto Campora: And probably they are in a position where, you know, they spend too much time on, on, on that over, you know, actually enjoy the work and even like, you know, doing conferences, like if you go in a conference, you still, you know, you're like maybe five people in the boots.
Alberto Campora: You end up, you know, meeting 200 people in three hours.
Alberto Campora: So it's very hard to capture all these contexts.
Alberto Campora: So I think there is, I believe, and that's my assumption, a way like, okay, how out of a voice note, how can that trigger data input and data output?
Alberto Campora: So input the data and output through a contextual analysis and output the database on.
Alberto Campora: Okay, this is what you've done through you, but this is what your CRM tells you based on what you've done.
Alberto Campora: And that in a, in a sort of like kind of in an action that doesn't require a lot of admin from, from the sales agent, that will definitely help their life, I think.
yusheng kuo: Do you know if any competitors like doing this already?
Alberto Campora: I mean speaking with a company that was.
Alberto Campora: Speaking with the companies that is also organizing events, they told me that there are a few tools kind of very.
Alberto Campora: The target, kind of a event led sales team.
Alberto Campora: When I say event like you know, conference, conference maybe that basically helping them through voice note to maybe input the data.
Alberto Campora: But none of them is actually helping them to enrich the data or to extract context out of the data they input, which I think dies.
Alberto Campora: That is the dies that you know, the sort of the agentic layer.
Alberto Campora: They also will have their work.
yusheng kuo: But I don't understand so, so, so they, they, they, they, they are responsible for like turning those contacts into your CRM or it just kind of recording things.
Alberto Campora: No, they record things and they, maybe they have, they think they, I don't know how, you know, we can do more research.
Alberto Campora: But they input, maybe they help you to input to, to add, you know, to add your data in the CRM.
Alberto Campora: But they don't help you to, but they don't help you to.
Alberto Campora: Let's say I'm putting Alberto Campera.
Alberto Campora: But they don't enrich my data.
Alberto Campora: For example, they don't tell me where I'm from or what my company is doing.
yusheng kuo: But they might, they might have another, they might have another CRM tool that's already doing things like that, right?
yusheng kuo: Like clay.
Alberto Campora: Yeah, they might, but they might not, you know, of course, but you know.
yusheng kuo: Because once the data is in CRM.
yusheng kuo: They are like, I don't know, maybe.
yusheng kuo: A Southern Tool like doing different things, like all working.
yusheng kuo: I mean if, if the data is.
yusheng kuo: Already in CRM, I think that's the.
Alberto Campora: Yeah, I mean that's, that's depend of like what CRM they use and how they use it.
yusheng kuo: Of course.
yusheng kuo: Right?
Alberto Campora: Yeah, I guess.
yusheng kuo: Yeah.
yusheng kuo: So I think the key is like.
yusheng kuo: How do we capture things into crn?
yusheng kuo: And then I'm not quite sure like from crn, if there's still quite enough of a space to operate because there are so many.
yusheng kuo: Like most of the CRM tool already.
yusheng kuo: Have some kind of enrichment building.
yusheng kuo: Like adio.
yusheng kuo: Have the enrichment building haspa have some level of it.
yusheng kuo: And then there are a bunch of.
yusheng kuo: External tools trying to do that.
yusheng kuo: Yeah, I think we can, what we can try is probably just try to capture that from Voice into crn.
yusheng kuo: But that one seems very achievable.
yusheng kuo: But maybe.
yusheng kuo: Yeah, it's like it probably is not super hard to do.
Alberto Campora: Yeah.
Alberto Campora: For me like, for me there are two things because I can tell you like an exact use case of a few companies that help to go to conferences in the past.
Alberto Campora: So yeah, one thing is to obviously you can capture the data you put in CRM.
yusheng kuo: Yeah.
Alberto Campora: But the other thing is like why are you doing that be able to have.
Alberto Campora: Because think about like you have three days, okay.
Alberto Campora: Especially in the US like conferences are very long.
Alberto Campora: Okay.
Alberto Campora: Like there are big conferences very long.
Alberto Campora: Or you have.
Alberto Campora: Even if the conference is one day, you maybe travel over the three days.
Alberto Campora: Okay.
Alberto Campora: There's one thing you want to do is to make sure that you are be able to respond immediately to what happened during the conference.
Alberto Campora: Okay.
Alberto Campora: And I think even if you capture the data in the CRM, you still, you know, assuming that you are a large company still need to have.
Alberto Campora: Well again this is dependent.
Alberto Campora: Maybe you can build that on the CRM, but.
Alberto Campora: But maybe not.
Alberto Campora: So that is like how.
Alberto Campora: How you, you know, how you.
Alberto Campora: You gather context out of your input.
Alberto Campora: So for me it's like the use case.
Alberto Campora: Okay.
Alberto Campora: You.
yusheng kuo: You.
Alberto Campora: You be.
Alberto Campora: You're able to capture all the context into the CRM somehow.
Alberto Campora: I think how that work, you know, to.
Alberto Campora: To be discussed.
Alberto Campora: But then also, also the.
Alberto Campora: The platform is helping you.
Alberto Campora: Okay, you give me this context.
Alberto Campora: For example, what are similar companies we were before what.
Alberto Campora: What.
Alberto Campora: What happened in that.
Alberto Campora: And I know that these things are.
Alberto Campora: Can be built within the CRM but like most of companies they don't.
Alberto Campora: So if for me this is like kind of it's.
Alberto Campora: And also if they, even if they don't or they could we're talking about Team they are sales like field.
Alberto Campora: Field teams are kind of.
Alberto Campora: I don't know, I don't know how to say properly in English but kind of like lose at some time abandoned on their work.
Alberto Campora: It's almost like these guys, they have and girls they have a goal, they need to get leads, they need to close stuff and they can't really fast and require to the central team, oh, let's build this, let's build that.
Alberto Campora: Because maybe there are different teams across countries managed in different ways.
Alberto Campora: So it's almost how can you have like an end to end process that will help build teams to do a better job Then will this be integrated within.
Alberto Campora: Fully within a CRM?
Alberto Campora: Yeah, yeah, it's possible.
Alberto Campora: But like how many companies will be the companies that will for me like think about data, you know, clay.
Alberto Campora: Okay.
Alberto Campora: Like yes, you, you can, you can embed everything you're doing clay within your CRM.
yusheng kuo: Right.
Alberto Campora: But you, but, but a lot of companies don't.
Alberto Campora: So it's obviously like there are, there are ways that you can also do on the CRM.
Alberto Campora: But for me the use case like is this is something for specific for field teams of company and companies.
Alberto Campora: They are relying on fields for the revenues and they haven't built a CRM for them, you know, because, because otherwise like you can go into two solutions.
Alberto Campora: One is like you, you end.
Alberto Campora: That's something the first conversation we had, right.
Alberto Campora: Like you enter the company as a consultant and you help them to rethink about all their CRM and their, you know, their processes to.
Alberto Campora: Or what they want to achieve and maybe that would be part of it or you target one area of the work.
Alberto Campora: You give them like a one stop solution to improve what they do.
Alberto Campora: But again this is, this is all.
Alberto Campora: These are all my thinking and I'm not.
Alberto Campora: And it's not necessarily right.
Alberto Campora: I'm telling you what you know.
yusheng kuo: Yeah, yeah.
Alberto Campora: Understand why these are my assumptions.
yusheng kuo: Yeah, yeah, yeah.
yusheng kuo: I think I agree.
yusheng kuo: So in terms of like the minimal like valuable thing for them at the moment, it's just a simple voice ui.
yusheng kuo: Right.
yusheng kuo: They can just talk to the model and then get back to.
yusheng kuo: Okay, this is what the insight.
yusheng kuo: What you.
yusheng kuo: What the.
yusheng kuo: What the what the what the company or the.
yusheng kuo: What the contest name is and maybe auto enrich a little bit and save to the cio.
yusheng kuo: That would be the minimal valuable.
Alberto Campora: Yeah, that would be definitely something that I think for me something like that is something that eventually some companies will try, you know.
yusheng kuo: Yeah.
Alberto Campora: You know I'm surprised, I was surprised, I was surprised.
yusheng kuo: We know we did a bit of a research.
yusheng kuo: I think there are, there are few are trying to do that, to capture the voice to do that.
yusheng kuo: Even like a whisper flow.
yusheng kuo: Right.
yusheng kuo: I think they might actually eventually tap into this area too because that basically just integrate into your CRM and then.
yusheng kuo: Just like.
yusheng kuo: They actually read your email to know the entity, the name.
yusheng kuo: So they have better entity recognition of their dictation.
yusheng kuo: Yeah.
yusheng kuo: So I, I think, yeah, this is something.
yusheng kuo: One thing I don't know is just like, I don't know what's their workflow?
yusheng kuo: Like when do they actually write it down?
yusheng kuo: Do they actually try to like use voice?
yusheng kuo: No.
yusheng kuo: Or they would just like memorize everything in their head and then when they go home, they open their laptop.
yusheng kuo: Yes.
yusheng kuo: It's like.
Alberto Campora: Yeah.
Alberto Campora: So from my understanding there are two ways.
Alberto Campora: Like there's several ways.
yusheng kuo: Think about.
Alberto Campora: So some people just write it down on, on paper.
yusheng kuo: Yeah.
yusheng kuo: Yeah.
Alberto Campora: Other people, they might have like tablets where they are connected with hotspot and they take notes.
yusheng kuo: Mm.
Alberto Campora: Okay.
Alberto Campora: Other people, they, they, they, they, they write down maybe on the phone.
Alberto Campora: This is what really depending on like.
Alberto Campora: Yeah, think about also.
Alberto Campora: Think about also like your field agent.
Alberto Campora: You need to meet like 15 clients.
yusheng kuo: Yes.
Alberto Campora: And then between, you have to drive.
Alberto Campora: Like, you can't really fuss around with a bloody tablet.
yusheng kuo: Yeah.
Alberto Campora: You know, like also, maybe also this kind of behavior change in terms of maybe countries and markets.
Alberto Campora: But I can tell you like for example, and type of use case, like definitely when you are at a conference.
Alberto Campora: I've been a sales agent at a conference and I mean that's like years ago.
Alberto Campora: So you know, they were, they were not even the tablets.
Alberto Campora: But yeah.
Alberto Campora: So you know, you don't have time.
Alberto Campora: You know, like.
Alberto Campora: Yeah, it's like even sometimes when you, you know, when you think about, you know, when you go in conference and you see like these people, maybe they don't look busy.
Alberto Campora: Yeah, they don't.
Alberto Campora: But also the other hand that you can't really sit down like for an hour during the conference to take notes because maybe someone will come.
Alberto Campora: So you can't really, you know, you, you invest your time or standing there, right.
Alberto Campora: Like you don't have.
Alberto Campora: Yeah, you don't, you can't invest time on something else.
Alberto Campora: And also a conference charge you per person.
Alberto Campora: I mean depend of the conference.
Alberto Campora: But like sometimes they tell you, oh, this is like £10,000 for like you need to bring, you can bring only five people or you know, otherwise like £15,000.
Alberto Campora: So there is also like an ROI business model of how many people you bring There.
Alberto Campora: So if you bring someone only taking notes.
yusheng kuo: Yeah.
Alberto Campora: And also how can you take notes when like sometimes you have five people having five different conversations, you know, so it's, you know, I think it is for me as much as, like, I don't know.
Alberto Campora: I'm comparing this to the use case of deep research for perspective.
Alberto Campora: Like today we have so many tools that they are building their reputation and their, and their business model on that use case.
Alberto Campora: Right.
Alberto Campora: There are a lot of tools that only basically they, at the end of the day, they mostly do that.
yusheng kuo: You mean team research?
Alberto Campora: Yeah, they help you to research your problem.
Alberto Campora: And it's true, it's true, it's true.
Alberto Campora: They provide you value.
Alberto Campora: But yeah, a sales agent can still do a lot of good research.
Alberto Campora: Without that, you're just taking more time.
yusheng kuo: Right.
Alberto Campora: So for me it's the same like that, you know, conferences and people, conference will, will still do stuff.
Alberto Campora: They will still, they've been doing for 10 years.
Alberto Campora: They were still doing it.
Alberto Campora: But yeah, it's been always a pain.
Alberto Campora: Like if you speak to people at conference, like people are exhausted about that.
Alberto Campora: There is always that, that, that friction.
Alberto Campora: Like we capture the right data and we.
Alberto Campora: What about the email?
Alberto Campora: What about that email?
Alberto Campora: Like, oh, what about that?
Alberto Campora: What about the conversation people, you know, debriefs and like country briefs.
Alberto Campora: And then there you have these five people maybe out there for five days and you have the rest of the team and the headquarter and they ask you how is it going?
Alberto Campora: And then you have to prove that they rely on your investment in the conference.
Alberto Campora: How you prove it?
Alberto Campora: You know, like it's number, lead, number of conversation.
Alberto Campora: But then we know that you know that someone is, is gonna buy you after the conference, you know, it's gonna take time.
Alberto Campora: So how do you create attribution of that?
Alberto Campora: And for me, all of this is based on like the better understanding of the context of all your conversations.
Alberto Campora: So better you capture what happened better, you will be able to tell a better story.
Alberto Campora: That's my assumption.
Alberto Campora: It's the same as like, better you are, you know, you are better.
Alberto Campora: More data, better data.
Alberto Campora: You capture your perspective prospecting better.
Alberto Campora: You can do your first part of the job.
Alberto Campora: And it's true and that's how it works.
Alberto Campora: But even in prospecting with AI, you still need to put some effort.
Alberto Campora: It's not like you click it and then you know, you're done.
Alberto Campora: You sell stuff, you know, then you still need to put creativity.
Alberto Campora: You need to see.
Alberto Campora: And for me, it's the same.
Alberto Campora: I'm comparing Is the same thing.
Alberto Campora: Yeah, but it's just like two different use cases and two different type of people and these two different type of selling.
Alberto Campora: But no, no, no.
Alberto Campora: Is one is not necessarily less important than the other and some industry will rely and still rely a lot on think about the construction industry.
yusheng kuo: Like.
yusheng kuo: Yeah, yeah.
Alberto Campora: Like you still need to go to this conference.
Alberto Campora: You still need to do these people.
Alberto Campora: Like people AI will not.
Alberto Campora: If, if, if only it will probably willing people.
Alberto Campora: It will invest more.
yusheng kuo: Yeah, because I think the question, the question I had, I think Yuri Pro had the same question is like how.
yusheng kuo: How badly people want this type of product?
yusheng kuo: Like have you gauge it a little bit?
yusheng kuo: Like, like how bad.
Alberto Campora: Yeah, that's a good question.
Alberto Campora: I don't know.
Alberto Campora: But is that for me I'm, I'm putting like best and going back on the prospecting.
yusheng kuo: Yeah, but, but do you know, you know Phil self and then have you brought up this idea or maybe just like.
yusheng kuo: Yeah, just brought up this idea.
yusheng kuo: What do they feel about it?
yusheng kuo: They feel.
Alberto Campora: Yeah, I brought up this idea on definitely a few teams and they were excited but we talking about small teams.
Alberto Campora: So I don't know if it's, you.
yusheng kuo: Know.
Alberto Campora: I'm not, I'm.
Alberto Campora: I mean I'm taking that as a positive sign.
Alberto Campora: But you know, obviously it could be.
yusheng kuo: Color polite, you mean?
Alberto Campora: Yeah, but for me this, I'm starting more from, from the problem.
Alberto Campora: Like.
yusheng kuo: Yeah, yeah.
Alberto Campora: And I'm comparing that to also the prospecting part.
Alberto Campora: Like.
yusheng kuo: Yeah.
Alberto Campora: You know, the ability to capture data faster and better during your field activity is a problem.
Alberto Campora: Yeah, it's a fact.
yusheng kuo: Yeah.
Alberto Campora: Like it's, it.
Alberto Campora: Then will companies still exist and still continue to exist?
Alberto Campora: Like.
Alberto Campora: Yes, but again, you know, prospecting, like is there a problem?
Alberto Campora: Yes.
Alberto Campora: Can you still carry on without it?
Alberto Campora: Yes.
yusheng kuo: Yeah.
yusheng kuo: Yeah.
Alberto Campora: So.
yusheng kuo: But yeah, I agree.
yusheng kuo: It's like.
yusheng kuo: Yeah.
yusheng kuo: I mean you don't, you don't necessarily need the voice input.
yusheng kuo: Right.
yusheng kuo: But people enjoy.
Alberto Campora: Yeah, but that, yeah, but that's for me is because like it's, it's, it's one of those things is like as much as like prospecting is like when you start to see that actually provide you value because you start to using it, you start to use it better, you start understanding.
Alberto Campora: Okay.
Alberto Campora: Then you start to see the value, you know.
Alberto Campora: Yeah, because you know.
yusheng kuo: Yeah, I think, I think it's like.
yusheng kuo: It'S, it's, it's, it's, it's.
yusheng kuo: It sounds like a very reasonable thing that people want.
yusheng kuo: Like just I talk to someone and then right after you're talking to it.
yusheng kuo: You can just like Talk to like ChatGPT for example.
yusheng kuo: And then, and then everything just like being put in.
yusheng kuo: Yeah.
yusheng kuo: And then that will come to.
yusheng kuo: My second question is like how, what do you think?
yusheng kuo: If we say use, we first just create a simple MCP for example that connected to their CRN and then, and then we will help them to add that, install that and then they can.
yusheng kuo: Just use cloud to talk to them.
yusheng kuo: And then let them feel if there's something they want.
yusheng kuo: Do you think that will be enough to test the idea or it has.
yusheng kuo: To be a full fledged like app?
Alberto Campora: Because I don't know for me, I think for me an interesting part is that also because you we need to.
Alberto Campora: Because well, for me the clothes might be all right as long as like the interesting part for me is.
Alberto Campora: And I'm talking from a perspective because I talk when I spoke about these ideas, I spoke with the decision maker.
Alberto Campora: There are not the field agents.
Alberto Campora: That's why like for me the field agents are kind of solo wolves.
Alberto Campora: And then sometimes it's not the people we need to sell to.
Alberto Campora: Okay.
Alberto Campora: The people that we need to start, they're still the heads of sales, but we need to create layer because for me it's like it would be interesting to find and maybe like in a very simple way, like, because it's interesting to provide to the sales team to have a easier life, but also for the edge to also to know basically to have a.
Alberto Campora: Because if, if we create a way to import data to have basically.
yusheng kuo: If.
Alberto Campora: Every conversation that happened offline becomes something online, we are also able to measure the impact of what's happening and then so the head of sales is understanding in real time.
yusheng kuo: Yeah, yeah, but that's.
Alberto Campora: You know what I mean?
yusheng kuo: Yeah, that's also possible.
yusheng kuo: I mean I don't see like if you have an MCP there, it's also.
yusheng kuo: Very possible you can just retrieve those data in real time.
yusheng kuo: Like the salespeople would input that through the MCP and then the head of.
yusheng kuo: Cells can just retrieve whatever the data that's already been saved into the CRM through the MCP as well.
Alberto Campora: For me that is also super powerful because you're basically connecting.
Alberto Campora: You allow the team at the headquarter to understand what's going on.
Alberto Campora: And imagine companies that like five conference happening at the same time within a week.
yusheng kuo: Yeah.
yusheng kuo: And then we recently have, we added this power.
yusheng kuo: You can turn MCP into code.
yusheng kuo: So you can even ask a lovable created app that have the MCP as a component to show the data.
yusheng kuo: You can create a dashboard out of the MCP results.
yusheng kuo: Yeah, so yeah, I think.
yusheng kuo: And it can be easily configured to whatever dashboard they will want to.
yusheng kuo: So my question is, okay, so if we can provide SMCP as a very simple thing and now I would say the voice mode for Both Cloud and ChatGPT were quite good.
yusheng kuo: We can try to leverage that as the first step to just know if that's something they want and we can basically just sell them this MCP first.
yusheng kuo: And if you like the idea they want to continue, then we can.
yusheng kuo: And then they feel the limitation of using mcp.
yusheng kuo: Then we can try to build an app that dedicated for it.
yusheng kuo: I just don't know if that, that's something you, you think it's viable or, or you think it's.
yusheng kuo: There's some kind of limiting factor.
Alberto Campora: I think we, you need to think about something.
Alberto Campora: For me, the way to, to this to happen, like it has to be something that under the teams and to plug in and test like in the way I see it is like, you know, if we can build something where we reach out because we know where conferences are happening, we know the company that field, field agents, we know what the CRM they have and then we can say maybe we only like we focus only on companies that have spot because then you know, we can build something on the top of the ecosystem.
Alberto Campora: But then we can say, you know, because you want to try this at your next conference.
Alberto Campora: Yeah, you know, like it's kind of.
Alberto Campora: If it's something we were like we frictionless to test, it's probably like it's going to be.
Alberto Campora: Wouldn't say easy, but it's going to be possible to try to get, to identify some traction and some tester within, you know, certain amount of time because we know the companies are happening.
yusheng kuo: Yeah, I mean we can.
yusheng kuo: I, I think nowadays because so many.
yusheng kuo: People have follow like in their, in their, in their, in their, in their phone.
yusheng kuo: Right.
yusheng kuo: So I, I would say it's probably even more precisionless.
yusheng kuo: Like we can just like show them the MCP we created and, and then they can just talk to them and then, and then we can showcase.
yusheng kuo: Okay, I can just talk to you.
yusheng kuo: And now after we talk to you, like I will already like have my CRM updated just using the cloud as a platform to do that instead of like asking them to download a new app.
yusheng kuo: And then because the MCP can just be like installed through a URL so they can just, if they have cloud, if we say, okay, we narrow down to customer who Use Cloud.
yusheng kuo: Who has cloud?
yusheng kuo: And also use Hotspot, for example, and we can immediately help them to add their hotspot.
yusheng kuo: So I don't know.
yusheng kuo: Yeah.
yusheng kuo: If that, that's something that.
yusheng kuo: To you.
Alberto Campora: Yeah, no, no.
yusheng kuo: Where do you see the friction is?
yusheng kuo: Yeah.
yusheng kuo: Yeah.
Alberto Campora: I mean, for me, it's hard to say.
Alberto Campora: We need to.
Alberto Campora: The only way is to test it.
yusheng kuo: Yeah, yeah, yeah.
yusheng kuo: Because if you want, I mean, do you know when's the next conference?
yusheng kuo: We can create an MCP just for that and then let people see how they can just like use the call and then talk to them and then like get the, get the CRM updated immediately.
Alberto Campora: Yeah, for me it's like, it's, it's interesting to understand, like if we want to do this, how we.
Alberto Campora: We gonna.
Alberto Campora: We.
Alberto Campora: We know, we organize this team.
Alberto Campora: That's it.
yusheng kuo: Yeah, yeah, yeah.
Alberto Campora: So how I'm interested to, to, to.
Alberto Campora: To, you know, to help, but like, you know, like, for me, like all this question, like, I don't have answers, but I'm happy to find out.
yusheng kuo: Yeah.
Alberto Campora: You know.
yusheng kuo: Yeah.
yusheng kuo: I think what we can do is we can provide a very dedicated, like hotspot CIM that's specific with all the tool that's very specific for the, for the field sales engineer and field salespeople.
yusheng kuo: Yeah.
yusheng kuo: So they don't even need to trigger the word.
yusheng kuo: They just need.
yusheng kuo: Yeah.
yusheng kuo: And you can test it.
yusheng kuo: You can just talk to Cloud and see if that actually give you the right answer.
yusheng kuo: And actually the MCP ui also, you can provide the UI in accessory in Cloud, but it hasn't been released yet.
yusheng kuo: And, but even without that, you can still see the answer of the update and.
yusheng kuo: Yeah, if we can create that for.
yusheng kuo: You and you can test it and maybe you can tell us if it's reasonable.
yusheng kuo: I don't know.
yusheng kuo: What do you think about it?
yusheng kuo: We would just create a MCP that's hosted remotely using OAUTH of.
yusheng kuo: So you don't, you don't even need to go through all this mcp.
yusheng kuo: Hell, it would just like turn on mcp, add the URL and add it.
yusheng kuo: That's it.
yusheng kuo: Yeah, I mean, you can test it.
yusheng kuo: And then you can immediately test it.
Alberto Campora: Yeah, yeah, I think it will be.
Alberto Campora: For me, it will be an interesting thing to test.
Alberto Campora: Like if we build like, you know, a landing page around it and then we, we kind of present it as something it will be in, you know, first.
Alberto Campora: I think, you know, we can even test ourselves, right?
Alberto Campora: Yeah, because we can.
Alberto Campora: Yeah, we can mock.
yusheng kuo: Yeah, we have cloth.
yusheng kuo: Yeah, yeah, yeah.
Alberto Campora: We can mock the scenarios, you know and then you know, by mocking the scenarios we can also kind of create a demo and you know and demonstration to.
Alberto Campora: To.
yusheng kuo: To share.
Alberto Campora: Yeah, I mean that made up.
Alberto Campora: I don't know.
Alberto Campora: I have.
Alberto Campora: I have the feeling that obviously I don't.
Alberto Campora: I don't know.
Alberto Campora: I don't have all the answers but is something that.
Alberto Campora: Because it will speak to a very specific use case.
Alberto Campora: A very specific type of company.
Alberto Campora: Slightly different than target other tools.
yusheng kuo: You mean they might not have Cloth for example.
Alberto Campora: Yeah, which is definitely a risk.
Alberto Campora: But also I think we are reaching a state.
yusheng kuo: But I think if we want to just test out like okay, this voice input will help their life, then we can first test on people who have cloud.
yusheng kuo: Right.
yusheng kuo: That should give us the same answer.
yusheng kuo: And then we can say okay, this is useful.
yusheng kuo: And then we can build an app for people who doesn't have claw.
yusheng kuo: Yeah, that's what I feel that kind of a progress.
Alberto Campora: I don't think we need to build anything special for me is more like the only risk.
Alberto Campora: Well the one thing they will be interesting somehow.
Alberto Campora: It doesn't have to be in a separate app, whatever.
Alberto Campora: But we need.
Alberto Campora: Because for me the only limitation of.
Alberto Campora: Of cloth or you know the traditional UI that I kind of.
Alberto Campora: Whatever happened get get bored, you know, get.
Alberto Campora: Get kind of get lost in a black hole.
Alberto Campora: Like I don't know how.
yusheng kuo: Like.
Alberto Campora: Because if you start to.
Alberto Campora: Because the question is like imagine like you using this thing for a day.
Alberto Campora: Five people using this for a day.
Alberto Campora: How do you have something at the end of the day that tells you this is actually what have you done through this?
Alberto Campora: And this is like the impact you had.
Alberto Campora: Because for me I'm doing comparison with clay.
Alberto Campora: Right.
Alberto Campora: The difference between running a line and clay where ultimately you might get the same results of what you will get through a cloth chart is that the results still there on that table.
Alberto Campora: You can easily say okay, I run hundreds.
yusheng kuo: Oh yes.
Alberto Campora: So you know what I mean?
Alberto Campora: Like so you still.
yusheng kuo: You can.
yusheng kuo: You can see all the data that we put in.
yusheng kuo: In Hotspot.
yusheng kuo: Right.
yusheng kuo: So Hotspot have like mobile app.
yusheng kuo: Right.
yusheng kuo: But they don't.
Alberto Campora: Yeah, yeah.
Alberto Campora: We still.
Alberto Campora: We need to find a way that maybe even threw up spot.
Alberto Campora: But we need to be clever on showing on.
Alberto Campora: On be able for someone that is using it to immediately see the impact of it.
Alberto Campora: Even if it's the data they are entering up.
Alberto Campora: Spot have a different colors.
Alberto Campora: You know what I mean?
Alberto Campora: Like.
Alberto Campora: Like whatever it is we need to.
Alberto Campora: Because if.
Alberto Campora: Because otherwise the risk is that we.
Alberto Campora: They're not gonna.
Alberto Campora: They're not gonna see the value of using it versus using cloth.
Alberto Campora: Just cloth without, you know.
yusheng kuo: But how do they use cloth to do it without rmcp?
Alberto Campora: I don't know.
Alberto Campora: Because they're gonna say, oh, well, we.
Alberto Campora: Because the risks can be like, oh, we.
Alberto Campora: Well, we have.
Alberto Campora: Yeah, we have ChatGPT3.
Alberto Campora: We're using it.
yusheng kuo: Yeah.
yusheng kuo: And then, I mean, if they.
yusheng kuo: Even if they use chargeability and then.
yusheng kuo: Be able to do whatever we want to let them do, then.
yusheng kuo: Yeah, then they should use chargeability, I think.
yusheng kuo: I mean, our MCP should provide the differentiation value.
yusheng kuo: Otherwise.
yusheng kuo: Yeah, I mean, I mean, I. I.
yusheng kuo: Just don't think how value should be relied on.
yusheng kuo: We can show the color of the.
Alberto Campora: No, color is an example.
Alberto Campora: Don't take me literally.
Alberto Campora: Like, okay, I'm saying, like, we need to.
Alberto Campora: It's like somehow if some.
Alberto Campora: That whatever it is, even if it's through clothes is used for a day, we need to find a way to show, okay, what happened.
yusheng kuo: Yeah, yeah.
yusheng kuo: I mean, we could have a tool to generate.
yusheng kuo: Just say, what have we.
yusheng kuo: What have I done through our mcp?
yusheng kuo: And that tool would just generate a report of what you've done with this MCP today.
yusheng kuo: Yeah, that should be quite straightforward to do.
yusheng kuo: So you can just say, hey, okay, yeah, give me a summary of today's input.
yusheng kuo: And then it would just generate things.
yusheng kuo: The nice thing, I think through call is you can continue to ask the question, like, say, what have I done today?
yusheng kuo: What should I be improved?
yusheng kuo: So on and so forth.
yusheng kuo: It's just like, you can just continue to use cloud and then the context from things we put into our mcp.
yusheng kuo: Yeah.
yusheng kuo: And then we can pull data.
yusheng kuo: Yeah.
Alberto Campora: For me, for the build teams, I will almost making this kind of additional question as standardized as possible, because I think the sales team has.
Alberto Campora: Has no time to think about this stuff.
yusheng kuo: Okay.
yusheng kuo: Yeah, yeah, yeah.
Alberto Campora: You know, like, they want answers and they want to be able to say, bam, boom, boom, beam, boom, boom.
Alberto Campora: And they know because ultimately they have one goal.
Alberto Campora: You know, they.
Alberto Campora: Ultimately the bottom line is how they survive.
Alberto Campora: You know, it's not like, yeah, yeah, GTM engineer, like, oh, we did this and blah, blah, blah.
Alberto Campora: We integrated like we did, you know.
yusheng kuo: Yeah, yeah.
Alberto Campora: You know, for them, it's like it's one day they're like, they, they, they, they, they.
Alberto Campora: You know, the rest of the world doesn't exist.
yusheng kuo: Yeah.
Alberto Campora: You know?
yusheng kuo: Yeah.
Alberto Campora: Like I'm telling you, my friend, My friends are filled.
Alberto Campora: They work like their sales field.
Alberto Campora: Sales in hospitality.
Alberto Campora: Like, no, there are no prisoners.
yusheng kuo: So what exactly they want for them?
Alberto Campora: They just want to just have a.
yusheng kuo: Yeah, I know, but like, what do they want from this tool?
yusheng kuo: I guess.
Alberto Campora: Well, they want to have it.
Alberto Campora: They want to reduce as much as possible the data inputs, but they also rely on the data to do a better job.
Alberto Campora: So it's almost like Sheeter.
yusheng kuo: Sorry, let me refresh.
yusheng kuo: So what's the issue of building an MCP in cloud?
yusheng kuo: Would say, like, if they have cloud.
yusheng kuo: Right.
yusheng kuo: So what was the issue?
yusheng kuo: If we are using MCP in cloud for them to do that, what are the extra effort they need to suffer compared to building that app?
yusheng kuo: Compared to using an app?
yusheng kuo: Like what.
yusheng kuo: What's the extra effort they need to put in by not using.
yusheng kuo: By.
yusheng kuo: By using Claw with mcp?
Alberto Campora: What the actual.
Alberto Campora: Well, the.
Alberto Campora: As I said, like, at some point they need to prove that they need to understand the impact of what.
Alberto Campora: Of what happened by using what they've been using it, what's.
Alberto Campora: What's been resolved.
Alberto Campora: And also having something, having if also whatever they use has been helping them to inform the rest of the company in real time what was happening.
Alberto Campora: It will also remove from them the need of like updates and say what's happening and why it's happening.
Alberto Campora: Like this is like, it's kind of like removing.
Alberto Campora: But.
yusheng kuo: But why cloud couldn't do that.
yusheng kuo: I think my question.
Alberto Campora: I'm not saying couldn't, I'm saying like, oh, okay, yeah, I'm not.
yusheng kuo: I think my question is like, why, like, can.
yusheng kuo: Okay.
yusheng kuo: The question is, can we use McP as our MVP first?
Alberto Campora: Yeah, I'm not against.
yusheng kuo: Okay, okay, okay, okay.
yusheng kuo: I was trying to understand this.
Alberto Campora: No, no, I'm not against it.
Alberto Campora: I'm just saying, like, if also.
Alberto Campora: I'm saying if also.
yusheng kuo: Okay.
Alberto Campora: Like, yeah, yeah, if also.
Alberto Campora: There is a way to make sure that even in MVP we can prove we can showcase the impact of using it.
yusheng kuo: Yeah, yeah.
Alberto Campora: It will also help to demystify, I think the use of MCP for this kind of activity.
Alberto Campora: I think it will help also to basically have the adoption, I think.
Alberto Campora: Yeah, because for me, I think if you tell.
Alberto Campora: If you made them a promise, you know, but then at the end of the day they don't understand.
Alberto Campora: You know, bear in mind that these people are still not, not everyone, but there is, there is still like a high friction of CRM adoption in the field sales world, you know, like, so we are talking to them about something that, you know, it's even more advanced.
Alberto Campora: Right.
Alberto Campora: These people, they still discussing about how to use upspot, how to, you Know why using a spot why is important.
Alberto Campora: Like, you know, bear in mind this.
Alberto Campora: So we need to make sure that if we offer them something else, they need to have a sense of why it's important to use it.
Alberto Campora: I'll help them because otherwise they're not going to use it.
Alberto Campora: Yeah, that's, that's what I mean.
Alberto Campora: Like if they don't see the impact.
Alberto Campora: And that's why, that's why, that's why the CRM.
Alberto Campora: The adoption of CRM is so hard for the field sales team.
Alberto Campora: Because the problem of the CRM is that unless everyone is using it, not everybody will get impact.
Alberto Campora: Right.
Alberto Campora: So if someone doesn't use it and then the other one, it does, you know, see the other one is not use it.
Alberto Campora: Like, oh, why, why I should spend time on this when ultimately I'm gonna be anyway, so I'm doing stuff as I want.
Alberto Campora: So if we don't show them that is helping them and how immediately they're gonna, they're gonna be resistant.
yusheng kuo: Yeah, I see.
Alberto Campora: You know.
yusheng kuo: Yeah, we can, we can add the visualization tool to help them to like.
Alberto Campora: Something to show them, like, okay, you, you be, you usually, you know, you've been spending, you know, this is, you know, to prove them that, you know, actually you haven't.
Alberto Campora: Because the worst case scenario will be we made them a promise.
Alberto Campora: I'm telling you, the worst case scenario.
Alberto Campora: So the worst case scenario is like, we made them a promise.
Alberto Campora: They haven't been used any pen and paper, they haven't been using any tablet, and they've been relying on what we offer them to make the most of the conference.
Alberto Campora: Right.
Alberto Campora: So it's a big, it's a big promise.
yusheng kuo: Yeah.
yusheng kuo: Right.
Alberto Campora: And if it doesn't work, they're.
Alberto Campora: Yeah, but they're like, they're, they're as, as.
Alberto Campora: Because they're gonna, they're gonna be as individuals, not the company.
Alberto Campora: It's their job.
Alberto Campora: They're gonna be fired.
yusheng kuo: Understand?
Alberto Campora: Yeah, you know?
Alberto Campora: Yeah, that's what I mean.
Alberto Campora: You know, it's like we, we talking to people.
Alberto Campora: They are there.
Alberto Campora: I think they're, they're on the edge and they're like, they need, like they, they need definitely.
Alberto Campora: I think when we talk about augmented AI, for me, their role is the role that probably should benefit the most, but obviously is, is the role where if AI up, they are probably the most up because they are last people on the chain.
yusheng kuo: Yeah, you know.
yusheng kuo: Yeah, I understand.
yusheng kuo: Yeah, yeah.
yusheng kuo: The stake there.
yusheng kuo: Yeah.
yusheng kuo: I think we can start by just testing ourselves and then you can Let them test it on the go and see how comfortable it is and how convenient it is.
yusheng kuo: And then I think we can start from here and then we can have a visualization tool.
yusheng kuo: Say like, okay, show me what you've got.
yusheng kuo: And then we just visualize everything.
Alberto Campora: Yeah, it's something that, you know, we don't have to over complicate, but it's something that also I think will provide a bit of confidence because then if they're using it, then we can improve it.
Alberto Campora: Because if they're not using it, we will never.
Alberto Campora: Yeah, because the only problem with this is like, it's, it's.
yusheng kuo: We can, we can have a, we can have a website that can log in and they can see all the input they have, like through the mcp.
Alberto Campora: Yeah, yeah.
yusheng kuo: That website could just be the visualization part.
Alberto Campora: Yeah, because I'm thinking about this now.
Alberto Campora: Like, this is like all coming up by talking loud.
Alberto Campora: Like it's definitely compared to prospecting, this is more high risk, high reward.
Alberto Campora: Because prospecting, you know, prospecting like through AI, like you get it wrong, you're not gonna, it's not, it's not gonna be a big deal, you lost time.
Alberto Campora: But like if this, you rely on this to, to capture your data, you don't capture like you are.
yusheng kuo: Yeah, yeah, yeah, yeah.
yusheng kuo: I fully understand.
yusheng kuo: Yeah.
yusheng kuo: And if it could, then yeah, it's a, it could be a really huge time saver.
yusheng kuo: You just talk to.
Alberto Campora: Yeah, but then, yeah, exactly.
Alberto Campora: But then if you get it right and we prove every proof quality is the is.
Alberto Campora: Is big.
yusheng kuo: Yeah, yeah, big.
Alberto Campora: Because it's also for me is the most augmented solution because it's not going to sustain humans.
Alberto Campora: Yeah, but it's gonna just help humans to be.
Alberto Campora: Is also, it's also mental health because if you remove all the thoughts to these people, their life is going to be way better from, from a quality of life.
Alberto Campora: Yeah, I'm telling you.
yusheng kuo: Yeah, yeah.
Alberto Campora: Like all my friends are doing this.
Alberto Campora: They spending like they come back home after seven, eight hours on the road and they.
Alberto Campora: On a tablet and they need to put everything in.
yusheng kuo: Yeah, yeah, I get it.
yusheng kuo: Totally.
yusheng kuo: So I think we, we use MCP to just test if this kind of thing is useful.
yusheng kuo: And once we can test it successfully, we can actually have a more dedicated model, whatever workflow to improve the accuracy to as high as possible.
yusheng kuo: But I think the first thing is.
yusheng kuo: You can test out, okay, if this thing really kind of fit into people's workflow and then get some of the early feedback, even probably not 100% accuracy.
yusheng kuo: Yeah, yeah.
yusheng kuo: Also we need to have data.
yusheng kuo: We need to have data to know what, what are the way to talk and why it's failing.
yusheng kuo: Like.
yusheng kuo: Yeah, so, so, yeah, so this kind of.
Alberto Campora: Yeah, but that's why we need to kind of, for me, like, we need to.
Alberto Campora: That's why when you were telling me like we need to do, you know, customer development is true, we do need.
Alberto Campora: But also I think the best way to do customer development, like we need to get some companies and say we're doing this, test it.
Alberto Campora: If you, you know, if you test it for your next 32 com, next 3 conference, then you're gonna get lifetime, lifetime membership.
Alberto Campora: I don't know.
yusheng kuo: Yeah, sure.
Alberto Campora: You know, because we need, we.
Alberto Campora: We need these people to tell us how far was from their life.
yusheng kuo: Yeah.
Alberto Campora: You know?
yusheng kuo: Yeah.
Alberto Campora: And then we can't, we can't tell them like, oh, you like that?
Alberto Campora: Because they don't know how it's gonna make their life better.
Alberto Campora: And maybe they want.
Alberto Campora: So.
Alberto Campora: But we need, we need to, we need to get into the field.
yusheng kuo: Yeah, yeah, you know, I agree.
yusheng kuo: Yeah.
yusheng kuo: I think that's like, there are so many nuance, you know, like accent, like the feel the place, different language.
yusheng kuo: Yeah.
yusheng kuo: So I think, yeah, it's.
yusheng kuo: I think cloud would not be the perfect solution, but it could at least be like very first, like just giving people like, okay, if you have this tool, what would you like?
yusheng kuo: And next we can have like for example, very dedicated, like a language tool.
yusheng kuo: Maybe even one for each language, even.
yusheng kuo: Yeah, things like that.
yusheng kuo: But yeah, I think, I think we.
yusheng kuo: Can, we can start by just.
yusheng kuo: Having.
yusheng kuo: Something out like SCP that install for them and say, okay, now you can just talk to the cloud and then do your CRM update.
yusheng kuo: Now you don't need to go to CRM.
yusheng kuo: You just talk to it and let it feel if that's something the flow they want and let them tell us like, okay, this is not good because why.
yusheng kuo: So at least we have something for people to test out, not just like some kind of bullshitting around, right?
Alberto Campora: No, exactly.
Alberto Campora: We need, because we need to see how far we are from.
yusheng kuo: Yeah.
yusheng kuo: And I think mcp for us, it was pretty easy to build down.
yusheng kuo: Yeah.
Alberto Campora: Okay, well, I'll let you think about and then we can use case and think about the next step.
yusheng kuo: Yeah.
yusheng kuo: And I can just go ahead and start to build one simple mcp.
yusheng kuo: Just let you update your CRM and then you can try to test it.
Alberto Campora: Yeah.
yusheng kuo: Do you have like hotspot.
yusheng kuo: Do you have hotspot receive?
Alberto Campora: Yeah, I mean, I Don't use much, but, yeah, I do it for my clients.
Alberto Campora: Yeah.
yusheng kuo: Okay.
yusheng kuo: What do you internally use for CI I?
yusheng kuo: For you, for your consultant?
Alberto Campora: I use Akio.
Alberto Campora: But my, you know, my use base is not huge.
Alberto Campora: I mean, I'm, you know, my portfolio is, you know.
yusheng kuo: Yeah.
yusheng kuo: Yeah.
Alberto Campora: Like, you know, I'm still.
Alberto Campora: I'm still able.
Alberto Campora: I mean, I usually, you know, using it, but, you know, just literally not crazy.
yusheng kuo: Yeah.
Alberto Campora: Yeah.
Alberto Campora: I mean, because, you know, my company is small.
Alberto Campora: Like, we are.
Alberto Campora: It's me and another few people.
Alberto Campora: Like, we don't.
Alberto Campora: We don't even.
Alberto Campora: We don't.
Alberto Campora: We also don't want to speak to work with too many companies.
Alberto Campora: Yeah, it's, you know, we are happy.
Alberto Campora: We are happy with the size.
yusheng kuo: We are.
yusheng kuo: Yeah.
yusheng kuo: Yeah, I understand.
yusheng kuo: Okay, cool.
yusheng kuo: Yeah, then let us do one for.
yusheng kuo: You and then let you test it and tell us why.
Alberto Campora: Yeah, but I think, like, we should really work, you know, also test together, like, all the option and, like, because we can, you know, we can fake a conference.
Alberto Campora: You know, like, we can, you know, we can find a way to test it.
yusheng kuo: Yeah.
yusheng kuo: I mean, or I can.
yusheng kuo: I can just go to any conference that's happening here now in this abstent child.
yusheng kuo: Okay, cool.
yusheng kuo: Yeah, I have to run now.
yusheng kuo: Have to go by here, but.
yusheng kuo: Yeah, thanks.
yusheng kuo: Thanks.
yusheng kuo: I think we have a good path forward.
yusheng kuo: I will send out some kind of documentation after this.
Alberto Campora: Yeah, thank you.
yusheng kuo: Cool.
yusheng kuo: Thank you.
yusheng kuo: Bye.
yusheng kuo: All right.
Title: Datagen X Alberto
Host Email: yusheng.kuo@datagen.dev
Organizer Email: yusheng.kuo@datagen.dev
Calendar Id: 7mmt1s65hsn00htqsotstjt1c6
Fireflies Users: yusheng.kuo@datagen.dev
Participants: yuehlin.chung@datagen.dev,alberto.campora@pipepod.co,yusheng.kuo@datagen.dev, yuehlin.chung@datagen.dev, alberto.campora@pipepod.co
Date: 1764629100000
Transcript Url: https://app.fireflies.ai/view/01KB8EFR4YVD6TVS4B2XZV3S5N
Audio Url: No audio url
Video Url: No video url
Duration: 65.44000244140625
Meeting Attendees: yuehlin.chung@datagen.dev, alberto.campora@pipepod.co, yusheng.kuo@datagen.dev
Cal Id: 7mmt1s65hsn00htqsotstjt1c6
Calendar Type: google
Meeting Link: https://meet.google.com/ncp-sfux-ckr
