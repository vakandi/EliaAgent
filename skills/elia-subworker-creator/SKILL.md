---
name: elia-subworker-creator
description: >-
  Create a new autonomous subworker in the EliaAI system. A subworker is an AI agent with its own personality
  (stored in ~/.config/opencode/agents/), its own detailed prompt (in subworkers/<agent-id>/PROMPT.md), a trigger
  script sourcing trigger_template.sh, an isolated workspace with per-agent permissions, and an optional
  LaunchAgent plist for scheduling. This skill handles the FULL pipeline:
  opencode.json + oh-my-openagent.json registration → agent personality → PROMPT.md with workspace constraint →
  trigger script → workspace isolation + per-agent opencode.json → plist → SUBWORKERS_SYSTEM.md update.
  Use this whenever the user says "create a subworker", "add a new agent", "make a promoter", "new sub-worker",
  "add subworker", or any request to create a scheduled autonomous agent for the EliaAI ecosystem.
  DO NOT attempt to create subworkers without this skill — the procedure has many interdependencies and
  forgetting any one step will break the system.
---

# EliaAI Subworker Creator

## Why This Skill Exists

This session, multiple mistakes were made creating a subworker because the full procedure has 8 interdependent
steps across 5 different locations (opencode.json, oh-my-openagent.json, subworkers directory, scripts, plists).
Forgetting even one step (like registering in `oh-my-openagent.json`) silently breaks the subworker.
This skill enforces the complete, verified pipeline.

## Overview — The 8-Step Pipeline

```
opencode.json + oh-my-openagent.json (register agent in TWO files)
  → ~/.config/opencode/agents/<agent-id>.md (personality + YAML frontmatter)
    → subworkers/<agent-id>/PROMPT.md (detailed workflow + workspace constraint)
      → subworkers/scripts/trigger_<agent_name>.sh (sources trigger_template.sh — 4 lines)
        → subworkers/<agent-id>/workspace/ + opencode.json (isolation + permissions)
          → subworkers/plists/com.elia.<agent-id>.plist (LaunchAgent)
            → SUBWORKERS_SYSTEM.md (register in master doc)
              → subworkers/<agent-id>/.enabled (disabled by default)
```

Each step references files from previous steps. Doing them in order is critical.

---

## Step 0: READ FIRST — Understand the existing patterns

**Before creating anything**, read these reference files to understand the conventions:

```bash
cat /path/to/EliaAI/subworkers/SUBWORKERS_SYSTEM.md
cat /path/to/EliaAI/subworkers/scripts/trigger_template.sh
cat /path/to/config/opencode/opencode.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('agent',{}), indent=2))"
ls /path/to/config/opencode/agents/
ls /path/to/EliaAI/subworkers/scripts/
ls /path/to/EliaAI/subworkers/plists/
```

Also read the newest subworker (yourapp-seo) — it follows the current system with workspace isolation:
```bash
cat /path/to/EliaAI/subworkers/yourapp-seo/PROMPT.md
cat /path/to/EliaAI/subworkers/scripts/trigger_yourapp_seo.sh
ls -la /path/to/EliaAI/subworkers/yourapp-seo/workspace/
```

---

## Step 1: Register agent — TWO files required

Every new subworker MUST be registered in both `opencode.json` AND `oh-my-openagent.json`.

### Conventions
- **Agent ID**: kebab-case, descriptive (e.g., `yourbrand-suppliers`, `yourapp-seo`)
- **Agent name** (for trigger scripts): underscore version of Agent ID (`yourbrand_suppliers`, `yourapp_seo`)
- **Mode**: always `"primary"` for scheduled autonomous agents

### File 1: `~/.config/opencode/opencode.json`

Add to the `"agent"` section:

```python
import json

with open('/path/to/config/opencode/opencode.json') as f:
    data = json.load(f)

data['agent']['<agent-id>'] = {
    "description": "<short description, 50-80 chars>",
    "mode": "primary"
}

with open('/path/to/config/opencode/opencode.json', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
```

### File 2: `~/.config/opencode/oh-my-openagent.json`

Add entries to THREE sections:

#### 2a. `"agents"` section:
```python
data['agents']['<agent-id>'] = {
    "model": "opencode/big-pickle",
    "mode": "primary",
    "fallback_models": []
}
```

#### 2b. `"categories"` section — add `prompt_append` pointing to PROMPT.md:
```python
data['categories']['<agent-id>'] = {
    "model": "opencode/big-pickle",
    "description": "<short description>",
    "prompt_append": "**FIRST: Read /path/to/EliaAI/subworkers/<agent-id>/PROMPT.md for your full instructions.**\n\nYou are <agent-id>. Execute your assigned task. Always respect your workspace constraint."
}
```

#### 2c. `"agent_display_names"` section:
```python
data['agent_display_names']['<agent-id>'] = "Readable Name"
```

**⚠️ Critical:** The `prompt_append` references the PROMPT.md path — make sure this path uses the EXACT same `<agent-id>`. The workspace constraint reminder is mandatory.

### Registration Summary

| # | What | Where | Why |
|---|------|-------|-----|
| 1 | `"mode": "primary"` | `opencode.json` → `"agent"` section | Makes agent visible in `/agents` list |
| 2 | `"mode": "primary"` | `oh-my-openagent.json` → `"agents"` section | Makes agent callable via `oh-my-opencode run -a <agent>` |
| 3 | Add to `"categories"` | `oh-my-openagent.json` → `"categories"` | Adds `prompt_append` with pointer to PROMPT.md |
| 4 | Add display name | `oh-my-openagent.json` → `"agent_display_names"` | Shows readable name in `/agents` menu |

> ⚠️ **Failure to register in both files = agent invisible/invokable.**

---

## Step 2: Create agent personality file (~/.config/opencode/agents/<agent-id>.md)

The agent personality file in `~/.config/opencode/agents/` serves as the agent's identity and is loaded
when the subworker triggers. ALWAYS include YAML frontmatter.

**YAML frontmatter fields:**
- `name`: Must match agent ID (e.g., `yourapp-seo`)
- `slug`: Same as name
- `description`: Short description
- `model`: `opencode/big-pickle`
- `temperature`: 0.2-0.3 for focused, 0.5+ for creative
- `mode`: `primary`

**Body content — what to include:**
- Identity (who they are, 1-2 sentences)
- Mission (what they do, in one sentence)
- Key skills or tools they use
- Behavioral rules
- Anti-patterns (must-avoid behaviors)

**Example:**
```markdown
---
name: <agent-id>
slug: <agent-id>
description: Short description
model: opencode/big-pickle
temperature: 0.3
mode: primary
---

# <Agent Name> — Identity

Tu es un [role] spécialisé en [domain]. [1-2 sentence identity].

## Mission
[One sentence mission]

## Behavioral Rules
1. [Rule 1]
2. [Rule 2]

## Anti-Patterns
- ❌ [What to avoid]
```

**Path:** `/path/to/config/opencode/agents/<agent-id>.md`

---

## Step 3: Create PROMPT.md (subworkers/<agent-id>/PROMPT.md)

Create the detailed workflow document. This is the MAIN file the agent reads at runtime.

**Location:** `/path/to/EliaAI/subworkers/<agent-id>/PROMPT.md`

**Required sections:**
1. **SOURCE DE VÉRITÉ** — List all personality files to read first (from `~/.config/opencode/agents/`)
2. **MISSION** — What this subworker does
3. **RUN CYCLE** — How long each run takes (max duration)
4. **WORKSPACE CONSTRAINT** — MUST include these exact instructions (copy from §3.4 of SUBWORKERS_SYSTEM.md):
   - Only read/write inside `workspace/` folder
   - Daily docs pattern (`workspace/docs/YYYY-MM-DD/`)
   - Mempalace: check previous days' docs for context, write summary to today's folder
5. **WORKFLOW** — Step-by-step instructions
6. **OUTILS** — What tools they can use (Discord channels, Jira, etc.)
7. **REPORTING** — How to report results (Discord format)
8. **LIMITATIONS** — What they must NOT do

**⚠️ NEVER include a personality.md in the subworker folder.** Personalities go in
`~/.config/opencode/agents/` only. The PROMPT.md references those files in SOURCE DE VÉRITÉ.

**Naming conventions:**
- Subworker folder name = agent name (kebab-case)
- `PROMPT.md` inside (not `prompt.md`, not `instructions.md`)

---

## Step 4: Create trigger script (subworkers/scripts/trigger_<agent_name>.sh)

The trigger script is the wrapper that launchd calls. **Do NOT write it from scratch** — use
the universal `trigger_template.sh` which handles all launch logic: PATH resolution, `.enabled`
gate, PROMPT.md loading, workspace creation, daily docs folders, mode detection, and logging.

**Create the wrapper (4 lines):**

```bash
#!/bin/zsh
# <Readable Name> — Trigger (template wrapper)
AGENT_NAME="<underscore_agent_name>"
source "$(dirname "$0")/trigger_template.sh"
```

The only configuration variable is `AGENT_NAME` (underscore convention, e.g., `yourapp_seo`).
The template derives the agent ID as `AGENT_ID="${AGENT_NAME//_/-}"` (e.g., `yourapp-seo`).

**Make it executable:**
```bash
chmod +x /path/to/EliaAI/subworkers/scripts/trigger_<agent_name>.sh
```

### What the template handles for you

| Feature | Detail |
|---------|--------|
| **PATH resolution** | Finds `oh-my-opencode` in launchd context |
| **`.enabled` gate** | Skips if no `.enabled` file |
| **PROMPT.md + personality loading** | Reads from subworker directory |
| **Workspace auto-creation** | Creates `workspace/` + `workspace/docs/YYYY-MM-DD/` |
| **`-d` flag** | Passes `--directory workspace/` for per-agent config |
| **Mode detection** | `task` (single-shot) vs `loop` (server-attach) |
| **Per-run logging** | Individual + aggregate logs |
| **Proxy support** | Via `.proxy_enabled` file |

---

## Step 5: Create workspace + per-agent permissions (subworkers/<agent-id>/workspace/)

The trigger template auto-creates `workspace/` and `workspace/docs/YYYY-MM-DD/`, but you
MUST also create the per-agent `opencode.json` to restrict file access.

### 5.1 Create workspace directory

```bash
mkdir -p /path/to/EliaAI/subworkers/<agent-id>/workspace
```

### 5.2 Create per-agent `workspace/opencode.json`

This file blocks ALL folders on the system except the agent's own workspace. The agent keeps
full MCP/API access but cannot read/write files outside `workspace/`.

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
      "allow": ["/path/to/EliaAI/subworkers/<agent-id>/workspace/**"],
      "deny": ["**"]
    },
    "write": {
      "allow": ["/path/to/EliaAI/subworkers/<agent-id>/workspace/**"],
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

**Key rules:**
- `permissions.read/write.deny: ["**"]` — blocks ALL paths by default
- `permissions.read/write.allow` — only the agent's own workspace
- `mcpServers` — agent still has full MCP access for API calls
- `permissions.execute.deny: ["**"]` — blocks arbitrary command execution

If no `workspace/opencode.json` exists, the agent falls back to global config (no restrictions).

**⚠️ The `-d` flag in `trigger_template.sh` (Step 4) is what makes this work.** Without `-d workspace/`,
OpenCode won't load the per-agent config. The template handles this automatically.

---

## Step 6: Create LaunchAgent plist (subworkers/plists/com.elia.<agent-id>.plist)

Creates a scheduled LaunchAgent. The plist runs the trigger script at the specified interval.

**Naming conventions in the plist:**
- `<agent-id>` = hyphenated (e.g., `yourapp-seo`) — used in Label and folder paths
- `<agent_name>` = underscored (e.g., `yourapp_seo`) — used in trigger script filename and log file

**Template:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.elia.<agent-id></string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>/path/to/EliaAI/subworkers/scripts/trigger_<agent_name>.sh</string>
    </array>

    <key>RunAtLoad</key>
    <false/>

    <key>StartCalendarInterval</key>
    <array>
        <!-- Customize schedule — example: hourly 9am-6pm -->
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/path/to/opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>/home/user</string>
    </dict>

    <key>WorkingDirectory</key>
    <string>/path/to/EliaAI</string>

    <key>StandardOutPath</key>
    <string>/path/to/EliaAI/subworkers/logs/<agent_name>.log</string>

    <key>StandardErrorPath</key>
    <string>/path/to/EliaAI/subworkers/logs/<agent_name>.log</string>
</dict>
</plist>
```

**Schedule examples:**
- Single daily: `<dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>`
- Hourly 8h-23h: one dict per hour
- Every 30 min: use `StartInterval` with `<integer>1800</integer>` instead of `StartCalendarInterval`

---

## Step 7: Update SUBWORKERS_SYSTEM.md

Edit `/path/to/EliaAI/subworkers/SUBWORKERS_SYSTEM.md` to register the new subworker:

1. **Directory Structure** (§2) — Add the new folder, script, plist, and log entries to the tree
2. **Creating a New Subworker** (§2.1) — Add `mkdir -p` and `.enabled` commands for the new agent
3. **Tools & MCP Servers** (§6) — If the agent needs new tools, add them to the tables

**⚠️ NEVER overwrite SUBWORKERS_SYSTEM.md — always edit it in place.** Use the `edit` tool
to add insertions to the existing sections. The doc is a generic system architecture reference
(no per-agent Key Differences table).

---

## Step 8: Create .enabled flag (disabled by default)

The subworker is disabled by default. To enable it later, create the `.enabled` flag:

```bash
# Disabled by default (skip this in the initial creation)
# touch /path/to/EliaAI/subworkers/<agent-id>/.enabled
```

Only create `.enabled` if the user explicitly asks to activate the subworker. By default,
the trigger script checks for `.enabled` and skips if absent.

---

## Common Mistakes — DO NOT REPEAT

| Mistake | Consequence | Correct |
|---------|-------------|---------|
| Writing trigger script from scratch instead of sourcing template | Misses workspace isolation, mode detection, logging | Use `source trigger_template.sh` (4 lines) |
| Forgetting to register in `oh-my-openagent.json` | `oh-my-opencode run -a <agent>` fails silently | Register in BOTH `opencode.json` AND `oh-my-openagent.json` |
| No workspace `opencode.json` with path restrictions | Agent can read/write anywhere on the system | Create per-agent `workspace/opencode.json` with `deny: ["**"]` |
| Missing workspace constraint in PROMPT.md | Agent writes files outside workspace | Include §3.4 sections: constraint, daily docs, mempalace |
| Not using `-d` flag in trigger | Per-agent opencode.json is never loaded | Already handled by `trigger_template.sh` — don't remove it |
| Overwriting `SUBWORKERS_SYSTEM.md` | Destroys existing subworker docs | Use `edit` tool to modify in place |
| Wrong agent ID in `prompt_append` or paths | Agent reads wrong PROMPT.md | Verify name matches exactly across all references |
| Not making trigger script executable | Plist runs but script fails silently | `chmod +x` the script |
| Skipping any of the 8 steps | Subworker silently broken | Run through all 8 steps in order |

## Verification Checklist

Before saying the subworker is ready, verify ALL of these:

```
[x] Step 1: opencode.json + oh-my-openagent.json registered (agents, categories, agent_display_names)
[x] Step 2: ~/.config/opencode/agents/<agent-id>.md exists with YAML frontmatter
[x] Step 3: subworkers/<agent-id>/PROMPT.md exists with workspace constraint + daily docs + mempalace
[x] Step 4: subworkers/scripts/trigger_<agent_name>.sh exists (sources trigger_template.sh) and is executable
[x] Step 5: subworkers/<agent-id>/workspace/ exists with per-agent opencode.json (deny: ["**"])
[x] Step 6: subworkers/plists/com.elia.<agent-id>.plist exists with correct PATH
[x] Step 7: SUBWORKERS_SYSTEM.md updated with new subworker
[x] Step 8: No .enabled flag (disabled by default — user enables manually)
```

Use this checklist in your response to confirm completion.
