# MVP feature checklist (from MVP.md + MVP_v2.md)

Consolidated testable feature matrix. Test status column is filled during a run.
Sources: `MVP.md` (product spec) and `MVP_v2.md` (Telescop audit → new data domains).

## Core product (MVP.md §5)

| Feature | Where it lives | Test signal |
|---------|----------------|-------------|
| Address/parcel search → propensity score (0–100) + confidence + top factors | `/chat` + `score_property`/`search_transactions` MCP tools | Chat prompt "score cette adresse" → score + reasoning displayed |
| Natural-language chat with @mentions + MCP tools | `/chat` | Message send → AI response with tool calls |
| CSV export of scored list (credit-gated) | `/profile` or leads table | Export button present; gated by credits |
| Saved searches / alerts (phase 1.5 — stub) | `mgmt_notification_log` / alerts UI | Collection exists, settings page present |

## MVP_v2 data domains (§2.2) — fed by the polling pipeline

| Domain | Collection | Backing source | Test signal |
|--------|-----------|----------------|-------------|
| Environmental/industrial risk overlays (ICPE/BASIAS/BASOL) | `realestate_risk_sites` | Géorisques | Map overlay "Risques" shows sites; `get_environmental_risk` tool |
| Successions / inheritance signals (internal-only, GDPR-phrased "Événement de transmission détecté") | `realestate_successions` | INSEE deaths file | Scoring factor appears anonymized, never raw "owner deceased" |
| Company ownership & dirigeants graph | `realestate_company_graphs` | Sirene + INPI RNE + BODACC | `get_company_officer_graph` / `get_company_legal_events` → company graph card; `/company/<siren>` page |
| Street view / visual context | `realestate_street_views` | Mapillary (Google fallback) | Thumbnails in lead/map cards; `get_street_view` |
| Pige listings feed | NOT in MVP (Step 3, buy-not-build) | — | Do NOT test as expected feature |

## MCP tools that must be registered (MVP.md §7.3 + MVP_v2 §3)

Thin wrappers over ingested tables, never live-calling external APIs mid-chat:

- `search_transactions(commune|postal_code|radius, date_range, price_range)`
- `get_property_history(ban_id|cadastral_ref)`
- `search_permits(commune|postal_code, permit_type, date_range)`
- `get_dpe(ban_id|address)`
- `get_company_ownership_signal(siren)`
- `score_property(ban_id|address)`
- `list_scored_addresses(area, min_score, band)`
- `search_parcels(commune|polygon, plu_zone, buildable_only, min_area)` (v2)
- `get_environmental_risk(ban_id|cadastral_ref)` (v2)
- `get_market_report(commune|zone, property_type)` (v2)
- `get_death_registry_signal(name_hint, commune, date_range)` (v2, INTERNAL — not user-facing)
- `get_company_officer_graph(siren|dirigeant_name)` (v2)
- `get_company_legal_events(siren)` (v2)
- `get_street_view(lat, lon)` (v2)

Check `GET /mcp/providers` and the AI's tool list (via a chat probe like "quels outils
as-tu ?") to see which are actually live.

## Credits & paywall (MVP.md §6 + MVP_v2 §7)

| Feature | Env knob (default) | Test signal |
|---------|--------------------|-------------|
| Anonymous free credits per IP | `ANON_FREE_CREDITS` (1) | 1 free chat turn without login |
| Signup free credits | `SIGNUP_FREE_CREDITS` (2) | Signup grants 2 more |
| Paywall modal (anon: "Sign up free" / "See plans"; authed: "Upgrade") | `paywall: true` response | Modal in DOM at 0 credits |
| Credit ledger shared across features | `FEATURE_COST_*` | One balance; feature costs sum per turn |
| Per-feature costs | overlays 2, successions 2, company graph 3, street view 1, map search 1, map overlay extra 2, market report 3, PDF 5 | Gating enforced server+client; FeatureLock state |

## Paywall test matrix — every gated feature, both identity states

**Rule (MVP_v2 §7.4): never a dead-end.** Every locked feature must show the
`FeatureLock` overlay with an immediate unlock path. Test each feature in BOTH states
(deterministic via localStorage — see FRONTEND-PAGES.md):

| Feature | FeatureLock label & cost | Anon CTA (0 crédits) | Authed CTA (0 crédits) |
|---------|--------------------------|----------------------|------------------------|
| Chat | "Chat IA — 1 crédit" | Créer un compte gratuit → +2, unlock | Voir les plans → /pricing |
| Environnement / overlays | "Overlays environnementaux — 2 crédits" | same | same |
| Successions factor | "Facteur successions — 2 crédits" | same | same |
| Graphe dirigeants | "Graphique dirigeants — 3 crédits" | same | same |
| Street view | "Street view — 1 crédit" | same | same |
| Recherche carte | "Recherche carte — 1 crédit" | same | same |
| Overlay carte supplémentaire | "Overlay supplémentaire — 2 crédits" | same | same |
| Étude de marché | "Étude de marché — 3 crédits" | same | same |
| Export PDF étude | "Étude de marché PDF — 5 crédits" | same | same |

For each row: force the feature to render in locked state → assert overlay + cost line →
click CTA → assert unlock (anon: identity `{kind:'user',plan:'free',credits:2}` in
localStorage + overlay gone; authed: `/pricing` reached) → snapshot before/after.
Bare error instead of FeatureLock, or a CTA that doesn't unlock/navigate = paywall bug.
Report per-feature pass/fail.

## Plans (MVP.md §6.4 + MVP_v2 §7.3)

| Plan | Price | Check |
|------|-------|-------|
| Starter | €49/mo, 200 credits | Pricing card present, checkout link → Bonzai |
| Pro / Big | €299/mo, 2000 credits | Pricing card present, checkout link → Bonzai |
| Pay-as-you-go | credit packs | Checkout link present |

Checkout must try Bonzai.pro first (`XWy2_8250`), fall back to Whop on failure. Success
URLs/webhooks go through `paybook2luxe.com` — verify links open with
`noopener,noreferrer` (do not actually pay).

## Frontend pages from MVP §9

- Homepage: live search box → chat (BUG-001 regression!), 3-step "How it works",
  pricing cards, paywall modal reusable.
- `/claim` — token finalization after payment.
- `/payment-success` — checkout redirect "check your email".
- `/profile` — plan, credits, transactions table (oldest → newest, status paid/refunded/cancelled).
