# Background Polling — CONSOLIDATED (source of truth)

> FastAPI ingests the French public datasets (Géorisques, INSEE, BODACC, DVF, Mapillary,
> Cadastre) on a schedule into the Directus `realestate_*` collections. The frontend
> reads Directus only — the maps, info panels, and chat cards consume these collections.
> Intervals are configurable per job in `mgmt_poll_configs` (default: 86400s = daily).
>
> ⚠️ **Redundancy removed**: `immosignal-fastapi/docs/BACKGROUND_FETCHING.md` describes the
> **obsolete** legacy system (Vercel/Coolify/Discord/Mail/AI session pollers writing to
> `mgmt_*` collections). It is kept on disk only as historical reference. THIS file is
> the single authoritative description of the current polling system. Do not test the
> legacy `mgmt_*` pollers as MVP features.

## Jobs (6, all MVP_v2)

| Job | Event Type | Méthode | Source | Collection cible |
|-----|------------|---------|--------|------------------|
| Risques ICPE | `mvp_risk_sites` | `_poll_georisques()` | Géorisques `/api/v1/installations_classees` | `realestate_risk_sites` |
| Successions | `mvp_successions` | `_poll_insee_deaths()` | INSEE fichier mensuel (largeur fixe 198, latin-1) | `realestate_successions` |
| Graphiques sociétés | `mvp_company_graphs` | `_poll_bodacc()` | BODACC (Opendatasoft) | `realestate_company_graphs` |
| Rapports marché | `mvp_market_reports` | `_poll_dvf()` | DVF data.gouv (CSV.gz par année) | `realestate_market_reports` |
| Vues street | `mvp_street_views` | `_poll_mapillary()` | Mapillary API v4 (`client_token`) | `realestate_street_views` |
| Parcelles cadastre | `mvp_parcels` | `_poll_cadastre()` | CSV source (URL dans config) | `realestate_parcels` |

Plus the core data tables the AI reads: `properties` and `transactions` (DVF backbone).

## Architecture

```
FastAPI lifespan
  └── PollerService.start()
        ├── _poll_loop("mvp_risk_sites")     → Géorisques → realestate_risk_sites
        ├── _poll_loop("mvp_successions")    → INSEE → realestate_successions
        ├── _poll_loop("mvp_company_graphs") → BODACC → realestate_company_graphs
        ├── _poll_loop("mvp_market_reports") → DVF → realestate_market_reports
        ├── _poll_loop("mvp_street_views")   → Mapillary → realestate_street_views
        └── _poll_loop("mvp_parcels")        → Cadastre CSV → realestate_parcels
```

### Flow par job

```
Pour chaque event_type de DEFAULT_INTERVALS:
  1. Lire la config mgmt_poll_configs (workspace = "immosignal")
  2. Vérifier interval_seconds écoulé depuis last_polled_at
  3. Skip si circuit-breaker désactivé (3 échecs consécutifs)
  4. Lire les credentials via mgmt_integrations (config JSON, provider = nom du job)
  5. Fetch source externe (httpx, timeout 30-120s)
  6. Upsert dans la collection realestate_* (get_one_by → update/create)
  7. Mettre à jour last_polled_at sur mgmt_poll_configs
```

### DVF — format URL (⚠️ a changé)

L'ancien format `latest/csv/{dep}/valeursfoncieres-{dep}.csv` est **mort** (404).
Nouveau format vérifié (juillet 2026) :

```
https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/departements/{dep}.csv.gz
```

- Fichiers **gzippés** par année (`gzip.decompress(resp.content)` puis utf-8)
- Année : `config.year` si présent, sinon les 5 dernières années en fallback
- `_dvf_is_sale` matche `nature_mutation` en uppercase ("Vente" → "VENTE" OK)

### Circuit-breaker

3 échecs consécutifs sur un job → auto-disable (`poller.collection_disabled`, fail_count=3).
Un poll suivant qui réussit le réactive (`poller.collection_recovered`).

## Config Directus

### `mgmt_poll_configs` — une ligne par event_type (créée au premier poll)

| Field | Type | Notes |
|-------|------|-------|
| `workspace` | string | `immosignal` |
| `event_type` | string | Un des 6 `mvp_*` |
| `interval_seconds` | integer | 60–86400. Default 86400 |
| `enabled` | boolean | Default true |
| `last_polled_at` | datetime | Mis à jour après chaque cycle |
| `fail_count` | integer | Compteur d'échecs (circuit-breaker) |

### `mgmt_integrations` — credentials par provider (champ `config`, JSON)

| Provider | Config fields |
|----------|--------------|
| `georisques` | `base_url`, `communes` (liste) |
| `insee` | `url` |
| `bodacc` | `base_url`, `departments` (liste) |
| `dvf` | `base_url`, `departments`, `zones` (optionnel), `year` (optionnel) |
| `mapillary` | `base_url`, `client_token` |
| `cadastre` | `url` (CSV source) |

Job skip (log `poller.skip`) si le provider est absent ou sans champs requis.

## Files (backend)

```
fastapi/app/
  services/poller.py    ← Moteur de polling (6 jobs MVP_v2)
  routers/poll.py       ← Statut / trigger / configs
  main.py               ← PollerService.start() au lifespan, stop au shutdown
```

## API

```bash
GET  /poll/status?workspace=immosignal                        # Statut + derniers polls
POST /poll/trigger/{event_type}?workspace=immosignal          # Trigger manuel
GET  /poll/configs?workspace=immosignal                       # Liste configs
POST /poll/configs?event_type=...&interval_seconds=...        # Update config
```

## Seed data (docs/TESTING.md, 2026-07-31)

`directus_setup/seed_realestate.py` seeded **373 items across 9 collections**
(properties 80, transactions 120, realestate_parcels 60, realestate_company_graphs 10,
realestate_market_reports 16, realestate_risk_sites 12, realestate_street_views 20,
realestate_successions 25, mgmt_notification_log 30) with Île-de-France data, idempotent.
A "collection empty" finding in a test means the poller OR the seed failed — check
`/poll/status` first.
