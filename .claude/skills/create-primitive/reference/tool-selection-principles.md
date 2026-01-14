# Tool Selection & Description Principles

Extracted from: `docs/useful-resources/tool-selection-optimization-llm-agents-at-scale.md`

## Bloomberg ACL 2025: Context Optimization

**Key finding:** Jointly optimizing agent instructions AND tool descriptions reduced tool calls by **70%** (StableToolBench) and **47%** (RestBench) while maintaining pass rates.

### The Problem

Incomplete descriptions force LLMs to make exploratory calls. Without clear boundaries, tools are either:
- **Under-selected**: Missing when they should be used
- **Over-selected**: Called inappropriately, wasting tokens and time

### The Solution: Structured Tool Descriptions

```json
{
  "name": "weather_forecast",
  "description": "Get weather forecast for a location. Returns temperature, precipitation %, wind, conditions.",
  "when_to_use": "Weather, temperature, rain, outdoor planning queries",
  "when_not_to_use": "Historical data (use weather_history), air quality (use air_quality_api)",
  "parameters": {
    "location": {"type": "string", "description": "City name or coordinates"},
    "days": {"type": "integer", "default": 7, "description": "Forecast days (1-14)"}
  },
  "example_queries": ["What's the weather in Tokyo?", "Will it rain this weekend?"]
}
```

### Key Elements

1. **`when_to_use`** — Triggers selection
   - List specific use cases
   - Include trigger keywords
   - Be explicit about what queries should select this tool

2. **`when_not_to_use`** — Prevents over-selection
   - Identify similar but wrong scenarios
   - Point to alternative tools
   - Prevent common mistakes

3. **`example_queries`** — Improves retrieval
   - Actual user queries that should match
   - Helps semantic retrieval find the right tool
   - Include vocabulary variations

4. **Clear schemas** — Reduces exploratory calls
   - Document all parameters
   - Provide default values
   - Explain return values

5. **Performance notes** — Cost optimization
   - Latency expectations
   - Cost per call
   - Rate limits

## The 80/20 of Tool Selection

**Distribution of impact:**

1. **Tool descriptions (40%)**: Clear "when to use", "when not to use", examples
2. **Retrieval quality (30%)**: Hybrid retrieval beats pure semantic
3. **Context awareness (20%)**: Use conversation history
4. **Learned components (10%)**: RL fine-tuning for edge cases

## Naming Conventions

### Snake Case for Primitives
- `firecrawl_scrape` ✓
- `FirecrawlScrape` ✗ (use for class name)
- `firecrawl-scrape` ✗ (use dash in files, not function names)

### Verb-Noun Pattern
- `scrape_webpage` ✓
- `find_email` ✓
- `enrich_profile` ✓
- `webpage_scraper` ✗ (noun-verb)

### Avoid Redundancy
- `firecrawl_scrape` ✓
- `firecrawl_scrape_with_firecrawl` ✗
- `scrape_using_firecrawl` ✗

### Be Specific but Not Verbose
- `scrape_webpage` ✓
- `scrape` ✗ (too vague)
- `scrape_webpage_content_using_firecrawl_api` ✗ (too verbose)

## Common Mistakes

### 1. Vague Descriptions
❌ "Get data from a URL"
✅ "Scrape web page content and return markdown. Best for articles, documentation, blog posts."

### 2. Missing Boundaries
❌ No "when not to use" section
✅ "When NOT to use: Multiple URLs (use batch_scrape), unknown URL (use search first)"

### 3. Incomplete Schemas
❌ `{"url": "string"}`
✅ `{"url": {"type": "string", "description": "The URL to scrape", "required": true}}`

### 4. No Examples
❌ Description only
✅ Include example usage code and example queries

### 5. Ignoring Performance
❌ No cost or latency info
✅ "Latency: ~500ms, Cost: $0.001 per page, Cache: 48h"

## Application to Primitives

Primitives are **atomic enrichment capabilities** that:
- Don't know about specific columns
- Work with named parameters
- Return structured results
- Follow error-first pattern: `(result, error)`

**Every primitive should have:**
1. ✅ Structured frontmatter docstring
2. ✅ Clear when_to_use / when_not_to_use
3. ✅ Complete input/output schemas
4. ✅ Example usage code
5. ✅ Performance characteristics
6. ✅ Proper error handling

## References

- Bloomberg ACL 2025: Context optimization for tool calling
- StableToolBench: 16,000+ real API benchmark
- RestBench: RESTful API evaluation
- "Retrieval Models Aren't Tool-Savvy" (ACL 2025): <35% completeness@10 without optimization
