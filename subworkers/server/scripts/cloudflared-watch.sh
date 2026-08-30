#!/bin/sh
# Watch /data/config/tunnel.token and auto-restart cloudflared on changes.
# No Docker socket needed — restart is internal to this container.
set -eu
TOKEN_FILE="/data/config/tunnel.token"
echo "[watch] cloudflared watcher started, watching $TOKEN_FILE"
while true; do
  if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE" 2>/dev/null | tr -d '\n\r ')
    if [ -n "$TOKEN" ]; then
      export TUNNEL_TOKEN="$TOKEN"
      echo "[watch] starting cloudflared (token ${TOKEN:0:8}…)"
      cloudflared tunnel --no-autoupdate run &
      PID=$!
      LAST_MD5=$(md5sum "$TOKEN_FILE" 2>/dev/null | awk '{print $1}')
      while kill -0 "$PID" 2>/dev/null; do
        sleep 5
        CUR_MD5=$(md5sum "$TOKEN_FILE" 2>/dev/null | awk '{print $1}' || echo "")
        if [ "$CUR_MD5" != "$LAST_MD5" ]; then
          echo "[watch] token changed, restarting cloudflared"
          kill "$PID" 2>/dev/null || true
          break
        fi
      done
      wait "$PID" 2>/dev/null || true
      echo "[watch] cloudflared exited, restarting in 2s"
      sleep 2
      continue
    fi
  fi
  echo "[watch] no token at $TOKEN_FILE, waiting 5s"
  sleep 5
done
