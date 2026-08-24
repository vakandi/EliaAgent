#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 2: Deep process analysis
# No sudo required

echo "============================================"
echo "  macOS SYSTEM HEALTH — PROCESS DEEP DIVE"
echo "============================================"
echo ""

# All processes sorted by CPU
echo "### ALL PROCESSES BY CPU USAGE"
ps -eo pid,pcpu,pmem,rss,vsz,comm -r | head -30
echo ""

# Memory breakdown
echo "### MEMORY BREAKDOWN"
echo "--- PhysMem: ---"
top -l 1 -n 0 | grep PhysMem
echo ""

# Virtual memory per top process
echo "### VIRTUAL MEMORY — TOP 15 PROCESSES"
ps -eo pid,vsz,rss,comm | sort -k2 -rn | head -15 | awk '{printf "%-8s %10.1f MB virt  %8.1f MB phys  %s\n", $1, $2/1024, $3/1024, $4}'
echo ""

# Compressed memory
echo "### COMPRESSED MEMORY"
vm_stat | grep -i "compressor"
echo ""

# Open files per process (leak detection)
echo "### OPEN FILES — TOP 15 (high count = potential leak)"
ps -eo pid,comm | while read pid comm; do
    count=$(lsof -p "$pid" 2>/dev/null | wc -l)
    if [ "$count" -gt 100 ]; then
        echo "$count $pid $comm"
    fi
done | sort -rn | head -15
echo "(showing processes with >100 open files)"
echo ""

# Zombie processes
echo "### ZOMBIE PROCESSES"
zombies=$(ps -eo stat | grep -c 'Z' || true)
if [ "$zombies" -gt 0 ]; then
    echo "WARNING: $zombies zombie processes found!"
    ps -eo pid,stat,comm | grep 'Z'
else
    echo "No zombie processes."
fi
echo ""

# Thread count (high thread count can indicate issues)
echo "### THREAD COUNT — TOP 10"
ps -eo pid,nlwp,comm | sort -k2 -rn | head -10
echo "(nlwp = number of threads)"
echo ""

# Kernel task check
echo "### KERNEL TASK"
kernel_cpu=$(ps -eo pid,pcpu,comm | grep "kernel_task" | awk '{print $2}')
if [ -n "$kernel_cpu" ]; then
    echo "kernel_task CPU usage: ${kernel_cpu}%"
    if (( $(echo "$kernel_cpu > 50" | bc -l 2>/dev/null || echo 0) )); then
        echo "WARNING: kernel_task at high CPU — possible thermal throttling or I/O contention"
    fi
else
    echo "kernel_task not found or 0% CPU"
fi
echo ""

# GPU processes (Apple Silicon unified memory)
echo "### GPU-RELATED PROCESSES"
# Check for processes known to use GPU
for proc in "WindowServer" "Photoshop" "Safari" "Chrome" "Firefox" "DaVinci" "Final Cut" "Blender" "MesaDemoGL"; do
    gpu_line=$(ps -eo pid,pcpu,comm | grep -i "$proc" | head -1)
    if [ -n "$gpu_line" ]; then
        echo "$gpu_line"
    fi
done
echo "(GPU usage is harder to detect from CLI on macOS — Activity Monitor GPU tab is more accurate)"
echo ""
