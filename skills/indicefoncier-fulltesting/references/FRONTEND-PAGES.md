# Frontend pages & components

Base URL: `https://indice.immobilia.ca/` (TanStack Start, React, Tailwind).
Route files live in `immosignal-frontend/src/routes/`. Components in
`immosignal-frontend/src/components/app/`. No `data-testid` attributes exist — use
roles, visible text (French), and classname patterns.

## Page inventory

| Route | File | Key sections to verify |
|-------|------|------------------------|
| `/` | `routes/index.tsx` | Hero + live search box (type address → "Rechercher"), "How it works" (3 steps), pricing cards, footer. Known bug history: hero search must navigate to `/chat` with query pre-filled (BUG-001). |
| `/chat` | `routes/chat.tsx` → `Workspace` | Message input, send button, streaming AI response, todo/reasoning display, tool-call bubbles, special cards (map/company/market/leads), credit state. THE critical page. |
| `/map` | `routes/map.tsx` | Interactive map (MapView), overlay layers (cadastre, PLU, risques), parcel data from `realestate_parcels`. |
| `/profile` | `routes/profile.tsx` | Account info, current plan, credit balance, transactions/subscriptions table. |
| `/pricing` | `routes/pricing.tsx` | 3 plans (Starter €49 / Pro €299 / Pay-as-you-go), checkout buttons → Bonzai/Whop. |
| `/claim` | `routes/claim.tsx` | Token-based account finalization (set password) after payment. |
| `/payment-success` | `routes/payment-success.tsx` | "check your email" confirmation state. |
| `/company/$siren` | `routes/company/$siren.tsx` | Company officer/ownership graph page (reuses CompanyGraphPanel). |
| `/data-sources` | `routes/data-sources.tsx` | Public data sources listing (DVF, Sitadel, BAN, cadastre, DPE, INSEE...). |
| `/gdpr` | `routes/gdpr.tsx` | Privacy/legal guardrails (opt-out form presence). |
| `/settings` | `routes/settings.tsx` | Account settings, notification settings. |
| `/dashboard` | `routes/dashboard/index.tsx` | Overview dashboard. |

## Key components

| Component | File | What it renders | Presence check |
|-----------|------|-----------------|----------------|
| `Workspace` | `components/app/workspace.tsx` | The whole chat workspace (input, messages, cards) | textarea/input for message |
| `ToolResultRenderer` / `ToolCallBubble` | `components/app/tool-renderer.tsx` | Renders MCP tool calls; special-rendering for `realestate_*` prefixes | bubble with "Appel outil — <name>" for generic, bordered card for special |
| `MapView` | `components/app/map-view.tsx` | Interactive parcel map (leaflet/maplibre style canvas) | `canvas`, `[class*="leaflet"]`, or `[class*="maplibre"]` |
| `CompanyGraphPanel` | `components/app/company-graph.tsx` | Officer/company node-link or nested-card graph | text containing SIREN / "dirigeant" / node elements |
| `MarketReportPanel` | `components/app/market-report.tsx` | Market study: comps, price/m² trends | headings "Étude de marché", tables, price rows |
| `ResultsTable` | `components/app/results-table.tsx` | Leads results table (scored addresses) | `<table>` with address/score columns |
| `StreetView` | `components/app/street-view.tsx` | Street-level thumbnail images | `<img>` with mapillary/street view src |
| `FeatureLock` | `components/app/feature-lock.tsx` | CreditGate locked state (cost badge + unlock CTA) | text "crédits" + unlock button |
| `PaywallModal` (in `Workspace`) | `components/app/workspace.tsx` (~line 454) | Chat-level paywall when `paywall: true` — "Créer un compte gratuit" (anon) / "Voir les plans" (authed) | modal container + one of the two CTAs |
| `PricingSection` / checkout | `components/marketing/pricing.tsx` | Plan cards with Bonzai/Whop checkout CTAs | plan name + "Acheter des crédits" / checkout button |

## Paywall & FeatureLock selectors (Phase 6)

The credit gate is **client-mirrored** (`lib/credits.ts`). Identity lives in
`localStorage['immosignal.credits.v1']`:
- anon with credits: `{"kind":"anon","credits":1}` (default; `ANON_FREE_CREDITS=1`)
- anon at 0: `{"kind":"anon","credits":0}` → locked + **"Créer un compte gratuit"**
- authed at 0: `{"kind":"user","plan":"free","credits":0}` → locked + **"Voir les plans"**

Sample counters live in `localStorage['immosignal.samples.v1']` (per-feature caps,
e.g. `{"chat":1,"company_graph":1}` exhausts free samples).

FeatureLock DOM (per feature, cost from `FEATURE_COSTS`):
- container: `[class*="rounded-2xl"][class*="border-primary"]` with `[class*="bg-grid"]`
- lock icon: `[class*="grid"][class*="place-items-center"]` containing an `svg`
- cost line: visible text matching `/<FeatureLabel> — N crédits/` (e.g. "Graphique dirigeants — 3 crédits")
- anon message: "Créez un compte gratuit et obtenez +2 crédits pour débloquer cette fonctionnalité."
- authed message: "Crédits insuffisants (solde : 0). Passez au plan Pro ou rechargez."
- anon CTA: `button` with text **"Créer un compte gratuit"** (UserPlus icon)
- authed CTA: `button` with text **"Voir les plans"** (Sparkles icon)
- plan badge: text among "Invité" / "Gratuit" / "Starter" / "Pro" / "À la carte"

Behavior assertions:
- anon click "Créer un compte gratuit" → identity becomes `{"kind":"user","plan":"free","credits":2}`
  in localStorage and the overlay disappears (feature unlocks) — snapshot before/after.
- authed click "Voir les plans" → navigates to `/pricing` or reveals pricing section with
  Bonzai/Whop checkout. No signup step for an authed user.
- Chat-level modal appears when `paywall: true` returned from `/chat/execute`.

Cost table (`FEATURE_COSTS`, mirrored from env): chat 1, env_overlays 2, successions 2,
company_graph 3, street_view 1, map_search 1, map_overlay_extra 2, market_report 3,
market_report_pdf 5.

## Component presence JS (generic)

```js
JSON.stringify({
  url: location.href,
  h1: document.querySelector('h1')?.textContent,
  tables: document.querySelectorAll('table').length,
  imgs: [...document.querySelectorAll('img')].map(i => i.src).filter(s => s && !s.includes('logo')).slice(0, 10),
  buttons: [...document.querySelectorAll('button')].map(b => b.textContent?.trim()).filter(Boolean).slice(0, 20),
  inputs: document.querySelectorAll('input, textarea').length,
  bodySnippet: document.body?.innerText?.substring(0, 300)
});
```

## Known issues to re-check (from docs/TESTING.md)

- BUG-001 (High, Open): homepage hero search box must navigate to `/chat` with the
  query pre-filled — verify on every full run.
- BUG-004 (Medium, Open): Directus meta/aggregate not supported — don't report as a
  new bug if pagination totals come from `data.length`.
- Frontend deploy note: frontend is on Vercel, owned by a third party — push to `main`
  and the Vercel owner redeploys. If the tested frontend doesn't match the repo `main`,
  say so in the report rather than "fixing" production.
