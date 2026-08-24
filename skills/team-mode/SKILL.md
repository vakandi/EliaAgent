---
name: team-mode
description: "Activate collaborative team mode where multiple AI agents work together in real-time, talking to each other via a shared mailbox — not just delegating. TRIGGER when: user types @agent-name to mention agents, user says 'team mode', user wants multiple agents to collaborate/discuss/debate on a task, user says 'assemble a team', 'bring in @X and @Y', 'get the team on this', or any request where multiple named agents should work together simultaneously with bidirectional communication. This is NOT simple delegation — use this when agents need to talk to each other, share findings, debate, and coordinate."
---

# Team Mode — Collaborative Agent System

You are activating **team mode**: a collaborative system where multiple AI agents work together in real-time, communicating via a shared mailbox. This is fundamentally different from delegation — agents **talk to each other**, share findings, debate, and coordinate work.

## How It Works

1. **User mentions agents** with `@agent-name` syntax (e.g., "get @gilfoyle and @picasso on this")
2. **You parse** the mentioned agents and validate eligibility
3. **You create a team** via `team_create` with the mentioned agents as members
4. **Agents communicate** via `team_send_message` — bidirectional, not just parent→child
5. **You manage lifecycle** — create tasks, monitor progress, shutdown when done

## Quick Start

When the user mentions agents with `@`:

```
User: "We need to redesign the landing page. Get @picasso for the UI and @gilfoyle for the backend API."
```

**Your response flow:**
1. Parse: picasso (frontend), gilfoyle (backend)
2. Validate both are eligible (see references/agent-registry.md)
3. Create team with `team_create`
4. Assign tasks with `team_task_create`
5. Members communicate findings via `team_send_message`
6. Monitor with `team_task_list` and `team_status`
7. Shutdown gracefully when all tasks complete

## Step-by-Step Protocol

### Step 1: Parse Agent Mentions

Extract all `@agent-name` mentions from the user's message. Common patterns:
- `@gilfoyle @picasso` — two agents
- `bring in @setbon for marketing` — agent with role hint
- `@markov-technical-analyst and @markov-fundamental-analyst` — full names work
- `team: @gilfoyle, @picasso, @setbon` — comma-separated

If the user doesn't mention specific agents but describes a task, suggest appropriate agents based on their roles (see agent-registry.md).

### Step 2: Validate Eligibility

Before creating the team, check each agent against the eligibility list in `references/agent-registry.md`. Some agents (like oracle, librarian, explore) cannot be team members because they lack write access to the mailbox system.

If an ineligible agent is mentioned, suggest an alternative and explain why.

### Step 3: Create the Team

Use `team_create` with an inline spec. The **current agent (you)** is always the lead unless the user specifies otherwise.

```typescript
team_create({
  inline_spec: {
    name: "landing-redesign",  // kebab-case, descriptive
    description: "Redesign the landing page with new branding",
    lead: { kind: "subagent_type", subagent_type: "<your-agent-name>" },
    members: [
      {
        kind: "subagent_type",
        name: "picasso",
        subagent_type: "picasso",
        prompt: "Lead the visual redesign of the landing page. Create component specs, color palette, and layout. Share your design decisions with the team."
      },
      {
        kind: "subagent_type",
        name: "gilfoyle",
        subagent_type: "gilfoyle",
        prompt: "Implement the backend API changes needed for the new landing page. Coordinate with picasso on data requirements."
      }
    ]
  }
})
```

**Member prompt guidelines:**
- Give each member a clear responsibility
- Tell them to use `team_send_message` to share findings
- Specify who they should coordinate with
- Keep prompts under 500 words — the member's personality file provides the rest

### Step 4: Assign Tasks

After team creation, create shared tasks:

```typescript
team_task_create({
  teamRunId: "<uuid-from-team_create>",
  subject: "Design new landing page layout",
  description: "Create wireframes, component hierarchy, and visual design for the hero section and features grid."
})

team_task_create({
  teamRunId: "<uuid>",
  subject: "Implement API endpoints",
  description: "Build the backend endpoints needed for the new landing page dynamic content."
})
```

Tasks can have dependencies:
```typescript
team_task_create({
  teamRunId: "<uuid>",
  subject: "Integrate frontend with API",
  description: "Connect the new landing page components to the backend API.",
  blockedBy: ["task-1", "task-2"]  // waits for design + API
})
```

### Step 5: Monitor & Facilitate

- Check `team_task_list` periodically to see progress
- Members will send you messages via `team_send_message` with updates
- If members are blocked, facilitate by sending messages between them
- Use `team_send_message({ to: "*", body: "..." })` to broadcast to all members

### Step 6: Shutdown

When all tasks are completed or the user says "wrap up" / "shutdown the team":

1. Check `team_task_list` — confirm all tasks are terminal (completed/deleted)
2. Send shutdown request to each member: `team_shutdown_request`
3. Each member responds with `team_approve_shutdown`
4. Delete the team: `team_delete`

**You are responsible for shutdown.** Don't wait for the user to ask.

## Team Communication Rules

### For the Lead (you)
- Create tasks and assign them
- Monitor progress via `team_task_list`
- Facilitate communication between members
- Make final decisions when members disagree
- Always run the shutdown sequence when done

### For Members (agents you spawn)
- Members receive their prompt as a "constitution" — it defines their role
- Members use `team_send_message` to communicate — plain text is invisible to others
- Members can claim tasks, update status, and coordinate with peers
- Members CANNOT spawn their own sub-agents (delegate-task budget = 0)

### Message Types
- `team_send_message({ to: "agent-name", body: "..." })` — direct message
- `team_send_message({ to: "*", body: "..." })` — broadcast to all (lead only)
- Messages are delivered automatically via `<peer_message>` envelope injection

## Team Spec Files (Optional)

For recurring teams, save specs to `~/.omo/teams/{name}/config.json`:

```json
{
  "name": "your-saas-squad",
  "description": "your-saas development and marketing team",
  "lead": { "kind": "subagent_type", "subagent_type": "gilfoyle" },
  "members": [
    { "kind": "subagent_type", "name": "picasso", "subagent_type": "picasso", "prompt": "Frontend development and UI/UX" },
    { "kind": "subagent_type", "name": "setbon", "subagent_type": "setbon", "prompt": "Marketing strategy and conversion optimization" },
    { "kind": "category", "name": "researcher", "category": "deep", "prompt": "Research and analysis tasks" }
  ]
}
```

Then create with: `team_create({ teamName: "your-saas-squad" })`

## Category-Routed Members

For tasks that don't need a specific agent personality, use category-routed members:

```typescript
{ kind: "category", name: "researcher", category: "deep", prompt: "Research the competitor landscape." }
```

Available categories: `quick`, `deep`, `ultrabrain`, `visual-engineering`, `unspecified-low`, `unspecified-high`, `artistry`, `writing`, `data-analysis`, `git`

## Configuration

Team mode must be enabled in `oh-my-openagent.jsonc`:

```jsonc
{
  "team_mode": {
    "enabled": true,
    "max_parallel_members": 4,
    "max_members": 8,
    "tmux_visualization": false
  }
}
```

If team tools are absent, tell the user to enable team_mode and restart opencode.

## Common Patterns

### Code Review Team
```
User: "Review the auth module. Get @gilfoyle for backend and @picasso for frontend."
```
→ Create team, gilfoyle reviews backend auth, picasso reviews frontend auth, they share findings.

### Marketing Launch
```
User: "Launch campaign for your-saas. @setbon for strategy, @your-saas-community-organic for content, @googlebot for SEO."
```
→ Create team, setbon leads strategy, community-organic creates content, googlebot handles SEO.

### Debugging Squad
```
User: "Bug in production. @gilfoyle investigate logs, @picasso check the frontend, someone research similar issues."
```
→ Create team with gilfoyle + picasso + category "deep" researcher.

### Full-Stack Feature
```
User: "Build the new dashboard. Backend by @gilfoyle, UI by @picasso, copy by @setbon."
```
→ Create team, all three coordinate their work via messages.

## Prerequisites & Setup Flow

If `team_create` or other team tools are **missing** (not available in your tool list), do NOT try to work around it. Follow this setup checklist in order. If a step requires user action, **stop and ask the user** — do not proceed.

1. **Check oh-my-openagent is installed** — run `npm list -g oh-my-openagent`. If missing, tell the user: *"oh-my-openagent must be installed. Run: `npm install -g oh-my-openagent`"*
2. **Check team_mode is enabled** — read `~/.config/opencode/oh-my-openagent.jsonc` and confirm `"team_mode": { "enabled": true }`. If not, ask the user to add it.
3. **Check the @latest cache exists** — if `~/.cache/opencode/packages/oh-my-openagent@latest/` is missing, tell the user: *"The plugin cache was deleted. I need to recreate it from ~/EliaAI/setup/oh-my-openagent."*
4. **If all of the above is correct but tools are still missing: stop and ask the user to restart opencode.** Say: *"Team tools are not loaded. Please restart opencode to activate the plugin, then ask me the same thing again."*

This skill **always works** — even if it requires stopping and asking the user to restart. That's the correct behavior.

## Agent Eligibility

All custom agents (gilfoyle, picasso, setbon, elia, markov, etc.) are eligible for team mode via `subagent_type`. The AGENT_ELIGIBILITY_REGISTRY in `dist/index.js` has been patched with all the user's custom agents. If an agent is rejected, use `kind: "category"` instead of `subagent_type` as a fallback workaround.
