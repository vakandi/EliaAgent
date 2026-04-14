---
name: mcp-cli
description: Access external services via mcp-cli wrapper (WhatsApp, Telegram, Discord, Jira, SSH, Gmail). Use skill(name="mcp-cli") to load this skill before calling any mcp-cli commands.
---

# MCP-CLI Skill

## ⚠️ CRITICAL: How to Call

**ALWAYS use the `bash` tool** to execute mcp-cli commands:

```
<invoke name="bash">
  <command>mcp-cli call <server> <tool> '<json-arguments>'</command>
</invoke>
```

## Available Servers & Tools

### Telegram
```bash
mcp-cli call telegram get_default_group_messages '{"limit":20}'
mcp-cli call telegram send_msg_to_default_group '{"message":"Hello"}'
mcp-cli call telegram get_personal_dms_only '{"limit":20}'
mcp-cli call telegram send_msg_to_recipient '{"recipient":"@username","message":"..."}'
```

⚠️ **IMPORTANT: When to use Telegram send_msg_to_default_group:**
- **ONLY for URGENT matters/blockers** — things Wael needs to fix ASAP so Elia can proceed with tasks on next runs
- **NOT for regular reports** — use Discord #reports (ELIA-HQ) for regular reports
- Reason: Telegram catches Wael's attention immediately for blocking issues only

### WhatsApp
```bash
mcp-cli call whatsapp list_chats '{"limit":20}'
mcp-cli call whatsapp list_messages '{"chat_jid":"120363408208578679@g.us","limit":30}'
mcp-cli call whatsapp send_message '{"recipient":"120363420711538035@g.us","message":"Hello"}'
mcp-cli call whatsapp download_media '{"message_id":"...","chat_jid":"..."}'
```

### Jira
```bash
mcp-cli call mcp-atlassian create_issue '{"project":"BEN","summary":"...","description":"...","issue_type":"Task"}'
mcp-cli call mcp-atlassian jira_get_project_issues '{"project_key":"BEN"}'
```

### Discord
```bash
mcp-cli call discord-mcp discord_get_dms '{"limit":10}'
mcp-cli call discord-mcp discord_send_dm '{"user_id":"...","message":"..."}'
```

### SSH Servers

#### Multi-SaaS Deploy (Production)
```bash
mcp-cli call ssh-server-multisaasdeploy execute-command '{"cmdString":"docker ps"}'
mcp-cli call ssh-server-multisaasdeploy execute-command '{"cmdString":"ls -la /app"}'
```

#### AccForge.io
```bash
mcp-cli call ssh-mpc-server-accforge.io execute-command '{"cmdString":"ls"}'
```

#### Angerscar.ma
```bash
mcp-cli call ssh-mcp-server-angerscar.ma execute-command '{"cmdString":"ls"}'
```

### Gmail
```bash
mcp-cli call gmail search_emails '{"query":"in:inbox newer_than:7d","maxResults":20}'
mcp-cli call gmail send_email '{"to":["email@example.com"],"subject":"Subject","body":"Body"}'
```

### Email: contact@cobou.agency (IONOS)
```bash
mcp-cli call mail_contact_cobou_agency list_emails_metadata '{"limit":20}'
mcp-cli call mail_contact_cobou_agency get_emails_content '{"email_id":"..."}'
mcp-cli call mail_contact_cobou_agency send_email '{"to":"...","subject":"...","body":"..."}'
```

### Email: cobou_distribution (Distribution)
```bash
mcp-cli call mail_contact_cofibou_distribution list_emails_metadata '{"limit":20}'
mcp-cli call mail_contact_cofibou_distribution send_email '{"to":"...","subject":"...","body":"..."}'
```

### GitHub Copilot
```bash
mcp-cli call github-copilot get_me
mcp-cli call github-copilot list_issues '{"repo":"owner/repo"}'
mcp-cli call github-copilot create_issue '{"repo":"owner/repo","title":"...","body":"..."}'
```

### Playwright (Browser Automation)
```bash
mcp-cli call playwright browser_navigate '{"url":"https://example.com"}'
mcp-cli call playwright browser_snapshot
mcp-cli call playwright browser_click '{"selector":"button"}'
```

### Bene2Luxe API (Full Backend)
```bash
# Orders
mcp-cli call bene2luxe_mcp get_orders '{"limit":20}'
mcp-cli call bene2luxe_mcp get_order_by_id '{"order_id":123}'
mcp-cli call bene2luxe_mcp update_order_status '{"order_id":123,"status":"shipped"}'

# Products
mcp-cli call bene2luxe_mcp get_products '{"limit":20}'
mcp-cli call bene2luxe_mcp search_products '{"query":"Stone Cargo"}'
mcp-cli call bene2luxe_mcp get_all_brands

# Users
mcp-cli call bene2luxe_mcp get_users '{"limit":20}'
mcp-cli call bene2luxe_mcp get_new_users '{"days":7}'

# Analytics
mcp-cli call bene2luxe_mcp get_order_stats
mcp-cli call bene2luxe_mcp get_analytics
mcp-cli call bene2luxe_mcp get_financial_summary

# Snapchat
mcp-cli call bene2luxe_mcp get_snapchat_army_info
mcp-cli call bene2luxe_mcp get_snapchat_device_health
mcp-cli call bene2luxe_mcp get_snapchat_campaigns
mcp-cli call bene2luxe_mcp get_snapchat_leads

# WhatsApp
mcp-cli call bene2luxe_mcp get_whatsapp_chats
mcp-cli call bene2luxe_mcp get_whatsapp_messages '{"chat_id":123}'
mcp-cli call bene2luxe_mcp send_whatsapp_message '{"chat_id":123,"message":"..."}'

# System
mcp-cli call bene2luxe_mcp get_system_health
mcp-cli call bene2luxe_mcp get_recent_notifications
```

### Discord Server MCP
```bash
mcp-cli call discord-server-mcp discord_discover
mcp-cli call discord-server-mcp discord_execute '{"action":"send_message","channel":"...","content":"..."}'
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `SERVER_NOT_FOUND: ssh-mpc-server...` | Use correct name: `ssh-server-multisaasdeploy` (NOT `ssh-mpc-server-multisaasdeploy`) |
| Tool not found | Check server name spelling exactly |

## Business Groups (WhatsApp JIDs)
- COBOU PowerRangers: `120363420711538035@g.us`
- B2LUXE BUSINESS: `120363408208578679@g.us`
- MAYAVANTA: `120363405622746597@g.us`

## Jira Projects
- Bene2Luxe: `BEN`
- CoBou Agency: `COBOUAGENC`
- TikTok/YouTube: `TIKYT`
- ZovaBoost: `ZOVAPANEL`
