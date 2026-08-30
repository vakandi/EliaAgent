#!/bin/bash
osascript -e '
tell application "Terminal"
    activate
    do script "export PATH=\"/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH\"; echo \"[SubWorkerKill] Running...\"; zsh ~/EliaAI/subworkers/kill_subwokers_dockers.sh; echo \"[SubWorkerKill] Restarting server...\"; cd ~/EliaAI/subworkers/server && /opt/homebrew/bin/docker-compose up -d 2>/dev/null || docker compose up -d 2>/dev/null || true; sleep 2; docker ps 2>/dev/null | grep elia-subworker-srv || echo \"Check docker\"; echo \"[SubWorkerKill] Done - window stays open\"; exec zsh"
end tell
' &>/dev/null &
# Also run directly for non-GUI fallback
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
zsh ~/EliaAI/subworkers/kill_subwokers_dockers.sh 2>&1 | tail -5
cd ~/EliaAI/subworkers/server && /opt/homebrew/bin/docker-compose up -d 2>/dev/null || docker compose up -d 2>/dev/null || true
