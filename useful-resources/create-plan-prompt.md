---
title: "Creating Implementation Plans for Coding Agents"
description: "Prompt system for creating detailed implementation plans through interactive research and iteration"
category: "research"
tags: ["agents", "planning", "implementation", "prompt-engineering", "12-factor"]
research-type: "agent-patterns"
created: 2026-01-14
updated: 2026-01-14
status: "active"
priority: "high"
reference: ["https://github.com/ai-that-works/ai-that-works/blob/main/2026-01-13-applying-12-factor-principles-to-coding-agent-sdks/src/prompts/create_plan.md"]
based_on: ["[[effective-harnesses-long-running-agents]]", "[[context-engineering-manus]]"]
---

# Creating Implementation Plans for Coding Agents

**Source:** ai-that-works/ai-that-works GitHub

## Overview

A comprehensive prompt system for creating detailed implementation plans through interactive research and iteration. Users work collaboratively with the agent to produce high-quality technical specifications, with the model serving as a skeptical, thorough partner.

## Key Process Steps

### Step 1: Context Gathering & Initial Analysis

- Read all mentioned files completely before planning (no partial reads)
- Spawn parallel research tasks using specialized agents:
  - `codebase-locator` - Find relevant code
  - `codebase-analyzer` - Understand architecture
  - `thoughts-locator` - Find existing analysis
- Read all files identified by research tasks in full
- Present informed understanding with focused questions only

**Goal**: Build comprehensive understanding of existing codebase before proposing changes.

### Step 2: Research & Discovery

- Create research todo lists to track exploration
- Spawn multiple concurrent sub-tasks for comprehensive investigation
- Use appropriate agents for different research types
- Wait for all sub-tasks to complete before proceeding
- Present findings with design options and open questions

**Goal**: Surface all relevant context and uncertainties before planning.

### Step 3: Plan Structure Development

- Create initial outline with proposed phases
- Obtain feedback on structure before writing details
- Validate approach with user before deep work

**Goal**: Get alignment on direction before writing detailed specifications.

### Step 4: Detailed Plan Writing

Write to: `thoughts/shared/plans/YYYY-MM-DD-ENG-XXXX-description.md`

Template structure includes:
- **Overview**: High-level summary
- **Current State**: Existing implementation details
- **Desired End State**: Target outcome
- **Phased Implementation**: Step-by-step execution plan
- **Success Criteria**: Automated and manual verification methods

**Goal**: Create detailed, reviewable specification with clear success criteria.

### Step 5: Sync and Review

- Run `humanlayer thoughts sync` to index the plan
- Present draft location and request feedback
- Iterate based on user feedback
- Update plan with refinements

**Goal**: Get explicit feedback before implementation begins.

## Critical Guidelines

### Read Files Completely

Never use limit/offset parameters; read entire files first. This prevents misunderstandings from partial context.

### No Open Questions in Final Plans

Resolve all uncertainties before finalizing the plan. If something is unclear, research or ask the user—don't push uncertainty to implementation.

### Be Skeptical

- Question vague requirements
- Verify with actual code rather than assumptions
- Challenge designs that don't make sense
- Push back on unclear success criteria

### Interactive Approach

Get buy-in at major steps rather than writing full plans upfront:
- Review structure before details
- Present findings before diving deep
- Validate direction collaboratively

### Separate Success Criteria

Distinguish automated verification from manual testing.

## Success Criteria Structure

Plans must include checkboxes for both:

### Automated Verification

Commands that can be run to verify success:
- `make migrate` - Database migrations
- Unit tests passing
- Type checking (`tsc`, `mypy`)
- Linting (`eslint`, `pylint`)
- Build succeeding

These are deterministic, repeatable checks.

### Manual Verification

Testing that requires human judgment:
- UI functionality and user experience
- Performance under load
- Edge cases and error handling
- Integration with other systems
- User acceptance criteria

## Why This Matters for Long-Running Agents

This approach addresses challenges from effective harnesses for long-running agents:

1. **Explicit specifications** (like feature lists) prevent vague implementation
2. **Success criteria checkboxes** provide objective verification
3. **Phased implementation** creates reviewable, mergeable changes
4. **Interactive feedback loops** ensure alignment before big investments
5. **Filesystem-based artifacts** (plans in `thoughts/` directory) persist across sessions

## Key Principles

**Completeness Before Implementation**: Do the hard thinking upfront so implementation is straightforward.

**Skeptical Partnership**: Question vague requirements and verify assumptions with actual code.

**Separated Concerns**: Distinguish research, planning, and implementation into clear phases.

**Objective Verification**: Both automated tests and manual checklists define success.

**Collaborative Iteration**: Build plans through feedback loops, not monolithic documents.
