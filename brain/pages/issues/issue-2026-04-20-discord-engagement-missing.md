---
title: Issue - Discord Engagement Missing
type: issue
date: 2026-04-20
severity: high
status: resolved
tags: [discord, engagement, passive-behavior]
---

# Issue - Discord Engagement Missing

## What Happened
PROMPT.md had 832 lines but Elia wasn't engaging on Discord - she just read messages without posting updates.

## Root Cause
- Passive "analyze → report → done" pattern (bottleneck: passive-behavior)
- No mandatory engagement rules
- No "INITIATE discussion" requirement
- 70%+ null runs

## Impact
- Team doesn't know what's happening
- Elia perceived as not helpful
- No real coordination on Discord

## Resolution
Modified PROMPT.md with:
1. **Mandatory: INITIATE & ENGAGE** section - NEW
2. **Discord Engagement Rules** - Must post to channels, not just read
3. **WhatsApp Engagement Rules** - Must say something every run
4. **Relance Rules** - Must follow up on "en attente" items
5. **Simplified Reporting** - Post to proper channels
6. **DON'T DO THIS table** - Shows wrong vs correct behavior

## Prevention
- Check engagement metrics every run
- If null_run → auto-initiate
- Track "posted to Discord" in metrics

---

*Status: RESOLVED*
*Date: 2026-04-20*