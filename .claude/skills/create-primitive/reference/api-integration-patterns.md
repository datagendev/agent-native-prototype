# API Integration Patterns

When creating primitives that need external APIs, you have two main approaches:

## Option A: MCP Server Integration (Recommended)

**When to use:**
- API will be used by multiple primitives
- Want to make the tool available system-wide
- API has complex authentication (OAuth, etc.)
- API has multiple endpoints you'll use

**Benefits:**
- ✅ Reusable across all primitives and workflows
- ✅ Centralized authentication management
- ✅ Better error handling and retry logic
- ✅ Appears in DataGen tool search
- ✅ Can be shared with other users

**How to implement:**

### 1. Using /build-integrations skill
```bash
/build-integrations

# Skill will:
# 1. Research the API
# 2. Create MCP server configuration
# 3. Add to DataGen
# 4. Make tools available
```

### 2. Using addRemoteMcpServer
```bash
# If a remote MCP server exists for the API
mcp__datagen__addRemoteMcpServer(
  server_name="Hunter",
  server_url="https://mcp.hunter.io"
)
```

### 3. Manual MCP Server Creation
See: `/build-integrations` skill documentation

---

## Option B: Direct API Calls in Primitive

**When to use:**
- Simple, single-endpoint API
- One-off usage, won't be reused
- Quick prototype or proof of concept
- API is too simple to justify MCP server

**Limitations:**
- ❌ Not reusable by other primitives
- ❌ No centralized auth management
- ❌ Must handle errors/retries yourself
- ❌ Doesn't appear in tool search

**How to implement:**

### 1. Store API Key in Secrets

API keys should be stored in DataGen secrets, not in code:

```python
def _get_api_key(self) -> tuple[str, str]:
    """Get API key from DataGen secrets."""
    try:
        import os
        api_key = os.getenv("API_KEY_NAME")
        if not api_key:
            return "", "API_KEY_NAME not found"
        return api_key, ""
    except Exception as e:
        return "", f"failed to get API key: {str(e)}"
```

### 2. Use httpx for HTTP Requests

```python
import httpx

def run(self, **inputs) -> tuple[dict, str]:
    api_key, err = self._get_api_key()
    if err:
        return {}, err

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                "https://api.example.com/endpoint",
                params={"key": api_key, **inputs},
                headers={"Authorization": f"Bearer {api_key}"}
            )
            response.raise_for_status()
            data = response.json()

    except httpx.HTTPStatusError as e:
        return {}, f"API error {e.response.status_code}"
    except httpx.RequestError as e:
        return {}, f"request failed: {str(e)}"

    return {"result": data}, ""
```

### 3. Handle Common Errors

```python
# Rate limiting
if response.status_code == 429:
    return {}, "rate limit exceeded, try again later"

# Authentication
if response.status_code == 401:
    return {}, "invalid API key"

# Not found
if response.status_code == 404:
    return {}, "resource not found"
```

---

## Decision Matrix

| Consideration | MCP Server | Direct API |
|--------------|------------|-----------|
| **Reusability** | High - available everywhere | Low - one primitive only |
| **Setup Time** | 30-60 min initially | 5-10 min |
| **Maintenance** | Centralized | Per-primitive |
| **Authentication** | Managed by server | Manual in code |
| **Error Handling** | Built-in | Manual |
| **Discoverability** | Searchable in DataGen | Not searchable |
| **Best For** | Production, reuse | Prototypes, one-offs |

---

## API Research Process

When no DataGen integration exists:

### 1. Search for APIs

```bash
# Use web search to find options
"best API for [capability] 2026"
"[capability] API comparison"
"[capability] API pricing"
```

### 2. Evaluate APIs

For each API, check:
- **Documentation quality**: Clear, complete API docs?
- **Pricing**: Free tier available? Cost per request?
- **Rate limits**: Sufficient for your use case?
- **Authentication**: Simple API key or complex OAuth?
- **Reliability**: User reviews, uptime guarantees?
- **Support**: Active community, responsive support?

### 3. Present Options to User

Use `AskUserQuestion` to show:
```
API Options for [capability]:

1. [API Name] - [Description]
   Pricing: [Free tier details]
   Docs: [Link]

2. [API Name] - [Description]
   Pricing: [Free tier details]
   Docs: [Link]

Which would you like to use?
- Option 1
- Option 2
- Research more options
- Skip (create without external API)
```

### 4. Fetch API Documentation

```python
# Use WebFetch to get API docs
from tools import web_fetch

docs, err = web_fetch(
    url="https://api.example.com/docs",
    prompt="Extract: base URL, authentication method, key endpoints, example requests"
)
```

---

## Example: Hunter.io Email Finder

See `examples/direct_api_primitive.py` for complete implementation.

**Key patterns:**
1. Store API key in secrets
2. Use httpx for requests
3. Handle rate limits and errors
4. Return error-first tuple
5. Document API in frontmatter

---

## Common APIs by Category

### Email Finding
- **Hunter.io**: Email finder and verifier
- **Clearbit**: Company and contact enrichment
- **RocketReach**: Contact information

### Web Scraping
- **Firecrawl**: Intelligent web scraping (MCP available)
- **ScrapingBee**: JavaScript rendering
- **Apify**: Web scraping platform

### LinkedIn
- **Proxycurl**: LinkedIn profile scraping
- **PhantomBuster**: LinkedIn automation
- **Captain Data**: LinkedIn enrichment

### Data Enrichment
- **Clearbit**: Company enrichment
- **ZoomInfo**: B2B contact data
- **Apollo.io**: Sales intelligence

---

## References

- DataGen MCP Integration: `/build-integrations`
- Add Remote MCP: `mcp__datagen__addRemoteMcpServer`
- Direct API Example: `examples/direct_api_primitive.py`
- httpx Documentation: https://www.python-httpx.org/
