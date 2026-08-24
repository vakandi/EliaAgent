#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 1: Disk overview
# Read-only — no modifications to disk
# Optimized for speed — avoids deep scans of system directories

echo "============================================"
echo "  macOS DISK USAGE — OVERVIEW"
echo "============================================"
echo ""

# System info
echo "### SYSTEM INFO"
echo "Hostname: $(scutil --get ComputerName 2>/dev/null || echo 'unknown')"
echo "macOS: $(sw_vers -productVersion) ($(sw_vers -buildVersion))"
echo "Hardware: $(sysctl -n hw.model)"
echo ""

# Disk usage summary
echo "### DISK USAGE SUMMARY"
df -h / | tail -1 | awk '{printf "Total: %s  Used: %s (%s)  Free: %s  Mount: %s\n", $2, $3, $5, $4, $6}'
echo ""

# Full disk layout
echo "### FULL DISK LAYOUT"
df -h | grep -v "devfs\|map\|VM" | column -t
echo ""

# APFS volume group info
echo "### APFS VOLUME GROUP"
diskutil apfs list 2>/dev/null | grep -E "Volume Group|Role|Capacity|Free|Size" | head -20 || echo "APFS info unavailable"
echo ""

# Physical disk info
echo "### PHYSICAL DISK"
diskutil info disk0 2>/dev/null | grep -E "Device Node|Protocol|Type|Total Size|Free Space|SMART" || echo "disk0 info unavailable"
echo ""

# Inode usage
echo "### INODE USAGE"
df -i / | tail -1 | awk '{printf "Total inodes: %s  Used: %s (%s)  Free: %s\n", $2, $3, $5, $4}'
echo ""

echo "### TOP-LEVEL DIRECTORY SIZES"
for dir in ~/Documents ~/Downloads ~/Desktop ~/Movies ~/Music ~/Pictures ~/Projects ~/Developer ~/repos ~/code ~/.cache ~/.npm ~/.cargo; do
    if [ -d "$dir" ]; then
        size=$(du -sk "$dir" 2>/dev/null | head -1 | cut -f1)
        if [ -n "$size" ]; then
            human=$(numfmt --to=iec-i --suffix=B "${size}k" 2>/dev/null || echo "${size}KB")
            printf "%10s  %s\n" "$human" "$dir"
        fi
    fi
done | sort -rn
echo ""
