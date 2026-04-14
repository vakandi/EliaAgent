# Morning Routine - Daily Task Review

Invoked daily by the cron job **Morning Business Review (9am)** (schedule `0 9 * * *`).

You are executing the **Morning Mode** routine. This is a daily automated task that runs every morning to review work progress, generate task lists, and send morning reports to the team.

> **⚠️ CRITICAL**: Before calling mcp-cli commands, ALWAYS load the skill first: `skill(name="mcp-cli")`. Then use `bash` tool to execute them.
> Read `/Users/vakandi/EliaAI/context/TOOLS.md` for full command reference.

---

## ⚠️ MANDATORY PRE-REPORT CHECKLIST (CANNOT SKIP)

**BEFORE sending ANY Discord report, you MUST complete this checklist:**

```
PRE-REPORT CHECKLIST:
For each business area, decide: DOES THIS APPLY THIS RUN?

☐ Server Health / MCP Status:
  If YES → Send to #health-checks (1489247935807099020)
  Command: mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489247935807099020","content":"YOUR MESSAGE"}'

☐ Bene2Luxe Orders / Sales:
  If YES → Send to #orders (1489244862871244950)
  Command: mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244862871244950","content":"YOUR MESSAGE"}'

☐ Bene2Luxe Products:
  If YES → Send to #products (1489244857250615416)
  Command: mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244857250615416","content":"YOUR MESSAGE"}'

☐ Bene2Luxe Clients:
  If YES → Send to #clients (1489244868235755580)
  Command: mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244868235755580","content":"YOUR MESSAGE"}'

☐ ZovaBoost Panel:
  If YES → Send to #panel (1489244946673176618)
  Command: mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244946673176618","content":"YOUR MESSAGE"}'

☐ TikTok/YouTube Content:
  If YES → Send to #content (1489244954646679662)
  Command: mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244954646679662","content":"YOUR MESSAGE"}'

☐ TikTok/YouTube Analytics:
  If YES → Send to #analytics (1489244965337956514)
  Command: mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244965337956514","content":"YOUR MESSAGE"}'
```

**⚠️ IF UNSURE WHERE TO SEND → VERIFY CHANNELS FIRST:**
```bash
mcp-cli call discord-server-mcp discord_execute '{"operation":"channels.list","params":{}}'
```
Check current channel structure and match your content to the most appropriate channel.

**THEN and ONLY THEN:**
- Send brief summary (3-5 bullets MAX) to #reports (1489244810777727046)
- DO NOT repeat details already sent to other channels

**❌ IF YOU SKIP THIS CHECKLIST → REPORT IS INVALID**

---

## ⚠️ NEVER SEND FILE PATHS - ALWAYS SEND FILES DIRECTLY

**When attaching documents, screenshots, or files to Discord reports:**

### ✅ CORRECT - Send file directly (NEW!):
```bash
# Send file directly to Discord channel
mcp-cli call discord-server-mcp discord_send_file '{"channel_id":"1489244810777727046","file_path":"/Users/vakandi/EliaAI/docs/2026-04-08/report.md","content":"📋 Rapport détaillé"}'
```

### ❌ WRONG - Never send file path as text:
```bash
# DON'T do this - sends just a path, not the file
mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244810777727046","content":"📄 Report: /Users/vakandi/EliaAI/docs/2026-04-08/report.md"}'
```

### Fallback - If direct upload fails, use tmpfiles.org:
```bash
# Upload to tmpfiles.org and share link
curl -X POST https://tmpfiles.org/api/v1/upload -F "file=@/path/to/file.pdf"
# Then send the returned URL in Discord message
```

**Why this matters:** File paths are useless to recipients. They need the actual file content.

---

## ⚠️ STARTUP SEQUENCE (every run, no skipping)

```bash
# 0. CRON TIMING - Load at STARTUP (REQUIRED - tells Elia when last run was)
CHECKPOINT_FILE="/Users/vakandi/EliaAI/.elia_checkpoint.json"

if [[ -f "$CHECKPOINT_FILE" ]]; then
    source /dev/stdin <<< "$(jq -r 'to_entries | .[] | tostring | "export \(.key)=\"\(.value)\""' "$CHECKPOINT_FILE" 2>/dev/null)"
    echo "📅 CRON TIMING LOADED:"
    echo "   - Dernier run: $last_run"
    echo "   - Prochain run: $next_run"
else
    echo "📅 CRON TIMING: First run - no checkpoint found"
fi
```

```bash
# 1. Load mcp-cli skill (REQUIRED before any mcp-cli commands)
skill(name="mcp-cli")

# 2. Load tools
read /Users/vakandi/EliaAI/context/TOOLS.md

# 3. Load memory
read /Users/vakandi/EliaAI/memory/MEMORY.md
read /Users/vakandi/EliaAI/memory/GLOBAL-*-WAEL-BOUSFIRA.md
read /Users/vakandi/EliaAI/memory/MEMORY-TOOLS-AND-AUTOMATION-WORKFLOWS.md

# 4. Check Google Calendar & Tasks (URGENT reminders)
gws-workspace list-events
gws-workspace list-tasks

# 5. Verify MCP is live (use bash tool)
bash: mcp-cli call telegram get_default_group_messages '{"limit":3}'
bash: mcp-cli call discord-server-mcp discord_execute '{"operation":"guild.get","params":{}}'

# 6. Run IDE Work Extraction (ALWAYS - track all work done)
bash: /Users/vakandi/EliaAI/tools/get_ide_work.sh
```

---

## Phase 1: Data Collection (ALL SOURCES)

### 1A. Read ALL messages since last run

```bash
# WhatsApp — all business groups
mcp-cli call whatsapp list_chats '{}'
# Then for each relevant group:
mcp-cli call whatsapp list_messages '{"chat_jid":"GROUP_JID","limit":30}'
# Groups: COBOU PowerRangers, B2LUXE BUSINESS, MAYAVANTA, personal contacts

# Telegram
mcp-cli call telegram get_default_group_messages '{"limit":30}'

# Discord DMs
mcp-cli call discord-mcp discord_get_dms '{"limit":20}'
```

### Discord Server - INBOX CHECK

```bash
# Get server structure
mcp-cli call discord-server-mcp discord_execute '{"operation":"channels.list","params":{}}'

# Read messages from last 12 hours (DEFAULT - use this for inbox check)
mcp-cli call discord-server-mcp discord_execute '{"operation":"messages.list_range","params":{"channel_id":"1489244810777727046","hours":12,"limit":50}}'

# Read messages from key channels (last 12h default):
# #reports: 1489244810777727046
# #urgent: 1489244806310793216
# #activity-logs: 1489244812107317402
# #health-checks: 1489247935807099020
# #projects (CoBou): 1489244906013593642
# #orders (B2L): 1489244862871244950
```

### Check emails (ProtonMail + IONOS)

Use agent-browser to open ProtonMail/IONOS. Read inbox. Flag:
- Unanswered emails from clients/partners
- Payment notifications
- Anything from: Marco, Thomas, Rida, Ali, or any active lead

---

## Phase 2: Business Pulse

Run these every cycle. Act on any anomaly.

### Bene2Luxe
- Check orders, stock alerts, customer messages
- → If action needed: do it or create ticket

### ZovaBoost
- Open tickets, overdue payments
- → Reply to tickets if non-sensitive

### MayaVanta (Marco's project)
- New bookings, messages in MAYAVANTA WhatsApp group
- → Coordinate with Marco

### AccForge
- Any new signups, API errors, payment events?
- → Note issues, create tickets

---

## Phase 3: Analysis & Task Generation

- Analyze work progress and advancements
- Identify completed vs. pending tasks
- Categorize by business (Bene2luxe, CoBou, MAYAVANTA, etc.)
- Generate tasks for Wael, Rida, Thomas, Ali
- Prioritize all tasks (most to least important)

### Google Workspace Sync (CRITICAL - MUST RUN)

**AFTER gathering ALL data from Phase 1, you MUST sync with Google Workspace:**

```bash
# 1. First, list current calendar and tasks to see what exists
python3 /Users/vakandi/EliaAI/tools/google_workspace.py list-events
python3 /Users/vakandi/EliaAI/tools/google_workspace.py list-tasks
```

**THEN, based on new information gathered from:**
- WhatsApp messages
- Telegram messages  
- Discord channels
- Emails (ProtonMail + IONOS)
- OpenCode session history

**UPDATE Google Calendar and Tasks:**

```bash
# 2A. Create NEW tasks for important items found in data gathering
python3 /Users/vakandi/EliaAI/tools/google_workspace.py create-task \
  "[Task Title]" \
  "Details about what needs to be done"

# 2B. Create calendar events with reminders for time-sensitive tasks
python3 /Users/vakandi/EliaAI/tools/google_workspace.py create-event \
  "HIGH PRIORITY: [Task]" \
  "Context: where it came from" \
  "2026-04-15T14:00:00" \
  "2026-04-15T15:00:00" \
  "5,15,30,60"  # Reminders at 5, 15, 30, 60 min before
```

**Rule: If it's urgent → calendar event with reminders. If it's todo → Google Task.**

### Add Important Tasks to Google Calendar with Reminders

**CRITICAL**: For all important tasks, create calendar events with reminders so they push to your phone.

```bash
# Use google_workspace.py to create events with reminders
# Reminders: 5,15,30,60,1440 = 5min, 15min, 30min, 1hour, 1day before
# Format: create-event "summary" "description" "start_iso" "end_iso" "reminders"

# Example - Create task with multiple reminders:
python3 /Users/vakandi/EliaAI/tools/google_workspace.py create-event \
  "HIGH PRIORITY: Complete X" \
  "Task details and context" \
  "2026-04-11T14:00:00" \
  "2026-04-11T15:00:00" \
  "5,15,30,60"

# For all-day tasks or non-meeting work items, create calendar blocks:
python3 /Users/vakandi/EliaAI/tools/google_workspace.py create-event \
  "Focus Time: [Task Name]" \
  "What to accomplish" \
  "2026-04-11T10:00:00" \
  "2026-04-11T12:00:00" \
  "15,60"
```

**Reminder Schedule**:
- **Urgent (today)**: [5, 15, 30, 60] - push notifications at 5, 15, 30, 60 min before
- **Important (this week)**: [60, 1440] - 1 hour and 1 day before
- **Follow-up meetings**: [5, 15, 30, 60, 1440] - all reminders including 1 day before

**Auto-create from Google Tasks**: Convert high-priority Google Tasks to calendar events with reminders.

---

## Phase 4: Message Creation & Sending

### Message Sending (CRITICAL - Split by channel):

**Full Morning Report → Split into multiple Discord channels:**
- Server health → #health-checks
- Orders/sales → #orders / #products
- Projects → #projects
- Analytics → #analytics
- Brief summary → #reports

**Also send to WhatsApp:**
- COBOU PowerRangers (always)
- B2LUXE BUSINESS (if bene2luxe tasks)
- MAYAVANTA (if MAYAVANTA tasks)

**Discord Report Command:**
```bash
mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"CHANNEL_ID","content":"Your message"}'
```

---

## Important Notes

**Business Context**:
- **ALWAYS READ**: `/Users/vakandi/EliaAI/memory/*`
- **READ BUSINESS-SPECIFIC FILES** based on detected businesses
- Do not invent facts about people, businesses, or agreements

**Team Members**:
- **Wael**: Owner, management, logistics, development, ads, banking
- **Rida**: CoBou Agency co-founder, social media, WhatsApp, client acquisition
- **Thomas Cogné**: CoBou Agency co-founder, technical, logistics, deals, SnapchatArmy
- **Ali**: Bene2luxe key associate, stocks, customer relations, product sourcing
- **Anass**: OGBoujee, client acquisition US/UK, frontend

**Business Relationships**:
- **MAYAVANTA**: CoBou agency's partner - treat all MAYAVANTA tasks as CoBou agency business
- **Bene2luxe**: Clothing business, Ali is key associate
- **AccForge**: CoBou agency client project

**Error Handling**:
- If mcp-cli or MCP servers are unavailable, note it in the report
- Always complete the routine even if some data sources fail

---

## Expected Output

**Success Criteria**:
- Morning report generated with all tasks prioritized
- Messages sent to appropriate Discord channels (split by category)
- Messages sent to WhatsApp groups
- All team members have their task lists

**Report Quality**:
- Tasks are clear and actionable
- Priorities are accurate
- Context is provided where needed
- All small tasks are included

---

## Checkpoint: Save State Before Exit

Before completion, save checkpoint:
```bash
CHECKPOINT_FILE="/Users/vakandi/EliaAI/.elia_checkpoint.json"
NEXT=$(date -u -d "+30 minutes" "+%Y-%m-%dT%H:%M:%SZ")
NOW=$(date -u "+%Y-%m-%dT%H:%M:%SZ")
echo "{\"last_run\":\"$NOW\",\"next_run\":\"$NEXT\"}" > "$CHECKPOINT_FILE"
```

**Critical**: Always save checkpoint before exiting, even on error.

**End of Morning Routine Instructions**
