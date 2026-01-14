# Graph Schema v1.0

This document defines the schema for the three-file graph definition system.

## File Structure

```
graph/
  node_types.yaml    # Base node definitions (library)
  instances.yaml     # Pre-configured nodes (reusable configs)
  workflows.yaml     # Workflow compositions (how nodes connect)
  nodes/             # Python implementations
    profile_enrichment.py
    keyword_mentions.py
    find_executive.py
```

## Hierarchy

```
Node Types     →    Node Instances    →    Workflow Nodes
(library)           (configured)           (composition)

Defines WHAT        Configures HOW         Defines WHEN/WHERE
a node can do       a node behaves         nodes connect
```

## 1. Node Types (`node_types.yaml`)

Base definitions - like classes in OOP.

### Schema

```yaml
version: "1.0"

node_types:
  <node_type_name>:
    description: string           # What this node does
    file: string                  # Path to Python file
    class: string                 # Python class name

    inputs:                       # Data received from connections
      <field_name>:
        type: string|integer|boolean|array|object
        required: boolean
        description: string
        example: any

    outputs:                      # Data produced for downstream
      <field_name>:
        type: string|integer|boolean|array|object
        description: string

    parameters:                   # Configuration (design-time)
      <param_name>:
        type: string|integer|boolean|array|object
        required: boolean
        default: any
        enum: [...]               # Optional: allowed values
        minimum: number           # Optional: for integers
        maximum: number
        secret: boolean           # Optional: marks sensitive values
        description: string
```

### Example

```yaml
node_types:
  keyword_mentions:
    description: Find posts mentioning specific keywords
    file: nodes/keyword_mentions.py
    class: KeywordMentions

    inputs:
      linkedin_url:
        type: string
        required: true

    outputs:
      mentions_count:
        type: integer
      mention_urls:
        type: string

    parameters:
      keywords:
        type: array
        items: string
        required: true
      output_prefix:
        type: string
        required: true
      max_posts:
        type: integer
        default: 100
```

## 2. Node Instances (`instances.yaml`)

Pre-configured nodes - like objects in OOP.

### Schema

```yaml
version: "1.0"
node_types_file: node_types.yaml  # Reference to types

instances:
  <instance_name>:
    type: string                  # References node_type name
    description: string           # What this configuration does
    parameters:                   # Override default parameters
      <param_name>: value
```

### Example

```yaml
instances:
  claude_mentions:
    type: keyword_mentions
    description: Find posts mentioning Claude Code
    parameters:
      keywords: ["claude code", "claude-code"]
      output_prefix: "claude"
      max_posts: 200

  datagen_mentions:
    type: keyword_mentions
    description: Find posts mentioning DataGen
    parameters:
      keywords: ["datagen", "datagen.dev"]
      output_prefix: "datagen"
```

## 3. Workflows (`workflows.yaml`)

Compositions with explicit connections.

### Schema

```yaml
version: "1.0"
node_types_file: node_types.yaml
instances_file: instances.yaml

table:
  name: string
  description: string
  source: string                  # CSV filename

  inputs:                         # Columns from source CSV
    <column_name>:
      type: string
      description: string

workflows:
  <workflow_name>:
    description: string

    nodes:                        # List of nodes to use
      - <instance_name>           # Reference to instance

      - id: string                # Inline definition
        type: <node_type_name>
        parameters: { ... }

      - id: string                # Override instance
        instance: <instance_name>
        parameters: { ... }       # Additional overrides

    connections:                  # Explicit data flow
      - from: <source>.<field>
        to: <target>.<field>
```

### Connection Syntax

| Pattern | Meaning |
|---------|---------|
| `$input.column_name` | Column from source CSV |
| `node_id.field_name` | Output field from a node |
| `$output.column_name` | Final output column |

### Example

```yaml
workflows:
  ceo_profile:
    description: Find CEO and enrich their profile
    nodes:
      - ceo_lookup              # Instance reference
      - ceo_profile             # Another instance
    connections:
      - from: $input.company_domain
        to: ceo_lookup.company_domain
      - from: ceo_lookup.linkedin_url
        to: ceo_profile.linkedin_url
```

## Node Resolution Order

When the executor loads a workflow node, parameters merge in this order:

```
Node Type defaults  →  Instance parameters  →  Workflow overrides
     (base)              (configured)            (inline)
```

Later values override earlier ones.

### Example Resolution

```yaml
# node_types.yaml
keyword_mentions:
  parameters:
    max_posts: { default: 100 }
    date_range_days: { default: 90 }

# instances.yaml
claude_mentions:
  type: keyword_mentions
  parameters:
    max_posts: 200              # Override: 100 → 200

# workflows.yaml
deep_scan:
  nodes:
    - id: deep_claude
      instance: claude_mentions
      parameters:
        max_posts: 500          # Override: 200 → 500

# Final resolved parameters:
# max_posts: 500 (workflow override)
# date_range_days: 90 (type default, not overridden)
```

## Workflow Patterns

### 1. Simple (Single Node)

```yaml
profile_only:
  nodes:
    - basic_profile
  connections:
    - from: $input.linkedin_url
      to: basic_profile.linkedin_url
```

### 2. Parallel (Fan-out)

Multiple nodes receive the same input:

```yaml
competitor_scan:
  nodes:
    - claude_mentions
    - cursor_mentions
    - copilot_mentions
  connections:
    - from: $input.linkedin_url
      to: claude_mentions.linkedin_url
    - from: $input.linkedin_url
      to: cursor_mentions.linkedin_url
    - from: $input.linkedin_url
      to: copilot_mentions.linkedin_url
```

### 3. Sequential (Chain)

Output of one node feeds input of next:

```yaml
ceo_profile:
  nodes:
    - ceo_lookup
    - ceo_profile
  connections:
    - from: $input.company_domain
      to: ceo_lookup.company_domain
    - from: ceo_lookup.linkedin_url    # Output from first
      to: ceo_profile.linkedin_url      # Input to second
```

### 4. Mixed (DAG)

Combine parallel and sequential:

```yaml
full_enrichment:
  nodes:
    - basic_profile
    - claude_mentions
    - ceo_lookup
    - ceo_profile
  connections:
    # Parallel from linkedin_url
    - from: $input.linkedin_url
      to: basic_profile.linkedin_url
    - from: $input.linkedin_url
      to: claude_mentions.linkedin_url
    # Parallel from company_domain
    - from: $input.company_domain
      to: ceo_lookup.company_domain
    # Sequential chain
    - from: ceo_lookup.linkedin_url
      to: ceo_profile.linkedin_url
```

## Python Node Implementation

Nodes must implement the `Graph` base class:

```python
from primitives.base import Graph

class KeywordMentions(Graph):
    """Find posts mentioning specific keywords."""

    def __init__(
        self,
        keywords: list[str],
        output_prefix: str,
        max_posts: int = 100,
        date_range_days: int = 90,
    ):
        self.keywords = keywords
        self.output_prefix = output_prefix
        self.max_posts = max_posts
        self.date_range_days = date_range_days

    @property
    def input_cols(self) -> list[str]:
        return ["linkedin_url"]

    @property
    def output_cols(self) -> list[str]:
        p = self.output_prefix
        return [f"{p}_mentions_count", f"{p}_mention_urls", f"{p}_first_mention_date"]

    @property
    def parameters(self) -> dict:
        """Current parameters for hashing/audit."""
        return {
            "keywords": self.keywords,
            "output_prefix": self.output_prefix,
            "max_posts": self.max_posts,
            "date_range_days": self.date_range_days,
        }

    def run(self, row: dict) -> tuple[dict, str]:
        """Execute node. Returns (result_dict, error_string)."""
        linkedin_url = row.get("linkedin_url")
        if not linkedin_url:
            return {}, "missing linkedin_url"

        # ... implementation ...

        p = self.output_prefix
        return {
            f"{p}_mentions_count": count,
            f"{p}_mention_urls": urls,
            f"{p}_first_mention_date": first_date,
        }, ""
```

## Validation Rules

### Node Types
- `file` must exist relative to graph directory
- `class` must be importable from file
- All `required: true` inputs must be connected in workflows
- All `required: true` parameters must have values (default or explicit)

### Instances
- `type` must reference existing node type
- All `required: true` parameters must be provided

### Workflows
- All node references must exist (instance or inline type)
- All connections must reference valid fields
- No circular dependencies in connections
- Every node input must have exactly one connection (or be optional)

## Migration from Single-File

If migrating from the old `graph.yaml` format:

| Old | New |
|-----|-----|
| `nodes:` | Split to `node_types.yaml` |
| `workflows[].nodes[].config` | `instances.yaml` or inline |
| `workflows[].nodes[].input_map` | `workflows.yaml` connections |
| `columns:` | `workflows.yaml` table.inputs |
