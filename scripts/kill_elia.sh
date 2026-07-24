#!/bin/zsh
# =============================================================================
# kill_elia.sh — Clean up EliaAI processes and tmux session
#
# Session name: elia-ui (matches EliaUI.command)
# Previous bug: targeted "elia" which collided with opencode sessions
# =============================================================================

PORT="${1:-4096}"
SESSION="elia-ui"

is_already_opencode_server() {
    local pid
    pid=$(lsof -ti :"$PORT" 2>/dev/null | head -1)
    [[ -z "$pid" ]] && return 1

    local process_name
    process_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "")
    # Accept "opencode" binary OR "node" process (opencode runs on Node.js)
    [[ "$process_name" == *"opencode"* ]] || [[ "$process_name" == "node" ]] || return 1

    echo "[kill_elia] Found existing opencode server on port $PORT (PID: $pid) — skipping kill" >&2
    return 0
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
    echo "[kill_elia] No active opencode server on port $PORT — cleaning up." >&2

    # Kill whatever is holding the port
    lsof -ti:"$PORT" | xargs kill -9 2>/dev/null || true

    # Only kill tmux session if it has NO active clients (nobody is using it)
    if tmux has-session -t "$SESSION" 2>/dev/null; then
        if tmux list-clients -t "$SESSION" 2>/dev/null | grep -q .; then
            echo "[GUARD] Session '$SESSION' has active clients — not killing." >&2
        else
            echo "[kill_elia] Killing idle tmux session '$SESSION'" >&2
            tmux kill-session -t "$SESSION" 2>/dev/null || true
        fi
    fi

    # Kill EliaAI-specific child processes (scoped, not system-wide)
    pkill -f "opencode-serve.sh" 2>/dev/null || true
    pkill -f "start_elias_discord.sh" 2>/dev/null || true
    sleep 1
else
    echo "[kill_elia] Active opencode server detected on port $PORT — preserving." >&2
fi