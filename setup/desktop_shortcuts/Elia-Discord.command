osascript -e '
tell application "Terminal"
    activate
    do script "cd /Users/vakandi/EliaAI && ./scripts/start_elias_discord.sh"
end tell
'