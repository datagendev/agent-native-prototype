---
title: "Business Ops Agents - Autonomous Multi-Step Execution"
description: "Three production agents running 100+ steps autonomously with Claude Code and MCP"
category: "use-cases"
tags: ["claude-code", "mcp", "autonomous-agents", "business-ops", "crm"]
created: 2025-01-27
updated: 2025-01-27
status: "active"
priority: "high"
author: "Jiquan Ngiam"
reference: ["https://www.linkedin.com/feed/update/urn:li:activity:7421617093432881152/"]
---

# Business Ops Agents - Autonomous Multi-Step Execution

**Author:** Jiquan Ngiam
**Date:** January 26, 2025

## Key Insight

Agents can now operate autonomously for **hundreds of steps** versus the previous 3-5 step limitation. The failure modes that made agents hard to use (loops, unexpected behaviors) are eliminated.

## Technical Stack

- **Model**: Claude Code + Opus 4.5
- **Integration**: Model Context Protocol (MCP) servers
- **Connected platforms**: Outlook, LinkedIn, Attio (CRM)

## Three Production Agents

### 1. Sally - LinkedIn Signal Scanner

Scans LinkedIn for customer signals and makes contextual judgment calls about relevant information.

**Function**: Social listening → signal detection → relevance filtering

### 2. Max - CRM Pipeline Reviewer

Reviews CRM pipeline data, identifies bottlenecks, and generates contextually appropriate outreach messages.

**Function**: Pipeline analysis → bottleneck detection → outreach generation

### 3. Charlie - Call Transcript Processor

Automatically locates call transcripts, filters for customer interactions, processes them, and creates CRM notes.

**Function**: Transcript discovery → filtering → processing → CRM update

## Core Achievement

> "I'm no longer seeing the loops or unexpected behaviors that made agents hard to use. They just work now..."

## What's Next

Work ongoing on agent orchestration and handoffs between agents.
