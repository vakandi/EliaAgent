---
name: prompts-subworker-edit
description: "Edit a subworker's PROMPT.md in the EliaAI subworker system. Takes a subworker name + edit request, finds the PROMPT.md at ~/EliaAI/subworkers/<name>/PROMPT.md, reads the current content, and applies MINIMAL targeted edits. Use this skill whenever the user says 'edit the subworker prompt for X', 'change the PROMPT.md for X', 'update X's instructions', 'modify X's prompt', 'fix the subworker prompt for X', or any request to edit a subworker's task instructions. Also trigger when the user says 'subworker prompt', 'PROMPT.md edit', or references changing a subworker's behavior, identity, workflow, tools, or reporting format. The workspace is always ~/EliaAI/subworkers/. TRIGGER PROACTIVELY on any mention of editing subworker prompts."
---

# Subworker PROMPT.md Editor

Edit a subworker's PROMPT.md with minimal, targeted changes. Never rewrite the whole file.

## Workspace

All subworkers live in:
```
~/EliaAI/subworkers/<agent-id>/PROMPT.md
```

Available subworkers:
- `your-brand-promoter`
- `your-brand-suppliers`
- `your-agency-promoter`
- `your-saas-community-organic`
- `your-saas-seo`
- `mirrorpay-telegram`
- `reddit-saas-scraper`
- `your-telecom-community-organic`
- `your-telecom-seo`
- `tempack-dev`
- `tiktok-content`

If the user says a name that doesn't match exactly, suggest the closest match.

## PROMPT.md Structure (Critical)

Every PROMPT.md has two zones:

### SACRED BOILERPLATE (Lines 1-24, NEVER EDIT)

```markdown
# <Agent Name> - PROMPT.md

## Workspace Constraint
You MUST only read and write files inside your `workspace/` folder:
`~/EliaAI/subworkers/<name>/workspace/`
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

**This section is identical across all subworkers** (except the agent name/path). If the user asks to edit something in this section, REFUSE and explain why — it's system infrastructure, not agent behavior.

### EDITABLE ZONE (Line 25+, the domain-specific sections)

Everything after the Mempalace section is the agent's actual behavior definition. This is what the user edits. Typical sections include:

- `## Identity` — Who the agent is
- `## Platforms Cibles` — Target platforms table
- `## Outils Disponibles` — Available tools
- `## Canaux de Reporting` — Discord/WhatsApp channels
- `## Workflow` — Step-by-step flow
- `## Questions Découverte` — Discovery questions
- `## Lead Scoring` — Scoring criteria
- `## Warm-Up Protocol` — Engagement pacing
- `## Actions Interdites` — Forbidden actions
- `## Format Report` — Report template
- `## Commandes Reporting` — Discord/WhatsApp send commands

Sections vary per agent. Read the file first to see what exists.

## Edit Workflow

### Step 1: Read the current PROMPT.md

```
Read ~/EliaAI/subworkers/<name>/PROMPT.md
```

### Step 2: Identify what to change

Map the user's request to specific sections. Examples:

| User says | Target section |
|-----------|---------------|
| "change the identity to..." | `## Identity` |
| "add LinkedIn as a platform" | `## Platforms Cibles` |
| "change the Discord channel to 12345" | `## Canaux de Reporting` + `## Commandes Reporting` |
| "add a new tool" | `## Outils Disponibles` |
| "forbid sending DMs on weekends" | `## Actions Interdites` |
| "change the report format to..." | `## Format Report` |
| "update the workflow to include a research step" | `## Workflow` |

### Step 3: Apply MINIMAL edit

Use the `edit` tool with the smallest possible `oldString` → `newString` change. The goal is surgical precision — change only what the user asked for.

**DO:**
- Change a single table row
- Add one line to a list
- Replace one section's content while keeping the rest
- Update a channel ID in both the table AND the command

**DON'T:**
- Rewrite the entire file
- Reformat existing content
- "Improve" wording the user didn't ask to change
- Add sections that weren't requested
- Change the boilerplate block

### Step 4: Verify the edit

After editing, read the file again and confirm:
1. The boilerplate (lines 1-24) is unchanged
2. Only the intended section was modified
3. The edit is consistent (e.g., if you changed a Discord channel ID in the table, also update it in the reporting command)

### Step 5: Show the user what changed

Present a brief before/after of the specific lines that changed. Don't dump the whole file.

## Language

PROMPT.md content is in **French**. Keep all edits in French. If the user gives an edit request in English, translate the content to French in the edit.

## Edge Cases

- **Unknown subworker name**: List available names and ask which one they mean
- **Ambiguous request** ("make it better"): Ask what specifically to change
- **Edit to boilerplate**: Refuse with explanation
- **Multiple sections affected**: Apply each edit independently, verify all after
- **User wants to add a whole new section**: Add it at the end, before the reporting section if one exists
