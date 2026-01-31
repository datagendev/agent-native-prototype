---
title: "Scheduled Competitor Intelligence"
description: "Auto-monitor competitor channels on a daily schedule, surface insights, and deliver digests via messaging"
category: "use-cases"
tags: ["async-agent", "competitor-intelligence", "scheduled", "monitoring", "youtube", "telegram"]
created: 2026-01-30
updated: 2026-01-30
status: "draft"
priority: "medium"
based_on: ["[[clawdbot-scheduled-automation]]"]
---

# Scheduled Competitor Intelligence

Monitor competitor content channels daily, identify high-performing content, and deliver actionable reports via messaging.

## Problem

- Competitor activity is spread across YouTube, blogs, social media, and product pages
- Manual monitoring takes 30-45 minutes daily and is easy to skip
- Teams miss competitor launches, messaging shifts, and content trends
- No systematic way to track what's resonating in the market

## Solution

Scheduled async agent that:
1. Runs daily at a fixed time (e.g., 8 AM)
2. Scrapes competitor channels for new content
3. Analyzes performance signals (views, engagement, topics)
4. Generates a prioritized digest
5. Delivers via Telegram, Slack, or email

## Trigger

```
Cron: Daily (8:00 AM local) OR
Manual: "Check competitor activity for [competitor list]"
```

## Pipeline

```
1. LOAD competitor list
   - YouTube channels, blogs, LinkedIn pages
   - From config file or CRM
    |
2. FOR EACH competitor:
   - Fetch recent content (last 24h or since last run)
   - YouTube: new videos, view counts, engagement
   - Blog: new posts, topics
   - LinkedIn: new posts, engagement metrics
    |
3. ANALYZE content
   - High-performing? (above baseline engagement)
   - New topic or messaging shift?
   - Product announcement or feature launch?
   - Targeting our audience segment?
    |
4. SCORE relevance
   - High: Product launch, direct competitive claim, viral content
   - Medium: New topic area, above-average engagement
   - Low: Routine content, recycled topics
    |
5. GENERATE digest
   - Group by priority
   - Include competitor name, content link, key takeaway
   - Highlight trends across competitors
    |
6. DELIVER
   - Telegram/Slack/Email with formatted digest
   - Optional: Update competitive tracking spreadsheet
```

## Content Analysis Schema

```yaml
competitor_update:
  id: string
  detected_at: datetime

  source:
    competitor: string
    channel: youtube|blog|linkedin|twitter
    url: string
    published_at: datetime

  content:
    title: string
    type: video|article|post|announcement
    topic: string
    summary: string  # 2-3 sentence summary

  performance:
    views: integer
    engagement_rate: float
    above_baseline: boolean
    velocity: string  # e.g., "5K views in 4 hours"

  analysis:
    priority: high|medium|low
    category: product_launch|messaging_shift|content_trend|audience_targeting
    takeaway: string  # Why this matters to us
    action: update_battlecard|brief_sales|monitor|ignore
```

## Output: Daily Competitor Digest

```markdown
# Competitor Intel: {date}

## High Priority

### [Competitor A] launched "AI Data Cleaner" - YouTube video
**Views**: 12K in 6 hours (3x their baseline)
**Summary**: Positioning directly against manual data cleanup workflows.
Targets ops teams frustrated with CSV formatting.
**Takeaway**: Overlaps with our CRM hygiene use case. Update battlecard.
**Link**: [URL]

---

## Medium Priority

### [Competitor B] blog post: "Why API-first beats UI-first"
**Engagement**: 200+ LinkedIn shares
**Summary**: Arguing that developer-first tools win in the long run.
**Takeaway**: Validates our SDK-first approach. Consider referencing in content.
**Link**: [URL]

---

## Trends This Week
- 3/5 competitors published content about "AI agents" (up from 1/5 last week)
- YouTube engagement is 2x higher than blog posts across all competitors
- [Competitor C] shifted messaging from "automation" to "AI-native"

## Summary
- High priority: 2
- Medium priority: 4
- Competitors with new content: 4/6 monitored
```

## Integration Points

- **Input**: YouTube API, RSS feeds, LinkedIn (via MCP), web scraping
- **Processing**: DataGen SDK for fetching; Claude for analysis and scoring
- **Output**: Telegram/Slack/Email digest, optional CRM or spreadsheet update
- **Storage**: `./tmp/competitor-intel/{date}/` for intermediate data

## Implementation with DataGen

### Custom Tool Pipeline

```python
from datagen_sdk import DatagenClient

client = DatagenClient()

# Step 1: Fetch competitor YouTube channels
for channel in competitor_channels:
    videos = client.execute_tool("mcp_YouTube_list_videos", {
        "channel_id": channel["id"],
        "published_after": yesterday
    })

# Step 2: Analyze with AI
for video in new_videos:
    analysis = client.execute_tool("web_search", {
        "query": f"{video['title']} site:youtube.com"
    })

# Step 3: Deliver digest
client.execute_tool("mcp_Telegram_send_message", {
    "chat_id": CHANNEL_ID,
    "text": formatted_digest
})
```

### Scheduling

Deploy as a DataGen custom tool and trigger via cron or webhook.

## Success Metrics

- Coverage: % of competitor content captured within 24 hours
- Actionable signals per week: 3-5 high-priority items
- Time saved: 30-45 min/day of manual monitoring
- Battlecard update frequency: driven by automated signals

## Phases

### Phase 1: YouTube Only
Monitor 3-5 competitor YouTube channels. Daily Telegram digest.

### Phase 2: Multi-Channel
Add blog RSS, LinkedIn pages. Unified digest across channels.

### Phase 3: Trend Analysis
Week-over-week trend tracking. Messaging shift detection. Automated battlecard suggestions.

## MCP Requirements

- YouTube MCP (video listing, metrics)
- Web scraping tool (blog content)
- LinkedIn MCP (company page posts)
- Telegram or Slack MCP (delivery)
- Optional: Google Sheets MCP (tracking spreadsheet)
