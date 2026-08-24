#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Phase 2: Applications and installed software
# Read-only — no modifications

echo "============================================"
echo "  macOS DISK USAGE — APPS & SOFTWARE"
echo "============================================"
echo ""

# Applications in /Applications
echo "### APPLICATIONS (/Applications) — sorted by size"
if [ -d /Applications ]; then
    for app in /Applications/*.app; do
        if [ -d "$app" ]; then
            size=$(du -sh "$app" 2>/dev/null | cut -f1)
            name=$(basename "$app" .app)
            echo "$size	$name"
        fi
    done | sort -rh | head -20
else
    echo "/Applications not found"
fi
echo ""

# User applications
echo "### USER APPLICATIONS (~/Applications)"
if [ -d ~/Applications ]; then
    for app in ~/Applications/*.app; do
        if [ -d "$app" ]; then
            size=$(du -sh "$app" 2>/dev/null | cut -f1)
            name=$(basename "$app" .app)
            echo "$size	$name"
        fi
    done | sort -rh | head -10
else
    echo "No ~/Applications directory"
fi
echo ""

# Total Applications size
echo "### TOTAL APPLICATIONS SIZE"
total_apps=$(du -sh /Applications 2>/dev/null | cut -f1)
total_user_apps=$(du -sh ~/Applications 2>/dev/null | cut -f1 || echo "0B")
echo "/Applications: $total_apps"
echo "~/Applications: $total_user_apps"
echo ""

# Homebrew packages
echo "### HOMEBREW PACKAGES"
if command -v brew &>/dev/null; then
    echo "Installed formulae: $(brew list --formula 2>/dev/null | wc -l | tr -d ' ')"
    echo "Installed casks: $(brew list --cask 2>/dev/null | wc -l | tr -d ' ')"
    brew_dir=$(brew --prefix 2>/dev/null)
    if [ -d "$brew_dir" ]; then
        echo "Homebrew directory size: $(du -sh "$brew_dir" 2>/dev/null | cut -f1)"
    fi
    echo ""
    echo "Largest Homebrew packages:"
    brew list --formula 2>/dev/null | while read pkg; do
        pkg_dir="$brew_dir/opt/$pkg" 2>/dev/null
        if [ -d "$pkg_dir" ]; then
            size=$(du -sh "$pkg_dir" 2>/dev/null | cut -f1)
            echo "$size	$pkg"
        fi
    done 2>/dev/null | sort -rh | head -10
else
    echo "Homebrew not installed"
fi
echo ""

# npm global packages
echo "### NPM GLOBAL PACKAGES"
if command -v npm &>/dev/null; then
    npm_dir=$(npm root -g 2>/dev/null)
    if [ -d "$npm_dir" ]; then
        echo "npm global dir: $npm_dir"
        echo "Size: $(du -sh "$npm_dir" 2>/dev/null | cut -f1)"
        echo "Packages: $(ls "$npm_dir" 2>/dev/null | wc -l | tr -d ' ')"
    fi
    # npm cache
    npm_cache=$(npm cache ls 2>/dev/null | head -1 || npm config get cache 2>/dev/null)
    if [ -d "$npm_cache" ]; then
        echo "npm cache: $(du -sh "$npm_cache" 2>/dev/null | cut -f1)"
    fi
else
    echo "npm not installed"
fi
echo ""

# pip packages
echo "### PYTHON PACKAGES (pip)"
if command -v pip3 &>/dev/null; then
    pip3_count=$(pip3 list 2>/dev/null | tail -n +3 | wc -l | tr -d ' ')
    echo "Installed packages: $pip3_count"
    # pip cache
    pip_cache=$(pip3 cache dir 2>/dev/null || echo "")
    if [ -n "$pip_cache" ] && [ -d "$pip_cache" ]; then
        echo "pip cache: $(du -sh "$pip_cache" 2>/dev/null | cut -f1)"
    fi
else
    echo "pip3 not installed"
fi
echo ""

# Ruby gems
echo "### RUBY GEMS"
if command -v gem &>/dev/null; then
    gem_dir=$(gem environment gemdir 2>/dev/null)
    if [ -d "$gem_dir" ]; then
        echo "Gems dir: $gem_dir"
        echo "Size: $(du -sh "$gem_dir" 2>/dev/null | cut -f1)"
        echo "Gems: $(ls "$gem_dir"/gems 2>/dev/null | wc -l | tr -d ' ')"
    fi
else
    echo "Ruby gems not installed"
fi
echo ""

# Xcode (if installed)
echo "### XCODE"
if [ -d /Applications/Xcode.app ]; then
    xcode_size=$(du -sh /Applications/Xcode.app 2>/dev/null | cut -f1)
    echo "Xcode.app: $xcode_size"
    # Derived data
    if [ -d ~/Library/Developer/Xcode/DerivedData ]; then
        echo "DerivedData: $(du -sh ~/Library/Developer/Xcode/DerivedData 2>/dev/null | cut -f1)"
    fi
    # Archives
    if [ -d ~/Library/Developer/Xcode/Archives ]; then
        echo "Archives: $(du -sh ~/Library/Developer/Xcode/Archives 2>/dev/null | cut -f1)"
    fi
else
    echo "Xcode not installed"
fi
echo ""
