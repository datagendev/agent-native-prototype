#!/usr/bin/env python3
"""
LinkedIn Prospect Monitoring Script

Fetches recent LinkedIn posts from a list of prospects and analyzes them for
DataGen relevance. Generates a structured markdown report.
"""

import csv
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from datagen_sdk import DatagenClient


# Initialize DataGen client
client = DatagenClient()


def load_prospects(csv_path: str) -> Tuple[List[Dict], str]:
    """Load prospects from CSV file.

    Returns: (prospects_list, error_message)
    """
    try:
        prospects = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('linkedin_url'):  # Skip empty rows
                    prospects.append({
                        'name': f"{row.get('first_name', '')} {row.get('last_name', '')}".strip(),
                        'linkedin_url': row['linkedin_url'],
                        'first_name': row.get('first_name', ''),
                        'last_name': row.get('last_name', '')
                    })
        return prospects, ""
    except Exception as e:
        return [], f"Failed to load prospects: {e}"


def fetch_person_posts(linkedin_url: str) -> Tuple[Optional[Dict], str]:
    """Fetch posts for a LinkedIn profile.

    Returns: (posts_data, error_message)
    """
    try:
        result = client.execute_tool(
            "get_linkedin_person_posts",
            {"linkedin_url": linkedin_url}
        )
        return result, ""
    except Exception as e:
        return None, f"Failed to fetch posts: {e}"


def filter_recent_posts(posts_data: Optional[Dict], days: int = 7) -> List[Dict]:
    """Filter posts to only those from the last N days (Central Time).

    Args:
        posts_data: Result from get_linkedin_person_posts
        days: Number of days to look back (default 7)

    Returns: List of recent posts
    """
    if not posts_data or not posts_data.get('posts'):
        return []

    # Calculate cutoff date (7 days ago from today in Central Time)
    # Today is 2026-01-23, so cutoff is 2026-01-16
    # Make cutoff_date timezone-aware (UTC)
    from datetime import timezone
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    recent_posts = []
    for post in posts_data['posts']:
        if not post.get('activityDate'):
            continue

        # Parse ISO datetime string
        post_date_str = post['activityDate']
        try:
            # Handle ISO format with timezone
            if 'T' in post_date_str:
                post_date = datetime.fromisoformat(post_date_str.replace('Z', '+00:00'))
            else:
                post_date = datetime.fromisoformat(post_date_str)
                # If no timezone info, assume UTC
                if post_date.tzinfo is None:
                    post_date = post_date.replace(tzinfo=timezone.utc)

            if post_date >= cutoff_date:
                recent_posts.append(post)
        except Exception as e:
            print(f"Warning: Could not parse date '{post_date_str}': {e}")
            continue

    return recent_posts


def score_relevance(post: Dict) -> Tuple[str, str, str]:
    """Analyze a post for DataGen relevance.

    Returns: (relevance_score, why_relevant, outreach_angle)
    """
    text = post.get('text', '').lower()

    # High relevance keywords
    high_keywords = [
        'data automation', 'ai agent', 'workflow automation', 'crm data',
        'data quality', 'lead enrichment', 'prospecting', 'python',
        'data pipeline', 'manual data', 'data hygiene'
    ]

    # Medium relevance keywords
    medium_keywords = [
        'sales automation', 'marketing automation', 'revops', 'gtm',
        'data integration', 'tool stack', 'sales ops', 'sales operations'
    ]

    # Low relevance keywords
    low_keywords = [
        'ai', 'automation', 'technology', 'saas', 'b2b', 'sales', 'marketing'
    ]

    # Check for keyword matches
    high_matches = [kw for kw in high_keywords if kw in text]
    medium_matches = [kw for kw in medium_keywords if kw in text]
    low_matches = [kw for kw in low_keywords if kw in text]

    if high_matches:
        relevance = "High"
        why = f"Directly discusses DataGen-relevant topics: {', '.join(high_matches)}"
        angle = f"Reference their post about {high_matches[0]} and show how DataGen addresses this"
    elif medium_matches:
        relevance = "Medium"
        why = f"Adjacent to DataGen value prop: {', '.join(medium_matches)}"
        angle = f"Connect their interest in {medium_matches[0]} to DataGen's capabilities"
    elif low_matches:
        relevance = "Low"
        why = f"Tangentially related: {', '.join(low_matches)}"
        angle = "General conversation starter about AI/automation trends"
    else:
        relevance = "Low"
        why = "No clear connection to DataGen value prop"
        angle = "Monitor for future relevant content"

    return relevance, why, angle


def generate_report(prospects: List[Dict], results: List[Dict], output_path: str) -> Tuple[bool, str]:
    """Generate markdown report.

    Returns: (success, error_message)
    """
    try:
        # Calculate summary stats
        total_prospects = len(prospects)
        total_posts = sum(len(r['posts']) for r in results)

        # Categorize posts by relevance
        high_relevance = []
        medium_relevance = []
        low_relevance = []
        no_activity = []

        for result in results:
            if not result['posts']:
                no_activity.append(result['name'])
            else:
                for post in result['posts']:
                    if post.get('relevance') == 'High':
                        high_relevance.append((result, post))
                    elif post.get('relevance') == 'Medium':
                        medium_relevance.append((result, post))
                    else:
                        low_relevance.append((result, post))

        datagen_relevant_count = len(high_relevance) + len(medium_relevance)

        # Identify key themes
        themes = []
        if high_relevance:
            themes.append("Data automation and AI agents")
        if medium_relevance:
            themes.append("Sales/marketing automation and RevOps")
        if not themes:
            themes.append("No strong DataGen-related themes detected")

        # Generate report content
        report_lines = [
            "---",
            f'title: "LinkedIn Prospect Activity - 2026-01-23"',
            'description: "Daily monitoring of prospect LinkedIn posts"',
            'category: "linkedin"',
            'tags: ["prospect-monitoring", "linkedin", "competitive-intelligence"]',
            'created: 2026-01-23',
            'updated: 2026-01-23',
            'status: "active"',
            'priority: "medium"',
            "---",
            "",
            "# LinkedIn Prospect Activity - January 23, 2026",
            "",
            "## Summary",
            f"- **Total Prospects Monitored**: {total_prospects}",
            f"- **Posts Found**: {total_posts}",
            f"- **DataGen-Relevant Posts**: {datagen_relevant_count}",
            "- **Key Themes**: " + "; ".join(themes),
            "",
            "## DataGen-Relevant Posts",
            ""
        ]

        # Add high relevance posts
        if high_relevance:
            report_lines.append("### High Relevance Posts\n")
            for result, post in high_relevance:
                report_lines.extend(format_post(result, post))

        # Add medium relevance posts
        if medium_relevance:
            report_lines.append("### Medium Relevance Posts\n")
            for result, post in medium_relevance:
                report_lines.extend(format_post(result, post))

        # Other notable posts (low relevance)
        if low_relevance:
            report_lines.extend([
                "",
                "## Other Notable Posts",
                ""
            ])
            for result, post in low_relevance[:5]:  # Limit to 5 for brevity
                report_lines.extend(format_post_brief(result, post))

        # Prospects with no activity
        if no_activity:
            report_lines.extend([
                "",
                "## Prospects with No Recent Activity",
                ""
            ])
            for name in no_activity:
                report_lines.append(f"- {name}")
            report_lines.append("")

        # Recommendations
        report_lines.extend([
            "",
            "## Recommended Actions",
            ""
        ])

        if high_relevance:
            report_lines.append(f"1. **Priority Outreach**: Contact {len(high_relevance)} prospects with high-relevance posts within 24-48 hours")
        if medium_relevance:
            report_lines.append(f"2. **Warm Outreach**: Follow up with {len(medium_relevance)} prospects showing adjacent interest")
        if no_activity:
            report_lines.append(f"3. **Monitor**: Track {len(no_activity)} quiet prospects for future activity")

        # Write report
        with open(output_path, 'w') as f:
            f.write('\n'.join(report_lines))

        return True, ""
    except Exception as e:
        return False, f"Failed to generate report: {e}"


def format_post(result: Dict, post: Dict) -> List[str]:
    """Format a post with full details."""
    lines = [
        f"### {result['name']}",
        f"**LinkedIn**: {result['linkedin_url']}",
        f"**Post Date**: {format_date(post.get('activityDate'))}",
        f"**Relevance Score**: {post.get('relevance', 'Unknown')}",
        f"**Engagement**: {post.get('reactionsCount', 0)} reactions, {post.get('commentsCount', 0)} comments",
        "",
        "**Post Summary**:",
        format_text(post.get('text', 'No content')),
        "",
        f"**Why Relevant**: {post.get('why_relevant', 'N/A')}",
        "",
        f"**Outreach Angle**: {post.get('outreach_angle', 'N/A')}",
        ""
    ]

    if post.get('activityUrl'):
        lines.append(f"**Original Post**: {post['activityUrl']}")
        lines.append("")

    lines.append("---\n")
    return lines


def format_post_brief(result: Dict, post: Dict) -> List[str]:
    """Format a post with brief details."""
    return [
        f"### {result['name']}",
        f"**Post Summary**: {truncate_text(post.get('text', 'No content'), 150)}",
        f"**Topic**: {extract_topic(post.get('text', ''))}",
        ""
    ]


def format_date(date_str: Optional[str]) -> str:
    """Format ISO date string to readable format."""
    if not date_str:
        return "Unknown"
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(date_str)
        return dt.strftime("%B %d, %Y")
    except:
        return date_str


def format_text(text: str, max_length: int = 500) -> str:
    """Format text for display, truncating if needed."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def truncate_text(text: str, length: int) -> str:
    """Truncate text to specified length."""
    if len(text) > length:
        return text[:length] + "..."
    return text


def extract_topic(text: str) -> str:
    """Extract main topic from text (simplified)."""
    topics = {
        'automation': 'Automation',
        'ai': 'AI/Technology',
        'sales': 'Sales',
        'marketing': 'Marketing',
        'data': 'Data',
        'revops': 'RevOps'
    }

    text_lower = text.lower()
    for keyword, topic in topics.items():
        if keyword in text_lower:
            return topic

    return "General"


def main():
    """Main execution function."""
    print("LinkedIn Prospect Monitoring Script")
    print("=" * 50)

    # Paths
    csv_path = "/Users/yu-shengkuo/projects/datagendev/agent-native-prototype/data/monitor_linkedin_persons.csv"
    output_path = "/Users/yu-shengkuo/projects/datagendev/agent-native-prototype/data/linkedin-monitoring/2026-01-23-prospect-activity.md"

    # Step 1: Load prospects
    print(f"\nStep 1: Loading prospects from {csv_path}")
    prospects, err = load_prospects(csv_path)
    if err:
        print(f"ERROR: {err}")
        return
    print(f"✓ Loaded {len(prospects)} prospects")

    # Step 2: Fetch posts for each prospect
    print("\nStep 2: Fetching LinkedIn posts...")
    results = []

    for i, prospect in enumerate(prospects, 1):
        print(f"  [{i}/{len(prospects)}] {prospect['name']}...", end=" ")

        posts_data, err = fetch_person_posts(prospect['linkedin_url'])
        if err:
            print(f"✗ {err}")
            results.append({
                'name': prospect['name'],
                'linkedin_url': prospect['linkedin_url'],
                'posts': [],
                'error': err
            })
            continue

        # Filter to recent posts (last 7 days)
        recent_posts = filter_recent_posts(posts_data, days=7)
        print(f"✓ Found {len(recent_posts)} recent posts")

        # Score each post for relevance
        scored_posts = []
        for post in recent_posts:
            relevance, why_relevant, outreach_angle = score_relevance(post)
            post['relevance'] = relevance
            post['why_relevant'] = why_relevant
            post['outreach_angle'] = outreach_angle
            scored_posts.append(post)

        results.append({
            'name': prospect['name'],
            'linkedin_url': prospect['linkedin_url'],
            'posts': scored_posts,
            'error': None
        })

    # Step 3: Generate report
    print(f"\nStep 3: Generating report...")
    success, err = generate_report(prospects, results, output_path)
    if err:
        print(f"ERROR: {err}")
        return

    print(f"✓ Report generated: {output_path}")

    # Summary
    total_posts = sum(len(r['posts']) for r in results)
    high_relevance_count = sum(1 for r in results for p in r['posts'] if p.get('relevance') == 'High')
    medium_relevance_count = sum(1 for r in results for p in r['posts'] if p.get('relevance') == 'Medium')

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total prospects monitored: {len(prospects)}")
    print(f"Total posts found: {total_posts}")
    print(f"High relevance posts: {high_relevance_count}")
    print(f"Medium relevance posts: {medium_relevance_count}")
    print(f"\nNext step: Review {output_path} for insights and outreach opportunities")


if __name__ == "__main__":
    main()
