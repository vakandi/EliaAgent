# 📋 [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] [[../../wiki/concepts/Marketing-Concepts|Content]] Strategy - Team Documentation
## Stratégie de Contenu - Équipe B2LUXE

**Date:** 26 Mars 2026  
**[[../../wiki/skills/Git-Version-Control|Version]]:** 1.0  
**Status:** ✅ PRÊT

---

## 🎯 Objectif

Générer du contenu vidéo de qualité pour [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] afin d'alimenter les canaux:
- [[../../wiki/channels/Snapchat|Snapchat]] (via [[../../wiki/channels/Snapchat|Snapchat]] [[../../wiki/channels/Snapchat#army|Army]])
- [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]] / Reels
- [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] Status / Catalog

**Format:** Vidéos courtes (15-20 secondes)  
**Structure:** 20% [[../../wiki/concepts/Ads-Funnel#hook|Hook]] | 40% [[../../wiki/concepts/Pricing|Value]] | 40% [[../../wiki/concepts/Ads-Funnel#cta|CTA]]  
**Volume cible:** 100+ vidéos prêtes à générer

---

## 📁 Documents Générés

| Fichier | Contenu | Scripts |
|---------|---------|---------|
| `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch1-25.md` | [[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] + [[../../wiki/concepts/Luxury-Brands#dior|Dior]] produits | 25 scripts |
| `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch2-50.md` | [[../../wiki/concepts/Luxury-Brands#louis-vuitton|Louis Vuitton]] + [[../../wiki/concepts/Luxury-Brands#gucci|Gucci]] + Casquettes | 25 scripts |
| `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch3-100.md` | [[../../wiki/concepts/Luxury-Brands|Fashion]] + Lifestyle + Urgency | 50 scripts |

**Total: 100 scripts vidéo ✅**

---

## 🎬 Format Alex Hormozi (20/40/40)

Chaque script suit cette structure:

```
🎣 [[../../wiki/concepts/Ads-Funnel#hook|Hook]] (20% - 3-4 secondes)
→ Accrocher l'attention immédiatement
→ Question, affirmation choc, ou visuels

💎 [[../../wiki/concepts/Pricing|Value]] (40% - 6-8 secondes)
→ Éduquer ou divertir
→ Details produit, histoire marque, comparison

📞 [[../../wiki/concepts/Ads-Funnel#cta|CTA]] (40% - 4-6 secondes)
→ Action desired
→ [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]], site, lien bio
```

---

## 🛠️ Outils de Génération

### 1. Higgsfield.[[../../wiki/concepts/AI-Automation|AI]] (PRINCIPAL)
**Compte:** [[../../wiki/people/Wael|Wael]] (abonnement $10/mois)
**Crédits:** ~600 Nano Banana Pro + ~200 Kling 3.0

#### Comment l'utiliser:

**Option A: Interface web**
1. Aller sur [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://higgsfield.[[../../wiki/concepts/AI-Automation|AI]]
2. [[../../wiki/concepts/File-Management|Upload]] l'image produit
3. Sélectionner Kling 3.0 (vidéo) ou Nano Banana Pro (image)
4. Générer

**Option B: Script [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Python-Scripting|Python]] (AUTOMATISÉ)**
```bash
# Setup
pip3 install higgsfield-client --break-system-packages

# Variables d'environnement
export HF_CREDENTIALS="VOTRE_KEY_ID:VOTRE_KEY_SECRET"

# Générer une image
python3 /Users/vakandi/EliaAI/[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py \
  image --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] sneakers luxury [[../../wiki/businesses/Bene2Luxe#products|Product]] photo"

# Générer une vidéo depuis une image
python3 /Users/vakandi/EliaAI/[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py \
  [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] --image [[../../wiki/businesses/Bene2Luxe#products|Product]].png --duration 5

# Batch génération
python3 /Users/vakandi/EliaAI/[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py \
  batch --dir ./generated/ --type [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
```

#### Modèles disponibles:
| Modèle | Usage | Durée |
|--------|-------|-------|
| Kling 3.0 (Pro) | Vidéos produit premium | 5-15s |
| Nano Banana Pro | [[../../wiki/skills/Higgsfield-Video|Images]] 4K ultra-détaillées | Image |
| Flux Pro | [[../../wiki/skills/Higgsfield-Video|Images]] photoréalistes | Image |
| Wan 2.2 | Vidéos alternatives | 5-10s |

**Ratio recommandé:** 9:16 (vertical) pour [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]/Reels

### 2. Artlist.io (Musique)
**URL:** [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://artlist.io/page/pricing/max?tab=creative-assets
**Compte:** [[../../wiki/people/Wael|Wael]]
**Usage:** Musique pour vidéos (royalty-free)

### 3. ComfyUI (Déjà utilisé)
**[[../../wiki/skills/Higgsfield-Video|Images]] produits déjà générées:** `/Users/vakandi/ComfyUI/bene2luxe_products_data/generated/`
- [[../../wiki/businesses/Bene2Luxe#products|Product]]-197554890_bene2luxe.png
- [[../../wiki/businesses/Bene2Luxe#products|Product]]-222921276_bene2luxe.png
- [[../../wiki/businesses/Bene2Luxe#products|Product]]-223520792_bene2luxe.png

---

## 📦 Produits en Catalogue (Mars 2026)

| Marque | Produit | Taille | Prix | Status |
|--------|---------|--------|------|--------|
| [[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] | La Pause Sneakers (grey suede, green sole) | 38-39 | €170 | ✅ Disponible |
| [[../../wiki/concepts/Luxury-Brands#dior|Dior]] | D-BEJE 3 Sunglasses (grey gradient) | 54-17-140 | €195 | ✅ Disponible |
| [[../../wiki/concepts/Luxury-Brands#dior|Dior]] | B23 Sneakers (white canvas, black logo) | 42-43 | À vérifier | ✅ Disponible |
| [[../../wiki/concepts/Luxury-Brands#louis-vuitton|Louis Vuitton]] | Bag / Accessoires | Mixte | À vérifier | ✅ Disponible |
| [[../../wiki/concepts/Luxury-Brands#gucci|Gucci]] | Accessoires / Vêtements | Mixte | À vérifier | ✅ Disponible |
| Caps | Casquettes Premium | Mixte | À vérifier | ✅ Disponible |

---

## 📋 Checklist Production Vidéo

### Phase 1: Préparation ([[../../wiki/people/Wael|Wael]] + Équipe)
- [ ] Configurer Higgsfield [[../../wiki/concepts/API-Integration|API]] key ✅ Script prêt
- [ ] Tester génération image → vidéo
- [ ] Générer 20 [[../../wiki/skills/Higgsfield-Video|Images]] produits ([[../../wiki/concepts/Luxury-Brands#chanel|Chanel]], [[../../wiki/concepts/Luxury-Brands#dior|Dior]], LV, [[../../wiki/concepts/Luxury-Brands#gucci|Gucci]])
- [ ] Générer 50+ vidéos produits (Kling 3.0)
- [ ] Télécharger musique Artlist.io

### Phase 2: Post-production
- [ ] Ajouter musique (Artlist.io)
- [ ] Ajouter textes/sous-titres
- [ ] Optimiser pour format (9:16 vertical)
- [ ] Export en formats multiples ([[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]], Reels, [[../../wiki/channels/Snapchat|Snapchat]])

### Phase 3: Distribution
- [ ] [[../../wiki/concepts/File-Management|Upload]] [[../../wiki/channels/Snapchat|Snapchat]] [[../../wiki/channels/Snapchat#army|Army]] (automation)
- [ ] [[../../wiki/concepts/File-Management|Upload]] [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]] (si compte)
- [ ] [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] Status / Catalog
- [ ] Monitor engagement

---

## 📝 Notes pour [[../../wiki/people/Thomas-Cogne|Thomas]]

1. **Scripts vidéo:** Tous les 100 scripts sont dans [[../../wiki/HOME|Docs]]/2026-03-26/
2. **Higgsfield:** Script [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Python-Scripting|Python]] prêt à l'emploi
3. **Ordre suggested:**
   - Commencer par les scripts "[[../../wiki/concepts/Ads-Funnel#hook|Hook]]" (scripts 1-20)
   - Utiliser les [[../../wiki/skills/Higgsfield-Video|Images]] produits existants
   - Générer 10-20 vidéos cette semaine
   - Tester sur [[../../wiki/channels/Snapchat|Snapchat]] [[../../wiki/channels/Snapchat#army|Army]]

## 📝 Notes pour [[../../wiki/people/Ali|Ali]]

1. **Photos produits:** Vérifier les [[../../wiki/skills/Higgsfield-Video|Images]] ComfyUI générées
2. **Nouveaux produits:** Si nouveaux produits disponibles → ajouter à la liste
3. **Descriptions:** Utiliser les scripts comme base pour [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]

## 📝 Notes pour [[../../wiki/people/Rida|Rida]]

1. **Stratégie contenu:** Scripts de 100 vidéos prêts
2. **Priorité:** Commencer par les scripts "urgency" (20, 56-58, 73)
3. **Organisation:** Grouper par catégorie pour le calendrier de publication

---

## 🔗 Liens Importants

| Ressource | Lien |
|-----------|------|
| Higgsfield Dashboard | [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/systems/Docker-Servers|Cloud]].higgsfield.[[../../wiki/concepts/AI-Automation|AI]] |
| Artlist Music | [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://artlist.io |
| [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] Site | [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]].com |
| Scripts Vidéo (Batch 1) | `[[../../wiki/HOME|Docs]]/2026-03-26/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch1-25.md` |
| Scripts Vidéo (Batch 2) | `[[../../wiki/HOME|Docs]]/2026-03-26/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch2-50.md` |
| Scripts Vidéo (Batch 3) | `[[../../wiki/HOME|Docs]]/2026-03-26/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch3-100.md` |
| Script Higgsfield | `[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py` |
| [[../../wiki/skills/Higgsfield-Video|Images]] ComfyUI | `/Users/vakandi/ComfyUI/bene2luxe_products_data/generated/` |

---

## 📊 Prochaines Étapes

### Cette semaine:
1. [[../../wiki/people/Thomas-Cogne|Thomas]]: Configurer Higgsfield, tester 5 vidéos
2. [[../../wiki/people/Rida|Rida]]: Planifier calendrier de publication (10 vidéos/semaine)
3. [[../../wiki/people/Ali|Ali]]: Vérifier [[../../wiki/skills/Higgsfield-Video|Images]] produits, ajouter nouveaux produits
4. [[../../wiki/people/Wael|Wael]]: Superviser et approuver contenu

### Objectif Avril 2026:
- 100+ vidéos générées
- 50+ publiées sur [[../../wiki/channels/Snapchat|Snapchat]] [[../../wiki/channels/Snapchat#army|Army]]
- [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] catalog mis à jour avec visuels

---

*Document créé par [[../../wiki/people/Elia|Elia]] - 26 Mars 2026*
*[[../../wiki/businesses/B2LUXE-BUSINESS|Business]]: [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] | [[../../wiki/concepts/Marketing-Concepts|Content]] Strategy*
