#!/bin/zsh
# Install LaunchAgent for persistent Playwright MCP server (port 8931).
# Keeps browser context alive for mcp-cli so navigate → snapshot → click work in one session.

set -euo pipefail

AGENT_DIR="/Users/$(whoami)/EliaAI"
LABEL="com.elia.playwright-mcp"
PLIST="${AGENT_DIR}/com.elia.playwright-mcp.plist"
DEST="${HOME}/Library/LaunchAgents/${LABEL}.plist"

echo "=== Playwright MCP LaunchAgent Installer ==="
echo ""

[[ ! -f "$PLIST" ]] && { echo "ERROR: $PLIST not found"; exit 1; }
mkdir -p "$(dirname "$DEST")"
mkdir -p "${AGENT_DIR}/logs"

launchctl unload "$DEST" 2>/dev/null || true
cp "$PLIST" "$DEST"
chmod 644 "$DEST"
launchctl load "$DEST"

if launchctl list | grep -q "$LABEL"; then
    echo "Playwright MCP LaunchAgent loaded. Server: http://localhost:8931/mcp"
    echo "Logs: tail -f ${AGENT_DIR}/logs/playwright-mcp.log"
    echo "Unload: launchctl unload $DEST"
else
    echo "Warning: launchctl list did not show $LABEL"
fi
echo "Done."
