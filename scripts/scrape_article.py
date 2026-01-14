#!/usr/bin/env python3
"""
Script to scrape an article using the Firecrawl primitive.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path so we can import primitives
sys.path.insert(0, str(Path(__file__).parent))

from primitives import firecrawl_scrape


def scrape_article(url: str, output_path: str = None) -> tuple[dict, str]:
    """
    Scrape an article and optionally save to file.

    Args:
        url: The URL to scrape
        output_path: Optional path to save the markdown content

    Returns:
        (result, error) tuple
    """
    print(f"Scraping: {url}")

    result, err = firecrawl_scrape(
        url=url,
        onlyMainContent=True
    )

    if err:
        return {}, err

    print(f"✓ Successfully scraped: {result.get('title', 'Untitled')}")
    print(f"  Content length: {len(result.get('markdown', ''))} chars")

    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["markdown"])

        print(f"✓ Saved to: {output_path}")

    return result, ""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scrape_article.py <url> [output_path]")
        sys.exit(1)

    url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    result, err = scrape_article(url, output_path)

    if err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    # If no output path, print the markdown
    if not output_path:
        print("\n--- Scraped Content ---")
        print(result["markdown"])
