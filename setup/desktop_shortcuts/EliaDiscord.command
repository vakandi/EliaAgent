osascript -e 'tell application "Terminal"
    activate
    do script "cd /Users/vakandi/EliaAI/integrations/elia-discord-bot && source venv/bin/activate && unset http_proxy && unset https_proxy && unset HTTP_PROXY && unset HTTPS_PROXY && python3 bot.py"
    delay 0.3
    set bounds of front window to {100, 50, 700, 600}
end tell'