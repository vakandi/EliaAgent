# [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] [[../../wiki/businesses/Bene2Luxe#products|Product]] Addition - [[../../wiki/systems/Jira-Tickets-Index|BEN]]-13

**Date**: 1 Avril 2026  
**[[../../wiki/concepts/AI-Automation#tasks|Task]]**: Ajouter [[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] Runner et [[../../wiki/concepts/Luxury-Brands#off-white|Off-White]] au catalogue  
**Status**: En cours d'analyse

---

## 🔍 Méthodes pour Ajouter des Produits

### Méthode 1: Panel Admin (Recommandé)

Le site [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] dispose d'un panel admin accessible à:
- **URL**: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]].com/admin
- **Login**: [[../../wiki/people/Wael|Wael]].bousfira@[[../../wiki/channels/Gmail|Gmail]].com / NzsP-+uH*_z3GhNzsP-+uH*_z3Gh

**Options disponibles:**
1. **ZIP [[../../wiki/concepts/File-Management|Upload]]** - Import en masse via fichiers ZIP avec manifest.[[../../wiki/concepts/API-Integration|JSON]]
2. **Manual Add** - Ajout manuel produit par produit via `ManualProductPopup.tsx`
3. **[[../../wiki/concepts/AI-Automation|AI]]-assisted** - Génération automatique via `AIProductAnalyzer.tsx`

---

### Méthode 2: API Backend

**Endpoints disponibles:**
- `/api/admin/products/` - CRUD produits
- `/api/admin/catalog/zip-[[../../wiki/concepts/File-Management|Upload]]` - Import ZIP
- `/api/admin/catalog/sync` - Synchronisation catalogue

**Codebase:**
- Backend: `/home/vakandi/[[../../wiki/systems/MultiSaasDeploy|MultiSaasDeploy]]/[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]/backend/`
- Routers: `backend/routers/admin/products.py`
- Models: `backend/models/ecommerce.py`

---

### Structure d'un Produit

```[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Python-Scripting|Python]]
{
    "product_id": int,
    "slug": str,
    "name": str,           # ex: "[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] Runner"
    "description": str,
    "short_description": str,
    "model_key": str,
    "color_name": str,
    "price": float,
    "compare_at_price": float,
    "[[../../wiki/concepts/Luxury-Brands|Brand]]": {"brand_id": int, "name": str},
    "[[../../wiki/concepts/Marketing-Concepts|Category]]": {"category_id": int, "name": str},
    "[[../../wiki/skills/Higgsfield-Video|Images]]": [[[../../wiki/concepts/[[../../wiki/channels/Google|Search]]|List]] of URLs],
    "variations": [[[../../wiki/businesses/Bene2Luxe#sizing|Sizes]]/colors],
    "stock_quantity": int,
    "sku": str
}
```

---

## 📋 Actions Requises pour [[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] Runner + [[../../wiki/concepts/Luxury-Brands#off-white|Off-White]]

### Informations nécessaires:
1. Nom du produit exact
2. [[../../wiki/concepts/Pricing|Prix]] de vente
3. [[../../wiki/skills/Higgsfield-Video|Images]] du produit
4. Variantes (tailles disponibles)
5. Marque ([[../../wiki/concepts/Luxury-Brands#chanel|Chanel]], [[../../wiki/concepts/Luxury-Brands#off-white|Off-White]])
6. Catégorie (Sneakers/Baskets)

### Processus:
1. [[../../wiki/people/Rida|Rida]]/[[../../wiki/people/Ali|Ali]] doivent fournir les infos produits
2. Ajouter via panel admin OU
3. Créer script d'import ZIP avec manifest.[[../../wiki/concepts/API-Integration|JSON]]

---

## 🔗 Sources

- Frontend: `/home/vakandi/[[../../wiki/systems/MultiSaasDeploy|MultiSaasDeploy]]/[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]/frontend_build/`
- Backend: `/home/vakandi/[[../../wiki/systems/MultiSaasDeploy|MultiSaasDeploy]]/[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]/backend/`
- Admin Products: `frontend_build/src/components/admin/products/`
