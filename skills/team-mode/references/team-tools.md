# Team Tools Reference — `team_*` API

All tools require `team_mode.enabled: true` in oh-my-openagent.jsonc. If these tools are absent, team mode is disabled.

---

## team_create

Create a new team. Returns `{ teamRunId, leadSessionId, memberSessionIds }`.

```typescript
team_create({
  // Option A: Pre-declared spec
  teamName: "my-team",  // looks up ~/.omo/teams/{name}/config.json

  // Option B: Inline spec (one-off team)
  inline_spec: {
    name: "feature-squad",
    description: "Build the new feature",
    lead: { kind: "subagent_type", subagent_type: "gilfoyle" },
    members: [
      { kind: "subagent_type", name: "picasso", subagent_type: "picasso", prompt: "..." },
      { kind: "category", name: "researcher", category: "deep", prompt: "..." }
    ]
  }
})
```

**Member spec fields:**
- `kind`: `"subagent_type"` (specific agent) or `"category"` (routed via sisyphus-junior)
- `name`: unique member identifier within the team
- `subagent_type`: agent name from opencode.json (when kind=subagent_type)
- `category`: model category (when kind=category): `quick`, `deep`, `ultrabrain`, `visual-engineering`, `unspecified-low`, `unspecified-high`, `artistry`, `writing`, `data-analysis`, `git`
- `prompt`: member's constitution — defines their role and responsibilities

---

## team_send_message

Send a message to a team member or broadcast to all.

```typescript
team_send_message({
  teamRunId: "<uuid>",
  to: "picasso",        // member name, or "*" for broadcast
  body: "I've finished the API endpoints. Here's the schema: ...",
  kind: "message"       // default; also: "announcement"
})
```

**Message kinds:**
- `message` — standard peer-to-peer communication
- `announcement` — lead broadcast (informational)

Messages are delivered automatically via `<peer_message>` envelope injection. No polling needed.

---

## team_task_create

Create a task on the shared task list.

```typescript
team_task_create({
  teamRunId: "<uuid>",
  subject: "Implement auth endpoints",
  description: "Build JWT auth with refresh tokens. Coordinate with frontend on token storage.",
  blockedBy: ["task-design"]  // optional: task IDs that must complete first
})
```

Returns `{ taskId }`.

---

## team_task_list

List tasks with optional status filter.

```typescript
team_task_list({
  teamRunId: "<uuid>",
  status: "pending"  // optional: "pending" | "claimed" | "in_progress" | "completed" | "deleted"
})
```

Returns array of task objects with id, subject, status, owner, blockedBy.

---

## team_task_update

Update task status or claim a task.

```typescript
team_task_update({
  teamRunId: "<uuid>",
  taskId: "task-1",
  status: "claimed",
  owner: "gilfoyle"  // required when status = "claimed"
})

team_task_update({
  teamRunId: "<uuid>",
  taskId: "task-1",
  status: "completed"
})
```

**Task statuses:** `pending` → `claimed` → `in_progress` → `completed` | `deleted`

---

## team_status

Get current team state — members, sessions, health.

```typescript
team_status({ teamRunId: "<uuid>" })
```

Returns member list, session IDs, message counts, task summary.

---

## team_list

List all active teams (no arguments).

```typescript
team_list()
```

---

## team_shutdown_request

Initiate graceful shutdown for a member (lead only).

```typescript
team_shutdown_request({
  teamRunId: "<uuid>",
  targetMemberName: "picasso"
})
```

The member receives the request and can approve or reject.

---

## team_approve_shutdown

Approve a pending shutdown request (member responds).

```typescript
team_approve_shutdown({
  teamRunId: "<uuid>",
  memberName: "gilfoyle"
})
```

---

## team_delete

Delete the team and clean up all resources.

```typescript
team_delete({ teamRunId: "<uuid>" })
```

**Only call after all members have approved shutdown.**

---

## Lifecycle Summary

```
1. team_create           → teamRunId, member sessions
2. team_task_create      → assign work
3. team_send_message     → coordinate, share findings
4. team_task_list        → monitor progress
5. team_shutdown_request → per member
6. team_approve_shutdown → per member
7. team_delete           → cleanup
```

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `team_mode not enabled` | Config missing | Add `team_mode.enabled: true` to oh-my-openagent.jsonc, restart |
| `member not eligible` | Agent lacks write access | Check references/agent-registry.md for alternatives |
| `RecipientBackpressureError` | Member inbox full | Increase `recipient_unread_max_bytes` or send smaller messages |
| `team not found` | Invalid teamRunId | Check `team_list()` for active teams |
