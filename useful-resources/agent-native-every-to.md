---
title: "Agent-Native Architectures Guide"
description: "Framework for building software where AI agents are first-class citizens"
category: "research"
tags: ["agent-native", "architecture", "ai-agents", "product-design"]
source: "https://every.to/guides/agent-native"
created: 2026-01-10
updated: 2026-01-10
status: "active"
priority: "high"
---

# Agent-Native Architectures: Building Applications Where Agents Are First-Class Citizens

## Core Concept

This guide presents a framework for developing software where AI agents operate as primary actors rather than supporting features. The key insight: reliable agent capabilities (demonstrated by Claude Code) create opportunities to build entire application architectures around agent-driven outcomes rather than traditional UI-based feature implementation.

## Five Foundational Principles

**1. Parity**
Agents must accomplish through tools anything users can do through the interface. The test: pick any UI action and verify the agent can achieve that outcome.

**2. Granularity**
Tools should be atomic primitives. Features become outcomes achieved by agents operating in loops until completion. Decision-making belongs in prompts, not bundled into tools.

**3. Composability**
With atomic tools and parity established, new features emerge simply by writing new prompts. Users can request novel combinations without code changes.

**4. Emergent Capability**
Agents accomplish unanticipated tasks by composing existing tools. This reveals latent user demand—patterns you observe rather than predict, enabling product discovery through agent usage.

**5. Improvement Over Time**
Agent applications improve without shipping code updates through accumulated context files and prompt refinement at developer and user levels.

## Architectural Patterns

### From Primitives to Domain Tools

Start with battle-tested primitives (bash, file operations, basic storage) to validate the approach. As patterns emerge, deliberately add domain-specific tools for:
- **Vocabulary anchoring** (teaching what "note" means in your system)
- **Guardrails** (validation that shouldn't rely on agent judgment)
- **Efficiency** (bundling common operations)

Critical principle: keep primitives available. Domain tools represent shortcuts, not restrictions. The default stance is openness; gating should be conscious, deliberate choices.

### Files as Universal Interface

Agents naturally work with files. This approach offers:
- **Familiarity** (agents know `cat`, `grep`, `mv`, `mkdir`)
- **Inspectability** (users see and can modify agent work)
- **Portability** (export and backup are trivial)
- **Cross-device sync** (iCloud enables agent work everywhere without server infrastructure)
- **Self-documentation** (`/projects/acme/notes/` is more legible than `SELECT * FROM notes WHERE project_id = 123`)

#### Suggested File Organization

Entity-scoped directories group related materials:
```
{entityType}/{entityId}/
├── primary content
├── metadata
└── related materials
```

Example: `Research/books/{bookId}/` contains full text, notes, sources, and agent logs.

Naming conventions: lowercase with underscores, markdown for human content, JSON for structured data. The `context.md` pattern maintains portable working memory—agent state without code changes.

### Database vs. Files Decision

**Use files for:**
- Content users should read/edit
- Configuration benefiting from version control
- Agent-generated content
- Anything valuing transparency

**Use databases for:**
- High-volume structured data
- Complex queries
- Ephemeral state
- Data requiring indexing and relationships

## Agent Execution Patterns

### Completion Signals
Agents need explicit "done" indicators, separate from success/failure status:
- Success signals continue the loop
- Errors signal continue (retry logic)
- Completion stops the loop

Current gaps exist around formal "pause" (awaiting user input), "escalate" (needing human judgment), and "retry" (transient failures) signals.

### Context Limits
Design for bounded contexts from the start. Rather than all-or-nothing approaches:
- Support iterative refinement (summary → detail → full)
- Provide consolidation tools mid-session
- Assume context will eventually fill

### Partial Completion Tracking
For multi-step tasks, maintain task-level status (pending, in_progress, completed, failed, skipped). This enables resumption after interruption and displays meaningful progress.

## Mobile Considerations

Mobile presents unique constraints and opportunities: local file systems, rich context access (health, location, photos, calendars), device-local applications, and iCloud syncing eliminate server dependencies.

**The core challenge:** Agents require time (30 seconds to hours), but iOS backgrounds apps after seconds, potentially killing them entirely.

### iOS Storage Architecture

Implement iCloud-first with local fallback:
```
iCloud Container (preferred)
Local Documents (fallback)
Migration layer
```

This provides automatic cross-device sync, transparent backup, graceful degradation, and user accessibility outside the app.

### Checkpoint and Resume
When iOS interrupts agents, save session state immediately:
- Checkpoint: agent type, messages, iteration count, task list, custom state, timestamp
- Frequency: after backgrounding, post tool-result, periodically during operations
- Resume: load interrupted sessions, filter by validity (one-hour default), prompt user, restore and continue

### Background Execution
iOS grants roughly 30 seconds. Use this window to:
- Complete current tool calls if possible
- Checkpoint state
- Transition gracefully to backgrounded status

For truly long-running agents, consider server-side orchestration with mobile as viewer/input.

## Product Implications

### Progressive Disclosure
Simple to start, endlessly powerful. Basic requests work immediately; power users discover capability through exploration. No ceiling exists—comparable to how Excel serves grocery lists and financial models identically.

### Latent Demand Discovery
Traditional product development guesses user needs then validates. Agent-native development builds a capable foundation, observes what users ask agents to accomplish, then formalizes emergent patterns. Success signals appear when requests work; failures reveal tool gaps or parity violations.

### Approval and User Agency

Unsolicited agent actions require consideration based on stakes and reversibility:
- Low stakes, easily reversible → auto-apply
- Low stakes, hard to reverse → quick confirm
- High stakes, easily reversible → suggest + apply
- High stakes, hard to reverse → explicit approval

(Note: explicit user requests bypass approval—"send that email" is pre-approved.)

Self-modifying agents must maintain legibility through visible changes, understood effects, and easy rollback.

## Anti-Patterns to Avoid

- **Agent-as-router**: Using agent intelligence only for request routing wastes capability
- **Add-on agents**: Exposing traditional features to agents limits emergent possibility
- **Request/response thinking**: Missing the loop architecture
- **Over-constrained tools**: Defensive programming prevents unanticipated compositions
- **Logic in code**: Edge cases handled by code prevent agent judgment
- **Orphan UI actions**: User capabilities agents cannot achieve violate parity
- **Context starvation**: Agents unaware of available resources
- **Artificial capability limits**: Restricting access without specific safety justification
- **Heuristic completion**: Detecting completion through patterns rather than explicit signals

## Success Criteria

**Architecture:**
- Parity achieved (agent accomplishes UI actions)
- Atomic primitives used; domain tools as shortcuts
- Prompt-driven features work
- Unanticipated tasks get completed
- Behavior changes require prompt edits, not code refactoring

**Implementation:**
- System prompts include available resources
- Shared data spaces (agent and user)
- Immediate UI reflection of agent actions
- Full CRUD for every entity
- Dynamic capability discovery where appropriate
- Explicit completion signals

**Product:**
- Low barrier to entry
- Discoverable power for advanced users
- Observable user demand guiding development
- Approval matching stakes/reversibility

**Ultimate Test:**
Describe an outcome within your domain that you didn't build explicitly. If the agent figures it out through tool composition, you've achieved agent-native architecture. If it fails, your system is too constrained.
