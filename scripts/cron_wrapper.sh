#!/bin/zsh

set -euo pipefail

# Get the directory where this script is located, then get parent (EliaAI root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
export HOME="$(eval echo ~$(whoami))"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
export PATH="$HOME/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin:$HOME/.npm-global/bin:$HOME/.nvm/versions/node/v20.20.2/bin:$PATH"

source /Users/vakandi/.zshrc 2>/dev/null || true

# Mark this as a cron run (used by trigger_opencode_interactive.sh for lock mechanism)
export ELIA_CRON=1

if [[ -f "${AGENT_DIR}/.proxy_enabled" ]]; then
    export USE_PROXY=1
    echo "[$(date)] Proxy enabled (HTTPS_PROXY env var - no proxychains4)"
else
    export USE_PROXY=0
    echo "[$(date)] Proxy disabled"
fi

# Timeout after 25 minutes (safety measure for cron runs)
TIMEOUT_SECS=1500

exec timeout $TIMEOUT_SECS /bin/zsh "${AGENT_DIR}/scripts/trigger_opencode_interactive.sh"
