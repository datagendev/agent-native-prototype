"""
Graph definition for example-leads table.

Structure:
  - node_types.yaml: Base node definitions
  - instances.yaml: Pre-configured nodes
  - workflows.yaml: Workflow compositions with connections
  - nodes/: Python node implementations

Usage:
  from graph import load_workflow, load_instance, get_workflows

  # Load a workflow (list of nodes)
  workflow = load_workflow("competitor_scan")

  # Load a single instance
  node = load_instance("claude_mentions")
"""

from .loader import (
    GraphLoader,
    get_loader,
    get_workflows,
    get_node_types,
    get_instances,
    load_workflow,
    load_instance,
)

from .nodes import NODES, KeywordMentions, ProfileEnrichment, FindCEO

# Register node classes with loader
_loader = get_loader()
for name, cls in NODES.items():
    _loader.register_node_class(name, cls)

# Backwards compatibility alias
GRAPHS = NODES

__all__ = [
    "GraphLoader",
    "get_loader",
    "get_workflows",
    "get_node_types",
    "get_instances",
    "load_workflow",
    "load_instance",
    "NODES",
    "GRAPHS",
    "KeywordMentions",
    "ProfileEnrichment",
    "FindCEO",
]
