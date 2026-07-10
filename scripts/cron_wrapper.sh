#!/bin/zsh

set -euo pipefail

# Get the directory where this script is located, then get parent (EliaAI root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "${AGENT_DIR}/.scheduler_disabled" ]]; then
    echo "[$(date)] Scheduler DISABLED - exiting"
    exit 0
fi
export HOME="$(eval echo ~$(whoami))"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
export PATH="$HOME/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin:$HOME/.npm-global/bin:$HOME/.nvm/versions/node/v20.20.2/bin:$PATH"

source ~/.zshrc 2>/dev/null || true

# Mark this as a cron run (used by trigger_opencode_interactive.sh for lock mechanism)
export ELIA_CRON=1

# CRITICAL: Ensure localhost/127.0.0.1 bypasses the proxy
# Without this, Node.js fetch() routes 127.0.0.1 through the proxy (Webshare) which returns 403.
# The codemem plugin, MCP servers, and other local services need direct access.
export NO_PROXY="127.0.0.1,localhost,::1"
export no_proxy="127.0.0.1,localhost,::1"

if [[ -f "${AGENT_DIR}/.proxy_enabled" ]]; then
    echo "[$(date)] Proxy enabled - refreshing proxy..."
    bash "${AGENT_DIR}/setup/switch-proxy.sh"
    echo "[$(date)] Proxy refreshed - using proxychains4"
else
    echo "[$(date)] Proxy disabled - using direct connection"
fi

# Timeout after 25 minutes (safety measure for cron runs)
TIMEOUT_SECS=1500

# Proxychains4 is used inside trigger_opencode_interactive.sh if .proxy_enabled exists
exec timeout $TIMEOUT_SECS /bin/zsh "${AGENT_DIR}/scripts/trigger_opencode_interactive.sh"
