# Subworkers System

**Date:** April 2026  
**Version:** 3.0

> Technical documentation for the autonomous subworker agent system.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Directory Structure](#2-directory-structure)
3. [Workspace Isolation & Per-Agent Permissions](#3-workspace-isolation--per-agent-permissions)
4. [OpenCode Agent Registration](#4-opencode-agent-registration)
5. [Trigger Template](#5-trigger-template)
6. [Tools & MCP Servers](#6-tools--mcp-servers)
7. [LaunchAgent Setup](#7-launchagent-setup)

---

## 1. Overview

### What Are Subworkers?

Subworkers are autonomous AI agents that run on a schedule or trigger. Each subworker has:
- A **personality file** (`~/.config/opencode/agents/<agent-id>.md`) — loaded automatically by oh-my-opencode via the `-a` flag
- A **PROMPT.md** with task-specific instructions — injected by the trigger
- A **workspace folder** for isolated file I/O
- A **trigger script** that launches via `oh-my-opencode run`
- An optional **LaunchAgent plist** for scheduled execution

### Architecture

```
Trigger (launchd / manual)
  └─ trigger_template.js (Node.js, child_process.spawn)
       ├── Creates workspace/ if missing
       ├── Loads PROMPT.md
       ├── oh-my-opencode run -d workspace/ -a <agent> "<task>"
       │     └── oh-my-opencode loads personality from ~/.config/opencode/agents/<agent-id>.md
       └── OpenCode loads workspace/opencode.json (per-agent permissions)
```

---

## 2. Directory Structure

```
EliaAI/subworkers/
├── SUBWORKERS_SYSTEM.md          # This file
├── scripts/
│   └── trigger_template.js       # UNIVERSAL TEMPLATE (Node.js, no per-agent wrappers needed)
├── logs/
│   ├── <agent_name>.log          # Aggregate logs
│   └── runs/
│       └── <agent_name>/         # Per-run logs
└── <agent-id>/
    ├── PROMPT.md                 # Task-specific instructions
    ├── .enabled                  # Gate file — presence = active
    ├── .loop_mode                # (Optional) Server-attach loop mode
    └── workspace/                # Runtime directory (auto-created)
        ├── opencode.json         # (Optional) Per-agent tool permissions
        └── docs/                 # Daily work folders (auto-created)
            ├── 2026-04-01/
            ├── 2026-04-02/
            └── ...               # idempotent — mkdir -p once per day
```

### Creating a New Subworker

```bash
mkdir -p ~/EliaAI/subworkers/<agent-id>/workspace
touch ~/EliaAI/subworkers/<agent-id>/.enabled  # or use --force to skip
```

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

### 5.1 Template File: `scripts/trigger_template.js`

The universal trigger template (Node.js) handles all subworker launch logic. No per-agent wrapper scripts needed — the launchd plist passes `--agent <name>` directly:

```xml
<string>node</string>
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

## 7. LaunchAgent Setup

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
        <string>node</string>
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
        <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
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

## 8. Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not responding | Check `launchctl list \| grep com.elia` |
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

**End of Guide**
