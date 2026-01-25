---
name: prospecting
description: Extract prospects from websites, LinkedIn posts, or web search using MCP tools
---

# Skill: Prospecting

Extract prospect data from multiple sources and save to `lead-list/` as CSV.

## Overview

This skill provides four prospecting methods:
1. **Website Scraping** - Extract team/contact info from company pages
2. **Map & Batch Scrape** - Multi-page extraction from large sites
3. **LinkedIn Engagers** - Get people who commented/reacted to a post
4. **Web Search** - Find prospects matching search criteria

## Interactive Workflow

When `/prospecting` is invoked, present the method selection menu:

```
AskUserQuestion:
  question: "Which prospecting method would you like to use?"
  header: "Method"
  multiSelect: false
  options:
    - label: "Website Scraping"
      description: "Extract team/contact info from a company website"
    - label: "LinkedIn Engagers"
      description: "Get people who engaged with a LinkedIn post"
    - label: "Find Alike"
      description: "Using find alike like DiscoLike to find similar ones"
    - label: "Web Search"
      description: "Find prospects via search query"
```

---

## Method 1: Website Scraping

Extract names, titles, and contact info from a company's team or about page.

### When to Use
- Scraping a single page (team page, about page, leadership page)
- Interactive extraction where you can see and validate results
- Pages requiring JavaScript rendering

### Option A: Chrome DevTools (Interactive)

Best for: Single pages, JavaScript-heavy sites, validation needed

```
Step 1: Navigate to target page
mcp__chrome-devtools__navigate_page(url: "https://company.com/team")

Step 2: Wait for content to load
mcp__chrome-devtools__wait_for(text: "Team")

Step 3: Take snapshot to see structure
mcp__chrome-devtools__take_snapshot()

Step 4: Extract data using JavaScript
mcp__chrome-devtools__evaluate_script(function: ```
() => {
  return Array.from(document.querySelectorAll('.team-member')).map(el => ({
    name: el.querySelector('.name')?.textContent?.trim(),
    title: el.querySelector('.title')?.textContent?.trim(),
    linkedin: el.querySelector('a[href*="linkedin"]')?.href
  }))
}
```)
```

### Option B: Firecrawl (Fast)

Best for: Static pages, simple extraction, no JavaScript needed

```
Step 1: Scrape page content
mcp_Firecrawl_firecrawl_scrape(
  url: "https://company.com/team",
  formats: ["markdown"]
)

Step 2: Parse markdown to extract names/titles

Step 3: For structured extraction, use:
mcp_Firecrawl_firecrawl_extract(
  urls: ["https://company.com/team"],
  prompt: "Extract all team members with their name, title, and LinkedIn URL",
  schema: {
    "type": "object",
    "properties": {
      "team_members": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "title": {"type": "string"},
            "linkedin_url": {"type": "string"}
          }
        }
      }
    }
  }
)
```

### Clarifying Questions

```
AskUserQuestion:
  question: "Which tool should I use for scraping?"
  header: "Tool"
  options:
    - label: "Chrome DevTools (Recommended)"
      description: "Interactive browser control, handles JavaScript, good for validation"
    - label: "Firecrawl"
      description: "Faster, simpler, works well for static content"
```

---

## Method 2: Map & Batch Scrape

Extract from multiple pages on a site (e.g., all team member profile pages).

### When to Use
- Site has multiple pages to scrape (e.g., `/team/john`, `/team/jane`)
- Need to discover URLs before scraping
- Large-scale extraction

### Workflow

```
Step 1: Map the site to discover URLs
mcp_Firecrawl_firecrawl_map(url: "https://company.com")
-> Returns array of URLs

Step 2: Filter URLs to target pages
- Filter for patterns like /team/*, /people/*, /about/*

Step 3: Scrape each URL
For small batches (< 10 URLs):
  Call mcp_Firecrawl_firecrawl_scrape() for each URL

For large batches (> 10 URLs):
  Use DataGen SDK with executeCode:
  mcp__datagen__executeCode(
    script: ```python
    from datagen_sdk import DatagenClient
    from concurrent.futures import ThreadPoolExecutor

    client = DatagenClient()
    urls = [...]  # List of URLs from map

    def scrape_url(url):
        return client.execute_tool("mcp_Firecrawl_firecrawl_scrape", {
            "url": url,
            "formats": ["markdown"]
        })

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(scrape_url, urls))
    ```,
    mcp_server_names: ["Firecrawl"]
  )
```

### Intermediate Storage

Save raw results to `/tmp/prospecting-{YYYY-MM-DD}/`:
```
/tmp/prospecting-2026-01-13/
├── map_urls.json          # URLs discovered
├── raw/                   # Raw scrape results
│   ├── page_1.json
│   └── page_2.json
└── prospects.json         # Parsed prospects
```

---

## Method 3: LinkedIn Engagers

Extract people who commented or reacted to a LinkedIn post.

### When to Use
- Building list from post engagement
- Finding people interested in specific topics
- Signal-based prospecting

### Step 1: Get Post Activity ID

Extract activity ID from LinkedIn post URL:
- Pattern: `https://www.linkedin.com/feed/update/urn:li:activity:{ACTIVITY_ID}`
- Or: `https://www.linkedin.com/posts/{username}_{ACTIVITY_ID}`

```
AskUserQuestion:
  question: "Paste the LinkedIn post URL"
  header: "Post URL"
```

### Step 2: Ask Engagement Type

```
AskUserQuestion:
  question: "What type of engagement should I extract?"
  header: "Engagement"
  multiSelect: false
  options:
    - label: "Comments only"
      description: "People who commented on the post"
    - label: "Reactions only"
      description: "People who liked/reacted to the post"
    - label: "Both"
      description: "Extract both comments and reactions"
```

### Step 3: Fetch Engagers

**For Comments:**
```
mcp__datagen__executeTool(
  tool_alias_name: "get_linkedin_person_post_comments",
  parameters: { activity_id: "{ACTIVITY_ID}" }
)

Returns:
{
  "comments": [
    {
      "text": "Great post!",
      "author": {
        "authorId": "...",
        "authorName": "John Doe",
        "authorPublicIdentifier": "john-doe-123",
        "authorLinkedinUrl": "https://linkedin.com/in/john-doe-123/"
      }
    }
  ],
  "total_comments": 45
}
```

**For Reactions:**
```
mcp__datagen__executeTool(
  tool_alias_name: "get_linkedin_person_post_reactions",
  parameters: { activity_id: "{ACTIVITY_ID}" }
)

Returns:
{
  "reactions": [
    {
      "type": "LIKE",
      "author": {
        "authorId": "...",
        "authorName": "Jane Smith"
      }
    }
  ]
}
```

### Step 4: Parse to CSV

Extract from response:
- `name` from `author.authorName`
- `linkedin_url` from `author.authorLinkedinUrl` or construct from `authorPublicIdentifier`
- `engagement_type` = "comment" or reaction type

---

## Method 4: Web Search

Find prospects via search queries.

### When to Use
- Finding companies/people matching specific criteria
- Research-based prospecting
- Unknown target sites

### Option A: Firecrawl Search

Best for: General web search with optional scraping

```
mcp__datagen__executeTool(
  tool_alias_name: "mcp_Firecrawl_firecrawl_search",
  parameters: {
    query: "AI startup founders San Francisco",
    limit: 10,
    sources: ["web"]
  }
)
```

### Option B: Exa Search

Best for: AI-optimized search, finding specific information

```
mcp__datagen__executeTool(
  tool_alias_name: "mcp_Exa_web_search_exa",
  parameters: {
    query: "AI agents startup founders LinkedIn",
    num_results: 10
  }
)
```

### Option C: Parallel Search

Best for: Multi-source search, comprehensive results

```
mcp__datagen__executeTool(
  tool_alias_name: "mcp_Parallel_Search_web_search_preview",
  parameters: {
    query: "series A AI companies hiring engineers",
    search_type: "targeted"
  }
)
```

### Clarifying Questions

```
AskUserQuestion:
  question: "Which search tool should I use?"
  header: "Search Tool"
  options:
    - label: "Firecrawl Search (Recommended)"
      description: "General web search with scraping capability"
    - label: "Exa Search"
      description: "AI-optimized search for specific information"
    - label: "Parallel Search"
      description: "Multi-source comprehensive search"
```

---

## Output Format

### CSV Schema

Save all prospects to `lead-list/{name}_{date}.csv`:

```csv
name,title,company,linkedin_url,email,source,source_url,engagement_type,extracted_at
John Doe,VP Sales,TechCorp,https://linkedin.com/in/johndoe,,website_scrape,https://techcorp.com/team,,2026-01-13T10:30:00Z
Jane Smith,CEO,StartupAI,https://linkedin.com/in/janesmith,,linkedin_comments,https://linkedin.com/feed/update/...,comment,2026-01-13T10:30:00Z
```

### Columns

| Column | Required | Description |
|--------|----------|-------------|
| `name` | Yes | Full name |
| `title` | No | Job title |
| `company` | No | Company name |
| `linkedin_url` | Yes* | LinkedIn profile URL |
| `email` | No | Email address |
| `source` | Yes | Prospecting method used |
| `source_url` | Yes | URL scraped/searched |
| `engagement_type` | No | For LinkedIn: comment, LIKE, etc. |
| `extracted_at` | Yes | ISO timestamp |

*Either `linkedin_url` or `email` should be present

### Save Location

```
AskUserQuestion:
  question: "What should I name the output file?"
  header: "Filename"
```

Save to: `lead-list/{user_provided_name}_{YYYY-MM-DD}.csv`

---

## Deduplication

Before saving, deduplicate by `linkedin_url`:
1. Group by `linkedin_url`
2. Keep first occurrence (or merge data)
3. Report: "Found X prospects (Y unique after dedup)"

---

## Error Handling

### Chrome DevTools Issues
- If snapshot returns empty: Check if page loaded, try `wait_for`
- If JS extraction fails: Inspect page structure in snapshot first

### Firecrawl Issues
- Rate limits: Add delays between requests
- Timeout: Reduce batch size or use simpler formats

### LinkedIn Issues
- Invalid activity_id: Verify URL format, try extracting from share URL
- Empty results: Post may have no engagement or be private

### Search Issues
- No results: Try broader queries
- Irrelevant results: Add filters like `site:linkedin.com`

---

## Examples

### Example 1: Scrape YC Company Team Page

```
User: /prospecting
Claude: [Shows method menu]
User: Website Scraping
Claude: [Asks for URL]
User: https://www.ycombinator.com/companies/anthropic
Claude: [Uses Chrome DevTools to navigate and extract]
Claude: Found 15 team members. Save to lead-list/anthropic_team_2026-01-13.csv?
```

### Example 2: Extract LinkedIn Post Commenters

```
User: /prospecting
Claude: [Shows method menu]
User: LinkedIn Engagers
Claude: [Asks for post URL]
User: https://www.linkedin.com/posts/activity-7287520881159761920
Claude: [Asks comments/reactions/both]
User: Comments only
Claude: [Fetches comments via get_linkedin_person_post_comments]
Claude: Found 42 commenters. Save to lead-list/post_commenters_2026-01-13.csv?
```

### Example 3: Search for AI Founders

```
User: /prospecting
Claude: [Shows method menu]
User: Web Search
Claude: [Asks for search query]
User: "AI agents" startup founder site:linkedin.com
Claude: [Uses Firecrawl search]
Claude: Found 10 results. Parsing LinkedIn profiles...
Claude: Extracted 8 founders. Save to lead-list/ai_founders_2026-01-13.csv?
```
