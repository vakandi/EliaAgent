---
name: immosignal-report-builder
description: >
  Create perfect AI market reports for ImmoSignal using MCP tools. Covers all 10 report types:
  market, residential, commercial, land, dpe, permits, potential_sell_owners, land_search,
  env_risk, successions, company_graph. Use this skill whenever the user asks to create,
  generate, or build a market report, étude de marché, property prospecting, company graph,
  land search, environmental risk, succession analysis, DPE report, or any real estate
  research report for the ImmoSignal platform. Also trigger on "créer un rapport",
  "générer une étude", "analyser ce quartier", "trouver des propriétaires", "graph
  entreprise", "parcelle", "risque", "succession", or any request involving French
  real estate data analysis that should become a persisted report.
---

# ImmoSignal Report Builder

Create complete, data-rich market reports that render perfectly in the ImmoSignal UI.
Every report is persisted in Directus via the `immosignal_market_reports` MCP and displayed
in `/app/studies` → `/app/report/[id]` with full rich rendering.

## 1. Workflow

1. **Understand** — identify `report_type`, zone, and scope
2. **Read schema** — call `immosignal_market_reports_docs` to confirm exact fields
3. **Query data MCPs** — parcels, permits, DPE, risks, successions, company graphs
4. **Web research** — public records, annuaires, presse (via `parallel-browser-mcp`)
5. **Assemble `data`** — fill the exact schema per type (§3). Missing fields = empty UI sections
6. **Build contacts** — extract public contacts with `notes` for the banner
7. **Build graph** — for company_graph, use GRID format (§4). For potential_sell_owners, build personal graphs
8. **Create** — call `immosignal_market_reports_create` with all params
9. **Close browser** — always close sessions you opened

---

## 2. Create Parameters

| Param | Required | Notes |
|---|---|---|
| `zone` | yes | Commune or label (e.g. "Bordeaux Centre") |
| `session_id` | yes | Read `.session_id.txt` in sandbox workdir |
| `report_type` | yes | One of the 10 types |
| `data` | yes | Exact schema per type — what you put in `data` is what the UI renders |
| `summary` | recommended | 2-3 sentences of analysis — displayed prominently |
| `locations` | recommended | `[{lat, lng, label?}]` — pins on map |
| `contacts` | recommended | `[{name?, type, value, label?, source?, relation?, notes?}]` |
| `image_paths` | optional | Local sandbox paths for street-level photos |
| `siren` | company_graph | SIREN |
| `siret` | company_graph | SIRET (optional) |
| `person` | potential_sell_owners | `{first_name, last_name, birth_date}` |
| `graph` | company_graph | GRID format (§4) |

**Session ID**: read from `.session_id.txt`. Without it, `missing_session_id` error.

---

## 3. Report Type Schemas — Exact Frontend Rendering

The frontend reads `data.*` directly. Missing keys = empty UI sections. What you put in `data` is what the user sees.

### 3.1 market — Étude de marché

**UI Components:** `MarketStatsGrid` + `SegmentBar` + recent_sales table.

```json
{
  "sample_size": 150,
  "median_m2": 4200,
  "median_price": 185000,
  "price_delta_12m": 8.2,
  "avg_time_on_market": 45,
  "demand_index": 72,
  "segments": [
    {"label": "Appartements", "share": 60, "median_m2": 3800},
    {"label": "Maisons", "share": 40, "median_m2": 5200}
  ],
  "recent_sales": [
    {"address": "12 Rue de Rivoli", "price": 195000, "m2": 48}
  ]
}
```

**Frontend fields:**
- `MarketStatsGrid` reads top-level: `sample_size`, `median_price`, `median_m2`, `demand_index`, `price_delta_12m`, `avg_time_on_market`
- `SegmentBar` reads: `segments[].label`, `segments[].share`, `segments[].median_m2`
- Recent sales table reads: `recent_sales[].address`, `recent_sales[].price`, `recent_sales[].m2`

### 3.2 residential — Résidentiel

Same as market. Segments: "Appartements" | "Maisons".

### 3.3 commercial — Commercial

Same as market. Segments: "Commerces" | "Bureaux".

### 3.4 dpe — Diagnostic Énergie

Same base. Segments MUST be: "DPE A-B" | "DPE C-D" | "DPE E-G" (for colored bars: green/orange/red).

```json
{
  "sample_size": 120,
  "median_m2": 3800,
  "median_price": 175000,
  "price_delta_12m": -2.3,
  "avg_time_on_market": 65,
  "demand_index": 45,
  "segments": [
    {"label": "DPE A-B", "share": 15, "median_m2": 5200},
    {"label": "DPE C-D", "share": 50, "median_m2": 4100},
    {"label": "DPE E-G", "share": 35, "median_m2": 2800}
  ],
  "recent_sales": []
}
```

**Frontend:** `dpeBarClass()` maps `label.startsWith("DPE A")` → green, `label.startsWith("DPE C")` → orange, else → red.

### 3.5 permits — Permis de construire

Same base. Segments: "Rénovations" | "Neuf".

### 3.6 land — Terrains

Same base. Custom segment labels allowed.

### 3.7 potential_sell_owners — Propriétaires prêts à vendre

**Most complex type.** UI renders `ProspectCard` per prospect with full detail.

**Data schema:**
```json
{
  "prospects": [
    {
      "address": "15 Avenue Victor Hugo, Paris 16e",
      "score": 78,
      "band": "Élevé",
      "reason": "Propriétaire depuis 22 ans, 1 mandat BODACC, DPE F",
      "factors": [
        "Ancienneté > 20 ans",
        "Événement BODACC détecté",
        "DPE F (pression loi Climat)",
        "SCI inactive depuis 2020"
      ],
      "last_transaction_year": 2003,
      "owner_first_name": "Jean",
      "owner_last_name": "Dupont",
      "birth_date": "1952-03-15",
      "companies": [
        {"name": "SCI Les Jardins", "siren": "750912345", "role": "Gérant"}
      ],
      "properties": [
        {
          "address": "15 Avenue Victor Hugo, Paris 16e",
          "commune": "Paris 16e",
          "purchase_price": 120000,
          "estimate": 280000,
          "last_sale": 2003
        }
      ],
      "successions": [
        {"address": "15 Avenue Victor Hugo", "death_date": "2024-01-10", "probability": 85}
      ],
      "last_sells": [
        {"address": "15 Avenue Victor Hugo", "price": 195000, "date": "2023-06"}
      ],
      "dpe": "F",
      "parcel": "750123456AB0001"
    }
  ]
}
```

**Also pass top-level:** `"person": {"first_name": "Jean", "last_name": "Dupont", "birth_date": "1952-03-15"}`

**Frontend ProspectCard reads:**
- `score` or `probability` — normalized `<= 1 ? *100`, displayed as ring (≥70 green, ≥40 orange, <40 red)
- `band` — "Élevé"/"Moyen"/"Faible" badge
- `factors` — string[] rendered as chips
- `reason` — fallback if no factors
- `owner_first_name`, `owner_last_name` — displayed as "Jean Dupont · né(e) 1952-03-15"
- `birth_date` — displayed as "né(e) YYYY-MM-DD"
- `dpe` — DPE badge (A-G)
- `parcel` — shown on property thumbnail
- `companies` — "Patrimoine dirigeant" panel: `[{name, siren, role}]`
- `properties` — "Autres biens" panel: `[{address, commune, purchase_price, estimate, last_sale}]`
- `successions` — "Successions" panel: `[{address, death_date, probability}]`
- `last_sells` or `sells` — "Dernières ventes" panel: `[{address, price, date}]`
- `last_transaction_year` — "Détention" field: `currentYear - last_transaction_year` ans
- `purchase_price`, `estimate` — "Prix d'achat" and "Estimation" fields, with gain% calculation

**Score:** 0-100 recommended. UI normalizes `<= 1 ? *100` but 0-100 is clearer.

### 3.8 land_search — Recherche terrain

```json
{
  "parcels": [
    {
      "reference": "750123456AB0001",
      "address": "12 Rue de la Paix, Paris 2e",
      "area": 850,
      "surface": 850,
      "plu": "UA",
      "buildable": true,
      "price": 420000
    }
  ]
}
```

**Frontend:** `SimpleListDetail` reads `data.parcels` or `data.terrains`. Renders: address (or reference), area/surface m², PLU zone, "Constructible"/"Non constructible", price.

### 3.9 env_risk — Risque environnemental

```json
{
  "risks": [
    {
      "name": "ICPE Les Mollettes",
      "kind": "ICPE",
      "category": "Installation classée pour la protection de l'environnement",
      "distance": 1200,
      "severity": "Élevé"
    }
  ]
}
```

**Frontend:** `SimpleListDetail` reads `data.risks` or `data.sites`. Renders: name, kind (ICPE/BASOL/BASIAS badge), category, distance "à X m", severity.

### 3.10 successions — Successions

```json
{
  "successions": [
    {
      "address": "28 Rue du Faubourg Saint-Antoine, Paris 12e",
      "commune": "Paris 12e",
      "death_date": "2024-01-10",
      "probability": 85,
      "estate_value": 350000,
      "heirs_count": 3
    }
  ]
}
```

**Frontend:** `SimpleListDetail` reads `data.successions`. Renders: address, death_date "Décès YYYY-MM-DD", probability "%", estate_value €.

### 3.11 company_graph — Entreprises & dirigeants

**UI:** `CompanyGraphPanel` renders GRID diagram + `CompanyGraphDetail` with graph + links.

**Data schema — top-level `data` fields:**
```json
{
  "siren": "750812345",
  "company": {
    "name": "SAS HABITAT PARISIEN",
    "siren": "750812345",
    "legal_form": "SAS",
    "status": "active",
    "head_office": "12 Rue de Rivoli, Paris 1er",
    "founded": "2015-03-12"
  },
  "graph": { "grid": [...], "legal_events": [...] }
}
```

**Frontend data flow** (`report-detail.tsx` CompanyGraphDetail):
1. Reads `data.graph` → checks if `rawGraph.grid` is array → `CompanyGraphGrid`
2. Falls back to `CompanyGraphHierarchy` if no grid
3. Ultimate fallback to flat `nodes`/`edges` → converted via `flatToGrid()`
4. Passes to `CompanyGraphPanel` → renders `GridGraphView`

---

## 4. Graph GRID Format (for company_graph)

**Always prefer GRID over hierarchical.** GRID renders as a positioned diagram with cards, levels (rows), columns, and SVG arrows between linked cards.

```json
{
  "title": "SAS HABITAT PARISIEN",
  "notes": "Réseau d'entreprises immobilier — 3 sociétés, 2 dirigeants",
  "grid": [
    {
      "level": 0,
      "label": "Société",
      "cards": [{
        "id": "societe",
        "column": 0,
        "card_type": "company",
        "name": "SAS HABITAT PARISIEN",
        "siren": "750812345",
        "legal_form": "SAS",
        "status": "active",
        "head_office": "12 Rue de Rivoli, Paris 1er",
        "founded": "2015-03-12",
        "facts": [
          {"label": "Activité", "value": "Promoteur immobilier"},
          {"label": "CA", "value": "2.4 M€ (2024)"}
        ]
      }]
    },
    {
      "level": 1,
      "label": "Dirigeants",
      "cards": [
        {
          "id": "dirigeant-0",
          "column": 0,
          "card_type": "person",
          "first_name": "Jean",
          "last_name": "Simon",
          "role": "Gérant",
          "birth_date": "1975-08-20",
          "companies": [{"name": "SCI RIVE GAUCHE", "siren": "750912346", "role": "Gérant"}],
          "properties": [{"label": "Appartement", "parcel": "750123456AB0001", "commune": "Paris 5e", "address": "45 Bd Saint-Germain"}],
          "facts": [
            {"label": "Rôle", "value": "Gérant"},
            {"label": "Revenus estimés", "value": "45 000 € / an"},
            {"label": "Source", "value": "Societe.com, 2026-08-07"}
          ],
          "links": [{"target": "societe", "role": "Gérant"}]
        },
        {
          "id": "dirigeant-1",
          "column": 1,
          "card_type": "person",
          "first_name": "Marie",
          "last_name": "Laurent",
          "role": "Présidente",
          "facts": [
            {"label": "Rôle", "value": "Présidente"},
            {"label": "Revenus", "value": "78 000 € / an"}
          ],
          "links": [{"target": "societe", "role": "Présidente"}]
        }
      ]
    },
    {
      "level": 2,
      "label": "Sociétés liées",
      "cards": [
        {
          "id": "sub-0",
          "column": 0,
          "card_type": "company",
          "name": "SCI RIVE GAUCHE",
          "siren": "750912346",
          "legal_form": "SCI",
          "status": "active",
          "head_office": "45 Boulevard Saint-Germain, Paris 5e",
          "founded": "2008-06-20",
          "links": [{"target": "dirigeant-0", "role": "Gérant"}]
        },
        {
          "id": "sub-1",
          "column": 1,
          "card_type": "company",
          "name": "SA PATRIMOINE 16E",
          "siren": "751212349",
          "legal_form": "SA",
          "status": "active",
          "head_office": "67 Rue de la Pompe, Paris 16e",
          "founded": "2005-11-30",
          "links": [{"target": "dirigeant-1", "role": "Présidente"}]
        }
      ]
    }
  ],
  "legal_events": [
    {"date": "2015-03-12", "type": "Création", "label": "Immatriculation SAS"},
    {"date": "2017-06-15", "type": "Modification", "label": "Changement de gérant"}
  ]
}
```

### GRID Rules (from `company-graph.tsx`)

- **`level`**: Row number (0 = top). Cards on same level appear side by side.
- **`label`**: Row label shown in gutter on left.
- **`column`**: X position within level (0 = left). Defaults to order of appearance.
- **`id`**: Unique identifier. Required for `links` to reference this card.
- **`card_type`**: `company` | `person` | `property`. Invalid types silently dropped.
- **`links`**: `[{target: "card-id", role?: "Gérant"}]` — creates SVG arrows. Target must be a card `id` on a different level.
- **`facts`**: `[{label, value}]` — free-form pairs rendered generically on ALL card types.
- **`legal_events`**: Optional `[{date, type, label}]` shown below graph.

### Card Rendering (from `GridCard` in `company-graph.tsx`)

**Person card** (`card_type: "person"`):
- Avatar with initials from `name` (or `first_name` + `last_name`)
- `name` → "Propriétaire" if missing
- `role` → subtitle
- `birth_date` → "Né(e) le ..."
- `companies[]` → "Sociétés" section: `{name, siren, role}`
- `properties[]` → "Biens" section: `{label, address, commune, parcel}`
- `facts[]` → key/value pairs rendered as rows

**Company card** (`card_type: "company"`):
- Building icon, `name`, `legal_form · status`, `siren` badge
- `head_office` → "Siège : ..."
- `founded` → "Créée en ..."
- `facts[]` → key/value pairs

**Property card** (`card_type: "property"`):
- Landmark icon, `name` or `label`, `address`
- `parcel` → "Parcelle ..."
- `facts[]` → key/value pairs

### Layout Constants
- Card width: 240px
- Card gap: 28px
- Row gap: 64px
- Gutter (label area): 132px
- Padding: 24px

### For potential_sell_owners graphs

Build personal graphs per prospect. Include web-researched `facts`:

```json
{
  "title": "Jean Dupont — Profil propriétaire",
  "grid": [
    {
      "level": 0,
      "label": "Propriétaire",
      "cards": [{
        "id": "person",
        "card_type": "person",
        "first_name": "Jean",
        "last_name": "Dupont",
        "role": "Propriétaire",
        "facts": [
          {"label": "Profession", "value": "Retraité"},
          {"label": "Ancienneté", "value": "22 ans propriétaire"},
          {"label": "Revenus estimés", "value": "35 000 € / an"},
          {"label": "LinkedIn", "value": "linkedin.com/jean-dupont"},
          {"label": "Source", "value": "Societe.com, 2026-08-07"}
        ]
      }]
    },
    {
      "level": 1,
      "label": "Sociétés",
      "cards": [{
        "id": "sci",
        "card_type": "company",
        "name": "SCI Les Jardins",
        "siren": "750912345",
        "legal_form": "SCI",
        "status": "active",
        "facts": [
          {"label": "Activité", "value": "Gestion de patrimoine immobilier"},
          {"label": "CA", "value": "120 000 € (2023)"}
        ],
        "links": [{"target": "person", "role": "Gérant"}]
      }]
    }
  ]
}
```

---

## 5. Contacts Contract

Optional for all types. Each contact displayed in `ContactsBanner` grouped by relation.

```json
[{
  "name": "SARL Dupont Immobilier",
  "type": "company",
  "value": "812345678",
  "label": "SIREN société",
  "source": "RNE",
  "relation": "company",
  "notes": "Société détentrice du bien — gérée par 2 associés, historique propre."
}]
```

- **`type`** (required): `email` | `phone` | `social` | `company`
- **`value`** (required): email, phone, social handle, SIREN...
- **`relation`**: `company` | `prospect` | `succession` | `owner` | `other`
  - Groups in UI: "Entreprises", "Prospects & propriétaires", "Successions", "Autres contacts"
- **`notes`**: AI analysis — displayed in "Note IA" highlighted banner. **Always include.**
- **Sources**: public data ONLY (RGPD).

---

## 6. What to Research Per Entity

### Companies
- SIREN/SIRET, denomination, forme juridique, siège, objet social, capital, date création
- Dirigeants actuels/passés, durée mandat, mandats multiples
- Événements récents: liquidation, redressement, cession (BODACC)
- Activité réelle: site web, secteur, présence en ligne
- Chiffre d'affaires, résultat net
- Articles de presse, actualités
- **Ajouter dans `facts`**: Métier, CA, nb employés, historique
- **Ajouter dans `contacts`**: SIREN comme `type: company`

### People (propriétaires privés)
- Profession, activité déclarée, employeur
- Présence en ligne: LinkedIn, réseaux sociaux, annuaires pro
- Actualités locales, mentions presse
- Autres propriétés connues (via parcels_history)
- **Ajouter dans `facts`**: Métier, revenus, anciennes sociétés
- **Ajouter dans `contacts`**: LinkedIn comme `type: social`

### Cities & Quartiers
- Démographie, projets d'urbanisme, prix immobilier tendance
- **Ajouter dans `summary`**: Contexte local, dynamique du quartier

### Web Research Sources
societe.com, pappers.fr, infogreffe.fr, verif.com, annuaire-entreprises.data.gouv.fr, pagesjaunes.fr, Google News, LinkedIn, cadastre.gouv.fr, geoportail-urbanisme.gouv.fr, georisques.gouv.fr, data.gouv.fr, insee.fr

---

## 7. MCP Data Tools

| Tool | Use for |
|---|---|
| `immosignal_parcels_search` | Parcels by commune, PLU zone, area, owner type |
| `immosignal_parcels_history` | Transaction history per parcel |
| `immosignal_permits_search` | Building permits by commune, type, date |
| `immosignal_dpe_labels_search` | Energy ratings by commune |
| `immosignal_risk_sites_search` | Environmental risks (ICPE/BASOL/BASIAS) |
| `immosignal_zoning_events_search` | PLU/GPU zoning changes |
| `immosignal_successions_search` | Death records (anonymize in output) |
| `immosignal_company_graphs_get_by_siren` | Company graph by SIREN |
| `immosignal_company_graphs_legal_events` | Legal events per company |
| `immosignal_company_graphs_search` | Company search |
| `immosignal_street_views_get` | Street-level photos (live Mapillary) |
| `immosignal_market_reports_docs` | **Consult BEFORE create** — schemas |
| `immosignal_market_reports_create` | Create report |
| `immosignal_market_reports_update` | Update existing report |
| `immosignal_market_reports_get` | Auto-generated market data |
| `immosignal_market_reports_list` | List recent reports |

---

## 8. Browser Session Lifecycle

1. `start_session` → get `sessionId` (numeric — **write it down**)
2. `browser_navigate` → search URLs
3. `browser_snapshot` or `browser_get_page_structure` → read results
4. `browser_fill` / `browser_click` → interact if needed
5. `browser_evaluate` → extract data via JS
6. `browser_screenshot` → save evidence
7. **`close_session(sessionId)`** → close THIS session before creating

**Critical:** Never leave sessions open. Always close before `immosignal_market_reports_create`.

---

## 9. Common Mistakes

1. **Missing `session_id`** → `missing_session_id`, report not created
2. **Wrong segment labels** → empty bars (must match exactly per type)
3. **Flat graph** (nodes/edges) → works but GRID preferred for better rendering
4. **Missing `id` on cards** → links can't target, arrows disappear
5. **Missing `facts`** → cards render empty below name/role
6. **Not calling docs first** → might miss new fields
7. **Leaving browser open** → resource leak
8. **Score as 0.01 instead of 85** → UI normalizes but 0-100 clearer
9. **Forgetting `contacts`** → no banner, no outreach context
10. **Not enriching with web data** → sparse report
11. **`data.prospects` missing** → ProspectCard renders nothing (also checks `leads`, `items`, `rows`)
12. **`data.risks` missing** → SimpleListDetail renders "Aucune donnée" (also checks `sites`)
13. **`data.successions` missing** → SimpleListDetail renders "Aucune donnée"
14. **`data.parcels` missing** → SimpleListDetail renders "Aucune donnée" (also checks `terrains`)
