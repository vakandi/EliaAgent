---
title: SSL Certificate Expiration Pattern
type: pattern
date: 2026-04-11
severity: medium
status: recurring
tags: [ssl, certificates, infrastructure, monitoring, expiration]
---

# SSL Certificate Expiration Pattern

> [!links]+ Related
> [[../issues/issue-2026-04-09-ssl-certificates-expired|SSL Certificates]] · [[../../wiki/businesses/Netfluxe|Netfluxe]] · [[../../wiki/businesses/OGBoujee|OGBoujee]] · [[../../wiki/businesses/ZovaBoost|ZovaBoost]] · [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] · [[../../wiki/people/Thomas-Cogne|Thomas]] · [[../../wiki/people/Wael|Wael]] · [[../../wiki/channels/Telegram|Telegram]] · [[../../wiki/systems/Docker-Servers|Docker Servers]] · [[../../wiki/topics/Infrastructure-Timeline|Infrastructure]]

## Description

SSL certificates for [[../../wiki/businesses/Netfluxe|Netfluxe]] and [[../../wiki/businesses/OGBoujee|OGBoujee]] expired without automated detection, causing service degradation. This is a recurring [[../../wiki/topics/Infrastructure-Timeline|infrastructure]] issue.

## Evidence

| Domain | Business | Expired | Detected By | Impact |
|--------|----------|---------|-------------|--------|
| [[../../wiki/businesses/Netfluxe|netfluxe.com]] | [[../../wiki/businesses/Netfluxe|Netfluxe]] | April 8 | [[../../wiki/channels/Telegram|Telegram]] | 🔴 No HTTPS |
| [[../../wiki/businesses/OGBoujee|ogboujee.com]] | [[../../wiki/businesses/OGBoujee|OGBoujee]] | April 8 | [[../../wiki/channels/Telegram|Telegram]] | 🔴 No HTTPS |
| (prior incidents) | Unknown | Unknown | User reports | Varies |

## Why This Matters for All Businesses

Every site needs HTTPS:

| Business | Domain | SSL Status |
|----------|---------|------------|
| [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] | bene2luxe.com | ✅ Valid |
| [[../../wiki/businesses/ZovaBoost|ZovaBoost]] | zovaboost.com | ✅ Valid |
| [[../../wiki/businesses/OGBoujee|OGBoujee]] | ogboujee.com | ✅ Fixed (April 10) |
| [[../../wiki/businesses/Netfluxe|Netfluxe]] | netfluxe.com | ⚠️ Still HTTP only |

## Root Cause Analysis

| Issue | Details | Why It Happens |
|-------|---------|----------------|
| **No monitoring** | No script checks expiration | Forgot to add |
| **Certbot partial** | Renews but no alert | Config not complete |
| **Human-dependent** | [[../../wiki/people/Thomas-Cogne|Thomas]] must remember | No automation |
| **Docker complexity** | Certs in containers | Harder to manage |

## Impact on Businesses

| Impact | Details | Severity |
|--------|---------|----------|
| **Security warnings** | Browser shows "Not Secure" | 🔴 HIGH |
| **No payments** | Stripe requires HTTPS | 🔴 CRITICAL |
| **SEO drop** | Google penalizes HTTP | 🟡 MEDIUM |
| **Trust loss** | Customers leave | 🔴 HIGH |

## The Fix - [[../improvements/improvement-2026-04-10-ogboujee-ssl-fixed|OGBoujee SSL Fixed]]

[[../../wiki/people/Thomas-Cogne|Thomas]] fixed [[../../wiki/businesses/OGBoujee|OGBoujee]] by running:
```bash
docker exec certbot certbot renew
```

Certificate now valid until **July 9, 2026**.

## Prevention - Automation Required

### Daily Health Check Script
```bash
#!/bin/bash
# Check all domains
for domain in bene2luxe.com zovaboost.com ogboujee.com netfluxe.com; do
  expiry=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2)
  days_left=$(($(date -d "$expiry" +%s) - $(date +%s) / 86400))
  if [ $days_left -lt 30 ]; then
    curl -X POST "https://ntfy.sh/YOUR_TOPIC" -d "⚠️ $domain SSL expires in $days_left days"
  fi
done
```

### Cron Setup
```bash
# Every day at 9am
0 9 * * * /opt/scripts/ssl-check.sh

# Auto-renew weekly
0 3 * * 0 docker exec certbot certbot renew --quiet
```

### Alert Thresholds
| Days Remaining | Action | Channel |
|---------------|--------|---------|
| 30 days | Warning | [[../../wiki/channels/Telegram|Telegram]] |
| 14 days | Alert | [[../../wiki/channels/Telegram|Telegram]] |
| 7 days | URGENT | [[../../wiki/channels/Telegram|Telegram]] + SMS |
| 1 day | CRITICAL | Call [[../../wiki/people/Thomas-Cogne|Thomas]] |

## Related Pages

- [[../issues/issue-2026-04-09-ssl-certificates-expired|SSL Certificates Expired]] - Recent incident
- [[../improvements/improvement-2026-04-10-ogboujee-ssl-fixed|OGBoujee SSL Fixed]] - Resolution
- [[../../wiki/systems/Docker-Servers|Docker Servers]] - Where certs live
- [[../../wiki/topics/Infrastructure-Timeline|Infrastructure Timeline]] - Historical context

---

*Pattern identified: 2026-04-11*
*Status: Recurring - Automation needed*
