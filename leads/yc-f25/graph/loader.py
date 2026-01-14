"""
Graph Loader - Split-file structure only

File Structure:
  - node_types.yaml: Base node definitions
  - instances.yaml: Pre-configured nodes
  - workflows.yaml: Workflow compositions with connections

Usage:
  from graph.loader import GraphLoader

  loader = GraphLoader()
  node = loader.load_instance("claude_mentions")
  workflow = loader.load_workflow("competitor_scan")
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class NodeType:
    """Base node type definition."""
    name: str
    description: str
    file: str
    class_name: str
    inputs: dict[str, dict]
    outputs: dict[str, dict]
    parameters: dict[str, dict]

    def get_default_parameters(self) -> dict:
        """Get default values for all parameters."""
        defaults = {}
        for param_name, param_def in self.parameters.items():
            if "default" in param_def:
                defaults[param_name] = param_def["default"]
        return defaults


@dataclass
class NodeInstance:
    """Pre-configured node instance."""
    name: str
    type_name: str
    description: str
    parameters: dict[str, Any]


@dataclass
class WorkflowNode:
    """A node in a workflow (resolved instance)."""
    id: str
    type_name: str
    parameters: dict[str, Any]
    instance_name: str | None = None


@dataclass
class Connection:
    """Connection between nodes."""
    from_node: str
    from_field: str
    to_node: str
    to_field: str


@dataclass
class Workflow:
    """Workflow definition with nodes and connections."""
    name: str
    description: str
    nodes: list[WorkflowNode]
    connections: list[Connection]
    conditions: dict[str, Any] | None = None


class GraphLoader:
    """
    Loads graph definitions from split YAML files.

    Structure:
      - node_types.yaml: Base definitions
      - instances.yaml: Pre-configured nodes
      - workflows.yaml: Workflow compositions
    """

    def __init__(self, graph_dir: Path | str = None):
        if graph_dir is None:
            graph_dir = Path(__file__).parent
        self.graph_dir = Path(graph_dir)

        self._node_types: dict[str, NodeType] | None = None
        self._instances: dict[str, NodeInstance] | None = None
        self._workflows: dict[str, dict] | None = None
        self._table_config: dict | None = None
        self._node_classes: dict[str, type] = {}

    def _load_yaml(self, path: Path) -> dict:
        """Load YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

        try:
            import yaml
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            # Fallback to JSON if YAML not available
            json_path = path.with_suffix(".json")
            if json_path.exists():
                with open(json_path, "r") as f:
                    return json.load(f)
            raise ImportError("PyYAML required. Install with: pip install pyyaml")

    def _ensure_loaded(self):
        """Load all definitions if not already loaded."""
        if self._node_types is not None:
            return

        # Load split files
        node_types_raw = self._load_yaml(self.graph_dir / "node_types.yaml")
        instances_raw = self._load_yaml(self.graph_dir / "instances.yaml")
        workflows_raw = self._load_yaml(self.graph_dir / "workflows.yaml")

        # Parse node types
        self._node_types = {}
        for name, type_def in node_types_raw.get("node_types", {}).items():
            self._node_types[name] = NodeType(
                name=name,
                description=type_def.get("description", ""),
                file=type_def.get("file", f"nodes/{name}.py"),
                class_name=type_def.get("class", name.title().replace("_", "")),
                inputs=type_def.get("inputs", {}),
                outputs=type_def.get("outputs", {}),
                parameters=type_def.get("parameters", {}),
            )

        # Parse instances
        self._instances = {}
        for name, inst_def in instances_raw.get("instances", {}).items():
            self._instances[name] = NodeInstance(
                name=name,
                type_name=inst_def.get("type", ""),
                description=inst_def.get("description", ""),
                parameters=inst_def.get("parameters", {}),
            )

        self._workflows = workflows_raw.get("workflows", {})
        self._table_config = workflows_raw.get("table", {})

    def register_node_class(self, name: str, cls: type):
        """Register a Python class for a node type."""
        self._node_classes[name] = cls

    def get_node_types(self) -> dict[str, NodeType]:
        """Get all node type definitions."""
        self._ensure_loaded()
        return self._node_types

    def get_instances(self) -> dict[str, NodeInstance]:
        """Get all node instance definitions."""
        self._ensure_loaded()
        return self._instances

    def get_workflows(self) -> dict[str, dict]:
        """Get all workflow definitions."""
        self._ensure_loaded()
        return self._workflows

    def get_table_config(self) -> dict:
        """Get table configuration."""
        self._ensure_loaded()
        return self._table_config

    def resolve_parameters(
        self,
        type_name: str,
        instance_name: str | None = None,
        overrides: dict | None = None,
    ) -> dict:
        """
        Resolve parameters: Type defaults -> Instance params -> Overrides
        """
        self._ensure_loaded()

        node_type = self._node_types.get(type_name)
        if not node_type:
            raise ValueError(f"Unknown node type: {type_name}")

        # Start with type defaults
        params = node_type.get_default_parameters()

        # Apply instance parameters
        if instance_name:
            instance = self._instances.get(instance_name)
            if instance:
                params.update(instance.parameters)

        # Apply overrides
        if overrides:
            params.update(overrides)

        return params

    def load_node(
        self,
        type_name: str,
        instance_name: str | None = None,
        parameters: dict | None = None,
        node_id: str | None = None,
    ):
        """
        Load and instantiate a node.
        """
        self._ensure_loaded()

        # Get the node class
        if type_name not in self._node_classes:
            try:
                from . import nodes
                if hasattr(nodes, "NODES") and type_name in nodes.NODES:
                    self._node_classes[type_name] = nodes.NODES[type_name]
                else:
                    raise ValueError(f"No class registered for: {type_name}")
            except ImportError:
                raise ValueError(f"No class registered for: {type_name}")

        NodeClass = self._node_classes[type_name]
        final_params = self.resolve_parameters(type_name, instance_name, parameters)

        # Instantiate
        node = NodeClass(**final_params)

        # Attach metadata
        node._node_name = node_id or instance_name or type_name
        node._node_type = type_name
        node._node_instance = instance_name
        node._node_config = final_params

        return node

    def load_instance(self, instance_name: str, parameters: dict | None = None):
        """Load a pre-configured node instance."""
        self._ensure_loaded()

        if instance_name not in self._instances:
            available = ", ".join(self._instances.keys())
            raise ValueError(f"Instance '{instance_name}' not found. Available: {available}")

        instance = self._instances[instance_name]
        return self.load_node(
            type_name=instance.type_name,
            instance_name=instance_name,
            parameters=parameters,
            node_id=instance_name,
        )

    def _parse_connection(self, conn_def: dict) -> Connection:
        """Parse a connection definition."""
        from_parts = conn_def["from"].split(".")
        to_parts = conn_def["to"].split(".")

        return Connection(
            from_node=from_parts[0],
            from_field=from_parts[1] if len(from_parts) > 1 else "",
            to_node=to_parts[0],
            to_field=to_parts[1] if len(to_parts) > 1 else "",
        )

    def _resolve_workflow_node(self, node_spec) -> WorkflowNode:
        """Resolve a workflow node specification."""
        self._ensure_loaded()

        # String reference to instance
        if isinstance(node_spec, str):
            if node_spec in self._instances:
                instance = self._instances[node_spec]
                return WorkflowNode(
                    id=node_spec,
                    type_name=instance.type_name,
                    parameters=self.resolve_parameters(instance.type_name, node_spec, None),
                    instance_name=node_spec,
                )
            elif node_spec in self._node_types:
                return WorkflowNode(
                    id=node_spec,
                    type_name=node_spec,
                    parameters=self.resolve_parameters(node_spec, None, None),
                )
            else:
                raise ValueError(f"Unknown node reference: {node_spec}")

        # Dict with 'instance' key (override existing instance)
        if "instance" in node_spec:
            instance_name = node_spec["instance"]
            if instance_name not in self._instances:
                raise ValueError(f"Unknown instance: {instance_name}")

            instance = self._instances[instance_name]
            return WorkflowNode(
                id=node_spec.get("id", instance_name),
                type_name=instance.type_name,
                parameters=self.resolve_parameters(
                    instance.type_name,
                    instance_name,
                    node_spec.get("parameters"),
                ),
                instance_name=instance_name,
            )

        # Dict with 'type' key (inline instance)
        if "type" in node_spec:
            type_name = node_spec["type"]
            if type_name not in self._node_types:
                raise ValueError(f"Unknown node type: {type_name}")

            return WorkflowNode(
                id=node_spec.get("id", type_name),
                type_name=type_name,
                parameters=self.resolve_parameters(
                    type_name, None, node_spec.get("parameters")
                ),
            )

        raise ValueError(f"Invalid node specification: {node_spec}")

    def load_workflow(self, workflow_name: str) -> list:
        """
        Load a workflow as a list of instantiated nodes.
        """
        self._ensure_loaded()

        if workflow_name not in self._workflows:
            available = ", ".join(self._workflows.keys())
            raise ValueError(f"Workflow '{workflow_name}' not found. Available: {available}")

        workflow_def = self._workflows[workflow_name]
        nodes_spec = workflow_def.get("nodes", [])
        connections_spec = workflow_def.get("connections", [])

        # Build connection lookup for input_map
        input_map_by_node: dict[str, dict] = {}
        for conn_def in connections_spec:
            conn = self._parse_connection(conn_def)
            if conn.to_node not in input_map_by_node:
                input_map_by_node[conn.to_node] = {}

            if conn.from_node == "$input":
                if conn.from_field != conn.to_field:
                    input_map_by_node[conn.to_node][conn.to_field] = conn.from_field
            else:
                input_map_by_node[conn.to_node][conn.to_field] = conn.from_field

        # Instantiate nodes
        result = []
        for node_spec in nodes_spec:
            wf_node = self._resolve_workflow_node(node_spec)

            node = self.load_node(
                type_name=wf_node.type_name,
                instance_name=wf_node.instance_name,
                parameters=wf_node.parameters,
                node_id=wf_node.id,
            )

            node._input_map = input_map_by_node.get(wf_node.id, {})
            node._output_prefix = wf_node.parameters.get("output_prefix")

            result.append(node)

        return result

    def get_workflow_metadata(self, workflow_name: str) -> Workflow:
        """Get workflow metadata without instantiating nodes."""
        self._ensure_loaded()

        if workflow_name not in self._workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        workflow_def = self._workflows[workflow_name]

        nodes = [self._resolve_workflow_node(n) for n in workflow_def.get("nodes", [])]
        connections = [self._parse_connection(c) for c in workflow_def.get("connections", [])]

        return Workflow(
            name=workflow_name,
            description=workflow_def.get("description", ""),
            nodes=nodes,
            connections=connections,
            conditions=workflow_def.get("conditions"),
        )

    def get_workflow_conditions(self, workflow_name: str) -> dict[str, Any] | None:
        """Get workflow conditions (WHERE clause filters)."""
        self._ensure_loaded()

        if workflow_name not in self._workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        workflow_def = self._workflows[workflow_name]
        return workflow_def.get("conditions")


# Singleton instance
_loader: GraphLoader | None = None


def get_loader() -> GraphLoader:
    """Get the default GraphLoader instance."""
    global _loader
    if _loader is None:
        _loader = GraphLoader()
    return _loader


# Convenience functions
def load_instance(instance_name: str, parameters: dict = None):
    return get_loader().load_instance(instance_name, parameters)


def load_workflow(workflow_name: str) -> list:
    return get_loader().load_workflow(workflow_name)


def get_workflows() -> dict:
    return get_loader().get_workflows()


def get_node_types() -> dict:
    return get_loader().get_node_types()


def get_instances() -> dict:
    return get_loader().get_instances()


def get_workflow_conditions(workflow_name: str) -> dict | None:
    """Get workflow conditions (WHERE clause filters)."""
    return get_loader().get_workflow_conditions(workflow_name)
