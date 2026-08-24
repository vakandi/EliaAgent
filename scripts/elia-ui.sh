#!/bin/zsh

# ============================================================
# TMUX INSIDE TMUX GUARD
# If already inside a tmux session, do NOT kill-session or
# attach — that would destroy the parent tmux session.
# ============================================================
if [[ -n "$TMUX" ]]; then
    echo "[GUARD] Already inside tmux session ($TMUX) — skipping elia-ui.sh."
    echo "[GUARD] To attach manually: tmux attach -t $SESSION"
    exit 0
fi

SESSION="elia-ui"

is_already_opencode_server() {
    local port="${1:-4096}"
    local pid
    pid=$(lsof -ti :"$port" 2>/dev/null | head -1)
    [[ -z "$pid" ]] && return 1
    local process_name
    process_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "")
    [[ "$process_name" == *"opencode"* ]] || return 1
    nc -z 127.0.0.1 "$port" 2>/dev/null
}

# ============================================================
# SKIP CLEANUP if opencode server is already running — don't
# kill the session that the running server depends on.
# ============================================================
if ! is_already_opencode_server 4096; then
    # Only kill tmux session if it has NO active clients (nobody is using it)
    if tmux has-session -t "$SESSION" 2>/dev/null; then
        if tmux list-clients -t "$SESSION" 2>/dev/null | grep -q .; then
            echo "[GUARD] Session '$SESSION' has active clients — not killing."
        else
            tmux kill-session -t "$SESSION" 2>/dev/null || true
        fi
    fi
    lsof -ti:4096 | xargs kill -9 2>/dev/null || true
    pkill -f "npm.*start" 2>/dev/null || true
    pkill -f "electron" 2>/dev/null || true
    pkill -f "bot.py" 2>/dev/null || true
    pkill -f "telegram-opencode-bot" 2>/dev/null || true
    sleep 1
fi

# Only create session if it doesn't already exist — preserves
# an existing "elia" session that's running opencode, etc.
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session -d -s "$SESSION"
    tmux split-window -h -t "$SESSION"
    tmux split-window -h -t "$SESSION"
    tmux select-layout -t "$SESSION" tiled
    sleep 1
    tmux send-keys -t "$SESSION":0.0 "~/EliaAI/scripts/opencode-serve.sh 4096" $'\n'
    sleep 1
    tmux send-keys -t "$SESSION":0.1 "~/EliaAI/scripts/start_elias_discord.sh" $'\n'
    sleep 1
    tmux send-keys -t "$SESSION":0.2 "cd ~/EliaAI/ui_electron && npm start" $'\n'
fi

tmux attach -t "$SESSION"