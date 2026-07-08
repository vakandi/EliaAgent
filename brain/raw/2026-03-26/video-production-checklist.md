# 🎬 [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] Production Checklist
## Guide pour l'équipe - Génération de vidéos avec Higgsfield

**Dernière mise à jour:** 26 Mars 2026
**Status:** Prêt pour production

---

## 📋 Vue d'ensemble

Ce guide explique comment utiliser les 100 scripts vidéo créés et le système Higgsfield pour générer des vidéos [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]/Reels.

### Ressources disponibles:
- **100 scripts vidéo** (Alex Hormozi 20/40/40 format)
- **Higgsfield [[../../wiki/concepts/API-Integration|API]]** (Nano Banana Pro + Kling 3.0)
- **Outil de génération** (`[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py`)

---

## 🚀 Étape 1: Configuration Higgsfield

### Obtenir les credentials:
1. Aller sur [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://[[../../wiki/systems/Docker-Servers|Cloud]].higgsfield.[[../../wiki/concepts/AI-Automation|AI]]
2. Créer un compte si pas encore fait
3. Récupérer [[../../wiki/concepts/API-Integration|API]] Key ( KEY_ID:KEY_SECRET )

### Configurer l'environnement:
```bash
# Option 1: Variable d'environnement
export HF_CREDENTIALS="YOUR_KEY_ID:YOUR_KEY_SECRET"

# Option 2: Éditer le [[../../wiki/concepts/Marketing-Concepts|Script]] directement
nano /Users/vakandi/[[../../wiki/people/Elia|Elia]]/[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py
# Ligne 36: HF_CREDENTIALS = "votre_clé_ici"
```

### Installer les dépendances:
```bash
pip install higgsfield-client pillow requests
```

---

## 🎥 Étape 2: Générer des [[../../wiki/skills/Higgsfield-Video|Images]] produits

### [[../../wiki/skills/Higgsfield-Video|Images]] individuelles:
```bash
python3 /Users/vakandi/[[../../wiki/people/Elia|Elia]]/[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py \
  image \
  --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] La Pause grey suede sneakers on white marble, luxury [[../../wiki/businesses/Bene2Luxe#products|Product]] photography" \
  --[[../../wiki/concepts/File-Management|Output]] ./generated/chanel_01.png \
  --aspect 1:1
```

### Batch d'[[../../wiki/skills/Higgsfield-Video|Images]]:
```bash
# Voir les prompts disponibles
python3 /Users/vakandi/[[../../wiki/people/Elia|Elia]]/[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py prompts

# Générer 5 [[../../wiki/skills/Higgsfield-Video|Images]] d'une catégorie
python3 /Users/vakandi/[[../../wiki/people/Elia|Elia]]/[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py batch \
  --dir ./products/ \
  --count 5 \
  --type image
```

---

## 🎬 Étape 3: Générer des vidéos

### Vidéo à partir d'une image:
```bash
python3 /Users/vakandi/[[../../wiki/people/Elia|Elia]]/[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py \
  [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] \
  --image ./generated/chanel_01.png \
  --[[../../wiki/concepts/File-Management|Output]] ./videos/chanel_01.mp4 \
  --duration 5
```

### Batch vidéos (répertoire):
```bash
# Générer des vidéos depuis toutes les [[../../wiki/skills/Higgsfield-Video|Images]] dans un dossier
python3 /Users/vakandi/[[../../wiki/people/Elia|Elia]]/[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py \
  batch \
  --dir ./generated/ \
  --count 50 \
  --type [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
```

---

## 📊 Étape 4: Plan de production

### Objectif: 50 vidéos cette semaine

| Jour | Scripts | Statut |
|------|---------|--------|
| Jour 1 | Scripts 1-10 ([[../../wiki/concepts/Luxury-Brands#chanel|Chanel]]) | À faire |
| Jour 2 | Scripts 11-20 ([[../../wiki/concepts/Luxury-Brands#dior|Dior]]) | À faire |
| Jour 3 | Scripts 21-30 (LV) | À faire |
| Jour 4 | Scripts 31-40 ([[../../wiki/concepts/Luxury-Brands#gucci|Gucci]]) | À faire |
| Jour 5 | Scripts 41-50 (Lifestyle) | À faire |

### Contenu par marque:

**[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] (Scripts 1-10):**
- [[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] La Pause grey suede, green sole
- Focus: qualité, héritage, style parisien

**[[../../wiki/concepts/Luxury-Brands#dior|Dior]] (Scripts 11-20):**
- [[../../wiki/concepts/Luxury-Brands#dior|Dior]] B23 white canvas sneakers
- [[../../wiki/concepts/Luxury-Brands#dior|Dior]] D-BEJE 3 sunglasses
- Focus: design, transparence, élégance

**[[../../wiki/concepts/Luxury-Brands#louis-vuitton|Louis Vuitton]] (Scripts 21-30):**
- LV monogram collection
- Focus: statut, investissement, iconicité

**[[../../wiki/concepts/Luxury-Brands#gucci|Gucci]] (Scripts 31-40):**
- GG hardware, Italian leather
- Focus: craftsmanship, Italian quality

**Lifestyle (Scripts 41-50):**
- Outfit combos, spring/summer
- Focus: aspiration, lifestyle

---

## 🎯 Workflow Recommandé

### Pour chaque vidéo:
1. **Lire le [[../../wiki/concepts/Marketing-Concepts|Script]]** (fichier batch correspondant)
2. **Générer image produit** avec Higgsfield
3. **Générer vidéo** depuis l'image
4. **Télécharger** vers [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]/YouTube
5. **Poster** avec description du [[../../wiki/concepts/Marketing-Concepts|Script]]

### Commandes rapides:
```bash
# 1. Setup
cd /Users/vakandi/[[../../wiki/people/Elia|Elia]]
source ~/.zshrc

# 2. Configurer credentials
export HF_CREDENTIALS="votre_clé"

# 3. Générer image
python3 [[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py image \
  --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "votre [[../../wiki/concepts/Prompt-Engineering|PROMPT]]" \
  --[[../../wiki/concepts/File-Management|Output]] ./temp/[[../../wiki/businesses/Bene2Luxe#products|Product]].png

# 4. Générer vidéo
python3 [[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] \
  --image ./temp/[[../../wiki/businesses/Bene2Luxe#products|Product]].png \
  --[[../../wiki/concepts/File-Management|Output]] ./temp/product_video.mp4
```

---

## 📁 Emplacements fichiers

| Type | Emplacement |
|------|-------------|
| Scripts vidéo | `[[../../wiki/HOME|Docs]]/2026-03-26/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-scripts-batch*.md` |
| Outil Higgsfield | `[[../../wiki/tools/Index|TOOLS]]/bene2luxe_higgsfield.py` |
| [[../../wiki/skills/Higgsfield-Video|Images]] ComfyUI | `~/ComfyUI/bene2luxe_products_data/generated/` |
| Videos générées | `[[../../wiki/tools/Index|TOOLS]]/generated/` (à créer) |

---

## ⚠️ Notes importantes

1. **Credentials Higgsfield**: [[../../wiki/people/Thomas-Cogne|Thomas]] doit fournir la clé [[../../wiki/concepts/API-Integration|API]]
2. **Rate limiting**: 2-5 sec entre chaque génération
3. **Format**: 9:16 (vertical) pour [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]/Reels
4. **Durée**: 5-15 sec selon modèle

---

## ✅ Checklist Production

- [ ] Configurer credentials Higgsfield
- [ ] Tester génération image
- [ ] Tester génération vidéo
- [ ] Générer 10 vidéos/jour
- [ ] Poster sur [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]
- [ ] Poster sur YouTube Shorts
- [ ] Monitorer engagement

---

## 📞 Contact

- **[[../../wiki/people/Thomas-Cogne|Thomas]]**: Configuration serveur, credentials
- **[[../../wiki/people/Rida|Rida]]**: Scripts vidéo, descriptions
- **[[../../wiki/people/Ali|Ali]]**: Validation produits, photos
- **[[../../wiki/people/Wael|Wael]]**: Stratégie globale, approval

---

**Prochaines étapes:**
1. [[../../wiki/people/Thomas-Cogne|Thomas]] configure Higgsfield [[../../wiki/concepts/API-Integration|API]] key
2. Test génération de 5 vidéos
3. Validation qualité
4. Lancement production en masse
