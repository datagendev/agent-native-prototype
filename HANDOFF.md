# Handoff: Class-Based Integration System + HeyReach Enrichments

**Generated**: 2026-01-10
**Branch**: master
**Status**: Ready for Review - Core implementation complete, tested successfully

## Goal

Build a scalable, agent-native enrichment system inspired by Clay's table enrichment. Enable users to enrich lead lists with LinkedIn data, HeyReach engagement metrics, and custom integrations through simple natural language prompts. System should support composable enrichments (mix LinkedIn + HeyReach in one batch) and be extensible for adding new integrations.

## Completed

- [x] Created base Integration class with shared logic (DatagenClient init, validation, error handling)
- [x] Refactored 3 existing integrations to class-based pattern (eliminated ~110 lines of boilerplate)
- [x] Built 5 new integrations:
  - `heyreach_engagement` - conversation metrics, reply tracking, meeting detection
  - `heyreach_campaigns` - campaign history and contact timeline
  - `heyreach_network` - connection degree and mutual connections
  - `linkedin_post_activity` - posting frequency (30/90 days, total posts)
  - `linkedin_claude_mentions` - finds posts mentioning "Claude Code"
- [x] Updated registry system with class-based discovery + backward compatibility
- [x] Successfully enriched test lead list (3/4 GTM influencers)
- [x] Fixed timezone comparison bug in post activity integration

## Not Yet Done

- [ ] Fix Jordan Crawford's LinkedIn URL (currently returns "Resource not found")
- [ ] Add structured extraction for web_research integration (currently returns raw text truncated to 200 chars)
- [ ] Add structured extraction for find_ceo integration (currently returns raw text truncated to 100 chars)
- [ ] Optional: Update batch_enrich.py to use class-based API (currently uses backward-compatible module-level API)
- [ ] Add caching layer for repeated lookups (avoid re-fetching same LinkedIn profile multiple times)
- [ ] Add progress persistence for resuming failed batches
- [ ] Build additional integrations: `ceo_email`, `company_linkedin`, `apollo_enrich`, `clearbit_enrich`

## Failed Approaches (Don't Repeat These)

**1. Naive datetime comparison in post activity**
- **Attempted**: Used `datetime.now()` (timezone-naive) to compare with LinkedIn API timestamps (timezone-aware)
- **Error**: `can't compare offset-naive and offset-aware datetimes`
- **Fix**: Changed to `datetime.now(timezone.utc)` for timezone-aware comparison
- **Location**: `scripts/integrations/linkedin_post_activity.py:27-28`

**2. Jordan Crawford's LinkedIn URL**
- **Issue**: `https://www.linkedin.com/in/jordan-crawford-02356a135/` returns "Resource not found"
- **Not yet resolved**: Need to verify correct LinkedIn URL or handle gracefully

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Hybrid class-based pattern** (base class + module-level wrappers) | Eliminates boilerplate (~50 lines per integration) while maintaining backward compatibility. Enables agent introspection via class properties. |
| **Error-first tuple returns** `(result, error)` | Explicit error handling without exceptions. Enables row-level isolation in batch processing. |
| **Backward compatible module-level API** | Existing orchestrator continues working unchanged. No breaking changes. |
| **ThreadPoolExecutor for parallelism** | I/O-bound operations (API calls) benefit from concurrent execution. Default 5 workers, configurable. |
| **Meeting detection via keywords** | Simple keyword matching for "book", "calendar", "meeting", etc. Could be improved with LLM-based classification. |

## Current State

**Working**:
- Base Integration class with validation and error wrapping
- 8 total integrations (3 LinkedIn, 3 HeyReach, 2 LinkedIn advanced)
- Batch enrichment orchestrator (`batch_enrich.py`)
- Composable enrichments (multiple integrations in one run)
- Test enrichment successful on 3/4 rows

**Broken**:
- Jordan Crawford's LinkedIn URL returns 404
- Web research and CEO finder return unstructured text (need LLM-based extraction)

**Uncommitted Changes**:
- All new integration code in `scripts/integrations/` (untracked)
- New test lead list `lead-list/gtm-influencers.csv` (untracked)
- Enriched output `lead-list/gtm-influencers_enriched.csv` (untracked)

## Files to Know

| File | Why It Matters |
|------|----------------|
| `scripts/integrations/base.py` | Base Integration class - all integrations inherit from this |
| `scripts/integrations/__init__.py` | Registry system - Claude reads this for discovery |
| `scripts/batch_enrich.py` | Orchestrator - runs integrations in parallel |
| `scripts/integrations/linkedin_profile.py` | Example refactored integration (74 → 43 lines) |
| `scripts/integrations/heyreach_engagement.py` | Example HeyReach integration with conversation analysis |
| `scripts/integrations/linkedin_claude_mentions.py` | Example content analysis integration |
| `lead-list/gtm-influencers.csv` | Test data (Eric, Jordan, Brady, Hannah) |

## Code Context

### Base Integration Class Signature

```python
# scripts/integrations/base.py
class Integration(ABC):
    def __init__(self):
        self.client = DatagenClient()

    @property
    @abstractmethod
    def input_cols(self) -> list[str]:
        """Columns required as input."""
        pass

    @property
    @abstractmethod
    def output_cols(self) -> list[str]:
        """Columns produced as output."""
        pass

    @abstractmethod
    def _enrich(self, row: dict) -> tuple[dict, str]:
        """
        Core enrichment logic.
        Returns: (enriched_fields, error)
        - Success: ({"col": "value"}, "")
        - Failure: ({}, "error message")
        """
        pass

    def enrich(self, row: dict) -> tuple[dict, str]:
        """Public method with validation."""
        # Validates input columns exist, calls _enrich(), wraps errors
```

### Integration Example

```python
# Pattern for new integrations
from .base import Integration

class MyIntegration(Integration):
    """Brief description for agent discovery."""

    input_cols = ["required_column"]
    output_cols = ["produced_column"]

    def _enrich(self, row: dict) -> tuple[dict, str]:
        result = self.client.execute_tool("tool_name", {"param": row["required_column"]})
        return {"produced_column": result.get("field")}, ""

# Backward compatibility
_instance = MyIntegration()
INPUT_COLS = _instance.input_cols
OUTPUT_COLS = _instance.output_cols
enrich = _instance.enrich
```

### Registry Structure

```python
# scripts/integrations/__init__.py

# Class registry (for introspection)
INTEGRATION_CLASSES = {
    "integration_name": IntegrationClass,
}

# Module-level registry (backward compatible)
INTEGRATIONS = {
    "integration_name": {
        "input": ["input_col"],
        "output": ["output_col"],
        "description": "Human-readable description"
    }
}
```

### Batch Enrichment Command

```bash
source .venv/bin/activate && python scripts/batch_enrich.py \
  --input lead-list/file.csv \
  --integrations integration1,integration2 \
  --parallel 10 \
  --output output.csv
```

### DataGen SDK Tool Execution

```python
# Pattern used in all integrations
from datagen_sdk import DatagenClient

client = DatagenClient()
result = client.execute_tool("tool_alias_name", {"param": "value"})

# Common LinkedIn tools:
# - "get_linkedin_person_data" (profile)
# - "get_linkedin_person_posts" (posts)
# - "mcp_Heyreach_get_conversations_v2" (conversations)
# - "mcp_Heyreach_get_campaigns_for_lead" (campaigns)
# - "chatgpt_webresearch" (web research)
```

## Resume Instructions

**Test the system**:

1. Activate venv and verify test data exists:
```bash
source .venv/bin/activate
cat lead-list/gtm-influencers.csv
# Expected: 4 rows (Eric, Jordan, Brady, Hannah)
```

2. Run basic enrichment (should work):
```bash
python scripts/batch_enrich.py \
  --input lead-list/gtm-influencers.csv \
  --integrations linkedin_profile \
  --parallel 4
# Expected: 3/4 rows succeed (Jordan fails with "Resource not found")
# Output: lead-list/gtm-influencers_enriched.csv
```

3. Run full enrichment with all integrations:
```bash
python scripts/batch_enrich.py \
  --input lead-list/gtm-influencers.csv \
  --integrations linkedin_profile,linkedin_post_activity,linkedin_claude_mentions \
  --parallel 4
# Expected: 3/4 rows enriched
# New columns: headline, current_company, location, follower_count, posts_last_30_days, posts_last_90_days, total_posts, last_post_date, claude_mentions_count, claude_mention_urls, first_claude_mention_date
```

4. Verify enrichment results:
```bash
cat lead-list/gtm-influencers_enriched.csv
# Expected results:
# - Eric: 48k followers, 6 posts (30d), 3 Claude mentions
# - Jordan: All empty (profile not found)
# - Brady: 7.8k followers, 4 posts (30d), 0 Claude mentions
# - Hannah: 2.7k followers, 3 posts (30d), 2 Claude mentions
```

**Add new integration**:

1. Create integration file:
```bash
touch scripts/integrations/my_integration.py
```

2. Implement integration class (see Code Context section for template)

3. Register in `__init__.py`:
```python
# Add import
from .my_integration import MyIntegration

# Add to INTEGRATION_CLASSES
"my_integration": MyIntegration,

# Add to INTEGRATIONS
"my_integration": {
    "input": MyIntegration.input_cols,
    "output": MyIntegration.output_cols,
    "description": MyIntegration.__doc__
}
```

4. Test new integration:
```bash
python scripts/batch_enrich.py \
  --input test.csv \
  --integrations my_integration \
  --parallel 2
```

**Fix Jordan's profile**:

1. Find correct LinkedIn URL (may need manual verification)
2. Update `lead-list/gtm-influencers.csv` with correct URL
3. Re-run enrichment

**Commit changes**:

```bash
git add scripts/integrations/ lead-list/
git commit -m "Add class-based integration system with HeyReach enrichments"
```

## Setup Required

**Environment**:
- Python virtual environment at `.venv/` (already created)
- `DATAGEN_API_KEY` in `../.env` file (already configured)

**Dependencies** (already installed in venv):
- `datagen-sdk`
- `python-dotenv`

**DataGen MCP Servers** (must be connected in DataGen dashboard):
- LinkedIn server (for profile/post data)
- HeyReach server (for campaign/conversation data)

**Test Data**:
- `lead-list/gtm-influencers.csv` with 4 GTM influencers

## Edge Cases & Error Handling

**LinkedIn profile not found**:
- Current: Returns error `"Resource not found"`, row skips enrichment
- Behavior: Other integrations in batch continue, row saved with empty values
- Example: Jordan Crawford in test data

**Timezone-aware vs naive datetime comparison**:
- Fixed: All datetime comparisons now use timezone-aware objects
- Location: `linkedin_post_activity.py:27-28`

**Empty post lists**:
- Handled: Returns 0 counts, empty strings for dates/URLs
- All integrations check for empty results before processing

**API rate limits**:
- Mitigation: Parallel workers configurable (default: 5, max recommended: 16)
- No retry logic yet - integration fails with error message

**Missing required columns**:
- Validation: Base class checks row has all required input columns
- Error: Returns descriptive error `"missing required columns: col1, col2"`

**DatagenClient connection issues**:
- Error: `"DATAGEN_API_KEY not set"` if env var missing
- Error: `401 unauthorized` if API key invalid or MCP server not connected

## Warnings

- **Don't use `datetime.now()` without timezone** - will cause comparison errors with API timestamps
- **Jordan Crawford's URL is broken** - expected failure, not a bug in the code
- **HeyReach integrations require both LinkedIn URL and sender ID** - `heyreach_network` needs 2 input columns
- **Meeting detection uses simple keywords** - not 100% accurate, can be improved with LLM
- **Web research returns truncated text** - needs structured extraction for production use
- **Module-level API is intentional** - provides backward compatibility, not a mistake
- **Virtual environment must be activated** - all Python commands require `source .venv/bin/activate` first

## Agent-Native Design Notes

**For future agents**: This system follows agent-native architecture principles:

1. **Parity**: Agent can discover and compose integrations like a human would browse Clay
2. **Granularity**: Each integration is atomic (one clear purpose)
3. **Composability**: Mix and match integrations via natural language
4. **Emergent Capability**: New combinations work without code changes
5. **Improvement Over Time**: Add integrations to expand capability

**Natural language usage**:
```
User: "Enrich with their job titles and posting frequency"
Agent: Maps to integrations linkedin_profile + linkedin_post_activity
      Runs batch_enrich.py with those integrations
```

**Discovery pattern**:
```python
# Agent reads registry to find what's available
from scripts.integrations import INTEGRATIONS

# Find integrations that output "headline"
matches = [name for name, meta in INTEGRATIONS.items()
           if "headline" in meta["output"]]
# Returns: ["linkedin_profile"]
```
