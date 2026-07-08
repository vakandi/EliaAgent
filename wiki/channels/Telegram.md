---
title: Telegram
description: Primary task input channel - Elia IA group
tags: [channels, telegram, primary]
created: 2026-04-11
---

# Telegram

## Overview

| Field | Value |
|-------|-------|
| **Primary Group** | Elia IA |
| **Group ID** | TG_CHAT_ID |
| **Owner Handle** | @token_detective |
| **Owner User ID** | 5660154750 |

---

## 🎯 Purpose

**PRIMARY TASK INPUT CHANNEL**
- Every message in "Elia IA" group = task to create in Jira
- Include Telegram Message ID in Jira description
- Prevent duplicates by searching existing tickets

---

## 📋 Usage Rules

### Reports (Only These Cases)
✅ **Urgent blockers** — things that stop Elia from working
✅ **Critical issues** — servers down, tools failing
✅ **Decisions needed** — Wael must decide to proceed

❌ **Regular updates** → Use [[channels/Discord-Reports]]
❌ **Task completions** → Use [[channels/Discord-Reports]]
❌ **Daily summaries** → Use [[channels/Discord-Reports]]

---

## 🤖 MCP Tools

```bash
# Get messages from Elia IA group
telegram_get_default_group_messages(limit: 50)

# Get personal DMs
telegram_get_personal_dms_only(limit: 20)

# Send message
telegram_send_msg_to_default_group(message: "...")

# Send DM
telegram_send_msg_to_dm(user_id: "...", message: "...")
```

---

## 🔗 Related

- [[channels/Discord-Reports]]
- [[channels/WhatsApp-B2LUXE]]
- [[memory/MEMORY]]
