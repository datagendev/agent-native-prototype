#!/usr/bin/env python3
"""
Batch Enrichment Orchestrator

Enriches CSV data with multiple integrations in parallel.

Usage:
    python batch_enrich.py --input leads.csv --integrations linkedin_profile
    python batch_enrich.py --input leads.csv --integrations linkedin_profile,web_research
    python batch_enrich.py --input leads.csv --integrations linkedin_profile --parallel 10 --output enriched.csv
    python batch_enrich.py --input leads_enriched.csv --integrations linkedin_profile,heyreach_engagement --skip-existing

Arguments:
    --input: Input CSV file path
    --integrations: Comma-separated list of integration names
    --parallel: Number of parallel workers (default: 5)
    --output: Output CSV file path (default: input_enriched.csv)
    --skip-existing: Skip integrations if their output columns already have data (saves API calls)
"""

import argparse
import csv
import importlib
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich import box

# Add integrations directory to path
sys.path.insert(0, str(Path(__file__).parent))

from integrations import list_integrations, get_integration

# Initialize rich console
console = Console()


def load_csv(filepath: str) -> tuple[List[Dict[str, Any]], List[str], str]:
    """
    Load CSV file.

    Returns:
        (rows, headers, error) tuple
        - Success: (rows_list, headers_list, "")
        - Failure: ([], [], "error message")
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            rows = list(reader)
        return rows, headers, ""
    except Exception as e:
        return [], [], f"load_csv error: {str(e)}"


def save_csv(filepath: str, rows: List[Dict[str, Any]], headers: List[str]) -> str:
    """
    Save rows to CSV file.

    Returns:
        error string ("" for success)
    """
    try:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        return ""
    except Exception as e:
        return f"save_csv error: {str(e)}"


def validate_integrations(integration_names: List[str]) -> tuple[List[Any], str]:
    """
    Validate and load integration modules.

    Returns:
        (modules_list, error) tuple
        - Success: (modules, "")
        - Failure: ([], "error message")
    """
    available = list_integrations()
    modules = []

    for name in integration_names:
        if name not in available:
            return [], f"Integration '{name}' not found. Available: {', '.join(available.keys())}"

        try:
            module = importlib.import_module(f"integrations.{name}")
            if not hasattr(module, 'enrich'):
                return [], f"Integration '{name}' missing enrich() function"
            modules.append({
                "name": name,
                "module": module,
                "metadata": available[name]
            })
        except Exception as e:
            return [], f"Failed to load integration '{name}': {str(e)}"

    return modules, ""


def validate_columns(headers: List[str], integrations: List[Dict]) -> str:
    """
    Validate that required input columns exist.

    Returns:
        error string ("" for success)
    """
    for integration in integrations:
        required = integration["metadata"]["input"]
        missing = [col for col in required if col not in headers]
        if missing:
            return f"Integration '{integration['name']}' requires columns: {missing} (not found in CSV)"
    return ""


def should_skip_integration(row: Dict[str, Any], integration: Dict, skip_existing: bool) -> bool:
    """
    Determine if integration should be skipped for this row.

    Args:
        row: Current row data
        integration: Integration metadata
        skip_existing: Whether to skip if output columns already populated

    Returns:
        True if should skip, False if should run
    """
    if not skip_existing:
        return False

    # Check if all output columns exist and have non-empty values
    output_cols = integration["metadata"]["output"]

    for col in output_cols:
        value = row.get(col)
        # Skip if column missing or empty
        if not value or (isinstance(value, str) and value.strip() == ""):
            return False  # Need to run integration

    # All output columns already populated
    return True


def enrich_row(row: Dict[str, Any], integrations: List[Dict], skip_existing: bool = False) -> tuple[Dict[str, Any], Dict[str, str], Dict[str, bool]]:
    """
    Enrich a single row with all integrations.

    Args:
        row: Row data to enrich
        integrations: List of integration metadata
        skip_existing: If True, skip integrations whose output columns already have data

    Returns:
        (enriched_row, errors_by_integration, skipped_by_integration) tuple
    """
    enriched = row.copy()
    errors = {}
    skipped = {}

    for integration in integrations:
        name = integration["name"]
        module = integration["module"]

        # Check if we should skip this integration
        if should_skip_integration(enriched, integration, skip_existing):
            skipped[name] = True
            continue

        # Call integration's enrich function
        result, error = module.enrich(enriched)

        if error:
            errors[name] = error
        else:
            # Merge enriched fields into row
            enriched.update(result)

    return enriched, errors, skipped


def create_stats_table(success: int, errors: int, total: int, recent_rows: List[tuple]) -> Table:
    """Create a live stats table showing current progress."""
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Value", style="bold white", width=20)

    # Overall stats
    table.add_row("Total Rows", str(total))
    table.add_row("Completed", str(success + errors))
    table.add_row("✅ Success", f"[green]{success}[/green]")
    table.add_row("❌ Errors", f"[red]{errors}[/red]")

    success_rate = (success / (success + errors) * 100) if (success + errors) > 0 else 0
    table.add_row("Success Rate", f"{success_rate:.1f}%")

    # Recent rows section
    if recent_rows:
        table.add_row("", "")  # Spacer
        table.add_row("[bold]Recent Rows[/bold]", "")
        for row_idx, status, name in recent_rows[-5:]:  # Last 5 rows
            status_icon = "✅" if status == "success" else "❌"
            color = "green" if status == "success" else "red"
            table.add_row(f"  Row {row_idx}", f"[{color}]{status_icon} {name[:30]}[/{color}]")

    return table


def run_batch(
    input_path: str,
    integration_names: List[str],
    parallel: int = 5,
    output_path: str = None,
    skip_existing: bool = False
) -> tuple[Dict[str, Any], str]:
    """
    Run batch enrichment with rich terminal UI.

    Returns:
        (stats, error) tuple
        - Success: (stats_dict, "")
        - Failure: ({}, "error message")
    """
    console.print("\n")
    console.rule("[bold blue]BATCH ENRICHMENT[/bold blue]", style="blue")
    console.print()

    # Print config
    config_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    config_table.add_column("Key", style="cyan")
    config_table.add_column("Value", style="white")
    config_table.add_row("Input File", input_path)
    config_table.add_row("Integrations", ", ".join(integration_names))
    config_table.add_row("Parallel Workers", str(parallel))
    if skip_existing:
        config_table.add_row("Skip Existing", "[yellow]Yes - will skip integrations with existing data[/yellow]")
    console.print(config_table)
    console.print()

    # Load CSV
    with console.status("[cyan]Loading CSV...", spinner="dots"):
        rows, headers, err = load_csv(input_path)
        if err:
            return {}, err
    console.print(f"✓ Loaded [bold]{len(rows)}[/bold] rows with [bold]{len(headers)}[/bold] columns", style="green")

    # Validate integrations
    with console.status("[cyan]Validating integrations...", spinner="dots"):
        integrations, err = validate_integrations(integration_names)
        if err:
            return {}, err
    console.print(f"✓ Loaded [bold]{len(integrations)}[/bold] integrations", style="green")

    # Validate columns
    with console.status("[cyan]Validating columns...", spinner="dots"):
        err = validate_columns(headers, integrations)
        if err:
            return {}, err
    console.print("✓ All required columns present", style="green")
    console.print()

    # Collect all output columns
    all_output_cols = []
    for integration in integrations:
        all_output_cols.extend(integration["metadata"]["output"])
    new_headers = headers + [col for col in all_output_cols if col not in headers]

    # Enrich rows in parallel with rich progress
    enriched_rows = []
    all_errors = {}
    all_skipped = {}  # Track skipped integrations per row
    success_count = 0
    error_count = 0
    skipped_count = 0
    recent_rows = []  # Track recent rows for display

    start_time = datetime.now()

    # Create progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        task = progress.add_task(
            f"[cyan]Enriching rows ({parallel} workers)...",
            total=len(rows)
        )

        with ThreadPoolExecutor(max_workers=parallel) as executor:
            # Submit all tasks with skip_existing flag
            futures = {executor.submit(enrich_row, row, integrations, skip_existing): i for i, row in enumerate(rows)}

            # Process results as they complete
            for future in as_completed(futures):
                row_idx = futures[future]
                try:
                    enriched, errors, skipped = future.result()
                    enriched_rows.append((row_idx, enriched))

                    # Get row identifier for display
                    row_name = enriched.get("name") or enriched.get("email") or enriched.get("linkedin_url", "Unknown")

                    # Track skipped integrations
                    if skipped:
                        all_skipped[row_idx] = skipped
                        skipped_count += len(skipped)

                    if errors:
                        error_count += 1
                        all_errors[row_idx] = errors
                        recent_rows.append((row_idx, "error", row_name))
                    else:
                        success_count += 1
                        recent_rows.append((row_idx, "success", row_name))

                    # Update progress with skip count
                    skip_info = f" [yellow]⊘ {skipped_count} skipped[/yellow]" if skip_existing and skipped_count > 0 else ""
                    progress.update(
                        task,
                        advance=1,
                        description=f"[cyan]Enriching rows ([green]{success_count}[/green] ✓ / [red]{error_count}[/red] ✗{skip_info})"
                    )

                except Exception as e:
                    error_count += 1
                    all_errors[row_idx] = {"system": str(e)}
                    recent_rows.append((row_idx, "error", "System error"))
                    progress.update(task, advance=1)

    elapsed_time = (datetime.now() - start_time).total_seconds()

    # Sort by original order
    enriched_rows.sort(key=lambda x: x[0])
    final_rows = [row for _, row in enriched_rows]

    console.print()
    console.print(f"✓ Enrichment complete in [bold]{elapsed_time:.1f}s[/bold]", style="green")
    console.print()

    # Save output
    if not output_path:
        input_pathobj = Path(input_path)
        output_path = str(input_pathobj.parent / f"{input_pathobj.stem}_enriched{input_pathobj.suffix}")

    with console.status(f"[cyan]Saving to {output_path}...", spinner="dots"):
        err = save_csv(output_path, final_rows, new_headers)
        if err:
            return {}, err
    console.print(f"✓ Saved [bold]{len(final_rows)}[/bold] rows", style="green")
    console.print()

    # Print skipped integrations summary if any
    if all_skipped and skip_existing:
        console.print("[yellow]ℹ️  Skipped integrations (already populated):[/yellow]")
        skip_table = Table(box=box.SIMPLE, show_header=True, header_style="bold yellow")
        skip_table.add_column("Row", style="cyan", width=10)
        skip_table.add_column("Skipped", style="yellow")

        for row_idx, skipped in list(all_skipped.items())[:5]:  # Show first 5
            skipped_names = ", ".join(skipped.keys())
            row_name = enriched_rows[row_idx][1].get("name", f"Row {row_idx}")
            skip_table.add_row(row_name[:20], skipped_names)

        console.print(skip_table)

        if len(all_skipped) > 5:
            console.print(f"[yellow]... and {len(all_skipped) - 5} more rows with skipped integrations[/yellow]")
        console.print()

    # Print error summary if any
    if all_errors:
        console.print("[yellow]⚠️  Errors occurred:[/yellow]")
        error_table = Table(box=box.SIMPLE, show_header=True, header_style="bold yellow")
        error_table.add_column("Row", style="cyan", width=10)
        error_table.add_column("Error", style="red")

        for row_idx, errors in list(all_errors.items())[:5]:  # Show first 5
            error_msg = ", ".join([f"{k}: {v}" for k, v in errors.items()])
            error_table.add_row(str(row_idx), error_msg[:80])

        console.print(error_table)

        if len(all_errors) > 5:
            console.print(f"[yellow]... and {len(all_errors) - 5} more errors[/yellow]")
        console.print()

    stats = {
        "total_rows": len(rows),
        "success": success_count,
        "errors": error_count,
        "skipped": skipped_count,
        "output_path": output_path,
        "new_columns": [col for col in all_output_cols if col not in headers],
        "elapsed_time": elapsed_time
    }

    # Final summary
    console.rule("[bold green]COMPLETE[/bold green]", style="green")
    console.print()

    summary_table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    summary_table.add_column("Metric", style="cyan", width=25)
    summary_table.add_column("Value", style="white")

    summary_table.add_row("✅ Successfully Enriched", f"[green]{success_count}/{len(rows)}[/green] rows")
    if skip_existing and skipped_count > 0:
        summary_table.add_row("⊘ Integrations Skipped", f"[yellow]{skipped_count}[/yellow] (already populated)")
    summary_table.add_row("📊 New Columns Added", f"{len(stats['new_columns'])}")
    summary_table.add_row("   Columns", ", ".join(stats['new_columns'][:5]) + ("..." if len(stats['new_columns']) > 5 else ""))
    summary_table.add_row("⏱️  Time Elapsed", f"{elapsed_time:.1f}s")
    summary_table.add_row("⚡ Throughput", f"{len(rows)/elapsed_time:.1f} rows/sec")
    summary_table.add_row("📂 Output File", output_path)

    console.print(summary_table)
    console.print()

    return stats, ""


def main():
    parser = argparse.ArgumentParser(description="Batch enrichment orchestrator with rich terminal UI")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--integrations", required=True, help="Comma-separated list of integration names")
    parser.add_argument("--parallel", type=int, default=5, help="Number of parallel workers (default: 5)")
    parser.add_argument("--output", help="Output CSV file path (default: input_enriched.csv)")
    parser.add_argument("--skip-existing", action="store_true",
                       help="Skip integrations if their output columns already have data (saves API calls)")

    args = parser.parse_args()

    # Parse integrations
    integration_names = [name.strip() for name in args.integrations.split(",")]

    # Run batch enrichment
    stats, err = run_batch(
        input_path=args.input,
        integration_names=integration_names,
        parallel=args.parallel,
        output_path=args.output,
        skip_existing=args.skip_existing
    )

    if err:
        console.print(f"\n[bold red]❌ Error:[/bold red] {err}\n", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
