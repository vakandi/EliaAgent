#!/bin/zsh
# =============================================================================
# DEPRECATED — DO NOT USE
#
# This was an AI-generated 4-window version created on May 2, 2026 that BROKE
# the original 3-pane tmux setup. It introduced start_agents.sh into the
# UI launcher which caused problems.
#
# The correct launcher is EliaUI.command which uses 3 panes:
#   Pane 0: OpenCode server
#   Pane 1: Discord bot
#   Pane 2: UI Electron
#
# Kept only for reference. Delete when no one remembers this existed.
# =============================================================================

# ============================================================
# TMUX INSIDE TMUX GUARD
# If already inside a tmux session, do NOT kill-session or
# attach — that would destroy the parent tmux session.
# ============================================================
if [[ -n "$TMUX" ]]; then
    echo "[GUARD] Already inside tmux session ($TMUX) — skipping elia-ui-4win.sh (deprecated)."
    echo "[GUARD] To attach manually: tmux attach -t elia-dev"
    exit 0
fi

# ============================================================
# STRONG EARLY EXIT — Ce script est deprecated et DANGEREUX.
# Il utilise tmux kill-session qui détruit la session en cours.
# Les seuls launchers autorisés sont:
#   - EliaUI.command (safe, check-then-attach)
#   - elia-ui.sh (safe, client-check avant kill)
# ============================================================
echo "⛔ [DEPRECATED] elia-ui-4win.sh est deprecated et dangereux."
echo "    Utilise EliaUI.command (3 panes) à la place."
echo "    Pour attacher à une session existante: tmux attach -t elia-dev"
exit 1

# Window 1: OpenCode server (opencode-serve.sh)
# Window 2: CodeMem Viewer (codemem-viewer.sh)
# Window 3: Agents (start_agents.sh)  ← WRONG, should not be here
# Window 4: UI (elia-ui.sh)

set -euo pipefail

AGENT_DIR="$HOME/EliaAI"
SCRIPTS_DIR="$AGENT_DIR/scripts"
SESSION="elia-dev"

# Kill any existing tmux session
tmux kill-session -t "$SESSION" 2>/dev/null || true
sleep 1

# Create new tmux session with window 1 (OpenCode server)
echo "Creating tmux session '$SESSION' with 4 windows..."
tmux new-session -d -s "$SESSION" -n "opencode" "bash $SCRIPTS_DIR/opencode-serve.sh 4096"

# Create window 2 (CodeMem Viewer)
tmux new-window -t "$SESSION" -n "codemem" "bash $SCRIPTS_DIR/codemem-viewer.sh"

# Create window 3 (Agents)
tmux new-window -t "$SESSION" -n "agents" "bash $SCRIPTS_DIR/start_agents.sh"

# Create window 4 (UI)
tmux new-window -t "$SESSION" -n "ui" "bash $SCRIPTS_DIR/elia-ui.sh"

# Select first window
tmux select-window -t "$SESSION":1

echo "✅ EliaUI started with 4 tmux windows:"
echo "  Window 1: OpenCode server (opencode-serve.sh)"
echo "  Window 2: CodeMem Viewer (codemem-viewer.sh)"
echo "  Window 3: Agents (start_agents.sh)"
echo "  Window 4: UI (elia-ui.sh)"
echo ""
echo "Attach with: tmux attach -t $SESSION"
echo "Switch windows: Ctrl-b 1, Ctrl-b 2, Ctrl-b 3, Ctrl-b 4"

# Attach to tmux session
tmux attach -t "$SESSION"
