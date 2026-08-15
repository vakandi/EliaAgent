#!/bin/zsh

# ============================================================
# SCHEDULER DISABLE GUARD
# If .scheduler_disabled exists, exit immediately without running.
# Create this file to permanently disable all scheduled/interactive agent runs:
#   touch ~/EliaAI/.scheduler_disabled
# ============================================================
if [[ -f "$HOME/EliaAI/.scheduler_disabled" ]]; then
    echo "[GUARD] .scheduler_disabled found — agent disabled. Exiting."
    exit 0
fi

AGENT_DIR="$HOME/EliaAI"
PROXY_CONF="$HOME/.proxychains.conf"
PORT=4096

export PATH="$HOME/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

cd "$AGENT_DIR"

PROXY_HTTP=""
PROXY_HTTPS=""

if [[ -f "$AGENT_DIR/.proxy_enabled" ]] && [[ -f "$PROXY_CONF" ]]; then
    PROXY_LINE=$(grep -v "^#" "$PROXY_CONF" | grep "http " | head -1)
    if [[ -n "$PROXY_LINE" ]]; then
        ip=$(echo "$PROXY_LINE" | awk '{print $2}')
        port_proxy=$(echo "$PROXY_LINE" | awk '{print $3}')
        user=$(echo "$PROXY_LINE" | awk '{print $4}')
        pass=$(echo "$PROXY_LINE" | awk '{print $5}')
        PROXY_HTTP="http://${user}:${pass}@${ip}:${port_proxy}"
        PROXY_HTTPS="http://${user}:${pass}@${ip}:${port_proxy}"
        echo "[PROXY] Loaded proxy: $ip:$port_proxy (HTTP_PROXY env vars ready)"
    fi
fi

echo "[SERVER] Starting on port $PORT..."
if [[ -n "$PROXY_HTTP" ]]; then
    env HTTP_PROXY="$PROXY_HTTP" HTTPS_PROXY="$PROXY_HTTPS" http_proxy="$PROXY_HTTP" https_proxy="$PROXY_HTTPS" /Users/vakandi/.opencode/bin/opencode serve --port $PORT &
else
    /Users/vakandi/.opencode/bin/opencode serve --port $PORT &
fi
echo "Server started"