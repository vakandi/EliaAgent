#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 6: Background services and network
# No sudo required

echo "============================================"
echo "  macOS SYSTEM HEALTH — SERVICES & NETWORK"
echo "============================================"
echo ""

# User launchd agents
echo "### USER LAUNCHD AGENTS"
ls ~/Library/LaunchAgents/ 2>/dev/null || echo "No user launch agents"
echo ""

# System launchd agents (not full list, just count + notable)
echo "### SYSTEM LAUNCHD AGENTS (count: $(ls /System/Library/LaunchAgents/ 2>/dev/null | wc -l))"
echo ""

# Active launchd jobs
echo "### ACTIVE LAUNCHD JOBS (user)"
launchctl list 2>/dev/null | head -30 || echo "launchctl not available"
echo ""

# Top network consumers by connections
echo "### NETWORK CONNECTIONS BY PROCESS"
lsof -i -n -P 2>/dev/null | awk 'NR>1{print $1}' | sort | uniq -c | sort -rn | head -15
echo ""

# Active network connections
echo "### ACTIVE NETWORK CONNECTIONS (sample)"
nettop -L 1 -P 2>/dev/null | head -20 || echo "nettop not available (try: sudo nettop)"
echo ""

# DNS resolution speed
echo "### DNS RESOLUTION SPEED"
start=$(python3 -c "import time; print(time.time())")
nslookup google.com >/dev/null 2>&1
end=$(python3 -c "import time; print(time.time())")
echo "DNS resolve time: $(python3 -c "print(f'{$end - $start:.3f}s')")"
echo ""

# Background uploads/downloads (iCloud, Dropbox, etc.)
echo "### BACKGROUND SYNC PROCESSES"
for proc in "bird" "fileproviderd" "cloudd" "photosgraphsd" "mdworker" "mds" "Dropbox" "OneDrive" "Google Drive"; do
    pid=$(pgrep -x "$proc" 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        cpu=$(ps -p "$pid" -o pcpu= 2>/dev/null | tr -d ' ')
        mem=$(ps -p "$pid" -o rss= 2>/dev/null | awk '{printf "%.1fMB", $1/1024}')
        echo "  $proc (PID $pid): CPU ${cpu}%  MEM $mem"
    fi
done
echo ""

# Spotlight activity
echo "### SPOTLIGHT ACTIVITY"
mds 2>/dev/null || echo "mds check not available"
echo "mds_stores processes:"
ps -eo pid,pcpu,rss,comm | grep mds | head -5
echo ""

# WindowServer (biggest GPU consumer typically)
echo "### WINDOWSERVER (display compositor)"
ws_pid=$(pgrep -x WindowServer 2>/dev/null | head -1)
if [ -n "$ws_pid" ]; then
    cpu=$(ps -p "$ws_pid" -o pcpu= 2>/dev/null | tr -d ' ')
    mem=$(ps -p "$ws_pid" -o rss= 2>/dev/null | awk '{printf "%.1fMB", $1/1024}')
    echo "WindowServer PID $ws_pid: CPU ${cpu}%  MEM $mem"
    echo "(High CPU = display issues, multiple monitors, or screen recording)"
else
    echo "WindowServer not found"
fi
echo ""

# Bluetooth devices (drain battery)
echo "### BLUETOUGHT DEVICES"
system_profiler SPBluetoothDataType 2>/dev/null | grep -E "Name:|Connected:" | head -10 || echo "Bluetooth info unavailable"
echo ""
