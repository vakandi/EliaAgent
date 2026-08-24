#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 3: Thermal and hardware diagnostics
# May require sudo for powermetrics

echo "============================================"
echo "  macOS SYSTEM HEALTH — THERMAL & HARDWARE"
echo "============================================"
echo ""

# Try powermetrics for temperature (requires sudo)
echo "### CPU/GPU TEMPERATURE (powermetrics — may need sudo)"
if sudo -n true 2>/dev/null; then
    # No password needed
    sudo powermetrics --samplers smc -i 1000 -n 1 2>/dev/null | grep -i -E "temperature|temp|die|core|gpu" || echo "No temperature data from powermetrics"
elif command -v powermetrics &>/dev/null; then
    echo "Sudo required for temperature sensors. Attempting with timeout..."
    # Give user 5 seconds to enter password
    timeout 8 sudo powermetrics --samplers smc -i 1000 -n 1 2>/dev/null | grep -i -E "temperature|temp|die|core|gpu" || echo "Sudo cancelled or timeout — temperature unavailable"
else
    echo "powermetrics not available"
fi
echo ""

# Fallback: ioreg sensor data
echo "### IOREG THERMAL DATA (no sudo needed)"
ioreg -l | grep -i -E "\"Temperature\"|\"CurrentCapacity\"|\"MaxCapacity\"|\"CycleCount\"" | head -20
echo ""

# Fan speeds
echo "### FAN SPEEDS"
if command -v powermetrics &>/dev/null && sudo -n true 2>/dev/null; then
    sudo powermetrics --samplers smc -i 1000 -n 1 2>/dev/null | grep -i fan || echo "No fan data"
else
    # Fallback via ioreg
    ioreg -l | grep -i "FanSpeed" | head -5 || echo "Fan speed data not available without sudo"
fi
echo ""

# Thermal throttle events from kernel log (last 24h)
echo "### THERMAL THROTTLE EVENTS (last 24h)"
log show --predicate 'eventMessage contains "thermal" or eventMessage contains "throttl"' --last 24h --style compact 2>/dev/null | tail -20 || echo "No thermal events found (or log show unavailable)"
echo ""

# CPU speed (check for throttling)
echo "### CPU FREQUENCY"
sysctl -n hw.cpufrequency 2>/dev/null | awk '{printf "CPU max frequency: %.2f GHz\n", $1/1000000000}' || echo "hw.cpufrequency not available (Apple Silicon?)"
echo "Active CPUs: $(sysctl -n hw.activecpu) / $(sysctl -n hw.ncpu) total"
echo ""

# Battery health (MacBook)
echo "### BATTERY HEALTH"
ioreg -l | grep -i -E "\"AppleRawMaxCapacity\"|\"MaxCapacity\"|\"DesignCapacity\"|\"CycleCount\"|\"Temperature\"|\"IsCharging\"|\"ExternalConnected\"" | head -20
echo ""

# Battery cycle count details
echo "--- Battery Cycle Count ---"
ioreg -l | grep -i "CycleCount" | head -3
echo ""

# Battery condition
pmset -g batt 2>/dev/null || echo "pmset battery info unavailable"
echo ""

# RAM hardware errors
echo "### MEMORY ERRORS (hardware)"
log show --predicate 'eventMessage contains "memory" and eventMessage contains "error"' --last 7d --style compact 2>/dev/null | tail -10 || echo "No memory error logs found"
echo ""

# SMC reset indicator
echo "### SMC STATUS"
echo "If thermal management seems broken, consider SMC reset:"
echo "  Intel Mac: Shut down → hold Left Shift+Ctrl+Option+Power for 10s → release → power on"
echo "  Apple Silicon: Shut down → wait 30s → power on (automatic SMC reset)"
echo ""
