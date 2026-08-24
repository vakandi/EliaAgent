---
name: indicefoncier-fulltesting
description: >-
  Full-stack end-to-end testing of the ImmoSignal platform (indice.immobilia.ca):
  frontend pages, FastAPI backend, AI chat system, MCP tool-call rendering, special
  UI cards (map results, company graph, market report, leads table), background
  polling pipeline (Géorisques/INSEE/BODACC/DVF/Mapillary/Cadastre → realestate_*
  Directus collections), credits/paywall and network health. Uses browser-test-features
  (parallel-browser-mcp, JS-first, network interception) + coolify-logs (agent
  verification in production logs). Make sure to use this skill whenever the user asks
  to "test all features", "test indice", "full testing", "test the chat AI", "verify
  the tool cards", "check the maps data", "is the agent working", "test frontend and
  backend", "vérifie tout", "test complet", or wants a full regression pass of the
  ImmoSignal product against MVP.md / MVP_v2.md — even if they don't explicitly name
  the skill. Baseline feature specs: MVP.md and MVP_v2.md in the repo root.
---

# IndiceFoncier Full Testing

Full-stack E2E test suite for the ImmoSignal product (frontend + backend + AI chat +
MCP tool cards + background data pipeline). Runs against **production** by default
(`https://indice.immobilia.ca/`, backend `https://api.immobilia.ca/`, Directus
`https://dash.immobilia.ca/`).

## Skills to load first

Load these skills at the start of every run — they are the toolbelt:

1. `browser-test-features` — parallel-browser-mcp, JS-first testing, network interceptor
2. `coolify-logs` — verify the AI agent actually ran in the backend logs
3. `mcp-cli` — only if MCP/Coolify/Directus access via mcp-cli is needed

## Reference files (read on demand, never all at once)

| File | Read when |
|------|-----------|
| `references/POLLING.md` | Checking background data pipeline (maps, risk, reports data present) |
| `references/BACKEND-ENDPOINTS.md` | Verifying backend endpoints (chat, credits, poll, payments) |
| `references/FRONTEND-PAGES.md` | Testing frontend pages & components |
| `references/CHAT-TOOLCARDS.md` | Testing AI tool-call parsing + special UI cards (THE critical part) |
| `references/MVP-FEATURES.md` | Building the feature checklist per MVP.md / MVP_v2.md |

## Ground rules

- **Evidence before assertions**: every "works" claim needs a curl body, snapshot,
  DOM query result, or log excerpt. Never say "it works" without proof.
- **JS-first in the browser**: install the network interceptor immediately after
  first navigation (see browser-test-features). Read `window.__api_log` after every
  significant action. Any non-2xx, CORS error, missing request, or >2s response is a bug.
- **One phase at a time**; run in order. Phase 4 (tool cards) is the deepest — budget
  time there.
- **Never burn production credits blindly**: anonymous IP gets `ANON_FREE_CREDITS` (default 1).
  Plan chat tests so the free credit is used on the most valuable prompt (a tool-card
  forcing prompt), then switch to an authenticated test user for the rest. If you hit
  the paywall mid-test, that's a PASS for Phase 6 — document it.
- Close the browser session at the end (`parallel-browser-mcp_close_session`).

## Test phases

### Phase 0 — Infrastructure health (no browser)

```bash
curl -s https://api.immobilia.ca/health | python3 -m json.tool          # expect 200 + status ok
curl -s -o /dev/null -w "%{http_code}" https://dash.immobilia.ca/server/health   # Directus 200
curl -s -o /dev/null -w "%{http_code}" https://indice.immobilia.ca/     # frontend 200
```

Record all three. Any failure → stop, report, do not proceed.

### Phase 1 — Background polling pipeline (data for maps/info)

Read `references/POLLING.md`. Verify the pipeline that feeds the maps and info panels:

```bash
curl -s "https://api.immobilia.ca/poll/status?workspace=immosignal" | python3 -m json.tool
```

- Confirm the 6 `mvp_*` jobs exist and `enabled=true`.
- Confirm `last_polled_at` is recent (< 2 × interval) — if never polled, run
  `POST /poll/trigger/{event_type}?workspace=immosignal` per job.
- Confirm the `realestate_*` Directus collections are **not empty** (the frontend maps
  and info panels read these). Use the Directus REST API with the service/admin token
  from `AGENTS.md`: `GET https://dash.immobilia.ca/items/realestate_parcels?limit=1` etc.
- Note: `docs/BACKGROUND_FETCHING.md` describes the **obsolete** legacy polling system
  (Vercel/Coolify/Discord/Mail/AI sessions). Ignore it for this run — the current
  system is BACKGROUND_POLLING.md only. Do not test legacy `mgmt_*` pollers as MVP features.
- Minimum data presence check: `realestate_parcels`, `realestate_risk_sites`,
  `realestate_company_graphs`, `realestate_market_reports`, `realestate_street_views`,
  `realestate_successions` + core `properties`/`transactions` each ≥ 1 item.

### Phase 2 — Frontend pages smoke test

Read `references/FRONTEND-PAGES.md`. Start a browser session, navigate, interceptor,
then walk the pages: `/`, `/chat`, `/map`, `/profile`, `/pricing`, `/claim`,
`/payment-success`, `/company/<siren>`, `/data-sources`, `/gdpr`. For each page:
screenshot + DOM presence of the key sections listed in the reference + check
`window.__api_log` for errors.

### Phase 3 — AI chat E2E (backend verified via Coolify logs)

Read `references/BACKEND-ENDPOINTS.md` and load `coolify-logs`.

1. On `/chat`, send a message (JS-first fill + submit — see browser-test-features
   for controlled-input patterns).
2. Confirm the assistant streams a text response in the UI (poll for the response
   bubble, don't assume instant).
3. **Verify the agent in the backend logs** (coolify-logs skill):
   - Find the FastAPI app UUID for ImmoSignal (check `AGENTS.md`; verify with
     `mcp-cli call coolify list_applications` if unsure).
   - `mcp-cli call coolify application_logs '{"uuid":"<UUID>","lines":100}'`
   - Look for the chat execution trace: `chat.*` / `opencode` session start,
     `ai_service`/`chat_engine` entries, tool-call entries, and any ERROR/CRITICAL/Traceback.
   - Assert: the message reached the backend, the agent session ran, and the response
     was produced — evidenced by log lines, not by the UI alone.
4. Confirm the AI **tools + reasoning** are displayed in the UI (tool-call bubbles,
   reasoning blocks) — see Phase 4 for the full card verification.

### Phase 4 — MCP tool parsing + special UI cards (the critical phase)

Read `references/CHAT-TOOLCARDS.md`. Send the forcing prompts one by one (each costs
credits — use the free credit on the first, then an authenticated user). For each:

1. Send the prompt.
2. Wait for the assistant turn to complete (network idle + response bubble).
3. **Snapshot + JavaScript** to confirm the special card is present, has the right
   data, and the correct component rendered:
   ```js
   JSON.stringify({
     url: location.href,
     specialCard: !!document.querySelector('[class*="rounded-2xl"] [class*="uppercase"]'),
     hasMap: !!document.querySelector('[class*="leaflet"], [class*="maplibre"], canvas'),
     hasGraph: !!document.querySelector('[class*="node"], [class*="graph"], [class*="siren"]'),
     hasReport: !!document.querySelector('[class*="market"], [class*="étude"], table'),
     toolCalls: [...document.querySelectorAll('pre')].map(p => p.textContent?.substring(0, 120)),
     text: document.body?.innerText?.substring(0, 400)
   });
   ```
   Use `browser_snapshot` (maxDepth 4) as the structured companion to the JS query.
4. Pull `window.__api_log` and verify: the chat execute call succeeded, the Directus
   `realestate_*` reads fired (the card data source), and no 4xx/5xx/CORS.
5. Map the tool name to the expected prefix (`realestate_map_results_*` → MapView,
   `realestate_company_graph_*` → CompanyGraphPanel, `realestate_market_report_*` →
   MarketReportPanel, `realestate_leads_results_*` → results table) and assert the
   rendered component matches.

If a card doesn't render (falls back to the generic "Appel outil" bubble), the tool
parsing or the frontend allowlist is broken — file it as a bug with the exact tool
name seen in `window.__api_log` / the bubble.

### Phase 5 — Network health (parallel browser, every request)

Throughout Phases 2–4, the interceptor is logging every fetch/XHR. Before finishing:
- List all requests with status ≥ 400, any CORS/TypeError, any duration > 2000ms.
- Cross-check that the `/chat/execute` call and the `realestate_*` Directus calls
  appear exactly when expected (chat send → execute; card render → realestate reads).
- Reset `window.__api_log = []` between phases so the log stays attributable.

### Phase 6 — Credits & paywall (on EVERY feature, both identity states)

Read `references/BACKEND-ENDPOINTS.md` (ai-credits) and `references/FRONTEND-PAGES.md`
(FeatureLock/PaywallModal section). The rule from MVP.md §6.3 + MVP_v2 §7.4: **never a
dead-end** — every locked feature shows a locked overlay with an immediate path:
"Créer un compte gratuit" (anon, grants `SIGNUP_FREE_CREDITS`) or "Voir les plans"
(authed at 0 credits, upgrade path). Test BOTH identity states on EVERY gated feature.

**Features to gate-test** (costs from `lib/credits.ts`): chat (1), environmental
overlays (2), successions factor (2), company graph (3), street view (1), map search (1),
map overlay extra (2), market report (3), market report PDF (5).

**Deterministic state control (do NOT burn credits to reach 0):** the client gate is
mirrored in localStorage — set the identity directly, then test the UI:

```js
// anon, 0 credits → locked state + signup CTA
localStorage.setItem('immosignal.credits.v1', JSON.stringify({kind:'anon', credits:0}));
// authed free user, 0 credits → locked state + upgrade CTA (no signup)
localStorage.setItem('immosignal.credits.v1', JSON.stringify({kind:'user', plan:'free', credits:0}));
location.reload();
```

Per feature (map overlays, company graph, market report, street view, leads/CSV export,
PDF export), with each identity state:

1. Force the feature to render (see CHAT-TOOLCARDS.md prompts, or open the relevant page).
2. Assert the **FeatureLock overlay** is in the DOM — not an error, not a dead-end:
   - lock container: `[class*="rounded-2xl"] [class*="gradient-soft"], [class*="bg-grid"]`
   - cost badge: text matching `/<feature label> — N crédits/`
   - anon: button "Créer un compte gratuit" present; text mentions "+2 crédits"
   - authed 0 credits: button "Voir les plans" present; text mentions "Crédits insuffisants"
3. **Anon state**: click "Créer un compte gratuit" → identity flips to
   `{kind:'user', plan:'free', credits:2}` in localStorage and the feature unlocks
   (overlay disappears). Snapshot before/after.
4. **Authed 0-credit state**: click "Voir les plans" → navigates to `/pricing` or opens
   the pricing section (checkout buttons Bonzai/Whop). No signup step is shown for an
   authed user.
5. **Chat-level paywall modal** (`paywall: true` response when balance hits 0): send a
   message with 0 credits → modal in DOM with the same two-state behavior
   ("Créer un compte gratuit" / "Voir les plans" depending on identity). Snapshot + JS.
6. Network check: any directus/chat calls around the gate action return 2xx; the gate is
   client-mirrored so a 402 is NOT expected — the server enforces via `paywall: true`
   payload in the chat response only.

If a feature shows a bare error instead of the FeatureLock overlay, or the CTA does not
unlock/navigate — that is a bug (paywall broken on that feature). Log every feature
tested with pass/fail in the report.

## Report template

Write the report to `docs/TESTING.md` (repo root `docs/`, append/overwrite as a dated
section). Always use this structure:

```markdown
## Test Report — <date>

### Summary
- Phases run: 0–6 (or subset)
- Issues found: N open / M fixed
- API calls monitored: X (errors: Y)

### Phase results
| Phase | Verdict | Evidence |
|-------|---------|----------|
| 0 Infra | PASS/FAIL | curl bodies |

### Bugs Found
#### BUG-NNN: <short title>
- Severity, Status
- What / Expected / Actual
- API call: METHOD /path → status
- Evidence: network log, snapshot, log excerpt
- Root cause + proposed fix (file, line, exact change)

### Working Features
- list

### Network Summary
| Endpoint | Method | Status | Duration | Issue |
|----------|--------|--------|----------|-------|
```

## Completion criteria

A run is only "done" when: all phases attempted, evidence captured for each phase,
every bug has a root cause + proposed fix, and the report is written to `docs/TESTING.md`.
If a phase was skipped (e.g. paywall exhaustion), say so explicitly in the report.
