---
name: parallel-work
description: "Force maximum parallel delegation for any multi-step task. Decomposes requests into independent work units and dispatches each to the best-fit subagent type/category simultaneously. Use this whenever a task has 2+ independent steps, involves multiple files/modules, or when the user asks to 'do X' and X touches multiple domains. Also use when user says 'parallel', 'delegate', 'multi-agent', 'fan out', or 'do everything at once'. This skill is the TOP-LEVEL orchestrator — it routes to dispatching-parallel-agents for debugging, subagent-driven-development for feature building, or handles general parallel dispatch directly. The orchestrator should NEVER write code itself when delegation is possible."
---

# Parallel Work — The Unified Delegation System

You are an orchestrator, not an implementer. Every task you receive gets decomposed into independent work units, each dispatched to the best-fit subagent in parallel. **Never touch code yourself** when a subagent can do it.

## The Three-Skill System

This skill is the entry point. It decides WHICH specialized skill to invoke based on the task type:

```
                        ┌─────────────────────┐
                        │    parallel-work     │
                        │  (YOU ARE HERE)      │
                        │  Top-level router    │
                        └─────────┬───────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
   ┌──────────────────┐ ┌────────────────┐ ┌─────────────────┐
   │  DEBUGGING?      │ │  BUILDING?     │ │  GENERAL?       │
   │                  │ │                │ │                 │
   │ dispatching-     │ │ subagent-      │ │ Handle directly │
   │ parallel-agents  │ │ driven-dev     │ │ in this skill   │
   │                  │ │                │ │                 │
   │ Multiple bugs,   │ │ Features with  │ │ Research, docs, │
   │ failing tests,   │ │ TDD + review   │ │ mixed tasks,    │
   │ investigations   │ │ per task       │ │ migrations,     │
   │ in parallel      │ │                │ │ refactors       │
   └──────────────────┘ └────────────────┘ └─────────────────┘
```

### Routing Decision (FIRST thing you do)

Ask yourself: **What is the PRIMARY nature of this task?**

| Task Contains | Route To | Why |
|---|---|---|
| Multiple bugs / failing tests / errors to investigate | `dispatching-parallel-agents` | Optimized for parallel investigation of independent failures |
| Features to build with specs / implementation plan | `subagent-driven-development` | TDD + two-stage review per task, structured execution |
| Mixed / general / research / migration / no clear plan | Handle directly in this skill | No specialized sub-skill needed |

**When the task spans multiple types** (e.g., "fix these 3 bugs AND add a new feature"):
1. Split by type first
2. Route debugging portion → `dispatching-parallel-agents`
3. Route building portion → `subagent-driven-development`
4. Handle any remaining general work directly

**When uncertain:** default to handling directly in this skill. It's better to decompose manually than to misroute.

---

## Part A: General Parallel Dispatch (this skill)

For tasks that don't fit debugging or structured feature building.

### Phase 1: Decompose

Read the user's request. Identify every **independent** work unit — things that can be done without waiting for another unit's output.

**Independence test:** Can unit B start if unit A hasn't finished? If yes → they're independent → dispatch both.

**Dependency graph example:**
```
Task: "Build a user dashboard with auth, stats cards, and a data table"

Independent units:
  1. Auth middleware (login page + session handling)
  2. Stats cards component (API + UI)
  3. Data table component (API + UI)
  4. Dashboard layout (depends on 1, 2, 3 being at least stubbed)

Dispatch 1, 2, 3 in parallel. 4 waits or gets a layout skeleton first.
```

### Phase 2: Map to Subagents

Each work unit needs the right **category** and **skills**. This is the most important decision you make.

#### Category Selection (mandatory — every unit gets one)

| Task Domain | Category | Why |
|---|---|---|
| UI, CSS, layout, animation, visual polish | `visual-engineering` | Model tuned for frontend |
| Backend API, server logic, database | `deep` | Autonomous end-to-end |
| Hard logic, algorithms, architecture | `ultrabrain` | High-reasoning model |
| Single-file fix, typo, config change | `quick` | Fast, cheap |
| Research, docs, exploration | `unspecified-low` | Light task |
| Multi-file feature, complex integration | `unspecified-high` | Full capability |
| Writing, documentation, prose | `writing` | Language-optimized |
| Code review, quality check | `unspecified-high` | Needs judgment |

**NEVER** use `quick` for anything touching 2+ files. **NEVER** use `unspecified-*` for visual work.

#### Skill Selection (mandatory — every unit gets relevant skills)

Check available skills against the task domain. Every skill whose expertise overlaps gets included.

**Anti-pattern:** `load_skills=[]` — this means you didn't look at what skills exist. At minimum, check if `backend-master`, `frontend-design`, `fastapi-pro`, `typescript-react-patterns`, or any domain-specific skill applies.

**Priority order:** User-installed skills > built-in skills. When in doubt, INCLUDE.

### Phase 3: Dispatch

Launch all independent units **in the same message**. Not sequentially. Not "first this, then that." ALL AT ONCE.

```
task(category="deep", load_skills=["fastapi-pro"], prompt="...", run_in_background=true)
task(category="visual-engineering", load_skills=["frontend-design"], prompt="...", run_in_background=true)
task(category="quick", load_skills=[], prompt="...", run_in_background=true)
```

**Background vs sync:**
- 3+ independent units → ALL background (`run_in_background=true`)
- 1-2 units → sync is fine, but background still works
- Unit that other units depend on → sync first, then fan out

### Phase 4: Wait, Collect, Verify

After dispatching:
1. **END YOUR RESPONSE.** Wait for completion notifications.
2. When `<system-reminder>` arrives → collect via `background_output(task_id="bg_...")`
3. **Verify each result:**
   - Does the output match what was requested?
   - Do results from different agents conflict (same file edited twice)?
   - Are there obvious errors or incomplete work?
4. If conflicts exist → merge manually or re-dispatch with conflict resolution instructions
5. Report aggregated results to the user

---

## Part B: Debugging Parallel Dispatch (→ dispatching-parallel-agents)

When the task is primarily **investigating and fixing multiple independent failures**, route to the `dispatching-parallel-agents` skill.

**Trigger conditions:**
- 3+ test files failing with different root causes
- Multiple subsystems broken independently
- User says "fix these bugs" or "all these tests are failing"
- Multiple error messages that look unrelated

**Key principles from dispatching-parallel-agents:**
1. **Group by failure domain** — each agent investigates one independent problem
2. **One agent per problem domain** — never bundle related failures
3. **Self-contained prompts** — each agent gets full error context, no need to read files
4. **Constraints matter** — "Do NOT change production code" or "Fix tests only"

**How to invoke:**
Read the `dispatching-parallel-agents` skill's SKILL.md for the full pattern, then apply it. The core flow is:

```
1. Group failures by domain (file A tests, file B tests, file C tests)
2. For each group, dispatch an agent with:
   - Specific scope (one test file or subsystem)
   - Clear goal (make these tests pass)
   - Constraints (don't change other code)
   - Full error context (paste the failures)
3. All agents run in parallel
4. Collect results, verify no conflicts, run full test suite
```

**Parallel with this skill:** You can dispatch debugging agents via `dispatching-parallel-agents` patterns AND general work via this skill's patterns in the same message. They don't conflict because debugging agents fix things while general agents build things.

---

## Part C: Feature Building Dispatch (→ subagent-driven-development)

When the task is primarily **building features with a clear spec**, route to the `subagent-driven-development` skill.

**Trigger conditions:**
- User provides a feature spec or implementation plan
- Task has clear acceptance criteria
- Building new endpoints, components, or modules
- User says "build X", "implement Y", "add feature Z"

**Key principles from subagent-driven-development:**
1. **Fresh subagent per task** — no context pollution between tasks
2. **TDD per task** — each subagent writes tests first, then implements
3. **Two-stage review** — spec compliance review first, then code quality review
4. **Model selection** — use cheapest model that can handle each role

**How to invoke:**
Read the `subagent-driven-development` skill's SKILL.md for the full pattern, then apply it. The core flow is:

```
1. Read plan, extract all tasks
2. Create TodoWrite with all tasks
3. For each task:
   a. Dispatch implementer subagent (with full task text + context)
   b. If questions arise → answer them
   c. When done → dispatch spec compliance reviewer
   d. If issues → implementer fixes, re-review
   e. Dispatch code quality reviewer
   f. If issues → implementer fixes, re-review
   g. Mark task complete
4. After all tasks → dispatch final code reviewer
```

**Parallel with this skill:** Feature building tasks can be parallelized at the TASK level (multiple implementers for independent tasks) but NOT at the subtask level (implement → review must be sequential within each task).

---

## Cross-Cutting Concerns

### Prompt Structure (ALL dispatched agents)

Every dispatched prompt MUST include these 6 sections. Vague prompts produce vague results.

```
## TASK
Atomic, specific goal — one action, one deliverable.

## EXPECTED OUTCOME
Concrete deliverables with success criteria. What "done" looks like.

## MUST DO
- Exhaustive requirements list
- File paths, function names, data structures
- Existing patterns to follow (reference specific files)
- Constraints and edge cases

## MUST NOT DO
- Forbidden actions (touching other files, refactoring, etc.)
- Anti-patterns to avoid

## CONTEXT
- Relevant file paths
- Existing code patterns to match
- Dependencies and imports
- Environment details

## TOOLS
- Which tools are allowed/required
```

### Conflict Avoidance (ALL parallel work)

The #1 rule: **no two agents edit the same file.**

Before dispatching, check:
- Are two units touching the same file? → Merge into one unit, or sequence them
- Are two units creating the same file? → Give each a different path
- Do units share state (same DB, same config)? → Read-only is fine, writes must be sequenced

**When in doubt about conflict:** dispatch the more foundational unit first (sync), then fan out dependents (background).

### The Orchestration Checklist

Before EVERY dispatch, run through this mentally:

- [ ] Did I route to the right skill? (debugging → dispatching-parallel-agents, building → subagent-driven-development, general → this skill)
- [ ] Did I decompose into truly independent units? (not just "split by file" but by responsibility)
- [ ] Did I pick the right category for EACH unit? (not just `quick` or `unspecified-*` as default)
- [ ] Did I load relevant skills for EACH unit? (not `load_skills=[]`)
- [ ] Did I write 6-section prompts for EACH unit? (not vague one-liners)
- [ ] Are there any file conflicts between units?
- [ ] Am I dispatching ALL independent units in the SAME message?

If any answer is "no" → fix before dispatching.

### What NOT to Do

- **DON'T** write code yourself when a subagent can. You are the conductor, not the orchestra.
- **DON'T** dispatch sequentially when you could dispatch in parallel. Every round-trip costs time.
- **DON'T** use `load_skills=[]`. If no skill matches, that's fine — but verify you checked.
- **DON'T** bundle multiple independent goals into one agent. One goal per agent.
- **DON'T** skip the MUST NOT DO section. Agents without constraints wander.
- **DON'T** wait for one agent to finish before dispatching the next if they're independent.
- **DON'T** re-read files that agents are already reading. Trust them.
- **DON'T** route debugging tasks to subagent-driven-development (no TDD review loop for bugs).
- **DON'T** route feature building to dispatching-parallel-agents (no review quality gates).

---

## Examples

### Example 1: "Fix all these failing tests" → dispatching-parallel-agents

```
User: "I have 6 test failures across 3 files after a refactor"

Route: dispatching-parallel-agents

Decompose:
  Group A: agent-tool-abort.test.ts (3 failures — timing issues)
  Group B: batch-completion-behavior.test.ts (2 failures — tools not executing)
  Group C: tool-approval-race-conditions.test.ts (1 failure — execution count = 0)

Dispatch (ALL in same message):
  task(category="deep", load_skills=["systematic-debugging"],
    prompt="Fix 3 failures in agent-tool-abort.test.ts: [full error context]...")
  task(category="deep", load_skills=["systematic-debugging"],
    prompt="Fix 2 failures in batch-completion-behavior.test.ts: [full error context]...")
  task(category="deep", load_skills=["systematic-debugging"],
    prompt="Fix 1 failure in tool-approval-race-conditions.test.ts: [full error context]...")

Result: 3 agents investigating in parallel, all fixes independent, zero conflicts
```

### Example 2: "Build a blog with auth, API, and frontend" → subagent-driven-development

```
User: "Add a blog section: auth-protected admin, public reader, REST API, Next.js frontend"

Route: subagent-driven-development

Decompose (from plan):
  Task 1: Blog admin auth middleware
  Task 2: Blog REST API (CRUD endpoints)
  Task 3: Blog public reader page
  Task 4: Blog admin dashboard page

Execute (sequential within each task, parallel across tasks where possible):
  Task 1 implement → review → Task 2 implement → review → etc.
  (Tasks 3+4 can be parallel if they don't share files)

Each task gets: implementer → spec reviewer → code quality reviewer
```

### Example 3: "Refactor the auth module and update docs" → parallel-work (general)

```
User: "Refactor auth to use JWT instead of sessions, and update the API docs"

Route: parallel-work (general) — mixed refactoring + writing

Decompose:
  Unit 1: Refactor auth module (JWT implementation)
  Unit 2: Update API documentation

Dispatch (ALL in same message):
  task(category="deep", load_skills=["backend-master"],
    prompt="## TASK\nRefactor src/auth/ to use JWT tokens...\n...")
  task(category="writing", load_skills=["doc-coauthoring"],
    prompt="## TASK\nUpdate API docs to reflect JWT auth changes...\n...")

Result: Both done in parallel, no file conflicts (code vs docs)
```

### Example 4: "Fix the login bug AND add a dashboard page" → mixed routing

```
User: "Login is broken on production, also add a analytics dashboard page"

Route: Split by type

  Fix login bug → dispatching-parallel-agents
    task(category="deep", load_skills=["systematic-debugging"],
      prompt="## TASK\nInvestigate and fix login failure on production...\n...")

  Add dashboard → subagent-driven-development (or general if no spec)
    task(category="visual-engineering", load_skills=["frontend-design"],
      prompt="## TASK\nCreate analytics dashboard page...\n...")
    task(category="deep", load_skills=["backend-master"],
      prompt="## TASK\nCreate analytics API endpoint...\n...")

All dispatched in same message. Bug fix and feature build happen in parallel.
```

## Category Quick Reference

```
visual-engineering  → Frontend, UI, CSS, animation, design
artistry           → Creative problem-solving, unconventional approaches
ultrabrain          → Hard logic, algorithms, architecture decisions
deep               → Autonomous end-to-end features, research + impl
quick              → Single-file typo, config, trivial fix
unspecified-low    → Light tasks that don't fit other categories
unspecified-high   → Complex tasks that don't fit other categories
writing            → Documentation, prose, technical writing
```

When multiple categories could fit, pick the one whose domain matches the CORE of the task. A "fix the auth bug" task is `deep` (investigation + fix), not `quick` (even if the fix is one line — the investigation is the work).
