# Investigation [[../../wiki/docs/Sessions|Report]]: /ulw-loop Command in OhMyOpenCode

**Date:** April 11, 2026  
**Investigated by:** Gilfoyle  
**[[../../wiki/concepts/AI-Automation#tasks|Task]]:** Running `/ulw-loop` in terminal CLI  

---

## Question Asked

> Check the [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Git-Version-Control|Git]]-Version-Control|GitHub]].com/code-yeongyu/oh-my-openagent releases on the last few weeks to check if they fix the logs timestamps and logs of [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] that were "fucked" if we were to [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] a ultra loop /ulw-loop in the terminal like this:
> ```
> [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] --[[../../wiki/concepts/AI-Automation|Agent]] [[../../wiki/people/Elia|Elia]] "/ulw-loop say your name" --attach
> ```
> Just [[../../wiki/concepts/Prompt-Engineering|VERIFY]] if the devs changed something about that, check each commit of each release.

---

## Command Syntax Investigation

### ✅ Working Commands

```bash
# Basic ULW loop
[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] --[[../../wiki/concepts/AI-Automation|Agent]] [[../../wiki/people/Elia|Elia]] "/ulw-loop say your name" --attach

# With completion promise
[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] --[[../../wiki/concepts/AI-Automation|Agent]] [[../../wiki/people/Elia|Elia]] "/ulw-loop your [[../../wiki/concepts/AI-Automation#tasks|Task]] --completion-promise DONE" --attach

# With max iterations (safer)
[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] --[[../../wiki/concepts/AI-Automation|Agent]] [[../../wiki/people/Elia|Elia]] "/ulw-loop your [[../../wiki/concepts/AI-Automation#tasks|Task]] --max-iterations 10" --attach
```

### ❌ Non-Working Commands

```bash
# Missing --attach causes issues
[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] --[[../../wiki/concepts/AI-Automation|Agent]] [[../../wiki/people/Elia|Elia]] "/ulw-loop say your name"

# Using --model flag (not needed with oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]])
[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] --model [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/big-pickle --[[../../wiki/concepts/AI-Automation|Agent]] [[../../wiki/people/Elia|Elia]] "/ulw-loop say your name" --attach
```

---

## Recent Releases Checked (March-April 2026)

### v3.16.0 (April 8, 2026)

| Commit | Description |
|--------|-------------|
| `bbbbf68` | fix(ralph-loop): update template to reflect 500 iteration cap |
| `0cb938e` | fix(boulder): count only top-level checkboxes in simple-mode plan progress |
| `917ae4d` | fix(delegate-[[../../wiki/concepts/AI-Automation#tasks|Task]]): strip ZWSP from [[../../wiki/concepts/AI-Automation|Agent]] names on background launch |
| `0479693` | fix(oauth): wire post-[[../../wiki/concepts/API-Integration|Request]] 401/403 handler into skill-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] |
| `14f4390` | fix(ultrawork): [[../../wiki/concepts/File-Management|Add]] iteration cap to prevent infinite loops |
| `359f741` | fix(keyword-detector): narrow ULW auto-start to leading keyword only |

### v3.15.0 (April 5, 2026)

| Commit | Description |
|--------|-------------|
| `d490b4d` | fix(ralph-loop): harden Oracle VERIFIED detection |
| `c3fe0ae` | fix(background): propagate variant in parent notifications |

### v3.14.0 (March 30, 2026)

Focus: [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] OAuth improvements, background [[../../wiki/concepts/AI-Automation#tasks|Task]] fixes.

### v3.13.0 (March 22, 2026)

| Commit | Description |
|--------|-------------|
| `717c976` | fix(keyword-detector): start ralph-loop when ulw keyword detected |

### v3.12.0 (March 15, 2026)

| Commit | Description |
|--------|-------------|
| `d3dbb497` | Fix Oracle invocation ([[../../wiki/concepts/AI-Automation#tasks|Task]] system now defaults to true) |

### v3.11.0 (March 7, 2026)

**Major Change:** ULW-Loop now requires Oracle verification before completing any [[../../wiki/concepts/AI-Automation#tasks|Task]].

---

## Known Issues (Still Open)

| [[../../wiki/systems/Jira-Tickets-Index|Issue]] # | Status | Description |
|---------|--------|-------------|
| #2489 | OPEN | ULW-loop sometimes doesn't stop, even when [[../../wiki/concepts/AI-Automation#tasks|Task]] is completed |
| #1921 | OPEN | [[../../wiki/concepts/AI-Automation|Agent]] can bypass Ralph/ULW loop by immediately outputting completion promise without doing work |
| #3113 | OPEN | ULW always automatically stops and does not continue execution |
| #2526 | OPEN | Stuck during planning phase |
| #3081 | OPEN | Variant field silently dropped in continuation paths |
| **Timestamps in terminal** | **NOT FIXED** | No timestamp in terminal output for ULW-loop |

---

## What Was Fixed

| [[../../wiki/systems/Jira-Tickets-Index|Issue]] | Status | Fixed In |
|-------|--------|---------|
| #622 | FIXED | Iteration counter always 1 |
| #1233 | FIXED | Completion promise tag not detected |
| #900 | FIXED | Argument parsing ignored |
| #2489 (partial) | PARTIAL | Semantic completion detection added |
| Race conditions | FIXED | Completion detection reliability |

---

## Conclusion

### ❌ Timestamp [[../../wiki/systems/Jira-Tickets-Index|Issue]]: NOT FIXED

The oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] developers have **NOT** added timestamps to terminal output for ULW-loop execution. This is not a priority for them.

### ❌ Log Visibility: NOT IMPROVED

Running ulw-loop without `--attach` flag causes:
- No visible timestamps
- No iteration counter in terminal
- Stuck in infinite loop behavior

### ✅ Recommendation: Use `--attach` Flag

```bash
# Mandatory for proper execution
[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] --[[../../wiki/concepts/AI-Automation|Agent]] [[../../wiki/people/Elia|Elia]] "/ulw-loop [[../../wiki/concepts/AI-Automation#tasks|Task]]" --attach
```

### ✅ Alternative: Use oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] Wrapper

```bash
# Via oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a [[../../wiki/people/Elia|Elia]] "/ulw-loop [[../../wiki/concepts/AI-Automation#tasks|Task]]"

# Via EliaAI [[../../wiki/concepts/Marketing-Concepts|Script]]
/Users/vakandi/EliaAI/scripts/trigger_opencode_interactive.sh
```

---

## References

- [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Git-Version-Control|Git]]-Version-Control|GitHub]]: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Git-Version-Control|Git]]-Version-Control|GitHub]].com/code-yeongyu/oh-my-openagent
- Releases: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Git-Version-Control|Git]]-Version-Control|GitHub]].com/code-yeongyu/oh-my-openagent/releases
- Latest: v3.16.0 (April 8, 2026)