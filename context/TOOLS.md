# TOOLS.md - Quick Reference

> ⚡ **codemem** (AI Memory) — Auto-captures session context. USE IT to:
> - Remember tasks, decisions, blockers across sessions
> - `codemem search "query"` — поиск memories
> - Auto-injects relevant memories before each prompt
> ⚠️ NO manual commands — works automatically via plugin

> ⚠️ All commands here = **terminal commands** — use the `bash` tool (not skills).

---

**All MCP tools are ALWAYS 100% available.** If any MCP tool fails:

1. **WhatsApp issues** → Run:
   ```bash
   /Users/vakandi/Documents/mcps_server/restart-whatsapp-bridge.sh restart
   ```

2. **Playwright issues** → Run:
   ```bash
   /Users/vakandi/Documents/mcps_server/restart_clean_mcp_playwright.sh
   ```

3. **Any other MCP failure** → **IMMEDIATELY** run a new ulw-loop to investigate:
   ```
   /ulw-loop
   ```
   See section **"ULW-Loop (Autonomous Task Execution)"** (lines 174-200) for full details on how to run and use it.

   Then send a report to Discord #reports with:
   - What MCP failed
   - Error messages
   - Investigation steps taken

**MCP Server Location**: `/Users/vakandi/Documents/mcps_server/`

---

## 🔊 Voice Message Handling (WhatsApp Only)

**CRITICAL**: When receiving or sending voice messages via WhatsApp, ALWAYS check for existing transcripts before transcribing.

### Voice Message Workflow

1. **Detect voice message** → Check `hasMedia` and `mediaType` in message
2. **Extract date** → Get timestamp from message → format as `YYYY-MM-DD`
3. **Check docs folder** → Look for `/Users/vakandi/EliaAI/docs/{YYYY-MM-DD}/`
4. **Check existing transcript** → Search for `{wa|tg}_{msg_id}` in filenames
5. **If already transcribed** → Skip processing
6. **If not transcribed** → Download audio → Transcribe with Whisper → Analyze as text

### Transcript Filename Convention

```
run_{source}_{msg_id}_{DD_mmm_YYYY_HHMM}.md
```

| Field | Description | Example |
|-------|-------------|---------|
| `source` | `wa` (WhatsApp) | `wa` |
| `msg_id` | Message ID from the platform | `msg_abc123` |
| `DD_mmm_YYYY_HHMM` | Day, month (French), year, time | `29_mars_2026_0945` |

**Examples:**
- WhatsApp: `run_wa_msg_abc123_29_mars_2026_0945.md`

### Transcript Check Logic

```bash
# Check if message already transcribed
MSG_ID="<message_id>"
TODAY=$(date +%Y-%m-%d)
DOCS_DIR="/Users/vakandi/EliaAI/docs/$TODAY"

# Direct filename check (fastest)
ls "$DOCS_DIR"/*_"$MSG_ID"_*.md 2>/dev/null && echo "Already transcribed" || echo "Need transcription"

# Or grep for msg_id in any file
grep -rl "$MSG_ID" "$DOCS_DIR"/*.md 2>/dev/null && echo "Already transcribed"
```

### Voice Message Transcription Command

```bash
# Download audio first via MCP, then transcribe
whisper /path/to/audio.ogg --model large-v3 --language French --task transcribe
```

### Transcript File Content Template

```markdown
# Voice Message Transcript

**Source:** WhatsApp
**Message ID:** {msg_id}
**Timestamp:** {DD_mmm_YYYY_HHMM}
**Sender:** {sender_name/number}

---

## Transcription

{transcribed_text_here}

---

## Context & Analysis

{analysis_of_content}
```

---

## 🖼️ Image Handling (WhatsApp)

```bash
# Detect: hasMedia=true, mediaType="image" → Download → Analyze
mcp-cli call whatsapp download_media '{"message_id":"<id>","chat_jid":"<jid>","save_path":"/Users/vakandi/EliaAI/docs/YYYY-MM-DD/"}'
mcp-cli call vision-mcp analyze_image '{"image_path": "/path/to/image.jpg", "prompt": "Describe this image", "model": "nvidia/nemotron-nano-12b-v2-vl:free"}'
# Save as: img_wa_{msg_id}_{DD_mmm_YYYY_HHMM}.md
```

---

## MCP-CLI (All External Services)

**⚠️ IMPORTANT:** `mcp-cli` is a **shell command** (terminal/bash), NOT a tool within OpenCode. It wraps all MCP servers and exposes them via command-line interface.

**Info:** `mcp-cli -h` or `mcp-cli --help`

```bash
# List servers (shell command)
mcp-cli

# All commands below are SHELL COMMANDS - run them in terminal or via bash

# WhatsApp
mcp-cli call whatsapp list_chats '{"limit":20}'
mcp-cli call whatsapp list_messages '{"chat_jid":"...","limit":30}'
mcp-cli call whatsapp send_message '{"recipient":"...","message":"..."}'
mcp-cli call whatsapp download_media '{"message_id":"...","chat_jid":"..."}'

# 📅 MESSAGE SCHEDULING (NEW!)
# Schedule a message for future delivery (ISO-8601 format)
mcp-cli call whatsapp schedule_message '{"recipient":"165558221861055","message":"Bonjour!","scheduled_time":"2026-04-22T09:00:00"}'

# List all scheduled messages (optional: filter by status: pending/sent/failed/cancelled)
mcp-cli call whatsapp list_scheduled_messages '{"status":"pending","limit":10}'

# Cancel a pending scheduled message
mcp-cli call whatsapp cancel_scheduled_message '{"message_id":123}'

# Delete a scheduled message from database
mcp-cli call whatsapp delete_scheduled_message '{"message_id":123}'

# Recipient formats:
# - Phone number with country code, no + (e.g., "165558221861055")
# - JID (e.g., "123456789@s.whatsapp.net")
# - Group JID (e.g., "123456789@g.us")

# ⚠️ VOICE MESSAGE HANDLING: When listing messages, check hasMedia + mediaType="ptt"
# If voice message detected:
# 1. Check date → /Users/vakandi/EliaAI/docs/{YYYY-MM-DD}/
# 2. Search for "wa_{msg_id}" in filenames to check if transcribed
# 3. If not → download_media → whisper → save as run_wa_{msg_id}_{DD_mmm_YYYY_HHMM}.md

# Discord (Personal Account - your own Discord)
mcp-cli call discord-mcp discord_get_dms '{"limit":10}'
mcp-cli call discord-mcp discord_send_dm '{"user_id":"...","message":"..."}'

# Discord Server (EliaWorkSpace - bot account "watson")
# Get server structure
# ⚠️ NOTE: Replace with YOUR Discord Bot Token
bash: cd ~/Documents/EliaVoiceRecorder && DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN_HERE" python3 discord_server_structure.py

# List channels
mcp-cli call discord-server-mcp discord_execute '{"operation":"channels.list","params":{}}'

# Read messages from channel (last N messages)
mcp-cli call discord-server-mcp discord_execute '{"operation":"messages.list","params":{"channel_id":"CHANNEL_ID","limit":20}}'

# Read messages from last N hours (default 12h) - CONVENIENCE WRAPPER
mcp-cli call discord-server-mcp discord_execute '{"operation":"messages.list_range","params":{"channel_id":"CHANNEL_ID","hours":12,"limit":50}}'

# Read messages after specific timestamp (ISO 8601 format)
mcp-cli call discord-server-mcp discord_execute '{"operation":"messages.list","params":{"channel_id":"CHANNEL_ID","after_timestamp":"2026-04-04T12:00:00Z","limit":50}}'

# Read messages after/before specific snowflake ID
mcp-cli call discord-server-mcp discord_execute '{"operation":"messages.list","params":{"channel_id":"CHANNEL_ID","after":"1489000000000000000","limit":50}}'
mcp-cli call discord-server-mcp discord_execute '{"operation":"messages.list","params":{"channel_id":"CHANNEL_ID","before":"1490000000000000000","limit":50}}'

# Send message to channel (RECOMMENDED - handles special chars properly)
mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244810777727046","content":"Your message here 🚀"}'

# Send file directly to channel (NEW! - always prefer this over sending paths)
mcp-cli call discord-server-mcp discord_send_file '{"channel_id":"1489244810777727046","file_path":"/Users/vakandi/EliaAI/docs/report.md","content":"📋 Detailed report"}'

# Fallback: Upload to tmpfiles.org if direct upload fails
# curl -X POST https://tmpfiles.org/api/v1/upload -F "file=@/path/to/file.pdf"

# Or read from file:
cat report.md | python3 /Users/vakandi/EliaAI/tools/discord_send.py 1489244810777727046 --stdin

# Server info
mcp-cli call discord-server-mcp discord_execute '{"operation":"guild.get","params":{}}'

## Discord Channel Mapping (EliaWorkSpace - Channel IDs)

### ELIA-HQ (SYSTEM - Elia AI)
| Channel | Channel ID |
|---------|------------|
| 💡-urgent | `1489244806310793216` |
| 📊-reports | `1489244810777727046` |
| 📝-activity-logs | `1489244812107317402` |
| 📚-knowledge | `1489244815790182450` |
| ✅-tasks-tracker | `1489244818134794330` |
| 🖥️-health-checks | `1489247935807099020` |

### BEN2LUXE (Jira: BEN) - DIFFERENT BUSINESS
| Channel | Channel ID |
|---------|------------|
| 🛍️-products | `1489244857250615416` |
| 📦-orders | `1489244862871244950` |
| 👥-clients | `1489244868235755580` |
| 📱-social-media | `1489244873847734292` |
| 📤-marketing | `1489244878431846523` |
| 📂-management | `1489246873998065745` |
| tiktok-ai-to-copy | `1489247163824345228` |

### COBOU-AGENCY (Jira: COBOUAGENC) - DIFFERENT BUSINESS
| Channel | Channel ID |
|---------|------------|
| 🚀-projects | `1489244906013593642` |
| 👥-clients | `1489244911449538680` |
| 💻-dev-work | `1489244916352684045` |
| 💰-invoices | `1489244921180455035` |

### ZOVABOOST (Jira: ZOVAPANEL) - DIFFERENT BUSINESS
| Channel | Channel ID |
|---------|------------|
| 💻-panel | `1489244946673176618` |
| 👥-clients | `1489244951861661787` |
| 🎨-support | `1489244963261780173` |

### MAYAVANTA (Jira: MAYA) - DIFFERENT BUSINESS
| Channel | Channel ID |
|---------|------------|
| 🤝-concierge | `1489244961269485711` |
| 🚗-car-rental | `1489244967095238777` |
| 🏜️-marrakech-ops | `1489244971772154057` |
| 💻-dev | `1489246953861546115` |

### TEAM
| Channel | Channel ID |
|---------|------------|
| 💬-general | `1489244970983624824` |
| 📅-meetings | `1489244975417000077` |
| 📢-announcements | `1489244980051710162` |

### OGBOUJEE (Jira: OGB) - DIFFERENT BUSINESS
| Channel | Channel ID |
|---------|------------|
| 👜-products | `1489628023266480280` |
| 📦-orders | `1489628028727459945` |
| 👥-clients | `1489628029704736848` |
| 📤-marketing | `1489628033089536162` |
| management | `1490351010252591154` |

### Voice Channels
| Channel | Channel ID |
|---------|------------|
| Chill Calls | `1489245009285877951` |
| Meeting Room | `1489245018261557550` |

### Root Channels
| Channel | ID |
|---------|-----|
| Salons textuels (category) | `1489242791849492661` |
| 💻-général | `1489242791849492663` |

### Categories (Parent IDs)
| Category | ID |
|----------|-----|
| Salons textuels | `1489242791849492661` |
| ELIA-HQ | `1489244763017187549` |
| BEN2LUXE | `1489244764808417320` |
| COBOU-AGENCY | `1489244768235028633` |
| ZOVABOOST | `1489244769505906818` |
| TIKTOK-YOUTUBE | `1489244773284974704` |
| MAYAVANTA | `1489244774882873364` |
| TEAM | `1489244778347499691` |
| OGBOUJEE | `1489628000730484938` |

# Gmail (server id: gmail — check tools: mcp-cli info gmail search_emails)
mcp-cli call gmail search_emails '{"query":"in:inbox newer_than:7d","maxResults":20}'
mcp-cli call gmail read_email '{"messageId":"..."}'
mcp-cli call gmail draft_email '{"to":["you@example.com"],"subject":"Subject","body":"Plain text body"}'
mcp-cli call gmail send_email '{"to":["you@example.com"],"subject":"Subject","body":"Plain text body"}'
mcp-cli call gmail list_email_labels '{}'

# Gmail-tweetsyncai (server id: gmail-tweetsyncai — tweetsyncai@gmail.com)
## ⚠️ IMPORTANT: This Gmail is for Bene2Luxe Snapchat Ads ONLY!
## Reason: Snapchat Business Ads requires a personal Gmail to create business ads account. Our business emails (contact@bene2luxe.com, contact@cofibou-distribution) cannot create business ads accounts, so we used tweetsyncai@gmail.com for this purpose.
## Use this Gmail MCP for:
## - Bene2Luxe Snapchat Ads management
## - Any business ads-related communications for Bene2Luxe
## - DO NOT use for general emails — use contact@bene2luxe.com or contact@cofibou-distribution for that
mcp-cli call gmail-tweetsyncai search_emails '{"query":"in:inbox newer_than:7d","maxResults":20}'
mcp-cli call gmail-tweetsyncai read_email '{"messageId":"..."}'
mcp-cli call gmail-tweetsyncai send_email '{"to":["you@example.com"],"subject":"Subject","body":"Plain text body"}'

# 📧 IONOS Business Email (PRIMARY - Business Emails)

## Morning Routine Integration

**In the morning routine (MORNING_PROMPT.md), Elia MUST:**
1. Run `python3 /Users/vakandi/EliaAI/tools/get_ide_work.sh` - ALWAYS extract IDE work
2. Check and update Google Calendar with reminders for time-sensitive items
3. Check and update Google Tasks for new todo items
4. After gathering data from all sources (WhatsApp, Discord, Email), sync findings to Google Workspace

## Available MCP Servers

### mail_contact_cofibou_distribution (contact@cofibou-distribution.com)
**Use this for:** Cofibou Distribution LLC emails - business logistics, carrier outreach, Point Relais setup

### mail_contact_cobou_agency (contact@cobou.agency)
**Use this for:** CoBou Agency, ZovaBoost, AccForge emails

## ⚠️ CRITICAL: How to Send Emails (JSON Payload Method)

**The `recipients` field MUST be a list (array), NOT a string!**

### WRONG ❌
```bash
mcp-cli call mail_contact_cofibou_distribution send_email '{"recipients":"recipient@email.com",...}'
```

### CORRECT ✅ — Use Python for complex body text
```python
python3 << 'PYEOF'
import subprocess
import json

body = """Your email body here.
Can have multiple lines."""

payload = {
    "recipients": ["recipient@email.com"],
    "subject": "Subject Line",
    "body": body
}

result = subprocess.run(
    ["mcp-cli", "call", "mail_contact_cofibou_distribution", "send_email", json.dumps(payload)],
    capture_output=True, text=True
)
print(result.stdout)
PYEOF
```

## Quick Commands

```bash
# Read inbox
mcp-cli call mail_contact_cofibou_distribution list_emails_metadata '{"limit":20}'
mcp-cli call mail_contact_cofibou_agency list_emails_metadata '{"limit":20}'

# Read specific email
mcp-cli call mail_contact_cofibou_distribution get_emails_content '{"email_ids":["123"]}'

# Send email (via Python - see above for body with special chars)
```

## ⚠️ IMPORTANT: Use COFIBOU email for business logistics!
- **contact@cofibou-distribution.com** = Cofibou Distribution LLC = business logistics, carriers, Point Relais
- **contact@cobou.agency** = CoBou Agency = CoBou/ZovaBoost/AccForge business

# ⚠️ CRITICAL: Most business emails (orders, invoices, notifications) now redirect to this inbox!
# Check this FIRST for business issues, not Gmail.

mcp-cli call mail_contact_cobou_agency list_available_accounts '{}'
mcp-cli call mail_contact_cobou_agency list_emails_metadata '{"account_name":"ionos","limit":20}'
mcp-cli call mail_contact_cobou_agency get_emails_content '{"account_name":"ionos","email_ids":["123"]}'
mcp-cli call mail_contact_cobou_agency send_email '{"account_name":"ionos","recipients":[" recipient@email.com"],"subject":"Subject","body":"Message"}'
mcp-cli call mail_contact_cobou_agency delete_emails '{"account_name":"ionos","email_ids":["123"]}'
mcp-cli call mail_contact_cobou_agency download_attachment '{"account_name":"ionos","email_id":"123","attachment_index":0,"save_path":"/path/to/save"}'

# Jira
mcp-cli call mcp-atlassian create_issue '{"project":"BEN","summary":"...","description":"...","issue_type":"Task"}'
mcp-cli call mcp-atlassian jira_get_project_issues '{"project_key":"BEN"}'

# Analytics-MCP (Google Analytics 4)
# Service account needs permission in GA4 first!
mcp-cli call analytics-mcp get_account_summaries '{}'
mcp-cli call analytics-mcp get_property_details '{"property_id": "432287363"}'
mcp-cli call analytics-mcp list_ga4_audiences '{"property_id": "432287363"}'
mcp-cli call analytics-mcp list_key_events '{"property_id": "432287363"}'

# Full tool list: See /Users/vakandi/.config/opencode/skills/mcp-cli/SKILL.md

# SSH
mcp-cli call ssh-mpc-server-multisaasdeploy execute-command '{"cmdString":"ls -la"}'
```

### Business Groups (WhatsApp)
| Group | JID |
|-------|-----|
| COBOU PowerRangers | `120363420711538035@g.us` |
| B2LUXE BUSINESS | `120363408208578679@g.us` |
| OGBOUJEE 👜 BUSINESS | `120363425082264099@g.us` |
| MAYAVANTA | `120363405622746597@g.us` |

### WhatsApp Individual IDs (CRITICAL)
| Membre | WhatsApp ID | Téléphone | Pays |
|--------|-----------|---------|------|
| Thomas | 165558221861055 | +33 6 29 35 22 37 | France |
| Rida | 131319447212112 | [À confirmer] | [À confirmer] |
| Ali | 178481677779049 | +41 (Suisse) | ✅ CORRIGÉ |

---

## Agent-Browser (Web Automation)

**Info:** `agent-browser -h`

**Use real Google Chrome** (not Chrome for Testing) to reduce bot detection on heavy/repetitive tasks.

```bash
# Navigation
agent-browser open <url> --executable-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headed
agent-browser click <selector>
agent-browser fill <selector> <text>
agent-browser snapshot
agent-browser screenshot [path]

# Alias (add to ~/.zshrc): alias chrome="agent-browser --executable-path \"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome\" --headed"
chrome open <url>   # Visible browser with real Chrome (less bot detection)
chrome snapshot     # Take screenshot

# Email
agent-browser open https://mail.proton.me/u/1/inbox --executable-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headed
agent-browser open https://email.ionos.fr/appsuite/#!!&app=io.ox/mail --executable-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headed
```

More options: `agent-browser -h`

---

## Voice Transcription (Whisper)

**Info:** `whisper -h`

```bash
# Download audio first, then transcribe
whisper /path/to/audio.ogg --model large-v3 --language French --task transcribe
```

---

## IDE Work Extraction

**Info:** `./tools/get_ide_work.sh -h`

```bash
./tools/get_ide_work.sh              # All IDEs (recommended)
./tools/get_opencode_work.sh 24       # OpenCode only (last 24h)
```

---

## Google Workspace Calendar (Meeting Scheduling)

**Info:** `gws-workspace -h` or `gws-workspace help`

```bash
gws-workspace create-event "Title" "Desc"
gws-workspace create-task "Task" "Notes"
gws-workspace import-md "file.md" "Title"
gws-workspace list-events
```

**📅 MEETING SCHEDULING - Elia MUST follow this workflow:**

### For Discord Team Meetings (when Wael asks for a meeting):
**→ Use Discord Server Events (so all team members can see)**
```bash
# Create Discord scheduled event (visible to all team members)
mcp-cli call discord-server-mcp discord_execute '{
  "operation": "events.create",
  "params": {
    "name": "Weekly Team Sync",
    "description": "Team sync meeting with Wael",
    "start_time": "2026-04-25T10:00:00Z",
    "end_time": "2026-04-25T10:30:00Z",
    "location": "Voice Channel: Meeting Room"
  }
}'
```

**Example:**
```bash
# Create team meeting visible in Discord
mcp-cli call discord-server-mcp discord_execute '{"operation":"events.create","params":{"name":"Team Sync with Wael","description":"Weekly sync - discuss current projects","start_time":"2026-04-28T10:00:00Z","end_time":"2026-04-28T10:30:00Z","location":"Meeting Room"}}'
```

### For External Meetings or Personal Tasks:
**→ Use Google Calendar with Google Meet link**
```bash
# Create Google Calendar event with Meet link
gws-workspace create-event "Meeting Title" "Description"

# Or create directly with Meet link generation (if available):
python3 /Users/vakandi/EliaAI/tools/google_workspace.py create-event "Meeting" "Desc"
# The event will have a Google Meet link auto-generated
```

**Note:** Google Meet links are automatically generated when creating Google Calendar events with video conferencing enabled.

### Summary:
| Type of Meeting | Where to Create | Tool |
|----------------|-----------------|------|
| Discord Team Meeting (Wael asks) | Discord Server | `discord-server-mcp events.create` |
| External/Personal Meeting | Google Calendar | `gws-workspace create-event` |

---

## Jira Projects
| Business | Key |
|----------|-----|
| Bene2Luxe | `BEN` |
| CoBou Agency | `COBOUAGENC` |
| TikTok/YouTube | `TIKYT` |
| ZovaBoost | `ZOVAPANEL` |

---

## SSH Server (use mcp-cli)

**Info:** `mcp-cli -h`

```bash
# Main SaaS server (Bene2Luxe, ZovaBoost, Netfluxe, OGBoujee)
mcp-cli call ssh-mpc-server-multisaasdeploy execute-command '{"cmdString":"ls -la"}'
```

---

## Voice Output

**TTS**: `elia-voxtral-speak` (Mistral, fast, French) → fallback: `elia-speak`

**⚠️ ALWAYS use the right tone:**
| Flag | Tone | When to use |
|------|------|-------------|
| `-j` | Happy | Good news, celebrations, positive updates |
| `-d` | Sad | Blockers, problems, urgent issues |
| `-a` | Angry | Urgent warnings, serious issues |
| `--play` | Play | Play audio after generation |
| `-x` | Fallback | Use elia-speak fallback |

```bash
elia-voxtral-speak "Great news!" -j           # happy
elia-voxtral-speak "Problem detected" -d      # sad
elia-voxtral-speak "URGENT!" -a               # angry
elia-voxtral-speak "Message" --play          # play audio
elia-speak -x "Message"                        # fallback
```

**⚠️ When sending a voice message to someone or a group:** ALWAYS use `elia-voxtral-speak` (or `elia-speak -x` as fallback) to generate the voice audio before sending via WhatsApp/Discord.

---

## ProtonMail CLI

**Info:** `~/.local/bin/protonmail -h`

```bash
# Location: ~/.local/bin/protonmail
~/.local/bin/protonmail list                    # Inbox
~/.local/bin/protonmail list -t sent           # Sent
~/.local/bin/protonmail list -t drafts         # Drafts
~/.local/bin/protonmail list -t spam          # Spam
~/.local/bin/protonmail list -t allmail        # All mail
```

---

## 🚀 ULW-Loop / Ralph-Loop (Autonomous Task Execution)

**Ralph-Loop = DEFAULT mode for cronjob runs (50 iterations max)**

### When to Use
- Task found during cronjob → execute it fully, don't just report
- Multiple tasks to do → run ralph-loop to process all of them
- Autonomous work mode → runs until `<promise>COMPLETE</promise>` or max iterations

### How to Launch (ALWAYS USE THIS FORMAT)

```
/ralph-loop
```

**⚠️ MANDATORY format for ALL runs:**
```bash
# Prefix with /ralph-loop + big-pickle model
oh-my-opencode run -a elia --model opencode/big-pickle "/ralph-loop YOUR TASK HERE" --attach
```

**⚠️ ALWAYS use `opencode/big-pickle` model** (free, stable, DEFAULT)

### What Happens
- Runs with ralph-loop (50 iterations max default)
- Spawns subagents for parallel execution
- Delegates to specialized agents (marketing, dev, sales, etc.)

**⚠️ CRITICAL: Why oh-my-opencode?**
- Regular `opencode run` does NOT resolve slash commands properly
- The LLM receives raw text instead of executing the command
- Use `oh-my-opencode run -a elia` for proper command execution

### Using Custom Subagents

**⚠️ ALWAYS provide context to subagents!**

When delegating to subagents, ALWAYS include:
- Relevant file paths (context, docs, reports)
- Business background needed
- Specific task details

```bash
# Start with elia, then delegate to subagents via task()
oh-my-opencode run -a elia "Message for subagent" --attach
# Then use task() to spawn specialized agents

# Available Subagents (via task(category="..."))
task(category="bene2luxe", ...)     # Luxury e-commerce
task(category="cobou-agency", ...) # B2B digital
task(category="zovaboost", ...)     # SMMPanel
task(category="setbon", ...)        # Marketing & Conversion
task(category="gilfoyle", ...)      # Backend dev
task(category="tiktok-youtube-auto", ...) # TikTok/YouTube auto
```

### Mandatory Context for Subagents

**ALWAYS give subagents the context they need:**

| Context File | When to Use |
|-------------|------------|
| `@context/business.md` | Tasks related to businesses, teams, operations |
| `@context/TOOLS.md` | Tasks needing tools, MCP, automation |
| `@memory/MEMORY.md` | Tasks needing long-term memory, blockers |
| `@docs/YYYY-MM-DD/*.md` | Tasks needing recent work/ reports |

**Example prompts WITH context:**
```bash
# GOOD - has context
task(category="bene2luxe", prompt="Create product listing for Chanel bag. 
Context: @context/business.md (team roles: Ali handles suppliers)
Recent: @docs/2026-04-20/morning_report.md
Tools: @context/TOOLS.md (image generation)")

# BAD - no context
task(category="bene2luxe", prompt="Create product listing")
```

**Context paths to reference:**
- Business context: `/Users/vakandi/EliaAI/context/business.md`
- Tools: `/Users/vakandi/EliaAI/context/TOOLS.md`
- Memory: `/Users/vakandi/EliaAI/memory/MEMORY.md`
- Today docs: `/Users/vakandi/EliaAI/docs/2026-04-20/`
- Jira: `https://bsbagency.atlassian.net` (project BEN, COBOUAGENC, etc.)

### High-Value Tasks to Execute
- Create accounts (Copify, Trendtrack, ad networks)
- Browse competitors (Wael's Edge folders: SHOP-5000$COPIFY, SHOP500-1000$COPIFY)
- Build React mockups for conversion ideas
- Research competitors and market opportunities
- Prepare sales documents and proposals
- ANYTHING that moves businesses forward

---

## 🚀 Starting New Work Sessions

```bash
# Quick start (uses big-pickle by default, ULW-loop enabled)
./start_agents.sh

# With extra context / task to execute
./start_agents.sh --extra-prompt="Create a Copify account and research ad earnings recovery"

# With proxy enabled (uses proxychains4)
./start_agents.sh --proxy --extra-prompt="Task description here"
```

**Options:**
| Flag | Purpose |
|------|---------|
| `--extra-prompt="..."` | Add task context to agent |
| `--proxy` | Run through proxychains4 |
| `--model=big-pickle` | Default (free, stable) |

---

## 🖼️ Image Generation (Bene2Luxe - Higgsfield.ai)

**⚠️ ALWAYS use this script for image generation** - Script: `/Users/vakandi/Documents/HiggsFieldGenerator/generate_photo_higgsfield.py`

The script automatically uses UNLIMITED mode (free, no credits).

### Quick Commands

```bash
cd /Users/vakandi/Documents/HiggsFieldGenerator

# Mascoot scenarios
python3 generate_photo_higgsfield.py mascoot vacation
python3 generate_photo_higgsfield.py mascoot party --items "champagne"
python3 generate_photo_higgsfield.py mascoot store --model gpt_image

# Human with product
python3 generate_photo_higgsfield.py human "Chanel bag"
python3 generate_photo_higgsfield.py human "Dior sneakers" --scenario wearing_sneakers

# With reference images (multi-photo support!)
python3 generate_photo_higgsfield.py human "Luxury Bag" --images "/path/to/photo1.png" "/path/to/photo2.png"
python3 generate_photo_higgsfield.py mascoot vacation --images "store.png" "mascot.png"

# Multiple models (queue mode)
python3 generate_photo_higgsfield.py human "Chanel bag" --models "gpt_image,soul_v2,flux_2_pro"
```

### CLI Options

| Flag | Description |
|------|-------------|
| `--model`, `-m` | Model (default: gpt_image) |
| `--models`, `-M` | Comma-separated models for batch |
| `--images`, `-i` | Reference images (paths) |
| `--output`, `-o` | Output file path |

### Available Models (Unlimited/Free)

| Model | Command |
|-------|---------|
| GPT Image | `gpt_image` |
| FLUX.2 Pro | `flux_2_pro` |
| Soul V2 | `soul_v2` |
| Nano Banana | `nano_banana` |
| Seedream 4.0 | `seedream_4_0` |

### Queue Management (Automatic)

The script monitors queue via eval:
- `get_queue_status()` - Returns queueCounter, processingCount, queueFull
- `wait_for_queue_slot()` - Waits for available slot
- `list_generation_items()` - Lists all generation items

### How It Works (Technical)

1. **Clear storage** - `localStorage.clear()`
2. **Enable unlimited** - `document.querySelector('[role="switch"]').click()`
3. **Upload images** - `agent-browser upload "[type=file]" "/path/to/image.png"`
4. **Set prompt** - Via localStorage injection + reload
5. **Click Generate** - Click the Unlimited button
6. **Monitor queue** - Via JavaScript eval

**Documentation**: `/Users/vakandi/Documents/HiggsFieldGenerator/docs/GENERATE_PHOTO_README.md`

---

## 🧠 MemPalace (AI Memory System)

**MemPalace** is an AI memory system that indexes your documentation with semantic search.

### ⚠️ CRITICAL: Docs and Brain are COPIES of each other

**NEVER search both at once** — they contain the SAME content in different formats:

| Folder | Format | Content |
|--------|--------|---------|
| `docs/` | Raw daily docs | Original files (chat logs, transcriptions, reports) |
| `brain/` | Obsidian wiki | Same content but with wiki-links between notes |

**They are mirrors of each other.** Don't combine searches — pick ONE:

- **docs/** = lire le contenu brut, les logs quotidiens
- **brain/** = lire les notes avec liens wiki (obsidian)

### Quick Commands

```bash
# Initialize (one-time per folder)
mempalace init /path/to/folder --yes

# Index content (create vector store)
mempalace mine /path/to/folder

# Search (pick ONE folder - they are duplicates!)
mempalace search /Users/vakandi/EliaAI/docs/ "query"
# OR
mempalace search /Users/vakandi/EliaAI/brain/ "query"
```

### Current Setup

**Two wings (DUPLICATES) in the same palace:**

| Wing | Path | Files | Rooms |
|------|------|-------|-------|
| `docs` | `/Users/vakandi/EliaAI/docs/` | 803 | diagram_elia_structure, general |
| `brain` | `/Users/vakandi/EliaAI/brain/` | 857 | linkers, documentation, frontend, raw, general |

**Both contain the same content** — choose one based on search needs:
- docs: raw files, daily logs, transcriptions
- brain: Obsidian vault with wiki-links connecting concepts

---

## 🎯 Task Delegation (during ulw-loop)

```typescript
// Development tasks
task(category="backend-dev", load_skills=["coding-agent"], prompt="...")

// Marketing tasks
task(category="marketing-social", load_skills=[], prompt="...")

// E-commerce (Bene2Luxe)
task(category="ecommerce-luxury", load_skills=["luxury-fashion-marketing-genius"], prompt="...")

// Multiple parallel agents
task(run_in_background=true, ...) // x3-5 in parallel
```

---

**Full details**: See PROMPT.md section "MCP Tools" and "Voice Transcription"

---

## 🔍 OpenCode Session Tools (Cron Job Context)

**CRITICAL**: These tools let Elia access previous cron job sessions for continuity and context.

### Why Use These?

When starting a new session, Elia should check what the previous cron runs did to:
- Avoid duplicating work
- Get context on pending tasks
- Understand what was already attempted
- See what failed and why

### Session Management Tools

```bash
# List recent sessions (last 20 by default)
session_list(limit=20, from_date="2026-03-29")

# Search sessions for specific topics/tasks
session_search(query="Bene2Luxe bug fix", limit=10)

# Read full session history
session_read(session_id="ses_abc123", include_todos=true)

# Get session metadata (date range, message count, agents used)
session_info(session_id="ses_abc123")
```

### Cron Job Session Pattern

**Every cron run creates a session**. Key patterns:

| Pattern | Session ID Prefix | Description |
|---------|------------------|--------------|
| `opencode_interactive_YYYYMMDD_HHMMSS.log` | `ses_2c...` | Main cron runs |
| Morning runs | `ses_2c7...` | 09:00-10:00 |
| Midday runs | `ses_2c5...` | 12:00-13:00 |
| Afternoon runs | `ses_2c6...` | 14:00-18:00 |
| Evening runs | `ses_2c4...` | 18:00-23:00 |

### Workflow: Check Previous Work Before Starting

```
1. session_list() → Find recent cron sessions
2. session_search(query="task or topic") → Find specific discussions
3. session_read(session_id) → Read what was done
4. Proceed with new work, avoiding duplication
```

### Example: Checking Yesterday's Work

```bash
# Find all sessions from yesterday
session_list(from_date="2026-03-29", limit=20)

# Search for specific task (e.g., "casquette" or "hat sizes")
session_search(query="casquette sizes bug", limit=5)

# Read a specific session to see what was attempted
session_read(session_id="ses_2c5e08b72ffe8LHrj9AAGc7dyI")
```

### Session Log Files

Sessions are also saved as log files:
```
/Users/vakandi/EliaAI/logs/
├── opencode_interactive_20260329_160001.log    # Cron run at 16:00
├── opencode_interactive_20260329_180001.log    # Cron run at 18:00
├── opencode_interactive_20260330_120001.log    # Today's run
└── ...
```

**Quick check via bash:**
```bash
ls -la /Users/vakandi/EliaAI/logs/opencode_interactive_2026*.log | tail -10
```

### Context Continuity Rule

**MANDATORY at start of each session:**
1. Check `session_list()` for recent cron runs
2. Check `session_search()` for relevant past discussions
3. Read key sessions if unclear about current state
4. Never repeat work that's already done
5. Note what failed before and why

This ensures Elia maintains context across cron runs and doesn't waste time re-doing work or repeating mistakes.
