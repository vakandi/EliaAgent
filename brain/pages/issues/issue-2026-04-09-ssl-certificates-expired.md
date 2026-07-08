---
title: SSL Certificate Expiration
type: issue
date: 2026-04-09
severity: medium
status: open
recurring: true
tags: [infrastructure, ssl, certificates, netfluxe, ogboujee, monitoring]
---

# SSL Certificate Expiration

> [!links]+ Related
> [[../../wiki/businesses/Netfluxe|Netfluxe]] · [[../../wiki/businesses/OGBoujee|OGBoujee]] · [[../../wiki/businesses/ZovaBoost|ZovaBoost]] · [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] · [[../../wiki/people/Thomas-Cogne|Thomas]] · [[../../wiki/people/Wael|Wael]] · [[../../wiki/channels/Telegram|Telegram]] · [[../../wiki/systems/Docker-Servers|Docker Servers]] · [[../../wiki/topics/Infrastructure-Timeline|Infrastructure]]

## What Happened

SSL certificates for two domains expired without automated detection:

| Domain | Business | Status | Expired |
|--------|----------|--------|---------|
| [[../../wiki/businesses/Netfluxe|netfluxe.com]] | [[../../wiki/businesses/Netfluxe|Netfluxe]] | ❌ Expired | April 8 |
| [[../../wiki/businesses/OGBoujee|ogboujee.com]] | [[../../wiki/businesses/OGBoujee|OGBoujee]] | ❌ Expired | April 8 |

Alert came via [[../../wiki/channels/Telegram|Telegram]] - someone noticed they couldn't access the sites securely.

## Why This Matters for [[../../wiki/businesses/OGBoujee|OGBoujee]] and [[../../wiki/businesses/Netfluxe|Netfluxe]]

Without HTTPS:
- 🔴 **Security warnings** in browsers
- 🔴 **No payments** - Stripe requires HTTPS
- 🔴 **SEO impact** - Google downranks non-HTTPS
- 🔴 **Trust loss** - Customers see "Not Secure"

[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] had similar risk - [[../../wiki/channels/Telegram|Telegram]] alerted the team.

## Root Cause

This is a [[../patterns/pattern-ssl-expiration|SSL Expiration Pattern]]:

- **No monitoring**: Certificates not tracked for expiration
- **Manual renewal**: [[../../wiki/people/Thomas-Cogne|Thomas]] does manually when reminded
- **Certbot works**: But needs human to trigger renewal
- **Docker complicates**: Certs managed in Docker containers

See [[../patterns/pattern-ssl-expiration|SSL Expiration Pattern]].

## Impact by Business

| Business | Impact | Payments Blocked? |
|----------|--------|-------------------|
| [[../../wiki/businesses/OGBoujee|OGBoujee]] | HIGH | Yes |
| [[../../wiki/businesses/Netfluxe|Netfluxe]] | MEDIUM | Yes |
| [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] | LOW | Already has HTTPS |

## Resolution ⚠️ PARTIEL

| Domain | Status | Method | Date |
|--------|--------|--------|------|
| [[../../wiki/businesses/OGBoujee|ogboujee.com]] | ❌ Expired | certbot Docker | April 10 (renewed) - expired again |
| [[../../wiki/businesses/Netfluxe|netfluxe.com]] | ❌ Expired | Pending IONOS manual | April 8 |

**NOTE (2026-04-14)**: Both ogboujee.com et netfluxe.com SSL sont toujours expirés.
- HTTPS: FAIL
- HTTP: 200 OK
- Action requise: Login IONOS ou SSH direct serveur

See [[../improvements/improvement-2026-04-10-ogboujee-ssl-fixed|OGBoujee SSL Fixed]] for resolution details.

## Infrastructure Context (2026-04-14)

All sites run on [[../../wiki/systems/Docker-Servers|Docker Servers]]:
- [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]: https://bene2luxe.com ✅
- [[../../wiki/businesses/ZovaBoost|ZovaBoost]]: https://zovaboost.com ✅
- [[../../wiki/businesses/OGBoujee|OGBoujee]]: http://ogboujee.com ⚠️ (HTTPS FAIL)
- [[../../wiki/businesses/Netfluxe|Netfluxe]]: http://netfluxe.com ⚠️ (HTTPS FAIL)

## Prevention

1. **SSL monitoring script** - Check expiration daily
2. **Auto-renewal** - certbot renew in cron
3. **Telegram alerts** - 30, 14, 7 days before expiry
4. **Health checks** - Include SSL in [[../../wiki/systems/Docker-Servers|server checks]]

---

*Status: OPEN (2026-04-14)*
*See also: [[../../wiki/topics/Infrastructure-Timeline|Infrastructure Timeline]]*
