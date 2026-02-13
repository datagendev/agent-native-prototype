---
name: speaker-prospecting
description: "Build B2B lead lists from natural language intent using the speaker CLI (756M+ person database). Use when the user wants to find people by role, company, industry, geography, or any combination — e.g., 'find compliance leaders at European fintechs', 'AI engineers at FAANG', 'founders who left Stripe'. Outputs deduplicated, enriched CSV files. Triggers: lead list, find people, prospect list, speaker, build list, who works at, people search."
---

# Speaker Prospecting

Build lead lists from natural language intent using `speaker query` (756M+ B2B profiles, SQL interface).

## Workflow

```
User intent (natural language)
  -> Parse into: companies, titles, seniority, geography
  -> Resolve org_slugs (if companies specified)
  -> Explore title distributions at sample companies
  -> Build config.json
  -> Run speaker_build_list.py
  -> Output: deduplicated, enriched CSV
```

### Phase 1: Parse Intent

Extract from the user's request:

| Dimension | Example |
|-----------|---------|
| Target companies | "Stripe, Revolut, Wise" |
| Industry/segment | "fintechs", "AI startups" |
| Role keywords | "compliance", "engineering", "sales" |
| Seniority | "leaders", "VP+", "C-level" |
| Geography | "Europe", "US", "UK and Germany" |
| Special filters | "who left X", "alumni of Y", "current only" |

If the user gives only a vague intent (e.g., "AI leaders"), ask one clarifying question covering the most ambiguous dimension. Don't over-ask.

### Phase 2: Resolve org_slugs

**Critical**: Company names are ambiguous. Always resolve to `org_slug` first.

```bash
speaker query "SELECT org, org_slug, count() as c FROM people_roles WHERE org = 'Mercury' AND end IS NULL GROUP BY org, org_slug ORDER BY c DESC LIMIT 20"
```

Slugs are not guessable: Wise = `wiseaccount`, Block = `joinblock`, Monzo = `monzo-bank`.

If the user gives an industry instead of company names (e.g., "top fintechs"), use your knowledge to suggest 10-20 companies, then resolve each slug.

When `org_slug` is empty, fall back to `WHERE org = 'Name'`. For very new startups, try `headline ILIKE '%Name%'` on the `people` table.

### Phase 3: Explore Titles

Before building filters, explore what titles actually exist at 2-3 target companies:

```bash
speaker query "SELECT title, count() as c FROM people_roles WHERE org_slug = 'revolut' AND end IS NULL GROUP BY title ORDER BY c DESC LIMIT 30"
```

**Why**: Title conventions vary wildly. Revolut says "Fincrime", not "Financial Crime". PayPal uses "SVP", not "Head of".

Use the `desc` field to understand role scope when available:
```bash
speaker query "SELECT title, desc FROM people_roles WHERE org_slug = 'stripe' AND title ILIKE '%Compliance%' AND end IS NULL LIMIT 10"
```

### Phase 4: Build Config and Execute

Create a config JSON at `./tmp/speaker-{date}/config.json`:

```json
{
    "searches": [
        {
            "type": "company",
            "org_slug": "revolut",
            "org_name": "Revolut",
            "title_patterns": ["%Compliance%", "%AML%", "%Fincrime%"],
            "seniority_patterns": ["%Head%", "%Director%", "%VP%", "%Chief%"],
            "current_only": true
        }
    ],
    "enrich": true,
    "limit_per_query": 100
}
```

Run:
```bash
source .venv/bin/activate && python .claude/skills/speaker-prospecting/scripts/speaker_build_list.py \
  --config ./tmp/speaker-{date}/config.json \
  --output ./lead-list/{name}_{date}.csv
```

Use `--dry-run` to preview queries before executing.

### Phase 5: Review and Iterate

After the CSV is generated, briefly summarize:
- Total leads found
- Breakdown by company (top 5)
- Email/bio coverage
- Any companies that returned 0 results

If results are thin, suggest broadening title patterns or adding companies.

## Query Pitfalls

Encode these in every query:

1. **Always DISTINCT** — `people_roles` has one row per person-role
2. **Always include slug** — unique person ID, needed for dedup and LinkedIn URLs
3. **Query per company** — never put >5 org_slugs in a single IN clause (LIMIT starvation)
4. **Short keywords are landmines** — `%AI%` matches Aircraft, `%CTO%` matches Director. Spell out: `%Artificial Intelligence%`, `%Chief Technology Officer%`
5. **ILIKE vs LIKE** — use LIKE for exact case-sensitive match on short terms
6. **Seniority false positives** — `%Global%` matches "Global AML Analyst", `%Executive%` matches "Executive Assistant". Be specific: `%Head of%`, `%Chief%Officer%`, `%Director%`, `%VP %`
7. **Current roles** — `end IS NULL` for current employees

## Seniority Mapping

When user says... use these patterns:

| Intent | Patterns |
|--------|----------|
| C-level | `%Chief%Officer%`, `%CEO%`, `%CTO%`, `%CFO%`, `%COO%` |
| VP+ | `%VP %`, `%Vice President%`, `%SVP%`, `%EVP%` |
| Director+ | `%Director%`, `%Head of%`, `%Global Head%` |
| Leaders (broad) | All of the above + `%General Manager%`, `%General Counsel%` |
| Managers | `%Manager%`, `%Lead %`, `%Team Lead%` |
| ICs | No seniority filter, just title keywords |

For non-English markets, add locale variants: German `Geschaeftsfuehrer` for CEO, French `Directeur` for Director.

## Broad Search (No Target Companies)

When the user doesn't name specific companies:

1. Start narrow with the most specific title patterns
2. Add `cc` country filter to avoid scanning 756M rows
3. Review first batch, then broaden progressively

```json
{
    "searches": [
        {
            "type": "broad",
            "title_patterns": ["%Chief AI Officer%", "%Head of AI%"],
            "seniority_patterns": [],
            "country_codes": ["us", "uk"],
            "current_only": true
        }
    ]
}
```

## Special Query Patterns

### Alumni (people who left a company)
```bash
speaker query "SELECT DISTINCT first, last, title, org, headline FROM people_roles WHERE slug IN (SELECT DISTINCT slug FROM people_roles WHERE org_slug = 'monzo-bank' AND end IS NOT NULL) AND end IS NULL AND org_slug != 'monzo-bank' LIMIT 100"
```

### Headline search (aspirational titles, freelancers)
```json
{
    "type": "broad",
    "headline_patterns": ["%Artificial Intelligence%", "%Machine Learning%"],
    "country_codes": ["us"],
    "current_only": true
}
```

### Education filter
```bash
speaker query "SELECT first, last, headline, loc FROM people WHERE arrayExists(e -> e.school ILIKE '%Stanford%', edu) AND cc = 'us' LIMIT 100"
```

## Output

CSV saved to `./lead-list/{name}_{date}.csv` with columns:
`first, last, title, org, loc, slug, linkedin_url, email, bio, desc`

LinkedIn profile URL: `https://linkedin.com/in/{slug}`

Email coverage is near zero for senior roles at large companies. Use `slug` for LinkedIn-based outreach.

## Reference

Full speaker documentation: `~/.speaker/SPEAKER.md`
- Schema details, country codes, field coverage, query limits
- Max 1,000 rows per query, 5,000 queries/day
