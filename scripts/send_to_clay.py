#!/usr/bin/env python3
"""
Send leads to Clay table via webhook.

Usage:
    python send_to_clay.py --lead-list gtm-engineers-series-a --webhook-url https://api.clay.com/webhooks/...
    python send_to_clay.py --lead-list gtm-engineers-series-a --webhook-url https://api.clay.com/webhooks/... --dry-run
"""

import sys
import json
import time
import argparse
import sqlite3
import csv
import httpx
from pathlib import Path
from typing import Iterator, Optional, Tuple

def load_leads_from_csv(csv_path: Path) -> Tuple[list[dict], str]:
    """Load leads from CSV file."""
    if not csv_path.exists():
        return [], f"CSV file not found: {csv_path}"

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows, ""
    except Exception as e:
        return [], f"Failed to read CSV: {e}"


def load_leads_from_db(db_path: Path) -> Tuple[list[dict], str]:
    """Load leads from SQLite database (completed rows only)."""
    if not db_path.exists():
        return [], f"Database file not found: {db_path}"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get completed rows only
        cursor.execute("SELECT * FROM leads WHERE _status = 'completed' ORDER BY _id")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return rows, ""
    except Exception as e:
        return [], f"Failed to read database: {e}"


def load_leads(lead_list_name: str) -> Tuple[list[dict], str]:
    """Load leads from either CSV or SQLite database."""
    lead_path = Path(__file__).parent.parent / "leads" / lead_list_name

    if not lead_path.exists():
        return [], f"Lead list not found: {lead_list_name}"

    # Try SQLite first
    db_path = lead_path / "table.db"
    if db_path.exists():
        return load_leads_from_db(db_path)

    # Fallback to CSV
    csv_path = lead_path / "table.csv"
    if csv_path.exists():
        return load_leads_from_csv(csv_path)

    return [], f"No table.db or table.csv found in {lead_path}"


def sanitize_row(row: dict) -> dict:
    """Convert row to JSON-serializable format."""
    result = {}
    for key, value in row.items():
        if value is None:
            result[key] = None
        elif isinstance(value, (str, int, float, bool)):
            result[key] = value
        else:
            # Convert to string for non-JSON types
            result[key] = str(value)
    return result


def send_batch(webhook_url: str, rows: list[dict], batch_num: int, max_retries: int = 3) -> Tuple[int, list[str]]:
    """
    Send a batch of rows to Clay webhook.

    Returns: (successful_count, error_messages)
    """
    successful = 0
    errors = []

    for attempt in range(max_retries):
        try:
            # Prepare payload: Clay expects array of objects
            payload = [sanitize_row(row) for row in rows]

            # Send to webhook
            response = httpx.post(
                webhook_url,
                json=payload,
                timeout=30.0,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in (200, 201, 202):
                successful = len(rows)
                return successful, []
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                errors.append(error_msg)

                # Retry on server errors (5xx)
                if response.status_code >= 500 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                else:
                    break

        except httpx.TimeoutException:
            error_msg = "Request timeout"
            errors.append(error_msg)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            break

        except Exception as e:
            error_msg = f"Request failed: {str(e)[:100]}"
            errors.append(error_msg)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            break

    return successful, errors


def validate_webhook_url(webhook_url: str) -> Tuple[bool, str]:
    """Validate webhook URL format."""
    if not webhook_url:
        return False, "Webhook URL is required"

    if not webhook_url.startswith("https://"):
        return False, "Webhook URL must start with https://"

    if "clay.com" not in webhook_url:
        return False, "Webhook URL must be from Clay (clay.com)"

    return True, ""


def main():
    parser = argparse.ArgumentParser(description="Send leads to Clay table via webhook")
    parser.add_argument("--lead-list", required=True, help="Lead list name (e.g., gtm-engineers-series-a)")
    parser.add_argument("--webhook-url", required=True, help="Clay table webhook URL")
    parser.add_argument("--batch-size", type=int, default=10, help="Rows per batch (default: 10)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--max-retries", type=int, default=3, help="Retry failed batches (default: 3)")

    args = parser.parse_args()

    # Validate webhook URL
    valid, err = validate_webhook_url(args.webhook_url)
    if not valid:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    # Load leads
    print(f"\nSend to Clay: {args.lead_list}")
    print(f"Webhook: {args.webhook_url[:50]}...")
    print(f"Mode: {'dry-run (preview only)' if args.dry_run else 'live'}\n")
    print("Loading leads...")

    leads, err = load_leads(args.lead_list)
    if err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    if not leads:
        print("No leads found.", file=sys.stderr)
        return 1

    print(f"Found {len(leads)} leads\n")

    # Preview
    if len(leads) > 0:
        print("Preview (first 3 rows):")
        for i, row in enumerate(leads[:3], 1):
            # Show first available field as identifier
            identifier = next(iter(row.values()), "")
            print(f"  {i}. {identifier}")
        print()

    if args.dry_run:
        print(f"Ready to send {len(leads)} rows in batches of {args.batch_size}.")
        print("\nUse --dry-run=false to actually send data, or remove --dry-run flag.")
        return 0

    # Send in batches
    print(f"Sending in batches of {args.batch_size}...\n")

    total_sent = 0
    total_failed = 0
    batch_num = 1

    for i in range(0, len(leads), args.batch_size):
        batch = leads[i:i + args.batch_size]
        start_row = i + 1
        end_row = min(i + args.batch_size, len(leads))

        sent, errors = send_batch(args.webhook_url, batch, batch_num, args.max_retries)

        if errors:
            status = f"✗ FAILED: {errors[0]}"
            total_failed += len(batch) - sent
        else:
            status = "✓ SUCCESS"

        print(f"Batch {batch_num} (rows {start_row}-{end_row}): {status}")

        total_sent += sent
        batch_num += 1

        # Small delay between batches
        if i + args.batch_size < len(leads):
            time.sleep(0.5)

    # Summary
    print(f"\nSummary:")
    print(f"  Total rows: {len(leads)}")
    print(f"  Sent: {total_sent} ✓")
    print(f"  Failed: {total_failed} ✗")
    success_rate = (total_sent / len(leads) * 100) if leads else 0
    print(f"  Success rate: {success_rate:.1f}%")

    if total_sent == len(leads):
        print(f"\nAll leads sent to Clay successfully!")
        return 0
    else:
        print(f"\n{total_failed} leads failed to send.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
