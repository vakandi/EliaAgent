# Subworkers System — Autonomous Background AI Agents

> **Subworkers are your 24/7 AI workforce.** Autonomous agents that run on a schedule, execute tasks without supervision, and report back. Accessed via the Elia UI or command line.

---

## What Are Subworkers?

Subworkers are **self-contained AI agent prompts** that run independently on a schedule (via macOS LaunchAgents or cron). Each subworker has:

- A **personality file** (`~/.config/opencode/agents/<name>.md`) — who they are, their domain, rules
- A **PROMPT.md** (`subworkers/<name>/PROMPT.md`) — full workflow instructions
- A **trigger script** (`subworkers/scripts/trigger_<name>.sh`) — how to launch them
- A **LaunchAgent plist** (`subworkers/plists/com.elia.<name>.plist`) — schedule configuration

They run in the background and handle repetitive tasks so you don't have to.

---

## How Subworkers Work

```
┌─────────────────────────────────────────────────────┐
│                  SUBSYSTEM ARCHITECTURE              │
├─────────────────────────────────────────────────────┤
│                                                      │
│  LaunchAgent (plist)                                 │
│  └── fires on schedule (every 20min, 30min, etc.)   │
│      └── trigger_<name>.sh                           │
│          └── oh-my-opencode run -a <agent> "<task>"  │
│              └── Agent reads PROMPT.md               │
│                  └── Executes workflow               │
│                      └── Reports to Discord/WhatsApp │
│                                                      │
└─────────────────────────────────────────────────────┘
```

Each subworker:
1. **Wakes up** on schedule (plist → trigger script)
2. **Reads its PROMPT.md** for full workflow instructions
3. **Executes** its domain-specific tasks (engage, scrape, post, etc.)
4. **Reports** results to Discord, WhatsApp, or other channels
5. **Goes back to sleep** until next run

---

## Accessing Subworkers via Elia UI

The Elia Electron UI (`ui_electron/`) has a built-in **Subworker Manager**:

1. Click the **AGENTS** toggle in the control bar
2. A popup shows all registered subworkers with:
   - **Name & description** — what each agent does
   - **Schedule badge** — next run time
   - **Status badge** — ● RUNNING / ○ STOPPED
   - **Toggle switch** — enable/disable individual agents
   - **Logs button** — view per-run logs in terminal
   - **Runs dropdown** — browse historical run logs, click to open
3. Enable/disable subworkers in real-time — no terminal needed

The UI fetches subworker data from the `subworkers/` directory structure at runtime.

---

## Creating a New Subworker

Use the **`elia-subworker-creator`** skill to scaffold a complete subworker:

```
Load skill: skill(name="elia-subworker-creator")
```

This skill handles the **full pipeline**:

| Step | What it creates | Location |
|------|----------------|----------|
| 1 | Agent personality | `~/.config/opencode/agents/<name>.md` |
| 2 | Agent registration | `opencode.json` → `"agent"` section |
| 3 | Agent config | `oh-my-openagent.json` → `"agents"` + `"categories"` |
| 4 | PROMPT.md | `subworkers/<name>/PROMPT.md` |
| 5 | Trigger script | `subworkers/scripts/trigger_<name>.sh` |
| 6 | LaunchAgent plist | `subworkers/plists/com.elia.<name>.plist` |
| 7 | System doc update | `SUBWORKERS_SYSTEM.md` updated |

**Location of the skill:** `../skills/elia-subworker-creator/SKILL.md`

### Quick start:

```bash
# 1. Load the skill
skill(name="elia-subworker-creator")

# 2. Follow the interactive pipeline
# The skill will prompt for:
# - Agent name (e.g., "my-promoter")
# - Role description
# - Schedule interval
# - Work hours
# - Domain/platforms
```

---

## Directory Structure

```
subworkers/
├── SUBWORKERS_SYSTEM.md        # This file — system documentation
├── SETUP_TOOLS.md              # Tools installation guide
├── plists/                     # LaunchAgent templates
│   └── com.elia.<name>.plist   # Schedule config per subworker
├── scripts/                    # Trigger scripts
│   └── trigger_<name>.sh       # How to launch each subworker
└── logs/                       # Per-subworker run logs (gitignored)
    └── <name>.log
```

Each subworker lives in its own directory:

```
subworkers/<name>/
├── PROMPT.md                   # Main agent prompt — full workflow
└── personality.md              # Agent personality file
```

---

## Registration Requirements

Every subworker **must** be registered in two config files:

| # | What | Where | Why |
|---|------|-------|-----|
| 1 | `"mode": "primary"` | `opencode.json` → `"agent"` section | Makes agent visible in `/agents` list |
| 2 | `"mode": "primary"` | `oh-my-openagent.json` → `"agents"` section | Makes agent callable via CLI |
| 3 | Add to `"categories"` | `oh-my-openagent.json` → `"categories"` | Adds `prompt_append` with pointer to PROMPT.md |
| 4 | Add display name | `oh-my-openagent.json` → `"agent_display_names"` | Shows readable name in UI |

> ⚠️ **Failure to register in both files = agent invisible/invokable.**

After registration, restart OpenCode for changes to take effect.

---

## LaunchAgent Scheduling

Subworkers use macOS LaunchAgents for scheduling:

```xml
<!-- com.elia.<name>.plist template -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.elia.<name></string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/EliaAI/subworkers/scripts/trigger_<name>.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <!-- Every 30 min from 09:00 to 21:00 -->
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>30</integer></dict>
        ...
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/path/to/EliaAI/subworkers/logs/<name>.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/EliaAI/subworkers/logs/<name>.log</string>
</dict>
</plist>
```

Load/unload:
```bash
launchctl load subworkers/plists/com.elia.<name>.plist
launchctl unload subworkers/plists/com.elia.<name>.plist
```

---

## Trigger Scripts — The Backbone

The trigger bash script (`subworkers/scripts/trigger_<name>.sh`) is the **execution engine** of every subworker. It's the entry point called by macOS LaunchAgent, cron, systemd, Docker, or any other scheduler.

### Why Bash Scripts?

| Feature | Why It Matters |
|---------|---------------|
| **Zero dependencies** | Bash runs on EVERY Unix system (macOS, Linux, WSL). No Python, Node, or Docker needed to launch. |
| **Portable** | Same script works on macOS LaunchAgents, Linux systemd timers, Docker containers, CI/CD pipelines. |
| **Self-contained** | All logic in one file. Copy it anywhere and it works. |
| **Easy to integrate** | Any app can call it: `trigger_myagent.sh` → returns exit code 0 (success) or 1+ (error). |
| **Debug-friendly** | `set -euo pipefail` catches errors immediately. Per-run log files for forensic analysis. |
| **Guardable** | Enable/disable flags, `.enabled` file checks, schedule validation — all in shell. |

### Architecture

```
Any Trigger Source                    Trigger Script                     AI Agent
─────────────────                    ──────────────                     ────────
                                                                         
 LaunchAgent  ──┐                                                      
 cron          ──┤                                                      
 systemd       ──┤──→  trigger_<name>.sh  ──→  oh-my-opencode run  ──→  Agent
 Docker CMD    ──┤         │                                              │
 CI/CD hook    ──┘         │                                              │
                           ├── Checks .enabled flag                      │
                           ├── Reads PROMPT.md                           │
                           ├── Creates per-run log                       │
                           └── Reports exit code                         │
                                                                         │
                                                                         ▼
                                                                     PROMPT.md
                                                                     Workflow
```

### Production-Grade Trigger Script

This is the **real pattern** used in production — inspired by `trigger_yourapp_seo.sh`:

```bash
#!/bin/zsh
set -euo pipefail

# ── Configuration ──────────────────────────────────────────
AGENT_DIR="/path/to/EliaAI"
LOG_DIR="$AGENT_DIR/subworkers/logs"
AGENT_NAME="my_agent"                       # OpenCode agent name (no spaces)
AGGREGATE_LOG="$LOG_DIR/${AGENT_NAME}.log"  # One combined log
RUNS_DIR="$LOG_DIR/runs/${AGENT_NAME}"      # Per-run logs for UI
mkdir -p "$RUNS_DIR"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
RUN_LOG="$RUNS_DIR/${TIMESTAMP}.log"

# ── Log helper (writes to BOTH aggregate + per-run) ───────
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$AGGREGATE_LOG" >> "$RUN_LOG"
}

# ── Config files ───────────────────────────────────────────
ENABLED_FLAG="$AGENT_DIR/subworkers/$AGENT_NAME/.enabled"
PROMPT_FILE="$AGENT_DIR/subworkers/$AGENT_NAME/PROMPT.md"
PERSONALITY_FILE="$HOME/.config/opencode/agents/$AGENT_NAME.md"

log "Starting $AGENT_NAME trigger..."

# ── Guard: enabled check ──────────────────────────────────
if [[ ! -f "$ENABLED_FLAG" ]]; then
    log "$AGENT_NAME skipped (.enabled not found). Create .enabled to activate."
    exit 0    # Not an error — just disabled
fi

# ── Guard: PROMPT.md must exist ───────────────────────────
if [[ ! -f "$PROMPT_FILE" ]]; then
    log "ERROR: PROMPT.md not found at $PROMPT_FILE"
    exit 1
fi

# ── Load prompts ───────────────────────────────────────────
PROMPT=$(cat "$PROMPT_FILE")
PERSONALITY=$(cat "$PERSONALITY_FILE" 2>/dev/null || echo "No personality file")

# ── Execute agent ──────────────────────────────────────────
cd "$AGENT_DIR"

oh-my-opencode run -a "$AGENT_NAME" "Execute ONE run now:

1. Lis ta personnalité (ci-dessous) et le PROMPT.md complet
2. Exécute ton workflow standard
3. Rapporte les résultats

PERSONNALITÉ:
$PERSONALITY

PROMPT:
$PROMPT" >> "$RUN_LOG" 2>&1

log "$AGENT_NAME completed"
```

### Key Features of This Pattern

| Feature | Implementation | Benefit |
|---------|---------------|---------|
| **Per-run logs** | `$RUNS_DIR/$TIMESTAMP.log` | UI can show individual runs, click to open any specific run log |
| **Aggregate log** | `$AGGREGATE_LOG` | Quick `tail -f` to see latest activity across all runs |
| **Enable/disable** | `.enabled` flag file | UI toggles this file. No plist reload needed. |
| **Error isolation** | `set -euo pipefail` | Script fails fast on any error, never silently continues |
| **Personality injection** | `$PERSONALITY` in prompt | Agent gets its full identity context every run |
| **Exit codes** | 0=ok, 1=error | Scheduler (cron/launchd/systemd) can react to failures |

### Integration Examples

The beauty of a bash trigger script: **any app can call it**.

```bash
# ── macOS LaunchAgent (plist calls it directly) ───────────
# ProgramArguments → /path/to/trigger_myagent.sh

# ── cron (any Unix) ──────────────────────────────────────
*/30 9-21 * * * /path/to/trigger_myagent.sh

# ── systemd timer (Linux) ────────────────────────────────
[Service]
ExecStart=/path/to/trigger_myagent.sh

# ── Docker container (as CMD or ENTRYPOINT) ──────────────
docker run -d --name myagent myimage /path/to/trigger_myagent.sh

# ── CI/CD pipeline (GitHub Actions, GitLab CI) ──────────
jobs:
  run-agent:
    steps:
      - run: ./subworkers/scripts/trigger_myagent.sh

# ── Another script (compose agents together) ─────────────
./trigger_agent_a.sh && ./trigger_agent_b.sh   # Sequential
./trigger_agent_a.sh & ./trigger_agent_b.sh &  # Parallel

# ── HTTP webhook (via any app) ───────────────────────────
curl -X POST http://localhost:9090/trigger && /path/to/trigger_myagent.sh
```

### Why Per-Run Logs Matter

The per-run log directory (`logs/runs/<name>/`) serves **two purposes**:

1. **Elia UI integration** — The Subworker Manager popup reads this directory to show individual run history. Each run appears as a clickable row — click to open the log in your terminal.
2. **Forensic debugging** — Every run is timestamped and preserved. If something went wrong 3 days ago, the exact log is still there — no rotation, no overwrite.

```
subworkers/logs/
├── runs/
│   ├── yourapp_seo/
│   │   ├── 20260708_091500.log   # Run at 09:15
│   │   ├── 20260708_094500.log   # Run at 09:45
│   │   └── 20260708_101500.log   # Run at 10:15
│   └── another_agent/
│       └── 20260708_100000.log
├── yourapp_seo.log              # Aggregate (tail -f)
└── another_agent.log             # Aggregate (tail -f)
```

### Pattern Summary

```
┌──────────────────────────────────────────────┐
│            TRIGGER SCRIPT PATTERN             │
├──────────────────────────────────────────────┤
│                                               │
│  1. set -euo pipefail       # Safety          │
│  2. mkdir -p runs/          # Per-run logs    │
│  3. Check .enabled flag     # Guard           │
│  4. Read PROMPT.md          # Load context    │
│  5. oh-my-opencode run      # Execute agent   │
│  6. Log completion          # Done            │
│                                               │
│  Exit: 0 = ok, 1 = error                     │
│  Integrates with: launchd, cron, systemd,     │
│  Docker, CI/CD, HTTP hooks, other scripts     │
└──────────────────────────────────────────────┘
```

---

## Reporting

Subworkers typically report to Discord channels, WhatsApp groups, or other messaging platforms. Each subworker defines its own reporting format in its PROMPT.md.

Standard report structure:
```
# <Agent Name> Report - {DATE}

## Summary
- Actions taken: {N}
- Leads/opportunities: {N}
- Responses received: {N}

## Details
[Platform-by-platform breakdown]

## Next Run
[What will be prioritized]
```

---

## Tools Installation

See `SETUP_TOOLS.md` in this directory for the complete tools setup guide (MCP servers, Python libraries, browser automation).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Subworker not running | Plist not loaded | `launchctl load plists/com.elia.<name>.plist` |
| Subworker not in UI | Not registered in config | Add to `opencode.json` + `oh-my-openagent.json` |
| "Agent not found" on run | Name mismatch | Check agent name matches exactly in both configs |
| No logs | Log path wrong | Check `StandardOutPath` in plist |
| Schedule wrong | Plist times incorrect | Edit `StartCalendarInterval` in plist |
