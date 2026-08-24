---
name: elia-subworker-creator
description: >-
  Create a new autonomous subworker in the EliaAI system. A subworker is an AI agent with its own personality
  (stored in ~/.config/opencode/agents/), its own detailed prompt (in subworkers/<name>/PROMPT.md), and an
  entry in the subworker server config (subworkers/server/app/config/subworkers.json) which schedules and
  triggers it (Docker FastAPI on port 5656). This skill handles the FULL pipeline:
  opencode.json registration → agent personality file → PROMPT.md → subworkers.json declaration → SUBWORKERS_SYSTEM.md update.
  Use this whenever the user says "create a subworker", "add a new agent", "make a promoter", "new sub-worker",
  "add subworker", or any request to create a scheduled autonomous agent for the EliaAI ecosystem.
  DO NOT attempt to create subworkers without this skill — the procedure has many interdependencies and
  forgetting any one step will break the system.
---

# EliaAI Subworker Creator

## Why This Skill Exists

This session, multiple mistakes were made creating a subworker because the full procedure has 7 interdependent
steps across 4 different locations. Forgetting even one step (like registering in `opencode.json`) silently
breaks the subworker. This skill enforces the complete, verified pipeline.

## Main Agent Designation (Elia as a Subworker)

**New feature (August 2026):** Elia, the main agent, is now also a subworker — the **main** one. The logic and
code are identical to any other subworker; only the designation differs ("main" title or not).

- `subworkers/main-agent.json` = `{"name":"elia"}` designates the main agent (default `"elia"` if file missing).
- The subworker popup (ui_electron) shows a **MAIN badge** + **★/✕ edit button** to set/unset which agent is main.
- The subworker server (Docker FastAPI, port 5656) uses `workspace` + `prompt_file` from `subworkers.json`:
  the main agent gets **repo root** as workspace (`~/EliaAI`) instead of `subworkers/<name>/workspace/`.
- Elia's prompt lives at `subworkers/elia/PROMPT.md` (moved from repo root **without editing**) — the standard
  subworker location, referenced via `prompt_file: PROMPT.md` in `subworkers.json`.

**To create or designate a main agent:** same pipeline as any subworker, then ensure
`subworkers/main-agent.json` names it. Default is Elia — no action needed for the standard setup.

## Overview — The 6-Step Pipeline

```
opencode.json (register agent)
  → ~/.config/opencode/agents/<name>.md (personality + YAML frontmatter)
    → subworkers/<name>/PROMPT.md (detailed workflow prompt)
      → subworkers/server/app/config/subworkers.json (declare + schedule)
        → SUBWORKERS_SYSTEM.md (register in master doc)
          → enable via subworkers.json "enabled": true
```

Each step references files from previous steps. Doing them in order is critical.

**Runtime:** the Docker FastAPI server (`elia-subworker-srv`, port 5656) reads `subworkers.json`,
schedules each subworker, and triggers runs via `POST /trigger/{name}`. No trigger shell scripts,
no LaunchAgent plists — scheduling lives in the server.

---

## Step 0: READ FIRST — Understand the existing patterns

**Before creating anything**, read these reference files to understand the conventions:

```bash
cat ~/EliaAI/subworkers/SUBWORKERS_SYSTEM.md
cat ~/.config/opencode/opencode.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('agent',{}), indent=2))"
ls ~/.config/opencode/agents/
cat ~/EliaAI/subworkers/server/app/config/subworkers.json
```

Also read 1-2 existing subworkers to match the style:
```bash
cat ~/EliaAI/subworkers/your-agency-promoter/PROMPT.md
cat ~/EliaAI/subworkers/mirrorpay-telegram/PROMPT.md
```

---

## Step 1: Register agent in opencode.json

Add the agent entry to `opencode.json`. The `name` MUST match what you use everywhere else.

**Conventions:**
- `name`: kebab-case, descriptive (e.g., `your-brand-suppliers`, `mirrorpay-telegram`)
- `mode`: `primary` for scheduled autonomous agents, `subagent` for agents called by other agents
- `color`: hex color for terminal display
- `model`: `opencode/big-pickle` (default)
- `prompt_append`: ALWAYS start with `"**FIRST: Read ~/EliaAI/subworkers/<name>/PROMPT.md pour ton workflow complet.**"`

```python
import json

with open('~/.config/opencode/opencode.json') as f:
    data = json.load(f)

data['agent']['<name>'] = {
    "description": "<short description, 50-80 chars>",
    "mode": "primary",
    "color": "#<hex-color>",
    "model": "opencode/big-pickle",
    "prompt_append": "**FIRST: Read ~/EliaAI/subworkers/<name>/PROMPT.md pour ton workflow complet.**\n\nTu es <name>, <role description>."
}

with open('~/.config/opencode/opencode.json', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
```

**⚠️ Critical:** The `prompt_append` references the PROMPT.md path — make sure this path uses the EXACT same `<name>`.

---

## Step 2: Create agent personality file (~/.config/opencode/agents/<name>.md)

The agent personality file in `~/.config/opencode/agents/` serves as the agent's identity and is loaded
when the subworker triggers. ALWAYS include YAML frontmatter.

**YAML frontmatter fields:**
- `name`: Must match the name in opencode.json
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
name: <name>
slug: <name>
description: Short description
model: opencode/big-pickle
temperature: 0.3
mode: primary
---

# <Name> — Identity

Tu es un [role] spécialisé en [domain]. [1-2 sentence identity].

## Mission
[One sentence mission]

## Behavioral Rules
1. [Rule 1]
2. [Rule 2]

## Anti-Patterns
- ❌ [What to avoid]
```

**Path:** `~/.config/opencode/agents/<name>.md`

---

## Step 3: Create PROMPT.md (subworkers/<name>/PROMPT.md)

Create the detailed workflow document. This is the MAIN file the agent reads at runtime.

**Location:** `~/EliaAI/subworkers/<name>/PROMPT.md`

**Required sections:**
1. **SOURCE DE VÉRITÉ** — List all personality files to read first (from `~/.config/opencode/agents/`)
2. **MISSION** — What this subworker does
3. **RUN CYCLE** — How long each run takes (max duration)
4. **WORKFLOW** — Step-by-step instructions
5. **OUTILS** — What tools they can use (Discord channels, Jira, etc.)
6. **REPORTING** — How to report results (Discord format)
7. **LIMITATIONS** — What they must NOT do

**⚠️ NEVER include a personality.md in the subworker folder.** Personalities go in
`~/.config/opencode/agents/` only. The PROMPT.md references those files in SOURCE DE VÉRITÉ.

**Naming conventions:**
- Subworker folder name = agent name (kebab-case)
- `PROMPT.md` inside (not `prompt.md`, not `instructions.md`)

---

## Step 4: Declare the subworker in subworkers.json (server schedule)

Add an entry to `~/EliaAI/subworkers/server/app/config/subworkers.json`. The Docker
FastAPI server (`elia-subworker-srv`, port 5656) reads this file, schedules the subworker, and
runs it with `opencode run -d <workspace> -a <agent_id> <prompt_file>`.

**Required fields per entry:**
- `name`: must match the agent name (kebab-case)
- `enabled`: `true`/`false` (serves as the on/off switch — no `.enabled` flag file anymore)
- `schedule`: `{"type": "interval", "hours": [...], "minute": 0}` or a cron expression
- `agent_id`: the opencode agent name (same as `name`)
- `workspace`: working directory for the run. The **main agent** (`elia`) gets repo root
  `~/EliaAI`; other subworkers use `~/EliaAI/subworkers/<name>/workspace/`
- `prompt_file`: `PROMPT.md` (path relative to workspace)
- `timeout_minutes`, `max_retries`, `mcp_servers`, `notify_discord`: optional per subworker

**Template:**
```json
{
  "name": "<name>",
  "enabled": false,
  "schedule": { "type": "interval", "hours": [8], "minute": 0 },
  "agent_id": "<name>",
  "workspace": "~/EliaAI/subworkers/<name>/workspace",
  "prompt_file": "PROMPT.md",
  "timeout_minutes": 30,
  "max_retries": 3,
  "mcp_servers": [],
  "notify_discord": false
}
```

**Trigger:** `POST http://127.0.0.1:5656/trigger/<name>` (the server replaces the old
`trigger_<name>.sh` scripts). Status via `GET /status`, run logs via the server.

---

## Step 5: Enable the subworker (subworkers.json "enabled": true)

New subworkers are created with `"enabled": false`. To activate one, set `"enabled": true` in
`subworkers.json` and restart the server (`docker compose restart` in `subworkers/server/`).
The server's scheduler starts the subworker on its schedule; manual trigger stays
`POST /trigger/<name>` regardless of the schedule.

## Step 6: Update SUBWORKERS_SYSTEM.md

Edit `~/EliaAI/subworkers/SUBWORKERS_SYSTEM.md` to register the new subworker:

1. **Key Differences table** — Add a new column for the subworker with: Business, Focus, Platforms, Interval, Hours, Max output
2. **Directory Structure** — Add the new folder and log entries

**⚠️ NEVER overwrite SUBWORKERS_SYSTEM.md — always edit it in place.** Use the `edit` tool
to add insertions to the existing sections.

---

## Step 7: Verify the server picks it up

The subworker is disabled by default (`"enabled": false`). After declaring it in `subworkers.json`:

```bash
# Server must be running (Docker container elia-subworker-srv, port 5656)
docker ps | grep elia-subworker-srv
curl -s http://127.0.0.1:5656/status | python3 -m json.tool | grep -A5 '"<name>"' || true
```

Only set `"enabled": true` (and restart the server) if the user explicitly asks to activate
the subworker. Manual trigger works regardless of the schedule:
`curl -s -X POST http://127.0.0.1:5656/trigger/<name>`

---

## Common Mistakes — DO NOT REPEAT

| Mistake | Consequence | Correct |
|---------|-------------|---------|
| Creating `personality.md` in subworker/ folder | Wrong location, agent won't find it | Put in `~/.config/opencode/agents/<name>.md` |
| Forgetting to register in `opencode.json` | `opencode run -a <name>` fails silently | Register BEFORE creating other files |
| Overwriting `SUBWORKERS_SYSTEM.md` | Destroys existing subworker docs | Use `edit` tool to modify in place |
| Wrong agent name in `prompt_append` | Agent reads wrong PROMPT.md | Verify name matches exactly |
| Not declaring in `subworkers.json` | Server never schedules the subworker | Add entry with `workspace` + `prompt_file` |
| Referencing personality.md in PROMPT.md | File doesn't exist at that path | Reference `~/.config/opencode/agents/<name>.md` |
| Skipping any of the 7 steps | Subworker silently broken | Run through all 7 steps in order |
| Creating agent file in subworkers/ | Not registered in opencode.json | Agent files go in `~/.config/opencode/agents/` |
| Using `permissions` (plural) in workspace/opencode.json | ConfigInvalidError, agent won't launch | Use `permission` (singular, tool-level) or omit entirely |
| Forgetting workspace/opencode.json has no path-level security | Agent CAN read/write outside workspace | Workspace isolation = `-d` flag + PROMPT.md instruction, not config |
| Using old `trigger_<name>.sh` / plist pipeline | Duplicates scheduling outside the server | Declare in `subworkers.json`; server schedules + triggers |

## Verification Checklist

Before saying the subworker is ready, verify ALL of these:

```
[x] Step 1: opencode.json has agent entry with prompt_append
[x] Step 2: ~/.config/opencode/agents/<name>.md exists with YAML frontmatter
[x] Step 3: subworkers/<name>/PROMPT.md exists
[x] Step 4: subworkers/server/app/config/subworkers.json has the entry (workspace + prompt_file + schedule)
[x] Step 5: SUBWORKERS_SYSTEM.md updated with new subworker
[x] Step 6: subworkers.json "enabled": false (disabled by default — user enables manually)
[x] Step 7: Docker server elia-subworker-srv is running (port 5656) and /status lists the subworker
```

**Config validation:** Before declaring a subworker ready, verify the entry with the server:

```bash
# Server must be running (Docker container elia-subworker-srv, port 5656)
docker ps | grep elia-subworker-srv
curl -s http://127.0.0.1:5656/status | python3 -m json.tool | grep -A5 '"<name>"' || true
# Manual trigger
curl -s -X POST http://127.0.0.1:5656/trigger/<name>
```

Use this checklist in your response to confirm completion.
