# Backend endpoints — verification cheat sheet

Backend base: `https://api.immobilia.ca/` (FastAPI + OpenCode on Coolify).
Directus: `https://dash.immobilia.ca/`.

## Health

```bash
curl -s https://api.immobilia.ca/health | python3 -m json.tool
# expect 200, status ok, redis connected
```

## Chat (the core feature)

| Method/Path | Purpose |
|---|---|
| `POST /chat/execute` | Execute an AI turn (message → MCP tool routing → response). Body contains session id, message, workspace. |
| `GET /chat/session/{session_id}/todo-stream` | SSE stream of the agent's todo/reasoning while a turn is running. The frontend consumes this to display agent reasoning. |
| `GET /chat/session/{session_id}/mcp-stale` | Whether the session's MCP tools are stale (reconnect signal). |

Verify pattern:
1. Send a message via the UI (JS-first) → `window.__api_log` must show `POST /chat/execute` → 200.
2. During the run, the UI must show reasoning/todo (fed by the todo-stream). Confirm via DOM query: elements containing "reasoning", "todo", "en train de", etc.
3. After completion, a tool-call bubble or special card must be in the DOM (see CHAT-TOOLCARDS.md).

## Credits / paywall

| Method/Path | Purpose |
|---|---|
| `POST /ai-credits/add` | Add credits to a balance |
| `POST /ai-credits/use` | Deduct credits (called server-side before/after AI turn) |

Balance/usage data also lives in Directus collections (`ai_credit_balances`,
`ai_credit_transactions`) — query via Directus REST with the service/admin token from
`AGENTS.md` when you need the source of truth. Paywall trigger: chat response with
`paywall: true` when `credits_remaining <= 0`.

## Polling pipeline

```bash
curl -s "https://api.immobilia.ca/poll/status?workspace=immosignal" | python3 -m json.tool
curl -s -X POST "https://api.immobilia.ca/poll/trigger/mvp_parcels?workspace=immosignal" | python3 -m json.tool
curl -s "https://api.immobilia.ca/poll/configs?workspace=immosignal" | python3 -m json.tool
```

See POLLING.md for the 6 jobs and collections.

## Payments

| Method/Path | Purpose |
|---|---|
| `POST /payments/create-checkout` | Create checkout (Bonzai primary → Whop fallback) |
| `POST /payments/webhook` | Generic webhook receiver |
| `POST /payments/webhook/bonzai` | Bonzai webhook (unsigned — non-guessable URL) |
| `POST /payments/webhook/whop` | Whop webhook (HMAC-SHA256, verify `X-Whop-Signature`) |

Do not send real money in a test run — verify the endpoint exists and responds with a
validation error on empty body (expected 422), which proves it's wired.

## MCP integration

| Method/Path | Purpose |
|---|---|
| `GET /mcp/providers` | List configured MCP providers (the AI's toolbelt) |
| `GET /mcp/providers/{provider_key}` | Provider detail |
| `POST /mcp/connections` | Create connection |
| `POST /mcp/connections/tokens` | Encrypt/decrypt tokens (server-side secrets) |
| `GET /mcp/connections/status` | Connection health |

Verify `GET /mcp/providers` returns the ImmoSignal domain providers — the AI must have
access to the real-estate MCP tools for the chat cards to ever render. If a provider is
missing from this list, the chat will never be able to call the tool regardless of what
the user types.

## Sandbox (OpenCode sessions)

`POST /sandbox/session/create`, `/session/status`, `/session/stop`, `/sessions`, `/stats`.
The chat runs inside sandboxed OpenCode sessions — when chat fails, check
`/sandbox/session/status` and `/sandbox/stats` before assuming a frontend bug.

## Directus data verification (read-only)

With the token from `AGENTS.md` (service or admin):

```bash
TOKEN="<DIRECTUS_SERVICE_TOKEN>"
curl -s "https://dash.immobilia.ca/items/realestate_parcels?limit=1" -H "Authorization: Bearer $TOKEN"
curl -s "https://dash.immobilia.ca/items/realestate_company_graphs?limit=1" -H "Authorization: Bearer $TOKEN"
curl -s "https://dash.immobilia.ca/items/realestate_market_reports?limit=1" -H "Authorization: Bearer $TOKEN"
# ... same for realestate_risk_sites, realestate_street_views, realestate_successions,
#     properties, transactions, ai_credit_balances
```

Note: Directus meta/aggregate params are NOT supported on this instance — rely on
`data.length` or `limit=1` presence checks.
