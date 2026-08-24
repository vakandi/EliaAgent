#!/bin/zsh


set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/health_check_$(date +%Y%m%d).log"

mkdir -p "${SCRIPT_DIR}/logs"

echo "=== Health Check - $(date) ===" | tee -a "$LOG_FILE"


declare -A servers=(
    ["your-brand.com"]="https"
    ["your-saas.com"]="https"
    ["your-other-saas.com"]="http"
    ["your-agency.com"]="http"
)

ALL_OK=true

for domain in "${(@k)servers}"; do
    protocol=${servers[$domain]}
    url="${protocol}://${domain}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$url" 2>/dev/null || echo "000")
    
    if [[ "$response" == "200" ]]; then
        echo "✅ $domain: HTTP $response" | tee -a "$LOG_FILE"
    else
        echo "❌ $domain: HTTP $response" | tee -a "$LOG_FILE"
        ALL_OK=false
    fi
done


echo "" | tee -a "$LOG_FILE"
echo "=== API Health ===" | tee -a "$LOG_FILE"

for api in "your-brand.com" "your-saas.com"; do
    health=$(curl -s --connect-timeout 5 "https://${api}/api/health" 2>/dev/null || echo "{}")
    if echo "$health" | grep -q "ok"; then
        db_status=$(echo "$health" | grep -o '"db":[^,}]*' | cut -d: -f2)
        redis_status=$(echo "$health" | grep -o '"redis":[^,}]*' | cut -d: -f2)
        echo "✅ ${api}/api/health - db:${db_status} redis:${redis_status}" | tee -a "$LOG_FILE"
    else
        echo "❌ ${api}/api/health: FAIL" | tee -a "$LOG_FILE"
    fi
done

echo "" | tee -a "$LOG_FILE"
if $ALL_OK; then
    echo "✅ All servers OK" | tee -a "$LOG_FILE"
    exit 0
else
    echo "⚠️ Some servers failed" | tee -a "$LOG_FILE"
    exit 1
fi