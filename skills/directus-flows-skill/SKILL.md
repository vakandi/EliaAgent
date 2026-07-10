# Directus Flows Master Skill

Complete reference for creating, managing, visualizing, and debugging Directus Flows programmatically via the REST API. Covers ALL trigger types, ALL operation types, operation chaining (resolve/reject), and troubleshooting.

## 1. ARCHITECTURE OVERVIEW

```
Directus Flows = Trigger → Operations Chain → Data Chain
                     │           │
                     ▼           ▼
              Event/Webhook/   Request/Transform/
              Schedule/Manual  Condition/Log/Mail/etc.
```

**Flow lifecycle:**
1. **Trigger** fires (event happens, webhook received, cron time reached)
2. **First operation** executes (specified by `flow.operation` UUID)
3. **Data chain** passes through each operation (each op's output feeds the next)
4. **Resolve/Reject** determines which operation runs next
5. Flow completes when an operation has `resolve: null` and `reject: null`

**Data chain variables** (accessible in operation templates via `{{...}}`):
- `{{ $trigger }}` — The original trigger payload
- `{{ $trigger.payload.field }}` — Specific trigger payload field
- `{{ $trigger.payload.id }}` — ID of the item that triggered the event
- `{{ $last }}` — Output of the last executed operation
- `{{ $env.VAR_NAME }}` — Environment variable
- `{{ operationKey }}` — Output of a specific operation by its key
- `{{ $accountability }}` — User/role context of who triggered it

---

## 2. COMPLETE API REFERENCE

### 2.1 Flows CRUD (REST API)

All operations go through `/flows` endpoint with an **Admin token**:
```
Authorization: Bearer <admin-token>
```

### GET /flows — List Flows
```http
GET /flows?access_token=<admin-token>&fields=id,name,status,trigger,operation,options
```

Response:
```json
{
  "data": [
    {
      "id": "flow-uuid-123",
      "name": "Send Welcome Email",
      "status": "active",
      "trigger": "event",
      "operation": "operation-uuid-456",
      "options": { "type": "action", "scope": ["items.create"], "collections": ["users"] }
    }
  ]
}
```

### POST /flows — Create Flow
```http
POST /flows?access_token=<admin-token>
Content-Type: application/json

{
  "name": "Flow Name",
  "icon": "bolt",
  "color": "#FFA439",
  "description": "What this flow does",
  "status": "active",
  "accountability": "all",
  "trigger": "event|webhook|schedule|operation|manual",
  "options": { /* trigger-specific config */ }
}
```

Response:
```json
{ "data": { "id": "new-flow-uuid", "name": "Flow Name", "status": "active" } }
```

### PATCH /flows/:id — Update Flow
```http
PATCH /flows/<flow-uuid>?access_token=<admin-token>
Content-Type: application/json

{
  "name": "Updated Name",
  "status": "inactive",
  "description": "Updated description",
  "operation": "first-operation-uuid"  // Sets the entry point operation
}
```

### DELETE /flows/:id — Delete Flow
```http
DELETE /flows/<flow-uuid>?access_token=<admin-token>
```

---

### 2.2 Operations CRUD (REST API)

Operations live under `/operations` endpoint:
```
Authorization: Bearer <admin-token>
```

### POST /operations — Create Operation
```http
POST /operations?access_token=<admin-token>
Content-Type: application/json

{
  "flow": "<flow-uuid>",     // Required: parent flow UUID
  "key": "my_operation",     // Required: unique key within the flow
  "type": "request",         // Required: operation type
  "name": "Display Name",    // Optional: human-readable name
  "position_x": 19,          // Required: grid X (use 19, 37, 55, 73, 91...)
  "position_y": 1,           // Required: grid Y (use 1, 19, 37, 55...)
  "options": { },            // Type-specific config
  "resolve": null,           // UUID of next operation on SUCCESS (null = end)
  "reject": null             // UUID of next operation on FAILURE (null = end)
}
```

Response:
```json
{ "data": { "id": "new-op-uuid", "key": "my_operation", "type": "request" } }
```

### PATCH /operations/:id — Update Operation (link operations)
```http
PATCH /operations/<op-uuid>?access_token=<admin-token>
Content-Type: application/json

{
  "resolve": "next-op-uuid",     // Link to next op on success
  "reject": "next-op-uuid",      // Link to next op on failure
  "options": { /* updated options */ }
}
```

### DELETE /operations/:id — Delete Operation
```http
DELETE /operations/<op-uuid>?access_token=<admin-token>
```

---

### 2.3 Correct Order to Create a Flow

```http
# STEP 1: Create the flow (no operations yet)
POST /flows?access_token=<admin-token>
{"name": "Email on Post Published", "trigger": "event",
 "options": {"type": "action", "scope": ["items.create"], "collections": ["posts"]}}
# → Returns: flow-uuid-123

# STEP 2: Create ALL operations with resolve=null, reject=null
POST /operations?access_token=<admin-token>
{"flow": "flow-uuid-123", "key": "check_status", "type": "condition",
 "position_x": 19, "position_y": 1,
 "options": {"filter": {"$trigger": {"payload": {"status": {"_eq": "published"}}}}},
 "resolve": null, "reject": null}
# → Returns: condition-uuid-456

POST /operations?access_token=<admin-token>
{"flow": "flow-uuid-123", "key": "send_email", "type": "mail",
 "position_x": 37, "position_y": 1,
 "options": {"to": ["admin@example.com"], "subject": "New post",
             "body": "{{$trigger.payload.title}}"},
 "resolve": null, "reject": null}
# → Returns: email-uuid-789

# STEP 3: Link operations by updating resolve/reject
PATCH /operations/condition-uuid-456?access_token=<admin-token>
{"resolve": "email-uuid-789"}    # condition met → send email
# No reject update → condition fails → flow ends silently

# STEP 4: Set the flow's entry point (first operation)
PATCH /flows/flow-uuid-123?access_token=<admin-token>
{"operation": "condition-uuid-456"}
```

**CRITICAL: After creating/updating/deleting via API, Directus auto-reloads flows in memory. No manual reload needed.**
- `FlowsService.createOne()` → calls `flowManager.reload()`
- `FlowsService.updateMany()` → calls `flowManager.reload()`
- `FlowsService.deleteMany()` → nullifies resolve/reject first, then calls `flowManager.reload()`

---

## 3. ALL TRIGGER TYPES — EXACT CONFIG

### 3.1 Event Hook Trigger

Fires when data changes in Directus collections.

```json
{
  "trigger": "event",
  "options": {
    "type": "action",                    // "action" (non-blocking) or "filter" (blocking)
    "scope": ["items.create"],           // Items: create, update, delete. Auth: login.
    "collections": ["posts", "pages"],   // Collections to monitor (for items.* scopes)
    "conditions": [                      // Optional: only fire when these conditions match
      { "status": { "_eq": "published" } }
    ]
  }
}
```

**Scope options:**
| Scope | Description |
|-------|-------------|
| `items.create` | Item created in collection |
| `items.update` | Item updated in collection |
| `items.delete` | Item deleted in collection |
| `auth.login` | User logs in (no `collections` needed) |

**Available in `{{ $trigger }}`:**
```json
{
  "event": "items.create",
  "collection": "posts",
  "key": "new-item-id",
  "payload": { "title": "New Post", "status": "published" },
  "keys": ["new-item-id"]
}
```

### 3.2 Webhook Trigger

Fires when an HTTP request is received. The URL is ALWAYS:
```
https://<directus-host>/flows/trigger/<flow-uuid>
```

```json
{
  "trigger": "webhook",
  "options": {
    "method": "POST",           // GET, POST (default), PUT, PATCH, DELETE
    "async": false,             // true = return immediately, false = wait for flow
    "return": "$last",          // Which operation output to return in response
    "cache": false              // Cache GET requests
  }
}
```

**CUSTOM WEBHOOK PATHS:** The `path` option exists in the UI but custom paths are NOT registered as Express routes. The actual URL is always `/flows/trigger/<flow-uuid>`. The `path` field is for display/documentation only.

**What the flow receives in `{{ $trigger }}`:**
```json
{
  "path": "/flows/trigger/flow-uuid",
  "query": { "param": "value" },
  "body": { /* POST data */ },
  "method": "POST",
  "headers": { "content-type": "application/json" }
}
```

### 3.3 Schedule Trigger (CRON)

Fires on a cron schedule.

```json
{
  "trigger": "schedule",
  "options": {
    "cron": "0 */15 * * * *"
  }
}
```

**CRON format:** `second minute hour day month weekday`
| Expression | Description |
|-----------|-------------|
| `0 */15 * * * *` | Every 15 minutes |
| `0 0 9 * * *` | Daily at 9 AM |
| `0 0 * * * *` | Every hour |
| `0 30 * * * *` | Every hour at :30 |
| `0 0 0 * * 0` | Every Sunday midnight |

### 3.4 Operation Trigger

Fires when another flow's "Trigger Operation" points to this flow.

```json
{
  "trigger": "operation",
  "options": {}  // No extra options needed
}
```

### 3.5 Manual Trigger

Fires when triggered manually from the Directus admin panel (on selected collection items).

```json
{
  "trigger": "manual",
  "options": {
    "collections": ["posts", "users"],   // Collections where the action is available
    "requireSelection": true             // Require item selection before triggering
  }
}
```

---

## 4. ALL OPERATION TYPES — EXACT CONFIG

### 4.1 Request (Webhook / Request URL)

Makes an HTTP request to an external URL.

```json
{
  "type": "request",
  "options": {
    "method": "POST",
    "url": "https://api.example.com/endpoint",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer my-token"
    },
    "body": { "field": "{{ $trigger.payload.value }}" },   // For JSON
    // OR for form-encoded:
    // "body": "field={{ $trigger.payload.value }}",  // For x-www-form-urlencoded
    "ignoreOutput": false          // Don't pass output to next operation
  }
}
```

**Content-Type handling:**
- `application/json` → body is serialized as JSON
- `application/x-www-form-urlencoded` → body must be a string (`key=value&key2=value2`)
- `multipart/form-data` → not supported via webhook operation

### 4.2 Transform

Transforms data using JSON template syntax (JavaScript-like expressions in `{{ }}`).

```json
{
  "type": "transform",
  "options": {
    "json": "{\n  \"title\": \"{{ $trigger.payload.title }}\",\n  \"status\": \"published\"\n}"
  }
}
```

The `json` field is a **string** containing JSON with `{{ }}` template placeholders. The templates use a sandboxed JavaScript engine and can access the full data chain.

### 4.3 Condition

Evaluates filter rules. Follows `resolve` path if condition matches, `reject` path if not.

```json
{
  "type": "condition",
  "options": {
    "filter": {
      "_and": [
        { "$trigger": { "payload": { "status": { "_eq": "published" } } } },
        { "$trigger": { "payload": { "featured": { "_eq": true } } } }
      ]
    }
  }
}
```

**Filter operators:** `_eq`, `_neq`, `_contains`, `_in`, `_nin`, `_gt`, `_gte`, `_lt`, `_lte`, `_null`, `_nnull`, `_and`, `_or`

### 4.4 Log

Logs a message to the Directus logs for debugging.

```json
{
  "type": "log",
  "options": {
    "message": "Processing item {{ $trigger.payload.id }} at {{ $trigger.payload.status }}"
  }
}
```

### 4.5 Sleep

Pauses flow execution for a specified duration.

```json
{
  "type": "sleep",
  "options": {
    "milliseconds": 5000
  }
}
```

### 4.6 Throw Error

Halts the flow and returns a custom error.

```json
{
  "type": "throw-error",
  "options": {
    "code": "CUSTOM_ERROR",
    "status": 400,
    "message": "Item is not published yet"
  }
}
```

### 4.7 Mail

Sends an email through Directus' configured mail transport.

```json
{
  "type": "mail",
  "options": {
    "to": ["{{ $trigger.payload.email }}"],
    "subject": "New article published: {{ $trigger.payload.title }}",
    "body": "Hello,\n\nA new article has been published: {{ $trigger.payload.title }}"
  }
}
```

### 4.8 Notification

Creates an in-app notification in Directus.

```json
{
  "type": "notification",
  "options": {
    "recipients": ["{{ $trigger.payload.author_id }}"],
    "title": "Article Published",
    "message": "Your article '{{ $trigger.payload.title }}' has been published"
  }
}
```

### 4.9 Item CRUD Operations

Create, Read, Update, or Delete items in any collection.

**Create Item:**
```json
{
  "type": "item-create",
  "options": {
    "collection": "notifications",
    "permissions": "$trigger",    // "$trigger" = use trigger's permissions, "$public" = public, "$full" = admin
    "payload": {
      "user": "{{ $trigger.payload.user_id }}",
      "message": "Welcome!"
    }
  }
}
```

**Read Items:**
```json
{
  "type": "item-read",
  "options": {
    "collection": "users",
    "query": {
      "filter": { "id": { "_eq": "{{ $trigger.payload.user_id }}" } },
      "fields": ["id", "email", "name"]
    }
  }
}
```

**Update Item:**
```json
{
  "type": "item-update",
  "options": {
    "collection": "orders",
    "key": "{{ $trigger.payload.id }}",
    "payload": { "status": "processed" }
  }
}
```

**Delete Item:**
```json
{
  "type": "item-delete",
  "options": {
    "collection": "temp_data",
    "key": ["item-id-1", "item-id-2"]
  }
}
```

### 4.10 Trigger Another Flow

Executes another flow.

```json
{
  "type": "trigger",
  "options": {
    "flow": "target-flow-uuid",
    "payload": { "data": "{{ transform_result }}" },
    "iterationMode": "parallel"    // "parallel" or "sequential"
  }
}
```

### 4.11 JWT

Creates or verifies JSON Web Tokens.

```json
{
  "type": "json-web-token",
  "options": {
    "action": "sign",              // "sign" or "verify"
    "secret": "{{ $env.JWT_SECRET }}",
    "payload": { "user_id": "{{ $trigger.payload.id }}" },
    "options": {
      "expiresIn": "24h"
    }
  }
}
```

### 4.12 Exec (Custom Code)

Runs custom JavaScript code in a sandbox.

```json
{
  "type": "exec",
  "options": {
    "code": "module.exports = async function() {\n  const result = $trigger.payload.items.map(i => i.id);\n  return { count: result.length, ids: result };\n}"
  }
}
```

---

## 5. OPERATION CHAINING (RESOLVE/REJECT)

Every operation has TWO output paths:

```
Operation
    │
    ├── ✓ resolve → next operation UUID (on success)
    │
    └── ✗ reject → next operation UUID (on failure/condition false)
```

### Linking rules:
- If `resolve: null` → flow ends on success
- If `reject: null` → flow ends on failure (or silently continues)
- Operations MUST be created BEFORE they can be referenced in resolve/reject
- Use UUIDs (36 chars) NOT operation keys

### Example flow with branching:

```
          [Trigger: Event Hook - items.create on posts]
                      │
                      ▼
              [check_status: Condition]
             ✓                     ✗
         (published)           (not published)
             │                      │
             ▼                      ▼
    [send_email: Mail]      [log_skip: Log]
             │                      │
             ▼                      ▼
          (end)                 (end)
```

**API Config:**
```json
// Create send_email operation
{ "flow": "flow-uuid", "key": "send_email", "type": "mail",
  "position_x": 37, "position_y": 1,
  "options": { "to": ["admin@example.com"], "subject": "Published!",
               "body": "{{ $trigger.payload.title }}" },
  "resolve": null, "reject": null }

// Create log_skip operation
{ "flow": "flow-uuid", "key": "log_skip", "type": "log",
  "position_x": 37, "position_y": 19,
  "options": { "message": "Skipped unpublished post: {{ $trigger.payload.id }}" },
  "resolve": null, "reject": null }

// Create condition operation (links both)
{ "flow": "flow-uuid", "key": "check_status", "type": "condition",
  "position_x": 19, "position_y": 1,
  "options": { "filter": { "$trigger": { "payload": { "status": { "_eq": "published" } } } } },
  "resolve": "send_email-uuid",    // → send email on published
  "reject": "log_skip-uuid"        // → log skip on draft
}
```

---

## 6. GRID POSITIONING (VISUAL LAYOUT)

Operations use `position_x` and `position_y` for the visual canvas. Standard steps:

```
position_x: 19, 37, 55, 73, 91, 109  (horizontal steps)
position_y: 1, 19, 37, 55, 73        (vertical branching)
```

```
           x=19       x=37       x=55
        ┌─────────────────────────────────
  y=1   │  [op1]  →  [op2]  →  [op3]
        │
 y=19   │             [op2b]  (branch)
        │
 y=37   │             [op2c]  (another branch)
```

---

## 7. PERMISSIONS & VISIBILITY

### Who can see Flows in the UI?

The **Flows section** in the Directus admin panel requires:

| Role | Can see Flows? | Can manage Flows? |
|------|---------------|-------------------|
| **Administrator** | ✅ Yes | ✅ Full CRUD |
| **Developer** | ✅ Yes | ✅ Full CRUD (read/write on system collections) |
| **Custom Role** | ❌ No, unless explicit `read` permission on `directus_flows` | ❌ No |

**If you're Administrator and still can't see the Flows section:**
1. Check that you're looking in **Settings > Flows** (not the old Webhooks section)
2. The old **Webhooks** section was deprecated in Directus 10+ — all webhooks migrated to Flows
3. Check if the Directus instance has the Flows module enabled (it's enabled by default)
4. Refresh the page or clear browser cache

### Why flows created via API might not show in UI:

- **Flows are cached in memory** by the FlowManager. Any create/update/delete via API auto-reloads the cache (`flowManager.reload()`) — so API-created flows should appear immediately.
- If flows still don't appear: log out, log back in, or force-refresh the admin page (Ctrl+Shift+R).
- If the admin page shows a blank Flows section: check the browser console for JS errors.

---

## 8. DEBUGGING & TROUBLESHOOTING

### Check if a flow is correctly registered:

```bash
# List all flows with details
curl -s "https://studio.nayo.chat/flows?access_token=<admin-token>&fields=id,name,status,trigger,options,operation" | python3 -m json.tool

# Get specific flow operations
curl -s "https://studio.nayo.chat/operations?access_token=<admin-token>&filter[flow][_eq]=<flow-uuid>&fields=id,key,type,options,resolve,reject" | python3 -m json.tool
```

### Common problems:

| Problem | Cause | Solution |
|---------|-------|----------|
| Flow doesn't trigger | Event scope wrong, collections mismatch, conditions too strict | Check `scope`, `collections`, `conditions` in flow options |
| Webhook returns 404 | Wrong URL | Use `/flows/trigger/<uuid>` not a custom path |
| Operation not executing | Wrong operation UUID in `resolve/reject`, or `flow.operation` not set | Verify `flow.operation` UUID, update `resolve/reject` |
| 500 error in flow | Bad template syntax in `{{ }}`, or operation type missing required options | Check operation options JSON, escape properly |
| Flow UI shows no operations | Browser cache, or operations created out of order | Force refresh, check API response |
| "Flow not found" error | Flow UUID wrong, or flow is inactive | Check UUID, set `status: "active"` |
| Template `{{ }}` not rendering | Wrong syntax or bad variable name | Use `$trigger.payload.field`, check case sensitivity |
| Resolve/Reject not working | UUID doesn't exist, or circular reference | Ensure target operation UUID exists, no cycles |
| Operations created but flow doesn't run | `flow.operation` not set to first operation UUID | PATCH `/flows/{id}` with `{"operation": "first-op-uuid"}` |
| Flow created via API not in UI | FlowManager cache not refreshed | Wait ~1s for `flowManager.reload()`, then refresh page |

### Stripe/PayPal Webhook Setup:

1. Create a flow with `trigger: "webhook"`, `method: "POST"`
2. Note the flow UUID from the API response
3. In Stripe dashboard → Webhooks → Add endpoint:
   ```
   URL: https://studio.nayo.chat/flows/trigger/<flow-uuid>
   ```
4. In the flow, add a **request operation** to forward the webhook to FastAPI:
   ```json
   {
     "type": "request",
     "options": {
       "method": "POST",
       "url": "https://api.nayo.chat/payments/webhook",
       "headers": {
         "Content-Type": "application/x-www-form-urlencoded",
         "Authorization": "Bearer nyo-flow-secret-7a9f3c2b8d1e4f5a6c7b8d9e0f1a2b3c"
       },
       "body": "data={{ $trigger.body | json_encode }}"
     }
   }
   ```

---

## 9. COMPLETE QUICK-START TEMPLATES

### Template: Forward Webhook to External API
```json
// 1. Create flow
POST /flows?access_token=<admin-token>
{
  "name": "Payment Webhook",
  "icon": "payments",
  "color": "#27AE60",
  "status": "active",
  "trigger": "webhook",
  "options": { "method": "POST", "async": false }
}

// 2. Create transform (extract & reshape payload)
POST /operations?access_token=<admin-token>
{
  "flow": "<flow-uuid>",
  "key": "extract_data",
  "type": "transform",
  "position_x": 19, "position_y": 1,
  "options": { "json": "{\n  \"payload\": {{ $trigger.body | json }}\n}" },
  "resolve": null, "reject": null
}

// 3. Create request (forward to FastAPI)
POST /operations?access_token=<admin-token>
{
  "flow": "<flow-uuid>",
  "key": "forward_to_fastapi",
  "type": "request",
  "position_x": 37, "position_y": 1,
  "options": {
    "method": "POST",
    "url": "https://api.nayo.chat/payments/webhook",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer nyo-flow-secret-7a9f3c2b8d1e4f5a6c7b8d9e0f1a2b3c"
    },
    "body": { "data": "{{ extract_data.payload }}" }
  },
  "resolve": null, "reject": null
}

// 4. Link: extract_data → forward_to_fastapi
PATCH /operations/<extract-op-uuid>?access_token=<admin-token>
{ "resolve": "<forward-op-uuid>" }

// 5. Set entry point
PATCH /flows/<flow-uuid>?access_token=<admin-token>
{ "operation": "<extract-op-uuid>" }
```

### Template: Event Hook → AI Chat Execute
```json
POST /flows?access_token=<admin-token>
{
  "name": "Chat AI Execution",
  "icon": "chat",
  "color": "#2D9CDB",
  "status": "active",
  "trigger": "event",
  "options": {
    "type": "action",
    "scope": ["items.create"],
    "collections": ["ai_messages"],
    "conditions": [{ "role": { "_eq": "user" } }]
  }
}

// Single request operation
POST /operations?access_token=<admin-token>
{
  "flow": "<flow-uuid>",
  "key": "execute_ai",
  "type": "request",
  "position_x": 19, "position_y": 1,
  "options": {
    "method": "POST",
    "url": "https://api.nayo.chat/chat/execute",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer nyo-flow-secret-7a9f3c2b8d1e4f5a6c7b8d9e0f1a2b3c"
    },
    "body": {
      "user_id": "{{ $trigger.payload.user_created }}",
      "workspace_id": "{{ $trigger.payload.workspace }}",
      "payload": { "key": "{{ $trigger.key }}",
                   "message": "{{ $trigger.payload.message }}" }
    }
  },
  "resolve": null, "reject": null
}

// Set entry point
PATCH /flows/<flow-uuid>?access_token=<admin-token>
{ "operation": "<execute-op-uuid>" }
```

### Template: Event Hook → Token Encryption (MCP)
```json
POST /flows?access_token=<admin-token>
{
  "name": "MCP Token Encryption",
  "icon": "lock",
  "color": "#F2994A",
  "status": "active",
  "trigger": "event",
  "options": {
    "type": "action",
    "scope": ["items.create"],
    "collections": ["mcp_connections"]
  }
}

// Single request operation
POST /operations?access_token=<admin-token>
{
  "flow": "<flow-uuid>",
  "key": "encrypt_tokens",
  "type": "request",
  "position_x": 19, "position_y": 1,
  "options": {
    "method": "POST",
    "url": "https://api.nayo.chat/mcp/connections/tokens",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer nyo-flow-secret-7a9f3c2b8d1e4f5a6c7b8d9e0f1a2b3c"
    },
    "body": {
      "user_id": "{{ $trigger.payload.user_created }}",
      "workspace_id": "{{ $trigger.payload.workspace }}",
      "payload": {
        "key": "{{ $trigger.key }}",
        "provider_key": "{{ $trigger.payload.provider_key }}",
        "access_token": "{{ $trigger.payload.access_token }}",
        "api_key": "{{ $trigger.payload.api_key }}"
      }
    }
  },
  "resolve": null, "reject": null
}
```

### Template: Credit Add on Payment Complete
```json
POST /flows?access_token=<admin-token>
{
  "name": "AI Credit Add on Payment",
  "icon": "add_circle",
  "color": "#27AE60",
  "status": "active",
  "trigger": "event",
  "options": {
    "type": "action",
    "scope": ["items.create", "items.update"],
    "collections": ["payment_transactions"],
    "conditions": [{ "status": { "_eq": "completed" } }]
  }
}
```

---

## 10. ENVIRONMENT VARIABLES IN FLOWS

Flows can access environment variables set at the Directus instance level:

```
{{ $env.DIRECTUS_FLOW_SECRET }}
{{ $env.DIRECTUS_URL }}
```

**Note for Directus 11:** Environment variables must be set at the **infrastructure level** (Coolify, Docker), NOT via the API. Directus 11 removed the `project_env` PATCH endpoint. If you need a shared secret between Directus and another service:

1. Set the env var in your hosting platform (Coolify → Service → Env Vars)
2. Use `{{ $env.MY_SECRET }}` in flow operation headers
3. If the env var is not set, **the `{{ $env.VAR }}` template will be empty** — no error, just blank

**Workaround for missing env vars:** Hardcode the secret directly in the flow operation's Authorization header instead of using `{{ $env }}`.

---

## 11. WEBHOOK TRIGGER — CRITICAL FACTS

1. **The URL is ALWAYS** `https://<directus>/flows/trigger/<flow-uuid>`
2. The `path` option in flow settings is **display only** — NOT used for routing
3. Old Directus Webhooks (`directus_webhooks` table) were **deprecated and migrated to Flows** in Directus 10+
4. To test a webhook flow: `curl -X POST "https://studio.nayo.chat/flows/trigger/<flow-uuid>" -H "Content-Type: application/json" -d '{"test": true}'`
5. Webhook flows can be triggered by both `GET` and `POST` (depending on configured method)
6. For `async: false`, the response includes the flow's result from the configured `return` operation
7. For `async: true`, the flow runs in background and returns immediately
