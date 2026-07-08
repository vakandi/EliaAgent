# Bene2Luxe Product Addition - BEN-13

**Date**: 1 Avril 2026  
**Task**: Ajouter Chanel Runner et Off-White au catalogue  
**Status**: En cours d'analyse

---

## 🔍 Méthodes pour Ajouter des Produits

### Méthode 1: Panel Admin (Recommandé)

Le site Bene2Luxe dispose d'un panel admin accessible à:
- **URL**: https://bene2luxe.com/admin
- **Login**: wael.bousfira@gmail.com / NzsP-+uH*_z3GhNzsP-+uH*_z3Gh

**Options disponibles:**
1. **ZIP Upload** - Import en masse via fichiers ZIP avec manifest.json
2. **Manual Add** - Ajout manuel produit par produit via `ManualProductPopup.tsx`
3. **AI-assisted** - Génération automatique via `AIProductAnalyzer.tsx`

---

### Méthode 2: API Backend

**Endpoints disponibles:**
- `/api/admin/products/` - CRUD produits
- `/api/admin/catalog/zip-upload` - Import ZIP
- `/api/admin/catalog/sync` - Synchronisation catalogue

**Codebase:**
- Backend: `/home/vakandi/multisaasdeploy/bene2luxe/backend/`
- Routers: `backend/routers/admin/products.py`
- Models: `backend/models/ecommerce.py`

---

### Structure d'un Produit

```python
{
    "product_id": int,
    "slug": str,
    "name": str,           # ex: "Chanel Runner"
    "description": str,
    "short_description": str,
    "model_key": str,
    "color_name": str,
    "price": float,
    "compare_at_price": float,
    "brand": {"brand_id": int, "name": str},
    "category": {"category_id": int, "name": str},
    "images": [list of URLs],
    "variations": [sizes/colors],
    "stock_quantity": int,
    "sku": str
}
```

---

## 📋 Actions Requises pour Chanel Runner + Off-White

### Informations nécessaires:
1. Nom du produit exact
2. Prix de vente
3. Images du produit
4. Variantes (tailles disponibles)
5. Marque (Chanel, Off-White)
6. Catégorie (Sneakers/Baskets)

### Processus:
1. Rida/Ali doivent fournir les infos produits
2. Ajouter via panel admin OU
3. Créer script d'import ZIP avec manifest.json

---

## 🔗 Sources

- Frontend: `/home/vakandi/multisaasdeploy/bene2luxe/frontend_build/`
- Backend: `/home/vakandi/multisaasdeploy/bene2luxe/backend/`
- Admin Products: `frontend_build/src/components/admin/products/`
