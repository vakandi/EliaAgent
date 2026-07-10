---
name: best-heygen-image
description: Generate blog hero images (1200×630px) that reflect article ideas, audience pain points, and marketing psychology. Uses the HeyGen Content MCP pipeline (HTML/CSS + Playwright screenshot). **Trigger on ANY request for blog images, hero images, social share cards, or article thumbnails — even if the user just says "make an image for this article" or "create a blog hero."** Also trigger when the user provides article content (title, pain point, audience) and needs a matching visual. Designed for YourApp, YourCheckout, and e-commerce marketing content. Each image is tailored to the article's core message, target audience pain point, and desired emotional response.
---

# Best HeyGen Image — Blog Hero Image Generator

## Overview

Create blog hero images (1200×630px) that actually convert readers by targeting the **exact pain point** of the article's audience. This skill uses the HeyGen Content MCP server's HTML composition pipeline with Playwright rendering.

**Key principle**: Every design choice (color, typography, layout, stat) must serve the article's core message and the reader's emotional state at the point of reading.

## Workflow

### Step 1: Extract Article DNA

For each article, extract:

| Element | What to look for | Example |
|---------|-----------------|---------|
| **Core Problem** | The main pain point the article solves | "34% des transactions cross-border échouent" |
| **Target Audience** | Who is reading this? | "Marchands Shopify vendant à l'international" |
| **Emotional Trigger** | The feeling to evoke | Urgency (fraude), Trust (guide), Relief (solution) |
| **Key Stat** | One number that shocks/validates | 34%, 92%, 70%, 20% |
| **CTA Direction** | What action should they take? | "Découvrez les 4 pièges" |

### Step 2: Map to Visual Psychology

Choose color palette based on article emotion:

| Emotion | Primary | Accent | Use Case |
|---------|---------|--------|----------|
| **Urgency/Danger** | `#0D0D0D` | `#DC2626` (Red) | Frais cachés, bans, risques |
| **Trust/Guidance** | `#0F172A` | `#3B82F6` (Blue) | Guides, comparatifs, how-to |
| **Premium/Innovation** | `#0A0A1A` | `#8B5CF6` (Purple) | Solutions innovantes, premium |
| **Success/Relief** | `#0A1A0A` | `#22C55E` (Green) | Solutions, optimisations, résultats |
| **Warning** | `#1A0F00` | `#F59E0B` (Amber) | Pièges à éviter, erreurs |

### Step 3: Compose the Layout

**Structure** (1200×630px):

```
┌──────────────────────────────────────────────┐
│  [●●] LABEL BADGE                     [STAT] │
│                                              │
│  TITLE LINE 1                                │
│  TITLE HIGHLIGHT LINE                        │
│                                              │
│  Pain point text with left accent bar        │
│                                              │
│  [CTA BUTTON →]                              │
│                                              │
│  Background: gradient + geometric shapes     │
│  + grid overlay + accent line bottom         │
├──────────────────────────────────────────────┤
│  Brand watermark                    Blueprint │
└──────────────────────────────────────────────┘
```

Elements:
1. **Label badge** — pill shape with colored dot, category label
2. **Title** — main headline (56px, 800 weight), highlight line with gradient
3. **Pain point** — smaller text with left accent bar, shows the severity
4. **Stat box** — right side, large number + label (the key stat)
5. **CTA button** — colored button with arrow
6. **Background** — dark base + colored radial gradients + geometric shapes + subtle grid

### Step 4: Generate via HeyGen MCP

Use the `generate_blog_image.py` script in the HeyGen Content MCP pipeline:

```bash
# Single article
cd /path/to/heygen-mcp
.venv/bin/python HeyGen/generate_blog_image.py --article 1

# All 4 articles
.venv/bin/python HeyGen/generate_blog_image.py --all

# Custom output directory
.venv/bin/python HeyGen/generate_blog_image.py --all --output-dir ./my-custom-images
```

The script:
1. Builds an HTML composition with all styling inline
2. Uses Playwright (Chromium headless) to render at 2x retina quality
3. Outputs JPEG at 95% quality, 1200×630px
4. Saves to `HeyGen/output/blog/` directory
5. Creates a `manifest.json` with all results

## Article Schema

Each blog image needs this data structure:

```python
{
    "id": 1,                    # Article number
    "title": "Main headline",   # First line
    "subtitle": "Highlight",    # Gradient-colored second line
    "slug": "url-slug",         # For filename
    "pain_point": "Core pain",  # Displayed below title
    "audience": "Target reader", # For design decisions
    "visual_concept": "iceberg", # The metaphor used
    "primary_color": "#000000",  # Background base
    "accent_color": "#FF0000",   # Main accent (buttons, labels)
    "accent2_color": "#FFD700",  # Secondary accent (gradients)
    "text_color": "#FFFFFF",      # Text
    "label": "CATEGORY TAG",      # Badge text
    "cta_text": "Call to action", # Button text
}
```

## Stat Mapping

Each article gets ONE key stat as the visual hook:

| Article Theme | Stat | Label |
|--------------|------|-------|
| Frais cachés/traps | 34% | des transactions cross-border échouent |
| Guide/trust | 92% | préfèrent payer en devise locale |
| Abandon/optimisation | 70% | d'abandon panier lié aux devises |
| Redirection | 20% | d'abandon sur checkout redirigé |

## Color Psychology Reference

### Red (`#DC2626`) — Urgency/Danger
- Triggers: alertness, caution, immediate action
- Best for: articles about problems, risks, hidden fees, bans
- Pair with: dark backgrounds (`#0D0D0D`)

### Blue (`#3B82F6`) — Trust/Stability
- Triggers: confidence, security, professionalism
- Best for: guides, tutorials, comparisons
- Pair with: slate dark (`#0F172A`)

### Purple (`#8B5CF6`) — Premium/Innovation
- Triggers: creativity, luxury, sophistication
- Best for: innovative solutions, premium offerings
- Pair with: deep navy (`#0A0A1A`)

### Green (`#22C55E`) — Success/Relief
- Triggers: growth, safety, resolution
- Best for: solutions, optimizations, positive outcomes
- Pair with: dark green (`#0A1A0A`)

## HTML Composition Template

The `build_html()` function in `generate_blog_image.py` produces:

- **Background layers**: dark base + radial gradients (20% and 80% positions) + subtle grid overlay
- **Geometric accents**: 3 overlapping circles/blobs at 8-15% opacity
- **Bottom accent line**: 4px gradient bar matching accent colors
- **Label**: border pill with animated dot indicator
- **Title**: 56px/800 weight with gradient highlight via `background-clip: text`
- **Pain point**: 15px with left border accent
- **Stat box**: centered number + label with backdrop blur
- **CTA**: filled button with shadow glow and arrow

## Anti-Patterns (DO NOT DO)

- ❌ Generic stock photos that don't reflect article pain points
- ❌ Text-heavy images (>20 words) — blog images must be scannable
- ❌ Bright/light backgrounds for e-commerce pain articles (dark = serious)
- ❌ Multiple stats — ONE key number only
- ❌ Ignoring the audience — a guide for beginners needs different visuals than expert content
- ❌ Mismatched color emotion — don't use green for "hidden fees" articles
- ❌ Small text — blog images are often displayed at 300×157px in cards

## Dev Notes

- Script: `/path/to/heygen-mcp/HeyGen/generate_blog_image.py`
- Output: `/path/to/heygen-mcp/HeyGen/output/blog/`
- Resolution: 1200×630px (2:1 blog hero ratio)
- Quality: JPEG 95%, 2x device scale factor
- Dependencies: playwright, mcp (in .venv)
- The Heygen MCP server definition is in `~/.config/mcp/mcp_servers.json` as `heygen-content-mcp`
- MCP Server startup: `cd /path/to/heygen-mcp && .venv/bin/python main.py`
