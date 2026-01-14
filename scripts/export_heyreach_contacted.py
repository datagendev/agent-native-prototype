#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from datagen_sdk import DatagenClient


def _utc_now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    # Example: "2025-12-21T03:35:49.335Z"
    v = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(v)
    except ValueError:
        return None


def _ensure_env_loaded() -> None:
    # Avoid third-party deps inside the repo venv; read a simple KEY=VALUE .env file if present.
    env_candidates = [
        Path("../.env"),  # expected when running from repo root
        Path(__file__).resolve().parents[2] / ".env",  # expected marketing/.env
    ]
    for env_path in env_candidates:
        _load_env_file(env_path)
    if not os.getenv("DATAGEN_API_KEY"):
        raise RuntimeError(
            "DATAGEN_API_KEY not set. Load it from ../.env or export it. "
            "See agent.md for the required setup."
        )


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


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _get_all_linked_in_account_ids(client: DatagenClient) -> list[int]:
    account_ids: list[int] = []
    offset = 0
    limit = 100
    while True:
        resp = client.execute_tool(
            "mcp_Heyreach_get_all_linked_in_accounts",
            {"limit": limit, "offset": offset, "keyword": None},
        )
        payload = _as_list(resp)[0] if _as_list(resp) else {}
        items = payload.get("items", []) if isinstance(payload, dict) else []
        total_count = payload.get("totalCount") if isinstance(payload, dict) else None

        for item in _as_list(items):
            if isinstance(item, dict) and isinstance(item.get("id"), int):
                account_ids.append(item["id"])

        if not isinstance(total_count, int):
            break
        offset += limit
        if offset >= total_count:
            break
    return sorted(set(account_ids))


@dataclass(frozen=True)
class ConversationSummary:
    conversation_id: str
    linked_in_account_id: Optional[int]
    lead_profile_url: Optional[str]
    lead_linkedin_id: Optional[str]
    lead_first_name: Optional[str]
    lead_last_name: Optional[str]
    lead_headline: Optional[str]
    lead_location: Optional[str]
    lead_company_name: Optional[str]
    lead_position: Optional[str]
    has_outbound: bool
    outbound_count: int
    inbound_count: int
    first_outbound_at: Optional[str]
    last_outbound_at: Optional[str]
    last_message_at: Optional[str]
    last_message_sender: Optional[str]
    total_messages: Optional[int]

    def to_json(self) -> dict[str, Any]:
        return {
            "conversationId": self.conversation_id,
            "linkedInAccountId": self.linked_in_account_id,
            "leadProfileUrl": self.lead_profile_url,
            "leadLinkedInId": self.lead_linkedin_id,
            "leadFirstName": self.lead_first_name,
            "leadLastName": self.lead_last_name,
            "leadHeadline": self.lead_headline,
            "leadLocation": self.lead_location,
            "leadCompanyName": self.lead_company_name,
            "leadPosition": self.lead_position,
            "hasOutbound": self.has_outbound,
            "outboundCount": self.outbound_count,
            "inboundCount": self.inbound_count,
            "firstOutboundAt": self.first_outbound_at,
            "lastOutboundAt": self.last_outbound_at,
            "lastMessageAt": self.last_message_at,
            "lastMessageSender": self.last_message_sender,
            "totalMessages": self.total_messages,
        }


def _summarize_conversation(conv: dict[str, Any]) -> ConversationSummary:
    conv_id = str(conv.get("id") or "")
    linked_in_account_id = conv.get("linkedInAccountId")
    if not isinstance(linked_in_account_id, int):
        linked_in_account_id = None

    correspondent = conv.get("correspondentProfile") if isinstance(conv.get("correspondentProfile"), dict) else {}
    messages = conv.get("messages") if isinstance(conv.get("messages"), list) else []

    outbound_times: list[datetime] = []
    outbound_count = 0
    inbound_count = 0
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        sender = msg.get("sender")
        if sender == "ME":
            outbound_count += 1
            dt = _parse_dt(msg.get("createdAt"))
            if dt:
                outbound_times.append(dt)
        elif sender == "CORRESPONDENT":
            inbound_count += 1

    outbound_times_sorted = sorted(outbound_times)
    first_outbound_at = outbound_times_sorted[0].isoformat() if outbound_times_sorted else None
    last_outbound_at = outbound_times_sorted[-1].isoformat() if outbound_times_sorted else None

    def _get_str(d: dict[str, Any], key: str) -> Optional[str]:
        v = d.get(key)
        return v if isinstance(v, str) and v else None

    lead_first = _get_str(correspondent, "firstName")
    lead_last = _get_str(correspondent, "lastName")
    return ConversationSummary(
        conversation_id=conv_id,
        linked_in_account_id=linked_in_account_id,
        lead_profile_url=_get_str(correspondent, "profileUrl"),
        lead_linkedin_id=_get_str(correspondent, "linkedin_id"),
        lead_first_name=lead_first,
        lead_last_name=lead_last,
        lead_headline=_get_str(correspondent, "headline"),
        lead_location=_get_str(correspondent, "location"),
        lead_company_name=_get_str(correspondent, "companyName"),
        lead_position=_get_str(correspondent, "position"),
        has_outbound=outbound_count > 0,
        outbound_count=outbound_count,
        inbound_count=inbound_count,
        first_outbound_at=first_outbound_at,
        last_outbound_at=last_outbound_at,
        last_message_at=conv.get("lastMessageAt") if isinstance(conv.get("lastMessageAt"), str) else None,
        last_message_sender=conv.get("lastMessageSender") if isinstance(conv.get("lastMessageSender"), str) else None,
        total_messages=conv.get("totalMessages") if isinstance(conv.get("totalMessages"), int) else None,
    )


def _iter_conversations(
    client: DatagenClient,
    *,
    account_ids: list[int],
    max_conversations: Optional[int],
) -> Iterable[dict[str, Any]]:
    limit = 100
    offset = 0
    returned = 0

    while True:
        resp = client.execute_tool(
            "mcp_Heyreach_get_conversations_v2",
            {
                "linkedInAccountIds": account_ids,
                "campaignIds": [],
                "seen": None,
                "limit": limit,
                "offset": offset,
                "searchString": "",
                "leadLinkedInId": None,
                "leadProfileUrl": None,
            },
        )
        payload = _as_list(resp)[0] if _as_list(resp) else {}
        if not isinstance(payload, dict):
            break

        total_count = payload.get("totalCount") if isinstance(payload.get("totalCount"), int) else None
        items = payload.get("items") if isinstance(payload.get("items"), list) else []

        print(f"[fetch] conversations offset={offset} limit={limit} got={len(items)} total={total_count}")
        for item in items:
            if not isinstance(item, dict):
                continue
            yield item
            returned += 1
            if max_conversations is not None and returned >= max_conversations:
                return

        if total_count is None:
            break
        offset += limit
        if offset >= total_count:
            break


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export HeyReach contacted leads using messaging (conversations) as ground truth via DataGen SDK."
    )
    parser.add_argument(
        "--out-dir",
        default="exports",
        help="Output directory for exports (default: exports).",
    )
    parser.add_argument(
        "--max-conversations",
        type=int,
        default=None,
        help="Optional cap on number of conversations to process (useful for testing).",
    )
    parser.add_argument(
        "--include-message-bodies",
        action="store_true",
        help="If set, exports message bodies in the raw conversations JSONL (can be sensitive).",
    )
    args = parser.parse_args()

    _ensure_env_loaded()
    client = DatagenClient()

    account_ids = _get_all_linked_in_account_ids(client)
    if not account_ids:
        raise RuntimeError(
            "No HeyReach LinkedIn accounts found. Check HeyReach connection in DataGen. See agent.md."
        )
    print(f"[accounts] Using linkedInAccountIds={account_ids}")

    stamp = _utc_now_stamp()
    out_dir = Path(args.out_dir)
    raw_jsonl = out_dir / f"heyreach_conversations_raw_{stamp}.jsonl"
    conv_jsonl = out_dir / f"heyreach_conversations_summary_{stamp}.jsonl"
    contacted_csv = out_dir / f"heyreach_contacted_leads_{stamp}.csv"
    inbound_only_csv = out_dir / f"heyreach_inbound_only_leads_{stamp}.csv"
    meta_json = out_dir / f"heyreach_export_meta_{stamp}.json"

    conversation_summaries: list[ConversationSummary] = []
    raw_rows: list[dict[str, Any]] = []

    for conv in _iter_conversations(client, account_ids=account_ids, max_conversations=args.max_conversations):
        if args.include_message_bodies:
            raw_rows.append(conv)
        else:
            conv_no_body = dict(conv)
            # Keep message metadata for ground truth; drop bodies.
            messages = conv_no_body.get("messages")
            if isinstance(messages, list):
                sanitized: list[dict[str, Any]] = []
                for m in messages:
                    if not isinstance(m, dict):
                        continue
                    sanitized.append(
                        {
                            "createdAt": m.get("createdAt"),
                            "sender": m.get("sender"),
                            "subject": m.get("subject"),
                            "postLink": m.get("postLink"),
                            "isInMail": m.get("isInMail"),
                        }
                    )
                conv_no_body["messages"] = sanitized
            raw_rows.append(conv_no_body)

        conversation_summaries.append(_summarize_conversation(conv))

    _write_jsonl(raw_jsonl, raw_rows)
    _write_jsonl(conv_jsonl, (s.to_json() for s in conversation_summaries))

    contacted = [s for s in conversation_summaries if s.has_outbound]
    inbound_only = [s for s in conversation_summaries if not s.has_outbound]

    def lead_key(s: ConversationSummary) -> str:
        return (s.lead_profile_url or s.lead_linkedin_id or s.conversation_id) or s.conversation_id

    def lead_row(s: ConversationSummary) -> dict[str, Any]:
        return {
            "leadProfileUrl": s.lead_profile_url,
            "leadLinkedInId": s.lead_linkedin_id,
            "leadFirstName": s.lead_first_name,
            "leadLastName": s.lead_last_name,
            "leadHeadline": s.lead_headline,
            "leadLocation": s.lead_location,
            "leadCompanyName": s.lead_company_name,
            "leadPosition": s.lead_position,
            "lastOutboundAt": s.last_outbound_at,
            "firstOutboundAt": s.first_outbound_at,
            "outboundCount": s.outbound_count,
            "inboundCount": s.inbound_count,
            "lastMessageAt": s.last_message_at,
            "lastMessageSender": s.last_message_sender,
            "totalMessages": s.total_messages,
            "linkedInAccountId": s.linked_in_account_id,
            "conversationId": s.conversation_id,
        }

    def dedupe_leads(summaries: list[ConversationSummary]) -> list[dict[str, Any]]:
        best: dict[str, ConversationSummary] = {}
        for s in summaries:
            k = lead_key(s)
            existing = best.get(k)
            if existing is None:
                best[k] = s
                continue
            # Keep the one with the most recent outbound (or last message if no outbound).
            a = _parse_dt(existing.last_outbound_at) or _parse_dt(existing.last_message_at) or datetime.min.replace(
                tzinfo=timezone.utc
            )
            b = _parse_dt(s.last_outbound_at) or _parse_dt(s.last_message_at) or datetime.min.replace(
                tzinfo=timezone.utc
            )
            if b > a:
                best[k] = s
        rows = [lead_row(s) for s in best.values()]
        rows.sort(key=lambda r: (r.get("lastOutboundAt") or r.get("lastMessageAt") or ""), reverse=True)
        return rows

    contacted_rows = dedupe_leads(contacted)
    inbound_rows = dedupe_leads(inbound_only)

    lead_fields = [
        "leadProfileUrl",
        "leadLinkedInId",
        "leadFirstName",
        "leadLastName",
        "leadHeadline",
        "leadLocation",
        "leadCompanyName",
        "leadPosition",
        "lastOutboundAt",
        "firstOutboundAt",
        "outboundCount",
        "inboundCount",
        "lastMessageAt",
        "lastMessageSender",
        "totalMessages",
        "linkedInAccountId",
        "conversationId",
    ]
    _write_csv(contacted_csv, lead_fields, contacted_rows)
    _write_csv(inbound_only_csv, lead_fields, inbound_rows)

    meta = {
        "generatedAtUtc": stamp,
        "linkedInAccountIds": account_ids,
        "conversations": {
            "totalSummaries": len(conversation_summaries),
            "contactedConversations": len(contacted),
            "inboundOnlyConversations": len(inbound_only),
            "uniqueContactedLeads": len(contacted_rows),
            "uniqueInboundOnlyLeads": len(inbound_rows),
        },
        "files": {
            "rawConversationsJsonl": str(raw_jsonl),
            "conversationSummariesJsonl": str(conv_jsonl),
            "contactedLeadsCsv": str(contacted_csv),
            "inboundOnlyLeadsCsv": str(inbound_only_csv),
        },
        "notes": {
            "groundTruth": "A lead is considered contacted if any message in the conversation has sender == 'ME'.",
            "privacy": "By default message bodies are NOT exported; use --include-message-bodies to include them.",
        },
    }
    meta_json.parent.mkdir(parents=True, exist_ok=True)
    meta_json.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print("[done] Export written:")
    print(f"  - {meta_json}")
    print(f"  - {contacted_csv}")
    print(f"  - {inbound_only_csv}")
    print(f"  - {conv_jsonl}")
    print(f"  - {raw_jsonl}")


if __name__ == "__main__":
    main()
