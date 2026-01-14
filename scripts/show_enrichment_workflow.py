#!/usr/bin/env python3
"""
Show Enrichment Workflow - Visual pipeline display

Displays the enrichment pipeline with statistics, showing which integrations ran,
success rates, and data flow.

Usage:
    python show_enrichment_workflow.py <csv_file>
    python show_enrichment_workflow.py lead-list/gtm-influencers_enriched.csv
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Dict, Tuple

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box
from rich.layout import Layout
from rich.text import Text

console = Console()


def load_csv(filepath: str) -> tuple[List[Dict], List[str], str]:
    """Load CSV file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            rows = list(reader)
        return rows, headers, ""
    except Exception as e:
        return [], [], f"Error loading CSV: {str(e)}"


def infer_integrations(headers: List[str]) -> Dict[str, List[str]]:
    """Infer which integrations were used based on column names."""

    integrations = {}

    # Define integration signatures
    signatures = {
        "linkedin_profile": ["headline", "current_company", "location", "follower_count"],
        "linkedin_post_activity": ["posts_last_30_days", "posts_last_90_days", "total_posts", "last_post_date"],
        "linkedin_claude_mentions": ["claude_mentions_count", "claude_mention_urls", "first_claude_mention_date"],
        "heyreach_engagement": ["heyreach_conversations_count", "heyreach_last_reply_date", "heyreach_meeting_booked", "heyreach_messages_sent", "heyreach_messages_received"],
        "heyreach_campaigns": ["heyreach_campaign_count", "heyreach_first_contacted_date", "heyreach_campaign_names", "heyreach_last_campaign_status"],
        "heyreach_network": ["heyreach_is_connection", "heyreach_connection_degree", "heyreach_mutual_connections_count"],
        "web_research": ["company_info", "research_summary"],
        "find_ceo": ["ceo_name", "ceo_linkedin"]
    }

    for integration, cols in signatures.items():
        matched_cols = [c for c in cols if c in headers]
        if matched_cols:
            integrations[integration] = matched_cols

    return integrations


def calculate_integration_stats(rows: List[Dict], integration: str, columns: List[str]) -> Dict:
    """Calculate statistics for an integration."""

    populated = 0
    empty = 0
    total = len(rows)

    for row in rows:
        # Check if ANY column from this integration has data
        has_data = any(
            row.get(col) and str(row[col]).strip() and str(row[col]).strip() not in ["0", "False", ""]
            for col in columns
        )

        if has_data:
            populated += 1
        else:
            empty += 1

    return {
        "total": total,
        "populated": populated,
        "empty": empty,
        "success_rate": (populated / total * 100) if total > 0 else 0,
        "columns": columns
    }


def show_workflow(filepath: str):
    """Display enrichment workflow visualization."""

    console.print("\n")

    # Load data
    with console.status("[cyan]Analyzing enrichment workflow...", spinner="dots"):
        rows, headers, err = load_csv(filepath)
        if err:
            console.print(f"\n[red]❌ {err}[/red]\n")
            sys.exit(1)

    # Infer integrations
    integrations = infer_integrations(headers)

    if not integrations:
        console.print("[yellow]⚠️  No enrichment integrations detected in this file.[/yellow]\n")
        sys.exit(0)

    # Calculate stats
    stats = {}
    for integration, columns in integrations.items():
        stats[integration] = calculate_integration_stats(rows, integration, columns)

    # Show header
    console.rule("[bold blue]ENRICHMENT WORKFLOW[/bold blue]", style="blue")
    console.print()

    # File info
    info_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    info_table.add_column("Key", style="cyan")
    info_table.add_column("Value", style="white")
    info_table.add_row("File", filepath)
    info_table.add_row("Total Rows", str(len(rows)))
    info_table.add_row("Integrations Detected", str(len(integrations)))
    info_table.add_row("Total Columns", str(len(headers)))

    console.print(info_table)
    console.print()

    # Pipeline visualization
    console.print("[bold cyan]📊 Enrichment Pipeline:[/bold cyan]\n")

    tree = Tree("📥 [bold]Input CSV[/bold]")

    # Group by category
    linkedin_integrations = {k: v for k, v in integrations.items() if k.startswith("linkedin_")}
    heyreach_integrations = {k: v for k, v in integrations.items() if k.startswith("heyreach_")}
    other_integrations = {k: v for k, v in integrations.items() if not k.startswith(("linkedin_", "heyreach_"))}

    if linkedin_integrations:
        linkedin_branch = tree.add("🔵 [bold blue]LinkedIn Integrations[/bold blue]")
        for integration, columns in linkedin_integrations.items():
            integration_stats = stats[integration]
            success_rate = integration_stats["success_rate"]

            # Color based on success rate
            if success_rate >= 80:
                color = "green"
                icon = "✅"
            elif success_rate >= 50:
                color = "yellow"
                icon = "⚠️"
            else:
                color = "red"
                icon = "❌"

            label = f"{icon} [{color}]{integration}[/{color}] ({integration_stats['populated']}/{integration_stats['total']} rows, {success_rate:.1f}%)"
            integration_branch = linkedin_branch.add(label)

            for col in columns:
                integration_branch.add(f"└─ {col}")

    if heyreach_integrations:
        heyreach_branch = tree.add("🟠 [bold yellow]HeyReach Integrations[/bold yellow]")
        for integration, columns in heyreach_integrations.items():
            integration_stats = stats[integration]
            success_rate = integration_stats["success_rate"]

            if success_rate >= 80:
                color = "green"
                icon = "✅"
            elif success_rate >= 50:
                color = "yellow"
                icon = "⚠️"
            else:
                color = "red"
                icon = "❌"

            label = f"{icon} [{color}]{integration}[/{color}] ({integration_stats['populated']}/{integration_stats['total']} rows, {success_rate:.1f}%)"
            integration_branch = heyreach_branch.add(label)

            for col in columns:
                integration_branch.add(f"└─ {col}")

    if other_integrations:
        other_branch = tree.add("🔧 [bold magenta]Other Integrations[/bold magenta]")
        for integration, columns in other_integrations.items():
            integration_stats = stats[integration]
            success_rate = integration_stats["success_rate"]

            if success_rate >= 80:
                color = "green"
                icon = "✅"
            elif success_rate >= 50:
                color = "yellow"
                icon = "⚠️"
            else:
                color = "red"
                icon = "❌"

            label = f"{icon} [{color}]{integration}[/{color}] ({integration_stats['populated']}/{integration_stats['total']} rows, {success_rate:.1f}%)"
            integration_branch = other_branch.add(label)

            for col in columns:
                integration_branch.add(f"└─ {col}")

    output_branch = tree.add("📤 [bold green]Enriched CSV[/bold green]")
    output_branch.add(f"✓ {len(rows)} rows enriched")
    output_branch.add(f"✓ {sum(len(cols) for cols in integrations.values())} new columns added")

    console.print(tree)
    console.print()

    # Summary statistics table
    console.print("[bold cyan]📈 Integration Performance:[/bold cyan]\n")

    perf_table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    perf_table.add_column("Integration", style="cyan")
    perf_table.add_column("Populated", style="green", justify="right")
    perf_table.add_column("Empty", style="red", justify="right")
    perf_table.add_column("Success Rate", style="yellow", justify="right")
    perf_table.add_column("Columns", style="white", justify="right")

    for integration, integration_stats in stats.items():
        success_rate = integration_stats["success_rate"]

        # Format with color
        if success_rate >= 80:
            rate_str = f"[green]{success_rate:.1f}%[/green]"
        elif success_rate >= 50:
            rate_str = f"[yellow]{success_rate:.1f}%[/yellow]"
        else:
            rate_str = f"[red]{success_rate:.1f}%[/red]"

        perf_table.add_row(
            integration,
            str(integration_stats["populated"]),
            str(integration_stats["empty"]),
            rate_str,
            str(len(integration_stats["columns"]))
        )

    console.print(perf_table)
    console.print()

    # Overall summary
    total_populated = sum(s["populated"] for s in stats.values())
    total_possible = len(stats) * len(rows)
    overall_rate = (total_populated / total_possible * 100) if total_possible > 0 else 0

    summary_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="white")

    summary_table.add_row("Overall Success Rate", f"{overall_rate:.1f}%")
    summary_table.add_row("Total Integration Runs", str(len(stats) * len(rows)))
    summary_table.add_row("Successful Runs", str(total_populated))
    summary_table.add_row("Failed/Empty Runs", str(total_possible - total_populated))

    console.print(Panel(summary_table, title="[bold green]Overall Statistics[/bold green]", border_style="green"))
    console.print()


def main():
    parser = argparse.ArgumentParser(description="Enrichment workflow visualizer")
    parser.add_argument("file", help="Path to enriched CSV file")

    args = parser.parse_args()

    show_workflow(args.file)


if __name__ == "__main__":
    main()
