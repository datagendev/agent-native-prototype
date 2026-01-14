# Agent‑Native “Clay” in Claude Code: Design Notes

## Goal

Build an agent-native alternative to Clay inside Claude Code: an enrichment table system that an AI agent can **read, execute, and iteratively improve**, with strong **parity between user and agent**.

Core idea: treat **“prompt as a feature (table column)”**, powered by composable **tools/integrations**, so building and evolving enrichment tables feels native to an agent workflow.

## Why build this (vs existing approaches)

Most Claude Code agent setups tend to fall into one of these patterns:

1. **MCP + agent tokens** for small, local tasks.
2. **Fully prebuilt end-to-end workflows** for specific use cases, with limited agentic flexibility.

Clay is great, but today it’s hard for an agent to **inspect and reliably execute** (until Jeremy’s API), and there’s **poor parity**: users can edit workflows/tables in ways the agent can’t easily reproduce or understand programmatically.

Building this in Claude Code also means:
- improvements become reusable knowledge for future table building,
- the system can **guide the model** rather than tightly control it.

## Constraints (current)

1. **Minimize runtime coding during table creation**.
2. **Minimize pre-created tools**.

These balance each other: if runtime coding is minimal, you don’t need a huge library of prebuilt tools.

## Proposed 4‑Component System

### 1) Table Storage: SQLite DB

- Store tables in SQLite (not CSV).
- Benefit: every write is persisted (not just in memory).
- Enables **massive parallelization** and easier auditing.

### 2) Workflow Definition: Graph (YAML) + Nodes (Generated Code)

- **Graph**: a human-auditable YAML file describing the workflow and dependencies.
- **Node**: small generated code blocks produced from primitives (filters, transforms, logic).
- The AI generates workflows by following “enrichment skills” and learns primitive capabilities over time.

### 3) Primitive Integrations

- A base set of “primitive” integrations (initially: DataGen integrations, extendable via direct APIs).
- This is what the model explores to understand capability boundaries.
- The model composes primitives via nodes + graph, instead of requiring many bespoke tools.

### 4) Batch Executor

- Executes the YAML graph across many rows.
- Supports **parallelized execution** and writes results back to SQLite.

## Key Design Decisions

### Why a DB (SQLite) instead of CSV

- Writes are recorded immediately and consistently.
- Avoids “hidden state” in memory.
- Supports scalable, parallel execution.

### Why Nodes exist (in addition to primitives)

Often you need task-specific transformations that are too specific to bake into primitives or the graph layer directly.

Example:
- Primitive: “LinkedIn Post Commenters”
- Needed output: “Number of commenters who are VP of Sales”

Nodes absorb this “last-mile” logic so the graph stays simple and primitives stay reusable.

### Why a YAML Graph

- Easy to read and audit.
- Users can edit directly.
- Users can ask the model to modify it (diff-friendly, reviewable changes).

### Why Primitive Integrations

- Enables capability exploration.
- Lets the agent discover what’s possible and choose the simplest composition.

## How it works (user flow)

### `/enrich`

1. The model asks which **lead CSV** you want to enrich.
2. The model asks what you want to enrich (new columns/features).
3. The model asks follow-up questions to clarify requirements.
4. The model performs capability exploration:
   - primarily via DataGen integrations,
   - optionally via external APIs,
   - and via an `askUserQuestion` tool when needed.
5. The model generates:
   - Node code (small transforms/logic),
   - a YAML workflow graph wiring nodes + primitives.
6. You review and edit the nodes/graph as needed.
7. The model runs enrichment at scale using the Batch Executor.

## Supporting Commands

### `/view-table`

- Spins up a frontend server to browse/select and inspect tables.

### `/view-workflow`

- Spins up a frontend server to visualize workflows (the YAML graph and node structure).

