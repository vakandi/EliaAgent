---
name: elia-subworker-creator
description: >-
  Create a new autonomous subworker in the EliaAI system. A subworker is an AI agent with its own personality
  (stored in ~/.config/opencode/agents/), its own detailed prompt (in subworkers/<name>/PROMPT.md), a trigger
  script, and an optional LaunchAgent plist for scheduling. This skill handles the FULL pipeline:
  opencode.json registration → agent personality file → PROMPT.md → trigger script → plist → SUBWORKERS_SYSTEM.md update.
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

## Overview — The 8-Step Pipeline

```
opencode.json (register agent)
  → ~/.config/opencode/agents/<name>.md (personality + YAML frontmatter)
    → subworkers/<name>/PROMPT.md (detailed workflow prompt)
      → subworkers/scripts/trigger_<name>.sh → sources trigger_template.sh
        → subworkers/plists/com.elia.<name>.plist (LaunchAgent)
          → SUBWORKERS_SYSTEM.md (register in master doc)
            → subworkers/<name>/.enabled (disabled by default)
              → workspace/ dir auto-created with -d isolation
```

Each step references files from previous steps. Doing them in order is critical.

---

## Step 0: READ FIRST — Understand the existing patterns

**Before creating anything**, read these reference files to understand the conventions:

```bash
cat /path/to/subworkers/SUBWORKERS_SYSTEM.md
cat /path/to/opencode-config/opencode.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('agent',{}), indent=2))"
ls /path/to/agents/
ls /path/to/subworkers/scripts/
ls /path/to/subworkers/plists/
```

Also read 1-2 existing subworkers to match the style:
```bash
cat /path/to/subworkers/youragency-promoter/PROMPT.md
cat /path/to/subworkers/yourapp-telegram/PROMPT.md
```

---

## Step 1: Register agent in opencode.json

Add the agent entry to `opencode.json`. The `name` MUST match what you use everywhere else.

**Conventions:**
- `name`: kebab-case, descriptive (e.g., `YourBrand-suppliers`, `yourapp-telegram`)
- `mode`: `primary` for scheduled autonomous agents, `subagent` for agents called by other agents
- `color`: hex color for terminal display
- `model`: `opencode/big-pickle` (default)
- `prompt_append`: ALWAYS start with `"**FIRST: Read /path/to/subworkers/<name>/PROMPT.md pour ton workflow complet.**"`

```python
import json

with open('/path/to/opencode-config/opencode.json') as f:
    data = json.load(f)

data['agent']['<name>'] = {
    "description": "<short description, 50-80 chars>",
    "mode": "primary",
    "color": "#<hex-color>",
    "model": "opencode/big-pickle",
    "prompt_append": "**FIRST: Read /path/to/subworkers/<name>/PROMPT.md pour ton workflow complet.**\n\nTu es <name>, <role description>."
}

with open('/path/to/opencode-config/opencode.json', 'w') as f:
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

**Path:** `/path/to/agents/<name>.md`

---

## Step 3: Create PROMPT.md (subworkers/<name>/PROMPT.md)

Create the detailed workflow document. This is the MAIN file the agent reads at runtime.

**Location:** `/path/to/subworkers/<name>/PROMPT.md`

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

## Step 4: Create trigger script (subworkers/scripts/trigger_<name>.sh)

The trigger script sources `trigger_template.sh`, which handles logging, PATH, .enabled gating,
PROMPT.md loading, workspace isolation, loop mode, and proxy detection. You just set `AGENT_NAME`.

**Template:**
```bash
#!/bin/zsh
AGENT_NAME="<underscore_name>"
source /path/to/subworkers/scripts/trigger_template.sh
```

Replace `<underscore_name>` with the agent name in underscore format (e.g., `yourapp_seo`, `YourBrand_suppliers`).
The template derives the directory name and agent ID from this value (underscore → hyphen).

**Workspace isolation:** The template sets `WORKSPACE_DIR="$SUBWORKER_DIR/workspace"` and passes
`-d "$WORKSPACE_DIR"` to `oh-my-opencode run`. This constrains the agent's working directory.

**Optional `workspace/opencode.json`:** A per-agent config override. Useful for model overrides.
Create it only if needed:
```json
{
  "agent": {
    "<agent-id>": {
      "description": "Per-agent config for <agent-id>",
      "mode": "primary"
    }
  }
}
```
Do NOT use `permissions` (plural) — the OpenCode schema only supports `permission` (singular, tool-level
allow/deny/ask, no path-level globs). The workspace dir + PROMPT.md instruction are the isolation mechanism.

**Make the script executable:**
```bash
chmod +x /path/to/subworkers/scripts/trigger_<name>.sh
```

---

## Step 5: Create LaunchAgent plist (subworkers/plists/com.elia.<name>.plist)

Creates a scheduled LaunchAgent. The plist runs the trigger script at the specified interval.

**Template:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.elia.<name></string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>/path/to/subworkers/scripts/trigger_<name>.sh</string>
    </array>

    <key>RunAtLoad</key>
    <false/>

    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>8</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>~/user</string>
    </dict>

    <key>WorkingDirectory</key>
    <string>/path/to/EliaAI</string>

    <key>StandardOutPath</key>
    <string>/path/to/subworkers/logs/<name>.log</string>

    <key>StandardErrorPath</key>
    <string>/path/to/subworkers/logs/<name>.log</string>
</dict>
</plist>
```

---

## Step 6: Update SUBWORKERS_SYSTEM.md

Edit `/path/to/subworkers/SUBWORKERS_SYSTEM.md` to register the new subworker:

1. **Key Differences table** — Add a new column for the subworker with: Business, Focus, Platforms, Interval, Hours, Max output
2. **Directory Structure** — Add the new folder, script, plist, and log entries

**⚠️ NEVER overwrite SUBWORKERS_SYSTEM.md — always edit it in place.** Use the `edit` tool
to add insertions to the existing sections.

---

## Step 7: Create .enabled flag (disabled by default)

The subworker is disabled by default. To enable it later, create the `.enabled` flag:

```bash
# Disabled by default (skip this in the initial creation)
# touch /path/to/subworkers/<name>/.enabled
```

Only create `.enabled` if the user explicitly asks to activate the subworker. By default,
the trigger script checks for `.enabled` and skips if absent.

---

## Common Mistakes — DO NOT REPEAT

| Mistake | Consequence | Correct |
|---------|-------------|---------|
| Creating `personality.md` in subworker/ folder | Wrong location, agent won't find it | Put in `~/.config/opencode/agents/<name>.md` |
| Forgetting to register in `opencode.json` | `oh-my-opencode run -a <name>` fails silently | Register BEFORE creating other files |
| Overwriting `SUBWORKERS_SYSTEM.md` | Destroys existing subworker docs | Use `edit` tool to modify in place |
| Wrong agent name in `prompt_append` | Agent reads wrong PROMPT.md | Verify name matches exactly |
| Not making trigger script executable | Plist runs but script fails silently | `chmod +x` the script |
| Referencing personality.md in PROMPT.md | File doesn't exist at that path | Reference `~/.config/opencode/agents/<name>.md` |
| Skipping any of the 7 steps | Subworker silently broken | Run through all 7 steps in order |
| Creating agent file in subworkers/ | Not registered in opencode.json | Agent files go in `~/.config/opencode/agents/` |
| Using `permissions` (plural) in workspace/opencode.json | ConfigInvalidError, agent won't launch | Use `permission` (singular, tool-level) or omit entirely |
| Forgetting workspace/opencode.json has no path-level security | Agent CAN read/write outside workspace | Workspace isolation = `-d` flag + PROMPT.md instruction, not config |

## Verification Checklist

Before saying the subworker is ready, verify ALL of these:

```
[x] Step 1: opencode.json has agent entry with prompt_append
[x] Step 2: ~/.config/opencode/agents/<name>.md exists with YAML frontmatter
[x] Step 3: subworkers/<name>/PROMPT.md exists
[x] Step 4: subworkers/scripts/trigger_<name>.sh exists, is executable, sources trigger_template.sh
[x] Step 5: subworkers/plists/com.elia.<name>.plist exists
[x] Step 6: SUBWORKERS_SYSTEM.md updated with new subworker
[x] Step 7: No .enabled flag (disabled by default — user enables manually)
[x] Step 8: subworkers/<name>/workspace/ dir exists (auto-created by trigger_template.sh)
```

**Config validation:** Before declaring a subworker ready, run a dry trigger to confirm the
`workspace/opencode.json` (if present) has no invalid keys. The `permission` key (singular) is
tool-level only (allow/deny/ask per tool) — path-level globs are not supported.

```bash
# Dry test (set .enabled first, then remove it)
touch /path/to/subworkers/<name>/.enabled
bash /path/to/subworkers/scripts/trigger_<name>.sh 2>&1 &
sleep 5 && kill %1 2>/dev/null
# Check the run log for ConfigInvalidError
cat /path/to/subworkers/logs/runs/<underscore_name>/$(ls -t /path/to/subworkers/logs/runs/<underscore_name>/ | head -1)
```

Use this checklist in your response to confirm completion.
