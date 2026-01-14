#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


ME_PROFILE_URL = "https://www.linkedin.com/in/yu-sheng-kuo-87658743"
ME_NAME = "Yusheng Kuo"


def _utc_now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    v = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(v)
    except ValueError:
        return None


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


@dataclass(frozen=True)
class SimplifiedConversation:
    linkedin_url: str
    first_name: Optional[str]
    last_name: Optional[str]
    company_name: Optional[str]
    company_url: Optional[str]
    position: Optional[str]
    messages: list[list[Any]]  # [speaker, text, createdAtUtc]
    conversation_id: Optional[str] = None

    def to_json(self) -> dict[str, Any]:
        return {
            "linkedin_url": self.linkedin_url,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "company_name": self.company_name,
            "company_url": self.company_url,
            "position": self.position,
            "messages": self.messages,
            "conversation_id": self.conversation_id,
        }


def _attach_last_message_text(
    messages: list[dict[str, Any]],
    *,
    last_message_at: Optional[str],
    last_message_text: Optional[str],
) -> list[dict[str, Any]]:
    if not last_message_text or not messages:
        return messages

    target_idx: Optional[int] = None
    if last_message_at:
        for i, m in enumerate(messages):
            if m.get("createdAt") == last_message_at:
                target_idx = i
                break

    if target_idx is None:
        # Fall back to the latest createdAt we can parse.
        parsed = [(i, _parse_dt(m.get("createdAt"))) for i, m in enumerate(messages)]
        parsed = [(i, dt) for i, dt in parsed if dt is not None]
        if parsed:
            parsed.sort(key=lambda x: x[1])
            target_idx = parsed[-1][0]

    if target_idx is None:
        return messages

    patched = []
    for i, m in enumerate(messages):
        mm = dict(m)
        if i == target_idx and mm.get("body") is None and mm.get("text") is None:
            # The raw export (without bodies) only provides conversation-level lastMessageText.
            mm["text"] = last_message_text
        patched.append(mm)
    return patched


def simplify_line(raw: dict[str, Any]) -> Optional[SimplifiedConversation]:
    correspondent = raw.get("correspondentProfile")
    if not isinstance(correspondent, dict):
        return None

    lead_profile_url = _get_str(correspondent, "profileUrl")
    if not lead_profile_url:
        return None

    if lead_profile_url.rstrip("/") == ME_PROFILE_URL.rstrip("/"):
        return None

    messages_raw = raw.get("messages")
    if not isinstance(messages_raw, list):
        messages_raw = []

    # Optional: if message bodies are missing, we can still attach lastMessageText to the latest message.
    messages_raw = [m for m in messages_raw if isinstance(m, dict)]
    messages_raw = _attach_last_message_text(
        messages_raw,
        last_message_at=raw.get("lastMessageAt") if isinstance(raw.get("lastMessageAt"), str) else None,
        last_message_text=raw.get("lastMessageText") if isinstance(raw.get("lastMessageText"), str) else None,
    )

    simplified_messages: list[list[Any]] = []
    for m in messages_raw:
        created_at = m.get("createdAt") if isinstance(m.get("createdAt"), str) else None
        if not created_at:
            continue
        sender = m.get("sender") if isinstance(m.get("sender"), str) else None
        speaker = _speaker_name(sender, correspondent)
        text = None
        if isinstance(m.get("body"), str):
            text = m.get("body")
        elif isinstance(m.get("text"), str):
            text = m.get("text")
        simplified_messages.append([speaker, text, created_at])

    # Sort by timestamp (best-effort).
    simplified_messages.sort(key=lambda x: (_parse_dt(x[2]) or datetime.min.replace(tzinfo=timezone.utc)))

    return SimplifiedConversation(
        linkedin_url=lead_profile_url,
        first_name=_get_str(correspondent, "firstName"),
        last_name=_get_str(correspondent, "lastName"),
        company_name=_get_str(correspondent, "companyName"),
        company_url=_get_str(correspondent, "companyUrl"),
        position=_get_str(correspondent, "position"),
        messages=simplified_messages,
        conversation_id=raw.get("id") if isinstance(raw.get("id"), str) else None,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Simplify HeyReach raw conversations JSONL to a compact per-lead format.")
    parser.add_argument(
        "--in",
        dest="in_path",
        default="exports/heyreach_conversations_raw_20251221T060840Z.jsonl",
        help="Input JSONL path.",
    )
    parser.add_argument("--out-dir", default="exports", help="Output directory (default: exports).")
    parser.add_argument("--stamp", default=None, help="Optional timestamp suffix (default: now UTC).")
    args = parser.parse_args()

    in_path = Path(args.in_path)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    stamp = args.stamp or _utc_now_stamp()
    out_dir = Path(args.out_dir)
    out_jsonl = out_dir / f"heyreach_conversations_simplified_{stamp}.jsonl"
    out_json = out_dir / f"heyreach_conversations_simplified_{stamp}.json"
    out_meta = out_dir / f"heyreach_conversations_simplified_meta_{stamp}.json"

    rows: list[dict[str, Any]] = []
    total = 0
    skipped = 0
    missing_text_entries = 0
    total_entries = 0

    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            raw = json.loads(line)
            if not isinstance(raw, dict):
                skipped += 1
                continue
            simplified = simplify_line(raw)
            if simplified is None:
                skipped += 1
                continue
            payload = simplified.to_json()
            rows.append(payload)

            for speaker, text, created_at in payload.get("messages", []):
                total_entries += 1
                if text is None:
                    missing_text_entries += 1

    out_dir.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    meta = {
        "input": str(in_path),
        "output_jsonl": str(out_jsonl),
        "output_json": str(out_json),
        "total_input_lines": total,
        "total_output_rows": len(rows),
        "skipped_lines": skipped,
        "message_entries_total": total_entries,
        "message_entries_missing_text": missing_text_entries,
        "note": "This source export does not include per-message bodies; only lastMessageText is attached to the latest message when possible.",
    }
    out_meta.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"[done] wrote: {out_jsonl}")
    print(f"[done] wrote: {out_json}")
    print(f"[done] wrote: {out_meta}")
    print(f"[stats] output_rows={len(rows)} message_entries={total_entries} missing_text={missing_text_entries}")


if __name__ == "__main__":
    main()

