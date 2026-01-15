#!/bin/bash
# Hook: Runs before /enrichment skill
# Injects progress context to help Claude resume enrichment workflows

# Check if this is the enrichment skill by reading CLAUDE_TOOL_INPUT
SKILL=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.skill // empty' 2>/dev/null)

# Exit silently if not enrichment skill
[ "$SKILL" != "enrichment" ] && exit 0

# Find and output any active enrichment progress
found_progress=false
for lead_dir in leads/*/; do
    [ ! -d "$lead_dir" ] && continue

    progress_file="${lead_dir}enrichment-progress.txt"
    node_status="${lead_dir}node-status.json"

    if [ -f "$progress_file" ]; then
        if [ "$found_progress" = false ]; then
            echo "=== Active Enrichment Context ==="
            found_progress=true
        fi

        lead_name=$(basename "$lead_dir")
        echo ""
        echo "## Lead: $lead_name"
        echo "### Progress Log:"
        cat "$progress_file"

        if [ -f "$node_status" ]; then
            echo ""
            echo "### Node Status:"
            cat "$node_status"
        fi
    fi
done

# If progress found, remind Claude of the protocol
if [ "$found_progress" = true ]; then
    echo ""
    echo "---"
    echo "REMINDER: Read progress above before starting. Run validation first."
fi
