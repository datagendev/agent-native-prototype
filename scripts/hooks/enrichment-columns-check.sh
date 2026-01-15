#!/bin/bash
# Hook: Blocks full enrichment runs until columns are shown
# Matcher: Bash (only runs for Bash tool calls)
# Triggers on: graph_enrich.py commands without --preview

# Get the command being run
COMMAND=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null)

# Exit silently if no command (shouldn't happen with Bash matcher)
[ -z "$COMMAND" ] && exit 0

# Check if this is a graph_enrich.py command
if ! echo "$COMMAND" | grep -q "graph_enrich.py"; then
    exit 0
fi

# Allow preview runs
if echo "$COMMAND" | grep -q "\-\-preview"; then
    exit 0
fi

# Allow --list and --describe commands
if echo "$COMMAND" | grep -qE "\-\-list|\-\-describe"; then
    exit 0
fi

# This is a full enrichment run - block and remind the model
cat << 'EOF'
BLOCKED: Full enrichment run detected without showing columns first.

Before running full enrichment, you MUST:

1. Show the user what columns will be added:
   ```
   ### Columns Added by This Workflow:
   | New Column | Type | Source Node | Description |
   |------------|------|-------------|-------------|
   | column_name | type | NodeName | What it contains |
   ```

2. Show the pipeline summary:
   ```
   ### Pipeline Summary:
   1. NodeName
      - Reads: input_col1, input_col2
      - Outputs: output_col1, output_col2
      - Method: How it works
   ```

3. Show sample results from preview (if preview was run)

4. Get explicit user confirmation with AskUserQuestion

After showing columns and getting confirmation, you may proceed with full enrichment.
EOF

exit 2  # Block the command
