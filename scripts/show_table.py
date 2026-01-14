#!/usr/bin/env python3
"""
Show Table - Interactive CSV table viewer

Displays enriched lead data in an interactive terminal table with sorting, filtering, and pagination.

Usage:
    python show_table.py <csv_file>
    python show_table.py lead-list/gtm-influencers_enriched.csv
    python show_table.py lead-list/gtm-influencers_enriched.csv --columns name,headline,follower_count
    python show_table.py lead-list/gtm-influencers_enriched.csv --filter "follower_count>10000"
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Dict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

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


def filter_rows(rows: List[Dict], filter_expr: str) -> List[Dict]:
    """Apply simple filter expression."""
    if not filter_expr:
        return rows

    # Simple filters: column>value, column<value, column=value, column!=value
    try:
        if ">" in filter_expr:
            col, val = filter_expr.split(">")
            return [r for r in rows if r.get(col.strip()) and float(r[col.strip()]) > float(val.strip())]
        elif "<" in filter_expr:
            col, val = filter_expr.split("<")
            return [r for r in rows if r.get(col.strip()) and float(r[col.strip()]) < float(val.strip())]
        elif "!=" in filter_expr:
            col, val = filter_expr.split("!=")
            return [r for r in rows if r.get(col.strip(), "").lower() != val.strip().lower()]
        elif "=" in filter_expr:
            col, val = filter_expr.split("=")
            return [r for r in rows if r.get(col.strip(), "").lower() == val.strip().lower()]
        else:
            console.print(f"[yellow]⚠️  Invalid filter: {filter_expr}[/yellow]")
            return rows
    except Exception as e:
        console.print(f"[yellow]⚠️  Filter error: {e}[/yellow]")
        return rows


def truncate_value(value: str, max_len: int = 30) -> str:
    """Truncate long values."""
    if len(value) > max_len:
        return value[:max_len-3] + "..."
    return value


def show_table(
    filepath: str,
    columns: List[str] = None,
    limit: int = 50,
    filter_expr: str = None,
    show_stats: bool = True
):
    """Display CSV data as a rich table."""

    # Load data
    console.print("\n")
    with console.status("[cyan]Loading data...", spinner="dots"):
        rows, headers, err = load_csv(filepath)
        if err:
            console.print(f"\n[red]❌ {err}[/red]\n")
            sys.exit(1)

    # Apply filter
    if filter_expr:
        rows = filter_rows(rows, filter_expr)

    # Select columns
    display_cols = columns if columns else headers

    # Show file info
    info_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    info_table.add_column("Key", style="cyan")
    info_table.add_column("Value", style="white")
    info_table.add_row("File", filepath)
    info_table.add_row("Total Rows", str(len(rows)))
    info_table.add_row("Total Columns", str(len(headers)))
    info_table.add_row("Displaying Columns", str(len(display_cols)))
    if filter_expr:
        info_table.add_row("Filter", filter_expr)

    console.print(Panel(info_table, title="[bold blue]CSV Table View[/bold blue]", border_style="blue"))
    console.print()

    # Show column statistics
    if show_stats:
        stats_table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        stats_table.add_column("Column", style="cyan")
        stats_table.add_column("Populated", style="green")
        stats_table.add_column("Empty", style="red")
        stats_table.add_column("Fill Rate", style="yellow")

        for col in display_cols:
            populated = sum(1 for r in rows if r.get(col) and r[col].strip())
            empty = len(rows) - populated
            fill_rate = (populated / len(rows) * 100) if len(rows) > 0 else 0

            stats_table.add_row(
                col,
                str(populated),
                str(empty),
                f"{fill_rate:.1f}%"
            )

        console.print(stats_table)
        console.print()

    # Show data table
    data_table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold magenta")

    for col in display_cols:
        data_table.add_column(col, overflow="fold")

    # Add rows (with limit)
    for i, row in enumerate(rows[:limit]):
        values = [truncate_value(str(row.get(col, ""))) for col in display_cols]
        data_table.add_row(*values)

    console.print(data_table)

    # Show pagination info
    if len(rows) > limit:
        console.print(f"\n[yellow]Showing first {limit} of {len(rows)} rows. Use --limit to show more.[/yellow]")

    console.print()


def main():
    parser = argparse.ArgumentParser(description="Interactive CSV table viewer")
    parser.add_argument("file", help="Path to CSV file")
    parser.add_argument("--columns", help="Comma-separated list of columns to display (default: all)")
    parser.add_argument("--limit", type=int, default=50, help="Number of rows to display (default: 50)")
    parser.add_argument("--filter", help="Filter expression (e.g., 'follower_count>10000')")
    parser.add_argument("--no-stats", action="store_true", help="Hide column statistics")

    args = parser.parse_args()

    columns = [c.strip() for c in args.columns.split(",")] if args.columns else None

    show_table(
        filepath=args.file,
        columns=columns,
        limit=args.limit,
        filter_expr=args.filter,
        show_stats=not args.no_stats
    )


if __name__ == "__main__":
    main()
