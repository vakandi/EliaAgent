---
title: Manual Dependencies Bottleneck
type: bottleneck
date: 2026-04-11
severity: high
status: open
tags: [automation, manual-work, wael-dependency, blockers]
---

# Manual Dependencies Bottleneck

> [!links]+ Related
> [[../patterns/pattern-manual-dependencies|Manual Dependencies Pattern]] · [[../issues/issue-2026-04-09-stripe-verification|Stripe Verification]] · [[../issues/issue-2026-04-07-shopify-token-expired|Shopify Token]] · [[../issues/issue-2026-03-25-point-relais-blocked|Point Relais]] · [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] · [[../../wiki/businesses/B2LUXE-BUSINESS|B2LUXE BUSINESS]] · [[../../wiki/people/Wael|Wael]] · [[../../wiki/people/Thomas-Cogne|Thomas]] · [[../../wiki/people/Ali|Ali]] · [[../../wiki/people/Rida|Rida]] · [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp B2LUXE]]

## What It Is

Many [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] workflows are blocked waiting for manual action from [[../../wiki/people/Wael|Wael]] or team members. [[../../wiki/people/Elia|Elia]] cannot complete these autonomously.

This is the **#1 blocker** for [[../../wiki/businesses/B2LUXE-BUSINESS|B2LUXE BUSINESS]] operations.

## Why This Blocks [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]

The [[../../wiki/businesses/B2LUXE-BUSINESS|B2LUXE BUSINESS]] [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp workflow]]:

```
Customer → WhatsApp → Ali/Rida → Payment (Stripe) → Shopify (Thomas) → Ship
     ↑           ↑           ↑           ↑              ↑
  Manual?    Manual?    Manual?     BLOCKED!         BLOCKED!
```

[[../../wiki/people/Ali|Ali]] and [[../../wiki/people/Rida|Rida]] can't finalize orders without Stripe.
[[../../wiki/people/Thomas-Cogne|Thomas]] can't update products without Shopify token.

## Evidence - All Blocked Tasks

| Task | Issue | Waiting On | Jira | Priority |
|------|-------|------------|------|----------|
| [[../issues/issue-2026-04-09-stripe-verification|Stripe Verification]] | Identity required | [[../../wiki/people/Wael|Wael]] | [[../../wiki/systems/Jira-Tickets-Index|BEN-23]] | 🔴 CRITICAL |
| [[../issues/issue-2026-04-07-shopify-token-expired|Shopify Token]] | Token expired | [[../../wiki/people/Wael|Wael]] | [[../../wiki/systems/Jira-Tickets-Index|BEN-20]] | 🔴 HIGH |
| [[../issues/issue-2026-03-25-point-relais-blocked|Point Relais Password]] | Password unknown | [[../../wiki/people/Wael|Wael]] | - | 🟡 MEDIUM |
| [[../../wiki/businesses/Netfluxe|Netfluxe]] SSL | Not renewed | [[../../wiki/people/Thomas-Cogne|Thomas]] | - | 🟡 MEDIUM |

## Root Cause Analysis

| Cause | Evidence | Impact |
|-------|----------|--------|
| **Credentials only with [[../../wiki/people/Wael|Wael]]** | Passwords, tokens, logins | Team stuck |
| **No delegation system** | Every decision needs [[../../wiki/people/Wael|Wael]] | Bottleneck |
| **Identity requirements** | Stripe needs human verification | Can't automate |
| **No shared vault** | Thomas/Ali can't access accounts | Blocked |

## Impact Assessment

| Impact | Severity | Details |
|--------|----------|---------|
| **Revenue blocked** | 🔴 CRITICAL | No Stripe = no payments |
| **Team frustrated** | 🔴 HIGH | Thomas, Ali, Rida ready but waiting |
| **[[../../wiki/people/Wael|Wael]] overwhelmed** | 🔴 HIGH | Constant reminders needed |
| **Elia appears ineffective** | 🟡 MEDIUM | Can't complete tasks alone |
| **Growth limited** | 🔴 HIGH | Can't scale manual processes |

## Why [[../../wiki/people/Elia|Elia]] Can't Help

| Task | Why Elia Blocked |
|------|-----------------|
| [[../issues/issue-2026-04-09-stripe-verification|Stripe Verification]] | Requires human identity |
| [[../issues/issue-2026-04-07-shopify-token-expired|Shopify Token]] | Token only with Wael |
| [[../issues/issue-2026-03-25-point-relais-blocked|Point Relais]] | Password only with Wael |

## Solutions

### Immediate (This Week)
- [ ] **Share credentials** - Give Thomas Shopify access
- [ ] **Document all accounts** - List every login needed
- [ ] **Decision matrix** - What can proceed without Wael

### Short-term (This Month)
- [ ] **Password manager** - 1Password/Bitwarden team vault
- [ ] **Credential handover** - Transfer critical access
- [ ] **Approval workflow** - Define pre-approved actions

### Long-term (Q2)
- [ ] **SSO everywhere** - Single login for all services
- [ ] **Auto-renewal** - Tokens and certs auto-refresh
- [ ] **Webhook approvals** - API-based approval workflow

## Related Pages

- [[../patterns/pattern-manual-dependencies|Manual Dependencies Pattern]] - Detailed analysis
- [[../issues/issue-2026-04-09-stripe-verification|Stripe Verification]] - Current blocker
- [[../issues/issue-2026-04-07-shopify-token-expired|Shopify Token]] - Current blocker
- [[../issues/issue-2026-03-25-point-relais-blocked|Point Relais]] - Current blocker

---

*Status: Open*
*Severity: HIGH*
*Impact: Blocking all automated workflows*
