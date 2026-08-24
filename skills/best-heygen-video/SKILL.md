---
name: best-heygen-video
description: Generate simple, clean promo videos using GSAP animations rendered via Playwright+FFmpeg. Best for B2B content, explainer videos, and content that illustrates a point clearly — NOT for highly animated, hook-driven social media content. For cinematic product videos with 2.5D camera moves, beat-synced cuts, and professional motion design, use video-shotcraft instead. Use this skill when you need a straightforward animated video to explain a concept, show a comparison, or present data — think "infographic in motion" rather than "film-grade promo."
---

# Best HeyGen Video

Generate clean, professional explainer videos using GSAP + Playwright + FFmpeg. No external video API needed — everything runs locally.

## When to Use This Skill vs Video-Shotcraft

| Use **best-heygen-video** when... | Use **video-shotcraft** when... |
|-----------------------------------|--------------------------------|
| B2B explainer or tutorial video | Cinematic product promo |
| Data visualization / infographic in motion | High-end marketing content |
| Simple comparison (before/after, us vs them) | Social media hooks that need wow factor |
| Internal presentation or demo | Brand video with 2.5D camera moves |
| Content that **illustrates a point** clearly | Content that **stops the scroll** |
| Quick turnaround, simple animations | Beat-synced cuts, sound design, film-grade SFX |

**Think of it this way:** best-heygen-video = "PowerPoint that moves." video-shotcraft = "Apple keynote intro."

If the user wants something with serious motion design, multiple camera angles, sound design, and cinematic quality — load `video-shotcraft` instead. This skill is for the 80% of videos that just need to communicate clearly without winning awards.

## Overview

The pipeline: **Download assets** → **Build HTML composition** → **Render frames via Playwright** → **Encode MP4 via FFmpeg**.

Output: vertical (1080×1920) or horizontal (1920×1080) MP4, 27-30fps, H.264.

## Directory Structure

All work happens in:
```
~/mcps_server/heygen-content-mcp/HeyGen/
├── work/              ← HTML files, frames, downloaded assets
├── output/            ← Final MP4 files
├── gsap.min.js        ← Local GSAP (offline, no CDN)
├── render_custom.py   ← Playwright+FFmpeg renderer
└── generate_content.py ← AI content generation (optional)
```

## Step 1: Download Real Assets

Before writing any HTML, gather real logos and images. Never use emoji placeholders when a real logo exists.

### Logo sourcing strategy

**Never use emoji placeholders when a real logo exists.** Premium feel requires real brand assets.

1. **Simple Icons CDN** (preferred — CC0 license, 2800+ brands):
```bash
mkdir -p work/assets/logos
curl -sL "https://cdn.simpleicons.org/stripe" -o work/assets/logos/stripe.svg
curl -sL "https://cdn.simpleicons.org/paypal" -o work/assets/logos/paypal.svg
curl -sL "https://cdn.simpleicons.org/mollie" -o work/assets/logos/mollie.svg

# Convert SVG → PNG at target size (200x200)
convert -background none -density 300 work/assets/logos/stripe.svg -resize 200x200 work/assets/logos/stripe.png
```

2. **Clearbit logo API** (fast, high quality):
```bash
curl -sL "https://logo.clearbit.com/stripe.com" -o work/assets/logos/stripe.png
curl -sL "https://logo.clearbit.com/paypal.com" -o work/assets/logos/paypal.png
```

3. **Parallel-browser-mcp** (for sites that block curl or need JS rendering):
```
Start session → navigate to logo URL → screenshot element → save to work/assets/logos/
```

4. **Brand press kit pages** (official, highest quality):
```bash
# Many brands have /press or /brand-resources pages
curl -sL "https://stripe.com/press" → find logo download link → save
```

### Logo specifications for 1080×1920

| Context | Size | Format |
|---------|------|--------|
| Provider row icon | 120×120px | PNG transparent |
| Card badge | 80×80px | PNG transparent |
| Feature icon (hero) | 160×160px | PNG transparent |
| Full brand logo (with wordmark) | 400×120px | PNG transparent |

### Asset rules

- Store all assets in `work/assets/logos/` before writing HTML
- Use `<img src="file:///full/path/to/asset.png">` in HTML (not relative paths)
- PNG with transparency preferred over JPG
- Always download GSAP locally: `curl -sL "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" -o gsap.min.js`
- Reference local GSAP with **absolute file:// path** — NEVER relative `../`:
  ```html
  <script src="file://~/mcps_server/heygen-content-mcp/HeyGen/gsap.min.js"></script>
  ```
  Relative paths like `../gsap.min.js` break when HTML is in subdirectories (e.g. `work/your-saas-youtube/`). The renderer loads via `file:///absolute/path.html` and relative `../` resolves WRONG — GSAP silently fails, video renders empty (just background).
- License: Use CC0 or official brand assets only. Never recreate or modify brand logos.

## Step 2: Build HTML Composition

### Mandatory structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1920">
    <title>Video Title</title>
    <script src="file://~/mcps_server/heygen-content-mcp/HeyGen/gsap.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            width:1080px; height:1920px;
            background:#0A0A1A;
            font-family:'Inter',-apple-system,sans-serif;
            overflow:hidden; position:relative; color:#fff;
        }
        .slide {
            position:absolute; top:0; left:0; width:1080px; height:1920px;
            display:flex; flex-direction:column; justify-content:center; align-items:center;
            padding:80px 60px; opacity:0; pointer-events:none;
        }
    </style>
</head>
<body>
    <!-- Scenes as .slide elements -->
    
    <script>
    const master = gsap.timeline({ paused: true });
    window.__timelines = { main: master };  // CRITICAL: renderer needs this
    
    // Build timeline...
    </script>
</body>
</html>
```

### Critical renderer requirements

1. **`window.__timelines = { main: master }`** — The Playwright renderer seeks this timeline. Without it, the video renders empty.

2. **`gsap.timeline({ paused: true })`** — Start paused. The renderer controls playback via `.seek()`.

3. **Use `.set()` and `.from()`/`.to()` for all visibility** — Elements start with `opacity:0` in CSS, GSAP reveals them. Don't use `display:none`.

4. **Local GSAP only** — CDN scripts fail in headless Playwright. Always use absolute `file://~/mcps_server/heygen-content-mcp/HeyGen/gsap.min.js`.

5. **Exact viewport** — `<meta name="viewport" content="width=1080, height=1920">` and body dimensions must match.

### Animation timeline pattern

```javascript
// Scenes at specific timestamps
const SCENES = {
    s1: { start: 0, end: 5 },      // Hook / Problem
    s2: { start: 5, end: 12 },     // Solution
    s3: { start: 12, end: 18 },    // Proof
    s4: { start: 18, end: 25 },    // CTA
};

// Scene 1: fade in elements with stagger
master.set('#s1', { opacity: 1 });
master.from('#s1 .badge', { y: -30, opacity: 0, duration: 0.4 }, 0);
master.from('#s1 h1', { y: 40, opacity: 0, duration: 0.6, ease: 'power3.out' }, 0.3);

// Scene transition: fade out previous, fade in next
master.to('#s1', { opacity: 0, duration: 0.4 }, 4.6);
master.set('#s2', { opacity: 1 }, 5.0);
```

### Design principles

**The 3-Layer Depth Model** — Every scene has 3 visual layers:
- Layer 0 (Background): Dark base + subtle radial gradient + noise texture
- Layer 1 (Context): Grid dots, subtle lines, geometric shapes (max 15% opacity)
- Layer 2 (Content): Main visuals, text, CTAs (high contrast, always the hero)

**Color system:**
```
Primary BG:     #0A0A1A (deep navy-black)
Secondary BG:   #111827 (dark gray, for cards)
Accent Success: #22C55E (green — solution, positive)
Accent Danger:  #EF4444 (red — problem, error)
Accent Warning: #F59E0B (amber — warnings)
Text Primary:   #F8FAFC (near-white)
Text Secondary: #94A3B8 (muted slate)
Card BG:        rgba(255,255,255,0.05) (glass morphism)
Card Border:    rgba(255,255,255,0.08)
```
Max 3 colors per scene. Green = solution, Red = problem, White = text.

**Typography for 1080×1920:**
- Headlines: Space Grotesk or Clash Display, 48-56px, weight 700, letter-spacing -0.02em
- Body: Inter, 28-32px, weight 400
- Stat numbers: JetBrains Mono, 72-80px, weight 800, green accent
- CTA: 28px, weight 600, uppercase, letter-spacing 0.05em
- Never more than 3 font sizes per scene

**Animation timing:**
- Scene duration: 4-6 seconds
- Entry animation: 0.4-0.6s (ease-out cubic)
- Hold (read time): 2.5-3.5s minimum — if viewer can't read it in 2.5s, text is too long
- Exit animation: 0.3-0.4s (ease-in)
- Stagger between elements: 0.1-0.15s

**Visual density:**
- Max 5-7 elements per scene
- Max 3-4 text lines per scene
- Max 1-2 CTAs per video (at the end)
- Each scene does ONE job — don't overload

**Animation patterns:**
- `power3.out` for entrances
- `back.out(1.4-2)` for pops/bounces
- `linear` for rotations
- Subtle noise texture overlay for depth (CSS SVG turbulence filter)
- Animated mesh gradients or aurora borealis instead of flat blur orbs

## Step 3: Render Video

### Using render_custom.py

**⚠️ CRITICAL: Always pass ABSOLUTE paths to render_custom.py.** Relative paths break `file://` protocol in Playwright.

```bash
python3 ~/mcps_server/heygen-content-mcp/HeyGen/render_custom.py \
    ~/mcps_server/heygen-content-mcp/HeyGen/work/my-video.html \
    ~/mcps_server/heygen-content-mcp/HeyGen/output/my-video.mp4 \
    {duration_seconds} {width} {height}
```

Example:
```bash
HEYGEN="~/mcps_server/heygen-content-mcp/HeyGen"
python3 "$HEYGEN/render_custom.py" \
    "$HEYGEN/work/your-saas-promo.html" \
    "$HEYGEN/output/your-saas-promo.mp4" \
    27 1080 1920
```

### What render_custom.py does

1. **CLEANS the frames directory** (removes stale frames from previous renders — prevents cross-contamination)
2. Launches headless Chromium via Playwright
3. Loads HTML file at exact viewport (1080×1920, 2x device scale)
4. Waits 2s for page load
5. Seeks `window.__timelines['main']` to frame-by-frame
6. Captures JPEG frames at 30fps
7. Encodes frames to MP4 via FFmpeg (libx264, CRF 23)

### If render fails

- **Empty video (gradient only)**: GSAP not loading. Check the GSAP src is `file://~/mcps_server/heygen-content-mcp/HeyGen/gsap.min.js` (absolute, NOT relative `../`). Also verify `window.__timelines = { main: master }` exists.
- **Wrong content / mixed videos**: Stale frames from a previous render. The renderer now auto-cleans the frames dir, but if you see this, manually delete `work/frames/` before re-rendering.
- **Short duration**: Frame count mismatch. Verify total_frames = duration × 30.
- **No frames captured**: Playwright can't load the file. Check all asset paths use `file:///absolute/` URLs.
- **GSAP ERR_FILE_NOT_FOUND in console**: The `../gsap.min.js` relative path is wrong. HTML files in subdirectories (e.g. `work/your-saas-youtube/`) need TWO levels up or an absolute path. Always use absolute.

## Step 4: Verify Output

```bash
# Check video metadata
ffprobe -v quiet -print_format json -show_format -show_streams output/video.mp4

# Open for visual review
open output/video.mp4
```

Expected for a 27s 1080×1920 video: ~1-2MB, 400-600 kbps, H.264.

## Quick Start Template

```bash
#!/usr/bin/env bash
set -euo pipefail

HEYGEN="~/mcps_server/heygen-content-mcp/HeyGen"
WORK="$HEYGEN/work"
OUTPUT="$HEYGEN/output"
RENDER="$HEYGEN/render_custom.py"
GSAP="file://~/mcps_server/heygen-content-mcp/HeyGen/gsap.min.js"

# 1. Create assets directory
mkdir -p "$WORK/assets"

# 2. Download real logos
curl -sL "https://logo.clearbit.com/stripe.com" -o "$WORK/assets/stripe.png"
curl -sL "https://logo.clearbit.com/paypal.com" -o "$WORK/assets/paypal.png"

# 3. Write HTML composition — USE ABSOLUTE GSAP PATH IN THE HTML:
#    <script src="$GSAP"></script>
# Save to: $WORK/my-video.html

# 4. Render — ALWAYS ABSOLUTE PATHS
python3 "$RENDER" "$WORK/my-video.html" "$OUTPUT/my-video.mp4" 27 1080 1920

# 5. Verify
ffprobe -v quiet -print_format json -show_format "$OUTPUT/my-video.mp4"
open "$OUTPUT/my-video.mp4"
```

## When to call @picasso for design advice

Before finalizing your video composition, call `@picasso` (subagent_type: "picasso") for expert design consultation. Picasso is the elite frontend specialist who can advise on:

- Color system refinement and brand consistency
- Typography pairings and scale for video
- Visual hierarchy and layout optimization
- Animation timing and easing curves
- Platform-specific design requirements (TikTok vs YouTube vs Instagram)
- Accessibility and readability at video speeds

**When to call:**
- Creating a new video template or brand style
- Uncertain about color palette or typography choices
- Need validation on visual hierarchy before rendering
- Adapting design for different platform formats

**How to call:**
```
task(subagent_type="picasso", prompt="Review this video composition HTML and advise on: [specific questions]", run_in_background=false)
```

## Quick Wins for Premium Feel

1. **Real logos** via Simple Icons CDN → instant upgrade from emoji placeholders
2. **Noise texture** on background (CSS: SVG turbulence filter at 3-5% opacity)
3. **Headline font**: Space Grotesk or Clash Display instead of Inter
4. **Animated counters** on stat numbers (count up from 0 on entry)
5. **Aurora gradient** animation instead of flat blur orbs

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Empty/gradient-only video | GSAP path is wrong. Use `file://~/mcps_server/heygen-content-mcp/HeyGen/gsap.min.js` (absolute, NOT `../`) |
| Video shows wrong content from another project | Stale frames. Renderer auto-cleans now, but manually delete `work/frames/` and re-render |
| GSAP not loading (console: ERR_FILE_NOT_FOUND) | HTML is in a subdirectory. Relative `../gsap.min.js` resolves wrong. Use absolute `file:///` path |
| Fonts not rendering | Google Fonts may not load in headless — use system fonts or inline @font-face |
| Video too short | Check timeline duration matches `duration` arg to render_custom.py |
| Logo not showing | Use `file:///absolute/path` for local assets, not relative paths |
| Frames not captured | Increase `wait_for_timeout(2000)` in render_custom.py |
| Video file very small (<500KB for 27s) | Frames are blank — GSAP timeline not seekable, check window.__timelines |
| render_custom.py errors with relative path | Always pass ABSOLUTE paths to render_custom.py, never relative |
