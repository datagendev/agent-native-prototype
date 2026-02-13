#!/usr/bin/env python3
"""
Build a lead list from speaker queries.

Takes a JSON config with structured search parameters, executes speaker queries
per company (avoiding LIMIT starvation), deduplicates by slug, enriches with
email/bio, and outputs a CSV.

Usage:
    python scripts/speaker_build_list.py --config ./tmp/speaker/config.json --output ./lead-list/output.csv

Config format:
{
    "searches": [
        {
            "type": "company",
            "org_slug": "revolut",
            "org_name": "Revolut",
            "title_patterns": ["%Compliance%", "%AML%", "%Fincrime%"],
            "seniority_patterns": ["%Head%", "%Director%", "%VP%", "%Chief%"],
            "current_only": true
        },
        {
            "type": "broad",
            "title_patterns": ["%Chief AI Officer%", "%Head of AI%"],
            "seniority_patterns": [],
            "country_codes": ["us", "uk"],
            "current_only": true
        }
    ],
    "enrich": true,
    "limit_per_query": 100
}
"""

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path


def run_speaker_query(sql: str) -> tuple[list[dict], str]:
    """Execute a speaker query and return parsed results."""
    try:
        result = subprocess.run(
            ["speaker", "query", sql],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return [], f"speaker query failed: {result.stderr.strip()}"

        rows = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # skip non-JSON lines (e.g., update notices)
        return rows, ""
    except subprocess.TimeoutExpired:
        return [], "speaker query timed out (30s)"
    except FileNotFoundError:
        return [], "speaker CLI not found. Install from https://speaker.dev"
    except Exception as e:
        return [], f"speaker query error: {e}"


def build_company_query(search: dict, limit: int) -> str:
    """Build SQL for a company-specific search."""
    conditions = [f"org_slug = '{search['org_slug']}'"]

    if search.get("title_patterns"):
        title_clauses = " OR ".join(
            f"title ILIKE '{p}'" for p in search["title_patterns"]
        )
        conditions.append(f"({title_clauses})")

    if search.get("seniority_patterns"):
        seniority_clauses = " OR ".join(
            f"title ILIKE '{p}'" for p in search["seniority_patterns"]
        )
        conditions.append(f"({seniority_clauses})")

    if search.get("current_only", True):
        conditions.append("end IS NULL")

    where = " AND ".join(conditions)
    return (
        f"SELECT DISTINCT first, last, title, org, loc, slug, desc "
        f"FROM people_roles WHERE {where} LIMIT {limit}"
    )


def build_broad_query(search: dict, limit: int) -> str:
    """Build SQL for a broad search (no specific company)."""
    conditions = []

    if search.get("title_patterns"):
        title_clauses = " OR ".join(
            f"title ILIKE '{p}'" for p in search["title_patterns"]
        )
        conditions.append(f"({title_clauses})")

    if search.get("seniority_patterns"):
        seniority_clauses = " OR ".join(
            f"title ILIKE '{p}'" for p in search["seniority_patterns"]
        )
        conditions.append(f"({seniority_clauses})")

    if search.get("country_codes"):
        cc_list = ", ".join(f"'{cc}'" for cc in search["country_codes"])
        conditions.append(f"cc IN ({cc_list})")

    if search.get("loc_patterns"):
        loc_clauses = " OR ".join(
            f"loc ILIKE '{p}'" for p in search["loc_patterns"]
        )
        conditions.append(f"({loc_clauses})")

    if search.get("current_only", True):
        conditions.append("end IS NULL")

    if search.get("headline_patterns"):
        # Use people table for headline search
        headline_clauses = " OR ".join(
            f"headline ILIKE '{p}'" for p in search["headline_patterns"]
        )
        conditions.append(f"({headline_clauses})")
        where = " AND ".join(conditions)
        return (
            f"SELECT first, last, headline, loc, slug "
            f"FROM people WHERE {where} LIMIT {limit}"
        )

    where = " AND ".join(conditions)
    return (
        f"SELECT DISTINCT first, last, title, org, loc, slug "
        f"FROM people_roles WHERE {where} LIMIT {limit}"
    )


def deduplicate(rows: list[dict]) -> list[dict]:
    """Deduplicate rows by slug, keeping first occurrence."""
    seen = set()
    unique = []
    for row in rows:
        slug = row.get("slug", "")
        if slug and slug not in seen:
            seen.add(slug)
            unique.append(row)
    return unique


def enrich_batch(slugs: list[str]) -> tuple[dict, str]:
    """Enrich a batch of slugs with email and bio from people table."""
    if not slugs:
        return {}, ""

    slug_list = ", ".join(f"'{s}'" for s in slugs)
    sql = f"SELECT slug, email, bio FROM people WHERE slug IN ({slug_list})"
    rows, err = run_speaker_query(sql)
    if err:
        return {}, err

    enrichment = {}
    for row in rows:
        enrichment[row["slug"]] = {
            "email": row.get("email") or "",
            "bio": row.get("bio") or "",
        }
    return enrichment, ""


def enrich_all(rows: list[dict], batch_size: int = 200) -> tuple[list[dict], str]:
    """Enrich all rows with email and bio, in batches."""
    slugs = [r["slug"] for r in rows if r.get("slug")]
    all_enrichment = {}
    errors = []

    for i in range(0, len(slugs), batch_size):
        batch = slugs[i:i + batch_size]
        enrichment, err = enrich_batch(batch)
        if err:
            errors.append(err)
            continue
        all_enrichment.update(enrichment)
        if i + batch_size < len(slugs):
            time.sleep(0.25)  # rate limit: max 5 queries/sec

    for row in rows:
        slug = row.get("slug", "")
        if slug in all_enrichment:
            row["email"] = all_enrichment[slug]["email"]
            row["bio"] = all_enrichment[slug]["bio"]
        row["linkedin_url"] = f"https://linkedin.com/in/{slug}" if slug else ""

    err_msg = "; ".join(errors) if errors else ""
    return rows, err_msg


def write_csv(rows: list[dict], output_path: str) -> tuple[str, str]:
    """Write rows to CSV."""
    if not rows:
        return "", "No rows to write"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "first", "last", "title", "org", "loc", "slug",
        "linkedin_url", "email", "bio", "desc", "headline"
    ]
    # Only include fields that exist in the data
    present_fields = set()
    for row in rows:
        present_fields.update(row.keys())
    fieldnames = [f for f in fieldnames if f in present_fields]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return output_path, ""


def main():
    parser = argparse.ArgumentParser(description="Build lead list from speaker queries")
    parser.add_argument("--config", required=True, help="Path to JSON config file")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--no-enrich", action="store_true", help="Skip enrichment step")
    parser.add_argument("--dry-run", action="store_true", help="Print queries without executing")
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    limit = config.get("limit_per_query", 100)
    searches = config.get("searches", [])

    if not searches:
        print("Error: no searches defined in config", file=sys.stderr)
        sys.exit(1)

    all_rows = []
    for i, search in enumerate(searches):
        search_type = search.get("type", "company")
        label = search.get("org_name") or search.get("org_slug") or f"broad search {i+1}"

        if search_type == "company":
            sql = build_company_query(search, limit)
        else:
            sql = build_broad_query(search, limit)

        if args.dry_run:
            print(f"[{label}] {sql}")
            continue

        print(f"Querying: {label}...", end=" ", flush=True)
        rows, err = run_speaker_query(sql)
        if err:
            print(f"FAILED: {err}")
            continue
        print(f"{len(rows)} results")
        all_rows.extend(rows)

        if i < len(searches) - 1:
            time.sleep(0.25)  # rate limit

    if args.dry_run:
        return

    # Deduplicate
    before = len(all_rows)
    all_rows = deduplicate(all_rows)
    after = len(all_rows)
    if before != after:
        print(f"Deduplicated: {before} -> {after} unique people")

    # Enrich
    if not args.no_enrich and config.get("enrich", True):
        print(f"Enriching {len(all_rows)} people...", end=" ", flush=True)
        all_rows, err = enrich_all(all_rows)
        if err:
            print(f"(partial enrichment: {err})")
        else:
            email_count = sum(1 for r in all_rows if r.get("email"))
            bio_count = sum(1 for r in all_rows if r.get("bio"))
            print(f"done ({email_count} emails, {bio_count} bios)")

    # Write CSV
    path, err = write_csv(all_rows, args.output)
    if err:
        print(f"Error writing CSV: {err}", file=sys.stderr)
        sys.exit(1)
    print(f"Saved {len(all_rows)} leads to {path}")


if __name__ == "__main__":
    main()
