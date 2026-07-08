#!/bin/bash
# Proxy Wrapper - Wrapper pour proxychains4 avec binaires non-SIP
# Usage: source proxy-wrapper.sh <command>

export PROXYCHAINS_CONF_FILE="$HOME/.proxychains.conf"

# Utiliser curl Homebrew au lieu du curl système
export CURL_BIN="/opt/homebrew/opt/curl/bin/curl"

# Fonction pour vérifier si un binaire est protégé par SIP
check_sip() {
    local binary="$1"
    if codesign -dvv "$binary" 2>&1 | grep -q "Runtime\|LibraryValidation"; then
        return 0  # Protégé
    fi
    return 1  # Non protégé
}

# Wrapper curl
pcurl() {
    proxychains4 -f "$PROXYCHAINS_CONF_FILE" "$CURL_BIN" "$@"
}

# Test rapide
ptest() {
    echo "🔄 Switching proxy..."
    "$HOME/EliaAI/setup/switch-proxy.sh" 2>&1 | tail -3
    echo ""
    echo "🧪 Testing with curl..."
    IP=$(proxychains4 -f "$PROXYCHAINS_CONF_FILE" "$CURL_BIN" -s https://api.ipify.org 2>&1 | grep -v proxychains | tail -1)
    echo "🌐 Current IP: $IP"
}

# Si appelé avec argument, exécuter via proxychains4
if [ $# -gt 0 ]; then
    proxychains4 -f "$PROXYCHAINS_CONF_FILE" "$@"
fi
