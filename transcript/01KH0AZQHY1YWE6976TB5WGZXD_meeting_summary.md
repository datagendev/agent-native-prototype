## Work Meeting Summary: HubSpot Reporting & Agent Development

**Date:** February 9, 2026
**Participants:** Jeremy Ross, Yusheng Kuo (yuehlin@datagen.dev)
**Duration:** 120 minutes

### Key Discussion Points

- Setting up DataGen SDK and Claude Code environment for HubSpot integration
- Building an automated sales rep reporting system using HubSpot API
- Creating baseline reports (8 reports covering deals, engagements, revivals)
- Developing priority outreach recommendations based on deal analysis
- Discussion of agent deployment strategies (local scripts vs. custom tools vs. skills)
- Context window management using tmp folder pattern for intermediate data storage
- Claude Code capabilities and product direction

### TODO Items

| Owner | Task | Priority | Context |
|-------|------|----------|---------|
| Jeremy | Restart Claude Code to get version 4.6 | Low | Currently running 4.5, needs upgrade |
| Yusheng | Develop agent from the baseline report process | High | Use the baseline_report.md as spec for agent creation |
| Jeremy | Document the HubSpot reporting workflow | Medium | Continue iterating on the report generation process |
| Jeremy | Test final report with real sales team feedback | High | Validate that priority outreach recommendations are actionable |
| Yusheng | Show Jeremy the compound engineering article | Medium | For understanding agent development patterns |
| Team | Deploy HubSpot reporting as agent or custom tool | Medium | Decision needed on deployment approach after baseline is validated |

### Decisions Made

- **Local development first**: Use .env file locally for faster iteration before deploying to DataGen
- **Temporary folder pattern**: Save intermediate data to /tmp to avoid context window cramping
- **Baseline then insights**: Generate factual reports first, then add AI reasoning layer to analyze conversations
- **Focus on open deals**: Prioritize actionable insights for sales reps rather than retrospective analysis of lost deals
- **Agent reasoning approach**: Combine scripts for efficient data population with Claude Code reading files recursively for insights generation
- **Git ignore setup**: Added .env and .venv to .gitignore for security

### Technical Setup Completed

- Installed DataGen Python SDK in project
- Created .env file with HubSpot API key (gitignored)
- Connected to HubSpot API successfully
- Established tmp folder pattern for data storage
- Generated 8 baseline reports for sales rep (James)
- Created priority outreach report with company research

### Next Steps

1. Refine priority outreach recommendations based on email content analysis
2. Add time-based filtering for deal prioritization
3. Convert the workflow into a reusable agent/skill
4. Test with multiple sales reps (8 AEs total)
5. Integrate company research using Perplexity MCP
