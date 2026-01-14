# Node Templates

Examples of enrichment node classes. Nodes implement the capabilities defined in `node_types.yaml`.

## Three Concepts

| Concept | File | Purpose |
|---------|------|---------|
| **Inputs** | node_types.yaml | Data received from connections (runtime) |
| **Outputs** | node_types.yaml | Data produced for downstream nodes (runtime) |
| **Parameters** | node_types.yaml | Configuration affecting behavior (design-time) |

## Node Type Definition

Define in `node_types.yaml`:

```yaml
node_types:
  keyword_mentions:
    description: Find posts mentioning specific keywords
    file: nodes/keyword_mentions.py
    class: KeywordMentions

    # Data contract - what flows through the graph
    inputs:
      linkedin_url:
        type: string
        required: true
        description: LinkedIn profile URL to scan

    outputs:
      mentions_count:
        type: integer
        description: Number of matching posts
      mention_urls:
        type: string
        description: URLs of matching posts
      first_mention_date:
        type: string
        format: date

    # Configuration - how the node behaves
    parameters:
      keywords:
        type: array
        items: string
        required: true
        description: Keywords to search for
      output_prefix:
        type: string
        required: true
        description: Prefix for output columns
      max_posts:
        type: integer
        default: 100
        minimum: 1
        maximum: 500
```

## Python Implementation

```python
# leads/{lead_name}/graph/nodes/keyword_mentions.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from primitives.base import Graph
from primitives.linkedin_posts import fetch_linkedin_posts
from primitives.filter_by import filter_by_keywords
from primitives.aggregate import aggregate_results


class KeywordMentions(Graph):
    """Count keyword mentions in LinkedIn posts."""

    def __init__(
        self,
        keywords: list[str],
        output_prefix: str,
        max_posts: int = 100,
        date_range_days: int = 90,
    ):
        # Store parameters
        self.keywords = keywords
        self.output_prefix = output_prefix
        self.max_posts = max_posts
        self.date_range_days = date_range_days

    @property
    def input_cols(self) -> list[str]:
        """Data received from connections."""
        return ["linkedin_url"]

    @property
    def output_cols(self) -> list[str]:
        """Data produced for downstream nodes."""
        p = self.output_prefix
        return [
            f"{p}_mentions_count",
            f"{p}_mention_urls",
            f"{p}_first_mention_date",
        ]

    @property
    def parameters(self) -> dict:
        """Current parameter values (for hashing/audit)."""
        return {
            "keywords": self.keywords,
            "output_prefix": self.output_prefix,
            "max_posts": self.max_posts,
            "date_range_days": self.date_range_days,
        }

    def run(self, row: dict) -> tuple[dict, str]:
        """Execute node. Returns (result_dict, error_string)."""
        url = row.get("linkedin_url", "")
        if not url:
            return {}, "missing linkedin_url"

        # Step 1: Fetch posts
        posts, err = fetch_linkedin_posts(url, limit=self.max_posts)
        if err:
            return {}, f"posts fetch failed: {err}"

        # Step 2: Filter by keywords
        filtered, err = filter_by_keywords(posts, self.keywords)
        if err:
            return {}, f"filter failed: {err}"

        # Step 3: Aggregate
        agg, err = aggregate_results(filtered)
        if err:
            return {}, f"aggregate failed: {err}"

        p = self.output_prefix
        return {
            f"{p}_mentions_count": agg.get("count", 0),
            f"{p}_mention_urls": ",".join(agg.get("urls", [])),
            f"{p}_first_mention_date": agg.get("first_date", ""),
        }, ""
```

## Profile Enrichment Node

### Type Definition

```yaml
# node_types.yaml
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
      headline:
        type: string
      current_company:
        type: string
      location:
        type: string
      follower_count:
        type: integer

    parameters:
      output_prefix:
        type: string
        default: ""
        description: Prefix for output columns
      fields:
        type: array
        items: string
        default: ["headline", "current_company", "location", "follower_count"]
```

### Implementation

```python
# leads/{lead_name}/graph/nodes/profile_enrichment.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from primitives.base import Graph
from integrations.linkedin_profile import fetch_linkedin_profile


class ProfileEnrichment(Graph):
    """Fetch and structure LinkedIn profile data."""

    def __init__(
        self,
        output_prefix: str = "",
        fields: list[str] = None,
    ):
        self.output_prefix = output_prefix
        self.fields = fields or ["headline", "current_company", "location", "follower_count"]

    @property
    def input_cols(self) -> list[str]:
        return ["linkedin_url"]

    @property
    def output_cols(self) -> list[str]:
        prefix = f"{self.output_prefix}_" if self.output_prefix else ""
        return [f"{prefix}{f}" for f in self.fields]

    @property
    def parameters(self) -> dict:
        return {
            "output_prefix": self.output_prefix,
            "fields": self.fields,
        }

    def run(self, row: dict) -> tuple[dict, str]:
        url = row.get("linkedin_url", "")
        if not url:
            return {}, "missing linkedin_url"

        profile, err = fetch_linkedin_profile(url)
        if err:
            return {}, f"fetch failed: {err}"

        prefix = f"{self.output_prefix}_" if self.output_prefix else ""
        result = {}
        for field in self.fields:
            result[f"{prefix}{field}"] = profile.get(field, "")

        return result, ""
```

## Find Executive Node

### Type Definition

```yaml
# node_types.yaml
node_types:
  find_executive:
    description: Find executive from company domain
    file: nodes/find_executive.py
    class: FindExecutive

    inputs:
      company_domain:
        type: string
        required: true

    outputs:
      name:
        type: string
      linkedin_url:
        type: string
      title:
        type: string

    parameters:
      role:
        type: string
        required: true
        enum: ["CEO", "CTO", "CFO", "COO", "Founder", "VP Engineering"]
      output_prefix:
        type: string
        required: true
      include_founders:
        type: boolean
        default: true
```

### Implementation

```python
# leads/{lead_name}/graph/nodes/find_executive.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from primitives.base import Graph
from primitives.web_research import web_research
from primitives.extract_structured import extract_structured


class FindExecutive(Graph):
    """Find executive contact from company domain."""

    def __init__(
        self,
        role: str,
        output_prefix: str,
        include_founders: bool = True,
    ):
        self.role = role
        self.output_prefix = output_prefix
        self.include_founders = include_founders

    @property
    def input_cols(self) -> list[str]:
        return ["company_domain"]

    @property
    def output_cols(self) -> list[str]:
        p = self.output_prefix
        return [f"{p}_name", f"{p}_linkedin_url", f"{p}_title"]

    @property
    def parameters(self) -> dict:
        return {
            "role": self.role,
            "output_prefix": self.output_prefix,
            "include_founders": self.include_founders,
        }

    def run(self, row: dict) -> tuple[dict, str]:
        domain = row.get("company_domain", "")
        if not domain:
            return {}, "missing company_domain"

        # Web research
        query = f"{self.role} of {domain} LinkedIn"
        research, err = web_research(query)
        if err:
            return {}, f"research failed: {err}"

        # Extract structured data
        schema = {"name": "string", "linkedin_url": "string", "title": "string"}
        extracted, err = extract_structured(research, schema)
        if err:
            return {}, f"extraction failed: {err}"

        p = self.output_prefix
        return {
            f"{p}_name": extracted.get("name", ""),
            f"{p}_linkedin_url": extracted.get("linkedin_url", ""),
            f"{p}_title": extracted.get("title", self.role),
        }, ""
```

## Registering Nodes

Create `nodes/__init__.py` to register all node classes:

```python
# leads/{lead_name}/graph/nodes/__init__.py
from .profile_enrichment import ProfileEnrichment
from .keyword_mentions import KeywordMentions
from .find_executive import FindExecutive

# Node registry - maps type names to classes
NODES = {
    "profile_enrichment": ProfileEnrichment,
    "keyword_mentions": KeywordMentions,
    "find_executive": FindExecutive,
}

__all__ = ["NODES", "ProfileEnrichment", "KeywordMentions", "FindExecutive"]
```

## Parameter Types Reference

| Type | Python | Example |
|------|--------|---------|
| `string` | `str` | `"claude code"` |
| `integer` | `int` | `100` |
| `number` | `float` | `0.95` |
| `boolean` | `bool` | `true` |
| `array` | `list` | `["a", "b"]` |
| `object` | `dict` | `{"key": "value"}` |

## Parameter Validation

Parameters support JSON Schema-style validation:

```yaml
parameters:
  count:
    type: integer
    minimum: 1
    maximum: 100
    default: 10

  mode:
    type: string
    enum: [fast, thorough, exhaustive]
    default: fast

  api_key:
    type: string
    secret: true  # Marks sensitive values
```
