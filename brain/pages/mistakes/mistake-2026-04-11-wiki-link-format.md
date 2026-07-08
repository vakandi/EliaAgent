---
title: Wiki Link Format Inconsistency
type: mistake
date: 2026-04-11
severity: low
status: resolved
recurring: true
tags: [wiki, obsidian, links, documentation, format]
---

# Wiki Link Format Inconsistency

> [!links]+ Related
> [[../../wiki/HOME|Wiki Hub]] · [[../../wiki/OBSIDIAN-LINKING-GUIDE|Linking Guide]] · [[../../wiki/docs/Docs-Index|Docs Index]] · [[../../wiki/index|Wiki Index]] · [[../analysis/analysis-2026-04-11|Apr 11 Analysis]] · [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] · [[../../wiki/people/Wael|Wael]]

## What Happened

Created wiki links with wrong format in [[../../wiki/docs/Docs-Index|Docs folder]], causing broken links in Obsidian.

## The Problem

| Format | Used | Correct |
|--------|------|---------|
| **Wrong** | `[[../wiki/businesses/Bene2Luxe\|Bene2Luxe]]` | ❌ Broke graph view |
| **Correct** | `[[wiki/businesses/Bene2Luxe\|Bene2Luxe]]` | ✅ Resolved |

Files affected in [[../../wiki/docs/Docs-Index|Docs]]:
- 11+ session reports
- Morning briefings
- Run reports

## Root Cause

1. **Didn't test** - Created 50+ links without verifying in Obsidian
2. **Assumed paths** - Thought `../wiki/` would resolve
3. **Didn't read docs** - [[../../wiki/OBSIDIAN-LINKING-GUIDE|Obsidian linking rules]] exist
4. **Bulk creation** - Made many links at once, harder to catch errors

## Impact

| Impact | Severity | Details |
|--------|----------|---------|
| **Broken graph** | 🟡 MEDIUM | Links not showing in Obsidian |
| **Manual fix needed** | 🟢 LOW | 11 docs to update |
| **Time lost** | 🟢 LOW | ~10 minutes to fix |
| **Confusion** | 🟢 LOW | [[../../wiki/people/Wael|Wael]] confused |

## Why Obsidian Links Matter

Obsidian wiki links power:
- **Graph view** - Visual connections between notes
- **Backlinks** - See what links to what
- **Navigation** - Click through related topics
- **[[../../wiki/index|Wiki Index]]** - Connected knowledge base

Without proper links, the [[../../wiki/HOME|Wiki Hub]] becomes a collection of isolated pages.

## Resolution

1. ✅ Fixed all 11+ affected docs
2. ✅ Created [[../../wiki/OBSIDIAN-LINKING-GUIDE|Obsidian Linking Guide]]
3. ✅ Verified all [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] links work
4. ✅ Documented in [[../AGENTS.md|AGENTS.md]]

## Prevention - Link Rules

| Rule | Example |
|------|---------|
| **From docs/ to wiki/** | `[[wiki/businesses/Bene2Luxe\|Bene2Luxe]]` |
| **From brain/ to wiki/** | `[[../../wiki/businesses/Bene2Luxe\|Bene2Luxe]]` |
| **Within brain/** | `[[../issues/issue-2026-04-09-stripe-verification\|Stripe]]` |
| **Always test** | Open in Obsidian, check graph view |

## Related Pages

- [[../../wiki/OBSIDIAN-LINKING-GUIDE|Obsidian Linking Guide]] - Official rules
- [[../../wiki/docs/Docs-Index|Docs Index]] - Fixed documents
- [[../../wiki/HOME|Wiki Hub]] - Central wiki hub
- [[../../wiki/index|Wiki Index]] - Master index
- [[../analysis/analysis-2026-04-11|Apr 11 Analysis]] - When this happened

---

*Mistake identified: 2026-04-11*
*All links now verified working*
