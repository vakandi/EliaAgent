# EliaAI Release Notes - April 2026

## Version: Public Release v1.0.1 (April 27, 2026)

### What's New in This Release

---

## 1. Desktop Shortcuts (NEW!)

### EliaUI.app (Platypus Native App)
- Native macOS application created with Platypus
- Double-click to launch EliaUI in clean app window
- No Terminal window required

### EliaUI.command (tmux-based)
- Terminal with tmux session for cleaner log display
- All logs in one organized window
- Easy desktop shortcut

### Other Shortcuts
- `Elia.command` - Main Elia agent
- `Elia-OC` - OpenCode CLI  
- `EliaDiscord.command` - Discord bot

---

## 2. Discord Integration (NEW!)

Full Discord bot integration at `integrations/elia-discord-bot/`:
- Chat with Elia in any Discord channel
- Slash commands: `/elia`, `/elia-reset`, `/elia-new`
- Typing indicator during processing
- Session persistence across messages

### Setup
```bash
cd integrations/elia-discord-bot
cp .env.example .env
# Add your DISCORD_BOT_TOKEN
pip install -r requirements.txt
python bot.py
```

---

## 3. Updated UI (ui_electron/)

- New GIF assets (`elia.gif`, `elia5.gif`, `elia6.gif`)
- New HTML popups (cron, morning, proxy-error)
- Updated src files

---

## 4. Subworkers System (Continued)

From v1.0.0 - Autonomous promotion agents now included:

| Component | Purpose |
|-----------|---------|
| `bene2luxe-promoter/` | Autonomous agent for Bene2Luxe |
| `cobou-promoter/` | Autonomous agent for CoBou Agency |
| `plists/` | macOS LaunchAgent configurations |

### Overview
Subworkers are autonomous AI promotion agents that run on a schedule to promote your businesses automatically.

### Components Added
| Component | Purpose |
|-----------|---------|
| `bene2luxe-promoter/` | Autonomous agent for Bene2Luxe (luxury fashion resale) promotion |
| `cobou-promoter/` | Autonomous agent for CoBou Agency (B2B) promotion |
| `plists/` | macOS LaunchAgent configurations |
| `scripts/trigger_*.sh` | Trigger scripts for promoters |

### How Subworkers Work

**CoBou Promoter** (B2B - every 30 min, 09:00-21:00):
- LinkedIn engagement
- X (Twitter) interactions  
- Reddit community participation
- Lead generation for web development services

**Bene2Luxe Promoter** (B2C - every 20 min, 10:00-22:00):
- Instagram engagement
- TikTok interactions (via browser)
- Facebook Marketplace browsing
- Luxury fashion resale promotion

### Setup
```bash
# Install LaunchAgents
cd plists
launchctl load com.elia.cobou-promoter.plist
launchctl load com.elia.bene2luxe-promoter.plist

# Manual test
cd scripts
./trigger_cobou_promoter.sh
./trigger_bene2luxe_promoter.sh
```

---

## 2. New Triggers System

### Command-based Triggers (in PROMPT.md)

The main trigger system now uses command keywords to spawn specialized agents:

| Command Trigger | Agent Spawned |
|----------------|--------------|
| `/ulw-loop` | UltraWork Loop (unlimited iterations) |
| `/ralph-loop` | Ralph Loop (50 iter max) |
| `appel Gilfoyle` | Backend dev agent |
| `appel Setbon` | Marketing agent |
| `appel Picasso` | Visual/design agent |

### Subagent Categories
- `gilfoyle` - Backend dev, SSH, accounts
- `bene2luxe` - Luxury e-commerce
- `cobou-agency` - B2B digital
- `zovaboost` - SMMPanel
- `setbon` - Marketing & conversion
- `tiktok-youtube-auto` - Content automation

---

## 3. Pre-Report Checklist (NEW in PROMPT.md)

Before sending ANY Discord report, agents MUST complete:

```markdown
PRE-REPORT CHECKLIST:
For each business area, decide: DOES THIS APPLY THIS RUN?

☐ Server Health / MCP Status → #health-checks
☐ Bene2Luxe Orders / Sales → #orders
☐ Bene2Luxe Products → #products
☐ Bene2Luxe Clients → #clients
☐ ZovaBoost Panel → #panel
☐ TikTok/YouTube Content → #content
☐ TikTok/YouTube Analytics → #analytics
```

**VALIDATION**: Reports without this checklist are INVALID.

---

## 4. File Sending Enhancement

### Discord File Upload (NEW)
```bash
# Send file directly to Discord
mcp-cli call discord-server-mcp discord_send_file '{
  "channel_id": "CHANNEL_ID",
  "file_path": "[AGENT_DIR]/docs/YYYY-MM-DD/report.md",
  "content": "📋 Rapport détaillé"
}'
```

**IMPORTANT**: Never send file paths as text - always upload the file directly.

---

## 5. Context Files Updated

### Tools Reference (context/TOOLS.md)
- MCP-CLI commands with proper JSON syntax
- WhatsApp business groups
- Discord channel IDs
- Telegram commands
- Image generation (Higgsfield.ai)

### Business Context (context/business.md)
- Cleaned for public release
- Placeholders forYOUR information
- Team structure templates

---

## 6. Documentation Added

### SETUP_TOOLS.md
Quick reference for setting up the agent system.

### SUBWORKERS_SYSTEM.md (NEW - 1700+ lines)
Complete implementation guide including:
- Subworker architecture
- OpenCode agent configuration
- System prompts for promoters
- LaunchAgent setup
- MCP server integration
- Workflows & reporting
- Step-by-step implementation

---

## 7. Updates to Core Files

### PROMPT.md (Major Update)
- Increased from ~600 to ~830 lines
- New triggers section with `/ulw-loop` and `/ralph-loop`
- Pre-report checklist requirement
- File sending enhancement
- Updated startup sequence

### MORNING_PROMPT.md
- Updated business references
- Team communication channels
- Reporting templates

---

## 8. Files Cleaned for Public Release

### Removed/Redacted
| File | Action |
|------|--------|
| `.env` | NOT included (private credentials) |
| `docs/YYYY-MM-DD/*` | NOT included (daily logs) |
| `brain/obsidian/*` | NOT included (private wiki) |
| `memory/*-CREDENTIALS.md` | NOT included (secrets) |
| `logs/*.log` | NOT included (runtime logs) |

### Kept for Public
| File | Purpose |
|------|--------|
| `PROMPT.md` | Main system prompt template |
| `MORNING_PROMPT.md` | Morning routine template |
| `README.md` | Setup guide |
| `context/TOOLS.md` | Tools reference (template) |
| `context/business.md` | Business info (template) |
| `skills/INDEX.md` | Available skills list |
| `setup/README.md` | Full setup guide |
| `SUBWORKERS_SYSTEM.md` | Subworker implementation |

---

## 9. Setup Instructions for Your Own Instance

### Quick Setup

1. **Clone the repo**:
```bash
git clone https://github.com/vakandi/EliaAgent.git
cd EliaAgent
```

2. **Update context files**:
```bash
# Edit these files with YOUR information:
vim context/business.md
vim context/TOOLS.md
vim context/jira-projects.md
vim PROMPT.md    # Update owner name
```

3. **Configure OpenCode**:
```bash
# Copy OpenCode config
mkdir -p ~/.config/opencode
cp -r setup/opencode-config/* ~/.config/opencode/

# Restart OpenCode
```

4. **Set up cron** (optional):
```bash
# Every 30 minutes
./scripts/manage_cron.sh install --interval 30m
```

### Full Setup Guide
See `setup/README.md` for complete instructions.

---

## 10. What's Different from Private Version

| Feature | Public | Private (EliaAI) |
|---------|--------|------------------|
| Business credentials | Template/Holders | Real data |
| Daily docs logs | NOT included | Full history |
| Obsidian brain | NOT included | Full wiki |
| Memory files | Generic | Personal |
| .env | NOT included | Contains secrets |

---

## 11. Architecture Summary

```
EliaAgent/
├── PROMPT.md              # Main system prompt
├── MORNING_PROMPT.md       # Morning routine
├── README.md              # → setup/README.md
├── setup/                # Setup scripts & docs
│   ├── README.md         # Full setup guide
│   ├── README_WINDOWS.md
│   └── switch-proxy.sh
├── context/              # 📝 UPDATE THESE
│   ├── TOOLS.md         # MCP commands
│   ├── business.md      # Business info
│   └── jira-projects.md
├── skills/               # Available skills
├── ui_electron/         # Desktop UI app
├── scripts/             # Automation scripts
│   ├── manage_cron.sh
│   ├── trigger_opencode_interactive.sh
│   └── ...
├── bene2luxe-promoter/  # Subworker
├── cobou-promoter/     # Subworker
└── plists/           # macOS LaunchAgents
```

---

## 12. Model Configuration

**REQUIRED**: Use ONLY free OpenCode models:

| Model | Badge | Use |
|-------|-------|-----|
| `opencode/big-pickle` | 🔴 Red | Default - 200K context |
| `opencode/minimax-m2.5-free` | 🟡 Yellow | Fallback |

**DO NOT USE**: Claude Opus, GPT-4, or any paid models.

---

## 13. Troubleshooting

### MCP Tools Not Working
```bash
# Restart MCP servers
mcp-cli list  # Check servers
pkill -f mcp && mcp-cli &  # Restart
```

### Cron Not Running (macOS)
```bash
# Use root crontab
./scripts/manage_cron.sh install --interval 30m --sudo
```

### Subworkers Not Starting
```bash
# Check LaunchAgents
launchctl list | grep -i promoter
launchctl load plists/com.elia.cobou-promoter.plist
```

---

## 14. Credits & License

**Creator**: Wael Bousfira  
**Repository**: https://github.com/vakandi/EliaAgent  
**License**: MIT

---

## 15. Changelog Summary

| Version | Date | Changes |
|---------|-----|---------|
| Public | April 2026 | Initial public release |
| update1763 | - | Added subworkers system |
| update13265 | - | New triggers (/ulw-loop) |
| update22984 | - | Pre-report checklist |

---

**Quick Start**: See `setup/README.md` for full setup instructions.