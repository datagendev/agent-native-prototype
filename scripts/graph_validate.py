#!/usr/bin/env python3
"""
Graph Validator - Validates the three-file graph structure.

Checks:
  1. YAML syntax
  2. Schema structure
  3. References (instances -> types, workflows -> instances/types)
  4. Connections (valid nodes and fields)
  5. Outputs match node outputs
  6. Required parameters provided

Usage:
  python scripts/graph_validate.py --lead example-leads
  python scripts/graph_validate.py --lead example-leads --verbose
  python scripts/graph_validate.py --lead example-leads --workflow ceo_profile
  python scripts/graph_validate.py --list  # List available leads
"""

import argparse
import sys
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ValidationError:
    file: str
    path: str
    message: str
    severity: str = "error"  # error, warning


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    def add_error(self, file: str, path: str, message: str):
        self.errors.append(ValidationError(file, path, message, "error"))

    def add_warning(self, file: str, path: str, message: str):
        self.warnings.append(ValidationError(file, path, message, "warning"))

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def load_yaml(path: Path) -> tuple[dict, str]:
    """Load YAML file. Returns (data, error)."""
    if not path.exists():
        return {}, f"File not found: {path}"

    try:
        import yaml
    except ImportError:
        return {}, "PyYAML not installed. Run: pip install pyyaml"

    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        return data, ""
    except yaml.YAMLError as e:
        return {}, f"YAML syntax error: {e}"


def validate_node_types(data: dict, result: ValidationResult):
    """Validate node_types.yaml structure."""
    node_types = data.get("node_types", {})

    if not node_types:
        result.add_error("node_types.yaml", "node_types", "No node types defined")
        return

    for name, type_def in node_types.items():
        path = f"node_types.{name}"

        # Required fields
        if not type_def.get("description"):
            result.add_warning("node_types.yaml", path, "Missing description")

        if not type_def.get("file"):
            result.add_error("node_types.yaml", path, "Missing 'file' field")

        if not type_def.get("class"):
            result.add_error("node_types.yaml", path, "Missing 'class' field")

        # Check inputs/outputs structure
        inputs = type_def.get("inputs", {})
        outputs = type_def.get("outputs", {})
        parameters = type_def.get("parameters", {})

        for input_name, input_def in inputs.items():
            if not isinstance(input_def, dict):
                result.add_error("node_types.yaml", f"{path}.inputs.{input_name}",
                               "Input must be a dict with 'type' field")
            elif "type" not in input_def:
                result.add_warning("node_types.yaml", f"{path}.inputs.{input_name}",
                                 "Missing 'type' field")

        for output_name, output_def in outputs.items():
            if not isinstance(output_def, dict):
                result.add_error("node_types.yaml", f"{path}.outputs.{output_name}",
                               "Output must be a dict with 'type' field")

        # Check required parameters have no default (or mark as required)
        for param_name, param_def in parameters.items():
            if isinstance(param_def, dict):
                if param_def.get("required") and "default" in param_def:
                    result.add_warning("node_types.yaml", f"{path}.parameters.{param_name}",
                                     "Required parameter has default value")


def validate_instances(data: dict, node_types: dict, result: ValidationResult):
    """Validate instances.yaml structure."""
    instances = data.get("instances", {})

    if not instances:
        result.add_warning("instances.yaml", "instances", "No instances defined")
        return

    type_names = set(node_types.get("node_types", {}).keys())

    for name, inst_def in instances.items():
        path = f"instances.{name}"

        # Check type reference
        type_name = inst_def.get("type")
        if not type_name:
            result.add_error("instances.yaml", path, "Missing 'type' field")
        elif type_name not in type_names:
            result.add_error("instances.yaml", path,
                           f"Unknown node type: '{type_name}'. Available: {', '.join(sorted(type_names))}")

        # Check required parameters are provided
        if type_name and type_name in type_names:
            type_def = node_types["node_types"][type_name]
            params = type_def.get("parameters", {})
            provided = inst_def.get("parameters", {})

            for param_name, param_def in params.items():
                if isinstance(param_def, dict) and param_def.get("required"):
                    if "default" not in param_def and param_name not in provided:
                        result.add_error("instances.yaml", path,
                                       f"Missing required parameter: '{param_name}'")


def validate_workflows(data: dict, node_types: dict, instances: dict, result: ValidationResult,
                      workflow_filter: str = None):
    """Validate workflows.yaml structure."""
    workflows = data.get("workflows", {})

    if not workflows:
        result.add_error("workflows.yaml", "workflows", "No workflows defined")
        return

    type_names = set(node_types.get("node_types", {}).keys())
    instance_names = set(instances.get("instances", {}).keys())

    for wf_name, wf_def in workflows.items():
        if workflow_filter and wf_name != workflow_filter:
            continue

        path = f"workflows.{wf_name}"

        # Check nodes
        nodes = wf_def.get("nodes", [])
        if not nodes:
            result.add_error("workflows.yaml", path, "No nodes defined")
            continue

        node_ids = set()
        node_outputs = {}  # node_id -> list of output fields

        for i, node_spec in enumerate(nodes):
            node_path = f"{path}.nodes[{i}]"

            if isinstance(node_spec, str):
                # String reference
                node_id = node_spec
                if node_spec in instance_names:
                    inst = instances["instances"][node_spec]
                    type_name = inst.get("type")
                elif node_spec in type_names:
                    type_name = node_spec
                else:
                    result.add_error("workflows.yaml", node_path,
                                   f"Unknown reference: '{node_spec}'")
                    continue
            elif isinstance(node_spec, dict):
                node_id = node_spec.get("id")

                if "instance" in node_spec:
                    # Instance override
                    inst_name = node_spec["instance"]
                    if inst_name not in instance_names:
                        result.add_error("workflows.yaml", node_path,
                                       f"Unknown instance: '{inst_name}'")
                        continue
                    inst = instances["instances"][inst_name]
                    type_name = inst.get("type")
                    node_id = node_id or inst_name
                elif "type" in node_spec:
                    # Inline type
                    type_name = node_spec["type"]
                    if type_name not in type_names:
                        result.add_error("workflows.yaml", node_path,
                                       f"Unknown type: '{type_name}'")
                        continue
                    node_id = node_id or type_name
                else:
                    result.add_error("workflows.yaml", node_path,
                                   "Node must have 'instance' or 'type'")
                    continue
            else:
                result.add_error("workflows.yaml", node_path,
                               "Invalid node specification")
                continue

            # Check for duplicate node IDs
            if node_id in node_ids:
                result.add_error("workflows.yaml", node_path,
                               f"Duplicate node ID: '{node_id}'")
            node_ids.add(node_id)

            # Track outputs for this node
            if type_name and type_name in type_names:
                type_def = node_types["node_types"][type_name]
                outputs = list(type_def.get("outputs", {}).keys())

                # Resolve output_prefix through inheritance chain:
                # type defaults -> instance params -> workflow overrides
                prefix = ""

                # 1. Type defaults
                type_params = type_def.get("parameters", {})
                if isinstance(type_params.get("output_prefix"), dict):
                    prefix = type_params["output_prefix"].get("default", "")
                elif isinstance(type_params.get("output_prefix"), str):
                    prefix = type_params["output_prefix"]

                # 2. Instance params (if using instance)
                inst_name = None
                if isinstance(node_spec, str) and node_spec in instance_names:
                    inst_name = node_spec
                elif isinstance(node_spec, dict) and "instance" in node_spec:
                    inst_name = node_spec["instance"]

                if inst_name and inst_name in instance_names:
                    inst_prefix = instances["instances"][inst_name].get("parameters", {}).get("output_prefix")
                    if inst_prefix:
                        prefix = inst_prefix

                # 3. Workflow overrides
                if isinstance(node_spec, dict):
                    override_prefix = node_spec.get("parameters", {}).get("output_prefix")
                    if override_prefix:
                        prefix = override_prefix

                if prefix:
                    outputs = [f"{prefix}_{o}" for o in outputs]

                node_outputs[node_id] = outputs

        # Check connections
        connections = wf_def.get("connections", [])
        if not connections:
            result.add_warning("workflows.yaml", path, "No connections defined")

        connected_inputs = {}  # node_id -> set of connected input fields

        for i, conn in enumerate(connections):
            conn_path = f"{path}.connections[{i}]"

            if not isinstance(conn, dict):
                result.add_error("workflows.yaml", conn_path, "Connection must be a dict")
                continue

            from_str = conn.get("from", "")
            to_str = conn.get("to", "")

            if not from_str:
                result.add_error("workflows.yaml", conn_path, "Missing 'from' field")
            if not to_str:
                result.add_error("workflows.yaml", conn_path, "Missing 'to' field")

            # Parse from
            from_parts = from_str.split(".")
            if len(from_parts) != 2:
                result.add_error("workflows.yaml", conn_path,
                               f"Invalid 'from' format: '{from_str}'. Expected 'node.field'")
            else:
                from_node, from_field = from_parts
                if from_node != "$input" and from_node not in node_ids:
                    result.add_error("workflows.yaml", conn_path,
                                   f"Unknown source node: '{from_node}'")

            # Parse to
            to_parts = to_str.split(".")
            if len(to_parts) != 2:
                result.add_error("workflows.yaml", conn_path,
                               f"Invalid 'to' format: '{to_str}'. Expected 'node.field'")
            else:
                to_node, to_field = to_parts
                if to_node not in node_ids:
                    result.add_error("workflows.yaml", conn_path,
                                   f"Unknown target node: '{to_node}'")

                # Track connected inputs
                if to_node not in connected_inputs:
                    connected_inputs[to_node] = set()
                connected_inputs[to_node].add(to_field)

        # Check outputs declared match node outputs
        declared_outputs = wf_def.get("outputs", [])
        if not declared_outputs:
            result.add_warning("workflows.yaml", path, "No outputs declared")
        else:
            # Collect all possible outputs from nodes
            all_possible_outputs = set()
            for node_id, outputs in node_outputs.items():
                all_possible_outputs.update(outputs)

            for output in declared_outputs:
                if output not in all_possible_outputs:
                    result.add_warning("workflows.yaml", f"{path}.outputs",
                                     f"Output '{output}' not produced by any node")


def validate_graph(graph_dir: Path, workflow_filter: str = None, verbose: bool = False) -> ValidationResult:
    """Validate the complete graph structure."""
    result = ValidationResult()

    # Load files
    node_types, err = load_yaml(graph_dir / "node_types.yaml")
    if err:
        result.add_error("node_types.yaml", "", err)
        return result

    instances, err = load_yaml(graph_dir / "instances.yaml")
    if err:
        result.add_error("instances.yaml", "", err)
        return result

    workflows, err = load_yaml(graph_dir / "workflows.yaml")
    if err:
        result.add_error("workflows.yaml", "", err)
        return result

    # Validate each file
    validate_node_types(node_types, result)
    validate_instances(instances, node_types, result)
    validate_workflows(workflows, node_types, instances, result, workflow_filter)

    return result


def print_result(result: ValidationResult, verbose: bool = False):
    """Print validation results."""
    if result.errors:
        print(f"\n{len(result.errors)} error(s):")
        for err in result.errors:
            print(f"  ERROR [{err.file}] {err.path}: {err.message}")

    if result.warnings and verbose:
        print(f"\n{len(result.warnings)} warning(s):")
        for warn in result.warnings:
            print(f"  WARN  [{warn.file}] {warn.path}: {warn.message}")

    if result.is_valid:
        print(f"\nValid! ({len(result.warnings)} warnings)")
    else:
        print(f"\nInvalid. {len(result.errors)} error(s), {len(result.warnings)} warning(s)")


def find_leads_dir() -> Path:
    """Find the leads directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "leads"


def list_leads() -> list[str]:
    """List available leads with graph directories."""
    leads_dir = find_leads_dir()
    leads = []
    if leads_dir.exists():
        for lead_dir in leads_dir.iterdir():
            if lead_dir.is_dir() and (lead_dir / "graph").exists():
                leads.append(lead_dir.name)
    return sorted(leads)


def main():
    parser = argparse.ArgumentParser(description="Validate graph YAML files")
    parser.add_argument("--lead", "-l", help="Lead name (e.g., example-leads)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show warnings")
    parser.add_argument("--workflow", "-w", help="Validate specific workflow only")
    parser.add_argument("--list", action="store_true", help="List available leads")
    args = parser.parse_args()

    # List mode
    if args.list:
        leads = list_leads()
        if leads:
            print("Available leads:")
            for lead in leads:
                print(f"  {lead}")
        else:
            print("No leads found with graph directories")
        sys.exit(0)

    # Validate mode
    if not args.lead:
        parser.error("--lead is required. Use --list to see available leads.")

    leads_dir = find_leads_dir()
    graph_dir = leads_dir / args.lead / "graph"

    if not graph_dir.exists():
        print(f"Error: Graph directory not found: {graph_dir}")
        print(f"Available leads: {', '.join(list_leads())}")
        sys.exit(1)

    print(f"Validating: {args.lead}")

    result = validate_graph(graph_dir, args.workflow, args.verbose)
    print_result(result, args.verbose)

    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
