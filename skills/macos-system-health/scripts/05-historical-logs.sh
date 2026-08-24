#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 5: Historical logs and events
# No sudo required for most

echo "============================================"
echo "  macOS SYSTEM HEALTH — HISTORICAL LOGS"
echo "============================================"
echo ""

# Kernel panics (last 7 days)
echo "### KERNEL PANICS (last 7 days)"
log show --predicate 'eventMessage contains "kernel panic" or messageType == panic' --last 7d --style compact 2>/dev/null | tail -20 || echo "No kernel panics found"
echo ""

# Thermal throttle events
echo "### THERMAL THROTTLE EVENTS (last 7 days)"
log show --predicate 'eventMessage contains "thermal" or eventMessage contains "throttl" or eventMessage contains "thermallevel"' --last 7d --style compact 2>/dev/null | tail -20 || echo "No thermal throttle events found"
echo ""

# OOM / memory pressure kills
echo "### MEMORY PRESSURE KILLS (last 7 days)"
log show --predicate 'eventMessage contains "jetsam" or eventMessage contains "memory pressure" or eventMessage contains "OOM" or eventMessage contains "killed process"' --last 7d --style compact 2>/dev/null | tail -20 || echo "No memory pressure kills found"
echo ""

# Crash reports
echo "### RECENT CRASH REPORTS (last 3 days)"
ls -lt ~/Library/Logs/DiagnosticReports/ 2>/dev/null | head -15 || echo "No crash reports found"
echo ""

# Sleep/wake history
echo "### SLEEP/WAKE HISTORY (last 50 events)"
log show --predicate 'eventMessage contains "Entering Sleep" or eventMessage contains "Wake from" or eventMessage contains "DarkWake"' --last 7d --style compact 2>/dev/null | tail -20 || echo "No sleep/wake events found"
echo ""

# Disk errors
echo "### DISK ERRORS (last 7 days)"
log show --predicate 'eventMessage contains "disk" and eventMessage contains "error"' --last 7d --style compact 2>/dev/null | tail -10 || echo "No disk errors found"
echo ""

# Security events (relevant for hardware tampering)
echo "### SECURITY / TAMPER EVENTS (last 7 days)"
log show --predicate 'eventMessage contains "TCC" or eventMessage contains "Security"' --last 7d --style compact 2>/dev/null | tail -10 || echo "No security events"
echo ""

# System boot time anomalies (slow boots indicate issues)
echo "### BOOT HISTORY"
last reboot | head -10
echo ""

# Process crashes
echo "### PROCESS CRASHES (last 3 days)"
log show --predicate 'eventMessage contains "abort" or eventMessage contains "segmentation fault" or eventMessage contains "EXC_BAD_ACCESS"' --last 3d --style compact 2>/dev/null | tail -15 || echo "No process crashes found"
echo ""
