#!/bin/bash
# Hook: Runs before Task tool spawns a subagent
# Injects context for enrichment-node-creator subagent

# Check if this is an enrichment-node-creator subagent
SUBAGENT=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.subagent_type // empty' 2>/dev/null)

# Exit silently if not enrichment-node-creator
[ "$SUBAGENT" != "enrichment-node-creator" ] && exit 0

echo "=== Node Creation Context ==="

# Show existing node types for reference
echo ""
echo "### Existing Node Implementations:"
for node_file in leads/*/graph/nodes/*.py; do
    [ -f "$node_file" ] && echo "  - $node_file"
done 2>/dev/null | head -15

# Show node_types.yaml locations
echo ""
echo "### Node Type Definitions:"
for types_file in leads/*/graph/node_types.yaml; do
    [ -f "$types_file" ] && echo "  - $types_file"
done 2>/dev/null

# Remind about one-node-per-delegation rule
echo ""
echo "---"
echo "REMINDER: Create ONE node at a time. Verify before creating next."
