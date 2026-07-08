---
title: Point Relais Registration Blocked
type: issue
date: 2026-03-25
severity: medium
status: open
recurring: false
tags: [bene2luxe, shipping, point-relais, hostedemail, cobibou-distribution]
---

# Point Relais Registration Blocked

> [!links]+ Related
> [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] · [[../../wiki/businesses/CoBou-Agency|CoBou Agency]] · [[../../wiki/businesses/B2LUXE-BUSINESS|B2LUXE BUSINESS]] · [[../../wiki/people/Wael|Wael]] · [[../../wiki/people/Thomas-Cogne|Thomas]] · [[../../wiki/people/Ali|Ali]] · [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp B2LUXE]] · [[../../wiki/topics/Infrastructure-Timeline|Infrastructure]]

## What Happened

[[../../wiki/businesses/CoBou-Agency|CoBou Agency]] (Thomas's company) was trying to register [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] for Point Relais shipping when they hit a blocker:

- **Account**: contact@cofibou-distribution.com (Cofibou Distribution)
- **Issue**: Password for hostedemail unknown
- **Blocked**: [[../../wiki/people/Thomas-Cogne|Thomas]] can't complete registration

This was discussed in [[../../wiki/businesses/B2LUXE-BUSINESS|B2LUXE BUSINESS]] [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp group]] between [[../../wiki/people/Wael|Wael]], [[../../wiki/people/Ali|Ali]], and [[../../wiki/people/Rida|Rida]].

## Why This Matters

[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] needs multiple shipping options:

| Current | Needed | Status |
|---------|--------|--------|
| Standard shipping | ✅ Available | Working |
| Express shipping | ✅ Available | Working |
| Point Relais | ❌ Blocked | Needs registration |

**Point Relais** is popular in France - adds convenience for customers who want to pick up at local shop.

## Root Cause - [[../bottlenecks/bottleneck-manual-dependencies|Manual Dependencies]]

This is a classic [[../patterns/pattern-manual-dependencies|Manual Dependencies Pattern]]:

- **Password only with [[../../wiki/people/Wael|Wael]]**: No one else can access hostedemail
- **No shared credential system**: [[../../wiki/people/Thomas-Cogne|Thomas]] stuck waiting
- **[[../../wiki/businesses/B2LUXE-BUSINESS|Team]] blocked**: [[../../wiki/people/Ali|Ali]] can't finalize shipping setup

## Impact on [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]

- **Customer experience**: Fewer delivery options
- **Competitive disadvantage**: Other sellers have Point Relais
- **Team frustration**: [[../../wiki/people/Thomas-Cogne|Thomas]] ready to complete but can't

## Required Action ⚠️

[[../../wiki/people/Wael|Wael]] must provide:
1. Password for hostedemail: contact@cofibou-distribution.com
2. Give to [[../../wiki/people/Thomas-Cogne|Thomas]] or store in shared system

## Related Issues

- [[../issues/issue-2026-04-09-stripe-verification|Stripe Verification]] - Same [[../patterns/pattern-manual-dependencies|Manual Dependencies Pattern]]
- [[../issues/issue-2026-04-07-shopify-token-expired|Shopify Token]] - Same pattern

## Prevention

1. **Password manager** - Use 1Password/Bitwarden for team
2. **Credential doc** - List all accounts with access
3. **Shared vault** - Give [[../../wiki/people/Thomas-Cogne|Thomas]] access to needed accounts
4. **Process doc** - How to add new shipping carriers

---

*Last updated: 2026-04-11*
*See also: [[../../wiki/topics/Infrastructure-Timeline|Infrastructure Timeline]]*
