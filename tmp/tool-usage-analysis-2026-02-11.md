# Tool Usage Analysis - Last 7 Days
**Date**: February 11, 2026

## Executive Summary

**Total Active Users**: 4 users with significant tool usage
**Total Tool Executions**: 3,569 executions
**Most Popular Tool**: `extract_structured_output` (2,411 executions by Jeremy)

## Top Users (Excluding Jeremy)

### 🥇 #1: david@automatedemand.com
**User ID**: 126
**Total Executions**: 618
**Unique Tools Used**: 10
**Last Activity**: Feb 10, 2026

**Focus Area**: LinkedIn Prospecting + Instantly Integration

**Tool Breakdown**:
- `get_linkedin_person_data`: 234 calls
- `get_linkedin_person_posts`: 178 calls
- `search_linkedin_person`: 93 calls
- `mcp_Instantly_list_accounts`: 47 calls
- `mcp_Instantly_get_warmup_analytics`: 34 calls
- `mcp_Instantly_list_campaigns`: 11 calls
- `mcp_Instantly_list_emails`: 10 calls
- `mcp_Instantly_get_campaign`: 6 calls
- `mcp_Instantly_get_campaign_analytics`: 4 calls
- `mcp_Instantly_get_account`: 1 call

**Analysis**:
David is running a sophisticated LinkedIn → Instantly workflow:
1. Searching for LinkedIn prospects
2. Extracting their profile data and posts
3. Managing Instantly campaigns
4. Monitoring email warmup and campaign analytics

This is a **power user** executing a complete prospecting-to-outreach pipeline.

---

### 🥈 #2: andriyvovchak15@gmail.com
**User ID**: 131
**Total Executions**: 140
**Unique Tools Used**: 5
**Last Activity**: Feb 9, 2026

**Focus Area**: Company Research + AI Content

**Tool Breakdown**:
- `search_linkedin_company`: 81 calls
- `chatgpt_webresearch`: 38 calls
- `search_linkedin_person`: 10 calls
- `perplexity_search`: 7 calls
- `ai_writer`: 4 calls

**Analysis**:
Andriy is doing market research workflows:
1. Identifying companies on LinkedIn
2. Web research on those companies
3. Using AI to synthesize findings

Potential use case: Competitive intelligence, market mapping, or ABM research.

---

### 🥉 #3: jeremy.scott.ross@gmail.com (For Comparison)
**User ID**: 74
**Total Executions**: 2,425
**Unique Tools Used**: 7
**Last Activity**: Feb 11, 2026 (today)

**Focus Area**: Structured Data Extraction

**Tool Breakdown**:
- `extract_structured_output`: 2,411 calls (99.4% of activity!)
- `search_linkedin_person`: 8 calls
- `mcp_Notion_notion_create_pages`: 2 calls
- Other LinkedIn tools: 4 calls
- `mcp_Firecrawl_firecrawl_scrape`: 1 call

**Analysis**:
Jeremy is running massive batch extraction jobs - likely processing large datasets and extracting structured information at scale.

---

## Most Popular Tools (Last 7 Days)

| Tool | Executions | Unique Users | Use Case |
|------|------------|--------------|----------|
| `extract_structured_output` | 2,411 | 1 | Data extraction/parsing |
| `get_linkedin_person_data` | 241 | 3 | LinkedIn profile scraping |
| `mcp_Neon_run_sql` | 222 | 1 | Database queries |
| `get_linkedin_person_posts` | 185 | 3 | LinkedIn content scraping |
| `search_linkedin_person` | 111 | 3 | LinkedIn prospecting |
| `search_linkedin_company` | 81 | 1 | Company research |
| `mcp_Posthog_query_run` | 61 | 1 | Analytics queries |
| `mcp_Instantly_list_accounts` | 47 | 1 | Email campaign mgmt |
| `chatgpt_webresearch` | 45 | 2 | Web research |
| `mcp_Instantly_get_warmup_analytics` | 34 | 1 | Email deliverability |

---

## Tool Categories

### LinkedIn Tools (771 executions)
- Profile data extraction
- Post scraping
- Person/company search
- Used by 3 users for prospecting workflows

### Email Outreach Tools (123 executions)
- Instantly.ai integration
- Campaign management
- Warmup monitoring
- Used by 1 user (david@automatedemand.com)

### AI/Research Tools (90 executions)
- ChatGPT web research
- Perplexity search
- AI writing
- Used by 2 users for content/research

### Database/Analytics (283 executions)
- Neon SQL queries
- PostHog analytics
- Used primarily for internal monitoring

---

## Key Insights

### 1. LinkedIn → Instantly Pipeline is the #1 Use Case
David's workflow demonstrates the product's core value prop:
- Find prospects on LinkedIn
- Extract their data
- Push to email outreach tool
- Monitor campaign performance

### 2. Users Are Running Multi-Tool Workflows
Not just single tool calls - users are orchestrating 5-10 different tools in sequence to accomplish complex tasks.

### 3. Heavy Batch Processing
Jeremy's 2,411 `extract_structured_output` calls suggest users need to process large datasets, not just one-off queries.

### 4. Research & Intelligence Use Cases Emerging
Andriy's company research workflow shows potential for:
- Market intelligence
- Competitive analysis
- Account-based marketing research

---

## Recommendations

### Product Development
1. **Template/Workflow Feature**: Pre-built templates for "LinkedIn → Instantly" workflow
2. **Batch Operations UI**: Better UX for processing 100+ records at once
3. **Campaign Dashboard**: View all Instantly campaigns + LinkedIn data in one place

### Marketing/Sales
1. **Case Study**: Interview david@automatedemand.com about his prospecting workflow
2. **Use Case Documentation**: Document "LinkedIn Prospecting to Email Outreach" as primary use case
3. **Outreach to Andriy**: He's at-risk (last activity Feb 9) - re-engage with company research templates

### Feature Requests to Prioritize
- Bulk LinkedIn profile enrichment
- Instantly.ai bi-directional sync
- LinkedIn → CRM direct integration (beyond Instantly)
- Scheduled workflows (run enrichment daily)

---

## Next Steps

1. **Interview david@automatedemand.com**: Understand his complete workflow
2. **Re-engage andriyvovchak15@gmail.com**: Last activity 2 days ago - send targeted content
3. **Monitor tool success rates**: Current data shows 0% success rate tracking - investigate schema
4. **Build workflow templates**: Based on actual usage patterns observed

---

**Note**: Success rate data appears to be 0% across all tools, suggesting the `status` field may not be populated correctly or uses different values than 'COMPLETED'. Need to investigate schema.
