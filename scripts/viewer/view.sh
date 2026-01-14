#!/bin/bash
# View Enrichment Data - Interactive viewer launcher
#
# Usage: ./view.sh [--port PORT]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEAD_LIST_DIR="$SCRIPT_DIR/../../lead-list"
PORT="${1:-3001}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

echo ""
echo "📊 Enrichment Data Viewer"
echo "========================="
echo ""

# Find all enriched CSV files
ENRICHED_FILES=($(find "$LEAD_LIST_DIR" -name "*_enriched.csv" -type f | sort -r))

if [ ${#ENRICHED_FILES[@]} -eq 0 ]; then
    echo "❌ No enriched CSV files found in $LEAD_LIST_DIR"
    echo ""
    echo "Run batch enrichment first:"
    echo "  python scripts/batch_enrich.py --input lead-list/file.csv --integrations linkedin_profile"
    exit 1
fi

# Display files with numbers
echo "Available enriched files:"
echo ""
for i in "${!ENRICHED_FILES[@]}"; do
    file="${ENRICHED_FILES[$i]}"
    basename=$(basename "$file")
    size=$(du -h "$file" | cut -f1)
    modified=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file" 2>/dev/null || stat -c "%y" "$file" 2>/dev/null | cut -d' ' -f1,2 | cut -d':' -f1-2)
    echo "  [$((i+1))] $basename"
    echo "      Size: $size, Modified: $modified"
done

echo ""
read -p "Select file (1-${#ENRICHED_FILES[@]}): " selection

# Validate selection
if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#ENRICHED_FILES[@]} ]; then
    echo "❌ Invalid selection"
    exit 1
fi

SELECTED_FILE="${ENRICHED_FILES[$((selection-1))]}"
echo ""
echo "✓ Selected: $(basename "$SELECTED_FILE")"
echo ""

# Check if server is already running
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Server already running on port $PORT"
    read -p "Kill existing server and restart? (y/N): " kill_server
    echo ""

    if [[ "$kill_server" =~ ^[Yy]$ ]]; then
        echo "🔄 Stopping existing server..."
        lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        echo "📊 Using existing server at http://localhost:$PORT"
        echo ""
        open "http://localhost:$PORT" 2>/dev/null || echo "Open: http://localhost:$PORT"
        exit 0
    fi
fi

# Start server in background
echo "🚀 Starting server on port $PORT..."
echo ""

cd "$SCRIPT_DIR"
~/.bun/bin/bun server.ts --file "$SELECTED_FILE" --port "$PORT" > /tmp/enrichment-viewer-$PORT.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Check if server started successfully
if ! lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "❌ Failed to start server. Check logs:"
    cat /tmp/enrichment-viewer-$PORT.log
    exit 1
fi

echo "✅ Server started successfully!"
echo ""
echo "📊 Viewing: $(basename "$SELECTED_FILE")"
echo "🔗 URL: http://localhost:$PORT"
echo "📋 PID: $SERVER_PID"
echo "📝 Logs: /tmp/enrichment-viewer-$PORT.log"
echo ""
echo "💡 To stop: lsof -ti:$PORT | xargs kill"
echo ""

# Open browser
open "http://localhost:$PORT" 2>/dev/null || true

echo "✨ Done!"
