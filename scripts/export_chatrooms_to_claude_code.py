#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from datagen_sdk import DatagenClient


ME_PROFILE_URL = "https://www.linkedin.com/in/yu-sheng-kuo-87658743"
ME_NAME = "Yusheng Kuo"


def _utc_now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_env_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        return
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and ((value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _ensure_env_loaded() -> None:
    _load_env_file(Path("../.env"))
    if not os.getenv("DATAGEN_API_KEY"):
        raise RuntimeError("DATAGEN_API_KEY not set. Load it from ../.env or export it.")


def _get_str(d: dict[str, Any], key: str) -> Optional[str]:
    v = d.get(key)
    return v if isinstance(v, str) and v else None


def _speaker_name(message_sender: Optional[str], correspondent: dict[str, Any]) -> str:
    if message_sender == "ME":
        return ME_NAME
    first = _get_str(correspondent, "firstName")
    if first:
        return first
    last = _get_str(correspondent, "lastName")
    if last:
        return last
    return "CORRESPONDENT"


def _slugify(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t[:80] if t else "unknown"


def _profile_identifier(profile_url: str) -> str:
    u = profile_url.rstrip("/")
    seg = u.split("/")[-1]
    seg = seg or hashlib.sha1(profile_url.encode("utf-8")).hexdigest()[:12]
    seg = re.sub(r"[^A-Za-z0-9_-]+", "", seg)
    return seg[:40] if seg else hashlib.sha1(profile_url.encode("utf-8")).hexdigest()[:12]


@dataclass(frozen=True)
class LeadThread:
    linkedin_url: str
    first_name: Optional[str]
    last_name: Optional[str]
    company_name: Optional[str]
    company_url: Optional[str]
    position: Optional[str]
    messages: list[list[Any]]  # [speaker, message, utc_time]
    conversation_id: str
    account_id: int

    def to_json(self) -> dict[str, Any]:
        return {
            "linkedin_url": self.linkedin_url,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "company_name": self.company_name,
            "company_url": self.company_url,
            "position": self.position,
            "conversation_id": self.conversation_id,
            "account_id": self.account_id,
            "messages": self.messages,
        }


def _simplify_chatroom(chat: dict[str, Any], *, account_id: int) -> Optional[LeadThread]:
    correspondent = chat.get("correspondentProfile")
    if not isinstance(correspondent, dict):
        return None

    lead_profile_url = _get_str(correspondent, "profileUrl")
    if not lead_profile_url:
        return None

    if lead_profile_url.rstrip("/") == ME_PROFILE_URL.rstrip("/"):
        return None

    conversation_id = chat.get("id")
    if not isinstance(conversation_id, str) or not conversation_id:
        return None

    messages_raw = chat.get("messages")
    messages_raw = messages_raw if isinstance(messages_raw, list) else []

    simplified_messages: list[list[Any]] = []
    for m in messages_raw:
        if not isinstance(m, dict):
            continue
        created_at = m.get("createdAt") if isinstance(m.get("createdAt"), str) else None
        if not created_at:
            continue
        sender = m.get("sender") if isinstance(m.get("sender"), str) else None
        speaker = _speaker_name(sender, correspondent)

        body: Optional[str] = None
        if isinstance(m.get("body"), str):
            body = m.get("body")
        elif isinstance(m.get("subject"), str) and m.get("subject"):
            body = f"[subject] {m.get('subject')}"

        simplified_messages.append([speaker, body, created_at])

    simplified_messages.sort(key=lambda x: x[2])

    return LeadThread(
        linkedin_url=lead_profile_url,
        first_name=_get_str(correspondent, "firstName"),
        last_name=_get_str(correspondent, "lastName"),
        company_name=_get_str(correspondent, "companyName"),
        company_url=_get_str(correspondent, "companyUrl"),
        position=_get_str(correspondent, "position"),
        messages=simplified_messages,
        conversation_id=conversation_id,
        account_id=account_id,
    )


def _load_conversation_ids(path: Path) -> list[str]:
    ids: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                continue
            conv_id = row.get("conversation_id")
            if isinstance(conv_id, str) and conv_id:
                ids.append(conv_id)
    # preserve order, dedupe
    seen = set()
    out: list[str] = []
    for cid in ids:
        if cid in seen:
            continue
        seen.add(cid)
        out.append(cid)
    return out


def _get_default_account_id(client: DatagenClient) -> int:
    resp = client.execute_tool("mcp_Heyreach_get_all_linked_in_accounts", {"limit": 100, "offset": 0, "keyword": None})
    payload = resp[0] if isinstance(resp, list) and resp else {}
    items = payload.get("items") if isinstance(payload, dict) and isinstance(payload.get("items"), list) else []
    for item in items:
        if isinstance(item, dict) and isinstance(item.get("id"), int):
            return item["id"]
    raise RuntimeError("No HeyReach LinkedIn account found.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch full HeyReach chatrooms for conversation ids and write per-person simplified JSON files under claude-code/."
    )
    parser.add_argument(
        "--in",
        dest="in_path",
        default="exports/heyreach_conversations_simplified_20251221T060840Z.jsonl",
        help="Input simplified JSONL containing conversation_id per line.",
    )
    parser.add_argument("--out-dir", default="claude-code", help="Output directory (default: claude-code).")
    parser.add_argument("--account-id", type=int, default=None, help="HeyReach LinkedIn sender account id (default: auto).")
    parser.add_argument("--sleep-ms", type=int, default=50, help="Sleep between requests (default: 50ms).")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N conversations (default: 0).")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit number of conversations to fetch after offset.")
    parser.add_argument("--resume", action="store_true", help="Skip conversations whose output file already exists.")
    args = parser.parse_args()

    _ensure_env_loaded()
    client = DatagenClient()

    in_path = Path(args.in_path)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    conv_ids = _load_conversation_ids(in_path)
    if args.offset:
        conv_ids = conv_ids[args.offset :]
    if args.limit is not None:
        conv_ids = conv_ids[: args.limit]

    account_id = args.account_id if args.account_id is not None else _get_default_account_id(client)
    print(f"[heyreach] using accountId={account_id} conversations={len(conv_ids)}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = _utc_now_stamp()
    index: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for i, conv_id in enumerate(conv_ids, 1):
        try:
            conv_hash = hashlib.sha1(conv_id.encode("utf-8")).hexdigest()[:10]
            resp = client.execute_tool("mcp_Heyreach_get_chatroom", {"accountId": account_id, "conversationId": conv_id})
            chat = resp[0] if isinstance(resp, list) and resp else resp
            if not isinstance(chat, dict):
                raise RuntimeError(f"Unexpected response type: {type(chat)}")

            simplified = _simplify_chatroom(chat, account_id=account_id)
            if simplified is None:
                failures.append({"conversation_id": conv_id, "error": "could_not_simplify"})
                continue

            name_part = " ".join([x for x in [simplified.first_name, simplified.last_name] if x]).strip()
            name_slug = _slugify(name_part) if name_part else "unknown"
            ident = _profile_identifier(simplified.linkedin_url)
            file_name = f"{name_slug}__{ident}__{conv_hash}.json"
            file_path = out_dir / file_name
            if args.resume and file_path.exists():
                print(f"[{i}/{len(conv_ids)}] skip existing {file_name}")
                continue
            file_path.write_text(json.dumps(simplified.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")

            index.append(
                {
                    "file": str(file_path),
                    "linkedin_url": simplified.linkedin_url,
                    "first_name": simplified.first_name,
                    "last_name": simplified.last_name,
                    "company_name": simplified.company_name,
                    "company_url": simplified.company_url,
                    "position": simplified.position,
                    "messages_count": len(simplified.messages),
                    "conversation_id": simplified.conversation_id,
                }
            )
            print(f"[{i}/{len(conv_ids)}] wrote {file_name} messages={len(simplified.messages)}")
        except Exception as e:
            failures.append({"conversation_id": conv_id, "error": str(e)[:400]})
            print(f"[{i}/{len(conv_ids)}] FAILED conversation_id={conv_id}: {type(e).__name__}: {str(e)[:200]}")

        if args.sleep_ms > 0:
            time.sleep(args.sleep_ms / 1000.0)

    index_path = out_dir / f"index_{stamp}.json"
    failures_path = out_dir / f"failures_{stamp}.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    failures_path.write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[done] index: {index_path}")
    print(f"[done] failures: {failures_path} ({len(failures)} failures)")


if __name__ == "__main__":
    main()
