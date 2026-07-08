# 📋 Bene2Luxe Content Strategy - Team Documentation
## Stratégie de Contenu - Équipe B2LUXE

**Date:** 26 Mars 2026  
**Version:** 1.0  
**Status:** ✅ PRÊT

---

## 🎯 Objectif

Générer du contenu vidéo de qualité pour Bene2Luxe afin d'alimenter les canaux:
- Snapchat (via Snapchat Army)
- TikTok / Reels
- WhatsApp Status / Catalog

**Format:** Vidéos courtes (15-20 secondes)  
**Structure:** 20% Hook | 40% Value | 40% CTA  
**Volume cible:** 100+ vidéos prêtes à générer

---

## 📁 Documents Générés

| Fichier | Contenu | Scripts |
|---------|---------|---------|
| `video-scripts-batch1-25.md` | Chanel + Dior produits | 25 scripts |
| `video-scripts-batch2-50.md` | Louis Vuitton + Gucci + Casquettes | 25 scripts |
| `video-scripts-batch3-100.md` | Fashion + Lifestyle + Urgency | 50 scripts |

**Total: 100 scripts vidéo ✅**

---

## 🎬 Format Alex Hormozi (20/40/40)

Chaque script suit cette structure:

```
🎣 HOOK (20% - 3-4 secondes)
→ Accrocher l'attention immédiatement
→ Question, affirmation choc, ou visuels

💎 VALUE (40% - 6-8 secondes)
→ Éduquer ou divertir
→ Details produit, histoire marque, comparison

📞 CTA (40% - 4-6 secondes)
→ Action desired
→ WhatsApp, site, lien bio
```

---

## 🛠️ Outils de Génération

### 1. Higgsfield.ai (PRINCIPAL)
**Compte:** Wael (abonnement $10/mois)
**Crédits:** ~600 Nano Banana Pro + ~200 Kling 3.0

#### Comment l'utiliser:

**Option A: Interface web**
1. Aller sur https://higgsfield.ai
2. Upload l'image produit
3. Sélectionner Kling 3.0 (vidéo) ou Nano Banana Pro (image)
4. Générer

**Option B: Script Python (AUTOMATISÉ)**
```bash
# Setup
pip3 install higgsfield-client --break-system-packages

# Variables d'environnement
export HF_CREDENTIALS="VOTRE_KEY_ID:VOTRE_KEY_SECRET"

# Générer une image
python3 /Users/vakandi/EliaAI/tools/bene2luxe_higgsfield.py \
  image --prompt "Chanel sneakers luxury product photo"

# Générer une vidéo depuis une image
python3 /Users/vakandi/EliaAI/tools/bene2luxe_higgsfield.py \
  video --image product.png --duration 5

# Batch génération
python3 /Users/vakandi/EliaAI/tools/bene2luxe_higgsfield.py \
  batch --dir ./generated/ --type video
```

#### Modèles disponibles:
| Modèle | Usage | Durée |
|--------|-------|-------|
| Kling 3.0 (Pro) | Vidéos produit premium | 5-15s |
| Nano Banana Pro | Images 4K ultra-détaillées | Image |
| Flux Pro | Images photoréalistes | Image |
| Wan 2.2 | Vidéos alternatives | 5-10s |

**Ratio recommandé:** 9:16 (vertical) pour TikTok/Reels

### 2. Artlist.io (Musique)
**URL:** https://artlist.io/page/pricing/max?tab=creative-assets
**Compte:** Wael
**Usage:** Musique pour vidéos (royalty-free)

### 3. ComfyUI (Déjà utilisé)
**Images produits déjà générées:** `/Users/vakandi/ComfyUI/bene2luxe_products_data/generated/`
- product-197554890_bene2luxe.png
- product-222921276_bene2luxe.png
- product-223520792_bene2luxe.png

---

## 📦 Produits en Catalogue (Mars 2026)

| Marque | Produit | Taille | Prix | Status |
|--------|---------|--------|------|--------|
| Chanel | La Pause Sneakers (grey suede, green sole) | 38-39 | €170 | ✅ Disponible |
| Dior | D-BEJE 3 Sunglasses (grey gradient) | 54-17-140 | €195 | ✅ Disponible |
| Dior | B23 Sneakers (white canvas, black logo) | 42-43 | À vérifier | ✅ Disponible |
| Louis Vuitton | Bag / Accessoires | Mixte | À vérifier | ✅ Disponible |
| Gucci | Accessoires / Vêtements | Mixte | À vérifier | ✅ Disponible |
| Caps | Casquettes Premium | Mixte | À vérifier | ✅ Disponible |

---

## 📋 Checklist Production Vidéo

### Phase 1: Préparation (Wael + Équipe)
- [ ] Configurer Higgsfield API key ✅ Script prêt
- [ ] Tester génération image → vidéo
- [ ] Générer 20 images produits (Chanel, Dior, LV, Gucci)
- [ ] Générer 50+ vidéos produits (Kling 3.0)
- [ ] Télécharger musique Artlist.io

### Phase 2: Post-production
- [ ] Ajouter musique (Artlist.io)
- [ ] Ajouter textes/sous-titres
- [ ] Optimiser pour format (9:16 vertical)
- [ ] Export en formats multiples (TikTok, Reels, Snapchat)

### Phase 3: Distribution
- [ ] Upload Snapchat Army (automation)
- [ ] Upload TikTok (si compte)
- [ ] WhatsApp Status / Catalog
- [ ] Monitor engagement

---

## 📝 Notes pour Thomas

1. **Scripts vidéo:** Tous les 100 scripts sont dans docs/2026-03-26/
2. **Higgsfield:** Script Python prêt à l'emploi
3. **Ordre suggested:**
   - Commencer par les scripts "Hook" (scripts 1-20)
   - Utiliser les images produits existants
   - Générer 10-20 vidéos cette semaine
   - Tester sur Snapchat Army

## 📝 Notes pour Ali

1. **Photos produits:** Vérifier les images ComfyUI générées
2. **Nouveaux produits:** Si nouveaux produits disponibles → ajouter à la liste
3. **Descriptions:** Utiliser les scripts comme base pour WhatsApp

## 📝 Notes pour Rida

1. **Stratégie contenu:** Scripts de 100 vidéos prêts
2. **Priorité:** Commencer par les scripts "urgency" (20, 56-58, 73)
3. **Organisation:** Grouper par catégorie pour le calendrier de publication

---

## 🔗 Liens Importants

| Ressource | Lien |
|-----------|------|
| Higgsfield Dashboard | https://cloud.higgsfield.ai |
| Artlist Music | https://artlist.io |
| Bene2Luxe Site | https://bene2luxe.com |
| Scripts Vidéo (Batch 1) | `docs/2026-03-26/video-scripts-batch1-25.md` |
| Scripts Vidéo (Batch 2) | `docs/2026-03-26/video-scripts-batch2-50.md` |
| Scripts Vidéo (Batch 3) | `docs/2026-03-26/video-scripts-batch3-100.md` |
| Script Higgsfield | `tools/bene2luxe_higgsfield.py` |
| Images ComfyUI | `/Users/vakandi/ComfyUI/bene2luxe_products_data/generated/` |

---

## 📊 Prochaines Étapes

### Cette semaine:
1. Thomas: Configurer Higgsfield, tester 5 vidéos
2. Rida: Planifier calendrier de publication (10 vidéos/semaine)
3. Ali: Vérifier images produits, ajouter nouveaux produits
4. Wael: Superviser et approuver contenu

### Objectif Avril 2026:
- 100+ vidéos générées
- 50+ publiées sur Snapchat Army
- WhatsApp catalog mis à jour avec visuels

---

*Document créé par Elia - 26 Mars 2026*
*Business: Bene2Luxe | Content Strategy*
