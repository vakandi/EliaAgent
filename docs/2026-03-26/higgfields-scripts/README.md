# 🎬 Bene2Luxe × Higgfields - Complete Video Generation System

**Date**: 26 Mars 2026  
**Purpose**: Generate 150 video scripts + automation scripts for Bene2Luxe content

---

## 📋 TABLE OF CONTENTS

1. [Quick Start](#-quick-start)
2. [Script Organization](#-script-organization)
3. [Video Generation Scripts](#-video-generation-scripts)
4. [Content Scripts (150)](#-content-scripts-150)
5. [Mascoot Mini-TV Show](#-mascoot-mini-tv-show)
6. [Generation Workflow](#-generation-workflow)
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

### Generate Video
```bash
# Single video from image
python3 higgfields_master.py video --image product.png --model kling-3

# Single video from prompt
python3 higgfields_master.py video --prompt "Luxury sneakers rotating on white background" --model kling-3

# Batch generate 50 videos
python3 higgfields_master.py batch --type product --count 50 --model kling-3

# Mascoot episode
python3 higgfields_master.py mascott --episode 1 --model kling-3
```

---

## 📁 SCRIPT ORGANIZATION

```
docs/2026-03-26/higgfields-scripts/
├── higgfields_master.py          # Master script (all models)
├── kling-3.0/
│   └── kling_scripts.py          # Kling 3.0 specific scripts
├── nano-banano-pro/
│   └── nano_banano_scripts.py    # Nano Banano specific scripts
└── free-models/
    └── free_models.py            # Free model scripts (Wan, Minimax)

docs/2026-03-26/content/
├── cta/
│   └── cta-scripts-51-110.md     # 60 CTA scripts
├── entertainment/
│   └── entertainment-scripts-111-170.md  # 60 entertainment scripts
└── trends/
    └── trends-scripts-171-200.md # 40 trend scripts

docs/2026-03-26/mascott-show/
├── mascott-episodes-01-50.md     # Mascoot episodes 1-50
└── mascott-episodes-51-75.md     # Mascoot episodes 51-75
```

---

## 🎬 VIDEO GENERATION SCRIPTS

### 1. Higgfields Master (higgfields_master.py)

**Purpose**: Unified script for all models via Higgfields platform

**Models**:
| Model | Type | Credits | Use Case |
|-------|------|---------|----------|
| `nano-banano` | Image | 1 | Product images (4K fast) |
| `flux-pro` | Image | 2 | Best quality images |
| `flux-dev` | Image | FREE | Testing/previews |
| `kling-3` | Video | 3 | Primary video generation |
| `kling-standard` | Video | 2 | Faster video |
| `wan-2` | Video | FREE | Free video tier |
| `minimax` | Video | FREE | Free video tier |

**Usage**:
```bash
# Image generation
python3 higgfields_master.py image --prompt "Chanel sneakers luxury" --model nano-banano

# Video from image
python3 higgfields_master.py video --image product.png --model kling-3 --duration 10

# Video from prompt
python3 higgfields_master.py video --prompt "Animated mascott in Paris" --model kling-3

# Batch generation
python3 higgfields_master.py batch --type product --count 50 --model kling-3

# Mascoot episode
python3 higgfields_master.py mascott --episode 1

# List models
python3 higgfields_master.py models
```

---

### 2. Kling 3.0 Scripts (kling_scripts.py)

**Purpose**: Direct Kling API integration (when available)

**Models**:
- `kling-v3` - Latest Kling 3.0
- `kling-v2.6-pro` - Professional quality
- `kling-v2.6-std` - Standard quality
- `kling-v2.5-turbo` - Fastest

**Usage**:
```bash
# Text-to-video
python3 kling_scripts.py t2v --prompt "Luxury sneakers rotating" --duration 5

# Image-to-video
python3 kling_scripts.py i2v --image product.png --prompt "Sneaker slowly turning"

# Batch from file
python3 kling_scripts.py batch --file prompts.txt --count 50

# Category-specific
python3 kling_scripts.py category --category chanel_sneakers --count 5

# List prompts
python3 kling_scripts.py prompts
```

---

### 3. Nano Banano Scripts (nano_banano_scripts.py)

**Purpose**: Image + video generation via Nano Banano

**Usage**:
```bash
# Generate image
python3 nano_banano_scripts.py image --prompt "Chanel sneakers on marble"

# Generate video
python3 nano_banano_scripts.py video --image product.png

# Batch images
python3 nano_banano_scripts.py batch --file prompts.txt --type image

# List available prompts
python3 nano_banano_scripts.py prompts
```

---

### 4. Free Models (free_models.py)

**Purpose**: Unlimited free-tier generation

**Models**:
- `flux-dev/text-to-image` - Free image
- `wan/wan-video/video-generation` - Free video
- `minimax/haibo/video-generation` - Free video

**Usage**:
```bash
# Free image
python3 free_models.py image --prompt "Fashion content"

# Free video
python3 free_models.py video --image photo.png

# Batch free
python3 free_models.py batch --file prompts.txt --type video
```

---

## 📝 CONTENT SCRIPTS (150)

### Distribution

| Category | Percentage | Count | File |
|----------|-----------|-------|------|
| **CTA** (Direct Sales) | 40% | 60 | `content/cta/cta-scripts-51-110.md` |
| **Entertainment** (Lifestyle/Humor) | 40% | 60 | `content/entertainment/entertainment-scripts-111-170.md` |
| **Trends** (Viral/Social) | 20% | 40 | `content/trends/trends-scripts-171-200.md` |
| **TOTAL** | 100% | 160 | |

### Script Format (Alex Hormozi 20/40/40)

```
🎣 HOOK (0-4s): Grab attention
💎 VALUE (4-12s): Educate or entertain
📞 CTA (12-20s): Call to action
```

### CTA Scripts Examples
- Direct product showcases
- Limited stock urgency
- WhatsApp ordering process
- Price comparison value

### Entertainment Scripts Examples
- French humor (Le French Dream)
- TV show tie-ins (Les Traîtres, Koh Lanta)
- Lifestyle content (GRWM, OOTD)
- Storytime formats

### Trends Scripts Examples
- Trending challenges (#SixSeven)
- TikTok format participation
- Fashion Week reactions
- Viral content formats

---

## 🎭 MASCOOT MINI-TV SHOW

### Concept
A luxury mascoot character arrives in France/Switzerland and has adventures discovering luxury fashion and French culture.

### Episodes Structure

| Season | Episodes | Location | Theme |
|--------|----------|----------|-------|
| Season 1 | 1-25 | Paris | Discovery |
| Season 2 | 26-50 | Switzerland | Alpine luxury |
| Season 3 | 51-75 | Côte d'Azur | Mediterranean |
| Season 4 | 76-100 | Shopping | Collection |

### Episode Format
```
🎬 EPISODE [#]: "[TITLE]"
📍 Location: [LOCATION]
⏱️ Duration: 15-20 seconds

🎣 HOOK (0-3s): Attention grabber
🎭 ADVENTURE (3-12s): Mascoot's journey
📞 CTA (12-20s): Bene2Luxe mention
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

## 🔄 GENERATION WORKFLOW

### Phase 1: Product Images
```bash
# Generate product images (Nano Banano Pro - 4K)
python3 nano_banano_scripts.py category --category chanel_la_pause --count 3
python3 nano_banano_scripts.py category --category dior_b23 --count 3
python3 nano_banano_scripts.py category --category dior_sunglasses --count 3
python3 nano_banano_scripts.py category --category louis_vuitton --count 3
python3 nano_banano_scripts.py category --category gucci --count 3
python3 nano_banano_scripts.py category --category caps --count 3
```

### Phase 2: Product Videos
```bash
# Generate product videos (Kling 3.0 - primary)
python3 kling_scripts.py batch --file product_prompts.txt --count 50 --model kling-3

# Fallback to free models if credits low
python3 free_models.py batch --file product_prompts.txt --count 50 --type video
```

### Phase 3: Mascoot Content
```bash
# Generate mascoot episodes (Kling 3.0 - 15s)
python3 higgfields_master.py mascott --episode 1
# Repeat for episodes 2-75
```

### Phase 4: Lifestyle/Trends
```bash
# Generate trending content (Free models - unlimited)
python3 free_models.py batch --file trending_prompts.txt --count 50 --type video
```

---

## 💳 MODELS & CREDITS

### Available Credits (~200 total)

| Model | Credits | Primary Use |
|-------|---------|-------------|
| Nano Banano Pro | ~600 | Product images |
| Kling 3.0 | ~200 | Primary videos |
| Flux Dev | ∞ (free) | Testing |
| Wan 2.2 | ∞ (free) | Backup videos |
| Minimax | ∞ (free) | Backup videos |

### Recommended Usage

| Content Type | Model | Priority |
|-------------|-------|----------|
| Product showcases | Kling 3.0 | HIGH |
| Mascoot adventures | Kling 3.0 | HIGH |
| Trending content | Wan 2.2 | MEDIUM |
| Testing/previews | Flux Dev | FREE |
| Product images | Nano Banano Pro | HIGH |

---

## 📊 BATCH PROMPTS FILES

### Product Prompts (for videos)
Located in: `docs/2026-03-26/higgfields-scripts/batch-prompts/`

| File | Content | Count |
|------|---------|-------|
| `chanel-prompt.txt` | Chanel La Pause prompts | 10 |
| `dior-prompt.txt` | Dior B23 & sunglasses prompts | 10 |
| `lv-prompt.txt` | Louis Vuitton prompts | 10 |
| `gucci-prompt.txt` | Gucci prompts | 10 |
| `lifestyle-prompt.txt` | Lifestyle prompts | 10 |

### Mascoot Prompts (for episodes)
```bash
# Generate all mascoot episode prompts
cat mascoot-episodes-01-50.md mascoot-episodes-51-75.md > mascoot_all_episodes.md
```

---

## 🎯 SUCCESS CRITERIA

### Video Generation Goals
- [ ] 150+ video scripts created ✅
- [ ] 50 product videos generated (Kling 3.0)
- [ ] 25 mascoot episodes animated
- [ ] 50+ trending content videos (free models)

### Content Distribution
- [ ] 40% CTA content (60 scripts)
- [ ] 40% Entertainment content (60 scripts)
- [ ] 20% Trends content (40 scripts)

### Platform Readiness
- [ ] All videos vertical format (9:16)
- [ ] Duration 15-20 seconds
- [ ] Text overlays ready
- [ ] Music ready (Artlist.io)

---

## 📞 SUPPORT

For questions:
- WhatsApp: Contact the team
- Check: `docs/2026-03-26/content-strategy-bene2luxe.md`
- Check: `docs/bene2luxe-content/`

---

*Generated by Elia - 26 Mars 2026*  
*Bene2Luxe Content Generation System*
