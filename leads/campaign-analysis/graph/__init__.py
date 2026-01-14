"""Campaign Analysis - Graph Module

Workflows for enriching HeyReach campaign data with reply rate statistics.
"""

import yaml
import sys
from pathlib import Path

# Add scripts to path for integration imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from integrations import get_integration_class

GRAPH_DIR = Path(__file__).parent


class IntegrationWrapper:
    """Wrapper to make Integration instances callable for graph_enrich.py"""

    def __init__(self, integration):
        self.integration = integration
        self.input_cols = integration.input_cols
        self.output_cols = integration.output_cols

    def __call__(self, row: dict) -> tuple[dict, str]:
        """Make integration callable"""
        return self.integration.enrich(row)

    def __repr__(self):
        return f"{self.integration.__class__.__name__}"


def load_workflow(workflow_name: str) -> list:
    """Load a workflow as list of callable integration instances."""
    with open(GRAPH_DIR / "graph.yaml") as f:
        config = yaml.safe_load(f)

    workflows = config.get("workflows", {})
    if workflow_name not in workflows:
        raise ValueError(f"Workflow '{workflow_name}' not found")

    workflow = workflows[workflow_name]
    instances = []

    for step in workflow.get("steps", []):
        if "integration" in step:
            integration_name = step["integration"]
            IntegrationClass = get_integration_class(integration_name)
            if not IntegrationClass:
                raise ValueError(f"Integration '{integration_name}' not found")
            # Wrap integration to make it callable
            instances.append(IntegrationWrapper(IntegrationClass()))
        else:
            raise ValueError(f"Unknown step type: {step}")

    return instances


def get_workflows() -> dict:
    """Get all available workflows."""
    with open(GRAPH_DIR / "graph.yaml") as f:
        config = yaml.safe_load(f)
    return config.get("workflows", {})
