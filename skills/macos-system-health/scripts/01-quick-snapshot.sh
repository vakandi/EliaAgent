#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 1: Quick system snapshot
# No sudo required — safe to run anywhere

echo "============================================"
echo "  macOS SYSTEM HEALTH — QUICK SNAPSHOT"
echo "============================================"
echo ""

# System info
echo "### SYSTEM INFO"
echo "Hostname: $(scutil --get ComputerName 2>/dev/null || echo 'unknown')"
echo "macOS: $(sw_vers -productVersion) ($(sw_vers -buildVersion))"
echo "Hardware: $(sysctl -n hw.model)"
echo "CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || sysctl -n hw.ncpu) cores"
echo "RAM: $(echo "$(sysctl -n hw.memsize) / 1073741824" | bc) GB"
echo "Uptime: $(uptime | sed 's/.*up //' | sed 's/,.*//')"
echo ""

# Load averages
echo "### LOAD AVERAGES (1/5/15 min)"
sysctl -n vm.loadavg
echo ""

# CPU usage overview
echo "### CPU USAGE"
top -l 1 -n 0 | head -12
echo ""

# Top 10 CPU consumers
echo "### TOP 10 CPU CONSUMERS"
ps -eo pid,pcpu,pmem,rss,comm -r | head -11
echo ""

# Top 10 RAM consumers
echo "### TOP 10 RAM CONSUMERS (RSS in MB)"
ps -eo pid,pmem,rss,comm | sort -k2 -rn | head -11 | awk '{printf "%-8s %5s%% %8.1f MB  %s\n", $1, $2, $3/1024, $4}'
echo ""

# Memory overview
echo "### MEMORY PRESSURE"
memory_pressure 2>/dev/null || echo "memory_pressure not available"
echo ""

# Swap usage
echo "### SWAP USAGE"
sysctl vm.swapusage
echo ""

# Pageins/Pageouts (indicator of memory pressure)
echo "### PAGE INS/OUTS (high = memory pressure)"
vm_stat | grep -E "Pages (free|active|inactive|speculative|throttled|wire|occupied)|pageins|pageouts|swapins|swapouts"
echo ""
