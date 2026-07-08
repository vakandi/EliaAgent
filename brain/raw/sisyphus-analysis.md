# Sisyphus vs [[../../wiki/people/Elia|Elia]] Analysis

**Generated**: 2026-04-10  
**Purpose**: Understand if "[[../../wiki/people/Elia|Elia]]" can have the same subagent capabilities as "sisyphus"

---

## What Makes Sisyphus Special

### 1. Code vs Config Pattern

**Sisyphus is NOT a config-based [[../../wiki/concepts/AI-Automation|Agent]]** - it's CODE that builds prompts dynamically:

```typescript
// From src/agents/sisyphus.ts
function buildDynamicSisyphusPrompt(
  model: string,
  availableAgents: AvailableAgent[],
  availableTools: AvailableTool[] = [],
  availableSkills: AvailableSkill[] = [],
  availableCategories: AvailableCategory[] = [],
  useTaskSystem = false,
): string {
  // Dynamically composes [[../../wiki/concepts/Prompt-Engineering|PROMPT]] from modular sections
  const keyTriggers = buildKeyTriggersSection(availableAgents, availableSkills);
  const toolSelection = buildToolSelectionTable(availableAgents, availableTools, availableSkills);
  const exploreSection = buildExploreSection(availableAgents);
  const categorySkillsGuide = buildCategorySkillsDelegationGuide(availableCategories, availableSkills);
  // ... 10+ more sections
  return `${agentIdentity}\n<Role>...</Role><Behavior_Instructions>...`;
}
```

**Key Difference**:
| Aspect | Config-Based [[../../wiki/concepts/AI-Automation|Agent]] | Sisyphus (Code-Based) |
|--------|-------------------|----------------------|
| [[../../wiki/concepts/Prompt-Engineering|PROMPT]] | Static [[../../wiki/concepts/API-Integration|JSON]] string | Composed from 15+ modular functions |
| Adaptability | Fixed | Conditional sections based on model type |
| Testability | Hard | Each section tested in isolation |
| Extensibility | Edit [[../../wiki/concepts/API-Integration|JSON]] | Add function to builder |

### 2. Special Capabilities

Sisyphus has unique features that config agents don't:

1. **Intent Gate (Phase 0)**: Analyzes true user intent before acting
2. **Intent Verbalization**: Announces routing decision out loud
3. **Model-Specific Enhancements**: Different prompts for [[../../wiki/people/GPT|GPT]] vs [[../../wiki/people/Gemini|Gemini]] vs [[../../wiki/people/GPT|GPT]]-5.4
4. **Parallel Delegation**: Fire multiple subagents in parallel by default
5. **Session Continuity**: Uses session_id to continue, never starts fresh
6. **Evidence Requirements**: Won't claim done without verification (lsp_diagnostics, build)

### 3. [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|Built]]-in Subagent Access

Sisyphus automatically has access to:
- **explore**: Codebase context [[../../wiki/channels/Google|Search]]
- **librarian**: External [[../../wiki/HOME|Docs]]/OSS [[../../wiki/channels/Google|Search]]  
- **oracle**: Read-only high-IQ consultant
- **metis**: Pre-planning consultant
- **momus**: Plan reviewer/QA
- **Sisyphus-Junior**: Category-spawned executor

---

## Subagent Access - What [[../../wiki/people/Elia|Elia]] Can Use

### Current [[../../wiki/people/Elia|Elia]] Configuration

From `~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/oh-my-openagent.[[../../wiki/concepts/API-Integration|JSON]]`:

```[[../../wiki/concepts/API-Integration|JSON]]
{
  "agents": {
    "[[../../wiki/people/Elia|Elia]]": {
      "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/big-pickle",
      "mode": "primary",
      "prompt_append": "**FIRST: Read `/Users/vakandi/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/AGENTS.md`..."
    }
  },
  "categories": {
    "visual-engineering": { "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/[[../../wiki/people/Gemini|Gemini]]-3.1-pro", "variant": "high" },
    "ultrabrain": { "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/[[../../wiki/people/GPT|GPT]]-5.4", "variant": "xhigh" },
    "deep": { "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/[[../../wiki/people/GPT|GPT]]-5.3-codex", "variant": "medium" },
    "artistry": { "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/[[../../wiki/people/Gemini|Gemini]]-3.1-pro", "variant": "high" },
    "quick": { "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/[[../../wiki/people/GPT|GPT]]-5.4-mini" },
    "unspecified-low": { "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/[[../../wiki/people/Claude|Claude]]-sonnet-4-6" },
    "unspecified-high": { "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/[[../../wiki/people/Claude|Claude]]-opus-4-6", "variant": "max" },
    "writing": { "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/[[../../wiki/people/Gemini|Gemini]]-3-flash" }
  }
}
```

### Available Invocation Methods

**YES - [[../../wiki/people/Elia|Elia]] CAN use these subagents**:

| Method | Syntax | Works? |
|--------|--------|--------|
| **Categories** (8 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|Built]]-in) | `[[../../wiki/concepts/AI-Automation#tasks|Task]](category="visual-engineering", ...)` | ✅ YES |
| **subagent_type** (6 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|Built]]-in) | `[[../../wiki/concepts/AI-Automation#tasks|Task]](subagent_type="explore", ...)` | ✅ YES |
| **[[../../wiki/businesses/B2LUXE-BUSINESS|Business]] agents** (custom) | `oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a setbon "..."` | ✅ YES |

**8 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|Built]]-in Categories**:
| Category | Default Model | Domain |
|----------|--------------|--------|
| `visual-engineering` | [[../../wiki/people/Gemini|Gemini]]-3.1-pro high | Frontend, UI/UX |
| `ultrabrain` | [[../../wiki/people/GPT|GPT]]-5.4 xhigh | Hard logic |
| `deep` | [[../../wiki/people/GPT|GPT]]-5.3-codex medium | Autonomous problem-solving |
| `artistry` | [[../../wiki/people/Gemini|Gemini]]-3.1-pro high | Creative approaches |
| `quick` | [[../../wiki/people/GPT|GPT]]-5.4-mini | Trivial tasks |
| `unspecified-low` | [[../../wiki/people/Claude|Claude]]-sonnet-4-6 | Moderate effort |
| `unspecified-high` | [[../../wiki/people/Claude|Claude]]-opus-4-6 max | High effort |
| `writing` | [[../../wiki/people/Gemini|Gemini]]-3-flash | Documentation |

**6 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|Built]]-in subagent_types**:
- `explore` - Codebase grep
- `librarian` - External [[../../wiki/HOME|Docs]] [[../../wiki/channels/Google|Search]]
- `oracle` - Architecture/debugging consultant
- `metis` - Pre-planning
- `momus` - Plan review
- `multimodal-looker` - PDF/image analysis

### Custom [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] Agents ([[../../wiki/people/Elia|Elia]] has these)

From config, [[../../wiki/people/Elia|Elia]] already has access to:
- `[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]`, `[[../../wiki/businesses/CoBou-Agency|CoBou]]-agency`, `[[../../wiki/businesses/ZovaBoost|ZovaBoost]]`, `[[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]-youtube-auto`, `[[../../wiki/businesses/Netfluxe|Netfluxe]]`
- `setbon` ([[../../wiki/concepts/Marketing-Concepts|Marketing]]), `gilfoyle` (backend), `markov` (trading)

These are configured in `oh-my-openagent.[[../../wiki/concepts/API-Integration|JSON]]` with `mode: "primary"` so they appear in `/agents` command.

---

## ZWSP Bug Explanation

### Root Cause

From `src/shared/[[../../wiki/concepts/AI-Automation|Agent]]-display-names.ts`:

```typescript
const AGENT_LIST_SORT_PREFIXES: Record<string, string> = {
  sisyphus: "\u200B",        // ZWSP (Zero Width Space)
  hephaestus: "\u200B\u200B", 
  prometheus: "\u200B\u200B\u200B",
  atlas: "\u200B\u200B\u200B\u200B",
}
```

**The Problem**: Display names like "Sisyphus - Ultraworker" have invisible ZWSP characters prepended for sorting in the [[../../wiki/concepts/AI-Automation|Agent]] dropdown. When using `oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a "Sisyphus - Ultraworker"`, the ZWSP must be included.

### Solution

The trigger scripts use:
```bash
# ZWJ character (different from ZWSP) for display names
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a "$(printf '\xe2\x80\x8b')Sisyphus - Ultraworker"
```

Or use config key directly: `oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a sisyphus`

### Why [[../../wiki/people/Elia|Elia]] Works Without ZWSP

[[../../wiki/people/Elia|Elia]]'s config uses just `"[[../../wiki/people/Elia|Elia]]"` as the key, no display name with suffix:
```[[../../wiki/concepts/API-Integration|JSON]]
"[[../../wiki/people/Elia|Elia]]": {
  "model": "[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/big-pickle",
  "mode": "primary"
}
```

---

## ULW-Loop Mechanism

### How It Works

1. **Trigger**: `/ulw-loop` command starts loop via `startLoop()`
2. **State**: Persisted to `.sisyphus/ralph-loop.[[../../wiki/systems/Docker-Servers|Local]].md`
3. **Detection**: On `session.idle`, scans for `<promise>DONE</promise>`
4. **Continuation**: If NOT done, injects [[../../wiki/concepts/Prompt-Engineering|PROMPT]] to continue

### Detection Logic

From `src/hooks/ralph-loop/completion-promise-detector.ts`:

```typescript
// Scans transcript [[../../wiki/concepts/File-Management|File]] OR session [[../../wiki/channels/Telegram|Messages]] API
function buildPromisePattern(promise: string): RegExp {
  return new RegExp(`<promise>\\s*${escapeRegex(promise)}\\s*</promise>`, "is")
}
```

**Two detection methods**:
- Transcript [[../../wiki/concepts/File-Management|File]] (`.sisyphus/transcripts/{sessionID}.jsonl`)
- Session [[../../wiki/channels/Telegram|Messages]] API (`client.session.[[../../wiki/channels/Telegram|Messages]]()`)

### [[../../wiki/concepts/Prompt-Engineering|PROMPT]] Injection

From `src/hooks/ralph-loop/continuation-[[../../wiki/concepts/Prompt-Engineering|PROMPT]]-injector.ts`:

```typescript
await ctx.client.session.promptAsync({
  path: { [[../../wiki/systems/Jira-Tickets-Index|ID]]: options.sessionID },
  body: {
    parts: [createInternalAgentTextPart(options.[[../../wiki/concepts/Prompt-Engineering|PROMPT]])],
  },
})
```

**Continuation [[../../wiki/concepts/Prompt-Engineering|PROMPT]] template**:
```
ultrawork RALPH LOOP 5/100
Your previous attempt did not output the completion promise. Continue working...
When FULLY complete, output: <promise>DONE</promise>
Original [[../../wiki/concepts/AI-Automation#tasks|Task]]: {[[../../wiki/concepts/AI-Automation#tasks|Task]]}
```

---

## Recommendations for [[../../wiki/people/Elia|Elia]] Configuration

### ✅ What's Already Working

1. **[[../../wiki/people/Elia|Elia]] can use [[../../wiki/concepts/AI-Automation#tasks|Task]]() tool** with categories and subagent_types
2. **8 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|Built]]-in categories** are available (visual-engineering, ultrabrain, deep, etc.)
3. **6 subagent_types** are available (explore, librarian, oracle, metis, momus)
4. **Custom [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] agents** configured ([[../../wiki/businesses/Bene2Luxe|Bene2Luxe]], setbon, gilfoyle, etc.)
5. **ULW-Loop works** - `/ulw-loop` command available

### 🔧 Recommendations

1. **Keep prompt_append for [[../../wiki/people/Elia|Elia]]** - Already configured correctly
2. **Use categories for delegation** - `[[../../wiki/concepts/AI-Automation#tasks|Task]](category="ultrabrain", ...)` works
3. **Use subagent_type for specialists** - `[[../../wiki/concepts/AI-Automation#tasks|Task]](subagent_type="explore", ...)` works
4. **For ULW tasks** - Use `/ulw-loop --completion-promise DONE`
5. **Model configuration** - Keep using `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/big-pickle` with no fallback_models

### Example Usage

```typescript
// Delegate to category (spawns Sisyphus-Junior with optimized model)
[[../../wiki/concepts/AI-Automation#tasks|Task]](category="ultrabrain", load_skills=[], [[../../wiki/concepts/Prompt-Engineering|PROMPT]]="Analyze this architecture")

// Invoke subagent directly  
[[../../wiki/concepts/AI-Automation#tasks|Task]](subagent_type="explore", load_skills=[], [[../../wiki/concepts/Prompt-Engineering|PROMPT]]="[[../../wiki/concepts/[[../../wiki/channels/Google|Search]]|Find]] similar patterns")

// [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] [[../../wiki/concepts/AI-Automation|Agent]] via CLI
oh-my-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] -a setbon "[[../../wiki/concepts/Marketing-Concepts|Marketing]] [[../../wiki/concepts/Ads-Funnel|Campaign]] for new [[../../wiki/businesses/Bene2Luxe#products|Product]]"

// ULW loop
/ulw-loop Analyze competitors and create [[../../wiki/docs/Sessions|Report]] --completion-promise DONE
```

---

## Summary

| Capability | [[../../wiki/people/Elia|Elia]] Has Access? |
|------------|------------------|
| Code-based [[../../wiki/concepts/Prompt-Engineering|PROMPT]] (like Sisyphus) | ❌ [[../../wiki/people/Elia|Elia]] uses config-based prompt_append |
| 8 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|Built]]-in categories | ✅ YES |
| 6 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Web-Development|Built]]-in subagent_types | ✅ YES |
| Custom [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] agents | ✅ YES ([[../../wiki/businesses/Bene2Luxe|Bene2Luxe]], setbon, gilfoyle, etc.) |
| ULW-Loop (/ulw-loop) | ✅ YES |
| [[../../wiki/concepts/AI-Automation#tasks|Task]]() tool delegation | ✅ YES |

**[[../../wiki/people/Elia|Elia]] can do almost everything Sisyphus can do** - the only difference is that Sisyphus uses CODE to dynamically build its [[../../wiki/concepts/Prompt-Engineering|PROMPT]] (with model-specific enhancements), while [[../../wiki/people/Elia|Elia]] uses a static `prompt_append` from config. Both can delegate to subagents, use categories, and [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] ULW loops.