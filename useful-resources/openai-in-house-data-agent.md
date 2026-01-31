---
title: "Inside OpenAI's In-House Data Agent"
description: "How OpenAI built an in-house AI data agent that uses GPT-5, Codex, and memory to reason over massive datasets and deliver reliable insights in minutes."
category: "research"
tags: ["data-agent", "openai", "rag", "memory", "codex", "agent-architecture", "internal-tools"]
research-type: "case-study"
sources: ["https://openai.com/index/inside-our-in-house-data-agent/"]
created: 2026-01-29
updated: 2026-01-29
status: "active"
priority: "high"
reference: ["https://openai.com/index/inside-our-in-house-data-agent/"]
---

# Inside OpenAI's In-House Data Agent

**Authors:** Bonnie Xu, Aravind Suresh, and Emma Tang
**Published:** January 29, 2026

Data powers how systems learn, products evolve, and how companies make choices. But getting answers quickly, correctly, and with the right context is often harder than it should be. To make this easier as OpenAI scales, they built **their own bespoke in-house AI data agent** that explores and reasons over their platform.

The agent is a custom internal-only tool (not an external offering), built specifically around OpenAI's data, permissions, and workflows. The OpenAI tools used to build and run it (Codex, GPT-5, the Evals API, and the Embeddings API) are the same tools available to developers everywhere.

The data agent lets employees go from question to insight in minutes, not days. This lowers the bar to pulling data and nuanced analysis across all functions, not just by the data team. Teams across Engineering, Data Science, Go-To-Market, Finance, and Research lean on the agent to answer **high-impact data questions**.

## Why They Needed a Custom Tool

OpenAI's data platform serves more than **3.5k internal users** working across Engineering, Product, and Research, spanning over **600 petabytes** of data across **70k datasets.** At that size, simply finding the right table can be one of the most time-consuming parts of doing analysis.

> "We have a lot of tables that are fairly similar, and I spend tons of time trying to figure out how they're different and which to use. Some include logged-out users, some don't. Some have overlapping fields; it's hard to tell what is what."

Even with the correct tables selected, producing correct results can be challenging. Analysts must reason about table data and table relationships to ensure transformations and filters are applied correctly. Common failure modes -- many-to-many joins, filter pushdown errors, and unhandled nulls -- can silently invalidate results.

## How It Works

The agent is powered by **GPT-5.2** and is designed to reason over OpenAI's data platform. It's available wherever employees already work: as a Slack agent, through a web interface, inside IDEs, in the Codex CLI via MCP, and directly in OpenAI's internal ChatGPT app through a MCP connector.

### Entry Points

- Agent-UI
- Local Agent-MCP
- Remote Agent-MCP
- Slack Agent

These feed into an Agent-API, which connects to internal data knowledge and company context, syncs with a data warehouse and platform sources, and exchanges requests with the GPT-5.2 model via Agent-MCP.

### Self-Correcting Reasoning

One of the agent's superpowers is how it reasons through problems. Rather than following a fixed script, the agent evaluates its own progress. If an intermediate result looks wrong (e.g., zero rows due to an incorrect join or filter), the agent investigates what went wrong, adjusts its approach, and tries again. Throughout this process, it retains full context and carries learnings forward between steps. This **closed-loop, self-learning process** shifts iteration from the user into the agent itself.

The agent covers the full analytics workflow: discovering data, running SQL, and publishing notebooks and reports. It understands internal company knowledge, can web search for external information, and improves over time through learned usage and memory.

## Context Is Everything

High-quality answers depend on **rich, accurate context**. Without context, even strong models can produce wrong results.

### Layer 1: Table Usage

- **Metadata grounding:** Schema metadata (column names and data types) to inform SQL writing and table lineage to provide context on how different tables relate.
- **Query inference:** Ingesting historical queries helps the agent understand how to write its own queries and which tables are typically joined together.

### Layer 2: Human Annotations

- **Curated descriptions** of tables and columns provided by domain experts, capturing intent, semantics, business meaning, and known caveats not easily inferred from schemas or past queries.

### Layer 3: Codex Enrichment

- By deriving a code-level definition of a table, the agent builds a deeper understanding of what the data actually contains.
- Provides nuances on what is stored and how it is derived from analytics events -- uniqueness of values, update frequency, scope of data, etc.
- Enhanced usage context showing how the table is used beyond SQL in Spark, Python, and other data systems.
- Can distinguish between tables that look similar but differ in critical ways.
- Context is refreshed automatically, staying up to date without manual maintenance.

### Layer 4: Institutional Knowledge

- Access to Slack, Google Docs, and Notion, capturing critical company context such as launches, reliability incidents, internal codenames and tools, and canonical metric definitions.
- Documents are ingested, embedded, and stored with metadata and permissions. A retrieval service handles access control and caching at runtime.

### Layer 5: Memory

- When the agent is given corrections or discovers nuances, it saves these learnings for next time, allowing constant improvement.
- Future answers begin from a more accurate baseline rather than repeatedly encountering the same issues.
- Memory retains and reuses non-obvious corrections, filters, and constraints critical for data correctness but difficult to infer from other layers alone.
- When corrections or learnings are found, the agent prompts users to save that memory.
- Memories can also be manually created and edited.
- Memories are scoped at the global and personal level.

### Layer 6: Runtime Context

- When no prior context exists or existing information is stale, the agent issues live queries to the data warehouse to inspect and query tables directly.
- Can also talk to other Data Platform systems (metadata service, Airflow, Spark) for broader context.

### Retrieval Architecture

A daily offline pipeline aggregates table usage, human annotations, and Codex-derived enrichment into a single, normalized representation. This enriched context is converted into embeddings using the OpenAI embeddings API and stored for retrieval. At query time, the agent pulls only the most relevant embedded context via RAG instead of scanning raw metadata or logs.

## Built to Think and Work Like a Teammate

The agent is built to behave like a teammate you can reason with. It's conversational, always-on, and handles both quick answers and iterative exploration.

- Carries over complete context across turns
- Users can interrupt mid-analysis and redirect
- Proactively asks clarifying questions when instructions are unclear
- Applies sensible defaults when no response is provided

### Reusable Workflows

After rollout, users frequently ran the same analyses for routine repetitive work. The agent's workflows package recurring analyses into reusable instruction sets (e.g., weekly business reports, table validations). By encoding context and best practices once, workflows streamline repeat analyses and ensure consistent results.

## Moving Fast Without Breaking Trust

### Evaluation Pipeline

Evals are built on curated sets of question-answer pairs. Each question targets an important metric or analytical pattern, paired with a manually authored "golden" SQL query that produces the expected result. For each eval:

1. Send the natural language question to the query-generation endpoint
2. Execute the generated SQL
3. Compare the output against the result of the expected SQL

Evaluation doesn't rely on naive string matching. Generated SQL can differ syntactically while still being correct. Both the SQL and resulting data are compared and fed into OpenAI's Evals grader, which produces a final score along with an explanation.

These evals are like unit tests that run continuously during development and as canaries in production.

## Agent Security

- Operates purely as an interface layer, inheriting and enforcing the same permissions and guardrails that govern OpenAI's data.
- All access is strictly **pass-through** -- users can only query tables they already have permission to access.
- When access is missing, it flags this or falls back to alternative datasets the user is authorized to use.
- **Exposes its reasoning process** by summarizing assumptions and execution steps alongside each answer.
- Links directly to underlying results, allowing users to inspect raw data and verify every step.

## Lessons Learned

### Lesson 1: Less is More

Early on, they exposed the full tool set to the agent and quickly ran into problems with overlapping functionality. While redundancy can be helpful for specific custom cases, it's confusing to agents. They restricted and consolidated tool calls to reduce ambiguity and improve reliability.

### Lesson 2: Guide the Goal, Not the Path

Highly prescriptive prompting degraded results. While many questions share a general analytical shape, the details vary enough that rigid instructions often pushed the agent down incorrect paths. By shifting to higher-level guidance and relying on GPT-5's reasoning to choose the appropriate execution path, the agent became more robust and produced better results.

### Lesson 3: Meaning Lives in Code

Schemas and query history describe a table's shape and usage, but its true meaning lives in the code that produces it. Pipeline logic captures assumptions, freshness guarantees, and business intent that never surface in SQL or metadata. By crawling the codebase with Codex, the agent understands how datasets are actually constructed and can answer "what's in here" and "when can I use it" far more accurately than from warehouse signals alone.

## Same Vision, New Tools

They're constantly working to improve the agent by increasing its ability to handle ambiguous questions, improving reliability and accuracy with stronger validations, and integrating it more deeply into workflows. The belief is it should blend naturally into how people already work, instead of functioning like a separate tool.
