# MCP Tools & Servers Reference

> Quick reference for available MCP tools, SSH servers, and deployment commands.

---

## MCP Servers

### Communication
- `whatsapp` — WhatsApp message operations (send, receive, download media)
- `discord-server-mcp` — Discord server operations (send messages, channels, roles)
- `mail_contact_*` — Email operations per business account

### Code & Dev
- `ssh-vcamvps` — SSH access to production VPS
- `github` — GitHub operations (PRs, issues, repos)
- `jira-mcp` — Jira project management

### Browser & Vision
- `playwright` — Browser automation (screenshots, navigation, form filling)
- `vision-mcp` — Image analysis via Mistral/OpenRouter models

### Storage & Docs
- `notion-mcp` — Notion page/database operations
- `gsc-mcp` — Google Search Console & GA4 analytics

---

## SSH Servers

Connect via: `ssh user@server-ip`

| Server | Purpose |
|--------|---------|
| Production VPS | App deployment, monitoring |
| Staging VPS | Testing before prod |

---

## Quick Commands

```bash
# Restart MCP servers
bash ~/Documents/mcps_server/restart-whatsapp-bridge.sh restart
bash ~/Documents/mcps_server/restart_clean_mcp_playwright.sh

# Check docs folder
ls ~/Documents/EliaAI/docs/$(date +%Y-%m-%d)/

# Run health check
bash ~/Documents/EliaAI/scripts/health_check.sh
```

---

## Discord Channels

| Business | Channel ID |
|----------|-----------|
| Main | `[channel-id]` |
| Reports | `[channel-id]` |
| Leads | `[channel-id]` |

---

## Notes

- All MCP server paths assume standard installation in `~/Documents/mcps_server/`
- Discord bot tokens and API keys are in `.env` files — never commit them
- Use `mcp-cli` wrapper for cross-platform MCP tool access
