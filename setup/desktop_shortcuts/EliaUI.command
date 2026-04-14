osascript -e '
tell application "Terminal"
    activate
    do script "cd ~/EliaAI/ui_electron && npm start"
    delay 0.3
    tell application "System Events" to keystroke "t" using command down
    delay 0.3
    do script "opencode serve" in front window
    set bounds of front window to {100, 50, 500, 900}
end tell
'
