# Workflow Examples

Examples of the three-file graph definition system.

## File Structure

```
graph/
  node_types.yaml    # Base definitions (library)
  instances.yaml     # Pre-configured nodes (reusable)
  workflows.yaml     # Workflow compositions (connections)
  nodes/             # Python implementations
```

## 1. Node Types (`node_types.yaml`)

Define base node capabilities:

```yaml
version: "1.0"

node_types:
  profile_enrichment:
    description: Fetch LinkedIn profile data
    file: nodes/profile_enrichment.py
    class: ProfileEnrichment
    inputs:
      linkedin_url:
        type: string
        required: true
    outputs:
      headline: { type: string }
      current_company: { type: string }
      location: { type: string }
      follower_count: { type: integer }
    parameters:
      output_prefix:
        type: string
        default: ""
      fields:
        type: array
        default: ["headline", "current_company", "location", "follower_count"]

  keyword_mentions:
    description: Find posts mentioning keywords
    file: nodes/keyword_mentions.py
    class: KeywordMentions
    inputs:
      linkedin_url:
        type: string
        required: true
    outputs:
      mentions_count: { type: integer }
      mention_urls: { type: string }
      first_mention_date: { type: string }
    parameters:
      keywords:
        type: array
        required: true
      output_prefix:
        type: string
        required: true
      max_posts:
        type: integer
        default: 100

  find_executive:
    description: Find executive from company domain
    file: nodes/find_executive.py
    class: FindExecutive
    inputs:
      company_domain:
        type: string
        required: true
    outputs:
      name: { type: string }
      linkedin_url: { type: string }
      title: { type: string }
    parameters:
      role:
        type: string
        required: true
        enum: ["CEO", "CTO", "CFO", "Founder"]
      output_prefix:
        type: string
        required: true
```

## 2. Instances (`instances.yaml`)

Create pre-configured nodes:

```yaml
version: "1.0"
node_types_file: node_types.yaml

instances:
  # Keyword scanners
  claude_mentions:
    type: keyword_mentions
    description: Find Claude Code mentions
    parameters:
      keywords: ["claude code", "claude-code", "claudecode"]
      output_prefix: "claude"
      max_posts: 200

  datagen_mentions:
    type: keyword_mentions
    description: Find DataGen mentions
    parameters:
      keywords: ["datagen", "datagen.dev"]
      output_prefix: "datagen"

  cursor_mentions:
    type: keyword_mentions
    description: Find Cursor IDE mentions
    parameters:
      keywords: ["cursor ai", "cursor ide"]
      output_prefix: "cursor"

  # Executive lookups
  ceo_lookup:
    type: find_executive
    description: Find CEO from company domain
    parameters:
      role: "CEO"
      output_prefix: "ceo"

  cto_lookup:
    type: find_executive
    description: Find CTO from company domain
    parameters:
      role: "CTO"
      output_prefix: "cto"

  # Profile variants
  basic_profile:
    type: profile_enrichment
    description: Basic profile enrichment
    parameters:
      output_prefix: ""

  ceo_profile:
    type: profile_enrichment
    description: Enrich CEO's LinkedIn profile
    parameters:
      output_prefix: "ceo"
```

## 3. Workflows (`workflows.yaml`)

Compose workflows with explicit connections:

```yaml
version: "1.0"
node_types_file: node_types.yaml
instances_file: instances.yaml

table:
  name: example-leads
  description: Lead enrichment table
  source: table.csv
  inputs:
    linkedin_url:
      type: string
      description: LinkedIn profile URL
    company_domain:
      type: string
      description: Company website domain

workflows:
  # Simple: single node
  profile_only:
    description: Basic profile enrichment
    nodes:
      - basic_profile
    connections:
      - from: $input.linkedin_url
        to: basic_profile.linkedin_url

  # Parallel: multiple nodes on same input
  competitor_scan:
    description: Scan for competitor mentions
    nodes:
      - claude_mentions
      - cursor_mentions
      - datagen_mentions
    connections:
      - from: $input.linkedin_url
        to: claude_mentions.linkedin_url
      - from: $input.linkedin_url
        to: cursor_mentions.linkedin_url
      - from: $input.linkedin_url
        to: datagen_mentions.linkedin_url

  # Sequential: chain outputs to inputs
  ceo_profile:
    description: Find CEO and enrich their profile
    nodes:
      - ceo_lookup
      - ceo_profile
    connections:
      - from: $input.company_domain
        to: ceo_lookup.company_domain
      - from: ceo_lookup.linkedin_url
        to: ceo_profile.linkedin_url

  # Mixed: parallel + sequential
  full_enrichment:
    description: Complete enrichment
    nodes:
      - basic_profile
      - claude_mentions
      - ceo_lookup
    connections:
      - from: $input.linkedin_url
        to: basic_profile.linkedin_url
      - from: $input.linkedin_url
        to: claude_mentions.linkedin_url
      - from: $input.company_domain
        to: ceo_lookup.company_domain

  # Inline: one-off configuration
  custom_scan:
    description: Custom keyword scan
    nodes:
      - id: windsurf_scan
        type: keyword_mentions
        parameters:
          keywords: ["windsurf", "codeium"]
          output_prefix: "windsurf"
    connections:
      - from: $input.linkedin_url
        to: windsurf_scan.linkedin_url

  # Override: modify instance parameters
  deep_claude_scan:
    description: Extended Claude scan
    nodes:
      - id: claude_deep
        instance: claude_mentions
        parameters:
          max_posts: 500
    connections:
      - from: $input.linkedin_url
        to: claude_deep.linkedin_url
```

## Connection Syntax

| Pattern | Meaning |
|---------|---------|
| `$input.column` | Column from source CSV |
| `node_id.field` | Output from a node |
| `$output.column` | Final output column |

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

```
$input.linkedin_url --> [basic_profile] --> headline, company, ...
```

### 2. Parallel (Fan-out)

Multiple nodes receive the same input:

```yaml
competitor_scan:
  nodes:
    - claude_mentions
    - cursor_mentions
  connections:
    - from: $input.linkedin_url
      to: claude_mentions.linkedin_url
    - from: $input.linkedin_url
      to: cursor_mentions.linkedin_url
```

```
                    ┌─> [claude_mentions] --> claude_*
$input.linkedin_url ─┤
                    └─> [cursor_mentions] --> cursor_*
```

### 3. Sequential (Chain)

Output of one feeds input of next:

```yaml
ceo_profile:
  nodes:
    - ceo_lookup
    - ceo_profile
  connections:
    - from: $input.company_domain
      to: ceo_lookup.company_domain
    - from: ceo_lookup.linkedin_url
      to: ceo_profile.linkedin_url
```

```
$input.company_domain --> [ceo_lookup] --> ceo_linkedin_url
                                              |
                                              v
                          [ceo_profile] <-----┘
                              |
                              v
                         ceo_headline, ceo_company, ...
```

### 4. DAG (Mixed)

Combine parallel and sequential:

```yaml
full_pipeline:
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

```
$input.linkedin_url ──┬─> [basic_profile] --> headline, company
                      └─> [claude_mentions] --> claude_*

$input.company_domain --> [ceo_lookup] --> ceo_linkedin_url
                                               |
                                               v
                           [ceo_profile] <-----┘
                               |
                               v
                          ceo_headline, ceo_company
```

## Node Reference Types

### 1. Instance Reference (String)

Reference a pre-configured instance:

```yaml
nodes:
  - claude_mentions    # Uses instance as-is
```

### 2. Inline Type Definition

Create one-off configuration:

```yaml
nodes:
  - id: custom_scan
    type: keyword_mentions
    parameters:
      keywords: ["custom"]
      output_prefix: "custom"
```

### 3. Instance Override

Start from instance, override some parameters:

```yaml
nodes:
  - id: extended_scan
    instance: claude_mentions
    parameters:
      max_posts: 500    # Override just this param
```

## Parameter Resolution

Parameters merge in order:

```
Node Type defaults  ->  Instance params  ->  Workflow overrides
```

Example:
```yaml
# node_types.yaml
keyword_mentions:
  parameters:
    max_posts: { default: 100 }

# instances.yaml
claude_mentions:
  parameters:
    max_posts: 200  # Override to 200

# workflows.yaml
deep_scan:
  nodes:
    - id: deep
      instance: claude_mentions
      parameters:
        max_posts: 500  # Final value: 500
```

## CLI Commands

```bash
# List available workflows
python3 scripts/graph_enrich.py --lead {name} --list

# Validate workflow
python3 scripts/graph_enrich.py --lead {name} --workflow {workflow} --validate

# Preview (first N rows)
python3 scripts/graph_enrich.py --lead {name} --workflow {workflow} --preview --limit 5

# Full run
python3 scripts/graph_enrich.py --lead {name} --workflow {workflow}
```
