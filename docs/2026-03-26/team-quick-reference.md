# 📱 Bene2Luxe Video Scripts - Team Quick Reference
## Pour Thomas, Rida, Ali - Mars 2026

---

## 🎬 CE QUI EST PRÊT

### ✅ 100 Scripts Vidéo (Format Alex Hormozi 20/40/40)

| Fichier | Contenu | Scripts |
|---------|---------|---------|
| `video-scripts-batch1-25.md` | Chanel + Dior | 25 |
| `video-scripts-batch2-50.md` | LV + Gucci + Caps | 25 |
| `video-scripts-batch3-100.md` | Lifestyle + Urgency | 50 |

---

## 🚀 POUR THOMAS - Prochaines Étapes

### 1. Configurer Higgsfield (5 min)
```bash
# Ajouter à ~/.zshrc
export HF_CREDENTIALS="VOTRE_KEY_ID:VOTRE_KEY_SECRET"

# Ou éditer directement
nano /Users/vakandi/EliaAI/tools/bene2luxe_higgsfield.py
# Ligne 36: HF_CREDENTIALS = "votre_clé"
```

### 2. Tester génération (10 min)
```bash
cd /Users/vakandi/EliaAI
python3 tools/bene2luxe_higgsfield.py --help

# Générer une image test
python3 tools/bene2luxe_higgsfield.py image \
  --prompt "Chanel sneakers on white marble, luxury product photography" \
  --output ./test_image.png

# Générer une vidéo test
python3 tools/bene2luxe_higgsfield.py video \
  --image ./test_image.png \
  --output ./test_video.mp4 \
  --duration 5
```

### 3. Générer 5 vidéos (1h)
1. Lire script #1 (Chanel La Pause - Grey Luxe)
2. Générer image produit
3. Générer vidéo
4. Télécharger vers TikTok/Snapchat
5. Poster avec description du script

---

## 📋 POUR RIDA - Calendrier de Publication

### Ordre de priorité:
1. Scripts Urgency (#20, #56-58, #73) - Créez un sentiment d'urgence
2. Scripts Chanel (#1-4, #11, #17, #21) - Produits populaires
3. Scripts Dior (#5-10, #12, #18, #22-23) - Deuxième priorité
4. Scripts LV (#26-28) - Statut/Investissement
5. Scripts Gucci (#29-31) - Qualité/Artisanat

### Plan suggéré:
- **Semaine 1:** 10 vidéos (2/jour)
- **Semaine 2:** 20 vidéos (4/jour)
- **Semaine 3:** 30 vidéos (6/jour)
- **Semaine 4:** 40 vidéos (8/jour)

---

## 🛍️ POUR ALI - Validation Produits

### Checklist:
- [ ] Vérifier images ComfyUI existantes
  - `/Users/vakandi/ComfyUI/bene2luxe_products_data/generated/`
- [ ] Ajouter nouveaux produits au catalogue
- [ ] Préparer descriptions WhatsApp basées sur les scripts
- [ ] Confirmer disponibilité et prix

### Produits actuels:
| Marque | Produit | Prix | Status |
|--------|---------|------|--------|
| Chanel | La Pause Sneakers | €170 | ✅ |
| Dior | D-BEJE 3 Sunglasses | €195 | ✅ |
| Dior | B23 Sneakers | À vérifier | ✅ |
| LV | Bag/Accessoires | À vérifier | ✅ |
| Gucci | Accessoires/Vêtements | À vérifier | ✅ |
| Caps | Casquettes Premium | À vérifier | ✅ |

---

## 📍 Emplacements Fichiers

```
EliaAI/
├── docs/2026-03-26/
│   ├── content-strategy-bene2luxe.md    # Stratégie complète
│   ├── video-production-checklist.md     # Guide production
│   ├── video-scripts-batch1-25.md       # Scripts 1-25
│   ├── video-scripts-batch2-50.md       # Scripts 26-50
│   └── video-scripts-batch3-100.md      # Scripts 51-100
├── tools/
│   └── bene2luxe_higgsfield.py          # Script génération
└── ComfyUI/
    └── bene2luxe_products_data/generated/  # Images produits
```

---

## 🎯 Objectif Avril 2026

- ✅ 100+ vidéos prêtes (DONE)
- ⏳ 50+ vidéos générées (À faire)
- ⏳ 25+ publiées (À faire)
- ⏳ WhatsApp catalog mis à jour (À faire)

---

## 📞 Contact Rapide

- **Thomas:** Configuration Higgsfield, Credentials API
- **Rida:** Scripts vidéo, Descriptions, Calendrier
- **Ali:** Validation produits, Photos, Catalog
- **Wael:** Stratégie globale, Approval final

---

*Document créé par Elia - 26 Mars 2026*
