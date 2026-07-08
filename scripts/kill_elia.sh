#!/bin/zsh
PORT="${1:-4096}"

is_already_opencode_server() {
    local pid
    pid=$(lsof -ti :"$PORT" 2>/dev/null | head -1)
    [[ -z "$pid" ]] && return 1

    local process_name
    process_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "")
    [[ "$process_name" == *"opencode"* ]] || return 1

    if nc -z 127.0.0.1 "$PORT" 2>/dev/null; then
        echo "[kill_elia] Found existing opencode server on port $PORT (PID: $pid) — skipping kill" >&2
        return 0
    fi

    return 1
}

# ============================================================
# TMUX INSIDE TMUX GUARD
# If already inside a tmux session (e.g. opencode's pane),
# do NOT kill-session — that would kill the parent session.
# ============================================================
if [[ -n "$TMUX" ]]; then
    echo "[GUARD] Already inside tmux session ($TMUX) — skipping kill_elia."
    exit 0
fi

if ! is_already_opencode_server; then
    lsof -ti:"$PORT" | xargs kill -9 2>/dev/null || true
    # Only kill tmux session if it has NO active clients (nobody is using it)
    if tmux has-session -t elia 2>/dev/null; then
        if tmux list-clients -t elia 2>/dev/null | grep -q .; then
            echo "[GUARD] Session 'elia' has active clients — not killing." >&2
        else
            tmux kill-session -t elia 2>/dev/null || true
        fi
    fi
fi

pkill -f "npm.*start" 2>/dev/null || true
pkill -f "electron" 2>/dev/null || true
pkill -f "bot.py" 2>/dev/null || true
pkill -f "telegram-opencode-bot" 2>/dev/null || true
pkill -f "node.*EliaAI" 2>/dev/null || true
sleep 1