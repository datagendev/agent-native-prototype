---
description: View enriched CSV data in interactive web viewer
---

# View Table Command

You are helping the user view their enriched CSV data in a modern interactive web viewer.

## Steps to follow:

1. **Check if server is already running**
   - Check if port 3001 is in use: `lsof -i :3001`
   - If running:
     - Show the user: ✅ Server running at http://localhost:3001
     - Ask if they want to open it or restart.

2. **Start server if needed**
   - Navigate to `scripts/viewer/`
   - Kill old server if restarting: `lsof -ti:3001 | xargs kill -9`
   - Start server: `~/.bun/bin/bun server.ts --port 3001`
   - Run in background (`&`) and capture PID.

3. **Confirm success**
   - Show the user:
     - ✅ Server running at http://localhost:3001
     - 📊 Dashboard: Select a file to view
     - 💡 To stop: `lsof -ti:3001 | xargs kill`
   - Open the URL for the user: `open http://localhost:3001` (if on Mac)

## Error handling:

- If server fails to start → check logs
- If port is blocked → suggest different port or kill process

## Example interaction:

```
User: /view-table
Agent: Checking server status...
Agent: Starting viewer server...
Agent: ✅ Server running at http://localhost:3001
Agent: Opening dashboard...
```
