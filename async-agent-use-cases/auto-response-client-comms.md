---
title: "Auto-Response Client Communication"
description: "Always-on agent that handles inbound client messages with context-aware responses and smart escalation"
category: "use-cases"
tags: ["async-agent", "client-communication", "auto-response", "whatsapp", "slack", "escalation"]
created: 2026-01-30
updated: 2026-01-30
status: "draft"
priority: "medium"
based_on: ["[[clawdbot-scheduled-automation]]"]
---

# Auto-Response Client Communication

Always-on agent that handles inbound client messages, provides project status updates, answers FAQs, and escalates urgent issues -- maintaining fast response times even outside business hours.

## Problem

- Clients expect fast responses (minutes, not hours)
- After-hours messages go unanswered until next business day
- Repetitive questions (project status, timelines, access issues) consume team time
- Urgent issues get lost in regular message flow
- Response quality varies by team member availability and knowledge

## Solution

Event-driven async agent that:
1. Listens for inbound client messages (WhatsApp, Slack, email)
2. Classifies message type and urgency
3. Auto-responds to routine queries with accurate, context-aware answers
4. Escalates urgent or complex issues to the right human
5. Maintains average 2-minute response time 24/7

## Trigger

```
Webhook: New message received on monitored channels OR
Polling: Check channels every 2 minutes
```

## Pipeline

```
1. RECEIVE inbound message
   - WhatsApp, Slack, or email
   - Extract sender, content, channel, timestamp
    |
2. IDENTIFY client
   - Match sender to client record in CRM
   - Load client context (projects, SLA, account manager)
   - Check conversation history
    |
3. CLASSIFY message
   - Status inquiry → Pull project data, respond
   - FAQ / How-to → Match to knowledge base, respond
   - Bug report → Log issue, acknowledge, escalate
   - Urgent / Escalation → Alert on-call, acknowledge
   - Scheduling → Check calendar, propose options
   - General chat → Friendly acknowledge, flag for human
    |
4. GENERATE response
   - Pull relevant context (project status, docs, previous conversations)
   - Draft response matching client's communication style
   - Include specific data (dates, numbers, links)
    |
5. RESPOND
   - Send on same channel message was received
   - Log interaction in CRM
    |
6. ESCALATE (if needed)
   - Page account manager via Slack DM or SMS
   - Include full context and suggested response
   - Track escalation until resolved
```

## Classification Schema

```yaml
client_message:
  id: string
  received_at: datetime

  sender:
    name: string
    company: string
    channel: whatsapp|slack|email
    is_vip: boolean

  client_context:
    account_manager: string
    active_projects: list
    sla_tier: premium|standard|basic
    last_interaction: datetime

  classification:
    type: status_inquiry|faq|bug_report|urgent|scheduling|general
    urgency: critical|high|normal|low
    can_auto_respond: boolean
    confidence: float

  response:
    text: string
    source: auto|template|escalated
    response_time_seconds: integer

  escalation:
    needed: boolean
    reason: string
    assigned_to: string
    status: pending|acknowledged|resolved
```

## Response Rules

```yaml
rules:
  - type: status_inquiry
    action: auto_respond
    data_source: project_management_tool
    template: |
      Hi {client_name}! Here's the latest on {project_name}:
      - Current phase: {phase}
      - Next milestone: {milestone} ({date})
      - Open items: {count}
      Let me know if you'd like more details on anything specific.

  - type: faq
    action: auto_respond
    data_source: knowledge_base
    confidence_threshold: 0.85
    fallback: escalate

  - type: bug_report
    action: acknowledge_and_escalate
    template: |
      Thanks for flagging this, {client_name}. I've logged the issue
      and notified the team. Someone will follow up within {sla_time}.
      Reference: {ticket_id}

  - type: urgent
    action: acknowledge_and_page
    template: |
      I understand this is urgent, {client_name}. I'm paging
      {account_manager} right now. They'll be in touch shortly.
    escalate_via: [slack_dm, sms]

  - type: general
    action: acknowledge_and_flag
    template: |
      Thanks for your message! I'll make sure {account_manager}
      sees this. They'll get back to you during business hours.
```

## Output: Interaction Log

```markdown
# Client Comms: {date}

## Auto-Responded (8)
| Time | Client | Channel | Type | Response Time |
|------|--------|---------|------|---------------|
| 09:15 | Acme Corp | WhatsApp | Status inquiry | 47s |
| 10:30 | TechStart | Slack | FAQ (API docs) | 1m 12s |
| 14:22 | BigCo | WhatsApp | Status inquiry | 38s |
| 18:45 | StartupX | Email | FAQ (pricing) | 2m 05s |
| 22:10 | Acme Corp | WhatsApp | Scheduling | 1m 30s |
| ... | ... | ... | ... | ... |

## Escalated (2)
| Time | Client | Channel | Type | Assigned To | Status |
|------|--------|---------|------|-------------|--------|
| 11:45 | BigCo | Slack | Bug report | @sarah | Resolved |
| 16:30 | VIPClient | WhatsApp | Urgent | @mike | In progress |

## Metrics
- Total messages handled: 10
- Auto-responded: 8 (80%)
- Escalated: 2 (20%)
- Avg response time: 1m 14s
- After-hours messages: 3 (all auto-responded)
- Client satisfaction: No complaints
```

## Integration Points

- **Input**: WhatsApp Business API, Slack MCP, Gmail MCP
- **Context**: CRM (client records), Project management tool (status), Knowledge base
- **Output**: Auto-responses on same channel, CRM interaction logging
- **Escalation**: Slack DM, SMS (PagerDuty/Twilio), email to account manager
- **Storage**: `./tmp/client-comms/{date}/` for interaction logs

## Implementation with DataGen

```python
from datagen_sdk import DatagenClient

client = DatagenClient()

# Step 1: Fetch new messages
messages = client.execute_tool("mcp_WhatsApp_get_messages", {
    "since": last_check_timestamp,
    "unread": True
})

# Step 2: For each message, identify client and classify
for msg in messages:
    # Look up client in CRM
    contact = client.execute_tool("mcp_HubSpot_search_contacts", {
        "query": msg["sender_phone"]
    })

    # Get project status if needed
    if classification == "status_inquiry":
        projects = client.execute_tool("mcp_Linear_list_projects", {
            "team": contact["team_id"]
        })

# Step 3: Send response
client.execute_tool("mcp_WhatsApp_send_message", {
    "to": msg["sender_phone"],
    "text": generated_response
})

# Step 4: Escalate if needed
client.execute_tool("mcp_Slack_post_message", {
    "channel": f"@{account_manager}",
    "text": f"Urgent from {client_name}: {summary}"
})
```

## Success Metrics

- Average response time: <2 minutes (target)
- Auto-response rate: >70% of messages handled without human
- Escalation accuracy: >95% (correct urgency classification)
- Client satisfaction: No increase in complaints
- After-hours coverage: 100% of messages acknowledged

## Phases

### Phase 1: Acknowledge & Route
Auto-acknowledge all messages, classify, and route to the right human. No auto-responses.

### Phase 2: FAQ & Status Auto-Response
Auto-respond to status inquiries and FAQs. Escalate everything else.

### Phase 3: Full Context-Aware Response
Pull project data, conversation history, and client preferences for personalized auto-responses.

## MCP Requirements

- WhatsApp Business MCP or Slack MCP (message receive/send)
- CRM MCP (client lookup, interaction logging)
- Project management MCP (status data)
- Slack MCP (internal escalation)
- Optional: PagerDuty/Twilio MCP (urgent escalation)
- Optional: Knowledge base MCP (FAQ matching)
