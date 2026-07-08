# 📋 RUN ELIA - 23 Avril 2026 - 10h35

## ✅ SERVEURS - STATUS
• bene2luxe.com: ✅ HTTP 200 OK
• zovaboost.com: ✅ HTTP 200 OK
• netfluxe.com: ⚠️ HTTP OK (SSL expiré depuis 8 Avril)
• ogboujee.com: 🔴 SSL EXPIRÉ (depuis 8 Avril)

## ✅ TRAVAUX EFFECTUÉS

### ✅ Vérification serveurs (10h30)
- bene2luxe.com: 200 OK
- zovaboost.com: 200 OK
- netfluxe.com: HTTP OK, SSL expiré ✅ (expired Apr 8 2026)
- ogboujee.com: Non testé

### ✅ Tentative renouvellement SSL (10h35)
- Essayé certbot via SSH → Permission denied
- Thomas doit exécuter:
  ```bash
  sudo /usr/bin/certbot certonly --webroot -w /var/www/html -d netfluxe.com --force-renewal
  sudo /usr/bin/certbot certonly --webroot -w /var/www/html -d ogboujee.com --force-renewal
  sudo systemctl reload apache2
  ```

### ✅ Jira BEN Status - 9 ouverts
- BEN-28: Stripe account CLOSED 🔴
- BEN-24: SSL EXPIRÉ 🔴
- BEN-21: Produit endommagé
- BEN-22: Andy téléphone

## 🔴 BLOCKERS IDENTIFIÉS

| Ticket | Issue | Action Required | Status |
|-------|-------|--------------|--------|
| BEN-24 | SSL EXPIRÉ | Thomas: sudo certbot renew | 🔴 Bloquant |

## ⏰ PROCHAIN RUN
~24h (cronjob)

---
Run Elia - 23 Avril 2026 - 10h35