---
name: personality-subworker-edit
description: "Edit a subworker's personality file in the EliaAI subworker system. Takes a subworker name + edit request, finds the personality at ~/.config/opencode/agents/<name>.md, reads the current content, and applies MINIMAL targeted edits — the personality sibling of the prompts-subworker-edit skill (which edits PROMPT.md). Use this skill whenever the user says 'edit the personality for X', 'change X's personality', 'update X's agent file', 'modify X's character', 'fix the agent personality for X', 'make X more aggressive/calmer/stricter', or any request to change HOW a subworker behaves or WHO it is (identity, mission, tone, behavioral rules, anti-patterns). Also trigger when the user says 'agent behavior file', 'personality file', or references editing ~/.config/opencode/agents/. TRIGGER PROACTIVELY on any mention of editing subworker personalities — this is the file loaded automatically by oh-my-opencode via the -a flag, so WHO the agent is belongs here, while WHAT it does belongs in the PROMPT.md (see prompts-subworker-edit)."
---

# Subworker Personality Editor

Edit a subworker's personality file (`~/.config/opencode/agents/<name>.md`) with minimal, targeted changes. Never rewrite the whole file. Two modes: **Edit** (surgical, default) and **Enhance** (deep improvement, only when the user asks to "enhance"/"améliorer"/"make better").

## Workspace

All personality files live in:
```
~/.config/opencode/agents/<agent-id>.md
```

Available subworker personalities (matching `subworkers/<name>/`):
- `your-saas-community-organic`
- `your-saas-seo`
- `mirrorpay-telegram`
- `reddit-saas-scraper`
- `refund-hunter`
- `your-telecom-community-organic`
- `your-telecom-seo`
- `vcam-community-organic`
- `vcam-seo`

Name mismatches to know (subworker → personality file):
- `tiktok-content` → `tiktok-youtube-auto.md`
- `your-agency-promoter` → search for the closest match (e.g. `your-agency-agency.md`) and confirm with the user
- `your-brand-promoter`, `your-brand-suppliers`, `tempack-dev` → no dedicated personality file; the skill should say so and suggest creating one or editing the shared `your-brand.md` / `your-agency-agency.md` with confirmation

If the user says a name that doesn't match exactly, suggest the closest match.

## Personality File Structure (Critical)

Every personality file has TWO zones, separated by the YAML frontmatter block (`---` ... `---`):

### CONFIG ZONE — YAML Frontmatter (NEVER EDIT unless explicitly requested)

```yaml
---
name: <agent-id>          # ← registration key, NEVER change
slug: <agent-id>          # ← registration key, NEVER change
description: <one-liner>
model: opencode/big-pickle
temperature: 0.3
mode: all
tools: { read: true, ... }
permissions: { bash: {...}, edit: {...}, file: {...} }
---
```

This is **system configuration**, not personality:
- `name` / `slug` are registration keys — changing them breaks the trigger/plist/registration. **Refuse** any request to change these.
- `model`, `temperature` affect quality and cost — only change with explicit user request, and confirm the choice.
- `permissions` are **security-sensitive** — editing them can give an agent filesystem/bash access it shouldn't have. Only change with explicit user request, and warn about the implications. Never loosen permissions "to make the agent more autonomous" without asking.
- `tools` toggles — same: confirm before changing.

### PERSONALITY ZONE — Body (what the user edits)

Everything after the closing `---` is the agent's actual identity and behavior. Typical sections (vary per agent — read the file first):
- `# <Agent Name> — Identity` — Who the agent is
- `## Mission` — Why it exists
- `## Behavioral Rules` — Numbered rules (the core editable content)
- `## Anti-Patterns` — What to never do
- `## Reporting` — Where/how it reports

There is **no universal boilerplate** — each personality file is unique. Read the whole file before editing.

## Why personality edits matter (the "why")

The personality file is loaded automatically by oh-my-opencode on every run (via the `-a` flag), **even if the agent forgets to read its PROMPT.md**. It is the "even if he forgets" insurance:
- **PROMPT.md** = WHAT the agent does (workflow, phases, tools, reporting format) → edit with `prompts-subworker-edit`
- **Personality** = WHO the agent is (identity, values, tone, behavioral rules, anti-patterns) → edit with this skill

Therefore every rule you write in a personality must be **self-sufficient**: understandable and actionable WITHOUT reading the PROMPT.md. A rule that references "see Phase 4 of the PROMPT.md" is useless if the agent never reads it. Spell out the rule fully, inline, including the concrete commands if needed.

When a personality rule changes behavior, check whether the matching PROMPT.md section should stay in sync — and tell the user ("this also exists in PROMPT.md, want me to update it too?"). Do NOT edit the PROMPT.md yourself in this skill — that's `prompts-subworker-edit`'s job.

## Edit Mode (default)

### Step 1: Read the current personality file

```
Read ~/.config/opencode/agents/<name>.md
```

### Step 2: Identify what to change

Map the user's request to specific sections:

| User says | Target section |
|-----------|---------------|
| "make him more aggressive/stricter/calmer" | `## Behavioral Rules` (tone) + `## Anti-Patterns` |
| "change his identity to..." | `# <Name> — Identity` |
| "add a rule about X" | `## Behavioral Rules` |
| "forbid doing Y" | `## Anti-Patterns` |
| "change his mission to..." | `## Mission` |
| "make him prioritize Z" | `## Behavioral Rules` (add a numbered rule) |

### Step 3: Apply MINIMAL edit

Use the `edit` tool with the smallest possible `oldString` → `newString` change. Surgical precision — change only what the user asked for.

**DO:**
- Add one numbered rule to `## Behavioral Rules`
- Add one line to `## Anti-Patterns`
- Replace one sentence in the Identity
- Tighten an existing rule's wording while keeping its intent

**DON'T:**
- Rewrite the entire file
- Reformat existing content
- "Improve" wording the user didn't ask to change
- Add sections that weren't requested
- Touch the YAML frontmatter

### Step 4: Verify the edit

After editing, read the file again and confirm:
1. The frontmatter block is unchanged
2. Only the intended section was modified
3. The edit is self-sufficient (no dangling reference to PROMPT.md sections)
4. The language matches the rest of the file

### Step 5: Show the user what changed

Present a brief before/after of the specific lines that changed. Don't dump the whole file.

## Enhance Mode (only when the user asks to "enhance"/"améliorer")

When the user asks to make the personality deeper or better (not just one change), run a deeper pass — the personality equivalent of the prompt-enhancer:

1. **Read the full file** + skim the matching PROMPT.md and the run logs (`~/EliaAI/subworkers/logs/runs/<name>/`) to ground improvements in real behavior.
2. **Improve on these axes** (only what's relevant — don't bloat):
   - **Precision** — make vague rules concrete (add numbers, thresholds, conditions)
   - **Self-sufficiency** — rewrite rules that reference the PROMPT.md so they stand alone
   - **Anti-patterns** — add the specific mistakes the agent actually makes (from run logs)
   - **Edge cases** — cover ambiguous situations (blocked sites, empty results, repeated failures)
   - **Tone consistency** — make the personality voice coherent with its mission
3. **Respect the file's core identity** — never change who the agent IS, only sharpen HOW it behaves. The mission/identity stay the same unless the user says otherwise.
4. **Keep it lean** — remove lines that don't pull their weight; don't add sections that will never be used.
5. **Append an `## Enhancement Notes` section at the end** listing what changed and why (like the prompt-enhancer does).

## Language

Personality files are mostly in **French**. Keep the file's language. If the user gives a request in English, translate the edit content to the file's language.

## Edge Cases

- **Unknown subworker name**: list available personalities and ask which one they mean
- **Ambiguous request** ("make him better"): ask what specifically to change, or offer Enhance Mode
- **Edit to frontmatter** (`name`, `slug`): refuse, explain it breaks registration
- **Model/temperature change**: confirm the exact model with the user before applying
- **Permission change**: warn about security implications before applying
- **Rule that also exists in PROMPT.md**: edit the personality (self-sufficient version) then tell the user the PROMPT.md should be synced — don't edit it yourself
- **No personality file exists** for the subworker: say so and offer to create one from the PROMPT.md (confirm first)
