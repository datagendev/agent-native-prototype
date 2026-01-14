"""
Primitive: Firecrawl Scrape

Scrape web page content using Firecrawl's powerful scraper and return markdown.

METADATA:
  name: firecrawl_scrape
  category: web
  created: 2026-01-14
  mcp_tool: mcp_Firecrawl_firecrawl_scrape

WHEN TO USE:
  - Need to extract content from a specific URL
  - Want clean markdown without ads/headers/footers
  - Scraping documentation, articles, or blog posts
  - Keywords: scrape, web page, markdown, content extraction

WHEN NOT TO USE:
  - Multiple URLs at once (use batch_scrape instead)
  - Don't know the URL (use search first)
  - Need structured data extraction (use extract_structured)
  - Already have the content cached

INPUT SCHEMA:
  - url (string): The URL to scrape [required]
  - formats (array): Output formats, default ["markdown"] [optional]
  - maxAge (integer): Cache max age in ms, default 172800000 (48h) [optional]
  - onlyMainContent (boolean): Extract only main content [optional]

OUTPUT SCHEMA:
  - markdown (string): Scraped content in markdown format
  - url (string): The URL that was scraped
  - title (string): Page title if available

EXAMPLE USAGE:
  ```python
  from primitives import firecrawl_scrape

  result, err = firecrawl_scrape(
      url="https://example.com/article",
      onlyMainContent=True
  )

  if err:
      print(f"Scraping failed: {err}")
      return

  print(f"Title: {result['title']}")
  print(f"Content: {result['markdown'][:200]}...")
  ```

PERFORMANCE:
  - Latency: ~500-2000ms depending on page size
  - Cost: $0.001 per page (with 48h cache)
  - Cache: 48h default (set maxAge for faster repeated scrapes)
  - Rate limits: Respects Firecrawl API limits

This is a TRUE primitive - no hardcoded columns, works with any URL.
"""

from .base import Primitive, register_primitive


@register_primitive
class FirecrawlScrape(Primitive):
    """Scrape content from a URL using Firecrawl and return markdown."""

    name = "firecrawl_scrape"
    description = "Scrape web page content and return markdown"

    input_schema = {
        "url": {
            "type": "string",
            "description": "The URL to scrape",
            "required": True
        },
        "formats": {
            "type": "array",
            "description": "Output formats (default: ['markdown'])",
            "required": False
        },
        "maxAge": {
            "type": "integer",
            "description": "Cache max age in ms for faster scrapes (default: 172800000 = 48h)",
            "required": False
        },
        "onlyMainContent": {
            "type": "boolean",
            "description": "Extract only main content, removing headers/footers/ads (default: True)",
            "required": False
        }
    }

    output_schema = {
        "markdown": {
            "type": "string",
            "description": "Scraped content in markdown format"
        },
        "url": {
            "type": "string",
            "description": "The URL that was scraped"
        },
        "title": {
            "type": "string",
            "description": "Page title if available"
        }
    }

    def run(self, **inputs) -> tuple[dict, str]:
        url = inputs["url"]

        if not url or not url.strip():
            return {}, "empty url"

        # Prepare parameters with defaults
        params = {
            "url": url,
            "formats": inputs.get("formats", ["markdown"]),
            "maxAge": inputs.get("maxAge", 172800000),  # 48 hours default
        }

        # Add onlyMainContent if specified
        if "onlyMainContent" in inputs:
            params["onlyMainContent"] = inputs["onlyMainContent"]

        try:
            result = self.client.execute_tool(
                "mcp_Firecrawl_firecrawl_scrape",
                params
            )
        except Exception as e:
            return {}, f"firecrawl scrape failed: {str(e)}"

        if not result:
            return {}, "no result from firecrawl scrape"

        # Firecrawl returns an array with one element
        if isinstance(result, list):
            if len(result) == 0:
                return {}, "empty result list from firecrawl scrape"
            result = result[0]

        # Extract markdown content
        markdown = result.get("markdown", "")
        if not markdown:
            return {}, "empty markdown from firecrawl scrape"

        return {
            "markdown": markdown,
            "url": url,
            "title": result.get("metadata", {}).get("title", "")
        }, ""


# Module-level instance for convenient imports
firecrawl_scrape = FirecrawlScrape()
