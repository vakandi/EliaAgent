#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/ssl_monitor_$(date +%Y%m%d).log"
mkdir -p "${SCRIPT_DIR}/logs"

echo "=== SSL Monitor - $(date) ===" | tee -a "$LOG_FILE"

declare -a domains=("yourbrand.com" "yourtool.com" "yourproject.com" "yourbrand2.com")

for domain in "${domains[@]}"; do
    expiry=$(echo | openssl s_client -servername "$domain" -connect "$domain":443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    if [[ -n "$expiry" ]]; then
        epoch=$(date -j -f "%b %d %H:%M:%S %Y" "$expiry" +%s 2>/dev/null || echo "0")
        now=$(date +%s)
        days=$(( (epoch - now) / 86400 ))
        if [[ $days -lt 0 ]]; then
            echo "❌ $domain: EXPIRED ($days days)" | tee -a "$LOG_FILE"
        elif [[ $days -lt 30 ]]; then
            echo "⚠️ $domain: $days days remaining" | tee -a "$LOG_FILE"
        else
            echo "✅ $domain: $days days" | tee -a "$LOG_FILE"
        fi
    else
        echo "❌ $domain: NO SSL or expired" | tee -a "$LOG_FILE"
    fi
done