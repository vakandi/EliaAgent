# Chat tool-call parsing & special UI cards (THE critical phase)

The AI assistant runs in OpenCode sessions inside the backend container. It has MCP
tools available; when it calls a tool, the backend relays the tool call to the
frontend, which renders it via `ToolResultRenderer` (`components/app/tool-renderer.tsx`).

## The allowlist (frontend special rendering)

```ts
const ALLOWLIST_PREFIXES = [
  "realestate_leads_results",     // → results table (scored addresses)
  "realestate_map_results",       // → MapView (parcels/PLU/risks)
  "realestate_company_graph",     // → CompanyGraphPanel (officers/ownership)
  "realestate_market_report",     // → MarketReportPanel (comps, price/m²)
];
```

- Tool names matching a prefix render a **special bordered card** with the rich
  component. Everything else falls back to the generic "Appel outil — <name>" bubble
  with a JSON `pre` of args.
- `ToolCallBubble` wraps special cards in `rounded-2xl border border-primary/15` — a
  reliable DOM signal for "the parser worked".
- Tool payloads for special prefixes include a `credit_cost` field; when balance is
  insufficient the frontend must fall back to generic bubble + FeatureLock notice
  (that fallback is ALSO a valid test result — the gating works).

## MCP providers available to the agent

- Backend domain MCP: `immosignal_deploy` (`fastapi/mcp_servers/immosignal_deploy/server.py`,
  prefix `immosignal_deploy_*`).
- The France open-data MCPs (DVF, permits, DPE, Sirene/RNE, BODACC, Géorisques) and the
  user-token leads MCP are the roadmap — `fastapi/app/core/mcp_providers.json` is the
  registry. **Before running card tests, verify the providers exist**:
  `GET https://api.immobilia.ca/mcp/providers`. If the real-estate tools aren't
  registered, the AI cannot call them — report that as the root cause instead of
  chasing a frontend bug.

## Forcing prompts (send these to make the AI call the right tool)

Send on `/chat`, one at a time, waiting for full completion between each. French
prompts map to the French product UI.

| # | Prompt (user message) | Expected tool prefix | Expected card |
|---|----------------------|----------------------|---------------|
| 1 | "Montre-moi sur une carte les terrains constructibles autour de Paris 15e, avec les zones PLU." | `realestate_map_results_*` | MapView card |
| 2 | "Qui dirige la société qui possède ce patrimoine ? Explore le graphe de dirigeants et le patrimoine des sociétés de cette personne." (mention/attach a SIREN if you have one, e.g. from seed data) | `realestate_company_graph_*` | CompanyGraphPanel card |
| 3 | "Fais une étude de marché sur le secteur de Nantes — prix au m², tendances, comparables." | `realestate_market_report_*` | MarketReportPanel card |
| 4 | "Quelles adresses à Nantes ont le meilleur score de vente ? Classe-les." | `realestate_leads_results_*` | results table / leads card |

Use the free anonymous credit on prompt #1 (most representative); then continue with
an authenticated test user for #2–#4.

## Verification protocol (per prompt)

1. Fill the chat input (React controlled-input pattern from browser-test-features),
   submit, and record the send in `window.__api_log`.
2. Wait for turn completion: poll for the response bubble / card presence
   (`browser_wait_for_selector` on the card container or a timeout poll via
   `browser_evaluate`).
3. Snapshot: `browser_snapshot(sessionId, maxDepth=4)` — confirm structure.
4. JS check — verify presence + data + correct component:

```js
(() => {
  const cards = [...document.querySelectorAll('[class*="rounded-2xl"]')];
  return JSON.stringify({
    url: location.href,
    specialCards: cards.length,
    cardTexts: cards.map(c => c.innerText?.substring(0, 150)),
    hasMapCanvas: !!document.querySelector('canvas, [class*="leaflet"], [class*="maplibre"]'),
    hasGraph: !!document.querySelector('[class*="node"], [class*="siren"], [class*="dirigeant"]'),
    hasReportTable: !!document.querySelector('table, [class*="market"], [class*="étude"]'),
    hasLeadsTable: [...document.querySelectorAll('table')].map(t => t.innerText?.substring(0, 120)),
    genericToolBubbles: [...document.querySelectorAll('pre')].map(p => p.textContent?.substring(0, 150)),
    reasoningVisible: document.body.innerText.includes('réflexion') || document.body.innerText.includes('raisonnement') || !!document.querySelector('[class*="reason"], [class*="todo"]')
  });
})();
```

5. Network: read `window.__api_log`, filter to the chat phase:
   - `POST /chat/execute` → 200 (the turn).
   - `GET /chat/session/{id}/todo-stream` → 200 (reasoning stream).
   - Directus reads on `realestate_*` → 200 (the card data source).
   - No 4xx/5xx/CORS; nothing > 2000ms (except the initial execute which legitimately
     takes seconds — flag only if > 60s).
6. Assert mapping: tool name from the bubble/log → expected prefix → rendered component.
   Mismatch = parsing/allowlist bug.

## Locked-fallback verification (per forced prompt)

When the identity balance is below the card's `credit_cost`, the frontend must NOT
render the rich card — it must fall back to the generic tool bubble AND show the
`FeatureLock` overlay (never a dead-end, never a bare error). Test this on the same
prompts by forcing the low-balance state first (see FRONTEND-PAGES.md paywall section):

```js
// anon at 0 credits → locked + "Créer un compte gratuit"
localStorage.setItem('immosignal.credits.v1', JSON.stringify({kind:'anon', credits:0}));
location.reload();
```

Then after the forced prompt completes, assert:
1. NO special card container (`[class*="border-primary/15"]` rich component) is present.
2. `FeatureLock` container IS present (`[class*="gradient-soft"]` + lock icon + cost line
   matching `/<FeatureLabel> — N crédits/`).
3. CTA matches the identity state: "Créer un compte gratuit" (anon) / "Voir les plans"
   (authed 0 credits).
4. Clicking the CTA works: anon → grants +2 credits, overlay disappears, card renders
   on the retry; authed → navigates to `/pricing`. Record snapshot before/after.
5. Repeat with `{"kind":"user","plan":"free","credits":0}` to cover the authed state.

Log per-feature pass/fail for the lock + both CTAs in the report.

## Failure signatures

| Symptom | Likely root cause |
|---------|-------------------|
| AI answers in text but no tool call at all | Provider missing from `mcp_providers.json`, or the agent identity/prompt doesn't encourage tool use |
| Tool call happened (seen in `/chat/execute` payload or backend logs) but generic bubble shown | Frontend allowlist missing the prefix, or payload `credit_cost` gate blocked rendering |
| Card renders but empty/no data | Directus `realestate_*` collection empty (polling/seed issue — see POLLING.md) |
| Reasoning/todo never visible during turn | todo-stream SSE not consumed — check `GET /chat/session/{id}/todo-stream` in network log |
| Chat hangs > 60s, no response | OpenCode sandbox down — check `coolify-logs` + `/sandbox/stats` |
