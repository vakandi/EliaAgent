osascript -e 'tell application "Terminal"
    activate
    do script "~/user/Documents/dictate.command"
    delay 0.3
    set bounds of front window to {100, 50, 500, 900}
end tell'
