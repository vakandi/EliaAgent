---
title: MCP Tools
description: External service integrations via mcp-cli
tags: [tools, mcp, integrations]
created: 2026-04-11
---

# MCP Tools

## Overview

MCP (Model Context Protocol) tools connect Elia to external services.

---

## 🔧 Tool Categories

### Communication
| Tool | Service | Commands |
|------|---------|----------|
| `telegram` | Telegram | send_msg, get_messages, get_dms |
| `whatsapp` | WhatsApp | send_message, list_chats, download_media |
| `discord-mcp` | Discord | get_dms, send_dm, send_group_message |

### Business
| Tool | Service | Commands |
|------|---------|----------|
| `mcp-atlassian` | Jira | create_issue, get_project_issues |
| `gmail` | Gmail | search_emails, send_email |
| `mail_contact_*` | IONOS | list_emails, send_email |

### Infrastructure
| Tool | Service | Commands |
|------|---------|----------|
| `ssh-server-*` | SSH | execute-command |

---

## 🚀 Common Commands

### Telegram
```bash
# Get messages from Elia IA group
mcp-cli call telegram get_default_group_messages '{"limit":50}'

# Send message
mcp-cli call telegram send_msg_to_default_group '{"message":"..."}'

# Get personal DMs
mcp-cli call telegram get_personal_dms_only '{"limit":20}'
```

### WhatsApp
```bash
# List chats
mcp-cli call whatsapp list_chats '{"limit":80}'

# Get messages
mcp-cli call whatsapp list_messages '{"chat_jid":"...","limit":80}'

# Send message
mcp-cli call whatsapp send_message '{"recipient":"...","message":"..."}'
```

### Jira
```bash
# Create ticket
mcp-cli call mcp-atlassian create_issue \
  '{"project":"BEN","summary":"...","description":"...","issue_type":"Task"}'
```

### SSH
```bash
# Execute command on server
mcp-cli call ssh-server-multisaasdeploy execute-command \
  '{"cmdString":"ls -la /var/www/"}'
```

---

## 🔗 Related

- [[systems/Elia-System]]
- [[channels/Telegram]]
- [[channels/WhatsApp-COBOU]]
