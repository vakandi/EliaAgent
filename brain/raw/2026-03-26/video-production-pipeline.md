# 🎬 [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] Production Pipeline
## [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] [[../../wiki/concepts/Marketing-Concepts|Content]] Creation [[../../wiki/concepts/AI-Automation|Workflow]]

**Created**: 26 Mars 2026
**Purpose**: [[../../wiki/docs/Sessions|Complete]] pipeline from script to published [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]

---

## 📋 PIPELINE OVERVIEW

```
SCRIPT → IMAGE → [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] → [[../../wiki/concepts/File-Management|Edit]] → TEXT → MUSIC → EXPORT → PUBLISH
   1        2        3        4       5       6        7         8
```

---

## STAGE 1: SCRIPT SELECTION

### Choose Script
```bash
# Navigate to scripts
cd [[../../wiki/HOME|Docs]]/2026-03-26/[[../../wiki/concepts/Marketing-Concepts|Content]]/

# Choose category
cat [[../../wiki/concepts/Ads-Funnel#cta|CTA]]/[[../../wiki/concepts/Ads-Funnel#cta|CTA]]-scripts-51-110.md      # Direct [[../../wiki/businesses/Bene2Luxe#revenue|Sales]]
cat entertainment/entertainment-*.md # Lifestyle
cat trends/trends-scripts-*.md       # Trending
```

### Script Format
```
🎣 [[../../wiki/concepts/Ads-Funnel#hook|Hook]] (0-4s): [Attention grabber]
💎 [[../../wiki/concepts/Pricing|Value]] (4-12s): [[[../../wiki/concepts/Marketing-Concepts|Content]]/education]
📞 [[../../wiki/concepts/Ads-Funnel#cta|CTA]] (12-20s): [Call to action]
```

### Selection Criteria
- Match current trends
- [[../../wiki/businesses/Bene2Luxe#products|Product]] availability
- [[../../wiki/concepts/Ads-Funnel#targeting|Target]] audience
- [[../../wiki/concepts/Marketing-Concepts|Content]] variety

---

## STAGE 2: IMAGE GENERATION

### Generate [[../../wiki/businesses/Bene2Luxe#products|Product]] Image
```bash
# Using Nano Banano Pro
SCRIPT="/Users/vakandi/[[../../wiki/people/Elia|Elia]]/[[../../wiki/HOME|Docs]]/2026-03-26/higgfields-scripts/higgfields_master.py"

python3 "$SCRIPT" \
    image \
    --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "[[../../wiki/concepts/Luxury-Brands#chanel|Chanel]] La Pause sneakers grey suede green sole luxury [[../../wiki/businesses/Bene2Luxe#products|Product]] photography" \
    --model nano-banano \
    --aspect 9:16 \
    --style luxury_product
```

### Output
- Location: `./generated/`
- Format: PNG, 4K
- Resolution: 9:16 (vertical)

---

## STAGE 3: [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] GENERATION

### Generate from Image
```bash
python3 "$SCRIPT" \
    [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] \
    --image ./generated/product_image.png \
    --model kling-3 \
    --duration 10 \
    --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "Luxury sneakers rotating slowly, soft studio lighting, [[../../wiki/concepts/Luxury-Brands|Fashion]] commercial style"
```

### Generate from [[../../wiki/concepts/Prompt-Engineering|PROMPT]] ([[../../wiki/skills/Higgsfield-Video|Mascoot]])
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

## STAGE 4: POST-PRODUCTION [[../../wiki/concepts/File-Management|Edit]]

### [[../../wiki/tools/Index|TOOLS]] Recommended
| Tool | Purpose | Free |
|------|---------|------|
| CapCut | Mobile editing | ✅ |
| DaVinci Resolve | Professional | ✅ |
| Premiere Pro | Advanced | ❌ |
| Final Cut | Mac only | ❌ |

### [[../../wiki/concepts/File-Management|Edit]] Checklist
- [ ] Trim to 15-20 seconds
- [ ] Add text overlays ([[../../wiki/concepts/Ads-Funnel#hook|Hook]], [[../../wiki/concepts/Pricing|Value]], [[../../wiki/concepts/Ads-Funnel#cta|CTA]])
- [ ] Adjust colors (optional)
- [ ] Add transitions (minimal)
- [ ] Review pacing

---

## STAGE 5: TEXT OVERLAYS

### Overlay Text Guide

#### [[../../wiki/concepts/Ads-Funnel#hook|Hook]] (0-4s)
- Large, bold text
- White or contrasting color
- 2-3 words max
- Example: "€170 for [[../../wiki/concepts/Luxury-Brands#chanel|Chanel]]??"

#### [[../../wiki/concepts/Pricing|Value]] (4-12s)
- Smaller text
- Key selling points
- Example: "Grey Suede • Green Sole"

#### [[../../wiki/concepts/Ads-Funnel#cta|CTA]] (12-20s)
- Clear action
- Include @[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]
- Example: "WA 06XXXXXXXX"

### Text Placement
```
[TOP]      - [[../../wiki/concepts/Ads-Funnel#hook|Hook]]/Title
[MIDDLE]   - Key details
[BOTTOM]   - [[../../wiki/concepts/Ads-Funnel#cta|CTA]] + @[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]
```

---

## STAGE 6: MUSIC SELECTION

### Music Sources
| Source | [[../../wiki/concepts/API-Integration|URL]] | Use |
|--------|-----|-----|
| Artlist.io | artlist.io | Primary (paid) |
| Epidemic Sound | epidemicsound.com | Alternative |
| YouTube Audio [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Python-Scripting|Python]]-Scripting|Library]] | youtube.com | Free |
| Pixabay Music | pixabay.com/music | Free |

### Music Guidelines
- Length: 15-30 seconds (loop if needed)
- Genre: Match [[../../wiki/concepts/Marketing-Concepts|Content]] mood
  - [[../../wiki/concepts/Ads-Funnel#cta|CTA]]: Upbeat, confident
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

### [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] Specifications

| Platform | Resolution | FPS | Bitrate | Format |
|----------|------------|-----|---------|--------|
| [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]] | 1080x1920 | 30 | 8 Mbps | MP4 |
| [[../../wiki/channels/Snapchat|Snapchat]] | 1080x1920 | 30 | 6 Mbps | MP4 |
| Instagram Reels | 1080x1920 | 30 | 8 Mbps | MP4 |
| [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] Status | 1080x1920 | 30 | 4 Mbps | MP4 |

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

| Platform | Post [[../../wiki/topics/Infrastructure-Timeline|Time]] | Day | Priority |
|----------|-----------|-----|----------|
| [[../../wiki/channels/Snapchat|Snapchat]] | 9:00 | Daily | HIGH |
| [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]] | 12:00 | Mon/Wed/Fri | HIGH |
| Instagram | 18:00 | Tue/Thu/Sat | MEDIUM |
| [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] Status | 20:00 | Daily | HIGH |

### Publishing Checklist
- [ ] Add location tag (France/[[../../wiki/concepts/Location-Targeting#switzerland|Switzerland]])
- [ ] Add relevant hashtags
- [ ] Tag @[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]
- [ ] Write engaging caption
- [ ] Add [[../../wiki/concepts/Ads-Funnel#cta|CTA]] in comments
- [ ] Share to [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]] groups

### Hashtag Strategy
```
#[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] #LuxuryFashion #FrenchStyle
#ChanelSneakers #DiorSunglasses #LVPurses
#ParisStyle #SwissLuxury #ModeFrancaise
#LuxuryResale #SecondeMain #VintedAlternative
#TikTokFashion #SnapchatStyle #ReelsTrend
```

---

## 🚀 QUICK [[../../wiki/concepts/AI-Automation|Workflow]]

### 1. Select Script
```bash
# Pick from [[../../wiki/concepts/Marketing-Concepts|Content]] folder
vim [[../../wiki/HOME|Docs]]/2026-03-26/[[../../wiki/concepts/Marketing-Concepts|Content]]/[[../../wiki/concepts/Ads-Funnel#cta|CTA]]/[[../../wiki/concepts/Ads-Funnel#cta|CTA]]-scripts-51-110.md
```

### 2. Generate Image (5 min)
```bash
python3 higgfields_master.py image --[[../../wiki/concepts/Prompt-Engineering|PROMPT]] "SCRIPT [[../../wiki/concepts/Ads-Funnel#hook|Hook]] TEXT" --model nano-banano
```

### 3. Generate [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] (10 min)
```bash
python3 higgfields_master.py [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] --image output.png --model kling-3 --duration 10
```

### 4. [[../../wiki/concepts/File-Management|Edit]] in CapCut (10 min)
- Add text overlays
- Add music
- Trim to 15-20s

### 5. Export & Publish (5 min)
- Export as MP4
- Upload to platforms
- Share to [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]

**Total [[../../wiki/topics/Infrastructure-Timeline|Time]]: ~30 minutes per [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]**

---

## 📊 PRODUCTION METRICS

### Weekly Capacity
| [[../../wiki/concepts/AI-Automation#tasks|Task]] | [[../../wiki/topics/Infrastructure-Timeline|Time]] | Videos/Week |
|------|------|-------------|
| Generation | 15 min/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] | 40 videos |
| Editing | 15 min/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] | 40 videos |
| Publishing | 5 min/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] | 40 videos |
| **Total** | **35 min/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]]** | **~30 videos** |

### Recommended Daily Output
- **Minimum**: 3 videos/day
- **[[../../wiki/concepts/Ads-Funnel#targeting|Target]]**: 5 videos/day
- **Maximum**: 8 videos/day

---

## 🔧 TROUBLESHOOTING

### [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] Generation [[../../wiki/systems/Jira-Tickets-Index|Issues]]
| Problem | Solution |
|---------|----------|
| Timeout | Use shorter duration (5s) |
| Low quality | Use kling-3 instead of wan-2 |
| Failed generation | Retry or use different [[../../wiki/concepts/Prompt-Engineering|PROMPT]] |

### Editing [[../../wiki/systems/Jira-Tickets-Index|Issues]]
| Problem | Solution |
|---------|----------|
| Text not visible | Add outline/shadow |
| Music too loud | Lower music volume to 30% |
| [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] too long | Trim in CapCut |

### Publishing [[../../wiki/systems/Jira-Tickets-Index|Issues]]
| Problem | Solution |
|---------|----------|
| Platform rejected | Check [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Higgsfield-Video|Video]] format/[[../../wiki/businesses/Bene2Luxe#sizing|Size]] |
| Low reach | Post at optimal times |
| Copyright | Use royalty-free music only |

---

*Pipeline v1.0 - 26 Mars 2026*
