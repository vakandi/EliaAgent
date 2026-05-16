#!/bin/zsh
lsof -ti:4096 | xargs kill -9 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
pkill -f "electron" 2>/dev/null || true
pkill -f "bot.py" 2>/dev/null || true
pkill -f "telegram-opencode-bot" 2>/dev/null || true
tmux kill-session -t elia 2>/dev/null || true
pkill -f "node.*EliaAI" 2>/dev/null || true
sleep 1