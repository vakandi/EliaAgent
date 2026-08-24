#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 5: System data and hidden consumers
# Read-only — no modifications

echo "============================================"
echo "  macOS DISK USAGE — SYSTEM DATA"
echo "============================================"
echo ""

# Docker
echo "### DOCKER"
if command -v docker &>/dev/null; then
    # Docker disk usage
    docker system df 2>/dev/null || echo "Docker not running or not accessible"
    echo ""
    # Docker raw disk image
    docker_img="$HOME/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw"
    if [ -f "$docker_img" ]; then
        echo "Docker.raw: $(du -sh "$docker_img" 2>/dev/null | cut -f1)"
    fi
    docker_img2="$HOME/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.qcow2"
    if [ -f "$docker_img2" ]; then
        echo "Docker.qcow2: $(du -sh "$docker_img2" 2>/dev/null | cut -f1)"
    fi
else
    echo "Docker not installed"
fi
echo ""

# Time Machine local snapshots
echo "### TIME MACHINE LOCAL SNAPSHOTS"
tmutil listlocalsnapshots / 2>/dev/null | head -10 || echo "No local snapshots or tmutil unavailable"
snap_count=$(tmutil listlocalsnapshots / 2>/dev/null | grep -c "com.apple" 2>/dev/null || echo "0")
echo "Total snapshots: $snap_count"
echo ""

# iCloud
echo "### ICLOUD DATA"
if [ -d ~/Library/Mobile\ Documents ]; then
    echo "Mobile Documents: $(du -sh ~/Library/Mobile\ Documents 2>/dev/null | cut -f1)"
    # iCloud drive breakdown
    if [ -d ~/Library/Mobile\ Documents/com~apple~CloudDocs ]; then
        echo "iCloud Drive: $(du -sh ~/Library/Mobile\ Documents/com~apple~CloudDocs 2>/dev/null | cut -f1)"
    fi
fi
echo ""

# Photos Library
echo "### PHOTOS LIBRARY"
photos_paths=(
    ~/Pictures/Photos\ Library.photoslibrary
    ~/Pictures/Photos\ Library.photoslibrary
)
for p in "${photos_paths[@]}"; do
    if [ -d "$p" ]; then
        echo "Photos Library: $(du -sh "$p" 2>/dev/null | cut -f1)"
        echo "Path: $p"
        break
    fi
done || echo "Photos Library not found in standard locations"
echo ""

# Mail
echo "### MAIL DATA"
if [ -d ~/Library/Mail ]; then
    echo "Mail data: $(du -sh ~/Library/Mail 2>/dev/null | cut -f1)"
    echo "Mailboxes:"
    du -sh ~/Library/Mail/* 2>/dev/null | sort -rh | head -5
fi
echo ""

# Messages database
echo "### MESSAGES DATABASE"
if [ -d ~/Library/Messages ]; then
    echo "Messages: $(du -sh ~/Library/Messages 2>/dev/null | cut -f1)"
    if [ -f ~/Library/Messages/chat.db ]; then
        echo "chat.db: $(du -sh ~/Library/Messages/chat.db 2>/dev/null | cut -f1)"
    fi
fi
echo ""

# Music and Podcasts
echo "### MUSIC & MEDIA"
if [ -d ~/Music ]; then
    echo "Music folder: $(du -sh ~/Music 2>/dev/null | cut -f1)"
    if [ -d ~/Music/Music ]; then
        echo "Music app data: $(du -sh ~/Music/Music 2>/dev/null | cut -f1)"
    fi
fi
if [ -d ~/Movies ]; then
    echo "Movies folder: $(du -sh ~/Movies 2>/dev/null | cut -f1)"
fi
echo ""

# Spotlight index
echo "### SPOTLIGHT INDEX"
if [ -d /.Spotlight-V100 ]; then
    echo "Spotlight index: $(du -sh /.Spotlight-V100 2>/dev/null | cut -f1)"
else
    echo "Spotlight index: SIP protected (readable only by system)"
fi
mdutil -s / 2>/dev/null | head -3 || echo "mdutil unavailable"
echo ""

# APFS snapshots
echo "### APFS SNAPSHOTS"
diskutil apfs list snapshots / 2>/dev/null | grep -E "Snapshot|Size|Date" | head -15 || echo "APFS snapshot info unavailable"
echo ""

# Swap files
echo "### SWAP FILES"
ls -lh /var/vm/ 2>/dev/null || echo "/var/vm not accessible"
swap_total=$(du -sh /var/vm 2>/dev/null | cut -f1 || echo "unknown")
echo "Swap total: $swap_total"
echo ""

# Font caches
echo "### FONT CACHE"
if [ -d ~/Library/Caches/com.apple.FontRegistry ]; then
    echo "Font cache: $(du -sh ~/Library/Caches/com.apple.FontRegistry 2>/dev/null | cut -f1)"
fi
echo ""
