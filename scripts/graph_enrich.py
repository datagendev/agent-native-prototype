#!/usr/bin/env python3
"""
Graph-based Enrichment Executor

Execute enrichment graphs on lead tables.
New architecture: Primitives -> Nodes -> Workflows -> Batch Execution

Usage:
    # List available nodes and workflows
    python graph_enrich.py --lead example-leads --list

    # Show graph definition (YAML)
    python graph_enrich.py --lead example-leads --show-graph

    # Preview a single node
    python graph_enrich.py --lead example-leads --graph keyword_mentions --preview --limit 3

    # Run a workflow (sequence of nodes)
    python graph_enrich.py --lead example-leads --workflow full_enrichment --preview

    # Run full batch with workflow
    python graph_enrich.py --lead example-leads --workflow claude_mentions

    # With custom config (for configurable nodes)
    python graph_enrich.py --lead example-leads --graph keyword_mentions --config '{"keywords": ["datagen"], "output_prefix": "datagen"}'
"""

import argparse
import csv
import importlib
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Import database module
from db import LeadDB

# Rich terminal UI (optional but recommended)
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


def _stable_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _node_name(node, fallback: str) -> str:
    return getattr(node, "_node_name", None) or fallback


def _node_config_for_hash(node) -> dict:
    """
    Best-effort config snapshot for hashing/audit.

    Includes any explicit _node_config (from graph loader) plus public instance attrs.
    """
    cfg = {}

    explicit = getattr(node, "_node_config", None)
    if isinstance(explicit, dict):
        cfg.update(explicit)

    # Capture public attrs (avoid private fields used by executor)
    for k, v in getattr(node, "__dict__", {}).items():
        if k.startswith("_"):
            continue
        if callable(v):
            continue
        cfg[k] = v

    # Executor-level modifiers (affect semantics)
    input_map = getattr(node, "_input_map", None)
    if isinstance(input_map, dict) and input_map:
        cfg["_input_map"] = input_map

    output_prefix = getattr(node, "_output_prefix", None)
    if output_prefix:
        cfg["_output_prefix"] = output_prefix

    cfg["_class"] = f"{node.__class__.__module__}.{node.__class__.__name__}"
    return cfg


def _build_node_input_row(row_data: dict, node_input_map: dict) -> dict:
    """
    Build a per-node input row without mutating row_data.

    node_input_map maps expected_input_col -> source_col_in_row_data.
    """
    input_row = row_data.copy()
    if not node_input_map:
        return input_row

    for dest_col, source_col in node_input_map.items():
        input_row[dest_col] = row_data.get(source_col, "")
    return input_row


def _apply_output_prefix(result: dict, output_prefix: str | None) -> dict:
    if not output_prefix:
        return result

    prefixed = {}
    for k, v in result.items():
        if isinstance(k, str) and k.startswith(f"{output_prefix}_"):
            prefixed[k] = v
        else:
            prefixed[f"{output_prefix}_{k}"] = v
    return prefixed


def _cache_key(node_name: str, input_hash: str, config_hash: str) -> str:
    return f"{node_name}:{input_hash}:{config_hash}"


def _hash_inputs(node_input_cols: list[str], input_row: dict) -> str:
    payload = {col: input_row.get(col, None) for col in node_input_cols}
    return _sha256(_stable_json(payload))


def _hash_config(node) -> str:
    return _sha256(_stable_json(_node_config_for_hash(node)))


def _should_overwrite(existing_value, overwrite: bool) -> bool:
    if overwrite:
        return True
    if existing_value is None:
        return True
    if isinstance(existing_value, str) and existing_value.strip() == "":
        return True
    return False


def get_leads_dir() -> Path:
    """Get the leads directory."""
    return Path(__file__).parent.parent / "leads"


def get_lead_path(lead_name: str) -> Path:
    """Get path to a specific lead table."""
    return get_leads_dir() / lead_name


def init_lead_db(lead_name: str, csv_path: Path) -> tuple[LeadDB, str]:
    """
    Initialize lead database from CSV.
    Auto-imports CSV on first run if DB is empty.

    Args:
        lead_name: Name of the lead table
        csv_path: Path to source CSV file

    Returns:
        (db, error): LeadDB instance and error message
    """
    lead_path = get_lead_path(lead_name)
    db_path = lead_path / "table.db"

    db = LeadDB(db_path)
    err = db.connect()
    if err:
        return None, err

    err = db.init_schema()
    if err:
        return None, err

    # Check if DB is empty (first run)
    rows, err = db.get_rows(limit=1)
    if err:
        return None, err

    if not rows:
        # Import from CSV
        if not csv_path.exists():
            return None, f"CSV not found: {csv_path}"

        csv_rows = load_csv(csv_path)
        count, err = db.import_csv(csv_rows)
        if err:
            return None, err

        if RICH_AVAILABLE:
            console.print(f"[green]Imported {count} rows from CSV to database[/green]")
        else:
            print(f"Imported {count} rows from CSV to database")

    return db, ""


def load_graph(lead_name: str, graph_name: str, config: dict = None):
    """
    Dynamically load a graph class from leads/{lead_name}/graph/

    Args:
        lead_name: Name of the lead table directory
        graph_name: Name of the graph to load
        config: Optional config dict to pass to graph constructor

    Returns:
        Instantiated graph object
    """
    lead_path = get_lead_path(lead_name)
    graph_module_path = lead_path / "graph"

    if not graph_module_path.exists():
        raise FileNotFoundError(f"Graph directory not found: {graph_module_path}")

    # Add to Python path for imports
    sys.path.insert(0, str(lead_path.parent))

    # Import the graph module
    try:
        graph_module = importlib.import_module(f"{lead_name}.graph")
        graphs = getattr(graph_module, "GRAPHS", {})

        if graph_name not in graphs:
            available = ", ".join(graphs.keys())
            raise ValueError(f"Graph '{graph_name}' not found. Available: {available}")

        GraphClass = graphs[graph_name]

        # Instantiate with config if provided
        if config:
            return GraphClass(**config)
        return GraphClass()

    except ModuleNotFoundError as e:
        raise ImportError(f"Failed to import graph module: {e}")


def list_graphs(lead_name: str) -> dict:
    """List all available nodes for a lead table."""
    lead_path = get_lead_path(lead_name)
    graph_init = lead_path / "graph" / "__init__.py"

    if not graph_init.exists():
        return {}

    sys.path.insert(0, str(lead_path.parent))

    try:
        graph_module = importlib.import_module(f"{lead_name}.graph")
        graphs = getattr(graph_module, "GRAPHS", {})

        result = {}
        for name, cls in graphs.items():
            instance = cls()
            result[name] = {
                "description": instance.description,
                "input_cols": instance.input_cols,
                "output_cols": instance.output_cols
            }
        return result
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[red]Error loading graphs: {e}[/red]")
        else:
            print(f"Error loading graphs: {e}")
        return {}


def list_workflows(lead_name: str) -> dict:
    """List all available workflows for a lead table."""
    lead_path = get_lead_path(lead_name)
    sys.path.insert(0, str(lead_path.parent))

    try:
        graph_module = importlib.import_module(f"{lead_name}.graph")
        get_workflows = getattr(graph_module, "get_workflows", None)
        if get_workflows:
            return get_workflows()
        return {}
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[red]Error loading workflows: {e}[/red]")
        else:
            print(f"Error loading workflows: {e}")
        return {}


def load_workflow(lead_name: str, workflow_name: str) -> list:
    """Load a workflow as a list of configured nodes."""
    lead_path = get_lead_path(lead_name)
    sys.path.insert(0, str(lead_path.parent))

    try:
        graph_module = importlib.import_module(f"{lead_name}.graph")
        load_workflow_fn = getattr(graph_module, "load_workflow", None)
        if load_workflow_fn:
            return load_workflow_fn(workflow_name)
        raise ValueError(f"Workflow loading not supported for {lead_name}")
    except Exception as e:
        raise ValueError(f"Failed to load workflow '{workflow_name}': {e}")


def show_graph_definition(lead_name: str):
    """Display the graph.yaml definition."""
    lead_path = get_lead_path(lead_name)
    graph_yaml = lead_path / "graph" / "graph.yaml"

    if not graph_yaml.exists():
        if RICH_AVAILABLE:
            console.print(f"[yellow]No graph.yaml found at {graph_yaml}[/yellow]")
        else:
            print(f"No graph.yaml found at {graph_yaml}")
        return

    with open(graph_yaml, "r") as f:
        content = f.read()

    if RICH_AVAILABLE:
        from rich.syntax import Syntax
        console.print(Panel.fit(f"[bold]Graph Definition: {lead_name}[/bold]", border_style="blue"))
        syntax = Syntax(content, "yaml", theme="monokai", line_numbers=True)
        console.print(syntax)
    else:
        print(f"\n=== Graph Definition: {lead_name} ===\n")
        print(content)


def load_csv(csv_path: Path) -> list[dict]:
    """Load CSV file into list of dicts."""
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_csv(csv_path: Path, rows: list[dict], fieldnames: list[str]):
    """Save list of dicts to CSV file."""
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_header(text: str):
    """Print a header line."""
    if RICH_AVAILABLE:
        console.print(Panel.fit(f"[bold]{text}[/bold]", border_style="blue"))
    else:
        print(f"\n{'=' * 60}")
        print(f"  {text}")
        print('=' * 60)


def print_info(key: str, value: str, color: str = "cyan"):
    """Print a key-value info line."""
    if RICH_AVAILABLE:
        console.print(f"{key}: [{color}]{value}[/{color}]")
    else:
        print(f"{key}: {value}")


def run_preview(lead_name: str, graph_name: str, limit: int = 3, config: dict = None):
    """Run graph on first N rows and show detailed output."""
    lead_path = get_lead_path(lead_name)
    csv_path = lead_path / "table.csv"

    if not csv_path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]Error: CSV not found at {csv_path}[/red]")
        else:
            print(f"Error: CSV not found at {csv_path}")
        return False

    # Load graph
    graph = load_graph(lead_name, graph_name, config)

    # Load data
    rows = load_csv(csv_path)

    print_header(f"ENRICHMENT PREVIEW: {graph_name}")
    print_info("Lead Table", f"{csv_path} ({len(rows)} rows)")
    print_info("Graph", f"{lead_path}/graph/{graph_name}.py")
    print_info("Input Columns", ", ".join(graph.input_cols), "green")
    print_info("Output Columns", ", ".join(graph.output_cols), "yellow")

    if RICH_AVAILABLE:
        console.print("=" * 60)
    else:
        print("=" * 60)

    # Run on preview rows
    success = 0
    partial = 0
    failed = 0

    for i, row in enumerate(rows[:limit]):
        if RICH_AVAILABLE:
            console.print(f"\n[bold]Row {i+1}/{limit}:[/bold]")
            for col in graph.input_cols:
                console.print(f"  {col} = [cyan]{row.get(col, '?')}[/cyan]")
        else:
            print(f"\nRow {i+1}/{limit}:")
            for col in graph.input_cols:
                print(f"  {col} = {row.get(col, '?')}")

        # Run graph
        result, err = graph(row)

        if err:
            if result:
                partial += 1
                status = "[yellow]PARTIAL[/yellow]" if RICH_AVAILABLE else "PARTIAL"
            else:
                failed += 1
                status = "[red]FAILED[/red]" if RICH_AVAILABLE else "FAILED"

            if RICH_AVAILABLE:
                console.print(f"  Error: [red]{err}[/red]")
            else:
                print(f"  Error: {err}")
        else:
            success += 1
            status = "[green]SUCCESS[/green]" if RICH_AVAILABLE else "SUCCESS"

        # Show output
        for col in graph.output_cols:
            val = result.get(col, "")
            # Truncate long values
            val_str = str(val)[:80] + "..." if len(str(val)) > 80 else str(val)
            if RICH_AVAILABLE:
                console.print(f"  -> {col}: [yellow]{val_str}[/yellow]")
            else:
                print(f"  -> {col}: {val_str}")

        if RICH_AVAILABLE:
            console.print(f"  Status: {status}")
        else:
            print(f"  Status: {status}")

    # Summary
    if RICH_AVAILABLE:
        console.print("\n" + "=" * 60)
        console.print(f"Preview Complete: [green]{success}[/green] successful, [yellow]{partial}[/yellow] partial, [red]{failed}[/red] failed")
        console.print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print(f"Preview Complete: {success} successful, {partial} partial, {failed} failed")
        print("=" * 60)

    return True


def run_batch_csv(lead_name: str, graph_name: str, output_path: str = None, parallel: int = 5, config: dict = None):
    """Run graph on all rows and save enriched CSV (CSV-only mode, legacy)."""
    lead_path = get_lead_path(lead_name)
    csv_path = lead_path / "table.csv"

    if not csv_path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]Error: CSV not found at {csv_path}[/red]")
        else:
            print(f"Error: CSV not found at {csv_path}")
        return False

    # Load graph
    graph = load_graph(lead_name, graph_name, config)

    # Load data
    rows = load_csv(csv_path)
    total = len(rows)

    print_header(f"BATCH ENRICHMENT: {graph_name}")
    print_info("Lead Table", f"{csv_path} ({total} rows)")
    print_info("Parallel Workers", str(parallel))

    # Determine output columns
    existing_cols = list(rows[0].keys()) if rows else []
    new_cols = [c for c in graph.output_cols if c not in existing_cols]
    all_cols = existing_cols + new_cols

    # Process rows
    enriched_rows = []
    success = 0
    failed = 0
    start_time = datetime.now()

    def process_row(idx_row):
        idx, row = idx_row
        result, err = graph(row)
        for col in graph.output_cols:
            row[col] = result.get(col, "")
        return idx, row, err

    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("*"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Enriching ({parallel} workers)...", total=total)

            with ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = {executor.submit(process_row, (i, row)): i for i, row in enumerate(rows)}

                for future in as_completed(futures):
                    idx, enriched_row, err = future.result()
                    enriched_rows.append((idx, enriched_row))

                    if err and not any(enriched_row.get(c) for c in graph.output_cols):
                        failed += 1
                    else:
                        success += 1

                    progress.update(
                        task,
                        advance=1,
                        description=f"[cyan]Enriching ([green]{success}[/green] OK / [red]{failed}[/red] err)"
                    )
    else:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(process_row, (i, row)): i for i, row in enumerate(rows)}

            for i, future in enumerate(as_completed(futures)):
                idx, enriched_row, err = future.result()
                enriched_rows.append((idx, enriched_row))

                if err and not any(enriched_row.get(c) for c in graph.output_cols):
                    failed += 1
                else:
                    success += 1

                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{total}...")

    # Sort by original order
    enriched_rows.sort(key=lambda x: x[0])
    final_rows = [row for _, row in enriched_rows]

    elapsed = (datetime.now() - start_time).total_seconds()

    # Save output
    if output_path:
        out_path = Path(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = lead_path / f"table_enriched_{graph_name}_{timestamp}.csv"

    save_csv(out_path, final_rows, all_cols)

    # Summary
    if RICH_AVAILABLE:
        console.print()
        console.rule("[bold green]COMPLETE[/bold green]", style="green")
        console.print()

        summary = Table(box=box.ROUNDED, show_header=False)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value")

        summary.add_row("Rows Processed", f"[green]{success}[/green] / {total}")
        summary.add_row("Errors", f"[red]{failed}[/red]")
        summary.add_row("New Columns", ", ".join(new_cols))
        summary.add_row("Time Elapsed", f"{elapsed:.1f}s")
        summary.add_row("Throughput", f"{total/elapsed:.1f} rows/sec")
        summary.add_row("Output File", str(out_path))

        console.print(summary)
    else:
        print(f"\nDone! {success} successful, {failed} failed in {elapsed:.1f}s")
        print(f"Output: {out_path}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Graph-based enrichment executor")
    parser.add_argument("--lead", required=True, help="Lead table name (directory under leads/)")
    parser.add_argument("--graph", help="Node name to execute (single node)")
    parser.add_argument("--workflow", help="Workflow name to execute (sequence of nodes)")
    parser.add_argument("--preview", action="store_true", help="Preview mode (first N rows, still saves to database)")
    parser.add_argument("--limit", type=int, default=10, help="Number of rows to process (default: 10)")
    parser.add_argument("--list", action="store_true", help="List available nodes and workflows")
    parser.add_argument("--show-graph", action="store_true", help="Show graph.yaml definition")
    parser.add_argument("--validate", action="store_true", help="Validate graph without running")
    parser.add_argument("--output", help="Output CSV path")
    parser.add_argument("--parallel", type=int, default=5, help="Number of parallel workers (default: 5)")
    parser.add_argument("--config", help="JSON config for node (e.g., '{\"keywords\": [\"datagen\"]}')")
    parser.add_argument("--use-csv", action="store_true", help="Use CSV-only mode (legacy, no database)")
    parser.add_argument(
        "--overwrite",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Overwrite existing values for this node/workflow (default: false)",
    )
    parser.add_argument(
        "--skip-existing",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip nodes already computed for the same inputs/config (default: true)",
    )
    parser.add_argument(
        "--cache",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use node cache to deduplicate work (default: true)",
    )

    args = parser.parse_args()

    # Parse config if provided
    config = None
    if args.config:
        try:
            config = json.loads(args.config)
        except json.JSONDecodeError as e:
            if RICH_AVAILABLE:
                console.print(f"[red]Invalid config JSON: {e}[/red]")
            else:
                print(f"Invalid config JSON: {e}")
            sys.exit(1)

    # Check lead exists
    lead_path = get_lead_path(args.lead)
    if not lead_path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]Error: Lead table not found: {lead_path}[/red]")
        else:
            print(f"Error: Lead table not found: {lead_path}")
        sys.exit(1)

    # Show graph definition
    if args.show_graph:
        show_graph_definition(args.lead)
        sys.exit(0)

    # List mode
    if args.list:
        nodes = list_graphs(args.lead)
        workflows = list_workflows(args.lead)

        if RICH_AVAILABLE:
            # Nodes table
            if nodes:
                table = Table(title=f"Nodes for {args.lead}")
                table.add_column("Name", style="cyan")
                table.add_column("Description")
                table.add_column("Input", style="green")
                table.add_column("Output", style="yellow")

                for name, info in nodes.items():
                    desc = info["description"][:40] + "..." if len(info["description"]) > 40 else info["description"]
                    table.add_row(
                        name,
                        desc,
                        ", ".join(info["input_cols"]),
                        ", ".join(info["output_cols"][:3]) + ("..." if len(info["output_cols"]) > 3 else "")
                    )

                console.print(table)
            else:
                console.print(f"[yellow]No nodes found for {args.lead}[/yellow]")

            # Workflows table
            if workflows:
                console.print()
                wf_table = Table(title=f"Workflows for {args.lead}")
                wf_table.add_column("Name", style="cyan")
                wf_table.add_column("Description")
                wf_table.add_column("Nodes", style="magenta")

                for name, info in workflows.items():
                    desc = info.get("description", "")[:40]
                    nodes_list = info.get("nodes", [])
                    # Extract node names
                    node_names = []
                    for n in nodes_list:
                        if isinstance(n, str):
                            node_names.append(n)
                        elif isinstance(n, dict):
                            node_names.append(n.get("node", "?"))
                    wf_table.add_row(name, desc, " -> ".join(node_names))

                console.print(wf_table)
            else:
                console.print(f"[yellow]No workflows defined in graph.yaml[/yellow]")

            console.print()
            console.print("[dim]Tip: Use --show-graph to see full graph.yaml definition[/dim]")
        else:
            if nodes:
                print(f"\nNodes for {args.lead}:")
                for name, info in nodes.items():
                    print(f"  {name}: {info['description'][:50]}")
                    print(f"    Input:  {', '.join(info['input_cols'])}")
                    print(f"    Output: {', '.join(info['output_cols'])}")

            if workflows:
                print(f"\nWorkflows for {args.lead}:")
                for name, info in workflows.items():
                    print(f"  {name}: {info.get('description', '')[:50]}")

        sys.exit(0)

    # Require graph or workflow for other operations
    if not args.graph and not args.workflow:
        if RICH_AVAILABLE:
            console.print("[red]Error: --graph or --workflow required (or use --list to see available options)[/red]")
        else:
            print("Error: --graph or --workflow required (or use --list to see available options)")
        sys.exit(1)

    # Validate mode
    if args.validate:
        try:
            if args.workflow:
                nodes = load_workflow(args.lead, args.workflow)
                if RICH_AVAILABLE:
                    console.print(f"[green]Workflow '{args.workflow}' is valid ({len(nodes)} nodes)[/green]")
                    for i, node in enumerate(nodes):
                        console.print(f"  {i+1}. {node.__class__.__name__}")
                        console.print(f"     Input:  {node.input_cols}")
                        console.print(f"     Output: {node.output_cols}")
                else:
                    print(f"Workflow '{args.workflow}' is valid ({len(nodes)} nodes)")
                    for i, node in enumerate(nodes):
                        print(f"  {i+1}. {node.__class__.__name__}")
            else:
                graph = load_graph(args.lead, args.graph, config)
                if RICH_AVAILABLE:
                    console.print(f"[green]Node '{args.graph}' is valid[/green]")
                    console.print(f"  Input:  {graph.input_cols}")
                    console.print(f"  Output: {graph.output_cols}")
                else:
                    print(f"Node '{args.graph}' is valid")
                    print(f"  Input:  {graph.input_cols}")
                    print(f"  Output: {graph.output_cols}")
            sys.exit(0)
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[red]Validation failed: {e}[/red]")
            else:
                print(f"Validation failed: {e}")
            sys.exit(1)

    # Preview mode
    if args.preview:
        if args.workflow:
            # Run workflow preview
            run_workflow_preview(args.lead, args.workflow, args.limit)
        else:
            run_preview(args.lead, args.graph, args.limit, config)
        sys.exit(0)

    # Batch mode
    if args.use_csv:
        # Legacy CSV-only mode
        if args.workflow:
            run_workflow_batch_csv(args.lead, args.workflow, args.output, args.parallel, args.overwrite)
        else:
            run_batch_csv(args.lead, args.graph, args.output, args.parallel, config)
    else:
        # Default: SQLite mode
        if args.workflow:
            run_workflow_batch(args.lead, args.workflow, args.output, args.parallel, args.overwrite, args.skip_existing, args.cache)
        else:
            run_batch(args.lead, args.graph, args.output, args.parallel, config, args.overwrite, args.skip_existing, args.cache)


def run_workflow_preview(lead_name: str, workflow_name: str, limit: int = 10):
    """Run a workflow on first N rows with detailed output and save to database."""
    lead_path = get_lead_path(lead_name)
    csv_path = lead_path / "table.csv"

    if not csv_path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]Error: CSV not found at {csv_path}[/red]")
        else:
            print(f"Error: CSV not found at {csv_path}")
        return False

    # Initialize database (same as batch mode)
    db, db_err = init_lead_db(lead_name, csv_path)
    if db_err:
        if RICH_AVAILABLE:
            console.print(f"[red]Database error: {db_err}[/red]")
        else:
            print(f"Database error: {db_err}")
        return False

    # Load workflow (list of nodes)
    nodes = load_workflow(lead_name, workflow_name)

    # Get rows from database (pending only, limited)
    rows, err = db.get_rows(status='pending', limit=limit)
    if err:
        if RICH_AVAILABLE:
            console.print(f"[red]Error loading rows: {err}[/red]")
        else:
            print(f"Error loading rows: {err}")
        return False

    total_in_db, _ = db.get_rows()
    total_count = len(total_in_db) if total_in_db else 0

    # Collect all input/output columns
    all_input_cols = set()
    all_output_cols = []
    for node in nodes:
        all_input_cols.update(node.input_cols)
        all_output_cols.extend(node.output_cols)

    print_header(f"WORKFLOW PREVIEW: {workflow_name}")
    print_info("Lead Table", f"{lead_path}/table.db ({total_count} rows total, processing {len(rows)})")
    print_info("Workflow", f"{len(nodes)} nodes")

    if RICH_AVAILABLE:
        console.print("\nNodes in workflow:")
        for i, node in enumerate(nodes):
            console.print(f"  {i+1}. [cyan]{node.__class__.__name__}[/cyan]: {node.input_cols} -> {node.output_cols}")
        console.print("=" * 60)
    else:
        print("\nNodes in workflow:")
        for i, node in enumerate(nodes):
            print(f"  {i+1}. {node.__class__.__name__}: {node.input_cols} -> {node.output_cols}")
        print("=" * 60)

    success = 0
    failed = 0

    for i, row in enumerate(rows):
        row_id = row.get("_id")
        display_limit = min(limit, len(rows))

        if RICH_AVAILABLE:
            console.print(f"\n[bold]Row {i+1}/{display_limit}:[/bold]")
        else:
            print(f"\nRow {i+1}/{display_limit}:")

        row_data = row.copy()
        row_success = True
        row_error = None

        for node_idx, node in enumerate(nodes):
            node_input_map = getattr(node, "_input_map", {}) or {}
            node_output_prefix = getattr(node, "_output_prefix", None)

            if RICH_AVAILABLE:
                console.print(f"  [{node_idx+1}] [cyan]{node.__class__.__name__}[/cyan]")
            else:
                print(f"  [{node_idx+1}] {node.__class__.__name__}")

            input_row = _build_node_input_row(row_data, node_input_map)
            raw_result, err = node(input_row)
            result = _apply_output_prefix(raw_result, node_output_prefix)

            if err:
                if RICH_AVAILABLE:
                    console.print(f"      [red]Error: {err}[/red]")
                else:
                    print(f"      Error: {err}")
                if not result:
                    row_success = False
                    row_error = err

            # Merge result into row_data for next node
            row_data.update(result)

            # Show outputs
            expected_cols = node.output_cols
            if node_output_prefix:
                expected_cols = [
                    c if c.startswith(f"{node_output_prefix}_") else f"{node_output_prefix}_{c}"
                    for c in node.output_cols
                ]

            for col in expected_cols:
                val = result.get(col, "")
                val_str = str(val)[:50] + "..." if len(str(val)) > 50 else str(val)
                if RICH_AVAILABLE:
                    console.print(f"      -> {col}: [yellow]{val_str}[/yellow]")
                else:
                    print(f"      -> {col}: {val_str}")

        # Save to database - collect all enriched columns (not starting with _)
        # Include columns that were updated with new values, not just new columns
        updates = {k: v for k, v in row_data.items() if not k.startswith("_") and k in all_output_cols}
        if updates and row_id:
            status = "completed" if row_success else "failed"
            db.update_row(row_id, updates, status=status, error=row_error)

        if row_success:
            success += 1
            status_display = "[green]SUCCESS[/green]" if RICH_AVAILABLE else "SUCCESS"
        else:
            failed += 1
            status_display = "[red]FAILED[/red]" if RICH_AVAILABLE else "FAILED"

        if RICH_AVAILABLE:
            console.print(f"  Status: {status_display} (saved to database)")
        else:
            print(f"  Status: {status_display} (saved to database)")

    # Summary
    if RICH_AVAILABLE:
        console.print("\n" + "=" * 60)
        console.print(f"Preview Complete: [green]{success}[/green] successful, [red]{failed}[/red] failed")
        console.print(f"Data saved to: [cyan]{lead_path}/table.db[/cyan]")
        console.print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print(f"Preview Complete: {success} successful, {failed} failed")
        print(f"Data saved to: {lead_path}/table.db")
        print("=" * 60)

    return True


def run_workflow_batch_csv(
    lead_name: str,
    workflow_name: str,
    output_path: str = None,
    parallel: int = 5,
    overwrite: bool = False,
):
    """Run a workflow on all rows and save enriched CSV (CSV-only mode, legacy)."""
    lead_path = get_lead_path(lead_name)
    csv_path = lead_path / "table.csv"

    if not csv_path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]Error: CSV not found at {csv_path}[/red]")
        else:
            print(f"Error: CSV not found at {csv_path}")
        return False

    # Load workflow
    nodes = load_workflow(lead_name, workflow_name)

    # Load data
    rows = load_csv(csv_path)
    total = len(rows)

    # Collect all output columns
    all_output_cols = []
    for node in nodes:
        node_output_prefix = getattr(node, "_output_prefix", None)
        if node_output_prefix:
            all_output_cols.extend(
                [
                    c if c.startswith(f"{node_output_prefix}_") else f"{node_output_prefix}_{c}"
                    for c in node.output_cols
                ]
            )
        else:
            all_output_cols.extend(node.output_cols)

    print_header(f"WORKFLOW BATCH: {workflow_name}")
    print_info("Lead Table", f"{csv_path} ({total} rows)")
    print_info("Nodes", f"{len(nodes)}")
    print_info("Parallel Workers", str(parallel))

    # Determine output columns
    existing_cols = list(rows[0].keys()) if rows else []
    new_cols = [c for c in all_output_cols if c not in existing_cols]
    all_cols = existing_cols + new_cols

    # Process function for a single row through all nodes
    def process_row_workflow(idx_row):
        idx, row = idx_row
        row_data = row.copy()
        has_error = False

        for node in nodes:
            node_input_map = getattr(node, "_input_map", {}) or {}
            node_output_prefix = getattr(node, "_output_prefix", None)
            input_row = _build_node_input_row(row_data, node_input_map)

            raw_result, err = node(input_row)
            result = _apply_output_prefix(raw_result, node_output_prefix)
            if err and not result:
                has_error = True
            row_data.update(result)

        # Copy output columns back to original row
        for col in all_output_cols:
            if col not in row_data:
                continue
            if _should_overwrite(row.get(col), overwrite):
                row[col] = row_data.get(col, "")

        return idx, row, has_error

    enriched_rows = []
    success = 0
    failed = 0
    start_time = datetime.now()

    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("*"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Running workflow ({parallel} workers)...", total=total)

            with ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = {executor.submit(process_row_workflow, (i, row)): i for i, row in enumerate(rows)}

                for future in as_completed(futures):
                    idx, enriched_row, has_error = future.result()
                    enriched_rows.append((idx, enriched_row))

                    if has_error:
                        failed += 1
                    else:
                        success += 1

                    progress.update(
                        task,
                        advance=1,
                        description=f"[cyan]Running workflow ([green]{success}[/green] OK / [red]{failed}[/red] err)"
                    )
    else:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(process_row_workflow, (i, row)): i for i, row in enumerate(rows)}

            for i, future in enumerate(as_completed(futures)):
                idx, enriched_row, has_error = future.result()
                enriched_rows.append((idx, enriched_row))

                if has_error:
                    failed += 1
                else:
                    success += 1

                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{total}...")

    # Sort by original order
    enriched_rows.sort(key=lambda x: x[0])
    final_rows = [row for _, row in enriched_rows]

    elapsed = (datetime.now() - start_time).total_seconds()

    # Save output
    if output_path:
        out_path = Path(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = lead_path / f"table_enriched_{workflow_name}_{timestamp}.csv"

    save_csv(out_path, final_rows, all_cols)

    # Summary
    if RICH_AVAILABLE:
        console.print()
        console.rule("[bold green]COMPLETE[/bold green]", style="green")
        console.print()

        summary = Table(box=box.ROUNDED, show_header=False)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value")

        summary.add_row("Rows Processed", f"[green]{success}[/green] / {total}")
        summary.add_row("Errors", f"[red]{failed}[/red]")
        summary.add_row("New Columns", ", ".join(new_cols[:5]) + ("..." if len(new_cols) > 5 else ""))
        summary.add_row("Time Elapsed", f"{elapsed:.1f}s")
        summary.add_row("Throughput", f"{total/elapsed:.1f} rows/sec")
        summary.add_row("Output File", str(out_path))

        console.print(summary)
    else:
        print(f"\nDone! {success} successful, {failed} failed in {elapsed:.1f}s")
        print(f"Output: {out_path}")

    return True


def run_batch(
    lead_name: str,
    graph_name: str,
    output_path: str = None,
    parallel: int = 5,
    config: dict = None,
    overwrite: bool = False,
    skip_existing: bool = True,
    use_cache: bool = True,
):
    """
    Run graph enrichment on all rows using SQLite backend (default mode).

    Args:
        lead_name: Name of the lead table directory
        graph_name: Name of the graph to execute
        output_path: Optional custom output CSV path
        parallel: Number of parallel workers
        config: Optional config dict for graph
    """
    lead_path = get_lead_path(lead_name)
    csv_path = lead_path / "table.csv"

    # Initialize database (auto-imports CSV if needed)
    db, err = init_lead_db(lead_name, csv_path)
    if err:
        if RICH_AVAILABLE:
            console.print(f"[red]Error initializing database: {err}[/red]")
        else:
            print(f"Error initializing database: {err}")
        return False

    # Load graph
    try:
        graph = load_graph(lead_name, graph_name, config)
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[red]Error loading graph: {e}[/red]")
        else:
            print(f"Error loading graph: {e}")
        return False

    # Get rows from database
    rows, err = db.get_rows()
    if err:
        if RICH_AVAILABLE:
            console.print(f"[red]Error loading rows: {err}[/red]")
        else:
            print(f"Error loading rows: {err}")
        return False

    total = len(rows)

    print_header(f"BATCH ENRICHMENT: {graph_name}")
    print_info("Lead Table", f"{lead_path / 'table.db'} ({total} rows)")
    print_info("Graph", graph_name)
    print_info("Parallel Workers", str(parallel))

    # Start execution tracking
    execution_id, err = db.start_execution("graph", graph_name, total, config)
    if err:
        if RICH_AVAILABLE:
            console.print(f"[red]Error starting execution: {err}[/red]")
        else:
            print(f"Error starting execution: {err}")
        return False

    node_name = graph_name
    config_hash = _sha256(_stable_json({"_node": node_name, "_config": config or {}, "_class": f"{graph.__class__.__module__}.{graph.__class__.__name__}"}))

    # Process function with DB updates
    def process_row(row):
        row_id = row["_id"]

        input_hash = _hash_inputs(graph.input_cols, row)

        # Skip if already computed for the same inputs/config (unless overwriting)
        if skip_existing and not overwrite:
            already_done, done_err = db.has_completed_row_execution(row_id, node_name, input_hash, config_hash)
            if done_err:
                return row_id, {}, done_err
            if already_done:
                return row_id, {}, ""

        cache_hit = False
        cache_k = _cache_key(node_name, input_hash, config_hash)
        cached_result = None
        cached_error = ""

        if use_cache:
            cached_result, cached_error, cache_err = db.get_cache_entry(cache_k)
            if cache_err:
                cached_result = None
            elif cached_result is not None and not cached_error:
                cache_hit = True

        row_exec_id, exec_err = db.start_row_execution(execution_id, row_id, node_name, input_hash, config_hash, cache_hit)
        if exec_err:
            return row_id, {}, exec_err

        if cache_hit:
            result = cached_result or {}
            err = ""
        else:
            result, err = graph(row)
            if use_cache:
                db.set_cache_entry(cache_k, node_name, input_hash, config_hash, result if not err else {}, err)

        updates = {}
        if not err:
            for k, v in result.items():
                if _should_overwrite(row.get(k), overwrite):
                    updates[k] = v

        # Update DB immediately (transactional)
        status = "completed" if not err else "failed"
        db_err = db.update_row(row_id, updates, status=status, error=err)

        complete_err = db.complete_row_execution(row_exec_id, status, err or db_err)
        return row_id, updates, err or db_err or complete_err

    success = 0
    failed = 0
    start_time = datetime.now()

    # Process with ThreadPoolExecutor
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("*"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Enriching ({parallel} workers)...", total=total)

            with ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = {executor.submit(process_row, row): row["_id"] for row in rows}

                for future in as_completed(futures):
                    row_id, result, err = future.result()
                    if err:
                        failed += 1
                    else:
                        success += 1

                    progress.update(
                        task,
                        advance=1,
                        description=f"[cyan]Enriching ([green]{success}[/green] OK / [red]{failed}[/red] err)"
                    )
    else:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(process_row, row): row["_id"] for row in rows}

            for i, future in enumerate(as_completed(futures)):
                row_id, result, err = future.result()
                if err:
                    failed += 1
                else:
                    success += 1

                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{total}...")

    elapsed = (datetime.now() - start_time).total_seconds()

    # Complete execution tracking
    db_err = db.complete_execution(execution_id, success, failed, str(output_path) if output_path else None)
    if db_err:
        if RICH_AVAILABLE:
            console.print(f"[yellow]Warning: Failed to complete execution tracking: {db_err}[/yellow]")
        else:
            print(f"Warning: Failed to complete execution tracking: {db_err}")

    # Export to CSV
    if output_path:
        out_path = Path(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = lead_path / f"table_enriched_{graph_name}_{timestamp}.csv"

    export_rows, err = db.export_to_csv(out_path)
    if err:
        if RICH_AVAILABLE:
            console.print(f"[red]Export error: {err}[/red]")
        else:
            print(f"Export error: {err}")
        return False

    # Get column names (excluding internal _ columns)
    fieldnames = [k for k in export_rows[0].keys() if not k.startswith('_')] if export_rows else []
    save_csv(out_path, export_rows, fieldnames)

    # Summary
    if RICH_AVAILABLE:
        console.print()
        console.rule("[bold green]COMPLETE[/bold green]", style="green")
        console.print()

        summary = Table(box=box.ROUNDED, show_header=False)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value")

        summary.add_row("Rows Processed", f"[green]{success}[/green] / {total}")
        summary.add_row("Errors", f"[red]{failed}[/red]")
        summary.add_row("New Columns", ", ".join(graph.output_cols))
        summary.add_row("Time Elapsed", f"{elapsed:.1f}s")
        summary.add_row("Throughput", f"{total/elapsed:.1f} rows/sec")
        summary.add_row("Output File", str(out_path))

        console.print(summary)
    else:
        print(f"\nDone! {success} successful, {failed} failed in {elapsed:.1f}s")
        print(f"Output: {out_path}")

    return True


def run_workflow_batch(
    lead_name: str,
    workflow_name: str,
    output_path: str = None,
    parallel: int = 5,
    overwrite: bool = False,
    skip_existing: bool = True,
    use_cache: bool = True,
):
    """
    Run a workflow on all rows using SQLite backend (default mode).

    Args:
        lead_name: Name of the lead table directory
        workflow_name: Name of the workflow to execute
        output_path: Optional custom output CSV path
        parallel: Number of parallel workers
    """
    lead_path = get_lead_path(lead_name)
    csv_path = lead_path / "table.csv"

    # Initialize database
    db, err = init_lead_db(lead_name, csv_path)
    if err:
        if RICH_AVAILABLE:
            console.print(f"[red]Error initializing database: {err}[/red]")
        else:
            print(f"Error initializing database: {err}")
        return False

    # Load workflow
    try:
        nodes = load_workflow(lead_name, workflow_name)
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[red]Error loading workflow: {e}[/red]")
        else:
            print(f"Error loading workflow: {e}")
        return False

    # Get workflow conditions (if any)
    try:
        from importlib import import_module
        graph_module = import_module(f"{lead_name}.graph")
        get_conditions_fn = getattr(graph_module, "get_workflow_conditions", None)
        conditions = get_conditions_fn(workflow_name) if get_conditions_fn else None
    except Exception:
        conditions = None

    # Get rows from database
    rows, err = db.get_rows()
    if err:
        if RICH_AVAILABLE:
            console.print(f"[red]Error loading rows: {err}[/red]")
        else:
            print(f"Error loading rows: {err}")
        return False

    # Apply workflow conditions (WHERE clause filtering)
    if conditions and "where" in conditions:
        where_clause = conditions["where"]
        filtered_rows, filter_err = db.filter_rows(where_clause)
        if filter_err:
            if RICH_AVAILABLE:
                console.print(f"[yellow]Warning: Failed to apply WHERE filter '{where_clause}': {filter_err}[/yellow]")
                console.print("[yellow]Proceeding with all rows[/yellow]")
            else:
                print(f"Warning: Failed to apply WHERE filter '{where_clause}': {filter_err}")
                print("Proceeding with all rows")
        else:
            rows = filtered_rows
            if RICH_AVAILABLE:
                console.print(f"[cyan]Applied WHERE filter: {where_clause} ({len(rows)} rows matched)[/cyan]")
            else:
                print(f"Applied WHERE filter: {where_clause} ({len(rows)} rows matched)")

    total = len(rows)

    # Collect all output columns
    all_output_cols = []
    for node in nodes:
        all_output_cols.extend(node.output_cols)

    print_header(f"WORKFLOW BATCH: {workflow_name}")
    print_info("Lead Table", f"{lead_path / 'table.db'} ({total} rows)")
    print_info("Nodes", f"{len(nodes)}")
    print_info("Parallel Workers", str(parallel))

    # Start execution tracking
    execution_id, err = db.start_execution("workflow", workflow_name, total, {})
    if err:
        if RICH_AVAILABLE:
            console.print(f"[red]Error starting execution: {err}[/red]")
        else:
            print(f"Error starting execution: {err}")
        return False

    # Process function for a single row through all nodes
    def process_row_workflow(row):
        row_id = row["_id"]
        row_data = row.copy()
        has_error = False
        errors = []

        for node in nodes:
            node_name = _node_name(node, node.__class__.__name__)
            input_map = getattr(node, "_input_map", {}) or {}
            output_prefix = getattr(node, "_output_prefix", None)

            input_row = _build_node_input_row(row_data, input_map)
            input_hash = _hash_inputs(node.input_cols, input_row)
            config_hash = _hash_config(node)

            # Skip if already computed for the same inputs/config (unless overwriting)
            if skip_existing and not overwrite:
                already_done, done_err = db.has_completed_row_execution(row_id, node_name, input_hash, config_hash)
                if done_err:
                    has_error = True
                    errors.append(done_err)
                    continue
                if already_done:
                    continue

            cache_hit = False
            cache_k = _cache_key(node_name, input_hash, config_hash)
            cached_result = None
            cached_error = ""

            if use_cache:
                cached_result, cached_error, cache_err = db.get_cache_entry(cache_k)
                if cache_err:
                    cached_result = None
                elif cached_result is not None and not cached_error:
                    cache_hit = True

            row_exec_id, exec_err = db.start_row_execution(execution_id, row_id, node_name, input_hash, config_hash, cache_hit)
            if exec_err:
                has_error = True
                errors.append(exec_err)
                continue

            if cache_hit:
                raw_result = cached_result or {}
                err = ""
            else:
                raw_result, err = node(input_row)
                if use_cache:
                    # Cache raw node outputs; output_prefix is part of config hash
                    db.set_cache_entry(cache_k, node_name, input_hash, config_hash, raw_result if not err else {}, err)

            result = _apply_output_prefix(raw_result, output_prefix)

            if err and not result:
                has_error = True
                errors.append(err)

            # Apply result to row_data + DB with overwrite semantics
            updates = {}
            for k, v in result.items():
                if k.startswith("_"):
                    continue
                if _should_overwrite(row_data.get(k), overwrite):
                    updates[k] = v

            db_err = db.update_row(row_id, updates, status=None, error=None)
            if db_err:
                has_error = True
                errors.append(db_err)

            # Ensure downstream nodes see the same data the table will have
            row_data.update(updates)

            status = "completed" if not err and not db_err else "failed"
            complete_err = db.complete_row_execution(row_exec_id, status, err or db_err)
            if complete_err:
                has_error = True
                errors.append(complete_err)

        # Update row status/error once at end
        final_status = "completed" if not has_error else "failed"
        final_error = "; ".join([e for e in errors if e]) if errors else ""
        db_err = db.update_row(row_id, {}, status=final_status, error=final_error)

        return row_id, has_error or bool(db_err)

    success = 0
    failed = 0
    start_time = datetime.now()

    # Process with ThreadPoolExecutor
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("*"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Running workflow ({parallel} workers)...", total=total)

            with ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = {executor.submit(process_row_workflow, row): row["_id"] for row in rows}

                for future in as_completed(futures):
                    row_id, has_error = future.result()
                    if has_error:
                        failed += 1
                    else:
                        success += 1

                    progress.update(
                        task,
                        advance=1,
                        description=f"[cyan]Running workflow ([green]{success}[/green] OK / [red]{failed}[/red] err)"
                    )
    else:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(process_row_workflow, row): row["_id"] for row in rows}

            for i, future in enumerate(as_completed(futures)):
                row_id, has_error = future.result()
                if has_error:
                    failed += 1
                else:
                    success += 1

                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{total}...")

    elapsed = (datetime.now() - start_time).total_seconds()

    # Complete execution tracking
    db_err = db.complete_execution(execution_id, success, failed, str(output_path) if output_path else None)
    if db_err:
        if RICH_AVAILABLE:
            console.print(f"[yellow]Warning: Failed to complete execution tracking: {db_err}[/yellow]")
        else:
            print(f"Warning: Failed to complete execution tracking: {db_err}")

    # Export to CSV
    if output_path:
        out_path = Path(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = lead_path / f"table_enriched_{workflow_name}_{timestamp}.csv"

    export_rows, err = db.export_to_csv(out_path)
    if err:
        if RICH_AVAILABLE:
            console.print(f"[red]Export error: {err}[/red]")
        else:
            print(f"Export error: {err}")
        return False

    # Get column names (excluding internal _ columns)
    fieldnames = [k for k in export_rows[0].keys() if not k.startswith('_')] if export_rows else []
    save_csv(out_path, export_rows, fieldnames)

    # Summary
    if RICH_AVAILABLE:
        console.print()
        console.rule("[bold green]COMPLETE[/bold green]", style="green")
        console.print()

        summary = Table(box=box.ROUNDED, show_header=False)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value")

        summary.add_row("Rows Processed", f"[green]{success}[/green] / {total}")
        summary.add_row("Errors", f"[red]{failed}[/red]")
        summary.add_row("New Columns", ", ".join(all_output_cols[:5]) + ("..." if len(all_output_cols) > 5 else ""))
        summary.add_row("Time Elapsed", f"{elapsed:.1f}s")
        summary.add_row("Throughput", f"{total/elapsed:.1f} rows/sec")
        summary.add_row("Output File", str(out_path))

        console.print(summary)
    else:
        print(f"\nDone! {success} successful, {failed} failed in {elapsed:.1f}s")
        print(f"Output: {out_path}")

    return True


if __name__ == "__main__":
    main()
