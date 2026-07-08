# 🎬 [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] × Higgfields - [[../../wiki/docs/Sessions|Complete]] [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] Generation System

**[[../../wiki/topics/Infrastructure-Timeline|Date]]**: 26 Mars 2026  
**Purpose**: Generate 150 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] scripts + automation scripts for [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] [[../../wiki/concepts/Marketing-Concepts|Content]]

---

## 📋 TABLE OF CONTENTS

1. [Quick Start](#-quick-start)
2. [Script Organization](#-script-organization)
3. [[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] Generation Scripts](#-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-generation-scripts)
4. [[[../../wiki/concepts/Marketing-Concepts|Content]] Scripts (150)](#-[[../../wiki/concepts/Marketing-Concepts|Content]]-scripts-150)
5. [[[../../wiki/skills/Higgsfield-Video|Mascoot]] Mini-TV Show](#-[[../../wiki/skills/Higgsfield-Video|Mascoot]]-mini-tv-show)
6. [Generation [[../../wiki/concepts/AI-Automation|Workflow]]](#-generation-[[../../wiki/concepts/AI-Automation|Workflow]])
7. [Models & Credits](#-models--credits)

---

## 🚀 QUICK START

### Setup
```bash
# Install dependencies
pip3 install higgsfield-client requests pillow --break-system-packages

# Set credentials
export HF_CREDENTIALS="YOUR_KEY_ID:YOUR_KEY_SECRET"
```

### Generate [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
```bash
# Single [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] from image
python3 higgfields_master.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] --image [[../../wiki/businesses/Bene2Luxe#products|Product]].png --model kling-3

# Single [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] from [[../../wiki/concepts/Prompt-Engineering|PROMPT]]
python3 higgfields_master.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "Luxury sneakers rotating on white background" --model kling-3

# Batch generate 50 videos
python3 higgfields_master.py batch --type [[../../wiki/businesses/Bene2Luxe#products|Product]] --count 50 --model kling-3

# [[../../wiki/skills/Higgsfield-Video|Mascoot]] episode
python3 higgfields_master.py mascott --episode 1 --model kling-3
```

---

## 📁 SCRIPT ORGANIZATION

```
[[../../wiki/HOME|Docs]]/2026-03-26/higgfields-scripts/
├── higgfields_master.py          # Master script (all models)
├── kling-3.0/
│   └── kling_scripts.py          # Kling 3.0 specific scripts
├── nano-banano-pro/
│   └── nano_banano_scripts.py    # Nano Banano specific scripts
└── free-models/
    └── free_models.py            # Free model scripts (Wan, Minimax)

[[../../wiki/HOME|Docs]]/2026-03-26/[[../../wiki/concepts/Marketing-Concepts|Content]]/
├── [[../../wiki/concepts/Ads-Funnel#cta|CTA]]/
│   └── [[../../wiki/concepts/Ads-Funnel#cta|CTA]]-scripts-51-110.md     # 60 [[../../wiki/concepts/Ads-Funnel#cta|CTA]] scripts
├── entertainment/
│   └── entertainment-scripts-111-170.md  # 60 entertainment scripts
└── trends/
    └── trends-scripts-171-200.md # 40 trend scripts

[[../../wiki/HOME|Docs]]/2026-03-26/mascott-show/
├── mascott-episodes-01-50.md     # [[../../wiki/skills/Higgsfield-Video|Mascoot]] episodes 1-50
└── mascott-episodes-51-75.md     # [[../../wiki/skills/Higgsfield-Video|Mascoot]] episodes 51-75
```

---

## 🎬 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] GENERATION SCRIPTS

### 1. Higgfields Master (higgfields_master.py)

**Purpose**: Unified script for all models via Higgfields platform

**Models**:
| Model | Type | Credits | Use Case |
|-------|------|---------|----------|
| `nano-banano` | Image | 1 | [[../../wiki/businesses/Bene2Luxe#products|Product]] images (4K fast) |
| `flux-pro` | Image | 2 | Best quality images |
| `flux-dev` | Image | FREE | Testing/previews |
| `kling-3` | [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] | 3 | Primary [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] generation |
| `kling-standard` | [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] | 2 | Faster [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] |
| `wan-2` | [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] | FREE | Free [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] tier |
| `minimax` | [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] | FREE | Free [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] tier |

**Usage**:
```bash
# Image generation
python3 higgfields_master.py image --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] sneakers luxury" --model nano-banano

# [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] from image
python3 higgfields_master.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] --image [[../../wiki/businesses/Bene2Luxe#products|Product]].png --model kling-3 --duration 10

# [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] from [[../../wiki/concepts/Prompt-Engineering|PROMPT]]
python3 higgfields_master.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "Animated mascott in Paris" --model kling-3

# Batch generation
python3 higgfields_master.py batch --type [[../../wiki/businesses/Bene2Luxe#products|Product]] --count 50 --model kling-3

# [[../../wiki/skills/Higgsfield-Video|Mascoot]] episode
python3 higgfields_master.py mascott --episode 1

# [[../../wiki/concepts/[[../../wiki/channels/Google|Search]]|List]] models
python3 higgfields_master.py models
```

---

### 2. Kling 3.0 Scripts (kling_scripts.py)

**Purpose**: Direct Kling [[../../wiki/concepts/API-Integration|API]] integration (when available)

**Models**:
- `kling-v3` - Latest Kling 3.0
- `kling-v2.6-pro` - Professional quality
- `kling-v2.6-std` - Standard quality
- `kling-v2.5-turbo` - Fastest

**Usage**:
```bash
# Text-to-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
python3 kling_scripts.py t2v --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "Luxury sneakers rotating" --duration 5

# Image-to-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
python3 kling_scripts.py i2v --image [[../../wiki/businesses/Bene2Luxe#products|Product]].png --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "Sneaker slowly turning"

# Batch from [[../../wiki/concepts/File-Management|File]]
python3 kling_scripts.py batch --[[../../wiki/concepts/File-Management|File]] prompts.txt --count 50

# Category-specific
python3 kling_scripts.py category --category chanel_sneakers --count 5

# [[../../wiki/concepts/[[../../wiki/channels/Google|Search]]|List]] prompts
python3 kling_scripts.py prompts
```

---

### 3. Nano Banano Scripts (nano_banano_scripts.py)

**Purpose**: Image + [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] generation via Nano Banano

**Usage**:
```bash
# Generate image
python3 nano_banano_scripts.py image --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] sneakers on marble"

# Generate [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
python3 nano_banano_scripts.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] --image [[../../wiki/businesses/Bene2Luxe#products|Product]].png

# Batch images
python3 nano_banano_scripts.py batch --[[../../wiki/concepts/File-Management|File]] prompts.txt --type image

# [[../../wiki/concepts/[[../../wiki/channels/Google|Search]]|List]] available prompts
python3 nano_banano_scripts.py prompts
```

---

### 4. Free Models (free_models.py)

**Purpose**: Unlimited free-tier generation

**Models**:
- `flux-dev/text-to-image` - Free image
- `wan/wan-[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-generation` - Free [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
- `minimax/haibo/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]-generation` - Free [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]

**Usage**:
```bash
# Free image
python3 free_models.py image --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "[[../../wiki/concepts/Luxury-Brands|Fashion]] [[../../wiki/concepts/Marketing-Concepts|Content]]"

# Free [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
python3 free_models.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] --image photo.png

# Batch free
python3 free_models.py batch --[[../../wiki/concepts/File-Management|File]] prompts.txt --type [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
```

---

## 📝 [[../../wiki/concepts/Marketing-Concepts|Content]] SCRIPTS (150)

### Distribution

| Category | Percentage | Count | [[../../wiki/concepts/File-Management|File]] |
|----------|-----------|-------|------|
| **[[../../wiki/concepts/Ads-Funnel#cta|CTA]]** (Direct [[../../wiki/businesses/Bene2Luxe#revenue|Sales]]) | 40% | 60 | `[[../../wiki/concepts/Marketing-Concepts|Content]]/[[../../wiki/concepts/Ads-Funnel#cta|CTA]]/[[../../wiki/concepts/Ads-Funnel#cta|CTA]]-scripts-51-110.md` |
| **Entertainment** (Lifestyle/Humor) | 40% | 60 | `[[../../wiki/concepts/Marketing-Concepts|Content]]/entertainment/entertainment-scripts-111-170.md` |
| **Trends** (Viral/Social) | 20% | 40 | `[[../../wiki/concepts/Marketing-Concepts|Content]]/trends/trends-scripts-171-200.md` |
| **TOTAL** | 100% | 160 | |

### Script Format (Alex Hormozi 20/40/40)

```
🎣 [[../../wiki/concepts/Ads-Funnel#hook|Hook]] (0-4s): Grab attention
💎 [[../../wiki/concepts/Pricing|Value]] (4-12s): Educate or entertain
📞 [[../../wiki/concepts/Ads-Funnel#cta|CTA]] (12-20s): Call to action
```

### [[../../wiki/concepts/Ads-Funnel#cta|CTA]] Scripts Examples
- Direct [[../../wiki/businesses/Bene2Luxe#products|Product]] showcases
- Limited stock urgency
- [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] ordering process
- Price comparison [[../../wiki/concepts/Pricing|Value]]

### Entertainment Scripts Examples
- French humor (Le French Dream)
- TV show tie-ins (Les Traîtres, Koh Lanta)
- Lifestyle [[../../wiki/concepts/Marketing-Concepts|Content]] (GRWM, OOTD)
- Storytime formats

### Trends Scripts Examples
- Trending challenges (#SixSeven)
- [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]] format participation
- [[../../wiki/concepts/Luxury-Brands|Fashion]] Week reactions
- Viral [[../../wiki/concepts/Marketing-Concepts|Content]] formats

---

## 🎭 [[../../wiki/skills/Higgsfield-Video|Mascoot]] MINI-TV SHOW

### Concept
A luxury [[../../wiki/skills/Higgsfield-Video|Mascoot]] character arrives in France/[[../../wiki/concepts/Location-Targeting#switzerland|Switzerland]] and has adventures discovering luxury [[../../wiki/concepts/Luxury-Brands|Fashion]] and French culture.

### Episodes Structure

| Season | Episodes | Location | Theme |
|--------|----------|----------|-------|
| Season 1 | 1-25 | Paris | Discovery |
| Season 2 | 26-50 | [[../../wiki/concepts/Location-Targeting#switzerland|Switzerland]] | Alpine luxury |
| Season 3 | 51-75 | Côte d'Azur | Mediterranean |
| Season 4 | 76-100 | Shopping | Collection |

### Episode Format
```
🎬 EPISODE [#]: "[TITLE]"
📍 Location: [LOCATION]
⏱️ Duration: 15-20 seconds

🎣 [[../../wiki/concepts/Ads-Funnel#hook|Hook]] (0-3s): Attention grabber
🎭 ADVENTURE (3-12s): [[../../wiki/skills/Higgsfield-Video|Mascoot]]'s journey
📞 [[../../wiki/concepts/Ads-Funnel#cta|CTA]] (12-20s): [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] mention
```

### Animation Prompts
```bash
# Paris episode
python3 higgfields_master.py mascott --episode 1 --model kling-3

# Swiss episode
python3 higgfields_master.py mascott --episode 26 --model kling-3

# Generate all 75 episodes
for i in {1..75}; do
  python3 higgfields_master.py mascott --episode $i
done
```

---

## 🔄 GENERATION [[../../wiki/concepts/AI-Automation|Workflow]]

### Phase 1: [[../../wiki/businesses/Bene2Luxe#products|Product]] Images
```bash
# Generate [[../../wiki/businesses/Bene2Luxe#products|Product]] images (Nano Banano Pro - 4K)
python3 nano_banano_scripts.py category --category chanel_la_pause --count 3
python3 nano_banano_scripts.py category --category dior_b23 --count 3
python3 nano_banano_scripts.py category --category dior_sunglasses --count 3
python3 nano_banano_scripts.py category --category louis_vuitton --count 3
python3 nano_banano_scripts.py category --category [[../../wiki/concepts/Luxury-Brands#gucci|Gucci]] --count 3
python3 nano_banano_scripts.py category --category caps --count 3
```

### Phase 2: [[../../wiki/businesses/Bene2Luxe#products|Product]] Videos
```bash
# Generate [[../../wiki/businesses/Bene2Luxe#products|Product]] videos (Kling 3.0 - primary)
python3 kling_scripts.py batch --[[../../wiki/concepts/File-Management|File]] product_prompts.txt --count 50 --model kling-3

# Fallback to free models if credits low
python3 free_models.py batch --[[../../wiki/concepts/File-Management|File]] product_prompts.txt --count 50 --type [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
```

### Phase 3: [[../../wiki/skills/Higgsfield-Video|Mascoot]] [[../../wiki/concepts/Marketing-Concepts|Content]]
```bash
# Generate [[../../wiki/skills/Higgsfield-Video|Mascoot]] episodes (Kling 3.0 - 15s)
python3 higgfields_master.py mascott --episode 1
# Repeat for episodes 2-75
```

### Phase 4: Lifestyle/Trends
```bash
# Generate trending [[../../wiki/concepts/Marketing-Concepts|Content]] (Free models - unlimited)
python3 free_models.py batch --[[../../wiki/concepts/File-Management|File]] trending_prompts.txt --count 50 --type [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]
```

---

## 💳 MODELS & CREDITS

### Available Credits (~200 total)

| Model | Credits | Primary Use |
|-------|---------|-------------|
| Nano Banano Pro | ~600 | [[../../wiki/businesses/Bene2Luxe#products|Product]] images |
| Kling 3.0 | ~200 | Primary videos |
| Flux Dev | ∞ (free) | Testing |
| Wan 2.2 | ∞ (free) | Backup videos |
| Minimax | ∞ (free) | Backup videos |

### Recommended Usage

| [[../../wiki/concepts/Marketing-Concepts|Content]] Type | Model | Priority |
|-------------|-------|----------|
| [[../../wiki/businesses/Bene2Luxe#products|Product]] showcases | Kling 3.0 | HIGH |
| [[../../wiki/skills/Higgsfield-Video|Mascoot]] adventures | Kling 3.0 | HIGH |
| Trending [[../../wiki/concepts/Marketing-Concepts|Content]] | Wan 2.2 | MEDIUM |
| Testing/previews | Flux Dev | FREE |
| [[../../wiki/businesses/Bene2Luxe#products|Product]] images | Nano Banano Pro | HIGH |

---

## 📊 BATCH PROMPTS FILES

### [[../../wiki/businesses/Bene2Luxe#products|Product]] Prompts (for videos)
Located in: `[[../../wiki/HOME|Docs]]/2026-03-26/higgfields-scripts/batch-prompts/`

| [[../../wiki/concepts/File-Management|File]] | [[../../wiki/concepts/Marketing-Concepts|Content]] | Count |
|------|---------|-------|
| `[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]]-[[../../wiki/concepts/Prompt-Engineering|PROMPT]].txt` | [[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] La Pause prompts | 10 |
| `[[../../wiki/concepts/Luxury-Brands#dior|Dior]]-[[../../wiki/concepts/Prompt-Engineering|PROMPT]].txt` | [[../../wiki/concepts/Luxury-Brands#dior|Dior]] B23 & sunglasses prompts | 10 |
| `lv-[[../../wiki/concepts/Prompt-Engineering|PROMPT]].txt` | [[../../wiki/concepts/Luxury-Brands#louis-vuitton|Louis Vuitton]] prompts | 10 |
| `[[../../wiki/concepts/Luxury-Brands#gucci|Gucci]]-[[../../wiki/concepts/Prompt-Engineering|PROMPT]].txt` | [[../../wiki/concepts/Luxury-Brands#gucci|Gucci]] prompts | 10 |
| `lifestyle-[[../../wiki/concepts/Prompt-Engineering|PROMPT]].txt` | Lifestyle prompts | 10 |

### [[../../wiki/skills/Higgsfield-Video|Mascoot]] Prompts (for episodes)
```bash
# Generate all [[../../wiki/skills/Higgsfield-Video|Mascoot]] episode prompts
cat [[../../wiki/skills/Higgsfield-Video|Mascoot]]-episodes-01-50.md [[../../wiki/skills/Higgsfield-Video|Mascoot]]-episodes-51-75.md > mascoot_all_episodes.md
```

---

## 🎯 SUCCESS CRITERIA

### [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] Generation Goals
- [ ] 150+ [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] scripts created ✅
- [ ] 50 [[../../wiki/businesses/Bene2Luxe#products|Product]] videos generated (Kling 3.0)
- [ ] 25 [[../../wiki/skills/Higgsfield-Video|Mascoot]] episodes animated
- [ ] 50+ trending [[../../wiki/concepts/Marketing-Concepts|Content]] videos (free models)

### [[../../wiki/concepts/Marketing-Concepts|Content]] Distribution
- [ ] 40% [[../../wiki/concepts/Ads-Funnel#cta|CTA]] [[../../wiki/concepts/Marketing-Concepts|Content]] (60 scripts)
- [ ] 40% Entertainment [[../../wiki/concepts/Marketing-Concepts|Content]] (60 scripts)
- [ ] 20% Trends [[../../wiki/concepts/Marketing-Concepts|Content]] (40 scripts)

### Platform Readiness
- [ ] All videos vertical format (9:16)
- [ ] Duration 15-20 seconds
- [ ] Text overlays ready
- [ ] Music ready (Artlist.io)

---

## 📞 SUPPORT

For questions:
- [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]: Contact the team
- Check: `[[../../wiki/HOME|Docs]]/2026-03-26/[[../../wiki/concepts/Marketing-Concepts|Content]]-strategy-[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]].md`
- Check: `[[../../wiki/HOME|Docs]]/[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]-[[../../wiki/concepts/Marketing-Concepts|Content]]/`

---

*Generated by [[../../wiki/people/Elia|Elia]] - 26 Mars 2026*  
*[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] [[../../wiki/concepts/Marketing-Concepts|Content]] Generation System*
