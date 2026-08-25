#!/bin/zsh
# start_subworkers.sh — start the full subworker stack in tmux.
# Same proven flow as ~/Desktop/EliaUI.command:
#   session "opencode-serve" : OpenCode server (port 4096), crash-isolated
#   session "elia-ui"        : 3 panels — Docker subworker logs / Discord bot / Electron UI
#
# The Docker container is persistent: killing this launcher does NOT stop it.

SESSION="elia-ui"
SERVER_SESSION="opencode-serve"
SUBWORKER_HEALTH_URL="http://localhost:5656/health"

ELIA_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

INSIDE_TMUX=false
if [[ -n "$TMUX" ]]; then
    INSIDE_TMUX=true
    echo "[subworkers] Already inside tmux — will create sessions but skip attach."
fi

is_already_opencode_server() {
    local port="${1:-4096}"
    local pid
    pid=$(lsof -ti :"$port" 2>/dev/null | head -1)
    [[ -z "$pid" ]] && return 1
    local process_name
    process_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "")
    [[ "$process_name" == *"opencode"* ]] || [[ "$process_name" == *"node"* ]] || return 1
    return 0
}

is_subworker_server_healthy() {
    local health_resp
    health_resp=$(curl -sf --max-time 3 "$SUBWORKER_HEALTH_URL" 2>/dev/null) || return 1
    [[ "$health_resp" == *'"status":"ok"'* ]]
}

# ── 1. Start opencode server (isolated session, crash-safe) ──────────────
if ! tmux has-session -t "$SERVER_SESSION" 2>/dev/null; then
    if ! is_already_opencode_server 4096; then
        echo "[subworkers] Starting opencode server in '$SERVER_SESSION'..."
        tmux new-session -d -s "$SERVER_SESSION" -n "Server"
        tmux send-keys -t "$SERVER_SESSION" "cd $ELIA_ROOT && ./scripts/opencode-serve.sh 4096" Enter
        sleep 2
    fi
fi

# ── 2. Ensure Docker daemon (Colima) is running ─────────────────────────
if ! docker info >/dev/null 2>&1; then
    echo "[subworkers] Docker daemon not reachable — starting Colima..."
    colima start --runtime docker 2>&1 | tail -3
    sleep 3
    if ! docker info >/dev/null 2>&1; then
        echo "[subworkers] FATAL: Docker daemon still not reachable after colima start"
        exit 1
    fi
fi

# ── 3. Build container image if missing ─────────────────────────────────
if ! docker images --format '{{.Repository}}' | grep -q "server-subworker-srv"; then
    echo "[subworkers] First run — building subworker server image..."
    (cd "$ELIA_ROOT/subworkers/server" && docker-compose build)
fi

# ── 4. Ensure the subworker server container is up ───────────────────────
if ! is_subworker_server_healthy; then
    echo "[subworkers] Starting elia-subworker-srv container..."
    (cd "$ELIA_ROOT/subworkers/server" && docker-compose up -d)
    sleep 3
fi

# ── 5. Create 3-panel tmux layout ────────────────────────────────────────
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session -d -s "$SESSION" -n "EliaAI"
    tmux set-option -t "$SESSION" mouse on
    tmux set-option -t "$SESSION" mode-keys vi
    tmux set-option -s -t "$SESSION" copy-command "pbcopy"
    tmux bind-key -T copy-mode-vi MouseDrag1Pane select-pane \; send -X begin-selection
    tmux bind-key -T copy-mode-vi MouseDragEnd1Pane send -X copy-pipe-and-cancel "pbcopy"

    # Pane 0 (top): Docker subworker logs
    tmux send-keys -t "$SESSION":0.0 "cd $ELIA_ROOT && ./scripts/docker_subworker.sh" Enter
    sleep 1

    # Pane 1 (middle): Discord bot
    tmux split-window -v -t "$SESSION":0.0
    sleep 1
    tmux send-keys -t "$SESSION":0.1 "cd $ELIA_ROOT && ./scripts/start_elias_discord.sh" Enter
    sleep 1

    # Pane 2 (bottom): Electron UI
    tmux split-window -v -t "$SESSION":0.1
    sleep 1
    tmux send-keys -t "$SESSION":0.2 "cd $ELIA_ROOT/ui_electron && npm start" Enter

    # Resize: Docker logs gets 35%, Discord 35%, Electron 30%
    tmux resize-pane -t "$SESSION":0.0 -y 35%
    tmux resize-pane -t "$SESSION":0.1 -y 35%

    # Select the Docker logs pane first
    tmux select-pane -t "$SESSION":0.0
fi

# ── 6. Attach ────────────────────────────────────────────────────────────
if [[ "$INSIDE_TMUX" == "false" ]]; then
    TMUX= tmux new-session -A -s "$SESSION"
else
    echo "[subworkers] Sessions ready. Attach: tmux attach -t $SESSION"
fi
