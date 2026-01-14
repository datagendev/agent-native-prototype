#!/usr/bin/env python3
"""
Sync HeyReach campaign results back to Neon campaign tables.

This script fetches lead status, message activity, and timestamps from HeyReach
campaigns and updates the corresponding Neon campaign tables.

Supports:
- Single campaign sync (--campaign-id)
- Multi-campaign sync (--all)
- Dry-run mode (--dry-run)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from datagen_sdk import DatagenClient


def _utc_now_stamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_env_file(path: Path) -> None:
    """Load environment variables from a file."""
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
    """Ensure DATAGEN_API_KEY is loaded from environment or ../.env"""
    _load_env_file(Path("../.env"))
    if not os.getenv("DATAGEN_API_KEY"):
        raise RuntimeError(
            "DATAGEN_API_KEY not set. Load it from ../.env or export it."
        )


def _sql_quote(text: str) -> str:
    """Escape single quotes for SQL."""
    return "'" + text.replace("'", "''") + "'"


def _sql_text(value: Optional[str]) -> str:
    """Convert string to SQL text literal or NULL."""
    if value is None:
        return "NULL"
    return _sql_quote(value)


def _sql_int(value: Optional[int]) -> str:
    """Convert int to SQL literal or NULL."""
    if value is None:
        return "NULL"
    return str(int(value))


def _sql_bool(value: bool) -> str:
    """Convert bool to SQL literal."""
    return "TRUE" if value else "FALSE"


def _sql_timestamptz(value: Optional[str]) -> str:
    """Convert ISO timestamp string to SQL timestamptz literal or NULL."""
    if not value:
        return "NULL"
    return f"{_sql_quote(value)}::timestamptz"


def _sql_jsonb(value: Any) -> str:
    """Convert Python object to SQL jsonb literal."""
    dumped = json.dumps(value, ensure_ascii=False)
    return f"{_sql_quote(dumped)}::jsonb"


@dataclass(frozen=True)
class NeonCampaign:
    """Represents a campaign record from Neon database."""
    id: int
    name: str
    table_name: str
    heyreach_campaign_id: Optional[int]
    total_prospects: int
    contacted: int
    responded: int


@dataclass(frozen=True)
class HeyReachLead:
    """Represents a lead from HeyReach campaign."""
    profile_url: str
    linkedin_id: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    headline: Optional[str]
    company: Optional[str]
    status: str  # pending, in_progress, stopped, etc.
    raw: dict[str, Any]


@dataclass(frozen=True)
class HeyReachConversation:
    """Represents a conversation from HeyReach."""
    conversation_id: str
    lead_profile_url: Optional[str]
    has_outbound: bool
    outbound_count: int
    inbound_count: int
    first_outbound_at: Optional[str]
    first_inbound_at: Optional[str]
    messages: list[dict[str, Any]]


@dataclass(frozen=True)
class SyncResult:
    """Result of syncing a single prospect."""
    prospect_id: int
    linkedin_url: str
    status_updated: bool
    old_status: Optional[str]
    new_status: Optional[str]
    contacted_at: Optional[str]
    responded_at: Optional[str]


def _run_sql(client: DatagenClient, *, project_id: str, branch_id: str, database_name: str, sql: str) -> Any:
    """Execute SQL query against Neon database."""
    return client.execute_tool(
        "mcp_Neon_run_sql",
        {"sql": sql, "projectId": project_id, "databaseName": database_name},
    )


def _fetch_neon_campaign(
    client: DatagenClient,
    *,
    project_id: str,
    branch_id: str,
    database_name: str,
    campaign_id: int,
) -> Optional[NeonCampaign]:
    """Fetch campaign record from Neon database."""
    sql = f"""
SELECT id, name, table_name, heyreach_campaign_id, total_prospects, contacted, responded
FROM campaigns
WHERE id = {campaign_id};
""".strip()

    result = _run_sql(client, project_id=project_id, branch_id=branch_id, database_name=database_name, sql=sql)

    if not result or not isinstance(result, list) or len(result) == 0:
        return None

    rows = result[0] if isinstance(result[0], list) else []
    if not rows:
        return None

    row = rows[0]
    return NeonCampaign(
        id=row.get("id"),
        name=row.get("name"),
        table_name=row.get("table_name"),
        heyreach_campaign_id=row.get("heyreach_campaign_id"),
        total_prospects=row.get("total_prospects", 0),
        contacted=row.get("contacted", 0),
        responded=row.get("responded", 0),
    )


def _fetch_all_neon_campaigns(
    client: DatagenClient,
    *,
    project_id: str,
    branch_id: str,
    database_name: str,
) -> list[NeonCampaign]:
    """Fetch all campaigns with heyreach_campaign_id set."""
    sql = """
SELECT id, name, table_name, heyreach_campaign_id, total_prospects, contacted, responded
FROM campaigns
WHERE heyreach_campaign_id IS NOT NULL
ORDER BY id;
""".strip()

    result = _run_sql(client, project_id=project_id, branch_id=branch_id, database_name=database_name, sql=sql)

    if not result or not isinstance(result, list) or len(result) == 0:
        return []

    rows = result[0] if isinstance(result[0], list) else []
    campaigns = []

    for row in rows:
        campaigns.append(NeonCampaign(
            id=row.get("id"),
            name=row.get("name"),
            table_name=row.get("table_name"),
            heyreach_campaign_id=row.get("heyreach_campaign_id"),
            total_prospects=row.get("total_prospects", 0),
            contacted=row.get("contacted", 0),
            responded=row.get("responded", 0),
        ))

    return campaigns


def _fetch_heyreach_campaign_leads(
    client: DatagenClient,
    *,
    heyreach_campaign_id: int,
) -> list[HeyReachLead]:
    """Fetch all leads from a HeyReach campaign with pagination."""
    offset = 0
    limit = 100
    leads: list[HeyReachLead] = []

    print(f"📊 Fetching HeyReach campaign leads (campaign_id={heyreach_campaign_id})...")

    while True:
        resp = client.execute_tool(
            "mcp_Heyreach_get_leads_from_campaign",
            {
                "campaignId": heyreach_campaign_id,
                "limit": limit,
                "offset": offset,
                "timeFrom": None,
                "timeTo": None,
                "timeFilter": None,
            },
        )

        payload = resp[0] if isinstance(resp, list) and resp else {}
        if not isinstance(payload, dict):
            break

        total_count = payload.get("totalCount") if isinstance(payload.get("totalCount"), int) else None
        items = payload.get("items") if isinstance(payload.get("items"), list) else []

        print(f"   Fetched {len(items)} leads (offset={offset}, total={total_count})")

        for item in items:
            if not isinstance(item, dict):
                continue

            profile_url = item.get("profileUrl")
            if not profile_url or not isinstance(profile_url, str):
                continue

            leads.append(HeyReachLead(
                profile_url=profile_url,
                linkedin_id=item.get("linkedinId") if isinstance(item.get("linkedinId"), str) else None,
                first_name=item.get("firstName") if isinstance(item.get("firstName"), str) else None,
                last_name=item.get("lastName") if isinstance(item.get("lastName"), str) else None,
                headline=item.get("position") if isinstance(item.get("position"), str) else None,
                company=item.get("companyName") if isinstance(item.get("companyName"), str) else None,
                status=item.get("status", "unknown"),
                raw=item,
            ))

        if total_count is None:
            break
        offset += limit
        if offset >= total_count:
            break

    print(f"✅ Found {len(leads)} leads in HeyReach campaign\n")
    return leads


def _get_all_linked_in_account_ids(client: DatagenClient) -> list[int]:
    """Get all LinkedIn account IDs from HeyReach."""
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


def _fetch_heyreach_conversations(
    client: DatagenClient,
    *,
    heyreach_campaign_id: int,
    linkedin_account_ids: list[int],
) -> dict[str, HeyReachConversation]:
    """
    Fetch conversations for a HeyReach campaign.

    Returns dict mapping lead_profile_url → HeyReachConversation.
    """
    offset = 0
    limit = 100
    conversations: dict[str, HeyReachConversation] = {}

    print(f"📨 Fetching HeyReach conversations (campaign_id={heyreach_campaign_id})...")

    while True:
        resp = client.execute_tool(
            "mcp_Heyreach_get_conversations_v2",
            {
                "linkedInAccountIds": linkedin_account_ids,
                "campaignIds": [heyreach_campaign_id],
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

        print(f"   Fetched {len(items)} conversations (offset={offset}, total={total_count})")

        for item in items:
            if not isinstance(item, dict):
                continue

            correspondent = item.get("correspondentProfile") if isinstance(item.get("correspondentProfile"), dict) else {}
            lead_profile_url = correspondent.get("profileUrl")
            if not lead_profile_url or not isinstance(lead_profile_url, str):
                continue

            messages = item.get("messages") if isinstance(item.get("messages"), list) else []

            # Count outbound/inbound and find first timestamps
            outbound_count = 0
            inbound_count = 0
            first_outbound_at: Optional[str] = None
            first_inbound_at: Optional[str] = None

            for msg in messages:
                if not isinstance(msg, dict):
                    continue

                sender = msg.get("sender")
                sent_at = msg.get("sentAt") if isinstance(msg.get("sentAt"), str) else None

                if sender == "ME":
                    outbound_count += 1
                    if sent_at and (first_outbound_at is None or sent_at < first_outbound_at):
                        first_outbound_at = sent_at
                elif sender == "CORRESPONDENT":
                    inbound_count += 1
                    if sent_at and (first_inbound_at is None or sent_at < first_inbound_at):
                        first_inbound_at = sent_at

            conversations[lead_profile_url] = HeyReachConversation(
                conversation_id=str(item.get("id", "")),
                lead_profile_url=lead_profile_url,
                has_outbound=outbound_count > 0,
                outbound_count=outbound_count,
                inbound_count=inbound_count,
                first_outbound_at=first_outbound_at,
                first_inbound_at=first_inbound_at,
                messages=[m for m in messages if isinstance(m, dict)],
            )

        if total_count is None:
            break
        offset += limit
        if offset >= total_count:
            break

    print(f"✅ Found {len(conversations)} conversations\n")
    return conversations


def _fetch_campaign_prospects(
    client: DatagenClient,
    *,
    project_id: str,
    branch_id: str,
    database_name: str,
    campaign_table: str,
) -> dict[str, dict[str, Any]]:
    """
    Fetch prospects from campaign table.

    Returns dict mapping linkedin_url → prospect data.
    """
    sql = f"""
SELECT
    ct.id as campaign_entry_id,
    ct.status as current_status,
    ct.contacted_at,
    ct.responded_at,
    p.id as prospect_id,
    p.linkedin_url,
    p.name
FROM {campaign_table} ct
JOIN prospects p ON p.id = ct.prospect_id
ORDER BY ct.id;
""".strip()

    result = _run_sql(client, project_id=project_id, branch_id=branch_id, database_name=database_name, sql=sql)

    prospects_map: dict[str, dict[str, Any]] = {}

    if result and isinstance(result, list) and len(result) > 0:
        rows = result[0] if isinstance(result[0], list) else []
        for row in rows:
            linkedin_url = row.get("linkedin_url")
            if linkedin_url:
                prospects_map[linkedin_url] = row

    return prospects_map


def sync_campaign(
    client: DatagenClient,
    *,
    campaign: NeonCampaign,
    project_id: str,
    branch_id: str,
    database_name: str,
    heyreach_campaign_id_override: Optional[int],
    dry_run: bool,
) -> dict[str, Any]:
    """
    Sync a single campaign from HeyReach to Neon.

    Returns sync statistics.
    """
    # Determine which HeyReach campaign ID to use
    heyreach_campaign_id = heyreach_campaign_id_override or campaign.heyreach_campaign_id

    if not heyreach_campaign_id:
        print(f"❌ Campaign {campaign.id} ({campaign.name}) has no heyreach_campaign_id set")
        return {"error": "no_heyreach_campaign_id"}

    print("="*80)
    print(f"Campaign: {campaign.name} (ID: {campaign.id})")
    print(f"HeyReach Campaign: {heyreach_campaign_id}")
    print(f"Campaign Table: {campaign.table_name}")
    print("="*80)
    print()

    # Fetch HeyReach data
    linkedin_account_ids = _get_all_linked_in_account_ids(client)
    if not linkedin_account_ids:
        print("⚠️  No LinkedIn accounts found in HeyReach")

    leads = _fetch_heyreach_campaign_leads(client, heyreach_campaign_id=heyreach_campaign_id)
    conversations = _fetch_heyreach_conversations(
        client,
        heyreach_campaign_id=heyreach_campaign_id,
        linkedin_account_ids=linkedin_account_ids,
    )

    # Fetch Neon prospects
    print(f"🔍 Fetching prospects from {campaign.table_name}...")
    prospects = _fetch_campaign_prospects(
        client,
        project_id=project_id,
        branch_id=branch_id,
        database_name=database_name,
        campaign_table=campaign.table_name,
    )
    print(f"✅ Found {len(prospects)} prospects in campaign table\n")

    # Match and update
    print("🔄 Matching HeyReach data to Neon prospects...")
    matched = 0
    unmatched = 0
    updates: list[SyncResult] = []

    # If we have leads, use them; otherwise use conversations
    if leads:
        # Use leads as the source
        for lead in leads:
            prospect = prospects.get(lead.profile_url)

            if not prospect:
                unmatched += 1
                continue

            matched += 1

            # Get conversation data if available
            conversation = conversations.get(lead.profile_url)

            # Determine new status
            old_status = prospect.get("current_status")
            new_status = old_status

            # Update status based on conversation activity
            if conversation and conversation.has_outbound:
                new_status = "contacted"
                if conversation.inbound_count > 0:
                    new_status = "responded"
            elif old_status == "pending":
                # Keep as pending if no conversation
                new_status = "pending"

            # Get timestamps
            contacted_at = conversation.first_outbound_at if conversation else None
            responded_at = conversation.first_inbound_at if conversation else None

            updates.append(SyncResult(
                prospect_id=prospect["prospect_id"],
                linkedin_url=lead.profile_url,
                status_updated=(new_status != old_status),
                old_status=old_status,
                new_status=new_status,
                contacted_at=contacted_at,
                responded_at=responded_at,
            ))

        print(f"✅ Matched {matched}/{len(leads)} leads ({unmatched} unmatched)\n")
    else:
        # No pending leads, use conversations instead
        print("ℹ️  No pending leads found, using conversations...")
        for profile_url, conversation in conversations.items():
            prospect = prospects.get(profile_url)

            if not prospect:
                unmatched += 1
                continue

            matched += 1

            # Determine new status
            old_status = prospect.get("current_status")
            new_status = old_status

            # Update status based on conversation activity
            if conversation.has_outbound:
                new_status = "contacted"
                if conversation.inbound_count > 0:
                    new_status = "responded"

            # Get timestamps
            contacted_at = conversation.first_outbound_at if conversation else None
            responded_at = conversation.first_inbound_at if conversation else None

            updates.append(SyncResult(
                prospect_id=prospect["prospect_id"],
                linkedin_url=profile_url,
                status_updated=(new_status != old_status),
                old_status=old_status,
                new_status=new_status,
                contacted_at=contacted_at,
                responded_at=responded_at,
            ))

        print(f"✅ Matched {matched}/{len(conversations)} conversations ({unmatched} unmatched)\n")

    # Apply updates
    if not dry_run and updates:
        print(f"📝 Updating {len(updates)} prospects in {campaign.table_name}...")

        status_updates = 0
        contacted_updates = 0
        responded_updates = 0

        for update in updates:
            # Build UPDATE statement
            set_clauses = []

            if update.status_updated and update.new_status:
                set_clauses.append(f"status = {_sql_text(update.new_status)}")
                status_updates += 1

            if update.contacted_at:
                set_clauses.append(f"contacted_at = {_sql_timestamptz(update.contacted_at)}")
                contacted_updates += 1

            if update.responded_at:
                set_clauses.append(f"responded_at = {_sql_timestamptz(update.responded_at)}")
                responded_updates += 1

            if not set_clauses:
                continue

            update_sql = f"""
UPDATE {campaign.table_name}
SET {', '.join(set_clauses)}
WHERE prospect_id = {update.prospect_id};
""".strip()

            _run_sql(client, project_id=project_id, branch_id=branch_id, database_name=database_name, sql=update_sql)

        print(f"   ✅ Status updates: {status_updates}")
        print(f"   ✅ Contacted timestamps: {contacted_updates}")
        print(f"   ✅ Response timestamps: {responded_updates}\n")

        # Update campaigns table metrics
        print("📊 Updating campaigns table metrics...")
        metrics_sql = f"""
UPDATE campaigns
SET
    contacted = (SELECT COUNT(*) FROM {campaign.table_name} WHERE contacted_at IS NOT NULL),
    responded = (SELECT COUNT(*) FROM {campaign.table_name} WHERE responded_at IS NOT NULL),
    last_synced_at = now()
WHERE id = {campaign.id};
""".strip()

        _run_sql(client, project_id=project_id, branch_id=branch_id, database_name=database_name, sql=metrics_sql)
        print("   ✅ Updated campaign metrics\n")

    elif dry_run:
        print(f"🔍 DRY RUN: Would update {len(updates)} prospects")
        status_updates = sum(1 for u in updates if u.status_updated)
        contacted_updates = sum(1 for u in updates if u.contacted_at)
        responded_updates = sum(1 for u in updates if u.responded_at)
        print(f"   - Status updates: {status_updates}")
        print(f"   - Contacted timestamps: {contacted_updates}")
        print(f"   - Response timestamps: {responded_updates}\n")

    return {
        "campaign_id": campaign.id,
        "leads_processed": len(leads),
        "matched": matched,
        "unmatched": unmatched,
        "status_updates": sum(1 for u in updates if u.status_updated),
        "contacted_updates": sum(1 for u in updates if u.contacted_at),
        "responded_updates": sum(1 for u in updates if u.responded_at),
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync HeyReach campaign results to Neon campaign tables."
    )
    parser.add_argument("--neon-project-id", default="blue-tree-25780810")
    parser.add_argument("--neon-branch-id", default="br-cool-leaf-afau0ra8")
    parser.add_argument("--neon-database", default="neondb")
    parser.add_argument("--campaign-id", type=int, help="Neon campaign ID to sync")
    parser.add_argument("--heyreach-campaign-id", type=int, help="HeyReach campaign ID override")
    parser.add_argument("--all", action="store_true", help="Sync all campaigns with heyreach_campaign_id set")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without updating database")

    args = parser.parse_args()

    # Validate arguments
    if not args.all and not args.campaign_id:
        parser.error("Either --campaign-id or --all is required")

    if args.all and args.campaign_id:
        parser.error("Cannot use both --campaign-id and --all")

    _ensure_env_loaded()
    client = DatagenClient(timeout=120)  # 120 second timeout for slow SQL queries

    print("\n" + "="*80)
    print("HEYREACH CAMPAIGN SYNC")
    print("="*80)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")

    # Fetch campaigns to sync
    campaigns_to_sync: list[NeonCampaign] = []

    if args.all:
        print("📊 Fetching all campaigns with HeyReach integration...")
        campaigns_to_sync = _fetch_all_neon_campaigns(
            client,
            project_id=args.neon_project_id,
            branch_id=args.neon_branch_id,
            database_name=args.neon_database,
        )
        print(f"✅ Found {len(campaigns_to_sync)} campaigns to sync\n")
    else:
        print(f"📊 Fetching campaign {args.campaign_id}...")
        campaign = _fetch_neon_campaign(
            client,
            project_id=args.neon_project_id,
            branch_id=args.neon_branch_id,
            database_name=args.neon_database,
            campaign_id=args.campaign_id,
        )
        if not campaign:
            print(f"❌ Campaign {args.campaign_id} not found in Neon database")
            sys.exit(1)
        campaigns_to_sync = [campaign]
        print(f"✅ Found campaign: {campaign.name}\n")

    if not campaigns_to_sync:
        print("❌ No campaigns to sync")
        sys.exit(0)

    # Sync each campaign
    all_stats = []
    for campaign in campaigns_to_sync:
        stats = sync_campaign(
            client,
            campaign=campaign,
            project_id=args.neon_project_id,
            branch_id=args.neon_branch_id,
            database_name=args.neon_database,
            heyreach_campaign_id_override=args.heyreach_campaign_id,
            dry_run=args.dry_run,
        )
        all_stats.append(stats)

    # Print summary
    print("\n" + "="*80)
    print("SYNC SUMMARY")
    print("="*80)
    print(f"Campaigns Synced: {len(campaigns_to_sync)}")
    print(f"Timestamp: {_utc_now_stamp()}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
