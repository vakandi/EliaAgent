# 📱 [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] Scripts - Team Quick Reference
## Pour [[../../wiki/people/Thomas-Cogne|Thomas]], [[../../wiki/people/Rida|Rida]], [[../../wiki/people/Ali|Ali]] - Mars 2026

---

## 🎬 CE QUI EST PRÊT

### ✅ 100 Scripts Vidéo (Format Alex Hormozi 20/40/40)

| Fichier | Contenu | Scripts |
|---------|---------|---------|
| `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch1-25.md` | [[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] + [[../../wiki/concepts/Luxury-Brands#dior|Dior]] | 25 |
| `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch2-50.md` | [[../../wiki/concepts/Luxury-Brands#louis-vuitton|LV]] + [[../../wiki/concepts/Luxury-Brands#gucci|Gucci]] + Caps | 25 |
| `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch3-100.md` | Lifestyle + Urgency | 50 |

---

## 🚀 POUR [[../../wiki/people/Thomas-Cogne|Thomas]] - Prochaines Étapes

### 1. Configurer Higgsfield (5 min)
```bash
# Ajouter à ~/.zshrc
export HF_CREDENTIALS="VOTRE_KEY_ID:VOTRE_KEY_SECRET"

# Ou éditer directement
nano /Users/vakandi/EliaAI/[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py
# Ligne 36: HF_CREDENTIALS = "votre_clé"
```

### 2. Tester génération (10 min)
```bash
cd /Users/vakandi/EliaAI
python3 [[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py --help

# Générer une image test
python3 [[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py image \
  --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] sneakers on white marble, luxury [[../../wiki/businesses/Bene2Luxe#products|Product]] photography" \
  --[[../../wiki/concepts/File-Management|Output]] ./test_image.png

# Générer une vidéo test
python3 [[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] \
  --image ./test_image.png \
  --[[../../wiki/concepts/File-Management|Output]] ./test_video.mp4 \
  --duration 5
```

### 3. Générer 5 vidéos (1h)
1. Lire script #1 ([[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] La Pause - Grey Luxe)
2. Générer image produit
3. Générer vidéo
4. Télécharger vers [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]/[[../../wiki/channels/Snapchat|Snapchat]]
5. Poster avec description du script

---

## 📋 POUR [[../../wiki/people/Rida|Rida]] - Calendrier de Publication

### Ordre de priorité:
1. Scripts Urgency (#20, #56-58, #73) - Créez un sentiment d'urgence
2. Scripts [[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] (#1-4, #11, #17, #21) - Produits populaires
3. Scripts [[../../wiki/concepts/Luxury-Brands#dior|Dior]] (#5-10, #12, #18, #22-23) - Deuxième priorité
4. Scripts [[../../wiki/concepts/Luxury-Brands#louis-vuitton|LV]] (#26-28) - Statut/Investissement
5. Scripts [[../../wiki/concepts/Luxury-Brands#gucci|Gucci]] (#29-31) - Qualité/Artisanat

### Plan suggéré:
- **Semaine 1:** 10 vidéos (2/jour)
- **Semaine 2:** 20 vidéos (4/jour)
- **Semaine 3:** 30 vidéos (6/jour)
- **Semaine 4:** 40 vidéos (8/jour)

---

## 🛍️ POUR [[../../wiki/people/Ali|Ali]] - Validation Produits

### Checklist:
- [ ] Vérifier [[../../wiki/skills/Higgsfield-Video|Images]] ComfyUI existantes
  - `/Users/vakandi/ComfyUI/bene2luxe_products_data/generated/`
- [ ] Ajouter nouveaux produits au catalogue
- [ ] Préparer descriptions [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] basées sur les scripts
- [ ] Confirmer disponibilité et prix

### Produits actuels:
| Marque | Produit | Prix | [[../../wiki/topics/Infrastructure-Timeline|Status]] |
|--------|---------|------|--------|
| [[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] | La Pause Sneakers | €170 | ✅ |
| [[../../wiki/concepts/Luxury-Brands#dior|Dior]] | D-BEJE 3 Sunglasses | €195 | ✅ |
| [[../../wiki/concepts/Luxury-Brands#dior|Dior]] | B23 Sneakers | À vérifier | ✅ |
| [[../../wiki/concepts/Luxury-Brands#louis-vuitton|LV]] | Bag/Accessoires | À vérifier | ✅ |
| [[../../wiki/concepts/Luxury-Brands#gucci|Gucci]] | Accessoires/Vêtements | À vérifier | ✅ |
| Caps | Casquettes [[../../wiki/concepts/Pricing|Premium]] | À vérifier | ✅ |

---

## 📍 Emplacements Fichiers

```
EliaAI/
├── [[../../wiki/HOME|Docs]]/2026-03-26/
│   ├── [[../../wiki/concepts/Marketing-Concepts|Content]]-strategy-[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]].md    # Stratégie complète
│   ├── [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-production-checklist.md     # Guide production
│   ├── [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch1-25.md       # Scripts 1-25
│   ├── [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch2-50.md       # Scripts 26-50
│   └── [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch3-100.md      # Scripts 51-100
├── [[../../wiki/tools/Index|TOOLS]]/
│   └── bene2luxe_higgsfield.py          # Script génération
└── ComfyUI/
    └── bene2luxe_products_data/generated/  # [[../../wiki/skills/Higgsfield-Video|Images]] produits
```

---

## 🎯 Objectif Avril 2026

- ✅ 100+ vidéos prêtes (DONE)
- ⏳ 50+ vidéos générées (À faire)
- ⏳ 25+ publiées (À faire)
- ⏳ [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] catalog mis à jour (À faire)

---

## 📞 Contact Rapide

- **[[../../wiki/people/Thomas-Cogne|Thomas]]:** Configuration Higgsfield, Credentials [[../../wiki/concepts/API-Integration|API]]
- **[[../../wiki/people/Rida|Rida]]:** Scripts vidéo, Descriptions, Calendrier
- **[[../../wiki/people/Ali|Ali]]:** Validation produits, Photos, Catalog
- **[[../../wiki/people/Wael|Wael]]:** Stratégie globale, Approval final

---

*Document créé par [[../../wiki/people/Elia|Elia]] - 26 Mars 2026*
