#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 4: Caches, logs, and temporary files
# Read-only — no modifications

echo "============================================"
echo "  macOS DISK USAGE — CACHES & LOGS"
echo "============================================"
echo ""

# User Library Caches breakdown
echo "### ~/Library/CACHES (by size)"
if [ -d ~/Library/Caches ]; then
    du -sh ~/Library/Caches/* 2>/dev/null | sort -rh | head -20
    echo ""
    echo "Total caches: $(du -sh ~/Library/Caches 2>/dev/null | cut -f1)"
else
    echo "~/Library/Caches not found"
fi
echo ""

# System caches
echo "### SYSTEM CACHES (/Library/Caches)"
if [ -d /Library/Caches ]; then
    du -sh /Library/Caches/* 2>/dev/null | sort -rh | head -10
    echo "Total: $(du -sh /Library/Caches 2>/dev/null | cut -f1)"
else
    echo "/Library/Caches not found"
fi
echo ""

# User logs
echo "### USER LOGS (~/Library/Logs)"
if [ -d ~/Library/Logs ]; then
    du -sh ~/Library/Logs/* 2>/dev/null | sort -rh | head -15
    echo ""
    echo "Total logs: $(du -sh ~/Library/Logs 2>/dev/null | cut -f1)"
    # Count old logs (>30 days)
    old_logs=$(find ~/Library/Logs -type f -mtime +30 2>/dev/null | wc -l | tr -d ' ')
    echo "Logs older than 30 days: $old_logs files"
else
    echo "~/Library/Logs not found"
fi
echo ""

# System logs
echo "### SYSTEM LOGS (/var/log)"
if [ -d /var/log ]; then
    du -sh /var/log/* 2>/dev/null | sort -rh | head -10
    echo "Total: $(du -sh /var/log 2>/dev/null | cut -f1)"
else
    echo "/var/log not accessible"
fi
echo ""

# Crash reports
echo "### CRASH REPORTS"
if [ -d ~/Library/Logs/DiagnosticReports ]; then
    crash_size=$(du -sh ~/Library/Logs/DiagnosticReports 2>/dev/null | cut -f1)
    crash_count=$(find ~/Library/Logs/DiagnosticReports -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "~/Library/Logs/DiagnosticReports: $crash_size ($crash_count files)"
fi
if [ -d /Library/Logs/DiagnosticReports ]; then
    sys_crash=$(du -sh /Library/Logs/DiagnosticReports 2>/dev/null | cut -f1)
    echo "/Library/Logs/DiagnosticReports: $sys_crash"
fi
echo ""

# Browser caches
echo "### BROWSER CACHES"
for browser_path in \
    ~/Library/Caches/Google/Chrome \
    ~/Library/Caches/com.apple.Safari \
    ~/Library/Caches/Firefox \
    ~/Library/Caches/BraveSoftware \
    ~/Library/Caches/Microsoft/Edge; do
    if [ -d "$browser_path" ]; then
        size=$(du -sh "$browser_path" 2>/dev/null | cut -f1)
        name=$(echo "$browser_path" | sed 's|.*/Caches/||')
        echo "$size	$name"
    fi
done
echo ""

# Xcode derived data and archives
echo "### XCODE DATA"
if [ -d ~/Library/Developer/Xcode/DerivedData ]; then
    echo "DerivedData: $(du -sh ~/Library/Developer/Xcode/DerivedData 2>/dev/null | cut -f1)"
fi
if [ -d ~/Library/Developer/Xcode/Archives ]; then
    echo "Archives: $(du -sh ~/Library/Developer/Xcode/Archives 2>/dev/null | cut -f1)"
fi
if [ -d ~/Library/Developer/CoreSimulator/Caches ]; then
    echo "Simulator caches: $(du -sh ~/Library/Developer/CoreSimulator/Caches 2>/dev/null | cut -f1)"
fi
if [ -d ~/Library/Developer/CoreSimulator/Devices ]; then
    echo "Simulator devices: $(du -sh ~/Library/Developer/CoreSimulator/Devices 2>/dev/null | cut -f1)"
fi
echo ""

# /tmp
echo "### TEMP FILES (/tmp)"
if [ -d /tmp ]; then
    tmp_size=$(du -sh /tmp 2>/dev/null | cut -f1)
    echo "/tmp: $tmp_size"
fi
echo ""

# Downloads folder (the classic)
echo "### DOWNLOADS FOLDER"
if [ -d ~/Downloads ]; then
    dl_size=$(du -sh ~/Downloads 2>/dev/null | cut -f1)
    dl_count=$(find ~/Downloads -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "~/Downloads: $dl_size ($dl_count files)"
    echo ""
    echo "Largest files in Downloads:"
    find ~/Downloads -type f -exec du -sh {} \; 2>/dev/null | sort -rh | head -10
fi
echo ""
