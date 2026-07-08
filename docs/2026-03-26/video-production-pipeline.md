# 🎬 Video Production Pipeline
## Bene2Luxe Content Creation Workflow

**Created**: 26 Mars 2026
**Purpose**: Complete pipeline from script to published video

---

## 📋 PIPELINE OVERVIEW

```
SCRIPT → IMAGE → VIDEO → EDIT → TEXT → MUSIC → EXPORT → PUBLISH
   1        2        3        4       5       6        7         8
```

---

## STAGE 1: SCRIPT SELECTION

### Choose Script
```bash
# Navigate to scripts
cd docs/2026-03-26/content/

# Choose category
cat cta/cta-scripts-51-110.md      # Direct sales
cat entertainment/entertainment-*.md # Lifestyle
cat trends/trends-scripts-*.md       # Trending
```

### Script Format
```
🎣 HOOK (0-4s): [Attention grabber]
💎 VALUE (4-12s): [Content/education]
📞 CTA (12-20s): [Call to action]
```

### Selection Criteria
- Match current trends
- Product availability
- Target audience
- Content variety

---

## STAGE 2: IMAGE GENERATION

### Generate Product Image
```bash
# Using Nano Banano Pro
SCRIPT="/Users/vakandi/EliaAI/docs/2026-03-26/higgfields-scripts/higgfields_master.py"

python3 "$SCRIPT" \
    image \
    --prompt "Chanel La Pause sneakers grey suede green sole luxury product photography" \
    --model nano-banano \
    --aspect 9:16 \
    --style luxury_product
```

### Output
- Location: `./generated/`
- Format: PNG, 4K
- Resolution: 9:16 (vertical)

---

## STAGE 3: VIDEO GENERATION

### Generate from Image
```bash
python3 "$SCRIPT" \
    video \
    --image ./generated/product_image.png \
    --model kling-3 \
    --duration 10 \
    --prompt "Luxury sneakers rotating slowly, soft studio lighting, fashion commercial style"
```

### Generate from Prompt (Mascoot)
```bash
python3 "$SCRIPT" \
    mascott \
    --episode 1 \
    --model kling-3
```

### Output
- Location: `./generated/`
- Format: MP4, H.264
- Duration: 10-15 seconds
- Resolution: 1080x1920 (9:16)

---

## STAGE 4: POST-PRODUCTION EDIT

### Tools Recommended
| Tool | Purpose | Free |
|------|---------|------|
| CapCut | Mobile editing | ✅ |
| DaVinci Resolve | Professional | ✅ |
| Premiere Pro | Advanced | ❌ |
| Final Cut | Mac only | ❌ |

### Edit Checklist
- [ ] Trim to 15-20 seconds
- [ ] Add text overlays (Hook, Value, CTA)
- [ ] Adjust colors (optional)
- [ ] Add transitions (minimal)
- [ ] Review pacing

---

## STAGE 5: TEXT OVERLAYS

### Overlay Text Guide

#### Hook (0-4s)
- Large, bold text
- White or contrasting color
- 2-3 words max
- Example: "€170 for CHANEL??"

#### Value (4-12s)
- Smaller text
- Key selling points
- Example: "Grey Suede • Green Sole"

#### CTA (12-20s)
- Clear action
- Include @bene2luxe
- Example: "WA 06XXXXXXXX"

### Text Placement
```
[TOP]      - Hook/Title
[MIDDLE]   - Key details
[BOTTOM]   - CTA + @bene2luxe
```

---

## STAGE 6: MUSIC SELECTION

### Music Sources
| Source | URL | Use |
|--------|-----|-----|
| Artlist.io | artlist.io | Primary (paid) |
| Epidemic Sound | epidemicsound.com | Alternative |
| YouTube Audio Library | youtube.com | Free |
| Pixabay Music | pixabay.com/music | Free |

### Music Guidelines
- Length: 15-30 seconds (loop if needed)
- Genre: Match content mood
  - CTA: Upbeat, confident
  - Lifestyle: Chill, European
  - Trending: Match viral sounds
- Volume: Music should not overpower voice

### Trending Sounds (March 2026)
- French rap beats
- Chill lo-fi
- Mediterranean vibes
- Café jazz

---

## STAGE 7: EXPORT SETTINGS

### Video Specifications

| Platform | Resolution | FPS | Bitrate | Format |
|----------|------------|-----|---------|--------|
| TikTok | 1080x1920 | 30 | 8 Mbps | MP4 |
| Snapchat | 1080x1920 | 30 | 6 Mbps | MP4 |
| Instagram Reels | 1080x1920 | 30 | 8 Mbps | MP4 |
| WhatsApp Status | 1080x1920 | 30 | 4 Mbps | MP4 |

### Export Preset (CapCut)
```
Resolution: 1080x1920
Frame Rate: 30fps
Format: MP4
Quality: High
Codec: H.264
```

---

## STAGE 8: PUBLISHING

### Platform Schedule

| Platform | Post Time | Day | Priority |
|----------|-----------|-----|----------|
| Snapchat | 9:00 | Daily | HIGH |
| TikTok | 12:00 | Mon/Wed/Fri | HIGH |
| Instagram | 18:00 | Tue/Thu/Sat | MEDIUM |
| WhatsApp Status | 20:00 | Daily | HIGH |

### Publishing Checklist
- [ ] Add location tag (France/Switzerland)
- [ ] Add relevant hashtags
- [ ] Tag @bene2luxe
- [ ] Write engaging caption
- [ ] Add CTA in comments
- [ ] Share to WhatsApp groups

### Hashtag Strategy
```
#Bene2Luxe #LuxuryFashion #FrenchStyle
#ChanelSneakers #DiorSunglasses #LVPurses
#ParisStyle #SwissLuxury #ModeFrancaise
#LuxuryResale #SecondeMain #VintedAlternative
#TikTokFashion #SnapchatStyle #ReelsTrend
```

---

## 🚀 QUICK WORKFLOW

### 1. Select Script
```bash
# Pick from content folder
vim docs/2026-03-26/content/cta/cta-scripts-51-110.md
```

### 2. Generate Image (5 min)
```bash
python3 higgfields_master.py image --prompt "SCRIPT HOOK TEXT" --model nano-banano
```

### 3. Generate Video (10 min)
```bash
python3 higgfields_master.py video --image output.png --model kling-3 --duration 10
```

### 4. Edit in CapCut (10 min)
- Add text overlays
- Add music
- Trim to 15-20s

### 5. Export & Publish (5 min)
- Export as MP4
- Upload to platforms
- Share to WhatsApp

**Total Time: ~30 minutes per video**

---

## 📊 PRODUCTION METRICS

### Weekly Capacity
| Task | Time | Videos/Week |
|------|------|-------------|
| Generation | 15 min/video | 40 videos |
| Editing | 15 min/video | 40 videos |
| Publishing | 5 min/video | 40 videos |
| **Total** | **35 min/video** | **~30 videos** |

### Recommended Daily Output
- **Minimum**: 3 videos/day
- **Target**: 5 videos/day
- **Maximum**: 8 videos/day

---

## 🔧 TROUBLESHOOTING

### Video Generation Issues
| Problem | Solution |
|---------|----------|
| Timeout | Use shorter duration (5s) |
| Low quality | Use kling-3 instead of wan-2 |
| Failed generation | Retry or use different prompt |

### Editing Issues
| Problem | Solution |
|---------|----------|
| Text not visible | Add outline/shadow |
| Music too loud | Lower music volume to 30% |
| Video too long | Trim in CapCut |

### Publishing Issues
| Problem | Solution |
|---------|----------|
| Platform rejected | Check video format/size |
| Low reach | Post at optimal times |
| Copyright | Use royalty-free music only |

---

*Pipeline v1.0 - 26 Mars 2026*
