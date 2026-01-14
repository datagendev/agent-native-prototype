# Graph YAML Schema Definition

This document defines the schema for `graph.yaml` files used in enrichment workflows.

## Top-Level Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Unique identifier for this lead table |
| `description` | string | Yes | Human-readable description of the lead table |
| `source` | string | Yes | Path to source CSV file (relative to graph directory) |
| `columns` | object | Yes | Column definitions (inputs and outputs) |
| `nodes` | object | Yes | Available enrichment nodes |
| `workflows` | object | Yes | Named sequences of nodes to execute |
| `mermaid` | string | No | Mermaid diagram for visualization |

## Columns Section

Defines what columns exist in the table and their metadata.

```yaml
columns:
  inputs:
    <column_name>:
      type: string | integer | boolean | array
      description: "What this column contains"
      example: "example value"

  outputs:
    <column_name>:
      type: string | integer | boolean | array
      source: <node_name>  # Which node produces this column
      description: "What this column contains"
```

## Nodes Section

Defines available enrichment nodes and their configurations.

```yaml
nodes:
  <node_name>:
    description: string        # What this node does
    file: string              # Path to Python file (relative to graph/)
    class: string             # Python class name to instantiate
    input_cols: [string]      # Required input columns
    output_cols: [string]     # Columns this node produces
    config:                   # Default configuration
      <param>: <value>
```

### Output Column Templates

Use `{{prefix}}` for configurable column prefixes:

```yaml
output_cols: ["{{prefix}}_mentions_count", "{{prefix}}_mention_urls"]
config:
  output_prefix: "claude"  # Results in: claude_mentions_count, claude_mention_urls
```

## Workflows Section

Defines named sequences of nodes to execute.

```yaml
workflows:
  <workflow_name>:
    description: string       # What this workflow does
    nodes:                    # List of nodes to execute
      - <node_name>           # Simple node reference (uses defaults)

      - node: <node_name>     # Node with config override
        config:
          <param>: <value>

      - node: <node_name>     # Node with input mapping (multi-hop)
        input_map:
          <input_col>: <output_col_from_previous>
        output_prefix: string  # Prefix all outputs from this node
```

### Workflow Node Spec

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `node` | string | Yes* | Node name from nodes section |
| `config` | object | No | Override default node config |
| `input_map` | object | No | Map outputs from previous nodes to inputs |
| `output_prefix` | string | No | Prefix all output columns |

*Simple string reference (just `- node_name`) is shorthand for `- node: node_name`

### Multi-Hop Chaining

Use `input_map` to chain node outputs as inputs:

```yaml
workflows:
  ceo_profile:
    description: Find CEO and enrich their profile
    nodes:
      - find_ceo  # Produces: ceo_linkedin_url
      - node: profile_enrichment
        input_map:
          linkedin_url: ceo_linkedin_url  # Use output from previous node
        output_prefix: "ceo"  # Produces: ceo_headline, ceo_current_company
```

## Mermaid Section

Optional Mermaid diagram for visualizing the enrichment flow:

```yaml
mermaid: |
  flowchart LR
    subgraph Inputs
      linkedin_url["linkedin_url"]
    end

    subgraph Nodes
      PE[profile_enrichment]
    end

    subgraph Outputs
      headline["headline"]
    end

    linkedin_url --> PE --> headline
```

## Complete Example

```yaml
name: my-leads
description: Lead table for prospecting campaign
source: table.csv

columns:
  inputs:
    linkedin_url:
      type: string
      description: LinkedIn profile URL
      example: "https://linkedin.com/in/username"

  outputs:
    headline:
      type: string
      source: profile_enrichment
      description: LinkedIn profile headline

nodes:
  profile_enrichment:
    description: Fetch LinkedIn profile data
    file: nodes/profile_enrichment.py
    class: ProfileEnrichment
    input_cols: [linkedin_url]
    output_cols: [headline, current_company, location, follower_count]
    config: {}

workflows:
  basic:
    description: Basic profile enrichment
    nodes:
      - profile_enrichment

mermaid: |
  flowchart LR
    linkedin_url --> PE[profile_enrichment] --> headline
```

## File Structure

```
leads/<lead_name>/
  table.csv              # Source data
  graph/
    graph.yaml           # This file - workflow definition
    graph_schema.md      # Schema reference (this doc)
    __init__.py          # Python loader
    nodes/
      __init__.py        # Node registry
      <node_name>.py     # Node implementations
```

## Node Python Implementation

Each node must extend `Graph` base class:

```python
from primitives.base import Graph

class MyNode(Graph):
    """Node description."""

    @property
    def input_cols(self) -> list[str]:
        return ["required_input_column"]

    @property
    def output_cols(self) -> list[str]:
        return ["output_column_1", "output_column_2"]

    def run(self, row: dict) -> tuple[dict, str]:
        # Process row, return (outputs, error)
        return {"output_column_1": "value", "output_column_2": "value"}, ""
```
