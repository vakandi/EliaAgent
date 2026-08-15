#!/bin/zsh
# Elia UI launcher — Discord bot + Electron UI
# opencode serve runs in its own session for crash isolation

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

SESSION="elia-ui"
SERVER_SESSION="opencode-serve"

# Track whether we're inside tmux (for attachment decision only)
INSIDE_TMUX=false
if [[ -n "$TMUX" ]]; then
    INSIDE_TMUX=true
    echo "[elia-ui] Already inside tmux session ($TMUX) — will create sessions but skip attach."
fi

is_already_opencode_server() {
    local port="${1:-4096}"
    local pid
    pid=$(lsof -ti :"$port" 2>/dev/null | head -1)
    [[ -z "$pid" ]] && return 1
    local process_name
    process_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "")
    # Accept "opencode" binary OR "node" process (opencode runs on Node.js)
    # NOTE: macOS `ps -o comm=` returns the FULL PATH for node, so match substring.
    [[ "$process_name" == *"opencode"* ]] || [[ "$process_name" == *"node"* ]] || return 1
    return 0
}

# Start opencode server in its own isolated session
# This prevents agent session kills from cascading to the server
if ! tmux has-session -t "$SERVER_SESSION" 2>/dev/null; then
    if ! is_already_opencode_server 4096; then
        echo "[elia-ui] Starting opencode server in dedicated session '$SERVER_SESSION'..."
        tmux new-session -d -s "$SERVER_SESSION" -n "Server"
        tmux send-keys -t "$SERVER_SESSION" "~/EliaAI/scripts/opencode-serve.sh 4096" Enter
        sleep 2
    fi
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
    if [[ "$INSIDE_TMUX" == "true" ]]; then
        echo "[GUARD] Running inside tmux — not killing session '$SESSION'."
    elif tmux list-clients -t "$SESSION" 2>/dev/null | grep -q .; then
        echo "[GUARD] Session '$SESSION' has active clients — not killing."
    else
        # Check if any pane has child processes (running commands like discord bot, electron, opencode)
        _has_live=false
        for _pid in $(tmux list-panes -t "$SESSION" -F '#{pane_pid}' 2>/dev/null); do
            if pgrep -P "$_pid" > /dev/null 2>&1; then
                _has_live=true
                break
            fi
        done
        if [[ "$_has_live" == "true" ]]; then
            echo "[GUARD] Session '$SESSION' has running processes — skipping cleanup."
        else
            echo "[CLEANUP] Session '$SESSION' exists with no clients or processes — killing stale session."
            tmux kill-session -t "$SESSION" 2>/dev/null || true
        fi
    fi
fi

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session -d -s "$SESSION" -n "EliaAI"
    tmux split-window -v -t "$SESSION":0
    sleep 1
    tmux send-keys -t "$SESSION":0.0 "~/EliaAI/scripts/start_elias_discord.sh" Enter
    sleep 1
    tmux send-keys -t "$SESSION":0.1 "cd ~/EliaAI/ui_electron && npm start" Enter
fi

if [[ "$INSIDE_TMUX" == "false" ]]; then
    TMUX= tmux new-session -A -s "$SESSION"
else
    echo "[elia-ui] Sessions are ready. Attach manually: tmux attach -t $SESSION"
fi