# LinkedIn Posts Scraper Node

## Quick Reference

### Node Type
`linkedin_posts_scraper` - Fetch and analyze recent LinkedIn posts from a profile

### Pre-configured Instances
- `founder_posts` - Standard scan (10 posts)
- `founder_posts_quick` - Quick scan (5 posts)
- `founder_posts_deep` - Deep scan (50 posts)

## Input/Output

### Required Input
- `founder_linkedin_url` - LinkedIn profile URL (e.g., "https://linkedin.com/in/patrickcollison")

### Output Columns
- `recent_posts_count` (integer) - Number of posts found
- `latest_post_text` (string) - Most recent post text (max 500 chars)
- `latest_post_date` (string) - Date of latest post
- `posts_summary` (string) - AI-generated summary of themes and topics

## Usage

### 1. Preview Mode (Test First!)
```bash
# Test with standard instance (10 posts)
python scripts/graph_enrich.py --lead yc-f25 --graph founder_posts --preview --limit 3

# Test with quick scan (5 posts)
python scripts/graph_enrich.py --lead yc-f25 --graph founder_posts_quick --preview --limit 3
```

### 2. Batch Processing
```bash
# Run on all rows
python scripts/graph_enrich.py --lead yc-f25 --graph founder_posts --parallel 5

# Deep scan (more posts, slower)
python scripts/graph_enrich.py --lead yc-f25 --graph founder_posts_deep --parallel 3
```

### 3. Custom Configuration
```bash
# Custom number of posts
python scripts/graph_enrich.py \
  --lead yc-f25 \
  --graph linkedin_posts_scraper \
  --config '{"max_posts": 25}' \
  --preview

# With output prefix
python scripts/graph_enrich.py \
  --lead yc-f25 \
  --graph linkedin_posts_scraper \
  --config '{"max_posts": 15, "output_prefix": "founder"}' \
  --preview
```

## Use Cases

### 1. Identify Active LinkedIn Users
Filter founders who post frequently:
```sql
SELECT name, founder_name, recent_posts_count, posts_summary
FROM leads
WHERE recent_posts_count > 5
ORDER BY recent_posts_count DESC;
```

### 2. Find Topic-Specific Founders
Look for founders posting about specific topics:
```sql
SELECT name, founder_name, posts_summary
FROM leads
WHERE posts_summary LIKE '%AI agents%'
   OR posts_summary LIKE '%automation%';
```

### 3. Prioritize Recent Activity
Find founders with recent posts:
```sql
SELECT name, founder_name, latest_post_date, latest_post_text
FROM leads
WHERE latest_post_date >= '2026-01-01'
ORDER BY latest_post_date DESC;
```

## Integration with Workflow

The node is designed to work in a multi-step enrichment pipeline:

```yaml
# In workflows.yaml
founder_enrichment:
  description: Enrich YC founders with LinkedIn insights
  nodes:
    - node: yc_founder
      # Step 1: Get founder LinkedIn URL

    - node: founder_posts
      # Step 2: Analyze their posts (uses founder_linkedin_url from step 1)

    - node: claude_code_check
      # Step 3: Check for Claude Code mentions
```

## Performance Tips

1. **Start Small**: Use `--preview --limit 3` to test before running on all rows
2. **Choose Right Instance**:
   - Quick scan (5 posts): For rapid initial screening
   - Standard (10 posts): Balanced performance/insights
   - Deep scan (50 posts): Comprehensive analysis (slower)
3. **Parallel Processing**: Use `--parallel 5` for faster batch processing
4. **Rate Limiting**: LinkedIn API has rate limits - use fewer workers for deep scans

## Troubleshooting

### Empty Results
If `recent_posts_count` is 0:
- Check if `founder_linkedin_url` is valid
- Founder may not have any public posts
- LinkedIn profile may be private

### Missing Summary
If `posts_summary` is empty:
- AI summarization may have failed (non-critical)
- Posts may be too short or lacking content
- Check error logs for API issues

### Slow Performance
If enrichment is taking too long:
- Reduce `max_posts` parameter
- Use fewer parallel workers
- Use `founder_posts_quick` instance instead

## Example Output

```csv
name,founder_linkedin_url,recent_posts_count,latest_post_date,posts_summary
Stripe,https://linkedin.com/in/patrickcollison,12,2026-01-10,"Focus on developer tools and API infrastructure. Key topics: fintech, developers, scaling"
```

## Architecture

```
Input: founder_linkedin_url
  ↓
linkedin_posts primitive
  ↓ (fetch posts from LinkedIn)
  ↓
extract_structured primitive
  ↓ (AI summarization)
  ↓
Output: count, latest post, summary
```

## Error Handling

The node gracefully handles:
- Missing LinkedIn URLs (returns empty results)
- API failures (returns partial results with error)
- Empty post lists (returns count: 0)
- AI summarization failures (continues without summary)
- Long posts (truncates to 500 chars)

## Next Steps

After running enrichment:
1. Review results in CSV output
2. Analyze `posts_summary` for common themes
3. Filter for active LinkedIn users
4. Use insights for outreach prioritization
5. Combine with other enrichment nodes (Claude Code mentions, B2B classification)
