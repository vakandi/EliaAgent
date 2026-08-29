# Subworkers System

**Date:** 29 August 2026  
**Version:** 4.1 — TZ + persistence + manual Continue

> Technical documentation for the autonomous subworker agent system.
>
> **Current runtime**: Fully dockerized — Python FastAPI (5656) + OpenCode serve (5655) **in the same container** `elia-subworker-srv`. No host `opencode` process. Timezone synced via `TZ=Africa/Casablanca` (host `+01` = container `+01`; `docker exec date` matches `date` on macOS).
> **Purpose**: **Save CPU/RAM** (one Colima VM instead of 14 host agents), **security isolation** (agents blocked to `workspace/` via container filesystem + `opencode.json` permissions), **full control** (one `docker compose` owns the whole stack).
> **Previous version**: `SUBWORKERS_SYSTEM_OLD.md` (v3.0 — Node.js trigger + launchd plists, host `opencode` on 4096).

---

## Table of Contents

1. [Overview](#1-overview)
2. [Directory Structure](#2-directory-structure)
3. [Workspace Isolation & Per-Agent Permissions](#3-workspace-isolation--per-agent-permissions)
4. [OpenCode Agent Registration](#4-opencode-agent-registration)
5. [Trigger Template](#5-trigger-template)
6. [Tools & MCP Servers](#6-tools--mcp-servers)
7. [LaunchAgent Setup](#7-launchagent-setup-legacy)
8. [Subworker Server (Docker + FastAPI)](#8-subworker-server-docker--fastapi)
9. [ColimaBar (Menu Bar Control)](#9-colimabar-menu-bar-control)

---

## 1. Overview

### What Are Subworkers?

Subworkers are autonomous AI agents that run on a schedule or trigger. Each subworker has:
- A **personality file** (`~/.config/opencode/agents/<agent-id>.md`) — loaded by the **container's** OpenCode server (`127.0.0.1:5655` inside `elia-subworker-srv`) via the session's `agent` field
- A **PROMPT.md** with task-specific instructions — injected by the runner as the message content
- A **workspace folder** for isolated file I/O (bind-mounted `/data/subworkers/...` → host `~/EliaAI/subworkers/...`)
- A **JSON schedule entry** in `server/app/config/subworkers.json` — defines schedule, enabled state, retries, timeout
- A **runner** — the Docker FastAPI server (SubworkerRunner) drives runs over the **container-local OpenCode HTTP API** (`POST /session` + `/message` on `127.0.0.1:5655`). No host CLI, no `host.docker.internal`.

> **Scheduling moved from launchd → APScheduler (Docker server).** LaunchAgent plists are legacy (see §7). Control is now via the REST API / WebSocket / ColimaBar (see §8, §9).

### Architecture

```
EliaUI.command (launcher — 2 tmux sessions, opencode now dockerized)
  ├── subworker-srv    (Docker container elia-subworker-srv, ports 5656 FastAPI + 5655 opencode)
  │     ├── opencode serve — 127.0.0.1:5655 (inside container, fully dockerized)
  │     └── uvicorn FastAPI — 0.0.0.0:5656
  └── elia-ui          (Discord bot + Electron UI)

Docker container (bridged, port-mapped 5656→host; opencode on 5655 internal)
  └─ APScheduler (from subworkers.json)
       └─ SubworkerRunner ──HTTP──► localhost OpenCode server :5655 (same container)
             ├── create_session(directory=/tmp/{name}, agent=<agent-id>)  # lightweight CWD for perf (89M workspace fix)
             │     └── container opencode loads personality from /root/.config/opencode/agents/<agent-id>.md
             │         + oh-my-openagent plugins from /root/.config/opencode
             │         + agent workspace still at /data/subworkers/{name}/workspace (bind-mounted, accessed via absolute path per PROMPT.md)
             └── send_message(prompt) → waits for completion  # pwd=/tmp/{name} is expected, not a bug

Manual/legacy (optional): trigger_template.js --agent <name>
  └─ spawns oh-my-opencode run -d workspace/ -a <agent> "<task>" (v3 path, kept for rollback)
```

### Control & Monitoring

- **ColimaBar** (menu bar app, source `~/Documents/EliaTopBar`) — Trigger Now, Enable/Disable, View Logs, live status via WebSocket + HTTP polling.
- **REST API** — `http://localhost:5656` (`/status`, `/trigger/{name}`, `/enable/{name}`, `/disable/{name}`, `/logs/{name}`, `/server/health`, WS `/ws`).
- Full API contract + failure modes: [`docs/SUBWORKERS_COLIMABAR_CONNECTION.md`](../docs/SUBWORKERS_COLIMABAR_CONNECTION.md).

---

## 2. Directory Structure

```
EliaAI/subworkers/
├── SUBWORKERS_SYSTEM.md          # This file
├── SUBWORKERS_SYSTEM_OLD.md      # Previous version (v3.0 — launchd/Node.js era)
├── server/                       # ★ PRIMARY RUNTIME (Docker FastAPI server)
│   ├── Dockerfile                # python:3.12-slim + Node 20 + TZ=Africa/Casablanca
│   ├── docker-compose.yml        # container elia-subworker-srv, ports 5656→host, 5655 internal, TZ + opencode-data volume
│   ├── opencode-data/            # ← container's opencode DB (2.8M, bind-mounted, persists across docker rm)
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py               # FastAPI app, /health endpoint
│   │   ├── config/
│   │   │   ├── server.json       # port 5656, opencode URL 5655, alert settings
│   │   │   └── subworkers.json   # ★ ALL subworker definitions + schedules (14)
│   │   ├── routes/               # subworkers.py (incl. POST /sessions/{name}/{id}/continue), server.py, websocket.py
│   │   ├── services/             # scheduler, runner, session_monitor, health_manager, error_parser, alert_manager
│   │   └── utils/                # opencode_client.py, exceptions.py
│   └── tests/                    # pytest suite
├── scripts/
│   └── trigger_template.js       # LEGACY/manual trigger (Node.js, no per-agent wrappers needed)
├── logs/
│   ├── <agent_name>.log          # Aggregate logs
│   └── runs/
│       └── <agent_name>/         # Per-run logs
├── plists/                       # LEGACY — launchd plists (superseded by server scheduler)
└── <agent-id>/
    ├── PROMPT.md                 # Task-specific instructions
    ├── .enabled                  # Gate file — presence = active (legacy manual runs)
    ├── .loop_mode                # (Optional) Server-attach loop mode
    └── workspace/                # Runtime directory (auto-created)
        ├── opencode.json         # (Optional) Per-agent tool permissions
        └── docs/                 # Daily work folders (auto-created)
            ├── 2026-04-01/
            ├── 2026-04-02/
            └── ...               # idempotent — mkdir -p once per day
```

### Creating a New Subworker

1. Create `subworkers/<agent-id>/PROMPT.md` + workspace (see §5.4)
2. Add an entry to `server/app/config/subworkers.json` — `name`, `enabled: true`, `schedule` (`interval` hours+minute, or `cron`), `agent_id`, `max_retries`, `timeout_minutes`
3. The server hot-reloads `subworkers.json` — no restart needed for config-only changes
4. Manual terminal run (bypasses server): `node scripts/trigger_template.js --agent <agent-id> --force`

---

## 3. Workspace Isolation & Per-Agent Permissions

### 3.1 Why Workspace Isolation

Every subworker agent runs in its own `workspace/` folder:

1. **Isolates file I/O** — agents only write inside their workspace, never outside. The `opencode.json` local config blocks access to all other folders on the system.
2. **Enables per-agent permissions** — place an `opencode.json` in the workspace folder to restrict tools per agent (OpenCode loads local config over global)
3. **Prevents cross-contamination** — log files, state, and generated content stay in one place
4. **Daily folders** — the trigger creates `workspace/YYYY-MM-DD/` every run. `mkdir -p` is idempotent: 50 runs on the same day = 1 folder. Agents can see all previous days' work.

### 3.2 How It Works

The trigger template (`trigger_template.js`) automatically:

1. Creates `workspace/` on every run (`mkdir -p "$WORKSPACE_DIR"`)
2. Creates `workspace/YYYY-MM-DD/` every run (idempotent — only one folder per day regardless of run count)
3. Passes `-d "$WORKSPACE_DIR"` (a.k.a. `--directory`) to `oh-my-opencode run`
4. OpenCode loads `workspace/opencode.json` (if present) as the local config, **overriding** the global `~/.config/opencode/opencode.json`
5. The agent sees only the tools/skills/MCPs defined in its local config

The `-d` flag works with both `--attach` (loop mode) and direct (task mode).

### 3.3 Per-Agent `opencode.json` Template

The `opencode.json` in the workspace folder MUST block access to ALL folders on the system except the agent's own workspace. The agent keeps full access to all MCP servers but cannot read/write outside its `workspace/` directory.

Create `subworkers/<agent-id>/workspace/opencode.json`:

```json
{
  "agent": {
    "<agent-id>": {
      "description": "Description of this agent",
      "mode": "primary"
    }
  },
  "tools": {
    "enabled": ["discord-server-mcp", "whatsapp-mcp", "telegram", "gmail"]
  },
  "permissions": {
    "read": {
      "allow": ["~/EliaAI/subworkers/<agent-id>/workspace/**"],
      "deny": ["**"]
    },
    "write": {
      "allow": ["~/EliaAI/subworkers/<agent-id>/workspace/**"],
      "deny": ["**"]
    },
    "execute": {
      "deny": ["**"]
    }
  },
  "mcpServers": {
    "discord-server-mcp": { ... },
    "whatsapp-mcp": { ... }
  }
}
```

- **`permissions.read/write.deny: ["**"]`** — blocks all paths by default
- **`permissions.read/write.allow`** — only the agent's own workspace is readable/writable
- **`mcpServers`** — the agent still has full MCP access for API calls, reporting, etc.
- **`permissions.execute.deny: ["**"]`** — prevents arbitrary command execution

If no `workspace/opencode.json` exists, the agent falls back to the global config (no restrictions).

### 3.4 PROMPT.md Workspace Constraint

Every subworker's PROMPT.md **MUST** include these instructions:

```
## Workspace Constraint
You MUST only read and write files inside your `workspace/` folder:
`~/EliaAI/subworkers/<agent-id>/workspace/`
Never write files outside this folder. All system paths outside workspace/ are blocked.

## Daily Folders
Each run creates a daily folder directly in workspace: `workspace/YYYY-MM-DD/`.
Write your work logs, research, and outputs into today's folder.
The folder is idempotent — only one per day regardless of how many times the trigger runs.
You can read all previous days' folders to understand context and history.

## Mempalace
To orient yourself on every run:
1. Check `workspace/` for the latest day folder to read today's work-in-progress
2. Scan previous days' docs for relevant context: decisions made, blockers, next steps
3. If you need to revisit something from days ago, navigate by date: `workspace/2026-04-01/`
4. Write a summary of what you did today into the current day's folder before finishing

## Completion Marker (MANDATORY)
When you build your todo list at the start of this run, ALWAYS include this final task:
"Output <promise>DONE</promise> to signal successful completion".
Only output `<promise>DONE</promise>` as the very last line of your final message, after ALL
tasks are done and verified. Never output it early. Never omit it — the subworker server
uses this marker to detect that the run succeeded.
```

> ⚠️ **The `<promise>DONE</promise>` marker is part of completion detection** (§8.5): the runner
> polls the session status until idle, then checks the final assistant message for the marker.
> A run without it may be classified as incomplete/failed even if the work was done — hence
> every PROMPT.md must instruct the agent to plan it as a todo item and emit it last.
```

---

## 4. OpenCode Agent Registration

### 4.1 File: `~/.config/opencode/agents/<agent-id>.md` (Personality File)

The personality file **MUST** contain YAML frontmatter before the markdown content. Without frontmatter, the agent will not appear in the `/agents` menu and cannot be `@mentioned` in opencode.

```yaml
---
name: <agent-id>
slug: <agent-id>
description: Short description of what this agent does
mode: all             # "all" = visible in agent selector + delegatable via @mention
model: opencode/big-pickle
temperature: 0.3
tools:
  read: true
  write: true
  edit: true
  bash: true
  glob: true
  grep: true
  webfetch: true
  task: true
  websearch: true
permissions:
  bash:
    "ls*": allow
    "cat*": allow
    "echo*": allow
    "curl*": allow
    "*": ask
  edit:
    "*.md": allow
    "*": ask
---
```

**Key rules:**
- **`mode: all`** — This is the single most important field. `"all"` registers the agent in BOTH the TUI agent selector (`primary` mode) AND the delegation system (`subagent` mode). Using `"primary"` alone hides it from `@mention` in chat; `"subagent"` alone hides it from the agent switcher.
- **`mode: all`** is what makes the agent appear everywhere: `/agents` menu, agent switcher, `@mention`, and `opencode run --agent`.
- **`permissions`** — Restrict bash commands and file edits appropriately for the agent's role. Marketing agents don't need `"git commit*": allow`, code agents don't need `"curl*": allow`.
- **`tools`** — Set to `true` for all tools the agent may need. At minimum: `read`, `write`, `edit`, `bash`, `grep`, `glob`.

### 4.2 File: `~/.config/opencode/opencode.json`

Add to the `"agent"` section:

```json
"<agent-id>": {
  "description": "What this agent does",
  "mode": "primary",
  "color": "#hexcolor",
  "model": "opencode/big-pickle",
  "prompt_append": "**FIRST: Read ~/.config/opencode/agents/<agent-id>.md for your full personality and workflow.**\n\n**THEN: Read subworkers/<agent-id>/PROMPT.md for your complete task instructions.**\n\nYou are <agent-id> - Description here. Execute your assigned task."
}
```

> ⚠️ **prompt_append MUST always tell the agent to read its own personality file.** oh-my-opencode loads personality via `-a`, but the prompt_append reinforces it. The trigger injects PROMPT.md, but the prompt_append should also reference it.

Note: `"mode": "primary"` here is fine even when the frontmatter uses `"mode": "all"`. The frontmatter `mode` controls the opencode TUI behavior; the `opencode.json` mode is used for configuration loading.

### 4.3 File: `~/.config/opencode/oh-my-openagent.json`

#### Add to `"agents"`:

```json
"<agent-id>": {
  "model": "opencode/big-pickle",
  "mode": "primary",
  "variant": "max",
  "fallback_models": []
}
```

#### Add to `"categories"`:

```json
"<agent-id>": {
  "model": "opencode/big-pickle",
  "description": "Short description",
  "prompt_append": "**FIRST: Read ~/.config/opencode/agents/<agent-id>.md for your full personality and workflow.**\n\nYou are <agent-id>. Execute your assigned task. Always respect your workspace constraint."
}
```

> ⚠️ **Same rule: prompt_append MUST always tell the agent to read its own personality file.** The trigger injects PROMPT.md automatically, but personality should be referenced in prompt_append.

#### Add to `"agent_display_names"`:

```json
"<agent-id>": "Readable Name"
```

### 4.4 Mandatory Registration Pattern

Every new subworker **MUST** complete ALL of these steps. Missing any one step = agent invisible or unusable:

| # | What | Where | Why |
|---|------|-------|-----|
| 1 | YAML frontmatter with `mode: all` | `~/.config/opencode/agents/<agent-id>.md` | Agent appears in agent switcher, `/agents` menu, AND `@mention` in chat. Without this, agent won't surface anywhere. |
| 2 | `"mode": "primary"` | `opencode.json` → `"agent"` section | Makes agent visible in `/agents` list and loads configuration |
| 3 | `"mode": "primary"` | `oh-my-openagent.json` → `"agents"` section | Makes agent callable via `oh-my-opencode run -a <agent>` |
| 4 | Add to `"categories"` | `oh-my-openagent.json` → `"categories"` | Adds `prompt_append` with personality reference + identity context |
| 5 | Add display name | `oh-my-openagent.json` → `"agent_display_names"` | Shows readable name in `/agents` menu |

> ⚠️ **Frontmatter with `mode: all` is the critical piece. Without it, registering in JSON configs alone is not enough — the agent will be invisible in the opencode TUI and unmentionalble.**

### 4.5 Verify Registration

After registering, confirm the agent shows up correctly:

```bash
# Check agent appears in the list
opencode agent list 2>&1 | grep "<agent-id>"

# Expected output: <agent-id> (all)
```

If it shows `(subagent)` instead of `(all)`, the frontmatter `mode: all` is missing or incorrect. If it doesn't show at all, check `opencode.json` syntax and file paths.

### 4.6 Restart OpenCode

New agents only appear after restarting opencode TUI sessions:

```bash
# Kill opencode processes
pkill -f "opencode$"

# Or restart the terminal/TUI session manually
```

Existing running opencode instances cache the agent list at startup — config changes are not hot-reloaded.

---

## 5. Trigger Template

> ⚠️ **The Docker server (§8) is the PRIMARY scheduler now.** `trigger_template.js` remains for manual terminal runs and as the launchd fallback. The server's SubworkerRunner performs the same job (PROMPT.md loading, workspace auto-creation, per-run logging) via APScheduler.

### 5.1 Template File: `scripts/trigger_template.js`

The universal trigger template (Node.js) handles all subworker launch logic. No per-agent wrapper scripts needed — the launchd plist passes `--agent <name>` directly:

```xml
<string>~/.bun/bin/node</string>
<string>~/EliaAI/subworkers/scripts/trigger_template.js</string>
<string>--agent</string>
<string>my_agent</string>
```

For manual terminal runs:
```bash
node scripts/trigger_template.js --agent my_agent --force
```

### 5.2 What the Template Handles

| Feature | Detail |
|---------|--------|
| **PATH resolution** | Finds `oh-my-opencode` for launchd (which lacks `~/.bun/bin`) |
| **`.enabled` gate** | Skips if `subworkers/<agent-id>/.enabled` doesn't exist. Use `--force` flag to bypass for manual terminal runs |
| **`--force` flag** | `--agent <name> --force` skips the `.enabled` check. Launchd never passes this flag, so scheduled runs still respect `.enabled` |
| **PROMPT.md loading** | Reads from `subworkers/<agent-id>/PROMPT.md` |
| **Personality** | Loaded automatically by oh-my-opencode from `~/.config/opencode/agents/<agent-id>.md` via `-a` flag |
| **Workspace auto-creation** | Creates `workspace/` + `workspace/YYYY-MM-DD/` (date folder at root) every run |
| **`-d` flag** | Passes `--directory workspace/` to `oh-my-opencode run` for per-agent config |
| **Mode detection** | `task` (single-shot) vs `loop` (server-attach with `/ulw-loop`) |
| **Per-run logging** | Each run logged individually + aggregate log |
| **Proxy support** | Via `.proxy_enabled` file |

### 5.3 Mode Selection

**Task mode** (default): Single-shot execution. Agent runs once and exits.

**Loop mode** (`.loop_mode` file): Agent runs in a persistent server-attached loop using `/ulw-loop` or `/ralph-loop`. Used for continuous promotion/social agents.

```bash
# Enable loop mode for an agent
touch ~/EliaAI/subworkers/<agent-id>/.loop_mode
```

### 5.4 Creating a New Subworker

1. Create `subworkers/<agent-id>/PROMPT.md`
2. Create `subworkers/<agent-id>/.enabled` to activate (or use `--force` to bypass for manual runs)
3. Register in `opencode.json` + `oh-my-openagent.json` (see §4.3)
4. Create personality file at `~/.config/opencode/agents/<agent-id>.md` with YAML frontmatter (see §4.1)
5. Add a plist entry in `plists/com.elia.<agent-id>.plist` pointing to `trigger_template.js --agent <agent_id>`

### 5.5 Exit/Completion Marker

Every run log ends with a unique marker line written by `trigger_template.js`:

```
[YYYY-MM-DD HH:MM:SS] EOF_SUBWORKER_EXIT:<code>
```

This marker is always written after `oh-my-opencode run` exits, regardless of success or failure.

**Why a unique marker instead of parsing "completed" in AI output:**
- The AI agent's stdout is redirected into the same run log file (`>> "$RUN_LOG" 2>&1`)
- The AI might output text like "All tasks completed" or "I've completed the task" — parsing for "completed" would false-match
- `EOF_SUBWORKER_EXIT:` is a string the AI can never produce: it's only written by the shell script's `log()` function after the opencode process fully exits

**How the Electron UI (subworker-popup.html) uses it:**
1. Opens the run log file and reads the last 300 bytes
2. Regex-searches for `EOF_SUBWORKER_EXIT:(\d+)`
3. If found: extracts exit code, calculates duration from start timestamp → marker timestamp
4. `exit 0` → green duration badge (success)
5. `exit non-zero` → orange "crashed" badge with duration (agent failed mid-run)
6. If marker not found: yellow "● RUNNING" badge (agent still executing or trigger script crashed before reaching the marker)

---

## 6. Tools & MCP Servers

### 6.1 Python Libraries

```bash
# Install via pip
pip install instagrapi
pip install linkedin-scraper
pip install TikTokApi

# Or use uv (faster)
uv pip install instagrapi linkedin-scraper TikTokApi
```

### 6.2 Available MCP Servers

#### Social Media

| Server | NPM/GitHub | Platforms | Capabilities |
|--------|-----------|----------|------------|
| **@mcpware/instagram-mcp** | [npm](https://www.npmjs.com/package/@mcpware/instagram-mcp) | Instagram | 23 tools |
| **facebook-marketplace-mcp** | [GitHub](https://github.com/jdcodes1/facebook-marketplace-mcp) | FB Marketplace | Browse, search |
| **x-mcp-server** | [GitHub](https://github.com/Lnxtanx/x-mcp-server) | X/Twitter | 54+ tools |
| **PostPulse** | [GitHub](https://github.com/PostPulse/mcp-server-postpulse) | Multi-platform | IG, FB, YouTube, TikTok, LinkedIn, X, Threads |
| **Outstand** | [mcphub.io](https://mcphub.io/servers/outstand) | Multi-platform | 10 platforms, 25 tools |

#### Browser Automation

| Server | NPM/GitHub | Capabilities |
|--------|-----------|------------|
| **Playwright MCP** | `@playwright/mcp` | Navigation, clicking, forms |
| **agent-browser-mcp** | [GitHub](https://github.com/quantmew/agent-browser-mcp) | Full Playwright API + 44 tools |

#### Communication (Reporting)

| Service | Command | Use |
|---------|---------|-----|
| WhatsApp | `mcp-cli call whatsapp send_message` | Emergency alerts |
| Discord | `mcp-cli call discord-server-mcp discord_send_message` | Regular reports |

### 6.3 MCP Configuration

File: `~/.config/mcp/mcp_servers.json`

```json
{
  "discord-report": {
    "command": "npx",
    "args": ["-y", "@pasympa/discord-mcp"],
    "env": {
      "DISCORD_TOKEN": "YOUR_BOT_TOKEN"
    }
  }
}
```

Restart:
```bash
pkill -f mcp && mcp-cli &
mcp-cli list
```

---

## 7. LaunchAgent Setup (LEGACY)

> ⚠️ **Superseded by the Docker server scheduler (§8).** Plists still exist under `plists/` and `trigger_template.js` still works, but the current system schedules via `subworkers.json` + APScheduler inside the container. Keep this section for rollback / manual machines.

### 7.1 Template Plist

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.elia.<agent-id></string>

    <key>ProgramArguments</key>
    <array>
        <string>~/.bun/bin/node</string>
        <string>~/EliaAI/subworkers/scripts/trigger_template.js</string>
        <string>--agent</string>
        <string><agent_id_with_underscores></string>
    </array>

    <key>RunAtLoad</key>
    <false/>

    <key>StartCalendarInterval</key>
    <array>
        <!-- Customize schedule here -->
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>~/.bun/bin:~/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>~</string>
    </dict>

    <key>WorkingDirectory</key>
    <string>~/EliaAI</string>

    <key>StandardOutPath</key>
    <string>~/EliaAI/subworkers/logs/<agent_name>.log</string>

    <key>StandardErrorPath</key>
    <string>~/EliaAI/subworkers/logs/<agent_name>.log</string>
</dict>
</plist>
```

### 7.2 Load & Verify

```bash
launchctl load ~/EliaAI/subworkers/plists/com.elia.<agent-id>.plist
launchctl list | grep "com.elia"
```

---

## 8. Subworker Server (Docker + FastAPI)

### 8.1 Overview

The **primary runtime** is a Python FastAPI server in Docker. It replaces launchd scheduling with a centralized JSON config + APScheduler.

| Aspect | Old (v3) | New (v4) |
|--------|----------|----------|
| Scheduling | 14 launchd plists | `subworkers.json` + APScheduler |
| Server | Manual start/restart | HealthManager auto-recovery |
| Task completion | EOF marker log parsing | Multi-layer API + process polling |
| Error handling | None | ErrorParser (10 types) + backoff |
| Alerts | None | macOS beep + Electron + ntfy.sh |
| Status view | 14 separate logs | REST API + WebSocket |
| Runtime | Shell + Node.js | Python FastAPI in Docker |

### 8.2 Start / Stop

Fully dockerized — no host `opencode serve` required. `entrypoint.sh` inside the container boots `opencode serve --port 5655 --hostname 127.0.0.1` before FastAPI, clears stale `models.json` cache, and healthchecks both. `TZ=Africa/Casablanca` is baked in (`Dockerfile` ENV + `docker-compose.yml` `environment`) so `docker exec date` matches host.

```bash
cd ~/EliaAI/subworkers/server && docker compose up --build   # start (builds opencode binary inside image)
docker compose down                                          # stop (container only, opencode-data persists)
docker restart elia-subworker-srv                            # quick restart — sessions survive via opencode-data volume
curl http://localhost:5656/health                            # health check → {"status":"ok",...}
curl http://localhost:5656/models -H "Authorization: Bearer $ELIA_AUTH_TOKEN" | jq .total  # 6 models, no deprecated
docker exec elia-subworker-srv date                          # should match host `date` (both +01)
docker exec elia-subworker-srv curl -sf http://127.0.0.1:5655/global/health  # opencode health inside container
lsof -i :5655 2>/dev/null || echo "host 5655 empty — opencode is inside Docker ✓"
lsof -i :4096 2>/dev/null || echo "host 4096 empty — legacy port unused ✓"
```

Container: `elia-subworker-srv`, `restart: unless-stopped`, ports **5656** (FastAPI host-exposed) + **5655** (opencode internal, not host-published). Healthcheck requires both `GET /health` (5656) and `GET /global/health` (5655). Volumes: `opencode-data` (2.8M) persists container DB, `logs` persists `scheduler_state.json`.

### 8.3 Configuration (JSON, hot-reloaded)

| File | Purpose |
|------|---------|
| `server/app/config/server.json` | Port (5656), OpenCode server URL (http://127.0.0.1:4096), health-check interval, max restarts, alert settings |
| `server/app/config/subworkers.json` | All subworker definitions: `name`, `enabled`, `schedule` (`interval` = hours+minute / `cron`), `agent_id`, `max_retries`, `timeout_minutes`, `mcp_servers`, `notify_discord` |

`subworkers.json` currently defines **14 subworkers** (refund-hunter, mirorpay-community-organic, mirrorpay-telegram, bene2luxe-promoter, bene2luxe-suppliers, cobou-promoter, mirorpay-seo, reddit-saas-scraper, teleorbit-community-organic, teleorbit-seo, tempack-dev, tiktok-content, vcam-community-organic, vcam-seo).

### 8.4 API (localhost, Bearer $ELIA_AUTH_TOKEN)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Docker healthcheck (status/timestamp/uptime/version) |
| GET | `/status` | All subworkers `{name, enabled, running, next_run, schedule_type}` |
| GET | `/status/{name}` | Detail + schedule + agent_id + model |
| PUT | `/status/{name}` | Edit config (schedule, agent_id, model, timeout, retries) |
| POST | `/trigger/{name}` | Run now (optional `{prompt, model}` body) — creates NEW session |
| POST | `/sessions/{name}/{session_id}/continue` | **Manual reinjection** — send `{"message":"continue the tasks"}` to an EXISTING session (old runs), used by EliaTopBar's **Continue** badge |
| POST | `/enable/{name}` / `/disable/{name}` | Toggle enabled state |
| POST | `/config/reload` | Hot-reload subworkers.json from disk |
| GET | `/logs/{name}?lines=N` | Recent log lines from run files |
| GET | `/sessions/{name}?limit=N` | OpenCode session messages (reasoning, tools, text) |
| GET | `/sessions/{name}/list` | Session list for LogViewer (matches by `agent==agent_id` OR `directory startswith /data/subworkers/{name}`) |
| GET/POST | `/main-agent` | Read / set the MAIN agent (`{"name": "..."}`) — persisted to `config/main-agent.json` |
| GET | `/server/health` | OpenCode server subprocess state/pid/restarts |
| POST | `/server/restart` | Restart OpenCode server subprocess |
| WS | `/ws?token=…` | Live events: `initial_status`, `pong`, `subworker_completed`, `subworker_error` (requires `?token=` or `Authorization: Bearer`) |

Interactive docs: `http://localhost:5656/docs`.

### 8.5 Run Lifecycle

1. APScheduler fires at scheduled time
2. SubworkerRunner checks OpenCode health
3. HTTP invocation: `OpenCodeClient.create_session(directory={workspace}, agent_id={agent})` + `send_message(prompt)` against the **container-local** OpenCode server (`OPENCODE_SERVER_URL`, default `http://127.0.0.1:5655`) — fully dockerized, no host process
   - ⚠️ **The workspace directory MUST be sent via the undocumented `x-opencode-directory` HTTP header.** OpenCode ignores `directory` in the `POST /session` body — without the header every session lands in the server CWD (`~/EliaAI`) instead of the agent's isolated `workspace/`.
   - Workspace resolution: main agent → `~/EliaAI` (repo root); every other subworker → `~/EliaAI/subworkers/<agent-id>/workspace/` (mapped from `/data/...` inside the container via `OPENCODE_WORKSPACE`)
4. SessionMonitor polls OpenCode API every 2s
5. Completion detection: process exit code → API status + idle timeout → message markers
6. On failure: retry with exponential backoff; on session crash: resume with `--continue`
7. Real-time updates broadcast via WebSocket; logs → `logs/runs/{name}/YYYYMMDD_HHMMSS.log`

> **Fully dockerized — no host `opencode` process.** The container's `entrypoint.sh` boots `opencode serve --port 5655` **inside the same container** before FastAPI, so `OPENCODE_SERVER_URL` is `http://127.0.0.1:5655` (container-local). `oh-my-openagent` plugins, `~/.config/opencode/`, and `~/.config/omo/` are bind-mounted read-only into the container and loaded by the container's opencode at startup. Host `opencode` is not used and should not be running on 4096/5655.

### 8.6 Tests & Dev

```bash
cd ~/EliaAI/subworkers/server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5656   # local dev
pytest -v                                    # test suite (routes, scheduler, runner, health, error_parser, ...)
```

### 8.7 Session Persistence (survives `docker restart` + `nuke_docker.sh` — verified 29/08)

Container opencode DB (`/root/.local/share/opencode/opencode.db` inside `elia-subworker-srv`, 2.8M) is **bind-mounted** to host `~/EliaAI/subworkers/server/opencode-data/opencode.db` — separate file from host TUI DB (`~/.local/share/opencode/opencode.db` 300M, 40k sessions), no concurrent corruption. Run logs live in bind-mounted `logs/` volume. Both survive `docker restart`, `docker rm`, `colima stop`, and `nuke_docker.sh`.

| Failure point | Cause | Fix (verified) |
|---------------|-------|----------------|
| Scheduler session map lost | `_last_session_ids` was in-memory dict, wiped on container recreation | Persisted to `logs/scheduler_state.json` (bind-mounted → host `/data/logs/`); loaded at startup, saved after every run — verified `refund-hunter` still 5 sessions after `docker restart` |
| Old sessions unreachable via API | `list_sessions()` without limit → server returns only 100 most recent | Routes now `list_sessions(limit=200)` + filter `agent==agent_id OR directory startswith /data/subworkers/{name}` (container path) → finds running session even when `x-opencode-directory` header used |
| Stale ID after DB wipe | `scheduler_state.json` pointed to `ses_fb4dcb...` from 01:30 which 404s after DB recreate | `GET /sessions/{name}` now catches 404, tries `get_running_session_id()` before 500; `GET /sessions/{name}/list` always merges `running_sid` + `scheduler_sid` into list |
| Only 1 session shown after restart | Container DB was ephemeral (no volume) → `down` wiped 2.9M DB, only stale fallback remained | Added volume `opencode-data:/root/.local/share/opencode:rw` — verified `opencode-data/opencode.db` persists 2.8M across `docker restart` |
| Container shows UTC 01:30 when host is 02:30 | No `TZ` set, `tzdata` installed but default UTC | `Dockerfile` + `docker-compose.yml` set `TZ=Africa/Casablanca` — verified `docker exec date` (`02:39 +01`) matches host `date` |

State files:
- `logs/scheduler_state.json` on host (`/data/logs/` in container), written atomically (tmp + rename) after each run. Verified `{"refund-hunter":"ses_fb2de82a…"}` persists.
- `server/opencode-data/opencode.db` (2.8M) — **do NOT delete** unless you want to wipe all container sessions; host DB (`~/.local/share/opencode`) is untouched.

---

## 9. ColimaBar (Menu Bar Control)

ColimaBar (menu bar app, source `~/Documents/EliaTopBar`) connects to the server for real-time control:

- ⚡ Trigger Now / Manual Run → `POST /trigger/{name}` (creates NEW session)
- 🔄 Continue (LogViewer badge) → `POST /sessions/{name}/{session_id}/continue` `{"message":"continue the tasks"}` — re-injects into an EXISTING old session, manual retry
- ▶️ Enable / ⏸️ Disable → `POST /enable|/disable/{name}`
- 📋 View Logs… → `GET /sessions/{name}/list` + `GET /sessions/{name}?session_id=…` (reasoning, tools, text; Continue badge on right of timestamp)
- 🔗 Change Server URL… → UserDefaults `"subworkerServerURL"` (**default is `http://localhost:8080` — set it to `http://localhost:5656`** on fresh setups; the real server runs on 5656)
- Live status: WS `/ws?token=…` with HTTP `/status` fallback (5s) + `/server/health` (30s) — requires `?token=` or `Authorization: Bearer`

> ⚠️ `lastError` / `lastCompleted` are only delivered over WebSocket events, not in HTTP `/status`. The WS error event currently carries only the subworker `name` → menu bar shows "Unknown error".

Full deep-dive: [`docs/SUBWORKERS_COLIMABAR_CONNECTION.md`](../docs/SUBWORKERS_COLIMABAR_CONNECTION.md)

---

## 10. Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not responding | Check server: `curl http://localhost:5656/status` + `docker ps \| grep elia-subworker-srv` |
| ColimaBar shows Disconnected | Set 🔗 Change Server URL… → `http://localhost:5656` (default is phantom 8080) |
| Server container not running | `cd ~/EliaAI/subworkers/server && docker compose up --build` (or restart via `EliaUI.command`) |
| OpenCode server down / `<defunct>` | `docker exec elia-subworker-srv ps aux` shows `[opencode] <defunct>` → `docker restart elia-subworker-srv` (healthcheck `global/health` fails, FastAPI `All connection attempts failed`) |
| Only 1 session after `docker restart` | Container DB was ephemeral pre-`opencode-data` volume — now `server/opencode-data/opencode.db` (2.8M) persists; verify `curl /sessions/{name}/list` shows 4-5, not 1 stale fallback |
| Time is 1h off (01:30 vs 02:30) | Check `TZ` — `docker exec date` must match host `date` (`Africa/Casablanca` `+01`); fix `Dockerfile` ENV + `docker-compose.yml` `environment: TZ` |
| OpenCode server down (auto-restart exhausted) | Check `/server/health`, restart via `POST /server/restart` or `~/EliaAI/scripts/opencode-serve.sh 4096` |
| Schedule not firing | Verify entry in `subworkers.json` (`enabled: true`, hours/minute) — server hot-reloads config |
| Trigger skips with ".enabled not found" | Create `subworkers/<agent-id>/.enabled` or run with `--force` flag for manual terminal runs |
| `EPERM: operation not permitted` on `oh-my-opencode` | Bun global package is a symlink to a local source checkout. Fix: `rm -rf ~/.bun/install/global/node_modules/oh-my-opencode && bun install -g oh-my-opencode` |
| MCP not connecting | `mcp-cli list` + restart if needed |
| Rate limited | Wait 1h + reduce frequency |
| Account banned | Stop immediately, wait 24-48h |

### 8.1 Bun Global Symlink Pitfall (macOS EPERM)

**Symptom**: The trigger script's log shows `EPERM: operation not permitted` when trying to read `oh-my-opencode.js`, even though the file exists and permissions look correct. The error happens at the Node.js module loading stage (`Module._extensions..js` → `defaultLoadImpl` → `readFileSync`).

**Root cause**: `bun install -g oh-my-opencode` was run from within a local clone of the oh-my-openagent repository. Bun creates a **symlink** in `~/.bun/install/global/node_modules/oh-my-opencode` pointing to the local checkout instead of copying the package files. When `oh-my-opencode` tries to load modules through this symlink chain, macOS blocks the read because the local checkout files may have `com.apple.provenance` extended attributes (set on downloaded/quarantined files).

**Detection**:
```bash
# Check if the global package is a symlink
ls -la ~/.bun/install/global/node_modules/oh-my-opencode
# If it shows: oh-my-opencode -> /some/local/path → BROKEN
# If it shows: drwxr-xr-x ... oh-my-opencode → OK (proper install)
```

**Fix**:
```bash
rm -rf ~/.bun/install/global/node_modules/oh-my-opencode
bun install -g oh-my-opencode
```

**Prevention**: The Node.js trigger (`trigger_template.js`) handles binary resolution via a `which()` function that checks `~/.bun/bin`, `~/.opencode/bin`, `/opt/homebrew/bin`, and `/usr/local/bin`. If `oh-my-opencode` is not found, the trigger fails immediately with a clear error message instead of a cryptic EPERM stack trace.

**Why it only affects `oh-my-opencode run` and not `oh-my-opencode --version`**: The `--version` flag reads `package.json` directly from the wrapper script location and exits before loading the platform-specific binary. The `run` command (and most other commands) trigger the full module loading chain, which traverses the symlink and hits macOS security restrictions.

---

## 11. Elia — Main Agent (as a Subworker)

**New feature (August 2026):** Elia, the main agent, is now also a subworker — the **main** one. The logic and code are the same as any other subworker; only the designation differs ("main" title or not).

### 11.1 Designation

- `subworkers/main-agent.json` holds `{"name":"elia"}` — the agent flagged as **MAIN** (managed via `GET/POST /main-agent`).
- **Both UIs fully control who is MAIN:**
  - **ui_electron subworker popup** — MAIN badge + ★/✕ edit button (`POST /main-agent`)
  - **EliaTopBar** — ★ marker on the agent row + "Set/Unset as Main Agent" in the submenu
- The main agent runs with the **repo root** (`~/EliaAI`) as workspace instead of an isolated `subworkers/<name>/workspace/` — resolved at run time by `SubworkerRunner._read_main_agent_name()`. Unsetting falls back to `elia`.

### 11.2 PROMPT.md location

Elia's prompt moved **without editing** from the repo root (`PROMPT.md`) to **`subworkers/elia/PROMPT.md`** — the standard subworker location. The server loads it via `prompt_file: PROMPT.md` (relative to workspace) in `subworkers.json`. The root-level `PROMPT.md` no longer exists.

### 11.3 Triggering

Elia runs through the **Docker subworker server** (`elia-subworker-srv`, port 5656) — scheduled from `subworkers.json` and triggered via the REST API (cron, morning, voice, UI):

```bash
curl -s -X POST http://127.0.0.1:5656/trigger/elia
```

The server's `SubworkerRunner` uses the entry's `workspace` (repo root for the main agent) and `prompt_file` (`PROMPT.md`) to create a session on the host OpenCode server with `agent=elia` and send the prompt over HTTP. Subworkers other than the main one keep their isolated workspace.

---

**End of Guide**
