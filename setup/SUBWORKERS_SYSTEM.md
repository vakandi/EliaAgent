# Subworkers System

**Date:** April 2026  
**Version:** 3.0

> Technical documentation for the autonomous subworker agent system.

---

## 🚫 RÈGLE ABSOLUE N°1 — LES AGENTS NE SE MODIFIENT JAMAIS EUX-MÊMES

> **CE PRÉFIXE EST TRANSMIS À TOUS LES SUBWORKERS, SANS EXCEPTION. AUCUN AGENT N'ÉDITE, NE CRÉE, NE SUPPRIME NI NE REMPLACE SA PROPRE INFRASTRUCTURE.**

**Interdiction totale et permanente**, applicable à chaque run, quel que soit le contexte : run normal, run forcé (`--force`), mode setup, mode débug, tâche ambiguë, "PROMPT.md partagé par l'utilisateur", etc.

**Fichiers VERROUILLÉS (lecture seule pour l'agent) :**
- Son propre `PROMPT.md` (`subworkers/<agent>/PROMPT.md`)
- Son fichier de personnalité (`~/.config/opencode/agents/<agent>.md`)
- Ses scripts de trigger, `.enabled`, `.loop_mode`, plists (`subworkers/plists/`, `~/Library/LaunchAgents/`)
- `SUBWORKERS_SYSTEM.md`, `opencode.json`, registres d'agents, `context/TOOLS.md`
- Ses skills (`~/.config/opencode/skills/<agent>/`)
- **TOUT fichier situé hors de son `workspace/`**

**Territoire d'écriture :** chaque agent n'écrit QUE dans `subworkers/<agent>/workspace/`. Tout le reste du système est en lecture seule.

**Comportement attendu si un fichier système semble cassé ou manquant :** signaler dans `HANDOFF_NEXT_SESSION.md` + rapport de fin de run. **NE JAMAIS corriger soi-même.** Seul Wael ou l'agent principal Elia modifie le système.

> ⚠️ Un subworker qui se modifie lui-même = violation fatale. Ceci n'est pas une suggestion, c'est la règle n°1 du système.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Directory Structure](#2-directory-structure)
3. [Workspace Isolation & Per-Agent Permissions](#3-workspace-isolation--per-agent-permissions)
4. [OpenCode Agent Registration](#4-opencode-agent-registration)
5. [Trigger Template](#5-trigger-template)
6. [Tools & MCP Servers](#6-tools--mcp-servers)
7. [LaunchAgent Setup](#7-launchagent-setup)
8. [Enable/Disable & Schedule Management](#8-enabledisable--schedule-management)

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
├── vcam-community-organic/       # VcamAndroid Community Manager (social content, engagement)
│   ├── PROMPT.md
│   └── workspace/
├── vcam-seo/                     # VcamAndroid SEO Strategist (blog, rankings, GEO)
│   ├── PROMPT.md
│   └── workspace/
├── refund-hunter/                # RefundHunter (ecommerce refund policy & resale research, Google Doc daily)
│   ├── PROMPT.md
│   └── workspace/
└── <agent-id>/                   # Template — replace with actual agent ID
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
mkdir -p /Users/vakandi/EliaAI/subworkers/<agent-id>/workspace
touch /Users/vakandi/EliaAI/subworkers/<agent-id>/.enabled  # or use --force to skip
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
      "allow": ["/Users/vakandi/EliaAI/subworkers/<agent-id>/workspace/**"],
      "deny": ["**"]
    },
    "write": {
      "allow": ["/Users/vakandi/EliaAI/subworkers/<agent-id>/workspace/**"],
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
`/Users/vakandi/EliaAI/subworkers/<agent-id>/workspace/`
Never write files outside this folder. All system paths outside workspace/ are blocked.

## Daily Folders
Each run creates a daily folder directly in workspace: `workspace/YYYY-MM-DD/`.
Write your work logs, research, and outputs into today's folder.
The folder is idempotent — only one per day regardless of how many times the trigger runs.
You can read all previous days' folders to understand context and history.

## Handoff
At the START of every run, read `workspace/HANDOFF_NEXT_SESSION.md` — it tells you exactly where the previous run left off, what's done, and what to do next.
At the END of every run, overwrite `workspace/HANDOFF_NEXT_SESSION.md` with current state so the next session can pick up seamlessly. Never leave stale tasks in the "Next priorities" section.

## Mempalace
To orient yourself on every run:
1. Read `workspace/HANDOFF_NEXT_SESSION.md` for the latest battle plan (completed, pending, next priorities)
2. Check `workspace/` for the latest day folder to read today's work-in-progress
3. Scan previous days' docs for relevant context: decisions made, blockers, next steps
4. If you need to revisit something from days ago, navigate by date: `workspace/2026-04-01/`
5. Before finishing, write a summary into the current day's folder AND update `HANDOFF_NEXT_SESSION.md`
```

### 3.5 Discord Channel Setup — Mandatory for Reporting

Every subworker that reports via Discord **MUST** have a dedicated channel. Discord is the ONLY interaction point between subworkers and the user — there is no other way for agents to communicate results, ask questions, or escalate blockers.

**When creating a new subworker, follow this procedure:**

1. **List available Discord guilds:**
```bash
mcp-cli call discord-server-mcp list_guilds '{}'
```

2. **Ask the user which guild to use** — present the list of available guilds with their names and IDs. The user chooses the guild where the agent should report.

3. **List categories in the chosen guild:**
```bash
mcp-cli call discord-server-mcp list_categories '{"guild_id":"<chosen_guild_id>"}'
```

4. **Ask the user which category** to place the agent's reporting channel under. Categories organize channels logically (e.g., "MIRORPAY", "BENE2LUXE", "REPORTS").

5. **Create the channel in the right category:**
```bash
mcp-cli call discord-server-mcp create_channel '{
  "guild_id": "<guild_id>",
  "name": "<agent-name>-reports",
  "type": 0,
  "parent_id": "<category_id>"
}'
```

6. **Save the channel ID** — the response returns the new channel's ID. Use this in the PROMPT.md reporting section:
```markdown
## 💬 REPORTING — Discord
**Canal:** `<channel_id>` (<guild_name> / <category_name>)
**Outil:** `mcp-cli call discord-server-mcp send_message`
```

**Why this matters:**
- Agents cannot ask questions or escalate issues without a Discord channel
- Each agent needs its own channel to avoid cross-talk between subworkers
- The channel MUST be in the correct category for organization
- The channel ID is what the agent uses to send reports via `mcp-cli call discord-server-mcp send_message`

**⚠️ DO NOT hardcode Discord channel IDs in PROMPT.md without first creating the channel via this procedure.** Channel IDs are unique per guild — copying an ID from another agent's PROMPT.md will send messages to the wrong channel.

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

### 4.6 Model IDs Must Match `opencode models`

The subworker UI and manual trigger must use the same model IDs that `opencode models` prints on this machine.

- Treat `opencode models` as the source of truth for the current catalog.
- Use the exact model string that the runtime accepts, not an old alias copied from a past popup.
- If a saved UI selection points to a stale alias, normalize it once on load and resave the fixed value.
- Do not invent provider prefixes or `:free` suffixes unless they are present in the current catalog and accepted by the trigger path.

For the Electron popup, the model badge and the "Run now" button should always round-trip through the same normalized model ID.

### 4.7 Restart OpenCode

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
<string>/Users/vakandi/.bun/bin/node</string>
<string>/Users/vakandi/EliaAI/subworkers/scripts/trigger_template.js</string>
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
| **OpenCode sandboxing** | Each trigger run creates a fresh temp XDG sandbox for OpenCode data/cache/state so parallel subworkers do not share `~/.local/share/opencode` or other host runtime files |
| **Proxy support** | When `.proxy_enabled` is present, the trigger refreshes proxy state via `setup/switch-proxy.sh` before launching the agent |
| **Recovery resume** | On retry, the trigger tries to recover the prior `Session:` line from the previous run log, waits 20s, and resends `continue the work` into the same session via `--session-id` before falling back to a fresh run |
### 5.3 Mode Selection

**Task mode** (default): Single-shot execution. Agent runs once and exits.

**Loop mode** (`.loop_mode` file): Agent runs in a persistent server-attached loop using `/ulw-loop` or `/ralph-loop`. Used for continuous promotion/social agents.

```bash
# Enable loop mode for an agent
touch /Users/vakandi/EliaAI/subworkers/<agent-id>/.loop_mode
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

### 5.6 Retry & Session Recovery

When a subworker run fails, the trigger now prefers to reuse the previous OpenCode session instead of starting over.

Recovery flow:

1. Read the previous run log and extract the last `Session:` / `Session ID:` value.
2. Wait 20 seconds before the first recovery resend.
3. Re-run `oh-my-opencode run` with `--session-id <recovered-session-id>`.
4. Send the short continuation prompt `continue the work` into that same session.
5. If the reuse path returns `promptAsync skipped by gate: active`, keep the same session and retry it again after another cooldown instead of immediately falling back.
6. If the resume is killed or does not validate after the same-session retries are exhausted, log the reason and let the outer retry loop decide whether to try a fresh run.
7. Between outer retry attempts, wait a random 20-40 seconds so parallel subworkers do not all restart on the same second.

Why this exists:

- It keeps continuity in the same session when the agent is still salvageable.
- It gives the session time to settle before replaying the prompt.
- It makes the retry logs explicit enough to diagnose whether the failure was reuse, validation, or an external kill.
- If OpenCode itself fails before a session ever exists, that is handled as a bootstrap failure first: the server connection layer retries the timed-out start before the outer trigger falls back to a fresh run.
- The trigger now also isolates OpenCode runtime state per run by exporting temp `XDG_DATA_HOME` / `XDG_CACHE_HOME` / `XDG_STATE_HOME` values, which prevents concurrent subworkers from fighting over the same OpenCode log/database files.
- When proxy mode is enabled, the trigger refreshes the proxy first via `setup/switch-proxy.sh`, then injects the resulting proxy env into the actual agent run while keeping localhost traffic unproxied.

Relevant log lines:

- `[RECOVERY] Session lookup result: ...`
- `[RECOVERY] Cooling down before reusing session ...`
- `[RECOVERY] Dispatching continuation prompt to session ...`
- `[RECOVERY] Continuation dispatch returned exit_code=...`
- `[RECOVERY] Reuse result: blockedByActive=..., validated=...`
- `[RECOVERY] Session ... is still active; keeping the same session and retrying after cooldown`
- `[RECOVERY] Exhausted same-session retries ...`
- `[RETRY] ...s remaining` heartbeat lines while waiting to restart
- In task mode, cleanup is scoped to owned loop servers only; it does not kill unrelated ports used by sibling subworkers.
- Retry backoff is randomized in the 20-40 second range to reduce startup collisions when several subworkers fail at once.

### 5.7 Handoff File (`HANDOFF_NEXT_SESSION.md`)

Every subworker run **MUST** end by writing or updating a handoff file at the workspace root:

```
workspace/HANDOFF_NEXT_SESSION.md
```

**Purpose:** This file is the bridge between runs. It tells the next session exactly where the previous one left off — what was done, what's pending, and what to do next. Without it, each run starts blind and risks duplicating work or repeating completed tasks.

**What the agent MUST write before finishing:**

```markdown
# Handoff — <agent-id>

**Last run:** YYYY-MM-DD HH:MM
**Run status:** success | partial | failed

## ✅ Completed this run
- [Specific task 1 with detail]
- [Specific task 2 with detail]

## 🔄 In progress
- [Task still being worked on — include exact file paths, line numbers, or state]

## ⏳ Next priorities (in order)
1. [Most important next action — be specific, not vague]
2. [Second priority]
3. [Third priority]

## 🚫 Do NOT repeat
- [Specific actions that were already attempted and completed]
- [Dead ends or approaches that were tried and rejected]

## 🔒 Blockers / Decisions needed
- [Any blockers preventing progress]
- [Decisions that need human input — include context so the next run can proceed or escalate]

## 📂 Key files touched
- path/to/file.py — [what was changed]
- path/to/other.md — [what was done]
```

**Rules for the handoff file:**

1. **Overwrite, don't append** — Each run replaces the entire file. The file reflects the LATEST state, not a history log.
2. **Be specific** — "Worked on auth" is useless. "Fixed token refresh in `auth.py:45` — added 30s buffer before expiry" is actionable.
3. **Name dead ends** — If a run tried something that failed, the next run must know NOT to retry it. Include "Do NOT repeat" entries.
4. **Prioritize the next run** — The "Next priorities" section is the most important part. The agent reads this FIRST to know what to do.
5. **No stale tasks** — If a task was completed, move it to "Completed" or delete it. Never leave finished work in "Next priorities."

**How the agent uses it on startup:**

When a subworker starts a new run, the Mempalace protocol (§3.4) should include reading this file:

```
## Startup Protocol
1. Read workspace/HANDOFF_NEXT_SESSION.md — this tells you exactly what to do next
2. Follow the "Next priorities" section in order
3. Do NOT redo anything listed in "Do NOT repeat"
4. At the end of your run, overwrite HANDOFF_NEXT_SESSION.md with the current state
```

**Why this matters:**

- **Without handoff:** Each run re-reads all context from scratch, potentially redoing completed work, missing in-progress tasks, or retrying dead ends.
- **With handoff:** Each run starts with a precise battle plan. The agent knows what's done, what's next, and what to avoid. Work advances every run instead of spinning.

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
        <string>/Users/vakandi/EliaAI/subworkers/scripts/trigger_template.js</string>
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
        <string>/Users/vakandi/.bun/bin:/Users/vakandi/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>/Users/vakandi</string>
    </dict>

    <key>WorkingDirectory</key>
    <string>/Users/vakandi/EliaAI</string>

    <key>StandardOutPath</key>
    <string>/Users/vakandi/EliaAI/subworkers/logs/<agent_name>.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/vakandi/EliaAI/subworkers/logs/<agent_name>.log</string>
</dict>
</plist>
```

### 7.2 Load & Verify

```bash
launchctl load /Users/vakandi/EliaAI/subworkers/plists/com.elia.<agent-id>.plist
launchctl list | grep "com.elia"
```

---

## 8. Enable/Disable & Schedule Management

### 8.1 The `.enabled` Gate

Every subworker has a gate file at `subworkers/<agent-id>/.enabled`:

| State | File | Behavior |
|-------|------|----------|
| **Enabled** | `.enabled` exists | LaunchAgent runs on schedule; manual runs work without `--force` |
| **Disabled** | `.enabled` missing | LaunchAgent skips scheduled runs; manual runs require `--force` flag |

**The trigger template (`trigger_template.js`) checks this file on every run:**
- If `.enabled` exists → proceed normally
- If `.enabled` missing AND no `--force` flag → exit code 0 (skip)
- If `.enabled` missing AND `--force` flag → proceed (manual override)

### 8.2 Electron UI — Subworker Popup (`ui_electron/subworker-popup.html`)

The Electron UI provides a visual interface to manage all subworkers:

**Features:**
- **Toggle switches** — Click to enable/disable any subworker
- **Schedule badges** — Shows configured schedule (e.g., "10:00–23:00 daily")
- **Run now button** — Manual trigger with model selection from the current `opencode models` catalog
- **Logs button** — Opens latest run log
- **Runs dropdown** — Shows recent run history with exit codes and durations

**How toggling works (via `ui_electron/src/main.js`):**

```javascript
ipcMain.on('toggle-subworker', (event, name) => {
  const subworkerDir = path.join(subworkersRoot, name);
  const plistName = `com.elia.${name}`;
  const plistPath = path.join(subworkersRoot, 'plists', `${plistName}.plist`);
  const enabledPath = path.join(subworkerDir, '.enabled');

  if (fs.existsSync(enabledPath)) {
    // DISABLE: remove .enabled + unload from launchd
    fs.unlinkSync(enabledPath);
    if (fs.existsSync(plistPath)) {
      execSync(`launchctl bootout gui/$(id -u) ${plistPath} 2>/dev/null || true`);
    }
  } else {
    // ENABLE: create .enabled + load into launchd
    fs.writeFileSync(enabledPath, 'enabled\n', 'utf8');
    if (fs.existsSync(plistPath)) {
      execSync(`launchctl bootstrap gui/$(id -u) ${plistPath} 2>/dev/null || true`);
    }
  }
  // Reply with new state
  event.reply('subworker-toggled', { name, enabled, running });
});
```

**Key behaviors:**
- **Enable** → Creates `.enabled` file + `launchctl bootstrap` the plist
- **Disable** → Removes `.enabled` file + `launchctl bootout` the plist
- **Requires plist** — Toggle only works if `subworkers/plists/com.elia.<name>.plist` exists
- **State sync** — UI receives `subworker-toggled` reply and updates toggle visuals

### 8.3 Changing Schedule Times

**To change a subworker's schedule:**

1. **Edit the plist** at `subworkers/plists/com.elia.<agent-id>.plist`
2. **Modify the `StartCalendarInterval` array** — each `<dict>` defines one scheduled time:
   ```xml
   <key>StartCalendarInterval</key>
   <array>
       <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
       <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>30</integer></dict>
       <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
   </array>
   ```
3. **Reload the LaunchAgent** (required for changes to take effect):
   ```bash
   launchctl bootout gui/$(id -u) /Users/vakandi/EliaAI/subworkers/plists/com.elia.<agent-id>.plist
   launchctl bootstrap gui/$(id -u) /Users/vakandi/EliaAI/subworkers/plists/com.elia.<agent-id>.plist
   ```

**Common schedule patterns:**
| Pattern | StartCalendarInterval |
|---------|----------------------|
| Every hour 9am–11pm | Hours 9–23, Minute 0 |
| Twice daily (9am, 2pm) | Hour 9 + Hour 14, Minute 0 |
| Every 30 min (9am–5pm) | Hours 9–17, Minutes 0 + 30 |
| Once daily at 6am | Hour 6, Minute 0 |

**⚠️ Important:** After editing the plist, you **MUST** reload it with `launchctl bootout` + `bootstrap`. The Electron UI toggle does this automatically when you enable/disable, but manual plist edits require manual reload.

### 8.4 Setting Up a New Subworker for Auto-Run

For a subworker to run automatically on schedule:

1. **Create the plist** at `subworkers/plists/com.elia.<agent-id>.plist` (use template in §7.1)
2. **Create `.enabled` file**: `touch subworkers/<agent-id>/.enabled`
3. **Load into launchd**: `launchctl bootstrap gui/$(id -u) subworkers/plists/com.elia.<agent-id>.plist`
4. **Verify**: `launchctl list | grep com.elia.<agent-id>` — should show a PID or `-` (loaded, waiting for schedule)

**Or use the Electron UI:**
1. Open the subworker popup
2. Click the toggle switch for the agent
3. The UI creates `.enabled` + loads the plist automatically

### 8.5 Current Subworker Status (as of Aug 2026)

| Subworker | .enabled | Plist | Launchd Status | Schedule |
|-----------|----------|-------|----------------|----------|
| refund-hunter | ✅ | ✅ | Loaded (PID 62965) | 10:00–22:00 hourly |
| bene2luxe-promoter | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| bene2luxe-suppliers | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| cobou-promoter | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| mirorpay-community-organic | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| mirorpay-seo | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| mirrorpay-telegram | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| vcam-community-organic | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| vcam-seo | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| teleorbit-community-organic | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| teleorbit-seo | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| reddit-saas-scraper | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| tempack-dev | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |
| tiktok-content | ❌ | ✅ | Not loaded | 9:00–23:00 hourly |

**To enable any subworker:** Click the toggle switch in the Electron UI (or run `touch subworkers/<agent-id>/.enabled` + `launchctl bootstrap gui/$(id -u) subworkers/plists/com.elia.<agent-id>.plist` manually).

---

## 9. Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not responding | Check `launchctl list \| grep com.elia` |
| Trigger skips with ".enabled not found" | Create `subworkers/<agent-id>/.enabled` or run with `--force` flag for manual terminal runs |
| OpenCode TUI says `Config invalid - run doctor` and shows `../.omo/omo.jsonc: Un...` | The project config is likely wrapped in `[opencode]` when it should use top-level `agents` / `categories` / `task` / `teams`. Flatten the file to the current `omo.jsonc` schema and keep `[opencode]` only for actual harness overrides like `codegraph`. |
| Parallel subworkers crash OpenCode with `FileSystem.open (.../opencode.log)` | The trigger should be launching with per-run temp `XDG_DATA_HOME` / `XDG_CACHE_HOME` / `XDG_STATE_HOME`. If you still see the host path, update `trigger_template.js` and restart the Electron UI so the button picks up the new wrapper. |
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
