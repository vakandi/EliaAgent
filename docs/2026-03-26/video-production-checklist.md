# 🎬 Bene2Luxe Video Production Checklist
## Guide pour l'équipe - Génération de vidéos avec Higgsfield

**Dernière mise à jour:** 26 Mars 2026
**Status:** Prêt pour production

---

## 📋 Vue d'ensemble

Ce guide explique comment utiliser les 100 scripts vidéo créés et le système Higgsfield pour générer des vidéos TikTok/Reels.

### Ressources disponibles:
- **100 scripts vidéo** (Alex Hormozi 20/40/40 format)
- **Higgsfield API** (Nano Banana Pro + Kling 3.0)
- **Outil de génération** (`tools/bene2luxe_higgsfield.py`)

---

## 🚀 Étape 1: Configuration Higgsfield

### Obtenir les credentials:
1. Aller sur https://cloud.higgsfield.ai
2. Créer un compte si pas encore fait
3. Récupérer API Key ( KEY_ID:KEY_SECRET )

### Configurer l'environnement:
```bash
# Option 1: Variable d'environnement
export HF_CREDENTIALS="YOUR_KEY_ID:YOUR_KEY_SECRET"

# Option 2: Éditer le script directement
nano /Users/vakandi/EliaAI/tools/bene2luxe_higgsfield.py
# Ligne 36: HF_CREDENTIALS = "votre_clé_ici"
```

### Installer les dépendances:
```bash
pip install higgsfield-client pillow requests
```

---

## 🎥 Étape 2: Générer des images produits

### Images individuelles:
```bash
python3 /Users/vakandi/EliaAI/tools/bene2luxe_higgsfield.py \
  image \
  --prompt "Chanel La Pause grey suede sneakers on white marble, luxury product photography" \
  --output ./generated/chanel_01.png \
  --aspect 1:1
```

### Batch d'images:
```bash
# Voir les prompts disponibles
python3 /Users/vakandi/EliaAI/tools/bene2luxe_higgsfield.py prompts

# Générer 5 images d'une catégorie
python3 /Users/vakandi/EliaAI/tools/bene2luxe_higgsfield.py batch \
  --dir ./products/ \
  --count 5 \
  --type image
```

---

## 🎬 Étape 3: Générer des vidéos

### Vidéo à partir d'une image:
```bash
python3 /Users/vakandi/EliaAI/tools/bene2luxe_higgsfield.py \
  video \
  --image ./generated/chanel_01.png \
  --output ./videos/chanel_01.mp4 \
  --duration 5
```

### Batch vidéos (répertoire):
```bash
# Générer des vidéos depuis toutes les images dans un dossier
python3 /Users/vakandi/EliaAI/tools/bene2luxe_higgsfield.py \
  batch \
  --dir ./generated/ \
  --count 50 \
  --type video
```

---

## 📊 Étape 4: Plan de production

### Objectif: 50 vidéos cette semaine

| Jour | Scripts | Statut |
|------|---------|--------|
| Jour 1 | Scripts 1-10 (Chanel) | À faire |
| Jour 2 | Scripts 11-20 (Dior) | À faire |
| Jour 3 | Scripts 21-30 (LV) | À faire |
| Jour 4 | Scripts 31-40 (Gucci) | À faire |
| Jour 5 | Scripts 41-50 (Lifestyle) | À faire |

### Contenu par marque:

**Chanel (Scripts 1-10):**
- Chanel La Pause grey suede, green sole
- Focus: qualité, héritage, style parisien

**Dior (Scripts 11-20):**
- Dior B23 white canvas sneakers
- Dior D-BEJE 3 sunglasses
- Focus: design, transparence, élégance

**Louis Vuitton (Scripts 21-30):**
- LV monogram collection
- Focus: statut, investissement, iconicité

**Gucci (Scripts 31-40):**
- GG hardware, Italian leather
- Focus: craftsmanship, Italian quality

**Lifestyle (Scripts 41-50):**
- Outfit combos, spring/summer
- Focus: aspiration, lifestyle

---

## 🎯 Workflow Recommandé

### Pour chaque vidéo:
1. **Lire le script** (fichier batch correspondant)
2. **Générer image produit** avec Higgsfield
3. **Générer vidéo** depuis l'image
4. **Télécharger** vers TikTok/YouTube
5. **Poster** avec description du script

### Commandes rapides:
```bash
# 1. Setup
cd /Users/vakandi/EliaAI
source ~/.zshrc

# 2. Configurer credentials
export HF_CREDENTIALS="votre_clé"

# 3. Générer image
python3 tools/bene2luxe_higgsfield.py image \
  --prompt "votre prompt" \
  --output ./temp/product.png

# 4. Générer vidéo
python3 tools/bene2luxe_higgsfield.py video \
  --image ./temp/product.png \
  --output ./temp/product_video.mp4
```

---

## 📁 Emplacements fichiers

| Type | Emplacement |
|------|-------------|
| Scripts vidéo | `docs/2026-03-26/video-scripts-batch*.md` |
| Outil Higgsfield | `tools/bene2luxe_higgsfield.py` |
| Images ComfyUI | `~/ComfyUI/bene2luxe_products_data/generated/` |
| Videos générées | `tools/generated/` (à créer) |

---

## ⚠️ Notes importantes

1. **Credentials Higgsfield**: Thomas doit fournir la clé API
2. **Rate limiting**: 2-5 sec entre chaque génération
3. **Format**: 9:16 (vertical) pour TikTok/Reels
4. **Durée**: 5-15 sec selon modèle

---

## ✅ Checklist Production

- [ ] Configurer credentials Higgsfield
- [ ] Tester génération image
- [ ] Tester génération vidéo
- [ ] Générer 10 vidéos/jour
- [ ] Poster sur TikTok
- [ ] Poster sur YouTube Shorts
- [ ] Monitorer engagement

---

## 📞 Contact

- **Thomas**: Configuration serveur, credentials
- **Rida**: Scripts vidéo, descriptions
- **Ali**: Validation produits, photos
- **Wael**: Stratégie globale, approval

---

**Prochaines étapes:**
1. Thomas configure Higgsfield API key
2. Test génération de 5 vidéos
3. Validation qualité
4. Lancement production en masse
