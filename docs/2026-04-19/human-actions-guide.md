# Human Actions Required - 19 Avril 2026

## 🔴 WAEL - STRIPE Account (BEN-28)
**Deadline: 21 Avril 2026 (2 jours!)**

### Login:
- https://dashboard.stripe.com/b/acct_1SzQwSFgCWjq1hBb
- Ou: https://support.stripe.com/express/contact

### Steps:
1. Login to Stripe dashboard
2. Look for "Request Review" or "Appeal" button
3. Fill form with:
   - Business registration docs
   - Order receipts (last 30-60 days)
   - Shipping confirmations
   - Explanation letter (factual, professional)
4. Submit within 48 hours

### Quick Reference:
- Appeal typically takes 2-7 business days
- Provide all documents upfront
- Stay factual, no emotional language

---

## 🔴 THOMAS - SSL Certificates (BEN-24)

### Commands (from VPS):
```bash
# SSH to server, then:
sudo certbot certonly --webroot -w /home/vakandi/multisaasdeploy/unified-acme-challenge -d netfluxe.com --force-renewal
sudo certbot certonly --webroot -w /home/vakandi/multisaasdeploy/unified-acme-challenge -d ogboujee.com --force-renewal

# Or via Docker:
docker exec apache_unified_server certbot certonly --webroot -w /usr/local/apache2/htdocs -d netfluxe.com --force-renewal
docker exec apache_unified_server certbot certonly --webroot -w /usr/local/apache2/htdocs -d ogboujee.com --force-renewal

# Then restart Apache:
docker restart apache_unified_server
```

### Alternative (from Mac with SSH):
```bash
mcp-cli call ssh-server-multisaasdeploy execute-command '{"cmdString":"sudo /usr/bin/certbot..."}'
```

---

## 📋 Other Tasks for Team

### Wael (Jira):
- BEN-29: GTM implementation
- BEN-27: Répondre à qutiee_me
- BEN-26: hostedemail password
- BEN-25: WhatsApp bridges restart
- BEN-22: Andy phone number
- BEN-21: LV jacket damaged

---
*Generated: 2026-04-19 by Elia*
*Human actions required - Elia cannot automate these*