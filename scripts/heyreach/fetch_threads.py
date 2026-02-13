#!/usr/bin/env python3
"""
Fetch full message threads for conversations with replies.

Step 2 (optional) of the conversation summary pipeline.
Reads: /tmp/heyreach-summary-{date}/conversations.json
Outputs: /tmp/heyreach-summary-{date}/threads/{conversation_id}.json

Use this when conversations.json has truncated messages or missing content.
If conversations already have full messages, skip this step.

Usage:
    python fetch_threads.py
    python fetch_threads.py --input-dir /tmp/heyreach-summary-2026-02-13
    python fetch_threads.py --skip-existing
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from datagen_sdk import DatagenClient


def get_output_dir() -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d")
    return Path(f"/tmp/heyreach-summary-{date_str}")


def load_conversations(input_dir: Path) -> tuple[list[dict], str]:
    """
    Load conversations from JSON.

    Returns (conversations, error). Check error first.
    """
    path = input_dir / "conversations.json"
    if not path.exists():
        return [], f"conversations.json not found in {input_dir}"

    try:
        return json.loads(path.read_text()), ""
    except Exception as e:
        return [], f"Failed to load conversations.json: {e}"


def has_replies(conversation: dict) -> bool:
    """Check if conversation has any replies from the correspondent."""
    messages = conversation.get("messages", [])
    return any(m.get("sender") == "CORRESPONDENT" for m in messages)


def fetch_thread(
    client: DatagenClient,
    account_id: int,
    conversation_id: str,
) -> tuple[dict, str]:
    """
    Fetch full message thread via get_chatroom.

    Returns (thread, error). Check error first.
    """
    try:
        result = client.execute_tool(
            "mcp_Heyreach_get_chatroom",
            {
                "accountId": account_id,
                "conversationId": conversation_id,
            },
        )

        if isinstance(result, dict):
            return result, ""
        elif isinstance(result, list) and len(result) > 0:
            return result[0] if isinstance(result[0], dict) else {"messages": result}, ""
        else:
            return {}, f"Unexpected response format for {conversation_id}"

    except Exception as e:
        return {}, f"fetch_thread failed for {conversation_id}: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch full HeyReach message threads")
    parser.add_argument("--input-dir", type=str, help="Input directory")
    parser.add_argument(
        "--skip-existing", action="store_true", help="Skip already-fetched threads"
    )
    args = parser.parse_args()

    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)

    if not os.getenv("DATAGEN_API_KEY"):
        print("ERROR: DATAGEN_API_KEY not set", file=sys.stderr)
        return 1

    input_dir = Path(args.input_dir) if args.input_dir else get_output_dir()
    threads_dir = input_dir / "threads"
    threads_dir.mkdir(parents=True, exist_ok=True)

    conversations, err = load_conversations(input_dir)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    # Filter to conversations with replies
    reply_conversations = [c for c in conversations if has_replies(c)]
    print(f"Conversations with replies: {len(reply_conversations)}/{len(conversations)}")

    if not reply_conversations:
        print("No conversations with replies. Nothing to fetch.")
        return 0

    client = DatagenClient()
    fetched = 0
    errors = []

    for conv in reply_conversations:
        conversation_id = conv.get("conversationId", conv.get("id", ""))
        account_id = conv.get("accountId", conv.get("account_id", 0))

        if not conversation_id or not account_id:
            continue

        # Skip if exists
        thread_path = threads_dir / f"{conversation_id}.json"
        if args.skip_existing and thread_path.exists():
            print(f"  {conversation_id}: skipped (exists)")
            continue

        thread, err = fetch_thread(client, account_id, str(conversation_id))
        if err:
            print(f"  {conversation_id}: ERROR - {err}")
            errors.append({"conversation_id": conversation_id, "error": err})
            continue

        # Merge campaign metadata from original conversation
        thread["_campaign_id"] = conv.get("_campaign_id")
        thread["_campaign_name"] = conv.get("_campaign_name")

        thread_path.write_text(json.dumps(thread, indent=2, ensure_ascii=False))
        msg_count = len(thread.get("messages", []))
        print(f"  {conversation_id}: {msg_count} messages")
        fetched += 1

    print(f"\nThreads fetched: {fetched}")
    print(f"Output: {threads_dir}")

    if errors:
        errors_path = input_dir / "thread_errors.json"
        errors_path.write_text(json.dumps(errors, indent=2))
        print(f"Errors ({len(errors)}): {errors_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
