---
title: "Claude Code Custom Workflows - Evaluator-Optimizer Pattern"
description: "Using Claude Code as orchestrator with sub-agents and slash commands for quality-controlled content generation"
category: "use-cases"
tags: ["claude-code", "subagents", "content", "quality-control"]
created: 2025-01-27
updated: 2025-01-27
status: "active"
priority: "medium"
author: "Elvis S. (Omar Saravia)"
reference: ["https://www.linkedin.com/posts/omarsar_claude-code-is-more-than-a-coding-agent-activity-7355365816118177792-e0sX"]
---

# Claude Code Custom Workflows - Evaluator-Optimizer Pattern

**Author:** Elvis S. (Omar Saravia)

## Key Insight

Claude Code is more than a coding agent - it can orchestrate sub-agents and slash commands for custom agentic workflows.

## Evaluator-Optimizer Loop

A two-agent system for quality-controlled content generation:

1. **Generator Agent** - Creates content (e.g., social media posts)
2. **Evaluator Agent** - Scores against rubric criteria
3. **Loop** - Iterate until quality threshold met (90+ score)

### Example Workflow

Generate "spicy, engaging, technical" posts from URLs:
- Constrained to 200-300 words
- Platform-specific (X, LinkedIn)
- Iterative refinement based on evaluation scores

## Critical Optimization Insights

### Token Efficiency
> "The system likes to use a lot of tokens and perform unnecessary tasks/tool calls."

Mitigations:
- Careful cost management
- Credits can max out quickly without optimization

### LLM-as-a-Judge Limitations
- Evaluator agents introduce inherent biases
- Take shortcuts in evaluation
- Orchestration logic belongs in slash commands, not agent instructions

### Slash Commands as Controllers
- Enforce workflow structure
- Set iteration limits
- Handle conditional logic across nested agents
- More reliable than autonomous decision-making

## Experimental Agents Mentioned

- **Context Compressor** - Reduces costs and latency through custom compression
- **Mock-Data Generator** - Accelerates sub-agent experimentation and testing

## Key Takeaway

Control sub-agent communication patterns:
- Chain
- Loop
- Hierarchical
- Critic (evaluator-optimizer)
