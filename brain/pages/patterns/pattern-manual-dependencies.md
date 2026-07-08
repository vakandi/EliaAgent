---
title: Manual Dependencies Pattern
type: pattern
date: 2026-04-11
severity: high
status: recurring
tags: [blockers, manual-action, wael-dependency, recurring]
---

# Manual Dependencies Pattern

> [!links]+ Related
> [[../bottlenecks/bottleneck-manual-dependencies|Manual Dependencies]] · [[../issues/issue-2026-04-09-stripe-verification|Stripe]] · [[../issues/issue-2026-04-07-shopify-token-expired|Shopify]] · [[../issues/issue-2026-03-25-point-relais-blocked|Point Relais]] · [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] · [[../../wiki/businesses/B2LUXE-BUSINESS|B2LUXE BUSINESS]] · [[../../wiki/people/Wael|Wael]] · [[../../wiki/people/Thomas-Cogne|Thomas]] · [[../../wiki/people/Ali|Ali]] · [[../../wiki/people/Rida|Rida]]

## Description

Many [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] workflows are blocked waiting for manual action from [[../../wiki/people/Wael|Wael]] or team members. [[../../wiki/people/Elia|Elia]] cannot complete these autonomously.

This is the #1 cause of stalled progress in [[../../wiki/businesses/B2LUXE-BUSINESS|B2LUXE BUSINESS]] operations.

## Evidence

| Date | Blocked Task | Waiting On | Business |
|------|--------------|------------|----------|
| 2026-04-09 | [[../issues/issue-2026-04-09-stripe-verification|Stripe Verification]] | [[../../wiki/people/Wael|Wael]] | [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] |
| 2026-04-07 | [[../issues/issue-2026-04-07-shopify-token-expired|Shopify Token]] | [[../../wiki/people/Wael|Wael]] | [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] |
| 2026-03-25 | [[../issues/issue-2026-03-25-point-relais-blocked|Point Relais Password]] | [[../../wiki/people/Wael|Wael]] | [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] |
| 2026-04-01 | [[../../wiki/businesses/Netfluxe|Netfluxe]] SSL | [[../../wiki/people/Thomas-Cogne|Thomas]] | [[../../wiki/businesses/Netfluxe|Netfluxe]] |

## Why This Blocks [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]

The [[../../wiki/businesses/B2LUXE-BUSINESS|B2LUXE BUSINESS]] [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp workflow]] depends on:

```
Customer → WhatsApp → Ali/Rida → Payment (Stripe) → Shopify (Thomas) → Ship
     ↑           ↑           ↑           ↑              ↑
  Manual?    Manual?    Manual?     BLOCKED!         BLOCKED!
```

[[../../wiki/people/Ali|Ali]] and [[../../wiki/people/Rida|Rida]] can't finalize orders without Stripe.
[[../../wiki/people/Thomas-Cogne|Thomas]] can't update products without Shopify token.

## Root Cause Analysis

| Cause | Evidence | Impact |
|-------|----------|--------|
| **Credentials only with [[../../wiki/people/Wael|Wael]]** | Passwords, tokens, logins | Team stuck |
| **No delegation system** | Every decision needs [[../../wiki/people/Wael|Wael]] | Bottleneck |
| **Identity requirements** | Stripe needs human verification | Can't automate |
| **No shared vault** | Thomas/Ali can't access accounts | Blocked |

## Impact on [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]

- 🔴 **Automation blocked** - Can't build auto workflows
- 🔴 **Team frustrated** - [[../../wiki/people/Thomas-Cogne|Thomas]], [[../../wiki/people/Ali|Ali]] ready but waiting
- 🔴 **[[../../wiki/people/Wael|Wael]] overwhelmed** - Constant reminders needed
- 🔴 **Revenue delayed** - Orders stuck waiting for payment

## Solutions

### Short-term (This Week)
1. **Shared password doc** - List all accounts needed
2. **Credential handover** - Give [[../../wiki/people/Thomas-Cogne|Thomas]] access to Shopify
3. **Decision matrix** - What can be done without [[../../wiki/people/Wael|Wael]] approval

### Medium-term (This Month)
1. **Password manager** - 1Password/Bitwarden team vault
2. **OAuth integration** - Remove manual token handling
3. **Approval rules** - Pre-approved actions for common cases

### Long-term (Q2)
1. **SSO everywhere** - Single login for all services
2. **Auto-renewal** - Tokens and certs auto-refresh
3. **Webhook approval** - API-based approval workflow

## Related Pages

- [[../bottlenecks/bottleneck-manual-dependencies|Manual Dependencies Bottleneck]] - Detailed analysis
- [[../issues/issue-2026-04-09-stripe-verification|Stripe Verification]] - Current blocker
- [[../issues/issue-2026-04-07-shopify-token-expired|Shopify Token]] - Current blocker
- [[../issues/issue-2026-03-25-point-relais-blocked|Point Relais]] - Current blocker

## How to Break This Pattern

1. **Start with Shopify** - Get [[../../wiki/people/Thomas-Cogne|Thomas]] full access
2. **Then Stripe** - Define what's needed for verification
3. **Then credentials** - Centralize passwords
4. **Then automation** - Build auto-renewal for tokens/certs

---

*Pattern identified: 2026-04-11*
*Status: Recurring - Multiple instances documented*
