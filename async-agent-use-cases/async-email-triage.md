---
title: "Async Email Triage & Draft"
description: "Scheduled agent that categorizes inbox emails by intent and drafts responses per user-defined rules"
category: "use-cases"
tags: ["async-agent", "email", "triage", "auto-draft", "scheduled", "inbox-management"]
created: 2026-01-30
updated: 2026-01-30
status: "draft"
priority: "medium"
based_on: ["[[clawdbot-scheduled-automation]]"]
---

# Async Email Triage & Draft

Process inbox on a recurring schedule, categorize emails by intent, draft responses per user-defined rules, and deliver summaries.

## Problem

- Inbox overwhelm: 50-200 emails/day for sales and ops teams
- Manual triage takes 30-60 minutes before any real work starts
- Important emails (buyer intent, urgent support) get buried
- Response quality varies; no consistent rules for common scenarios
- Context-switching between reading, categorizing, and responding

## Solution

Scheduled async agent that:
1. Runs every 30 minutes (or configurable interval)
2. Fetches unread/new emails since last run
3. Categorizes each email by intent
4. Drafts responses for routine categories
5. Flags urgent items for immediate attention
6. Delivers a summary via Slack/WhatsApp

## Trigger

```
Cron: Every 30 minutes OR
Manual: "Triage my inbox" OR
Webhook: New email received (real-time mode)
```

## Pipeline

```
1. FETCH new emails
   - Gmail/Outlook via MCP
   - Since last processed timestamp
   - Include sender, subject, body, thread context
    |
2. FOR EACH email:
   - Classify intent
   - Extract key information (dates, asks, names)
   - Check sender against CRM (known contact? deal stage?)
    |
3. CATEGORIZE by intent
   - Sales inquiry → Draft qualifying response
   - Support request → Draft solution or escalate
   - Meeting request → Check calendar, propose times
   - Follow-up needed → Draft follow-up
   - Newsletter/FYI → Archive or tag
   - Urgent → Flag immediately
    |
4. DRAFT responses
   - Apply user-defined rules and templates
   - Include relevant context from CRM/previous threads
   - Mark as draft (never auto-send without approval)
    |
5. GENERATE summary
   - Group by category and priority
   - Include draft links for review
    |
6. DELIVER summary
   - Slack/WhatsApp with action items
   - Optional: Create CRM tasks for sales-related emails
```

## Classification Schema

```yaml
email_triage:
  id: string
  processed_at: datetime

  email:
    from: string
    subject: string
    received_at: datetime
    thread_id: string
    has_attachments: boolean

  sender_context:
    known_contact: boolean
    company: string
    deal_stage: string  # From CRM
    previous_interactions: integer

  classification:
    intent: sales_inquiry|support_request|meeting_request|follow_up|newsletter|urgent|internal
    confidence: float
    priority: high|medium|low
    requires_human: boolean

  draft:
    response_text: string
    template_used: string
    status: drafted|needs_review|auto_archived

  rules_applied:
    - rule_name: string
      action: draft|archive|flag|escalate
```

## User-Defined Rules (Example Config)

```yaml
rules:
  - name: "Sales inquiry from target account"
    condition:
      intent: sales_inquiry
      sender_context.deal_stage: [prospect, qualified]
    action: draft
    template: sales_response
    priority: high
    notify: true

  - name: "Support - known issue"
    condition:
      intent: support_request
      keywords: ["login", "password", "access"]
    action: draft
    template: support_password_reset
    priority: medium

  - name: "Newsletter"
    condition:
      intent: newsletter
    action: archive
    priority: low
    notify: false

  - name: "Urgent from VIP"
    condition:
      priority: high
      sender_context.deal_stage: [negotiation, closed_won]
    action: flag
    escalate_to: slack_dm
    priority: high
```

## Output: Inbox Summary

```markdown
# Inbox Triage: {time}

## Urgent (Respond Now)
- **[VIP Client]** Re: Contract renewal - asking about pricing changes
  Priority: High | Draft ready | [Review draft →]

## Sales Inquiries (2)
- **Sarah@acme.com** "Interested in your data enrichment tool"
  New lead, no CRM record | Draft ready | [Review draft →]
- **mike@techstart.io** Re: Demo follow-up
  Existing prospect, demo stage | Draft ready | [Review draft →]

## Support (1)
- **user@company.com** "Can't access dashboard"
  Known issue, password reset | Auto-drafted | [Review draft →]

## Meetings (1)
- **partner@firm.com** "Let's sync next week"
  Calendar checked, 3 slots available | Draft ready | [Review draft →]

## Auto-Archived (12)
- 8 newsletters, 3 notifications, 1 marketing email

## Summary
- Total processed: 18 emails
- Drafts ready: 5
- Auto-archived: 12
- Needs human: 1 (urgent)
```

## Integration Points

- **Input**: Gmail/Outlook MCP, CRM MCP (contact context)
- **Processing**: DataGen SDK for email fetching; Claude for classification and drafting
- **Output**: Draft emails (saved as drafts in Gmail), Slack/WhatsApp summaries
- **Storage**: `./tmp/email-triage/{date}/` for processing logs

## Implementation with DataGen

```python
from datagen_sdk import DatagenClient

client = DatagenClient()

# Step 1: Fetch new emails
emails = client.execute_tool("mcp_Gmail_search_emails", {
    "query": "is:unread after:{last_run_timestamp}",
    "limit": 50
})

# Step 2: Classify each email
for email in emails:
    # Get sender context from CRM
    contact = client.execute_tool("mcp_HubSpot_search_contacts", {
        "query": email["from"]
    })

    # AI classification happens in the custom tool logic
    # Draft response based on rules

# Step 3: Create drafts
client.execute_tool("mcp_Gmail_create_draft", {
    "to": email["from"],
    "subject": f"Re: {email['subject']}",
    "body": drafted_response
})

# Step 4: Send summary
client.execute_tool("mcp_Slack_post_message", {
    "channel": "#inbox-triage",
    "text": formatted_summary
})
```

## Success Metrics

- Emails processed per run: 10-50
- Classification accuracy: >90%
- Draft acceptance rate: >70% (sent with minor or no edits)
- Time saved: 30-60 min/day
- Response time improvement: from hours to minutes for routine items

## Phases

### Phase 1: Classify & Summarize
Categorize emails and deliver summary. No drafting.

### Phase 2: Rule-Based Drafting
Add user-defined rules and auto-draft responses for common categories.

### Phase 3: Context-Aware Drafting
Pull CRM context, previous thread history, and adapt tone per sender relationship.

## MCP Requirements

- Gmail or Outlook MCP (email read, draft creation)
- CRM MCP (contact lookup, deal stage)
- Slack or WhatsApp MCP (summary delivery)
- Calendar MCP (meeting availability)
