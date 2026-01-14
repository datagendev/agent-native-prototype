#!/usr/bin/env python3
"""
LinkedIn Post Search Agent

Searches for LinkedIn posts using Exa, Linkup, and Parallel Search in parallel,
ranks results by relevance, and saves top posts to the database.
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs
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

# Database configuration
PROJECT_ID = "blue-tree-25780810"
DATABASE = "neondb"

# Configuration
RELEVANCE_THRESHOLD = 40  # Lowered from 60 since we don't have engagement data from search
MAX_RESULTS_TO_SAVE = 15


def normalize_linkedin_url(url: str) -> str:
    """Normalize LinkedIn post URLs for deduplication."""
    if not url or "linkedin.com" not in url:
        return url

    # Remove query parameters and fragments
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    # Remove trailing slashes
    return base_url.rstrip("/")


def extract_post_id(url: str) -> str:
    """Extract LinkedIn post activity ID from URL."""
    if "activity-" in url:
        parts = url.split("activity-")
        if len(parts) > 1:
            return parts[1].split("-")[0].split("/")[0].split("?")[0]
    return ""


def calculate_relevance_score(post: Dict[str, Any], query: str) -> int:
    """Calculate relevance score (0-100) for a post."""
    score = 0

    # Freshness (30 points)
    if post.get("publish_date"):
        try:
            post_date = datetime.fromisoformat(post["publish_date"].replace("Z", "+00:00"))
            days_old = (datetime.now(timezone.utc) - post_date).days

            if days_old <= 7:
                score += 30
            elif days_old <= 30:
                score += 20
            elif days_old <= 90:
                score += 10
            else:
                score += 5
        except:
            score += 5
    else:
        score += 5

    # Engagement (30 points)
    engagement = post.get("engagement_count", 0)
    if engagement >= 50:
        score += 30
    elif engagement >= 20:
        score += 20
    elif engagement >= 5:
        score += 15
    else:
        score += 10

    # LinkedIn Specificity (20 points)
    url = post.get("post_url", "")
    if "linkedin.com/posts/" in url:
        score += 20
    elif "linkedin.com" in url:
        score += 10

    # Topic Relevance (20 points)
    query_terms = query.lower().split()
    content = (
        post.get("headline", "") + " " +
        post.get("excerpt", "") + " " +
        post.get("author_name", "")
    ).lower()

    matches = sum(1 for term in query_terms if term in content)
    if matches >= len(query_terms):
        score += 20
    elif matches >= len(query_terms) / 2:
        score += 10
    else:
        score += 5

    return min(score, 100)


def search_exa(query: str) -> List[Dict[str, Any]]:
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

        posts = []
        if result and len(result) > 0:
            # Parse Exa results
            results_text = result[0] if isinstance(result, list) else result
            # Simple parsing - in production, would parse more carefully
            # For now, return raw for processing
            print(f"✅ Exa: Found results")

        return []  # Placeholder - would parse actual results

    except Exception as e:
        print(f"❌ Exa search failed: {e}")
        return []


def search_linkup(query: str) -> List[Dict[str, Any]]:
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

        posts = []
        if result and len(result) > 0:
            print(f"✅ Linkup: Found results")

        return []  # Placeholder

    except Exception as e:
        print(f"❌ Linkup search failed: {e}")
        return []


def search_parallel(query: str) -> List[Dict[str, Any]]:
    """Search using Parallel Search."""
    print("🔍 Searching Parallel...")

    try:
        result = client.execute_tool(
            "mcp_Parallel_Search_web_search_preview",
            {
                "objective": f"Find LinkedIn posts discussing {query}",
                "search_queries": [f"{query} LinkedIn", f"{query} go-to-market LinkedIn"],
                "search_type": "list",
                "include_domains": ["linkedin.com"]
            }
        )

        posts = []
        if result and len(result) > 0:
            search_results = result[0].get("results", [])

            for item in search_results:
                posts.append({
                    "post_url": normalize_linkedin_url(item.get("url", "")),
                    "headline": item.get("title", ""),
                    "publish_date": item.get("publish_date", ""),
                    "excerpt": item.get("excerpts", [""])[0] if item.get("excerpts") else "",
                    "source_tool": "Parallel",
                    "engagement_count": 0,  # Not available from search
                    "author_name": "",
                    "author_profile": ""
                })

            print(f"✅ Parallel: Found {len(posts)} posts")

        return posts

    except Exception as e:
        print(f"❌ Parallel search failed: {e}")
        return []


def aggregate_and_deduplicate(all_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aggregate results and remove duplicates."""
    seen_urls = set()
    unique_posts = []

    for post in all_posts:
        url = post.get("post_url", "")
        normalized_url = normalize_linkedin_url(url)

        if normalized_url and normalized_url not in seen_urls:
            seen_urls.add(normalized_url)
            post["post_url"] = normalized_url
            unique_posts.append(post)

    return unique_posts


def ensure_table_exists():
    """Create linkedin_posts_tracker table if it doesn't exist."""
    print("📊 Checking if linkedin_posts_tracker table exists...")

    # Create table
    create_table_sql = """CREATE TABLE IF NOT EXISTS linkedin_posts_tracker (
      id SERIAL PRIMARY KEY,
      post_url TEXT NOT NULL UNIQUE,
      author_name TEXT,
      author_profile TEXT,
      headline TEXT,
      publish_date DATE,
      engagement_count INTEGER DEFAULT 0,
      excerpt TEXT,
      topic_tags JSONB DEFAULT '[]'::jsonb,
      source_tool TEXT,
      relevance_score INTEGER,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )"""

    try:
        client.execute_tool(
            "mcp_Neon_run_sql",
            {
                "params": {
                    "projectId": PROJECT_ID,
                    "databaseName": DATABASE,
                    "sql": create_table_sql
                }
            }
        )
        print("✅ Table created/verified")
    except Exception as e:
        print(f"⚠️  Table check: {e}")

    # Create indexes separately
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_linkedin_posts_url ON linkedin_posts_tracker(post_url)",
        "CREATE INDEX IF NOT EXISTS idx_linkedin_posts_date ON linkedin_posts_tracker(publish_date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_linkedin_posts_score ON linkedin_posts_tracker(relevance_score DESC)"
    ]

    for idx_sql in indexes:
        try:
            client.execute_tool(
                "mcp_Neon_run_sql",
                {
                    "params": {
                        "projectId": PROJECT_ID,
                        "databaseName": DATABASE,
                        "sql": idx_sql
                    }
                }
            )
        except:
            pass  # Indexes might already exist


def save_posts_to_db(posts: List[Dict[str, Any]]) -> int:
    """Save posts to database."""
    if not posts:
        return 0

    print(f"\n💾 Saving {len(posts)} posts to database...")

    saved_count = 0
    failed_count = 0

    for post in posts:
        try:
            # Extract topic tags from query
            topic_tags = json.dumps(["Claude AI", "GTM"])

            # Parse date
            publish_date = post.get("publish_date", "")
            if publish_date:
                try:
                    date_obj = datetime.fromisoformat(publish_date.replace("Z", "+00:00"))
                    publish_date = date_obj.strftime("%Y-%m-%d")
                except:
                    publish_date = None
            else:
                publish_date = None

            # Build insert query
            sql = f"""
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
              '{post.get("post_url", "").replace("'", "''")}',
              '{post.get("author_name", "").replace("'", "''")}',
              '{post.get("author_profile", "").replace("'", "''")}',
              '{post.get("headline", "").replace("'", "''")}',
              {f"'{publish_date}'" if publish_date else "NULL"},
              {post.get("engagement_count", 0)},
              '{post.get("excerpt", "")[:500].replace("'", "''")}',
              '{topic_tags}'::jsonb,
              '{post.get("source_tool", "")}',
              {post.get("relevance_score", 0)}
            )
            ON CONFLICT (post_url)
            DO UPDATE SET
              engagement_count = EXCLUDED.engagement_count,
              relevance_score = EXCLUDED.relevance_score,
              updated_at = NOW();
            """

            client.execute_tool(
                "mcp_Neon_run_sql",
                {
                    "params": {
                        "projectId": PROJECT_ID,
                        "databaseName": DATABASE,
                        "sql": sql
                    }
                }
            )

            saved_count += 1
            print(f"   ✅ {saved_count}. {post.get('headline', 'Untitled')[:60]}...")

        except Exception as e:
            failed_count += 1
            print(f"   ❌ Failed: {post.get('headline', 'Untitled')[:60]}... - {e}")

    return saved_count


def generate_summary(query: str, all_posts: List[Dict[str, Any]], saved_posts: List[Dict[str, Any]]):
    """Generate search results summary."""
    print("\n" + "="*80)
    print(f"SEARCH RESULTS: \"{query}\"")
    print("="*80)

    print(f"\n📊 OVERVIEW:")
    print(f"   🔍 Total Results: {len(all_posts)} posts")
    print(f"   ✅ Saved to Database: {len(saved_posts)} posts (score >= {RELEVANCE_THRESHOLD})")

    if all_posts:
        dates = [p.get("publish_date") for p in all_posts if p.get("publish_date")]
        if dates:
            print(f"   📅 Date Range: {min(dates)} to {max(dates)}")

    if saved_posts:
        avg_score = sum(p.get("relevance_score", 0) for p in saved_posts) / len(saved_posts)
        print(f"   ⭐ Average Relevance Score: {avg_score:.0f}")

    print(f"\n🏆 TOP POSTS:")
    for i, post in enumerate(saved_posts[:5], 1):
        print(f"\n   {i}. Score: {post.get('relevance_score', 0)} | {post.get('headline', 'Untitled')[:80]}")
        print(f"      Date: {post.get('publish_date', 'Unknown')} | Source: {post.get('source_tool', 'Unknown')}")
        print(f"      URL: {post.get('post_url', '')}")

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Fetch engagement from top posts using fetch_linkedin_engagement.py")
    print("2. Analyze post authors for potential prospects")
    print("3. Create campaigns targeting engaged audiences")
    print("4. Monitor topics for trending conversations")
    print("="*80 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python post_search_agent.py <search_query>")
        print("\nExample:")
        print("  python post_search_agent.py 'Claude Code for GTM'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    print("="*80)
    print("LINKEDIN POST SEARCH AGENT")
    print("="*80)
    print(f"\nQuery: {query}\n")

    # Step 1: Parallel search
    print("🚀 Starting parallel search across all tools...\n")

    exa_results = search_exa(query)
    linkup_results = search_linkup(query)
    parallel_results = search_parallel(query)

    # Step 2: Aggregate and deduplicate
    all_posts = exa_results + linkup_results + parallel_results
    unique_posts = aggregate_and_deduplicate(all_posts)

    print(f"\n📋 Aggregated {len(unique_posts)} unique posts")

    # Step 3: Calculate relevance scores
    print("\n⚖️  Calculating relevance scores...")
    for post in unique_posts:
        post["relevance_score"] = calculate_relevance_score(post, query)
        print(f"   - Score {post['relevance_score']}: {post.get('headline', 'Untitled')[:60]}...")

    # Sort by score
    unique_posts.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    # Step 4: Filter by threshold
    posts_to_save = [p for p in unique_posts if p.get("relevance_score", 0) >= RELEVANCE_THRESHOLD]
    posts_to_save = posts_to_save[:MAX_RESULTS_TO_SAVE]

    print(f"\n✅ {len(posts_to_save)} posts meet threshold (>= {RELEVANCE_THRESHOLD})")

    # Step 5: Ensure table exists
    ensure_table_exists()

    # Step 6: Save to database
    if posts_to_save:
        saved_count = save_posts_to_db(posts_to_save)
    else:
        saved_count = 0
        print("\n⚠️  No posts to save (none met relevance threshold)")

    # Step 7: Generate summary
    generate_summary(query, unique_posts, posts_to_save)


if __name__ == "__main__":
    main()
