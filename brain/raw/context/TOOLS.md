# [[../../wiki/tools/Index|TOOLS]].md - Quick Reference

> ⚠️ All commands here = **terminal commands** — use the `bash` tool (not [[../../wiki/skills/Index|SKILLS]]).

---

**All [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] [[../../wiki/tools/Index|TOOLS]] are ALWAYS 100% available.** If any [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] tool fails:

1. **[[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] issues** → [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]]:
   ```bash
   /Users/vakandi/Documents/mcps_server/restart-[[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]-bridge.sh restart
   ```

2. **[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Playwright|Playwright]] issues** → [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]]:
   ```bash
   /Users/vakandi/Documents/mcps_server/restart_clean_mcp_playwright.sh
   ```

3. **Any other [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] failure** → **IMMEDIATELY** [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] a new ulw-loop to investigate:
   ```
   /ulw-loop
   ```
   See section **"ULW-Loop (Autonomous [[../../wiki/concepts/AI-Automation#tasks|Task]] Execution)"** (lines 174-200) for full details on how to [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] and use it.

   Then send a report to [[../../wiki/channels/Telegram|Telegram]] with:
   - What [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] failed
   - Error messages
   - Investigation steps taken

**[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] Server Location**: `/Users/vakandi/Documents/mcps_server/`

---

## 🔊 Voice Message Handling ([[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] & [[../../wiki/channels/Telegram|Telegram]])

**CRITICAL**: When receiving or sending voice messages via [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]/[[../../wiki/channels/Telegram|Telegram]], ALWAYS check for existing transcripts before transcribing.

### Voice Message Workflow

1. **Detect voice message** → Check `hasMedia` and `mediaType` in message
2. **Extract date** → Get timestamp from message → format as `YYYY-MM-DD`
3. **Check [[../../wiki/HOME|Docs]] folder** → Look for `/Users/vakandi/EliaAI/[[../../wiki/HOME|Docs]]/{YYYY-MM-DD}/`
4. **Check existing transcript** → Search for `{wa|tg}_{msg_id}` in filenames
5. **If already transcribed** → Skip processing
6. **If not transcribed** → Download audio → Transcribe with Whisper → Analyze as text

### Transcript Filename Convention

```
run_{source}_{msg_id}_{DD_mmm_YYYY_HHMM}.md
```

| Field | Description | Example |
|-------|-------------|---------|
| `source` | `wa` ([[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]) or `tg` ([[../../wiki/channels/Telegram|Telegram]]) | `wa` |
| `msg_id` | Message ID from the platform | `msg_abc123` |
| `DD_mmm_YYYY_HHMM` | Day, month (French), year, time | `29_mars_2026_0945` |

**Examples:**
- [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]: `run_wa_msg_abc123_29_mars_2026_0945.md`
- [[../../wiki/channels/Telegram|Telegram]]: `run_tg_msg_xyz789_29_mars_2026_1000.md`

### Transcript Check Logic

```bash
# Check if message already transcribed
MSG_ID="<message_id>"
TODAY=$(date +%Y-%m-%d)
DOCS_DIR="/Users/vakandi/EliaAI/[[../../wiki/HOME|Docs]]/$TODAY"

# Direct filename check (fastest)
ls "$DOCS_DIR"/*_"$MSG_ID"_*.md 2>/dev/null && echo "Already transcribed" || echo "Need transcription"

# Or grep for msg_id in any [[../../wiki/concepts/File-Management|File]]
grep -rl "$MSG_ID" "$DOCS_DIR"/*.md 2>/dev/null && echo "Already transcribed"
```

### Voice Message Transcription Command

```bash
# Download audio first via [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]], then transcribe
whisper /path/to/audio.ogg --model large-v3 --language French --[[../../wiki/concepts/AI-Automation#tasks|Task]] transcribe
```

### Transcript [[../../wiki/concepts/File-Management|File]] [[../../wiki/concepts/Marketing-Concepts|Content]] Template

```[[../../wiki/concepts/Documentation|Markdown]]
# Voice Message Transcript

**Source:** [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] / [[../../wiki/channels/Telegram|Telegram]]
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

## [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-CLI (All External Services)

**⚠️ IMPORTANT:** `[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli` is a **shell command** (terminal/bash), NOT a tool within [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]. It wraps all [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] servers and exposes them via command-line interface.

**Info:** `[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli -h` or `[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli --help`

```bash
# List servers (shell command)
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli

# All commands below are SHELL COMMANDS - [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] them in terminal or via bash

# [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] list_chats '{"limit":20}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] list_messages '{"chat_jid":"...","limit":30}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] send_message '{"recipient":"...","message":"..."}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] download_media '{"message_id":"...","chat_jid":"..."}'

# ⚠️ VOICE MESSAGE HANDLING: When listing messages, check hasMedia + mediaType="ptt"
# If voice message detected:
# 1. Check date → /Users/vakandi/EliaAI/[[../../wiki/HOME|Docs]]/{YYYY-MM-DD}/
# 2. Search for "wa_{msg_id}" in filenames to check if transcribed
# 3. If not → download_media → whisper → save as run_wa_{msg_id}_{DD_mmm_YYYY_HHMM}.md

# [[../../wiki/channels/Telegram|Telegram]] (Watson - Personal [[../../wiki/businesses/Bene2Luxe#account|Account]])
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Telegram|Telegram]] get_default_group_messages '{"limit":20}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Telegram|Telegram]] send_msg_to_default_group '{"message":"..."}'

# Rule: [[../../wiki/channels/Telegram|Telegram]] send_msg_to_default_group = URGENT/blockers only | [[../../wiki/channels/Discord-EliaWorkSpace|Discord]] #reports = Regular reports

[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Telegram|Telegram]] get_personal_dms_only '{"limit":20}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Telegram|Telegram]] get_personal_dms_and_groups '{"limit":50}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Telegram|Telegram]] send_msg_to_recipient '{"recipient":"@username","message":"Hello!"}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Telegram|Telegram]] send_voice_to_recipient '{"recipient":"@username","file_path":"/path/to/audio.ogg"}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Telegram|Telegram]] send_file_to_recipient '{"recipient":"-1001234567890","file_path":"/path/to/[[../../wiki/concepts/File-Management|File]].pdf"}'

# ⚠️ VOICE MESSAGE HANDLING: Check message objects for voice/audio
# If voice message detected (voice=true or has audio):
# 1. Check date → /Users/vakandi/EliaAI/[[../../wiki/HOME|Docs]]/{YYYY-MM-DD}/
# 2. Search for "tg_{msg_id}" in filenames to check if transcribed
# 3. If not → download audio [[../../wiki/concepts/File-Management|File]] → whisper → save as run_tg_{msg_id}_{DD_mmm_YYYY_HHMM}.md

# [[../../wiki/channels/Telegram|Telegram]] (Approvals)
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Telegram|Telegram]] send_approval_request '{"text":"Approve this?","chat_id":"..."}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Telegram|Telegram]] get_approval_responses '{}'

# [[../../wiki/channels/Discord-EliaWorkSpace|Discord]] (Personal [[../../wiki/businesses/Bene2Luxe#account|Account]] - your own [[../../wiki/channels/Discord-EliaWorkSpace|Discord]])
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_get_dms '{"limit":10}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_send_dm '{"user_id":"...","message":"..."}'

# [[../../wiki/channels/Discord-EliaWorkSpace|Discord]] Server (EliaWorkSpace - bot [[../../wiki/businesses/Bene2Luxe#account|Account]] "watson")
# Get server structure
bash: cd ~/Documents/EliaVoiceRecorder && DISCORD_BOT_TOKEN="<your-discord-bot-token>" python3 discord_server_structure.py

# List channels
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-server-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_execute '{"operation":"channels.list","params":{}}'

# Read messages from channel (last N messages)
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-server-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_execute '{"operation":"messages.list","params":{"channel_id":"CHANNEL_ID","limit":20}}'

# Read messages from last N hours (default 12h) - CONVENIENCE WRAPPER
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-server-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_execute '{"operation":"messages.list_range","params":{"channel_id":"CHANNEL_ID","hours":12,"limit":50}}'

# Read messages after specific timestamp (ISO 8601 format)
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-server-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_execute '{"operation":"messages.list","params":{"channel_id":"CHANNEL_ID","after_timestamp":"2026-04-04T12:00:00Z","limit":50}}'

# Read messages after/before specific snowflake ID
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-server-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_execute '{"operation":"messages.list","params":{"channel_id":"CHANNEL_ID","after":"1489000000000000000","limit":50}}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-server-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_execute '{"operation":"messages.list","params":{"channel_id":"CHANNEL_ID","before":"1490000000000000000","limit":50}}'

# Send message to channel (RECOMMENDED - handles special chars properly)
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-server-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_send_message '{"channel_id":"1489244810777727046","[[../../wiki/concepts/Marketing-Concepts|Content]]":"Your message here 🚀"}'

# Send [[../../wiki/concepts/File-Management|File]] directly to channel (NEW! - always prefer this over sending paths)
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-server-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_send_file '{"channel_id":"1489244810777727046","file_path":"/Users/vakandi/EliaAI/[[../../wiki/HOME|Docs]]/report.md","[[../../wiki/concepts/Marketing-Concepts|Content]]":"📋 Detailed report"}'

# Fallback: Upload to tmpfiles.org if direct upload fails
# curl -X POST [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://tmpfiles.org/api/v1/upload -F "[[../../wiki/concepts/File-Management|File]]=@/path/to/[[../../wiki/concepts/File-Management|File]].pdf"

# Or read from [[../../wiki/concepts/File-Management|File]]:
cat report.md | python3 /Users/vakandi/EliaAI/[[../../wiki/tools/Index|TOOLS]]/discord_send.py 1489244810777727046 --stdin

# Server info
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-server-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] discord_execute '{"operation":"guild.get","params":{}}'

## [[../../wiki/channels/Discord-EliaWorkSpace|Discord]] Channel Mapping (EliaWorkSpace - Channel IDs)

### [[../../wiki/people/Elia|Elia]]-HQ (SYSTEM - [[../../wiki/people/Elia|Elia]] [[../../wiki/concepts/AI-Automation|AI]])
| Channel | Channel ID |
|---------|------------|
| 💡-urgent | `1489244806310793216` |
| 📊-reports | `1489244810777727046` |
| 📝-activity-logs | `1489244812107317402` |
| 📚-knowledge | `1489244815790182450` |
| ✅-tasks-tracker | `1489244818134794330` |
| 🖥️-health-checks | `1489247935807099020` |

### BEN2LUXE ([[../../wiki/systems/Jira-Tickets-Index|Jira]]: BEN) - DIFFERENT BUSINESS
| Channel | Channel ID |
|---------|------------|
| 🛍️-products | `1489244857250615416` |
| 📦-[[../../wiki/businesses/B2LUXE-BUSINESS#orders|Orders]] | `1489244862871244950` |
| 👥-clients | `1489244868235755580` |
| 📱-social-media | `1489244873847734292` |
| 📤-marketing | `1489244878431846523` |
| 📂-management | `1489246873998065745` |
| [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]-[[../../wiki/concepts/AI-Automation|AI]]-to-copy | `1489247163824345228` |

### [[../../wiki/businesses/CoBou-Agency|CoBou]]-AGENCY ([[../../wiki/systems/Jira-Tickets-Index|Jira]]: COBOUAGENC) - DIFFERENT BUSINESS
| Channel | Channel ID |
|---------|------------|
| 🚀-projects | `1489244906013593642` |
| 👥-clients | `1489244911449538680` |
| 💻-dev-work | `1489244916352684045` |
| 💰-invoices | `1489244921180455035` |

### [[../../wiki/businesses/ZovaBoost|ZovaBoost]] ([[../../wiki/systems/Jira-Tickets-Index|Jira]]: ZOVAPANEL) - DIFFERENT BUSINESS
| Channel | Channel ID |
|---------|------------|
| 💻-panel | `1489244946673176618` |
| 👥-clients | `1489244951861661787` |
| 🎨-support | `1489244963261780173` |

### [[../../wiki/businesses/Mayavanta|MAYAVANTA]] ([[../../wiki/systems/Jira-Tickets-Index|Jira]]: MAYA) - DIFFERENT BUSINESS
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

### [[../../wiki/businesses/OGBoujee|OGBoujee]] ([[../../wiki/systems/Jira-Tickets-Index|Jira]]: OGB) - DIFFERENT BUSINESS
| Channel | Channel ID |
|---------|------------|
| 👜-products | `1489628023266480280` |
| 📦-[[../../wiki/businesses/B2LUXE-BUSINESS#orders|Orders]] | `1489628028727459945` |
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
| [[../../wiki/people/Elia|Elia]]-HQ | `1489244763017187549` |
| BEN2LUXE | `1489244764808417320` |
| [[../../wiki/businesses/CoBou-Agency|CoBou]]-AGENCY | `1489244768235028633` |
| [[../../wiki/businesses/ZovaBoost|ZovaBoost]] | `1489244769505906818` |
| [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]-YOUTUBE | `1489244773284974704` |
| [[../../wiki/businesses/Mayavanta|MAYAVANTA]] | `1489244774882873364` |
| TEAM | `1489244778347499691` |
| [[../../wiki/businesses/OGBoujee|OGBoujee]] | `1489628000730484938` |

# [[../../wiki/channels/Gmail|Gmail]] (server id: [[../../wiki/channels/Gmail|Gmail]] — check [[../../wiki/tools/Index|TOOLS]]: [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli info [[../../wiki/channels/Gmail|Gmail]] search_emails)
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Gmail|Gmail]] search_emails '{"query":"in:inbox newer_than:7d","maxResults":20}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Gmail|Gmail]] read_email '{"messageId":"..."}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Gmail|Gmail]] draft_email '{"to":["you@example.com"],"subject":"Subject","body":"Plain text body"}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Gmail|Gmail]] send_email '{"to":["you@example.com"],"subject":"Subject","body":"Plain text body"}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/channels/Gmail|Gmail]] list_email_labels '{}'

# 📧 [[../../wiki/systems/IONOS|IONOS]] Business Email (PRIMARY - Business Emails)

## Available [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] Servers

### mail_contact_cofibou_distribution (contact@cofibou-distribution.com)
**Use this for:** Cofibou Distribution LLC emails - business logistics, carrier outreach, Point Relais setup

### mail_contact_cobou_agency (contact@[[../../wiki/businesses/CoBou-Agency|CoBou]].agency)
**Use this for:** [[../../wiki/businesses/CoBou-Agency|CoBou]] Agency, [[../../wiki/businesses/ZovaBoost|ZovaBoost]], AccForge emails

## ⚠️ CRITICAL: How to Send Emails ([[../../wiki/concepts/API-Integration|JSON]] Payload Method)

**The `recipients` field MUST be a list (array), NOT a string!**

### WRONG ❌
```bash
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call mail_contact_cofibou_distribution send_email '{"recipients":"recipient@email.com",...}'
```

### CORRECT ✅ — Use [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Python-Scripting|Python]] for complex body text
```[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Python-Scripting|Python]]
python3 << 'PYEOF'
import subprocess
import [[../../wiki/concepts/API-Integration|JSON]]

body = """Your email body here.
Can have multiple lines."""

payload = {
    "recipients": ["recipient@email.com"],
    "subject": "Subject Line",
    "body": body
}

result = subprocess.[[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]](
    ["[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli", "call", "mail_contact_cofibou_distribution", "send_email", [[../../wiki/concepts/API-Integration|JSON]].dumps(payload)],
    capture_output=True, text=True
)
print(result.stdout)
PYEOF
```

## Quick Commands

```bash
# Read inbox
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call mail_contact_cofibou_distribution list_emails_metadata '{"limit":20}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call mail_contact_cofibou_agency list_emails_metadata '{"limit":20}'

# Read specific email
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call mail_contact_cofibou_distribution get_emails_content '{"email_ids":["123"]}'

# Send email (via [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Python-Scripting|Python]] - see above for body with special chars)
```

## ⚠️ IMPORTANT: Use COFIBOU email for business logistics!
- **contact@cofibou-distribution.com** = Cofibou Distribution LLC = business logistics, carriers, Point Relais
- **contact@[[../../wiki/businesses/CoBou-Agency|CoBou]].agency** = [[../../wiki/businesses/CoBou-Agency|CoBou]] Agency = [[../../wiki/businesses/CoBou-Agency|CoBou]]/[[../../wiki/businesses/ZovaBoost|ZovaBoost]]/AccForge business

# ⚠️ CRITICAL: Most business emails ([[../../wiki/businesses/B2LUXE-BUSINESS#orders|Orders]], invoices, notifications) now redirect to this inbox!
# Check this FIRST for business issues, not [[../../wiki/channels/Gmail|Gmail]].

[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call mail_contact_cobou_agency list_available_accounts '{}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call mail_contact_cobou_agency list_emails_metadata '{"account_name":"[[../../wiki/systems/IONOS|IONOS]]","limit":20}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call mail_contact_cobou_agency get_emails_content '{"account_name":"[[../../wiki/systems/IONOS|IONOS]]","email_ids":["123"]}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call mail_contact_cobou_agency send_email '{"account_name":"[[../../wiki/systems/IONOS|IONOS]]","recipients":[" recipient@email.com"],"subject":"Subject","body":"Message"}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call mail_contact_cobou_agency delete_emails '{"account_name":"[[../../wiki/systems/IONOS|IONOS]]","email_ids":["123"]}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call mail_contact_cobou_agency download_attachment '{"account_name":"[[../../wiki/systems/IONOS|IONOS]]","email_id":"123","attachment_index":0,"save_path":"/path/to/save"}'

# [[../../wiki/systems/Jira-Tickets-Index|Jira]]
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-atlassian create_issue '{"project":"BEN","summary":"...","description":"...","issue_type":"[[../../wiki/concepts/AI-Automation#tasks|Task]]"}'
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-atlassian jira_get_project_issues '{"project_key":"BEN"}'

# [[../../wiki/systems/SSH-Servers|SSH]]
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/systems/SSH-Servers|SSH]]-mpc-server-[[../../wiki/systems/MultiSaasDeploy|MultiSaasDeploy]] execute-command '{"cmdString":"ls -la"}'
```

### Business Groups ([[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]])
| Group | JID |
|-------|-----|
| [[../../wiki/businesses/CoBou-Agency|CoBou]] PowerRangers | `120363420711538035@g.us` |
| [[../../wiki/businesses/B2LUXE-BUSINESS|B2LUXE BUSINESS]] | `120363408208578679@g.us` |
| [[../../wiki/businesses/OGBoujee|OGBoujee]] 👜 BUSINESS | `120363425082264099@g.us` |
| [[../../wiki/businesses/Mayavanta|MAYAVANTA]] | `120363405622746597@g.us` |

---

## Agent-Browser (Web Automation)

**Info:** `agent-browser -h`

**Use real [[../../wiki/channels/Google|Google]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]]** (not [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]] for Testing) to reduce bot detection on heavy/repetitive tasks.

```bash
# Navigation
agent-browser open <url> --executable-path "/Applications/[[../../wiki/channels/Google|Google]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]].app/Contents/MacOS/[[../../wiki/channels/Google|Google]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]]" --headed
agent-browser click <selector>
agent-browser fill <selector> <text>
agent-browser snapshot
agent-browser screenshot [path]

# Alias (add to ~/.zshrc): alias [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]]="agent-browser --executable-path \"/Applications/[[../../wiki/channels/Google|Google]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]].app/Contents/MacOS/[[../../wiki/channels/Google|Google]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]]\" --headed"
[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]] open <url>   # Visible browser with real [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]] (less bot detection)
[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]] snapshot     # Take screenshot

# Email
agent-browser open [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://mail.[[../../wiki/channels/ProtonMail|Proton]].me/u/1/inbox --executable-path "/Applications/[[../../wiki/channels/Google|Google]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]].app/Contents/MacOS/[[../../wiki/channels/Google|Google]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]]" --headed
agent-browser open [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://email.[[../../wiki/systems/IONOS|IONOS]].fr/appsuite/#!!&app=io.ox/mail --executable-path "/Applications/[[../../wiki/channels/Google|Google]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]].app/Contents/MacOS/[[../../wiki/channels/Google|Google]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Chrome-Automation|Chrome]]" --headed
```

More options: `agent-browser -h`

---

## Voice Transcription (Whisper)

**Info:** `whisper -h`

```bash
# Download audio first, then transcribe
whisper /path/to/audio.ogg --model large-v3 --language French --[[../../wiki/concepts/AI-Automation#tasks|Task]] transcribe
```

---

## [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Cursor-IDE|Cursor]]-IDE|IDE]] Work Extraction

**Info:** `./[[../../wiki/tools/Index|TOOLS]]/get_ide_work.sh -h`

```bash
./[[../../wiki/tools/Index|TOOLS]]/get_ide_work.sh              # All IDEs (recommended)
./[[../../wiki/tools/Index|TOOLS]]/get_opencode_work.sh 24       # [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] only (last 24h)
```

---

## [[../../wiki/channels/Google|Google]] Workspace

**Info:** `gws-workspace -h` or `gws-workspace help`

```bash
gws-workspace create-event "Title" "Desc"
gws-workspace create-[[../../wiki/concepts/AI-Automation#tasks|Task]] "[[../../wiki/concepts/AI-Automation#tasks|Task]]" "Notes"
gws-workspace import-md "[[../../wiki/concepts/File-Management|File]].md" "Title"
gws-workspace list-events
```

---

## [[../../wiki/systems/Jira-Tickets-Index|Jira]] Projects
| Business | Key |
|----------|-----|
| [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] | `BEN` |
| [[../../wiki/businesses/CoBou-Agency|CoBou]] Agency | `COBOUAGENC` |
| [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]/YouTube | `TIKYT` |
| [[../../wiki/businesses/ZovaBoost|ZovaBoost]] | `ZOVAPANEL` |

---

## [[../../wiki/systems/SSH-Servers|SSH]] Server (use [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli)

**Info:** `[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli -h`

```bash
# Main SaaS server ([[../../wiki/businesses/Bene2Luxe|Bene2Luxe]], [[../../wiki/businesses/ZovaBoost|ZovaBoost]], [[../../wiki/businesses/Netfluxe|Netfluxe]], [[../../wiki/businesses/OGBoujee|OGBoujee]])
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call [[../../wiki/systems/SSH-Servers|SSH]]-mpc-server-[[../../wiki/systems/MultiSaasDeploy|MultiSaasDeploy]] execute-command '{"cmdString":"ls -la"}'
```

---

## Voice Output

**TTS**: `[[../../wiki/people/Elia|Elia]]-voxtral-speak` (Mistral, fast, French) → fallback: `[[../../wiki/people/Elia|Elia]]-speak`

**⚠️ ALWAYS use the right tone:**
| Flag | Tone | When to use |
|------|------|-------------|
| `-j` | Happy | Good news, celebrations, positive updates |
| `-d` | Sad | Blockers, problems, urgent issues |
| `-a` | Angry | Urgent warnings, serious issues |
| `--play` | Play | Play audio after generation |
| `-x` | Fallback | Use [[../../wiki/people/Elia|Elia]]-speak fallback |

```bash
[[../../wiki/people/Elia|Elia]]-voxtral-speak "Great news!" -j           # happy
[[../../wiki/people/Elia|Elia]]-voxtral-speak "Problem detected" -d      # sad
[[../../wiki/people/Elia|Elia]]-voxtral-speak "URGENT!" -a               # angry
[[../../wiki/people/Elia|Elia]]-voxtral-speak "Message" --play          # play audio
[[../../wiki/people/Elia|Elia]]-speak -x "Message"                        # fallback
```

---

## ProtonMail CLI

**Info:** `~/.[[../../wiki/systems/Docker-Servers|Local]]/bin/protonmail -h`

```bash
# Location: ~/.[[../../wiki/systems/Docker-Servers|Local]]/bin/protonmail
~/.[[../../wiki/systems/Docker-Servers|Local]]/bin/protonmail list                    # Inbox
~/.[[../../wiki/systems/Docker-Servers|Local]]/bin/protonmail list -t sent           # Sent
~/.[[../../wiki/systems/Docker-Servers|Local]]/bin/protonmail list -t drafts         # Drafts
~/.[[../../wiki/systems/Docker-Servers|Local]]/bin/protonmail list -t spam          # Spam
~/.[[../../wiki/systems/Docker-Servers|Local]]/bin/protonmail list -t allmail        # All mail
```

---

## 🚀 ULW-Loop (Autonomous [[../../wiki/concepts/AI-Automation#tasks|Task]] Execution)

**ULW-Loop = Unlimited iterations for executing tasks during cronjob runs**

### When to Use
- [[../../wiki/concepts/AI-Automation#tasks|Task]] found during cronjob → execute it fully, don't just report
- Multiple tasks to do → [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] ulw-loop to process all of them
- Autonomous work mode → ulw-loop runs until `<promise>DONE</promise>`

### How to Launch
```
/ulw-loop
```

### What Happens
- Unlimited iterations until tasks complete
- Spawns subagents for parallel execution
- Delegates to specialized agents (marketing, dev, [[../../wiki/businesses/Bene2Luxe#revenue|Sales]], etc.)

### Using oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] with Custom Subagents

**⚠️ IMPORTANT**: Always use `oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]` (not direct `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]`) to use custom subagents.

```bash
# Syntax
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a <agent> "<[[../../wiki/concepts/AI-Automation#tasks|Task]]/message>"

# Available Subagents (categories)
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a setbon "Message pour Setbon"           # Marketing & Conversion
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] "Message pour [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]"      # Luxury e-commerce
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a [[../../wiki/businesses/CoBou-Agency|CoBou]]-agency "Message pour [[../../wiki/businesses/CoBou-Agency|CoBou]]"      # B2B digital
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a [[../../wiki/businesses/ZovaBoost|ZovaBoost]] "Message pour [[../../wiki/businesses/ZovaBoost|ZovaBoost]]"    # SMMPanel
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a gilfoyle "Message pour Gilfoyle"       # Backend dev
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]-youtube-auto "Message"         # [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]/YouTube auto

# [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] with ULW loop (unlimited iterations until DONE)
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a setbon "你的任务 ici" --ulw-loop --completion-promise DONE --max-iterations 0
```

**Why oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]?**
- Direct `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]` (v1.3.10) doesn't support categories/subagents
- It will show: `agent "setbon" is a subagent, not a primary agent`
- oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] handles subagent routing correctly

### High-[[../../wiki/concepts/Pricing|Value]] Tasks to Execute
- Create accounts (Copify, Trendtrack, ad networks)
- Browse competitors ([[../../wiki/people/Wael|Wael]]'s Edge folders: SHOP-5000$COPIFY, SHOP500-1000$COPIFY)
- Build React mockups for conversion ideas
- Research competitors and market opportunities
- Prepare [[../../wiki/businesses/Bene2Luxe#revenue|Sales]] documents and proposals
- ANYTHING that moves businesses forward

---

## 🚀 Starting New Work Sessions

```bash
# Quick start (uses big-pickle by default, ULW-loop enabled)
./start_agents.sh

# With extra context / [[../../wiki/concepts/AI-Automation#tasks|Task]] to execute
./start_agents.sh --extra-[[../../wiki/concepts/Prompt-Engineering|PROMPT]]="Create a Copify [[../../wiki/businesses/Bene2Luxe#account|Account]] and research ad earnings recovery"

# With proxy enabled
./start_agents.sh --proxy --extra-[[../../wiki/concepts/Prompt-Engineering|PROMPT]]="[[../../wiki/concepts/AI-Automation#tasks|Task]] description here"
```

**Options:**
| Flag | Purpose |
|------|---------|
| `--extra-[[../../wiki/concepts/Prompt-Engineering|PROMPT]]="..."` | Add [[../../wiki/concepts/AI-Automation#tasks|Task]] context to agent |
| `--proxy` | [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] through proxychains4 |
| `--model=big-pickle` | Default (free, stable) |

---

## 🖼️ Image Generation ([[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] - Higgsfield.[[../../wiki/concepts/AI-Automation|AI]])

**⚠️ ALWAYS use this script for image generation** - Script: `/Users/vakandi/Documents/HiggsFieldGenerator/generate_photo_higgsfield.py`

The script automatically uses UNLIMITED mode (free, no credits).

### Quick Commands

```bash
cd /Users/vakandi/Documents/HiggsFieldGenerator

# [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-[[../../wiki/skills/Higgsfield-Video|Video]]|Mascoot]] scenarios
python3 generate_photo_higgsfield.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-[[../../wiki/skills/Higgsfield-Video|Video]]|Mascoot]] vacation
python3 generate_photo_higgsfield.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-[[../../wiki/skills/Higgsfield-Video|Video]]|Mascoot]] party --items "champagne"
python3 generate_photo_higgsfield.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-[[../../wiki/skills/Higgsfield-Video|Video]]|Mascoot]] store --model gpt_image

# Human with [[../../wiki/businesses/Bene2Luxe#products|Product]]
python3 generate_photo_higgsfield.py human "[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] bag"
python3 generate_photo_higgsfield.py human "[[../../wiki/concepts/Luxury-Brands#dior|Dior]] sneakers" --scenario wearing_sneakers

# With reference images (multi-photo support!)
python3 generate_photo_higgsfield.py human "Luxury Bag" --images "/path/to/photo1.png" "/path/to/photo2.png"
python3 generate_photo_higgsfield.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-[[../../wiki/skills/Higgsfield-Video|Video]]|Mascoot]] vacation --images "store.png" "mascot.png"

# Multiple models (queue mode)
python3 generate_photo_higgsfield.py human "[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] bag" --models "gpt_image,soul_v2,flux_2_pro"
```

### CLI Options

| Flag | Description |
|------|-------------|
| `--model`, `-m` | Model (default: gpt_image) |
| `--models`, `-M` | Comma-separated models for batch |
| `--images`, `-i` | Reference images (paths) |
| `--output`, `-o` | Output [[../../wiki/concepts/File-Management|File]] path |

### Available Models (Unlimited/Free)

| Model | Command |
|-------|---------|
| [[../../wiki/people/GPT|GPT]] Image | `gpt_image` |
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
3. **Upload images** - `agent-browser upload "[type=[[../../wiki/concepts/File-Management|File]]]" "/path/to/image.png"`
4. **Set [[../../wiki/concepts/Prompt-Engineering|PROMPT]]** - Via localStorage injection + reload
5. **Click Generate** - Click the Unlimited button
6. **Monitor queue** - Via JavaScript eval

**Documentation**: `/Users/vakandi/Documents/HiggsFieldGenerator/[[../../wiki/HOME|Docs]]/GENERATE_PHOTO_README.md`

---

## 🎯 [[../../wiki/concepts/AI-Automation#tasks|Task]] Delegation (during ulw-loop)

```typescript
// Development tasks
[[../../wiki/concepts/AI-Automation#tasks|Task]](category="backend-dev", load_skills=["coding-agent"], [[../../wiki/concepts/Prompt-Engineering|PROMPT]]="...")

// Marketing tasks
[[../../wiki/concepts/AI-Automation#tasks|Task]](category="marketing-social", load_skills=[], [[../../wiki/concepts/Prompt-Engineering|PROMPT]]="...")

// E-commerce ([[../../wiki/businesses/Bene2Luxe|Bene2Luxe]])
[[../../wiki/concepts/AI-Automation#tasks|Task]](category="ecommerce-luxury", load_skills=["luxury-[[../../wiki/concepts/Luxury-Brands|Fashion]]-marketing-genius"], [[../../wiki/concepts/Prompt-Engineering|PROMPT]]="...")

// Multiple parallel agents
[[../../wiki/concepts/AI-Automation#tasks|Task]](run_in_background=true, ...) // x3-5 in parallel
```

---

**Full details**: See [[../../wiki/concepts/Prompt-Engineering|PROMPT]].md section "[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] [[../../wiki/tools/Index|TOOLS]]" and "Voice Transcription"

---

## 🔍 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] Session [[../../wiki/tools/Index|TOOLS]] (Cron Job Context)

**CRITICAL**: These [[../../wiki/tools/Index|TOOLS]] let [[../../wiki/people/Elia|Elia]] access previous cron job sessions for continuity and context.

### Why Use These?

When starting a new session, [[../../wiki/people/Elia|Elia]] should check what the previous cron runs did to:
- Avoid duplicating work
- Get context on pending tasks
- Understand what was already attempted
- See what failed and why

### Session Management [[../../wiki/tools/Index|TOOLS]]

```bash
# List recent sessions (last 20 by default)
session_list(limit=20, from_date="2026-03-29")

# Search sessions for specific topics/tasks
session_search(query="[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] bug fix", limit=10)

# Read full session [[../../wiki/docs/Sessions|History]]
session_read(session_id="ses_abc123", include_todos=true)

# Get session metadata (date [[../../wiki/businesses/Bene2Luxe#sizing|Range]], message count, agents used)
session_info(session_id="ses_abc123")
```

### Cron Job Session Pattern

**Every cron [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] creates a session**. Key patterns:

| Pattern | Session ID Prefix | Description |
|---------|------------------|--------------|
| `opencode_interactive_YYYYMMDD_HHMMSS.log` | `ses_2c...` | Main cron runs |
| Morning runs | `ses_2c7...` | 09:00-10:00 |
| Midday runs | `ses_2c5...` | 12:00-13:00 |
| Afternoon runs | `ses_2c6...` | 14:00-18:00 |
| Evening runs | `ses_2c4...` | 18:00-23:00 |

### Workflow: Check Previous Work Before Starting

```
1. session_list() → [[../../wiki/concepts/Search|Find]] recent cron sessions
2. session_search(query="[[../../wiki/concepts/AI-Automation#tasks|Task]] or topic") → [[../../wiki/concepts/Search|Find]] specific discussions
3. session_read(session_id) → Read what was done
4. Proceed with new work, avoiding duplication
```

### Example: Checking Yesterday's Work

```bash
# [[../../wiki/concepts/Search|Find]] all sessions from yesterday
session_list(from_date="2026-03-29", limit=20)

# Search for specific [[../../wiki/concepts/AI-Automation#tasks|Task]] (e.g., "casquette" or "hat sizes")
session_search(query="casquette sizes bug", limit=5)

# Read a specific session to see what was attempted
session_read(session_id="ses_2c5e08b72ffe8LHrj9AAGc7dyI")
```

### Session Log Files

Sessions are also saved as log files:
```
/Users/vakandi/EliaAI/logs/
├── opencode_interactive_20260329_160001.log    # Cron [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] at 16:00
├── opencode_interactive_20260329_180001.log    # Cron [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] at 18:00
├── opencode_interactive_20260330_120001.log    # Today's [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]]
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

This ensures [[../../wiki/people/Elia|Elia]] maintains context across cron runs and doesn't waste time re-doing work or repeating mistakes.
