#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 4: Disk and I/O analysis
# No sudo required

echo "============================================"
echo "  macOS SYSTEM HEALTH — DISK & I/O"
echo "============================================"
echo ""

# Disk usage
echo "### DISK USAGE"
df -h | grep -v "devfs\|map\|VM"
echo ""

# I/O statistics
echo "### I/O STATISTICS"
iostat -d -c 1 -w 2 2>/dev/null | tail -20 || echo "iostat not available"
echo ""

# Disk space on key directories
echo "### KEY DIRECTORIES SIZE"
for dir in ~/Library/Caches ~/Library/Logs ~/Downloads /tmp ~/Library/Application\ Support; do
    if [ -d "$dir" ]; then
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        echo "$size  $dir"
    fi
done
echo ""

# SMART disk health
echo "### SMART DISK HEALTH"
diskutil info disk0 2>/dev/null | grep -i -E "SMART|Protocol|Type|Total Size|Free Space" || echo "Could not read disk0 info"
echo ""

# Spotlight indexing status
echo "### SPOTLIGHT INDEXING"
mdutil -s / 2>/dev/null || echo "mdutil not available"
echo ""

# Time Machine status
echo "### TIME MACHINE STATUS"
tmutil status 2>/dev/null || echo "Time Machine not configured"
echo ""
tmutil latestbackup 2>/dev/null || echo ""
echo ""

# APFS volume snapshots
echo "### APFS SNAPSHOTS (recent)"
tmutil listlocalsnapshots / 2>/dev/null | tail -5 || echo "No local snapshots"
echo ""

# Filesystem type
echo "### FILESYSTEM TYPE"
mount | grep " / " | awk '{print $1, $5, $6}'
echo ""

# Disk queue depth (high = I/O bottleneck)
echo "### DISK QUEUE DEPTH"
iostat -d -c 1 2>/dev/null | tail -5 || echo "Queue depth not available"
echo ""
