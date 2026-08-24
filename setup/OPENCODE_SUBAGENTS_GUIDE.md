# Subagent Persona Design Guide

## Overview

This guide documents best practices for creating effective subagent personas in OhMyOpenCode. It captures lessons learned from prompt engineering research, agent design patterns, and production experience.

---

## Core Principles

### 1. The Three Questions

Every agent persona must answer:

1. **Who are you?** — Role, persona, constraints
2. **What do you have?** — Available tools and what each does
3. **How should you work?** — Decision-making process, output format, edge cases

### 2. System Prompt Structure

```
# Agent Name

Brief one-line description.

## Persona
[Who you are, tone, style, constraints]

## Scope
[What you help with, what you don't]

## Tools & Access
[Available tools and when to use each]

## Workflow
[Step-by-step process for your domain]

## Communication Style
[Format, tone, examples]

## Constraints
[Hard rules, escalation paths]
```

### 3. Keep Prompts Under 1500 Words

Long prompts dilute model attention. Reference external docs for depth.

---

## Persona Design Elements

### The Persona Section

**BAD:**
```markdown
You are a helpful assistant. Be professional and friendly.
```

**GOOD:**
```markdown
## Persona

You are Oliver, Backend Architect for your-agency.

**Personality traits:**
- Methodical and technically precise — no hand-waving
- Direct communication style — "The fix is straightforward"
- Casual but not informal ("Let's debug this")
- Patient with beginners, peer-level with experts

**You never:**
- Start with "Certainly!" or "Of course!"
- Use excessive emojis
- Make excuses for complexity
```

### The Scope Section

Define both what the agent handles AND what it doesn't:

```markdown
## Scope

### You Handle
- API development with FastAPI, PostgreSQL
- Docker containerisation and CI/CD
- Database design and optimisation
- Code review for backend systems

### You Don't Handle
- Frontend development (delegate to frontend-dev)
- UI/UX design decisions
- Marketing or sales tasks
- Billing or finance matters

**When asked about out-of-scope:**
Acknowledge the request, explain you specialise in backend work, 
and offer to delegate to the appropriate agent.
```

### Few-Shot Examples (Most Powerful Technique)

Show, don't just tell. Examples dramatically improve behavior:

```markdown
## Example Interactions

### Handling a Bug Report

User: The API is returning 500 errors
You: I need specifics to diagnose. Can you share:
1. The endpoint affected
2. The request payload
3. Any logs from the error

### Handling a Feature Request

User: Add user authentication
You: Before I scope this out:
- JWT or session-based auth?
- Existing user table or new?
- Third-party providers (Google, GitHub)?

### When You Need Clarification

User: Fix the endpoint
You: Could you specify? I see three endpoints with recent changes:
- /api/users
- /api/products  
- /api/orders

Which one has the issue?
```

### Error Handling

Explicit error handling prevents common failure modes:

```markdown
## Error Handling

**When a tool fails:**
1. Read the error message carefully
2. Attempt one fix based on the error
3. If it fails again, report the error with context

**When you don't know:**
- Say "I don't have that information" rather than guessing
- Suggest where to find the answer
- Offer alternatives if possible

**Never:**
- Invent tool results or data
- Make up error explanations
- Ignore repeated failures
```

### Chain-of-Thought Instructions

Encourage explicit reasoning:

```markdown
## Decision Process

Before taking action, think through:

1. What does the user actually need?
2. What information do I have?
3. What tools should I use?
4. What's the expected output?

<thinking>
The user wants to optimize the database query.
I should first identify slow queries using EXPLAIN ANALYZE,
then propose targeted indexes based on the query patterns.
</thinking>
```

---

## UK English Naming Conventions

Use formal but approachable British names:

| Domain | Name | Rationale |
|--------|------|----------|
| Backend Development | Oliver | Classic British, technically minded |
| Frontend Development | James | Professional, creative |
| Finance Operations | William | Traditional, trustworthy |
| Marketing Social | Victoria | Sophisticated, strategic |
| Sales Closing | Charles | Persuasive, professional |
| HR Recruitment | Elizabeth | Warm, professional |
| Content Creation | Thomas | Creative, production-minded |
| E-commerce Luxury | Charlotte | Refined, luxury-oriented |
| Partnership your-partner | Alexander | Diplomatic, bridge-builder |
| Operations Workflow | Sebastian | Systems thinker |
| DM Customer Comms | Catherine | Empathetic, articulate |
| Snapchat Growth | Marcus | Growth-focused, analytical |
| TikTok/YouTube Auto | Eleanor | Efficient, automated |

---

## Prompt Template

```markdown
# {NAME} - {TITLE}

**{ONE-LINE DESCRIPTIVE TAGLINE}**

## Persona

[Comprehensive persona description with:]
- Professional background
- Personality traits (3-5 max)
- Communication style
- What you NEVER do (prevents bad habits)

## Scope

### You Handle
- [Domain-specific list]

### You Don't Handle
- [Clear boundaries]

### Escalation Path
- When to escalate to main agent
- What information to include

## Tools & Access

| Tool | When to Use |
|------|-------------|
| agent-browser | Web tasks, emails, forms |
| mcp-cli | WhatsApp, Telegram, Discord |
| mcp-atlassian | Jira, project management |
| file operations | Code, configs, docs |
| bash | Scripts, git, docker |

## Workflow

```
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

## Communication Format

**Standard response:**
```
[SUMMARY]
[KEY POINTS or DETAILS]
[RECOMMENDED NEXT STEPS or QUESTION]
```

**Never:**
- Start with "Certainly!" or "Of course!"
- Use more than 3 emojis per message
- Send walls of unformatted text

## Examples

### Example 1: [Scenario]
User: [Input]
You: [Expected output]

### Example 2: [Scenario]
User: [Input]
You: [Expected output]

## Constraints

1. [Hard rule 1]
2. [Hard rule 2]
3. [Hard rule 3]

---

**Signature phrase:** "{ONE SENTENCE PHILOSOPHY}"
```

---

## Anti-Patterns to Avoid

### 1. Over-Prompting
- Keep system prompts under 1500 words
- Put reference material in separate files
- Trust the model to infer

### 2. Contradictory Instructions
- Audit prompts for conflicts regularly
- "Be concise" vs "Always explain in detail" = conflict

### 3. Vague Persona
- "Be helpful and friendly" = useless
- "Helpful, friendly to enterprise clients about APIs" = useful

### 4. No Negative Examples
- Tell what BAD responses look like
- "Here's what I don't want" is often more effective

### 5. Ignoring Edge Cases
- Test: off-topic questions, very long messages, emotional users
- Include handling for empty tool results

---

## agent-browser Best Practices

### When to Use agent-browser

| Use Case | Tool | Why |
|----------|------|-----|
| Web browsing, screenshots | agent-browser | Persistent state, authenticated |
| Quick lookups | websearch | Faster, no state needed |
| Form fills, clicks | agent-browser | Full interaction support |
| Document downloads | agent-browser | State persistence |

### agent-browser Command Reference

```bash
# Navigation
agent-browser --profile ~/.agent-browser-profile open <url>
agent-browser close

# Interaction
agent-browser click <selector>
agent-browser type <sel> <text>
agent-browser fill <sel> <text>
agent-browser find text "X" click

# Get Info
agent-browser snapshot  # Accessibility tree
agent-browser screenshot [path]
agent-browser get url
agent-browser get title

# Wait
agent-browser wait <selector>
agent-browser wait --text "Welcome"
```

---

## Testing Your Agent

### Test Cases to Run

1. **Happy path:** Normal request for your domain
2. **Edge case:** Ambiguous or incomplete request
3. **Out of scope:** Request for another domain
4. **Error simulation:** What if a tool fails?
5. **Escalation:** Complex issue requiring main agent

### Rating Scale

| Rating | Criteria |
|--------|----------|
| 1 (Bad) | Wrong tools, wrong format, missed scope |
| 2 (Acceptable) | Correct tools, adequate response |
| 3 (Good) | Correct tools, good format, helpful extras |

### Iteration Process

1. Run 10-20 test conversations
2. Rate each 1-3
3. For 1s: Write ideal response as few-shot example
4. Add example to prompt
5. Retest

---

## File Structure

```
~/.config/opencode/
├── agents/
│   ├── oliver-backend.md
│   ├── james-frontend.md
│   ├── william-finance.md
│   ├── victoria-marketing.md
│   ├── charles-sales.md
│   ├── elizabeth-hr.md
│   ├── thomas-content.md
│   ├── charlotte-ecommerce.md
│   ├── alexander-partnership.md
│   ├── sebastian-operations.md
│   ├── catherine-dm.md
│   ├── marcus-snapchat.md
│   └── eleanor-tiktok.md
├── docs/
│   └── SUBAGENT-DESIGN-GUIDE.md  (this file)
└── oh-my-opencode.json  (categories reference)
```

---

## Agent Registration Requirements

To make an agent accessible via `@name` mentions and appear in the `/agents` list, ensure the agent is registered in **all** relevant configuration files with the correct fields.

### Two Config Files, Two Different Purposes

| File | Purpose |
|------|---------|
| `opencode.json` | **OpenCode core config.** Defines the agent for the OpenCode runtime. **`mode` field here controls @mention.** |
| `oh-my-openagent.json` | **oh-my-openagent plugin config.** The `agents` section provides model overrides (variant, fallback_models) when the agent is called via `task()`. The `agent_display_names` section provides human-readable names for the `/agents` list. |

### Critical: `mode` Means Different Things in Each File

| File | `mode: "primary"` | `mode: "subagent"` | `mode: "all"` |
|------|-------------------|--------------------|---------------|
| `opencode.json` | **@mention BLOCKED.** Agent only selectable as default. | **@mention WORKS.** Can be invoked via `@name` or `task()`. | Both primary AND @mentionable. |
| `oh-my-openagent.json` | Agent CANNOT be called via `task()` delegation (primary agents are direct-select only). | Agent CAN be called via `task()` delegation. | Both. |

**Rule of thumb:**
- `"subagent"` → @mention ✅, `/agents` listing ❌
- `"all"` → @mention ✅, `/agents` listing ✅
- `"primary"` → @mention ❌, `/agents` listing ✅ (default agent only)

Use `"all"` for agents that need both @mention AND `/agents` access.

### Working Example: Gilfoyle Setup

This is a known-working configuration verified in production.

#### `opencode.json` (controls @mention)

```json
"gilfoyle": {
  "description": "Gilfoyle - Backend & Full-Stack Developer",
  "mode": "subagent",
  "color": "#e089af",
  "model": "opencode/big-pickle",
  "prompt_append": "**FIRST: Read `~/.config/opencode/agents/gilfoyle.md` for your full workflow and rules.**\n\nTu es Gilfoyle - spécialiste backend/full-stack."
}
```

**Key field: `"mode": "subagent"`** — this is what enables @mention. Without it, the agent won't appear in the TUI @mention dropdown.

#### `oh-my-openagent.json` `agents` section (model overrides for task())

```json
"gilfoyle": {
  "model": "opencode/big-pickle",
  "variant": "max",
  "fallback_models": [],
  "mode": "primary",
  "description": "Gilfoyle - Backend & Full-Stack Developer",
  "prompt_append": "**Read `~/.config/opencode/agents/gilfoyle.md` for full workflow and rules.**\n\nYou are Gilfoyle - senior backend/full-stack developer."
}
```

The `mode` here affects whether `task(subagent_type="gilfoyle", ...)` is allowed (needs `"subagent"`), not @mention.

#### `oh-my-openagent.json` `agent_display_names`

```json
"gilfoyle": "Gilfoyle"
```

This controls the label shown in `/agents` listing.

### Required Fields in `opencode.json`

Each agent entry should include:

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Short one-line description shown in listings |
| `mode` | string | `"subagent"` or `"all"` for @mention; `"primary"` to block @mention |
| `color` | string | Hex color code for UI display |
| `model` | string | Model identifier (e.g., `"opencode/big-pickle"`) |
| `prompt_append` | string | Instructions appended to the prompt; should reference the agent's `.md` personality file |

### Working Example: GoogleBot Setup

The GoogleBot agent is configured identically to Gilfoyle. Both are @mentionable subagents.

#### `opencode.json` (controls @mention)

```json
"googlebot": {
  "description": "GoogleBot - SEO & Web Crawling Specialist",
  "mode": "all",
  "color": "#4285f4",
  "model": "opencode/big-pickle",
  "prompt_append": "**FIRST: Read `~/.config/opencode/agents/googlebot.md` for your full system prompt.**\n\nTu es GoogleBot - expert SEO et crawling."
}
```

#### `oh-my-openagent.json` `agents` section

```json
"googlebot": {
  "model": "opencode/big-pickle",
  "variant": "max",
  "fallback_models": [],
  "mode": "primary",
  "description": "GoogleBot - SEO & Web Crawling Specialist",
  "prompt_append": "**FIRST: Read `~/.config/opencode/agents/googlebot.md` for your full system prompt.**\n\nTu es GoogleBot - expert SEO et crawling."
}
```

#### `oh-my-openagent.json` `agent_display_names`

```json
"googlebot": "GoogleBot"
```

### Required Fields in `oh-my-openagent.json`

The `oh-my-openagent.json` has **three** relevant sections for agent registration:

#### 1. `agents` key — Model overrides for task() delegation

Must include `model`, `variant`, `fallback_models`, `description`, and `prompt_append`.

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Model identifier (e.g., `"opencode/big-pickle"`) |
| `variant` | string | Model variant (e.g., `"max"`, `"standard"`) |
| `fallback_models` | array | Fallback models if primary fails |
| `mode` | string | `"subagent"` or `"all"` to allow `task()` delegation |
| `description` | string | Short one-line description |
| `prompt_append` | string | Instructions for the agent |

Example from `agents` section:
```json
"googlebot": {
  "model": "opencode/big-pickle",
  "variant": "max",
  "fallback_models": [],
  "mode": "primary",
  "description": "GoogleBot - SEO & Web Crawling Specialist",
  "prompt_append": "**FIRST: Read .../agents/googlebot.md for your full system prompt.**"
}
```

**Note:** The `mode` in this section does NOT affect @mention. It affects whether `task(subagent_type="googlebot", ...)` is allowed. Set to `"subagent"` to allow task delegation.

#### 2. `agent_display_names` key — Human-readable name for `/agents` list

```json
"googlebot": "GoogleBot"
```

This is what users see in the TUI `/agents` listing. The key must match the agent config key exactly.

#### 3. `categories` key (optional) — Category registration for agent

Each agent can optionally be assigned to a category and appear under the `/agents` categorized view:

```json
"googlebot": {
  "icon": "🔍",
  "name": "GoogleBot",
  "category": "seo",
  "model": "opencode/big-pickle",
  "description": "GoogleBot - SEO & Web Crawling Specialist",
  "prompt_append": "**FIRST: Read .../agents/googlebot.md for your full system prompt.**"
}
```

### Agent Naming Rules

The `-a` or `--agent` flag in CLI commands uses the **config key** (e.g., `googlebot`, not `google-bot`). The @mention in the TUI also uses the config key.

```bash
# ✅ Correct - uses config key
oh-my-opencode run -a googlebot 'Research SEO'

# ❌ Wrong - hyphens or display names don't work
oh-my-opencode run -a google-bot 'Research SEO'
oh-my-opencode run -a "GoogleBot" 'Research SEO'
```

### Checklist for New Agents

- [ ] Agent `.md` personality file exists in `agents/` directory
- [ ] Entry exists in `opencode.json` under `agent` with `mode: "subagent"` (for @mention) or `"all"`
- [ ] Entry exists in `oh-my-openagent.json` under `agents` with `model`, `variant`, `fallback_models`, `description`, `prompt_append`
- [ ] Entry exists in `oh-my-openagent.json` under `agent_display_names` with a human-readable name
- [ ] Verify: `opencode agent list --pure \| grep <agent-name>` shows the correct mode

---

## Revision History

| Date | Version | Changes |
|-------|---------|---------|
| 2026-03-19 | 1.0 | Initial creation with UK English names |
