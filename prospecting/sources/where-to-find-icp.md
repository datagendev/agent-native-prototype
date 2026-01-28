---
title: "Where to Find Claude Code Deployers"
description: "Channels, communities, and signals for finding ICP prospects"
category: "gtm"
tags: ["prospecting", "channels", "communities", "linkedin", "github", "outbound"]
created: 2026-01-28
updated: 2026-01-28
status: "active"
priority: "high"
asset-type: "prospecting-playbook"
target-persona: "gtm-operators"
based_on: ["[[claude-code-deployers]]", "[[claude-code-non-developer-landscape]]"]
---

# Where to Find Claude Code Deployers

## Channel Overview

| Channel | Intent Level | Volume | Effort |
|---------|--------------|--------|--------|
| LinkedIn posts | High | Medium | Low |
| GitHub skill repos | High | Low | Medium |
| Communities (Discord, Slack) | Medium | High | Medium |
| Twitter/X | Medium | High | Low |
| Content comments | High | Low | High |

---

## 1. LinkedIn (Highest Intent)

### Search Queries

```
"Claude Code" GTM
"Claude Code" workflow
"Claude Code" automation
"Claude Code" marketing OR sales OR ops
"AI agent" workflow manual
```

### What to Look For

- Posts sharing transformation stories (before/after AI adoption)
- Posts with specific use cases (not vague "AI is amazing")
- Comments asking "how do I schedule this?" or "I run this daily"
- People tagging others asking for automation help

### Example High-Value Posts

| Author | Post Theme | Why Valuable |
|--------|------------|--------------|
| Maja Voje | "10 Claude Code use cases for GTM" | Specific use cases, GTM audience |
| James Ngiam | "Last year I wouldn't trust AI agents" | Trust transformation story |
| Xavier C. | "Told my team of 4 about AI" | Team adoption, scale signal |
| Ajay Khanna | "Building GTM Intelligence App" | Hands-on project builder |
| Hans Dekker | "How powerful is Claude Code for GTM?" | Direct GTM question |
| Victor Sowers | "Pushing Claude Code as hard as anyone" | Power user, heavy usage |

### Action Playbook

1. Search weekly for new Claude Code GTM posts
2. Engage genuinely in comments first
3. Note specific workflows they mention
4. DM with reference to their exact use case

---

## 2. GitHub

### Repositories to Monitor

| Repository | Focus | What to Track |
|------------|-------|---------------|
| [gtmagents/gtm-agents](https://github.com/gtmagents/gtm-agents) | GTM-specific skills | Contributors, issues |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | 48 domain skills | Marketing/business forks |
| [anthropics/skills](https://github.com/anthropics/skills) | Official enterprise | Issue discussions |
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | Marketing specific | Contributors |

### Signals to Watch

- Contributors building business (not dev) skills
- Issues asking about scheduling, deployment, persistence
- Forks from profiles with non-developer job titles
- Stars from GTM/marketing professionals

### How to Find Them

1. Check contributor profiles → look for GTM titles
2. Search issues for "schedule," "cron," "deploy," "webhook"
3. Look at who's forking marketing/GTM skill repos

---

## 3. Communities

### High-Value Communities

| Community | Platform | Size | How to Find ICPs |
|-----------|----------|------|------------------|
| **Claude Code Discord** | Discord | Growing | Search "schedule," "overnight," "cron," "webhook" |
| **Every.to** | Substack/workshops | High engagement | Dan Shipper's non-dev audience |
| **GTMfund** | Newsletter/Slack | 50k+ readers | Jordan Crawford's GTM AI crowd |
| **AI Marketing** | Skool | Active | @boringmarketer's audience |
| **Pavilion** | Slack | 10k+ members | RevOps/GTM professionals |
| **Indie Hackers** | Forum | Large | Solopreneurs automating ops |

### Keywords to Search in Communities

```
schedule
overnight
cron
webhook
deploy
"run automatically"
"keep running"
persistence
```

### Engagement Strategy

1. Join and lurk first — understand the culture
2. Answer questions genuinely (build reputation)
3. Note people asking about automation/scheduling
4. DM after providing value publicly

---

## 4. Twitter/X

### Accounts to Monitor

| Account | Focus | Why |
|---------|-------|-----|
| @danshipper | Every.to, non-dev Claude Code | Runs Claude101 workshops |
| @boringmarketer | Marketing automation skills | "10 skills to turn Claude Code into marketing team" |
| @jordancrawford | GTM + AI outbound | "The man who mastered AI + GTM" |
| @lennysan | Product/founder audience | "Everyone should use Claude Code" |
| @petergyang | Product management | PM audience using Claude Code |
| @_catwu | Anthropic official | Internal Anthropic use cases |

### Search Queries

```
"Claude Code" -is:retweet
"Claude Code" wish OR schedule OR overnight
"Claude Code" workflow OR automation
"AI agent" GTM OR marketing OR sales
```

### What to Look For

- Threads sharing Claude Code workflows
- Complaints about manual execution
- Questions about running agents automatically
- Replies to influencer posts with specific use cases

---

## 5. Content Comments

### Where to Look

| Content Type | Where | What to Find |
|--------------|-------|--------------|
| Lenny's Newsletter | Substack | Comments on Claude Code articles |
| Every.to articles | Substack | Non-dev use case discussions |
| YouTube tutorials | YouTube | "How do I run this automatically?" |
| Dev.to posts | Dev.to | Marketing/GTM Claude Code guides |
| Medium articles | Medium | Non-technical Claude Code guides |

### Gold Comments to Find

- "This is great but how do I make it run automatically?"
- "I do this every day manually, wish it could schedule"
- "Works when I'm at my laptop but..."
- "How do I trigger this from a webhook?"

---

## 6. Events

### Upcoming/Recurring

| Event | Organizer | Audience |
|-------|-----------|----------|
| GTMfund events | Jordan Crawford | GTM founders learning AI |
| Claude101 workshops | Dan Shipper | Non-dev Claude Code users |
| Every.to meetups | Every.to | AI productivity enthusiasts |
| Pavilion events | Pavilion | RevOps/GTM professionals |

### How to Use Events

1. Attend (virtual or in-person)
2. Note who asks questions about automation/deployment
3. Connect on LinkedIn post-event
4. Reference their specific question in outreach

---

## Outbound Playbook

### Step-by-Step

| Step | Action |
|------|--------|
| 1 | Find post/comment about Claude Code workflow |
| 2 | Check if they mention manual execution pain |
| 3 | Engage genuinely first (like, comment, share) |
| 4 | DM with specific reference to their workflow |
| 5 | Offer to show async deployment for their use case |

### DM Template

```
Saw your post about [specific workflow]. I've been working on
a way to deploy Claude Code agents so they run on webhooks/schedules
without keeping terminal open.

Would that solve the problem you mentioned about [specific pain]?
```

### Connection Request Template

```
[Name] - loved your post about [specific Claude Code use case].
Building tools to help deploy these workflows async.
Would love to connect and share notes.
```

---

## Automated Monitoring

### What to Automate

| Monitor | Tool | Trigger |
|---------|------|---------|
| LinkedIn posts | linkedin-post-search agent | Daily |
| GitHub activity | GitHub API | Weekly |
| Twitter mentions | Twitter API | Daily |
| Community keywords | Discord/Slack bots | Real-time |

### Alerts to Set Up

- New post containing "Claude Code" + GTM keywords
- New GitHub issue mentioning "schedule" or "deploy"
- New comment on tracked influencer posts
- New member in GTM AI communities
