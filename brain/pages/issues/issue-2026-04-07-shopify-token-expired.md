---
title: Shopify Admin Token Expired
type: issue
date: 2026-04-07
severity: high
status: open
recurring: false
tags: [bene2luxe, shopify, api, blocker, ben-20]
---

# Shopify Admin Token Expired

> [!links]+ Related
> [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] · [[../../wiki/people/Thomas-Cogne|Thomas]] · [[../../wiki/people/Wael|Wael]] · [[../../wiki/people/Rida|Rida]] · [[../../wiki/systems/Jira-Tickets-Index|Jira BEN-20]] · [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp B2LUXE]] · [[../../wiki/topics/Bene2Luxe-Timeline|Bene2Luxe Timeline]]

## What Happened

[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]'s Shopify Admin API token expired, blocking all automated product updates. This was discovered when [[../../wiki/people/Rida|Rida]] and [[../../wiki/people/Ali|Ali]] tried to add Balenciaga sizes 35-46 (task [[../../wiki/systems/Jira-Tickets-Index|BEN-20]]).

[[../../wiki/people/Thomas-Cogne|Thomas]] who handles [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] development couldn't access the Shopify API to make updates.

## Why This Matters for [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]

The [[../../wiki/businesses/B2LUXE-BUSINESS|B2LUXE BUSINESS]] workflow:
1. [[../../wiki/people/Wael|Wael]] sources luxury items
2. [[../../wiki/people/Rida|Rida]] coordinates product photos
3. [[../../wiki/people/Thomas-Cogne|Thomas]] adds to [[../../wiki/businesses/Bene2Luxe|Shopify store]]
4. Customers order via [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]

**Step 3 is blocked** - no new products can be added!

## Root Cause

This is a [[../bottlenecks/bottleneck-manual-dependencies|Manual Dependencies]] issue:

- **Token with [[../../wiki/people/Wael|Wael]]**: Only [[../../wiki/people/Wael|Wael]] can generate new tokens
- **No automation**: No refresh mechanism exists
- **[[../../wiki/people/Thomas-Cogne|Thomas]] blocked**: Cannot do his job without valid token

See [[../patterns/pattern-manual-dependencies|Manual Dependencies Pattern]].

## Impact on [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]

| Blocker | Task | Status |
|---------|------|--------|
| [[../../wiki/systems/Jira-Tickets-Index|BEN-20]] | Balenciaga sizes 35-46 | 🔴 Blocked |
| [[../../wiki/systems/Jira-Tickets-Index|BEN-21]] | Blouson LV Brûlé | 🔴 Blocked |
| New products | Adding inventory | 🔴 Blocked |

## Required Action ⚠️

[[../../wiki/people/Wael|Wael]] must:
1. Log into Shopify Admin
2. Go to Apps → Develop Apps
3. Create new Admin API token
4. Give to [[../../wiki/people/Thomas-Cogne|Thomas]] or [[../../wiki/people/Wael|Wael]] directly

## Jira Tracking

- [[../../wiki/systems/Jira-Tickets-Index|BEN-20]] - Shopify Token (Open)
- [[../../wiki/systems/Jira-Tickets-Index|BEN-21]] - Blouson LV (Blocked)

## Related Issues

- [[../issues/issue-2026-04-09-stripe-verification|Stripe Verification]] - Same [[../patterns/pattern-manual-dependencies|Manual Dependencies Pattern]]
- [[../issues/issue-2026-03-25-point-relais-blocked|Point Relais Blocked]] - Same pattern

## Prevention

1. **Calendar reminder** - Set 30 days before token expiry
2. **Token vault** - Store tokens in shared secure location
3. **Documentation** - Document token refresh process
4. **Alert system** - Auto-alert [[../../wiki/people/Wael|Wael]] before expiry

---

*Last updated: 2026-04-11*
*See also: [[../../wiki/topics/Bene2Luxe-Timeline|Bene2Luxe Timeline]]*
