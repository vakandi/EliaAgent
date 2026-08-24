#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 3: Projects and repositories
# Read-only — no modifications
# Optimized: depth limits + exclusions for speed

echo "============================================"
echo "  macOS DISK USAGE — PROJECTS & REPOS"
echo "============================================"
echo ""

# Common project directories
echo "### PROJECT DIRECTORIES"
for dir in ~/Projects ~/Developer ~/code ~/repos ~/work ~/src ~/Documents/GitHub ~/Documents/Projects; do
    if [ -d "$dir" ]; then
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        count=$(find "$dir" -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
        echo "$size	$dir ($count subdirectories)"
    fi
done
echo ""

# Git repos (depth 4, skip Library/node_modules)
echo "### GIT REPOSITORIES (by size)"
find ~ -maxdepth 4 -name ".git" -type d \
    ! -path "*/Library/*" \
    ! -path "*/node_modules/*" \
    ! -path "*/.*/*" \
    2>/dev/null | while read gitdir; do
    repo=$(dirname "$gitdir")
    size=$(du -sh "$repo" 2>/dev/null | cut -f1)
    echo "$size	$repo"
done 2>/dev/null | sort -rh | head -20
echo ""

# node_modules
echo "### NODE_MODULES DIRECTORIES"
find ~ -maxdepth 5 -name "node_modules" -type d \
    ! -path "*/Library/*" \
    2>/dev/null | while read nm_dir; do
    size=$(du -sh "$nm_dir" 2>/dev/null | cut -f1)
    echo "$size	$nm_dir"
done 2>/dev/null | sort -rh | head -15
echo ""

# Python virtual environments
echo "### PYTHON VIRTUAL ENVIRONMENTS"
find ~ -maxdepth 5 -name "pyvenv.cfg" -type f \
    ! -path "*/Library/*" \
    2>/dev/null | while read cfg; do
    venv=$(dirname "$cfg")
    size=$(du -sh "$venv" 2>/dev/null | cut -f1)
    echo "$size	$venv"
done 2>/dev/null | sort -rh | head -10
echo ""

# Build artifacts
echo "### BUILD ARTIFACTS"
for pattern in "dist" "build" ".next" ".nuxt" "out" "target"; do
    count=$(find ~ -maxdepth 5 -name "$pattern" -type d \
        ! -path "*/Library/*" \
        ! -path "*/node_modules/*" \
        2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt 0 ]; then
        echo "Found $count '$pattern' directories:"
        find ~ -maxdepth 5 -name "$pattern" -type d \
            ! -path "*/Library/*" \
            ! -path "*/node_modules/*" \
            2>/dev/null | while read d; do
            size=$(du -sh "$d" 2>/dev/null | cut -f1)
            echo "    $size	$d"
        done 2>/dev/null | sort -rh | head -5
        echo ""
    fi
done
echo ""
