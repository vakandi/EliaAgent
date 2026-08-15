#!/bin/zsh
# EliaUI — Open tmux session with Elia services
# opencode serve runs in its own session for crash isolation
# Discord bot + Electron UI run in elia-ui session

SESSION="elia-ui"
SERVER_SESSION="opencode-serve"

# Track whether we're inside tmux (for attachment decision only)
INSIDE_TMUX=false
if [[ -n "$TMUX" ]]; then
    INSIDE_TMUX=true
    echo "[EliaUI] Already inside tmux session ($TMUX) — will create sessions but skip attach."
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

# Start opencode server in its own isolated session (crash-safe)
# Skip if an opencode server is already running on port 4096
if ! tmux has-session -t "$SERVER_SESSION" 2>/dev/null; then
    if ! is_already_opencode_server 4096; then
        echo "[EliaUI] Starting opencode server in dedicated session '$SERVER_SESSION'..."
        tmux new-session -d -s "$SERVER_SESSION" -n "Server"
        tmux send-keys -t "$SERVER_SESSION" "cd ~/EliaAI && ./scripts/opencode-serve.sh 4096" Enter
        sleep 2
    fi
fi

# Create elia-ui session only if it doesn't exist
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session -d -s "$SESSION" -n "EliaAI"

    # Split into 2 panes: Discord bot (top) + Electron UI (bottom)
    # Pane 0: Discord bot
    # Pane 1: Electron UI
    tmux split-window -v -t "$SESSION":0
    sleep 1

    # Start Discord bot in pane 0 (top)
    tmux send-keys -t "$SESSION":0.0 "cd ~/EliaAI && ./scripts/start_elias_discord.sh" Enter

    sleep 1

    # Start Electron UI in pane 1 (bottom)
    tmux send-keys -t "$SESSION":0.1 "cd ~/EliaAI/ui_electron && npm start" Enter
fi

# Attach only if NOT already inside tmux (attaching from inside tmux replaces the current shell)
if [[ "$INSIDE_TMUX" == "false" ]]; then
    TMUX= tmux new-session -A -s "$SESSION"
else
    echo "[EliaUI] Sessions are ready. Attach manually: tmux attach -t $SESSION"
fi
