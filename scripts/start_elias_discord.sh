#!/bin/zsh
# Start EliaAI Discord bot

set -euo pipefail

AGENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BOT_DIR="${AGENT_DIR}/integrations/elia-discord-bot"
PROXY_CONF="$HOME/.proxychains.conf"

if [[ ! -d "$BOT_DIR" ]]; then
    echo "elia-discord-bot not found at: $BOT_DIR"
    exit 1
fi

# Load proxy from proxychains.conf for HTTP_PROXY env vars
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

for env in "${BOT_DIR}/.env" "${AGENT_DIR}/.env"; do
    if [[ -f "$env" ]]; then
        cd "$BOT_DIR"
        
        if [[ ! -d "venv" ]]; then
            echo "Creating venv..."
            python3 -m venv venv
        fi
        
        source venv/bin/activate
        
        if ! python -c "import discord" 2>/dev/null; then
            echo "Installing dependencies..."
            pip install -r requirements.txt
        fi
        
        echo "Starting EliaDiscord bot..."
        mkdir -p "${BOT_DIR}/logs"
        if [[ -n "$PROXY_HTTP" ]]; then
            env HTTP_PROXY="$PROXY_HTTP" HTTPS_PROXY="$PROXY_HTTPS" http_proxy="$PROXY_HTTP" https_proxy="$PROXY_HTTPS" python bot.py
        else
            python bot.py
        fi
        exit 0
    fi
done

echo "No .env found."
exit 1