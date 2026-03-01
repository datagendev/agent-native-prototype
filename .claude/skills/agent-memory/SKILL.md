---
name: agent-memory
description: Memory system for recurring agents. Tracks state across runs to surface only what's new, changed, or escalated — eliminates repetitive reporting.
---

# Agent Memory Skill

Gives recurring agents persistent memory so they stop repeating themselves.

## The Problem

Without memory, every report run is stateless. The agent re-discovers the same users, re-flags the same risks, re-surfaces the same insights. Day after day:
- "ben@beneficial-intelligence.com is at-risk" (reported 4 times, no one acted)
- "jeremy.scott.ross@gmail.com is a power user" (yes, we know)
- Same at-risk users listed with incrementing `days_since_signup`

## The Fix: State + Diff

Memory lives at `memory/<agent-name>/state.json`. Each run:
1. **Read** previous state
2. **Fetch** current data (same queries as before)
3. **Diff** current vs previous
4. **Report** only what changed
5. **Write** updated state back

## Memory State Schema

```
memory/<agent-name>/state.json
```

```json
{
  "last_updated": "2026-03-01",
  "run_count": 5,
  "users": {
    "user@example.com": {
      "segment": "power_user|active|high_intent|at_risk|churned|new",
      "first_seen": "2026-01-25",
      "segment_since": "2026-01-25",
      "last_reported": "2026-02-10",
      "times_reported": 4,
      "last_snapshot": {
        "credits": 2429,
        "run_count": 2087,
        "success_rate": 92.5
      },
      "notes": ["Free-text context from previous runs"]
    }
  },
  "actions_log": [
    {
      "date": "2026-02-15",
      "user": "user@example.com",
      "action": "sent_reengagement_email",
      "outcome": "pending"
    }
  ],
  "metrics_history": [
    {
      "date": "2026-02-10",
      "total_users": 81,
      "new_users_7d": 1,
      "users_with_usage": 25
    }
  ]
}
```

## Diff Categories

After fetching current data, classify every user into exactly one diff category:

### 1. NEW — First time seeing this user
- User email not in `state.users`
- **Always report.** This is the most valuable signal.
- Example: "david@automatedemand.com just signed up and clicked 9 MCP servers"

### 2. SEGMENT_CHANGED — User moved between segments
- User exists in state but `segment` is different now
- **Always report.** Transitions tell a story.
- Examples:
  - `high_intent` → `active` = "They started using it!"
  - `active` → `at_risk` = "They stopped"
  - `at_risk` → `active` = "Re-engaged!"
  - `at_risk` → `churned` = "Lost them — 30+ days inactive"

### 3. SIGNIFICANT_CHANGE — Same segment, but meaningful metric shift
- User stays in same segment, but key metrics changed substantially
- **Report if the delta is significant:**
  - `run_count` increased by >20% since last snapshot
  - `success_rate` changed by >10 percentage points
  - `credits` dropped by >50% (heavy usage burst)
  - New MCP servers connected
- Example: "Jeremy went from 2087→2500 runs, success rate held at 92%"

### 4. ESCALATION — At-risk/failing user with no action taken
- User has been in `at_risk` or `failing` segment for 3+ reports AND no action logged in `actions_log`
- **Report ONCE as escalation, then suppress until action is taken**
- Format: "ESCALATION: ben@beneficial-intelligence.com has been at-risk for 35 days across 5 reports with no action. Decide: re-engage or mark as churned?"
- After escalation, set `times_reported` to 0 and add note "Escalated on {date}"

### 5. STABLE — Nothing meaningful changed
- Same segment, metrics within normal range
- **Do NOT report.** This is the noise we're eliminating.
- Silently update `last_snapshot` in state

## Diff Execution Process

```
Step 1: Read memory/daily-activity/state.json
Step 2: Fetch current data (PostHog + Neon queries)
Step 3: For each user in current data:
  - If not in state → category = NEW
  - If in state, segment changed → category = SEGMENT_CHANGED
  - If in state, same segment, big metric delta → category = SIGNIFICANT_CHANGE
  - If in state, at_risk 3+ times, no action → category = ESCALATION
  - Otherwise → category = STABLE (skip reporting)
Step 4: For each user in state but NOT in current data:
  - If segment was active/power_user → flag as DISAPPEARED (might be data issue)
Step 5: Generate report with only NEW + CHANGED + ESCALATION items
Step 6: Update state.json with current snapshots for ALL users
Step 7: Append to metrics_history
```

## Report Structure With Memory

Instead of flat lists, organize by what matters:

```markdown
## Daily Activity Report — 2026-03-01

### What's New (3 users)
- **sarah@company.com** — Signed up yesterday, clicked Gmail + Slack MCPs, hasn't run yet
- **mike@startup.io** — New power user: 15 runs in first day, 100% success
- **team@agency.co** — Signed up, no activity yet (watch for 3 days before flagging)

### What Changed (2 users)
- **david@automatedemand.com** — Moved from high_intent → active (first 3 runs, all successful)
- **steve@misterbrady.com** — Usage dropped: 0 runs in 12 days (was active, now at_risk)

### Needs Decision (1 escalation)
- **ben@beneficial-intelligence.com** — At-risk for 35 days, flagged 5 times, no action taken.
  Options: Send re-engagement email / Mark as churned / Ignore

### Metrics Trend
| Metric | Today | 7d ago | 14d ago | Trend |
|--------|-------|--------|---------|-------|
| Total Users | 85 | 82 | 81 | ↑ |
| Active Users | 27 | 25 | 25 | ↑ |
| MCP Clicks (7d) | 8 | 2 | 14 | ↑ |

### Stable (not shown): 12 users unchanged
```

## Updating State After Run

After generating the report, update `state.json`:

```python
import json
from datetime import date

def update_memory(state_path, current_data, diff_results):
    with open(state_path) as f:
        state = json.load(f)

    today = date.today().isoformat()
    state["last_updated"] = today
    state["run_count"] += 1

    for email, data in current_data["users"].items():
        if email not in state["users"]:
            # NEW user
            state["users"][email] = {
                "segment": data["segment"],
                "first_seen": today,
                "segment_since": today,
                "last_reported": today,
                "times_reported": 1,
                "last_snapshot": data["snapshot"],
                "notes": []
            }
        else:
            user = state["users"][email]
            old_segment = user["segment"]
            new_segment = data["segment"]

            if old_segment != new_segment:
                user["segment"] = new_segment
                user["segment_since"] = today
                user["notes"].append(f"{old_segment} -> {new_segment} on {today}")

            # Update snapshot regardless
            user["last_snapshot"] = data["snapshot"]

            # Only bump reported count if we actually reported them
            if email in diff_results["reported"]:
                user["last_reported"] = today
                user["times_reported"] += 1

    # Append metrics
    state["metrics_history"].append({
        "date": today,
        **current_data["metrics"]
    })

    # Keep only last 30 entries in metrics_history
    state["metrics_history"] = state["metrics_history"][-30:]

    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
```

## Logging Actions

When you or the user take action on a flagged user, log it:

```json
{
  "date": "2026-03-01",
  "user": "ben@beneficial-intelligence.com",
  "action": "marked_churned",
  "outcome": "removed from active tracking"
}
```

This prevents future escalation for users that have been dealt with.

## Segment Assignment Rules

| Segment | Criteria | Transition From |
|---------|----------|-----------------|
| `new` | Signed up in last 3 days, no runs yet | — |
| `high_intent` | Clicked MCP but no runs, or credits = starting amount | `new` (after 3 days) |
| `active` | Has runs in last 14 days | `new`, `high_intent`, `at_risk` |
| `power_user` | run_count > 20 AND active in last 14 days | `active` |
| `at_risk` | No runs in 14+ days (but had previous activity) OR signed up 7+ days ago with no runs | `active`, `high_intent`, `new` |
| `churned` | No activity in 30+ days | `at_risk` |
| `failing` | success_rate < 50% with run_count > 5, active in last 14 days | `active`, `power_user` |

## Threshold Constants

```python
SIGNIFICANT_RUN_INCREASE = 0.20      # 20% more runs = worth reporting
SIGNIFICANT_RATE_CHANGE = 10.0       # 10pp success rate change
SIGNIFICANT_CREDIT_DROP = 0.50       # 50% credit drop = heavy usage
ESCALATION_THRESHOLD = 3             # Reports before escalation
AT_RISK_DAYS = 14                    # Days inactive before at-risk
CHURNED_DAYS = 30                    # Days inactive before churned
NEW_USER_WINDOW = 3                  # Days before "new" becomes "high_intent"
METRICS_HISTORY_LIMIT = 30           # Max entries in metrics_history
```

## File Locations

| File | Purpose |
|------|---------|
| `memory/daily-activity/state.json` | Persistent state across runs |
| `tmp/daily-report-{date}/activity.json` | Current run's raw data (ephemeral) |
| `tmp/daily-report-{date}/diff.json` | Current run's diff results (ephemeral) |
| `tmp/daily-report-{date}/report.html` | Final report (ephemeral) |
