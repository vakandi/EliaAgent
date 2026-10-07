#!/bin/sh
# Watch /data/config/tunnel.token and auto-start cloudflared on changes.
# Mirror of the live cloudflared-watch.sh: no Docker socket needed — restart
# is internal to this container. Also touches a heartbeat file so the shim's
# tunnel status can report cloudflared_running without container inspect.
set -eu
TOKEN_FILE="/data/config/tunnel.token"
HEARTBEAT_FILE="/data/config/cloudflared.alive"
echo "[watch] cloudflared watcher started, watching $TOKEN_FILE"
while true; do
  if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE" 2>/dev/null | tr -d '\n\r ')
    if [ -n "$TOKEN" ]; then
      echo "[watch] starting cloudflared"
      cloudflared tunnel --no-autoupdate run &
      PID=$!
      LAST_MD5=$(md5sum "$TOKEN_FILE" 2>/dev/null | awk '{print $1}')
      while kill -0 "$PID" 2>/dev/null; do
        touch "$HEARTBEAT_FILE" 2>/dev/null || true
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
