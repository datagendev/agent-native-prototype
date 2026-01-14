#!/usr/bin/env python3
"""
LinkedIn Post Search - Save Raw Results

Searches for LinkedIn posts using Exa, Linkup, and Parallel Search in parallel,
saves raw results and creates clean normalized markdown for manual review.
"""

import os
import sys
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from datagen_sdk import DatagenClient

# Load environment variables from ../.env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Verify API key
DATAGEN_API_KEY = os.getenv("DATAGEN_API_KEY")
if not DATAGEN_API_KEY:
    print("ERROR: DATAGEN_API_KEY not found")
    print(f"Tried loading from: {env_path}")
    sys.exit(1)

# Initialize DataGen client
client = DatagenClient()

# Output directory
RESULTS_DIR = Path(__file__).parent.parent / "search-results" / "linkedin-posts"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def search_exa(query: str) -> Dict[str, Any]:
    """Search using Exa."""
    print("🔍 Searching Exa...")
    try:
        result = client.execute_tool(
            "mcp_Exa_web_search_exa",
            {
                "query": f"{query} LinkedIn posts",
                "numResults": 10
            }
        )
        print(f"✅ Exa: Complete")
        return {"tool": "Exa", "query": query, "results": result}
    except Exception as e:
        print(f"❌ Exa failed: {e}")
        return {"tool": "Exa", "query": query, "error": str(e)}


def search_linkup(query: str) -> Dict[str, Any]:
    """Search using Linkup."""
    print("🔍 Searching Linkup...")
    try:
        result = client.execute_tool(
            "mcp_Linkup_linkup_search",
            {
                "query": f"LinkedIn posts about {query}",
                "depth": "standard"
            }
        )
        print(f"✅ Linkup: Complete")
        return {"tool": "Linkup", "query": query, "results": result}
    except Exception as e:
        print(f"❌ Linkup failed: {e}")
        return {"tool": "Linkup", "query": query, "error": str(e)}


def search_parallel(query: str) -> Dict[str, Any]:
    """Search using Parallel Search."""
    print("🔍 Searching Parallel...")
    try:
        result = client.execute_tool(
            "mcp_Parallel_Search_web_search_preview",
            {
                "objective": f"Find LinkedIn posts discussing {query}",
                "search_queries": [f"{query} LinkedIn", f"{query} go-to-market"],
                "search_type": "list",
                "include_domains": ["linkedin.com"]
            }
        )
        print(f"✅ Parallel: Complete")
        return {"tool": "Parallel", "query": query, "results": result}
    except Exception as e:
        print(f"❌ Parallel failed: {e}")
        return {"tool": "Parallel", "query": query, "error": str(e)}


def save_raw_json(data: Dict[str, Any], timestamp: str):
    """Save raw JSON results."""
    filename = RESULTS_DIR / f"raw_{data['tool'].lower()}_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"   💾 Saved: {filename.name}")


def parse_and_normalize(all_results: List[Dict[str, Any]], query: str, timestamp: str) -> str:
    """Parse all results and create normalized markdown."""

    md = f"""# LinkedIn Post Search Results

**Query:** {query}
**Timestamp:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Search Tools:** Exa, Linkup, Parallel Search

---

"""

    for tool_result in all_results:
        tool_name = tool_result.get("tool", "Unknown")

        md += f"\n## {tool_name} Results\n\n"

        if "error" in tool_result:
            md += f"❌ **Error:** {tool_result['error']}\n\n"
            continue

        results = tool_result.get("results", [])

        if tool_name == "Parallel":
            # Parallel returns structured results
            if results and len(results) > 0:
                search_results = results[0].get("results", [])
                md += f"**Total Results:** {len(search_results)}\n\n"

                for i, item in enumerate(search_results, 1):
                    url = item.get("url", "")
                    title = item.get("title", "Untitled")
                    publish_date = item.get("publish_date", "Unknown date")
                    excerpts = item.get("excerpts", [])
                    excerpt = excerpts[0] if excerpts else ""

                    md += f"### {i}. {title}\n\n"
                    md += f"- **URL:** {url}\n"
                    md += f"- **Date:** {publish_date}\n"
                    if excerpt:
                        md += f"- **Excerpt:** {excerpt[:200]}...\n"
                    md += "\n"

        elif tool_name == "Linkup":
            # Linkup returns text results
            if results and len(results) > 0:
                link_results = results[0].get("results", [])
                md += f"**Total Results:** {len(link_results)}\n\n"

                for i, item in enumerate(link_results, 1):
                    name = item.get("name", "Untitled")
                    url = item.get("url", "")
                    content = item.get("content", "")

                    md += f"### {i}. {name}\n\n"
                    md += f"- **URL:** {url}\n"
                    md += f"- **Content:** {content[:300]}...\n\n"

        elif tool_name == "Exa":
            # Exa returns mixed text results
            if results and len(results) > 0:
                # Parse the text response
                text_results = results[0] if isinstance(results[0], str) else str(results[0])

                # Split by "Title:" to find individual results
                posts = text_results.split("Title: ")[1:]
                md += f"**Total Results:** {len(posts)}\n\n"

                for i, post in enumerate(posts, 1):
                    lines = post.split("\n")
                    title = lines[0] if lines else "Untitled"

                    # Extract URL
                    url = ""
                    for line in lines:
                        if line.startswith("URL: "):
                            url = line.replace("URL: ", "").strip()
                            break

                    # Extract date
                    publish_date = ""
                    for line in lines:
                        if line.startswith("Published Date: "):
                            publish_date = line.replace("Published Date: ", "").strip()
                            break

                    md += f"### {i}. {title}\n\n"
                    if url:
                        md += f"- **URL:** {url}\n"
                    if publish_date:
                        md += f"- **Date:** {publish_date}\n"
                    md += "\n"

        md += "---\n\n"

    return md


def main():
    if len(sys.argv) < 2:
        print("Usage: python search_and_save_raw.py <search_query>")
        print("\nExample:")
        print("  python search_and_save_raw.py 'Claude Code for GTM'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')

    print("="*80)
    print("LINKEDIN POST SEARCH - SAVE RAW RESULTS")
    print("="*80)
    print(f"\nQuery: {query}")
    print(f"Output: {RESULTS_DIR}\n")

    # Step 1: Search all tools in parallel
    print("🚀 Starting parallel search...\n")

    exa_result = search_exa(query)
    linkup_result = search_linkup(query)
    parallel_result = search_parallel(query)

    all_results = [exa_result, linkup_result, parallel_result]

    # Step 2: Save raw JSON
    print("\n💾 Saving raw JSON results...")
    for result in all_results:
        save_raw_json(result, timestamp)

    # Step 3: Create normalized markdown
    print("\n📝 Creating normalized markdown...")
    markdown = parse_and_normalize(all_results, query, timestamp)

    md_filename = RESULTS_DIR / f"normalized_{timestamp}.md"
    with open(md_filename, 'w') as f:
        f.write(markdown)

    print(f"   ✅ Saved: {md_filename.name}")

    # Summary
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    print(f"\n📂 Results saved to: {RESULTS_DIR}")
    print(f"\n📄 Files created:")
    print(f"   - raw_exa_{timestamp}.json")
    print(f"   - raw_linkup_{timestamp}.json")
    print(f"   - raw_parallel_{timestamp}.json")
    print(f"   - normalized_{timestamp}.md")
    print(f"\n💡 Next step: Review normalized_{timestamp}.md")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
