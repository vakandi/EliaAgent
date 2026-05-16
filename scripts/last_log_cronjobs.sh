#!/bin/zsh

# Get the directory where this script is located, then get parent (EliaAI root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${AGENT_DIR}/logs"

echo "=== CRON.LOG (last 30 lines) ==="
tail -30 "${LOG_DIR}/cron.log" 2>/dev/null || echo "No cron.log found"

echo ""
echo "=== LATEST OPENCODE INTERACTIVE LOGS (today) ==="
for log in $(ls -t "${LOG_DIR}"/opencode_interactive_2026*.log 2>/dev/null | head -3); do
    SIZE=$(stat -f%z "$log" 2>/dev/null || stat -c%s "$log" 2>/dev/null)
    echo "--- $log (${SIZE} bytes) ---"
    tail -20 "$log" 2>/dev/null
    echo ""
done

echo "=== RUNNING PROCESSES ==="
ps aux | grep -E "(opencode|oh-my-opencode)" | grep -v grep | head -5

echo ""
echo "=== OPENCODE SERVER STATUS ==="
if nc -z 127.0.0.1 4096 2>/dev/null; then
    echo "✅ Port 4096: OPEN"
else
    echo "❌ Port 4096: CLOSED"
fi

echo ""
echo "=== LOCK FILE ==="
if [[ -f "/tmp/elia_running.lock" ]]; then
    echo "Lock exists: $(cat /tmp/elia_running.lock)"
else
    echo "No lock file"
fi

echo ""
echo "=== MCP SERVERS ==="
ls -la /tmp/elia_mcp_pids/ 2>/dev/null || echo "No MCP PID dir"
