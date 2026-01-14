#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from datagen_sdk import DatagenClient


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
    # Repo convention from CLAUDE.md: API key typically lives in ../.env
    _load_env_file(Path("../.env"))
    if not os.getenv("DATAGEN_API_KEY"):
        raise RuntimeError(
            "DATAGEN_API_KEY not set. Load it from ../.env or export it. See agent.md for setup."
        )


def _sql_quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def _sql_text(value: Optional[str]) -> str:
    if value is None:
        return "NULL"
    return _sql_quote(value)


def _sql_int(value: Optional[int]) -> str:
    if value is None:
        return "NULL"
    return str(int(value))


def _sql_bool(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def _sql_timestamptz(value: Optional[str]) -> str:
    if not value:
        return "NULL"
    # Accept HeyReach style "...Z"; store as timestamptz.
    return f"{_sql_quote(value)}::timestamptz"


def _sql_jsonb(value: Any) -> str:
    dumped = json.dumps(value, ensure_ascii=False)
    return f"{_sql_quote(dumped)}::jsonb"


@dataclass(frozen=True)
class Conversation:
    conversation_id: str
    linked_in_account_id: Optional[int]
    last_message_at: Optional[str]
    last_message_sender: Optional[str]
    total_messages: Optional[int]
    correspondent_profile: dict[str, Any]
    messages: list[dict[str, Any]]
    raw: dict[str, Any]

    @property
    def lead_profile_url(self) -> Optional[str]:
        v = self.correspondent_profile.get("profileUrl")
        return v if isinstance(v, str) and v else None

    @property
    def lead_linkedin_id(self) -> Optional[str]:
        v = self.correspondent_profile.get("linkedin_id")
        return v if isinstance(v, str) and v else None

    def counts(self) -> tuple[int, int]:
        outbound = 0
        inbound = 0
        for m in self.messages:
            sender = m.get("sender")
            if sender == "ME":
                outbound += 1
            elif sender == "CORRESPONDENT":
                inbound += 1
        return outbound, inbound

    def has_outbound(self) -> bool:
        outbound, _ = self.counts()
        return outbound > 0


def _get_all_linked_in_account_ids(client: DatagenClient) -> list[int]:
    offset = 0
    limit = 100
    ids: list[int] = []
    while True:
        resp = client.execute_tool(
            "mcp_Heyreach_get_all_linked_in_accounts",
            {"limit": limit, "offset": offset, "keyword": None},
        )
        payload = resp[0] if isinstance(resp, list) and resp else {}
        if not isinstance(payload, dict):
            break
        total_count = payload.get("totalCount") if isinstance(payload.get("totalCount"), int) else None
        items = payload.get("items") if isinstance(payload.get("items"), list) else []
        for item in items:
            if isinstance(item, dict) and isinstance(item.get("id"), int):
                ids.append(item["id"])
        if total_count is None:
            break
        offset += limit
        if offset >= total_count:
            break
    return sorted(set(ids))


def _fetch_all_conversations(
    client: DatagenClient,
    *,
    linked_in_account_ids: list[int],
    max_conversations: Optional[int],
) -> list[Conversation]:
    offset = 0
    limit = 100
    conversations: list[Conversation] = []

    while True:
        resp = client.execute_tool(
            "mcp_Heyreach_get_conversations_v2",
            {
                "linkedInAccountIds": linked_in_account_ids,
                "campaignIds": [],
                "seen": None,
                "limit": limit,
                "offset": offset,
                "searchString": "",
                "leadLinkedInId": None,
                "leadProfileUrl": None,
            },
        )
        payload = resp[0] if isinstance(resp, list) and resp else {}
        if not isinstance(payload, dict):
            break
        total_count = payload.get("totalCount") if isinstance(payload.get("totalCount"), int) else None
        items = payload.get("items") if isinstance(payload.get("items"), list) else []
        print(f"[fetch] conversations offset={offset} limit={limit} got={len(items)} total={total_count}")

        for item in items:
            if not isinstance(item, dict):
                continue
            conv_id = str(item.get("id") or "")
            if not conv_id:
                continue
            linked_in_account_id = item.get("linkedInAccountId")
            if not isinstance(linked_in_account_id, int):
                linked_in_account_id = None
            correspondent = item.get("correspondentProfile") if isinstance(item.get("correspondentProfile"), dict) else {}
            messages = item.get("messages") if isinstance(item.get("messages"), list) else []
            last_message_at = item.get("lastMessageAt") if isinstance(item.get("lastMessageAt"), str) else None
            last_message_sender = item.get("lastMessageSender") if isinstance(item.get("lastMessageSender"), str) else None
            total_messages = item.get("totalMessages") if isinstance(item.get("totalMessages"), int) else None

            conversations.append(
                Conversation(
                    conversation_id=conv_id,
                    linked_in_account_id=linked_in_account_id,
                    last_message_at=last_message_at,
                    last_message_sender=last_message_sender,
                    total_messages=total_messages,
                    correspondent_profile=correspondent,
                    messages=[m for m in messages if isinstance(m, dict)],
                    raw=item,
                )
            )
            if max_conversations is not None and len(conversations) >= max_conversations:
                return conversations

        if total_count is None:
            break
        offset += limit
        if offset >= total_count:
            break

    return conversations


def _ensure_neon_schema(client: DatagenClient, *, project_id: str, branch_id: str, database_name: str) -> None:
    statements = [
        """
CREATE TABLE IF NOT EXISTS public.heyreach_conversations (
  conversation_id text PRIMARY KEY,
  linked_in_account_id integer,
  lead_profile_url text,
  lead_linkedin_id text,
  lead_first_name text,
  lead_last_name text,
  lead_headline text,
  lead_location text,
  lead_company_name text,
  lead_position text,
  has_outbound boolean NOT NULL DEFAULT false,
  outbound_count integer NOT NULL DEFAULT 0,
  inbound_count integer NOT NULL DEFAULT 0,
  last_message_at timestamptz,
  last_message_sender text,
  total_messages integer,
  messages jsonb NOT NULL DEFAULT '[]'::jsonb,
  raw jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
""".strip(),
        "CREATE INDEX IF NOT EXISTS idx_heyreach_conversations_lead_profile_url ON public.heyreach_conversations (lead_profile_url);",
        "CREATE INDEX IF NOT EXISTS idx_heyreach_conversations_last_message_at ON public.heyreach_conversations (last_message_at DESC);",
    ]
    for sql in statements:
        client.execute_tool(
            "mcp_Neon_run_sql",
            {"params": {"projectId": project_id, "branchId": branch_id, "databaseName": database_name, "sql": sql}},
        )


def _upsert_conversation_sql(conv: Conversation) -> str:
    outbound_count, inbound_count = conv.counts()
    corr = conv.correspondent_profile

    def _get_str(key: str) -> Optional[str]:
        v = corr.get(key)
        return v if isinstance(v, str) and v else None

    sql = f"""
INSERT INTO public.heyreach_conversations (
  conversation_id,
  linked_in_account_id,
  lead_profile_url,
  lead_linkedin_id,
  lead_first_name,
  lead_last_name,
  lead_headline,
  lead_location,
  lead_company_name,
  lead_position,
  has_outbound,
  outbound_count,
  inbound_count,
  last_message_at,
  last_message_sender,
  total_messages,
  messages,
  raw,
  updated_at
) VALUES (
  {_sql_text(conv.conversation_id)},
  {_sql_int(conv.linked_in_account_id)},
  {_sql_text(conv.lead_profile_url)},
  {_sql_text(conv.lead_linkedin_id)},
  {_sql_text(_get_str('firstName'))},
  {_sql_text(_get_str('lastName'))},
  {_sql_text(_get_str('headline'))},
  {_sql_text(_get_str('location'))},
  {_sql_text(_get_str('companyName'))},
  {_sql_text(_get_str('position'))},
  {_sql_bool(outbound_count > 0)},
  {_sql_int(outbound_count)},
  {_sql_int(inbound_count)},
  {_sql_timestamptz(conv.last_message_at)},
  {_sql_text(conv.last_message_sender)},
  {_sql_int(conv.total_messages)},
  {_sql_jsonb(conv.messages)},
  {_sql_jsonb(conv.raw)},
  now()
)
ON CONFLICT (conversation_id) DO UPDATE SET
  linked_in_account_id = EXCLUDED.linked_in_account_id,
  lead_profile_url = EXCLUDED.lead_profile_url,
  lead_linkedin_id = EXCLUDED.lead_linkedin_id,
  lead_first_name = EXCLUDED.lead_first_name,
  lead_last_name = EXCLUDED.lead_last_name,
  lead_headline = EXCLUDED.lead_headline,
  lead_location = EXCLUDED.lead_location,
  lead_company_name = EXCLUDED.lead_company_name,
  lead_position = EXCLUDED.lead_position,
  has_outbound = EXCLUDED.has_outbound,
  outbound_count = EXCLUDED.outbound_count,
  inbound_count = EXCLUDED.inbound_count,
  last_message_at = EXCLUDED.last_message_at,
  last_message_sender = EXCLUDED.last_message_sender,
  total_messages = EXCLUDED.total_messages,
  messages = EXCLUDED.messages,
  raw = EXCLUDED.raw,
  updated_at = now();
""".strip()
    return sql


def _update_linkedin_outreach_threads_sql(conv: Conversation) -> Optional[str]:
    if not conv.lead_profile_url:
        return None
    outbound_count, inbound_count = conv.counts()
    if outbound_count == 0:
        return None
    # We treat "responded" as having any correspondent messages in the thread.
    responded = inbound_count > 0
    return f"""
UPDATE public.linkedin_outreach
SET
  messages_sent = {_sql_jsonb(conv.messages)},
  if_respond = {_sql_bool(responded)},
  updated_at = now()
WHERE engager_linkedin_url = {_sql_text(conv.lead_profile_url)};
""".strip()


def _run_sql(client: DatagenClient, *, project_id: str, branch_id: str, database_name: str, sql: str) -> Any:
    return client.execute_tool(
        "mcp_Neon_run_sql",
        {"params": {"projectId": project_id, "branchId": branch_id, "databaseName": database_name, "sql": sql}},
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync HeyReach conversation threads into Neon and optionally backfill linkedin_outreach.messages_sent."
    )
    parser.add_argument("--neon-project-id", default="blue-tree-25780810")
    parser.add_argument("--neon-branch-id", default="br-cool-leaf-afau0ra8")
    parser.add_argument("--neon-database", default="neondb")
    parser.add_argument("--max-conversations", type=int, default=None)
    parser.add_argument("--only-contacted", action="store_true", help="Only sync conversations with outbound messages.")
    parser.add_argument(
        "--backfill-linkedin-outreach",
        action="store_true",
        help="If set, update public.linkedin_outreach.messages_sent where engager_linkedin_url matches lead profile URL.",
    )
    args = parser.parse_args()

    _ensure_env_loaded()
    client = DatagenClient()

    account_ids = _get_all_linked_in_account_ids(client)
    if not account_ids:
        raise RuntimeError("No HeyReach LinkedIn accounts found. Check HeyReach connection in DataGen.")
    print(f"[accounts] linkedInAccountIds={account_ids}")

    conversations = _fetch_all_conversations(
        client, linked_in_account_ids=account_ids, max_conversations=args.max_conversations
    )
    if args.only_contacted:
        conversations = [c for c in conversations if c.has_outbound()]
    print(f"[sync] conversations_to_sync={len(conversations)}")

    _ensure_neon_schema(client, project_id=args.neon_project_id, branch_id=args.neon_branch_id, database_name=args.neon_database)
    print("[neon] ensured schema public.heyreach_conversations")

    upserted = 0
    outreach_updates_attempted = 0

    for conv in conversations:
        _run_sql(
            client,
            project_id=args.neon_project_id,
            branch_id=args.neon_branch_id,
            database_name=args.neon_database,
            sql=_upsert_conversation_sql(conv),
        )
        upserted += 1

        if args.backfill_linkedin_outreach:
            update_sql = _update_linkedin_outreach_threads_sql(conv)
            if update_sql:
                _run_sql(
                    client,
                    project_id=args.neon_project_id,
                    branch_id=args.neon_branch_id,
                    database_name=args.neon_database,
                    sql=update_sql,
                )
                outreach_updates_attempted += 1

    stats_rows = _run_sql(
        client,
        project_id=args.neon_project_id,
        branch_id=args.neon_branch_id,
        database_name=args.neon_database,
        sql="""
SELECT
  (SELECT COUNT(*)::int FROM public.heyreach_conversations) AS heyreach_conversations,
  (SELECT COUNT(*)::int FROM public.heyreach_conversations WHERE has_outbound) AS heyreach_contacted_conversations,
  (SELECT COUNT(DISTINCT lead_profile_url)::int FROM public.heyreach_conversations WHERE lead_profile_url IS NOT NULL) AS unique_lead_profile_urls,
  (SELECT COUNT(*)::int FROM public.linkedin_outreach WHERE messages_sent <> '[]'::jsonb) AS linkedin_outreach_with_threads;
""".strip(),
    )

    stamp = _utc_now_stamp()
    print(f"[done] upserted={upserted} outreach_updates_attempted={outreach_updates_attempted} stamp={stamp}")
    print(f"[done] neon_stats={stats_rows}")


if __name__ == "__main__":
    main()
