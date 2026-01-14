#!/usr/bin/env python3
"""
Generate Mermaid flowchart from graph.yaml column lineage.

Usage:
    python scripts/graph_to_mermaid.py --lead gtm-engineers-series-a
    python scripts/graph_to_mermaid.py --lead gtm-engineers-series-a --direction TB
    python scripts/graph_to_mermaid.py --lead gtm-engineers-series-a --output graph.mmd
"""

import argparse
from pathlib import Path

import yaml


def load_graph(lead_name: str) -> dict:
    """Load graph.yaml for a lead."""
    graph_path = Path("leads") / lead_name / "graph" / "graph.yaml"
    if not graph_path.exists():
        raise FileNotFoundError(f"Graph not found: {graph_path}")

    with open(graph_path) as f:
        return yaml.safe_load(f)


def to_mermaid(graph: dict, direction: str = "LR") -> str:
    """
    Generate Mermaid flowchart from column lineage.

    Args:
        graph: Parsed graph.yaml dictionary
        direction: Graph direction - LR (left-right), TB (top-bottom)

    Returns:
        Mermaid diagram string
    """
    columns = graph.get("columns", {})
    nodes_def = graph.get("nodes", {})

    lines = [f"flowchart {direction}"]

    # Group columns by source
    csv_cols = []
    node_outputs = {}  # node_name -> [output_cols]

    for col_name, col_spec in columns.items():
        source = col_spec.get("from")
        if source == "csv":
            csv_cols.append(col_name)
        elif source in nodes_def:
            if source not in node_outputs:
                node_outputs[source] = []
            node_outputs[source].append(col_name)

    # Helper to make safe Mermaid IDs
    def safe_id(name: str) -> str:
        return name.replace(" ", "_").replace("-", "_")

    # Create subgraph for CSV inputs
    lines.append("")
    lines.append("    subgraph input[CSV Input]")
    for col in csv_cols:
        sid = safe_id(col)
        lines.append(f'        {sid}["{col}"]')
    lines.append("    end")

    # Create subgraph for each node
    for node_name, output_cols in node_outputs.items():
        node_desc = nodes_def.get(node_name, {}).get("description", node_name)
        lines.append("")
        lines.append(f'    subgraph {node_name}["{node_desc}"]')
        for col in output_cols:
            sid = f"{node_name}_{safe_id(col)}"
            lines.append(f'        {sid}["{col}"]')
        lines.append("    end")

    # Create edges based on 'via' dependencies
    lines.append("")
    for col_name, col_spec in columns.items():
        source = col_spec.get("from")
        via = col_spec.get("via", [])

        if source == "csv" or not via:
            continue

        # Edge: via_col -> output_col
        for via_col in via:
            out_sid = f"{source}_{safe_id(col_name)}"

            # Check if via_col is from CSV or another node
            via_source = columns.get(via_col, {}).get("from")
            if via_source == "csv":
                via_sid = safe_id(via_col)
                lines.append(f"    {via_sid} --> {out_sid}")
            else:
                # via_col is from another node
                via_sid = f"{via_source}_{safe_id(via_col)}"
                lines.append(f"    {via_sid} --> {out_sid}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate Mermaid from graph.yaml")
    parser.add_argument("--lead", required=True, help="Lead name (directory under leads/)")
    parser.add_argument("--direction", default="LR", choices=["LR", "TB", "RL", "BT"],
                        help="Graph direction (default: LR)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")

    args = parser.parse_args()

    graph = load_graph(args.lead)
    mermaid = to_mermaid(graph, args.direction)

    if args.output:
        with open(args.output, "w") as f:
            f.write(mermaid)
        print(f"Written to: {args.output}")
    else:
        print(mermaid)


if __name__ == "__main__":
    main()
