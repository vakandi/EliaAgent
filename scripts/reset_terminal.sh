#!/bin/zsh
# Reset terminal to fix escape character corruption

echo "Resetting terminal..."

# Reset terminal settings
stty sane 2>/dev/null

# Reset color and formatting
printf '\033[0m'

# Show cursor
printf '\033[?25h'

# Enable line wrapping
printf '\033[?7h'

# Clear screen and scrollback
printf '\033[2J\033[3J\033[H'

# Alternative: use tput if available
if command -v tput &> /dev/null; then
    tput reset 2>/dev/null || true
    tput sgr0 2>/dev/null || true
    tput cnorm 2>/dev/null || true
fi

echo "Terminal reset complete."
echo ""
