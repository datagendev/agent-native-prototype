# Claude Code Detector Node

Node for detecting Claude Code mentions in LinkedIn profiles for YC F25 leads.

## Overview

The `claude_code_detector` node scans a LinkedIn profile for posts mentioning Claude Code and returns:
- Count of mentions
- URLs of posts with mentions (max 5)
- Boolean flag indicating usage

## Node Type Definition

**Location**: `leads/yc-f25/graph/node_types.yaml`

```yaml
claude_code_detector:
  description: Scan LinkedIn profile for Claude Code mentions
  file: nodes/claude_code_detector.py
  class: ClaudeCodeDetector

  inputs:
    founder_linkedin_url:
      type: string
      required: true
      description: LinkedIn profile URL to scan for posts

  outputs:
    claude_code_mentions:
      type: integer
      description: Number of posts mentioning Claude Code
    claude_code_urls:
      type: string
      description: URLs of posts (comma-separated, max 5)
    uses_claude_code:
      type: boolean
      description: Whether the founder mentions Claude Code

  parameters:
    keywords:
      type: array
      default: ["claude code", "claude-code", "claudecode"]
      description: Keywords to search for (OR logic)
    max_posts:
      type: integer
      default: 50
      description: Maximum posts to scan
    output_prefix:
      type: string
      default: ""
      description: Prefix for output columns
```

## Pre-configured Instances

**Location**: `leads/yc-f25/graph/instances.yaml`

### 1. claude_code_check

Default configuration for Claude Code detection:

```yaml
claude_code_check:
  type: claude_code_detector
  parameters:
    keywords:
      - "claude code"
      - "claude-code"
      - "claudecode"
      - "@anthropic claude code"
    max_posts: 50
    output_prefix: ""
```

**Output columns**:
- `claude_code_mentions` (integer)
- `claude_code_urls` (string)
- `uses_claude_code` (boolean)

### 2. founder_claude_code_check

Same as above but with "founder_" prefix:

```yaml
founder_claude_code_check:
  type: claude_code_detector
  parameters:
    keywords:
      - "claude code"
      - "claude-code"
      - "claudecode"
    max_posts: 50
    output_prefix: "founder"
```

**Output columns**:
- `founder_claude_code_mentions` (integer)
- `founder_claude_code_urls` (string)
- `founder_uses_claude_code` (boolean)

## Implementation

**Location**: `leads/yc-f25/graph/nodes/claude_code_detector.py`

The node is implemented as a Graph that composes three primitives:

1. **linkedin_posts**: Fetch recent posts from LinkedIn profile
2. **filter_by**: Filter posts by Claude Code keywords
3. **aggregate**: Count mentions and collect URLs

### Error Handling

The node follows the error-first pattern:

```python
def run(self, row: dict) -> tuple[dict, str]:
    # Returns: (output_dict, error_message)
    # On error: Returns empty result + error description
```

**Empty result on error**:
```python
{
    "claude_code_mentions": 0,
    "claude_code_urls": "",
    "uses_claude_code": False
}
```

## Usage Example

### In Python

```python
from leads.yc_f25.graph.nodes import ClaudeCodeDetector

# Create detector with custom parameters
detector = ClaudeCodeDetector(
    keywords=["claude code", "claudecode"],
    max_posts=100,
    output_prefix=""
)

# Run on a row of data
row = {
    "founder_linkedin_url": "https://linkedin.com/in/johndoe"
}

result, error = detector.run(row)

if error:
    print(f"Error: {error}")
else:
    print(f"Mentions: {result['claude_code_mentions']}")
    print(f"Uses Claude Code: {result['uses_claude_code']}")
    print(f"URLs: {result['claude_code_urls']}")
```

### In Graph Pipeline

```yaml
# Example workflow using the instance
workflow:
  - node: yc_founder_lookup
    inputs:
      name: "@company_name"
      yc_url: "@yc_url"

  - node: claude_code_check  # Use pre-configured instance
    inputs:
      founder_linkedin_url: "#founder_linkedin_url"
```

## Output Format

### Success Case

```python
{
    "claude_code_mentions": 3,
    "claude_code_urls": "https://linkedin.com/posts/..., https://linkedin.com/posts/...",
    "uses_claude_code": True
}
```

### No Mentions Case

```python
{
    "claude_code_mentions": 0,
    "claude_code_urls": "",
    "uses_claude_code": False
}
```

### Error Case

Returns empty result + error message:

```python
result = {
    "claude_code_mentions": 0,
    "claude_code_urls": "",
    "uses_claude_code": False
}
error = "failed to fetch posts: rate limited"
```

## Dependencies

- `primitives.linkedin_posts`: Fetch LinkedIn posts
- `primitives.filter_by`: Keyword filtering
- `primitives.aggregate`: Result aggregation

## Testing

```python
# Test with sample data
from leads.yc_f25.graph.nodes import ClaudeCodeDetector

detector = ClaudeCodeDetector()

test_row = {
    "founder_linkedin_url": "https://linkedin.com/in/testuser"
}

result, error = detector.run(test_row)
assert not error, f"Unexpected error: {error}"
assert "claude_code_mentions" in result
assert "uses_claude_code" in result
assert isinstance(result["uses_claude_code"], bool)
```

## Related Nodes

- `yc_founder_lookup`: Find founder LinkedIn from YC company page
- `keyword_mentions`: Generic keyword mention detector (example-leads)
- `profile_enrichment`: Enrich LinkedIn profile data

## Notes

- The node scans up to `max_posts` recent posts (default: 50)
- Keywords are case-insensitive by default
- URL collection is limited to 5 URLs to avoid overly long strings
- Empty LinkedIn URL returns empty result with error message
