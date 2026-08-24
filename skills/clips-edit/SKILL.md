---
name: clips-edit
description: >
  Multi-style competitor clip editor for your-saas social content. Transforms raw competitor
  videos into branded, high-conversion vertical clips for Reels/TikTok/Stories. Includes 5
  production-tested styles: (1) Text Overlay on raw clip, (2) Split Vertical with static
  image bottom, (3) Split Vertical with GSAP animated bottom video, (4) Full-screen branded
  overlay with hook text, (5) Side-by-side comparison clip. Use this skill whenever editing
  competitor videos, creating branded clips, building split-screen content, adding overlays
  to clips, generating vertical social content from landscape sources, or any request to
  "make a clip from this video", "edit this competitor video", "add branding to a clip",
  "make vertical content", "create Reels from YouTube", "build TikTok clips". Always load
   related skills (heygen-mcp, gsap, best-heygen-video, pricing-secrets, persuasion-genius,
   sales-mastery, marketing-strategy, customer-acquisition)
   for full context on copywriting, animation, and conversion optimization.
---

# Clips Edit — Multi-Style Competitor Clip Pipeline

Transform raw competitor videos into branded, high-conversion vertical clips for social media.

## Loading Required Skills

Before creating any clip, load these skills to inform copywriting, animation, and conversion strategy:

| Skill | Why | When |
|-------|-----|------|
| `heygen-mcp` | All video/audio tools (transcribe, cut, overlay, render, watermark, resize) | Every clip |
| `gsap` | Animation reference for GSAP timelines in HTML compositions | V3 animated bottom, V4 overlays |
| `best-heygen-video` | GSAP + Playwright + FFmpeg render pipeline, asset sourcing | When building custom animated scenes |
| `pricing-secrets` | Hormozi pricing frameworks for CTA copy (value anchoring, price signaling) | Writing CTAs, pricing hooks |
| `persuasion-genius` | Influence techniques for hook text and problem framing | Writing hooks, problem statements |
| `sales-mastery` | Closing techniques for CTA design (urgency, scarcity, speed) | CTA button text, urgency framing |
| `marketing-strategy` | Content repurposing, audience alignment, value density | Selecting which clips to produce, hook strategy |
| `customer-acquisition` | Cold/warm process thinking, response optimization | Platform-specific CTA paths (DM vs link vs bio) |


## Design System (your-saas)

| Token | Value | Usage |
|-------|-------|-------|
| Background | `#0A0A1A` | All backgrounds, padding, separators |
| Problem/Danger | `#EF4444` | Red for pain points, competitor failures |
| Solution/Safe | `#22C55E` | Green for your-saas features, CTAs |
| Accent | `#00FF88` | Brand accent, button fills, highlights |
| Text Primary | `#FFFFFF` | Headlines, main text |
| Text Secondary | `#94A3B8` | Subtitles, descriptions |
| Font — Title | Inter (700) | Scene titles, hooks |
| Font — Body | Inter (400) | Descriptions, features |
| Font — Data | JetBrains Mono (600) | Stats, numbers, code-like elements |

## The 5 Clip Styles

### Style 1 — Text Overlay (Simplest)

**What:** Raw competitor clip with branded hook text overlay on top. Fastest to produce.  
**Best for:** Quick wins, testing which hooks resonate, high-volume posting.  
**Output:** Same resolution as source (typically 640x360 landscape or 1080x1920 vertical).

```
┌──────────────────────┐
│  🔴 HOOK TEXT HERE   │  ← White text, black bg strip, top 15%
│                      │
│   Original competitor│
│   video plays below  │
│                      │
└──────────────────────┘
```

**Pipeline:**
```bash
# 1. Cut clip from source
ffmpeg -y -ss START -to END -i source.mp4 -c:v libx264 -c:a aac -preset fast clip.mp4

# 2. Add text overlay
mcp-cli call heygen-content-mcp add_text_overlay '{
  "video_path": "clip.mp4",
  "text": "Stripe just killed your store. What now?",
  "position": "top",
  "font_size": 24,
  "font_color": "white",
  "bg_color": "black"
}'
```

**Hook writing rules (from persuasion-genius + marketing-strategy):**
- Lead with the pain point, not the solution
- Use specificity: "$90K in 3 days" > "a lot of money"
- Create curiosity gap: "The hidden pattern Stripe doesn't want you to see"
- Match the speaker's energy — calm authority gets calm hooks, outrage gets outrage hooks

---

### Style 2 — Split Vertical with Static Image Bottom (V2)

**What:** Competitor clip on top (1080x608) + branded CTA image on bottom (1080x960).  
**Best for:** Maximum CTA visibility, clean brand presentation, Reels/TikTok/Stories.  
**Output:** 1080x1920 (9:16 vertical).

```
┌──────────────────────────┐
│                          │
│    Original clip         │  1080x608
│    (scaled to width)     │
│                          │
├──────────────────────────┤  ← 48px separator
│   your-saas Branding      │
│   • Multi-gateway        │  1080x960
│   • Real-time failover   │  (static PNG)
│   • Zero downtime        │
│   [Start Free →]         │
└──────────────────────────┘
   Total: 1080x1920
```

**⚠️ ZERO-GAP — Use `vstack`, NEVER overlay positioning.**
```bash
# 1. Get clip height after scaling to 1080 width
CLIP_H_SCALED=$((1080 * $(ffprobe -v quiet -select_streams v:0 -show_entries stream=height -of csv=p=0 clip.mp4) / $(ffprobe -v quiet -select_streams v:0 -show_entries stream=width -of csv=p=0 clip.mp4)))
BOTTOM_H=$((1920 - CLIP_H_SCALED))

# 2. Generate CTA image at 1080xBOTTOM_H via Playwright (NOT Pillow)

# 3. Combine with vstack — zero gaps guaranteed
ffmpeg -y -i clip.mp4 -i cta_image.png \
  -filter_complex "
    [0:v]scale=1080:-2[clip];
    [1:v]scale=1080:${BOTTOM_H}[cta];
    [clip][cta]vstack=inputs=2[out]
  " \
  -map "[out]" -map "0:a?" \
  -c:v libx264 -c:a aac -preset fast -shortest \
  output_v2.mp4

# 4. Add hook text at top
mcp-cli call heygen-content-mcp add_text_overlay '{
  "video_path": "output_v2.mp4",
  "text": "Hook text here",
  "position": "top",
  "font_size": 24
}'
```

**CTA image design (from pricing-secrets):**
- Lead with value, not features: "Never Lose Your Stripe Account" > "Multi-Gateway Routing"
- One clear CTA: "Start Free → your-saas.com"
- Use price anchoring if applicable: "Free while your competitor pays 2.9% + $30/mo in reserves"
- Green (#00FF88) button on dark (#0A0A1A) background — high contrast, can't miss

---

### Style 3 — Split Vertical with Animated GSAP Bottom (V3) ⭐ PREFERRED

**What:** Competitor clip on top (1080x608) + 5-scene GSAP animated video on bottom (1080x960).  
**Best for:** Highest engagement, story-driven conversion, premium feel.  
**Output:** 1080x1920 (9:16 vertical).

```
┌──────────────────────────┐
│                          │
│    Original clip         │  1080x608
│    (speaker talks)       │
│                          │
├──────────────────────────┤
│  Scene 1: PROBLEM        │  1080x960
│  (red, animated stats)   │  GSAP timeline
│  Scene 2: SOLUTION       │  synced to clip
│  (green, features)       │  duration
│  Scene 3: GATEWAY SWITCH │
│  Scene 4: BEFORE/AFTER   │
│  Scene 5: CTA            │
└──────────────────────────┘
```

**⚠️ ZERO-GAP FORMULA — Always calculate dynamically:**
```bash
# 1. Get clip height after scaling to 1080 width
CLIP_H=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=height -of csv=p=0 clip.mp4)
# Scale: CLIP_H_SCALED = 1080 * CLIP_H / CLIP_WIDTH
# 2. Bottom = 1920 - CLIP_H_SCALED (render bottom animation at 1080 x BOTTOM_H)
# 3. Use vstack, NOT overlay:
ffmpeg -y -i clip.mp4 -i bottom.mp4 \
  -filter_complex "[0:v]scale=1080:-2[clip];[1:v]scale=1080:BOTTOM_H[bot];[clip][bot]vstack=inputs=2[out]" \
  -map "[out]" -map "0:a?" -c:v libx264 -c:a aac -preset fast -shortest output.mp4
```
**NEVER use overlay positioning for split clips — it creates black gaps. Use `vstack`.**

**Pipeline (automated via generate_v3_clips.py):**
```bash
# One command — handles everything
python3 generate_v3_clips.py --all
# Or specific clips
python3 generate_v3_clips.py --clip-numbers 1,2,3
```

**What the script does internally:**
1. Finds clip file (handles descriptive names like `clip_01_bench_collapse.mp4`)
2. Gets clip dimensions → calculates BOTTOM_H = 1920 - scaled_clip_height
3. Generates per-clip HTML with custom text from `CLIP_THEMES` dict
4. Renders bottom animation via `render_custom.py` at 1080xBOTTOM_H (Playwright + GSAP)
5. Combines via ffmpeg `vstack` (NO overlay — zero gaps guaranteed)

**GSAP timeline structure (adaptive to clip duration):**

| Scene | % of Duration | Animation |
|-------|---------------|-----------|
| 1 — Problem | 0-20% | Red title slides in, stat counters animate (0→value) |
| 2 — Solution | 20-45% | Green title fades in, 4 feature cards stagger from bottom |
| 3 — Gateway Switch | 45-70% | Red card shrinks left, green card grows right |
| 4 — Before/After | 70-85% | Side-by-side comparison panels |
| 5 — CTA | 85-100% | Button pulse animation, "Start Free" text |

**CLIP_THEMES structure (per clip):**
```python
{
    "problem_title": "Stripe Account<br><span class='red'>Frozen Overnight</span>",
    "problem_subtitle": "Your payment processor just shut you down.",
    "stat1_val": "$0", "stat1_label": "Revenue",
    "stat2_val": "0%", "stat2_label": "Uptime",
    "stat3_val": "48h", "stat3_label": "Recovery",
    "solution_title": "<span class='green'>your-saas</span> Prevents This",
    "features": [
        ("🔄", "Auto Rotation", "Switches gateways instantly"),
        ("⚡", "Failover Routing", "Zero revenue loss"),
        ("🌍", "Multi-Region", "Payments always flow"),
        ("🔒", "Revenue Shield", "Protected 24/7"),
    ],
    "cta_text": "Start Free →",
}
```

**Technical requirements:**
- GSAP: `file://~/mcps_server/heygen-content-mcp/HeyGen/gsap.min.js` (absolute path)
- Renderer: `render_custom.py` captures at 30fps, outputs 2160x1920 (device_scale_factor=2)
- Must export: `window.__timelines = { main: master }`
- Timeout: 900s per clip (longer clips need more render time)
- Downscale filter: ffmpeg `-vf "scale=1080:1920"` during combine step

---

### Style 4 — Full-Screen Branded Overlay (Hook + CTA)

**What:** Raw clip fills entire vertical frame with branded hook text at top and CTA bar at bottom.  
**Best for:** Maximum video real estate, mobile-first, when the speaker's visual is compelling.  
**Output:** 1080x1920 (9:16 vertical).

```
┌──────────────────────────┐
│  ╔════════════════════╗  │
│  ║ 🔴 HOOK TEXT HERE  ║  │  ← Semi-transparent black bar
│  ╚════════════════════╝  │
│                          │
│                          │
│   Original clip fills    │
│   entire frame           │
│                          │
│                          │
│  ╔════════════════════╗  │
│  ║ your-saas · Start   ║  │  ← Green CTA bar
│  ║ Free →             ║  │
│  ╚════════════════════╝  │
└──────────────────────────┘
```

**Pipeline:**
```bash
# 1. Scale clip to fill 1080x1920 (crop top/bottom if needed)
ffmpeg -y -i clip.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
  -c:v libx264 -c:a aac -preset fast \
  clip_filled.mp4

# 2. Render hook bar (1080x120) + CTA bar (1080x120) via Playwright HTML/CSS
# (ffmpeg drawtext NOT available on this system — always use Playwright)

# 3. Overlay bars on filled clip
ffmpeg -y -i clip_filled.mp4 -i hook_bar.png -i cta_bar.png \
  -filter_complex "
    [1:v]scale=1080:120[hook];
    [2:v]scale=1080:120[cta];
    [0:v][hook]overlay=0:0[top];
    [top][cta]overlay=0:1800
  " \
  -c:v libx264 -c:a aac -preset fast \
  output_v4.mp4
```

**When to use vs Style 2/3:**
- Use when the speaker's facial expressions/body language are compelling (don't hide them)
- Use for shorter clips (<20s) where the story is visual
- Don't use for data-heavy clips (those benefit from animated stats in Style 3)

---

### Style 5 — Side-by-Side Comparison (Before/After)

**What:** Split screen showing "competitor way" vs "your-saas way" with branded divider.  
**Best for:** Direct comparison content, "what if" scenarios, showing the alternative.  
**Output:** 1080x1920 (9:16 vertical) or 1080x1080 (square for feed).

```
┌──────────────────────────┐
│    ❌ THE OLD WAY        │  ← Red label
├────────────┬─────────────┤
│            │             │
│ Competitor │  your-saas   │
│ clip       │  clip/anim  │
│ (problem)  │  (solution) │
│            │             │
├────────────┴─────────────┤
│    ✅ THE MIRRORPAY WAY  │  ← Green label
│    Start Free →          │
└──────────────────────────┘
```

**Pipeline:**
```bash
# 1. Prepare left clip (competitor problem moment)
ffmpeg -y -i competitor_clip.mp4 \
  -vf "scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2:color=#0A0A1A" \
  -c:v libx264 -preset fast left.mp4

# 2. Prepare right clip (your-saas solution — could be animation or screen recording)
ffmpeg -y -i your-saas_clip.mp4 \
  -vf "scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2:color=#0A0A1A" \
  -c:v libx264 -preset fast right.mp4

# 3. Combine side-by-side with divider
ffmpeg -y -i left.mp4 -i right.mp4 \
  -filter_complex "
    [0:v]pad=544:960:0:0:black[left];
    [1:v]pad=544:960:4:0:black[right];
    [left][right]hstack=inputs=2[split];
    color=#0A0A1A:s=1080x80:d=DURATION[label_top];
    color=#0A0A1A:s=1080x80:d=DURATION[label_bot];
    [label_top][split][label_bot]vstack=inputs=3[out]
  " \
  -map "[out]" -map "0:a?" \
  -c:v libx264 -preset medium -crf 20 \
  output_v5.mp4

# 4. Add labels
mcp-cli call heygen-content-mcp add_text_overlay '{
  "video_path": "output_v5.mp4",
  "text": "❌ Their Way  vs  ✅ your-saas",
  "position": "top",
  "font_size": 20
}'
```

**Content strategy (from marketing-strategy):**
- Left side: show the pain (frozen account, lost revenue, customer complaints)
- Right side: show the solution (payment flowing, dashboard green, revenue up)
- Use real screenshots/recordings when possible — authenticity beats animation
- The comparison should feel unfair — your-saas should obviously win

---

## Clip Production Pipeline (Full Workflow)

### Phase 1 — Source & Transcribe
```bash
# Download
yt-dlp -f "best[height<=720]" --output "/tmp/competitor_content/downloads/VIDEO.mp4" "URL"

# Transcribe
mcp-cli call heygen-content-mcp transcribe '{
  "file_path": "/tmp/competitor_content/downloads/VIDEO.mp4",
  "model": "medium.en"
}'

# Analyze for viral moments
mcp-cli call heygen-content-mcp analyze_transcript '{
  "transcript": "<transcript>",
  "business_context": "your-saas is a payment cloaking and multi-gateway routing service..."
}'
```

### Phase 2 — Cut Clips
```bash
ffmpeg -y -ss START -to END -i source.mp4 -c:v libx264 -c:a aac -preset fast clip.mp4
```

### Phase 3 — Choose Style & Produce
Pick the right style based on clip characteristics:

| Clip Duration | Speaker Visual | Data-Heavy | Best Style |
|---------------|---------------|------------|------------|
| <15s | Compelling face | No | Style 4 (Full-screen overlay) |
| 15-30s | Average | No | Style 3 (Animated bottom) ⭐ |
| 15-30s | Average | Yes | Style 3 (Animated bottom) ⭐ |
| 30-60s | Average | Yes | Style 3 (Animated bottom) ⭐ |
| Any | N/A | N/A | Style 2 (Static image bottom) — fallback |
| Any | N/A | N/A | Style 1 (Text overlay) — quick test |
| Comparison | N/A | N/A | Style 5 (Side-by-side) |

### Phase 4 — Add Text & Branding
```bash
# Hook text (always at top for vertical)
mcp-cli call heygen-content-mcp add_text_overlay '{...}'

# Watermark (bottom-right corner)
mcp-cli call heygen-content-mcp add_watermark '{
  "image_path": "frame.png",
  "text": "@your-saas",
  "position": "bottom-right"
}'
```

### Phase 5 — Review & Post
```bash
# Create VLC playlist
ls output/*.mp4 | sed "s/^/file '/" | sed "s/$/'/" > review.m3u
open -a VLC review.m3u

# Post via Zernio (Instagram, TikTok, Facebook, LinkedIn, YouTube)
# Post via twitter-mcp (X/Twitter)
```

## Hook Writing Framework

Every clip needs a hook. The hook is the single most important element — it determines whether someone watches the clip or scrolls past.

### Hook Formula (from persuasion-genius + marketing-strategy)

**Pattern 1 — The Problem Statement:**
> "Stripe just killed your store. What now?"

**Pattern 2 — The Hidden Truth:**
> "The hidden clause Stripe doesn't want you to see."

**Pattern 3 — The Statistic:**
> "$120K tied up in reserves. 90 days. No warning."

**Pattern 4 — The Question:**
> "Why does this keep happening to successful businesses?"

**Pattern 5 — The Contrast:**
> "Your biggest win can trigger a shutdown."

### Hook Rules
1. **Short:** ≤10 words for overlay, ≤6 words for animated text
2. **Specific:** Numbers > adjectives ("$90K" > "a lot of money")
3. **Pain-first:** Lead with the problem, not the solution
4. **Platform-native:** TikTok hooks need energy; LinkedIn hooks need authority
5. **Test multiple:** Create 3 hooks per clip, A/B test on first post

## CTA Design (from pricing-secrets + sales-mastery)

### CTA Hierarchy (strongest to weakest)
1. **Free trial** — "Start Free → your-saas.com" (lowest friction)
2. **Social proof** — "Join 500+ merchants who switched"
3. **Urgency** — "Before your next payout gets frozen"
4. **Value anchor** — "Free forever vs 2.9% + reserves"
5. **Risk reversal** — "No credit card. Cancel anytime."

### CTA Placement by Platform
| Platform | CTA Location | Format |
|----------|-------------|--------|
| Instagram Reels | Caption + Link in bio | "Link in bio 👆" |
| TikTok | Caption + Bio link | "Free tool in bio" |
| YouTube Shorts | Description + Pinned comment | "Try your-saas free →" |
| LinkedIn | Post body + Comments | "DM me for early access" |
| X/Twitter | Tweet body + Profile | "your-saas.com" |
| Facebook | Post body + Page link | "Learn more →" |
| Pinterest | Pin description + Board link | "your-saas.com/start" |

## Batch Processing

For processing multiple clips from the same source video:

```bash
# Process all clips in a directory
python3 generate_v3_clips.py --all

# Process specific clips
python3 generate_v3_clips.py --clip-numbers 1,5,12

# Custom directories
python3 generate_v3_clips.py \
  --clips-dir /path/to/clips \
  --output-dir /path/to/output \
  --all
```

## File Locations

| Asset | Path |
|-------|------|
| GSAP library | `file://~/mcps_server/heygen-content-mcp/HeyGen/gsap.min.js` |
| Renderer | `~/mcps_server/heygen-content-mcp/HeyGen/render_custom.py` |
| Design system | `~/Documents/mirrorpay-promo/docs/design-system.md` |
| Visual style guide | `~/Documents/mirrorpay-promo/docs/visual-style-guide.md` |
| V3 generator | `generate_v3_clips.py` (in workspace) |
| V3 template | `bottom-half-template.html` (in workspace) |
| CTA image | `/tmp/competitor_content/your-saas_cta_bottom.png` |
| Clip work dir | `/tmp/competitor_content/v3_work/` |
| Clip output | `/tmp/competitor_content/your-saas_v3/` |
| Raw clips | `/tmp/competitor_content/evil_stripe_clips/` |

## Quick Style Selection

Tell the agent which style you want:
- **"text overlay"** or **"simple"** → Style 1
- **"split image"** or **"static bottom"** → Style 2
- **"animated bottom"** or **"GSAP split"** or **"premium"** → Style 3 ⭐
- **"full screen"** or **"overlay"** → Style 4
- **"comparison"** or **"side by side"** or **"before after"** → Style 5
- **"best style for this clip"** → Agent analyzes clip and recommends
