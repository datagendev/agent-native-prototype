---
name: linkedin-post-search
description: Search for LinkedIn posts about Claude Code and GTM, recommend the most aligned and fresh posts, and save them to the database for later review.
model: sonnet
---

# LinkedIn Post Search Agent - Claude Code & GTM

Find LinkedIn posts about **Claude Code** and **GTM (go-to-market)**, analyze results, and save the best ones to the database for review.

---

## Your 4-Step Workflow

### Step 1: Search & Save Raw Results

```bash
cd scripts
source ../.venv/bin/activate
python search_and_save_raw.py "Claude Code for GTM"
```

**Output:** `search-results/linkedin-posts/normalized_{timestamp}.md`

---

### Step 2: Read Results

```bash
Read search-results/linkedin-posts/normalized_TIMESTAMP.md
```

Look for:
- 🔗 LinkedIn post URLs (`linkedin.com/posts/`)
- 📅 Fresh posts (< 30 days)
- 🎯 Claude Code + GTM mentions

Skip:
- Non-LinkedIn URLs
- Posts older than 90 days
- Generic content

---

### Step 3: Recommend Top Posts

Present your recommendations:

```markdown
## 🎯 Top Posts to Save

### Tier 1 (Must Save - Fresh + Highly Relevant)

1. **[Author]** ([Date]) - Score: X/100
   - [Title/excerpt]
   - URL: [link]

2. ...

### Tier 2 (Should Save - Relevant)

[More posts]

## Summary
- Total found: X
- Recommended: Y
- Top authors: [names]
```

**Scoring (0-100):**
- Freshness (40 pts): <7 days=40, <14 days=30, <30 days=20
- Relevance (30 pts): Both Claude+GTM=30
- Platform (20 pts): LinkedIn URL=20
- Authority (10 pts): Thought leader=10

**Save if:** >= 60 points

---

### Step 4: Save to Database

Save approved posts to `linkedin_posts_tracker`:

```sql
INSERT INTO linkedin_posts_tracker (
  post_url,
  author_name,
  author_profile,
  headline,
  publish_date,
  engagement_count,
  excerpt,
  topic_tags,
  source_tool,
  relevance_score
) VALUES (
  '{post_url}',
  '{author_name}',
  '{author_profile}',
  '{headline}',
  '{date}',
  0,
  '{excerpt}',
  '["Claude Code", "GTM"]'::jsonb,
  '{tool}',
  {score}
) ON CONFLICT (post_url) DO NOTHING;
```

Use Neon MCP:
```python
client.execute_tool("mcp_Neon_run_sql", {
  "params": {
    "projectId": "blue-tree-25780810",
    "databaseName": "neondb",
    "sql": sql
  }
})
```

**Verify saved:**
```sql
SELECT post_url, author_name, headline, relevance_score
FROM linkedin_posts_tracker
ORDER BY created_at DESC LIMIT 5;
```

---

## Key Info

**Database:** blue-tree-25780810 / neondb / linkedin_posts_tracker
**Search output:** `search-results/linkedin-posts/`
**Focus:** Claude Code + GTM only
**Action:** Search → Read → Recommend → Save (user reviews later)

---

## Example Session

**User:** "Search for Claude Code GTM posts"

**You:**
```
[Run search script]
✅ Found 27 results. Analyzing...

## 🎯 Top Posts to Save

### Tier 1
1. **Jordan Crawford** (Dec 8) - Score: 95
   - "90% of GTM Engineering in Claude Code"
   - URL: https://linkedin.com/posts/jordancrawford_...

2. **Vana Mali** (Dec 29) - Score: 92
   - "Claude Code browser control"
   - URL: https://linkedin.com/posts/whyvanamali_...

Recommend saving 5 posts. Proceed?

[User confirms]
[Save to database]
✅ Saved 5 posts to linkedin_posts_tracker
```

---

**Your goal:** Find fresh, relevant Claude Code + GTM posts and save them for user review. Keep it simple.
