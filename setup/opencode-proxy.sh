#!/bin/bash
# Wrapper opencode avec proxy via variables d'environnement

PROXY_CONF="$HOME/.proxychains.conf"
PROXY_LINE=$(grep "http " "$PROXY_CONF" | head -1)
IP=$(echo "$PROXY_LINE" | awk '{print $2}')
PORT=$(echo "$PROXY_LINE" | awk '{print $3}')
USER=$(echo "$PROXY_LINE" | awk '{print $4}')
PASS=$(echo "$PROXY_LINE" | awk '{print $5}')

echo "🔧 Proxy activé: $IP:$PORT"
env HTTP_PROXY="http://${USER}:${PASS}@${IP}:${PORT}" \
    HTTPS_PROXY="http://${USER}:${PASS}@${IP}:${PORT}" \
    http_proxy="http://${USER}:${PASS}@${IP}:${PORT}" \
    https_proxy="http://${USER}:${PASS}@${IP}:${PORT}" \
    NO_PROXY="127.0.0.1,localhost,::1" \
    no_proxy="127.0.0.1,localhost,::1" \
    opencode "$@"
