#!/bin/bash
# Wrapper opencode avec proxy via variables d'environnement
# Lit la config depuis ~/.proxychains.conf (écrite par switch-proxy.sh)

PROXY_CONF="$HOME/.proxychains.conf"

if [ ! -f "$PROXY_CONF" ]; then
    echo "❌ $PROXY_CONF introuvable. Run 'sp' d'abord pour configurer un proxy."
    exit 1
fi

PROXY_LINE=$(grep "^http " "$PROXY_CONF" | head -1)
if [ -z "$PROXY_LINE" ]; then
    echo "❌ Aucun proxy configuré dans $PROXY_CONF. Run 'sp' d'abord."
    exit 1
fi

IP=$(echo "$PROXY_LINE" | awk '{print $2}')
PORT=$(echo "$PROXY_LINE" | awk '{print $3}')
USER=$(echo "$PROXY_LINE" | awk '{print $4}')
PASS=$(echo "$PROXY_LINE" | awk '{print $5}')

if [ -z "$IP" ] || [ -z "$PORT" ]; then
    echo "❌ Configuration proxy invalide dans $PROXY_CONF."
    exit 1
fi

echo "🔧 Proxy activé: $IP:$PORT"
env HTTP_PROXY="http://${USER}:${PASS}@${IP}:${PORT}" \
    HTTPS_PROXY="http://${USER}:${PASS}@${IP}:${PORT}" \
    http_proxy="http://${USER}:${PASS}@${IP}:${PORT}" \
    https_proxy="http://${USER}:${PASS}@${IP}:${PORT}" \
    NO_PROXY="127.0.0.1,localhost,::1" \
    no_proxy="127.0.0.1,localhost,::1" \
    opencode "$@"
