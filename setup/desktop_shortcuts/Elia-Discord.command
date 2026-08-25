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

osascript -e '
tell application "Terminal"
    activate
    do script "cd /Users/vakandi/EliaAI && ./scripts/start_elias_discord.sh"
end tell
'