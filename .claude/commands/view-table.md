---
description: View enriched CSV data in interactive web viewer
---

# View Table Command

Launch the interactive table viewer for enriched lead data.

## Steps to follow:

1. **Find available port** (starting from 3001)
   ```bash
   PORT=3001; while lsof -i :$PORT >/dev/null 2>&1; do ((PORT++)); done; echo $PORT
   ```

2. **Start server on available port**
   ```bash
   ~/.bun/bin/bun scripts/viewer/server.ts --port $PORT &
   ```

3. **Wait briefly and open browser**
   ```bash
   sleep 1 && open http://localhost:$PORT
   ```

4. **Open browser window for user**
   ```bash
   open http://localhost:$PORT
   ```
   Always use `open` to pop the browser window automatically.

5. **Confirm to user**
   - Server running at http://localhost:{PORT}
   - To stop: `lsof -ti:{PORT} | xargs kill`

## One-liner (preferred)

```bash
PORT=3001; while lsof -i :$PORT >/dev/null 2>&1; do ((PORT++)); done; ~/.bun/bin/bun scripts/viewer/server.ts --port $PORT & sleep 1 && open http://localhost:$PORT
```

## Data Sources

The viewer scans:
- `lead-list/` - CSV files
- `leads/` - SQLite databases (shows as "name (SQLite)")
