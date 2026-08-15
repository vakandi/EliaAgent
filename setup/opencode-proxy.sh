#!/bin/bash
# Wrapper opencode avec proxy via variables d'environnement.
# Bun honors HTTP_PROXY/HTTPS_PROXY, so we export the full set here before
# launching the OpenCode process.

set -euo pipefail

PROXY_CONF="$HOME/.proxychains.conf"

if [[ ! -f "$PROXY_CONF" ]]; then
    echo "❌ Proxy config not found: $PROXY_CONF" >&2
    exit 1
fi

PROXY_LINE="$(grep -v '^#' "$PROXY_CONF" | grep '^http ' | head -1 || true)"
if [[ -z "$PROXY_LINE" ]]; then
    echo "❌ No proxy entry found in $PROXY_CONF" >&2
    exit 1
fi

read -r _ IP PORT USER PASS <<< "$PROXY_LINE"
if [[ -z "${IP:-}" || -z "${PORT:-}" || -z "${USER:-}" || -z "${PASS:-}" ]]; then
    echo "❌ Invalid proxy entry in $PROXY_CONF: $PROXY_LINE" >&2
    exit 1
fi

PROXY_URL="http://${USER}:${PASS}@${IP}:${PORT}"

echo "🔧 Proxy activé: $IP:$PORT"
exec env \
    HTTP_PROXY="$PROXY_URL" \
    HTTPS_PROXY="$PROXY_URL" \
    ALL_PROXY="$PROXY_URL" \
    http_proxy="$PROXY_URL" \
    https_proxy="$PROXY_URL" \
    all_proxy="$PROXY_URL" \
    NO_PROXY="127.0.0.1,localhost,::1" \
    no_proxy="127.0.0.1,localhost,::1" \
    opencode "$@"
