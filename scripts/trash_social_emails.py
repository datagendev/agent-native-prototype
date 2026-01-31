"""Trash all Social category emails from Yusheng Gmail using DataGen SDK."""

import sys
import time
import json
from datagen_sdk import DatagenClient

def log(msg):
    print(msg, flush=True)

client = DatagenClient()

total_trashed = 0
iteration = 0
BATCH = 10

while True:
    iteration += 1
    log(f"\n=== Iteration {iteration} ===")
    log(f"[{time.strftime('%H:%M:%S')}] Searching for social emails...")

    try:
        results = client.execute_tool(
            "mcp_Gmail_Yusheng_gmail_search_emails",
            {"query": "category:social", "maxResults": 50},
        )
    except Exception as exc:
        log(f"[{time.strftime('%H:%M:%S')}] Search failed: {exc}")
        break

    log(f"[{time.strftime('%H:%M:%S')}] Search complete.")

    if isinstance(results, str):
        try:
            results = json.loads(results)
        except json.JSONDecodeError:
            log(f"Unexpected response: {results[:200]}")
            break

    # Flatten nested list
    if results and isinstance(results[0], list):
        results = results[0]

    if not results or len(results) == 0:
        log("No more social emails found. Done!")
        break

    message_ids = [e["id"] for e in results if isinstance(e, dict) and "id" in e]
    log(f"[{time.strftime('%H:%M:%S')}] Found {len(message_ids)} emails to trash")

    if not message_ids:
        log("Could not extract IDs. Stopping.")
        break

    # Process in small batches
    trashed_this_round = 0
    for i in range(0, len(message_ids), BATCH):
        chunk = message_ids[i : i + BATCH]
        batch_num = i // BATCH + 1
        total_batches = (len(message_ids) + BATCH - 1) // BATCH
        log(f"  [{time.strftime('%H:%M:%S')}] Batch {batch_num}/{total_batches} ({len(chunk)} emails)...")
        try:
            client.execute_tool(
                "mcp_Gmail_Yusheng_gmail_batch_modify_emails",
                {
                    "messageIds": chunk,
                    "addLabelIds": ["TRASH"],
                    "removeLabelIds": ["CATEGORY_SOCIAL"],
                    "batchSize": BATCH,
                },
            )
            trashed_this_round += len(chunk)
            log(f"  [{time.strftime('%H:%M:%S')}] OK ({trashed_this_round}/{len(message_ids)})")
        except Exception as exc:
            log(f"  [{time.strftime('%H:%M:%S')}] FAILED: {exc}")
        time.sleep(0.5)

    total_trashed += trashed_this_round
    log(f"[{time.strftime('%H:%M:%S')}] Round done: {trashed_this_round} trashed | Running total: {total_trashed}")

    time.sleep(1)

    if iteration >= 50:
        log("Safety limit (50 iterations) reached.")
        break

log(f"\n=== COMPLETE === Trashed {total_trashed} social emails in {iteration} iterations.")
