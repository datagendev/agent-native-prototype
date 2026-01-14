---
title: "Effective Harnesses for Long-Running Agents"
description: "Anthropic's strategies for enabling Claude to make consistent progress across multiple context windows"
category: "research"
tags: ["agents", "harness", "long-running", "context-windows", "anthropic"]
research-type: "agent-architecture"
created: 2026-01-14
updated: 2026-01-14
status: "active"
priority: "high"
reference: ["https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents"]
---

# Effective Harnesses for Long-Running Agents

**Source:** Anthropic Research

## Overview

Anthropic researchers developed strategies to enable Claude to make consistent progress across multiple context windows—a challenge because agents work in discrete sessions without memory of previous work.

## Core Problem

"Each new session begins with no memory of what came before." This forces agents to repeatedly figure out project status, often leading to incomplete features and wasted effort.

The fundamental challenge: agents lose context between sessions and must reconstruct their understanding of what's been done and what remains.

## Two-Part Solution

### Initializer Agent (First Session)

The initializer sets up infrastructure for subsequent agent work:

- Creates `init.sh` script to run the development server
- Generates `claude-progress.txt` tracking file
- Establishes initial git repository with baseline commit

This creates a stable foundation that subsequent agents can build upon.

### Coding Agent (Subsequent Sessions)

The coding agent picks up where initialization left off:

- Works on one feature at a time
- Makes incremental progress with clean, mergeable code
- Uses git commits and progress updates to communicate state
- Reviews existing progress to understand what's already done

## Key Environmental Components

### Feature List

A JSON file with 200+ detailed end-to-end feature descriptions, all initially marked as failing. This prevents premature project completion and gives agents a clear roadmap of work.

The feature list is critical because it:
- Provides explicit, verifiable success criteria
- Prevents agents from declaring work complete when it's not
- Guides agent decision-making about what to work on next

### Version Control

Git history allows agents to:
- Identify recent work and understand project trajectory
- Recover from mistakes by reverting bad changes
- Communicate state through clean, atomic commits
- Provide context for reviewing what's been implemented

### Testing Infrastructure

Browser automation tools (Puppeteer) enable:
- End-to-end verification that features actually work, not just that code exists
- Automated testing of functionality across sessions
- Detection of regressions introduced by new changes

## Typical Session Pattern

Agents start each session by:

1. Running `pwd` to confirm working directory
2. Reading progress files and git logs to understand context
3. Reviewing feature requirements and existing implementation
4. Running basic functionality tests to verify current state
5. Implementing one new feature incrementally

This pattern ensures agents can reconstruct context efficiently at the start of each session.

## Key Insights

### State is Filesystem-Based

The agent's state (progress, features, test results) lives in the filesystem, not in prompt engineering. This allows:
- State to persist across sessions without being in context
- Easy access via file operations rather than elaborate prompting
- Clear, inspectable representation of what the agent knows

### Features Drive Progress

Explicit feature lists prevent agents from:
- Declaring work done prematurely
- Getting confused about success criteria
- Repeating work across sessions

A well-designed feature list acts as a contract between sessions.

### Testing is Essential

Automated testing provides:
- Objective verification of progress
- Early detection of issues
- Confidence that features work, not just that they're coded

## Remaining Challenges

- Browser automation limitations (can't detect native alert modals)
- Unclear whether single agents outperform multi-agent architectures for extended work
- Solutions currently optimized for web development; applicability to other domains unclear
- Determining optimal feature granularity and testing strategy

## Implications for Agent Design

This work suggests effective long-running agents need:

1. **Clear environmental structure**: Filesystem-based state, git history, feature lists
2. **Explicit success criteria**: Features with pass/fail status, automated tests
3. **Session boundaries acknowledgment**: Assume no context carryover; force reconstruction
4. **Incremental progress**: Small, reviewable changes that can be integrated across sessions
5. **Memory externalization**: Everything important lives outside the context window
