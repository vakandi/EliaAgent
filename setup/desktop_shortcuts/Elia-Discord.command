osascript -e '
tell application "Terminal"
    activate
    do script "cd /path/to/EliaAI && ./scripts/start_elias_discord.sh"
end tell
'