# Next Run Prep - 17 Avril 2026 09h00

## 🚨 CRITICAL - Action Required NOW

### 1. Wael - STRIPE (BEN-28)
**Login**: https://dashboard.stripe.com/b/acct_1SzQwSFgCWjq1hBb
**Problem**: Account CLOSED, ~€6,000+ blocked
**Deadline**: 5 business days from April 16 (refunds start April 21)
**Action**: Fill out appeal form, provide business documentation

### 2. Thomas - SSL Certificates (BEN-24)
**Command to run**:
```bash
sudo /usr/bin/certbot certonly --webroot -w /var/www/html -d ogboujee.com -d netfluxe.com --force-renewal --non-interactive
```
**Problem**: Certificates expired since April 8

---

## 📊 Current Status

| Site | Status |
|------|--------|
| bene2luxe.com | ✅ OK |
| zovaboost.com | ✅ OK |
| ogboujee.com | ❌ SSL Expired |
| netfluxe.com | ❌ SSL Expired |

**Docker**: 19 containers healthy ✅

---

## 📋 Pending Jira Tickets

| Ticket | Priority | Action |
|--------|----------|--------|
| BEN-28 | 🔴 CRITICAL | Stripe appeal - Wael |
| BEN-24 | 🔴 | SSL renewal - Thomas |
| BEN-27 | 🟡 | qutiee_me Telegram |
| BEN-26 | 🟡 | hostedemail password |
| BEN-25 | 🟡 | WhatsApp bridges |
| ELIA-8 | 🟡 | Swissquote closure |

---

## ✅ Completed This Run

1. ✅ Infrastructure check (bene2luxe.com, zovaboost.com OK)
2. ✅ SSL issue investigated - found expired certs
3. ✅ Attempted certbot renewal - blocked by sudo
4. ✅ Discord alert sent (#urgent)
5. ✅ Telegram alert sent
6. ✅ Documentation saved

---

## 📝 Docs Created

- `/Users/vakandi/EliaAI/docs/2026-04-17/run_17_avril_2026_0900.md` - Full run report
- `/Users/vakandi/EliaAI/docs/2026-04-17/SSL_RENEWAL_FIX.md` - SSL fix instructions
