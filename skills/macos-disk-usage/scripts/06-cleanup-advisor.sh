#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

fast_du() {
    timeout 10 du -sh "$1" 2>/dev/null | cut -f1 || echo "slow"
}

echo "============================================"
echo "  macOS DISK USAGE — CLEANUP ADVISOR"
echo "============================================"
echo ""
echo "This script ONLY recommends cleanup actions."
echo "It NEVER deletes, moves, or modifies any files."
echo "You decide what to delete manually."
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TIER 1: SAFE TO DELETE (zero risk to system)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Browser caches (these rebuild automatically):"
for cache_dir in \
    ~/Library/Caches/Google/Chrome \
    ~/Library/Caches/com.apple.Safari \
    ~/Library/Caches/Firefox \
    ~/Library/Caches/BraveSoftware \
    ~/Library/Caches/Microsoft/Edge; do
    if [ -d "$cache_dir" ]; then
        size=$(fast_du "$cache_dir")
        name=$(echo "$cache_dir" | sed 's|.*/Caches/||')
        echo "  ✓ $name cache: $size"
    fi
done
echo ""

echo "Old logs (>30 days):"
if [ -d ~/Library/Logs ]; then
    old_count=$(find ~/Library/Logs -type f -mtime +30 2>/dev/null | wc -l | tr -d ' ')
    if [ "$old_count" -gt 0 ]; then
        old_size=$(find ~/Library/Logs -type f -mtime +30 -exec du -sk {} \; 2>/dev/null | awk '{sum+=$1} END {printf "%.1fMB", sum/1024}')
        echo "  ✓ $old_count old log files: ~$old_size"
    fi
fi
echo ""

echo "Crash reports:"
if [ -d ~/Library/Logs/DiagnosticReports ]; then
    crash_size=$(fast_du ~/Library/Logs/DiagnosticReports)
    crash_count=$(find ~/Library/Logs/DiagnosticReports -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "  ✓ DiagnosticReports: $crash_size ($crash_count files)"
fi
echo ""

echo "Package manager caches:"
if [ -d ~/.npm ]; then
    npm_size=$(fast_du ~/.npm)
    echo "  ✓ npm cache: $npm_size  →  npm cache clean --force"
fi
pip_cache=$(pip3 cache dir 2>/dev/null || echo "")
if [ -n "$pip_cache" ] && [ -d "$pip_cache" ]; then
    pip_size=$(fast_du "$pip_cache")
    echo "  ✓ pip cache: $pip_size  →  pip3 cache purge"
fi
brew_cache=$(brew --cache 2>/dev/null || echo "")
if [ -n "$brew_cache" ] && [ -d "$brew_cache" ]; then
    brew_size=$(fast_du "$brew_cache")
    echo "  ✓ brew cache: $brew_size  →  brew cleanup"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TIER 2: MODERATE RISK (delete if you're sure)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Repositories with no recent activity (>6 months):"
find ~ -maxdepth 4 -name ".git" -type d \
    ! -path "*/Library/*" \
    ! -path "*/.*/*" \
    2>/dev/null | while read gitdir; do
    repo=$(dirname "$gitdir")
    last_commit=$(git -C "$repo" log -1 --format="%as" 2>/dev/null || echo "")
    if [ -n "$last_commit" ]; then
        commit_epoch=$(date -j -f "%Y-%m-%d" "$last_commit" "+%s" 2>/dev/null || echo "0")
        now_epoch=$(date "+%s")
        if [ "$commit_epoch" -gt 0 ]; then
            days_old=$(( (now_epoch - commit_epoch) / 86400 ))
            if [ "$days_old" -gt 180 ]; then
                size=$(fast_du "$repo")
                echo "  ⚠ $size  $repo (last: $last_commit, ${days_old}d ago)"
            fi
        fi
    fi
done 2>/dev/null | sort -rh | head -10
echo ""

echo "Docker unused resources:"
if command -v docker &>/dev/null; then
    docker system df 2>/dev/null | grep -E "Build cache|Images|Containers|Volumes" | while read line; do
        echo "  ⚠ $line"
    done
    echo "  → docker system prune -a"
else
    echo "  Docker not installed"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TIER 3: RISKY (back up first, think twice)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ⚠ Photos Library — use Photos > Optimize Storage instead of deleting"
echo "  ⚠ Mail data — back up ~/Library/Mail first"
echo "  ⚠ Messages — back up ~/Library/Messages first"
echo "  ⚠ Docker volumes — may contain persistent data"
echo "  ⚠ Time Machine snapshots — auto-recreate but take space"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  QUICK CLEANUP COMMANDS (copy-paste to execute)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "# Clean package manager caches:"
echo "  npm cache clean --force"
echo "  pip3 cache purge"
echo "  brew cleanup"
echo ""
echo "# Remove crash reports:"
echo "  rm -rf ~/Library/Logs/DiagnosticReports/*"
echo ""
echo "# Remove old logs (>30 days):"
echo "  find ~/Library/Logs -type f -mtime +30 -delete"
echo ""
echo "# Prune Docker:"
echo "  docker system prune -a"
echo ""
echo "# Find your 20 largest files:"
echo "  find ~ -type f -size +100M -exec du -sh {} \\; | sort -rh | head -20"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  REMEMBER: This skill ONLY recommends."
echo "  YOU decide what to delete. Be careful."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
