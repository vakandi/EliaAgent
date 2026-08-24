---
name: apple-image-generator
description: Generate images using Apple Intelligence (on-device) and Pollinations.ai (cloud) via MCP. Use this skill whenever the user asks to generate images, create social media visuals, make blog post images, produce content visuals, or any request involving AI image generation. Also trigger on: "make an image", "generate a picture", "create visual content", "social media images", "blog images", "product images", "brand art", "illustration", "sketch", "animation style". The server provides 40+ platform presets, text overlay, watermark, smart crop, and batch generation.
---

# Apple Image Generator MCP

## How to Call

```bash
mcp-cli call apple-image-playground <tool> '<json-arguments>'
```

**Server name:** `apple-image-playground`

## IMPORTANT — Many Styles, Many Results

The same prompt with a different style produces a **completely different image**. This is not a minor tweak — the style determines the entire visual identity. Always try multiple styles for the same prompt to get the best result. Don't just pick one and ship it.

**Style exploration is mandatory for any brand content.** Generate the same prompt with `illustration`, `sketch`, and `animation` before deciding. Each one gives a totally different vibe.

### Available Apple Intelligence Styles

| Style | What It Does | Best For |
|-------|-------------|----------|
| `illustration` | Clean vector-like illustration, flat colors | Blog headers, social posts, brand assets |
| `sketch` | Hand-drawn pencil/charcoal look | Artistic, editorial, rough concepts |
| `animation` | 3D cartoon/render style, Pixar-like | Fun, playful, product showcases |
| `emoji` | Emoji-style character art | Fun content, reactions (iOS only) |
| `messages-background` | Stylized background pattern | Backgrounds, textures (iOS only) |

**On macOS:** `illustration`, `sketch`, and `animation` work reliably. `emoji` and `messages-background` may timeout.

## Quick Start

### 1. Check Available Engines

```bash
mcp-cli call apple-image-playground list_engines '{}'
```

### 2. Generate an Image — Try Multiple Styles

```bash
# Same prompt, 3 different styles — always compare:
mcp-cli call apple-image-playground generate_image '{"prompt":"a cute cat wearing a hat","engine":"apple","style":"illustration"}'
mcp-cli call apple-image-playground generate_image '{"prompt":"a cute cat wearing a hat","engine":"apple","style":"sketch"}'
mcp-cli call apple-image-playground generate_image '{"prompt":"a cute cat wearing a hat","engine":"apple","style":"animation"}'

# Photorealistic (Pollinations.ai — free, no API key)
mcp-cli call apple-image-playground generate_image '{"prompt":"a sunset over mountains","engine":"pollinations"}'
```

### 3. Generate Social Media Pack

```bash
mcp-cli call apple-image-playground generate_social_pack '{"prompt":"product launch announcement","platforms":["instagram_post","twitter_post","linkedin_post"]}'
```

## Brand Content — Use `input_image` for Better Results

**This is the key to brand-quality images.** When generating for a brand (your-saas, your-brand, etc.):

1. **Download the real logo/brand images first** — curl from their website
2. **Pass them as `input_image`** — Apple Intelligence uses the photo as a concept, blending the brand's visual identity into the generated image
3. **Result:** The generated image actually looks like it belongs to that brand, not generic AI art

### Workflow for Brand Images

```bash
# Step 1: Download the brand logo
curl -sL "https://your-saas.com/favicon.ico" -o /tmp/your-saas_logo.png

# Step 2: Generate with the logo as input — Apple blends it into the style
mcp-cli call apple-image-playground generate_image '{
  "prompt": "a futuristic payment terminal floating in space",
  "style": "illustration",
  "engine": "apple",
  "input_image": "/tmp/your-saas_logo.png",
  "absolute_path": "/tmp/your-saas_hero.png"
}'

# Step 3: Add brand text overlay
mcp-cli call apple-image-playground add_text_overlay '{
  "image_path": "/tmp/your-saas_hero.png",
  "text": "The Future of Payments",
  "font_size": 48,
  "font_color": "#FFFFFF",
  "position": "center"
}'
```

### Brand Asset Quick Reference

| Brand | Logo Source | Colors | Style |
|-------|------------|--------|-------|
| **your-saas** | `https://your-saas.com/favicon.ico` | Deep purple, gold, white | Clean tech, financial |
| **your-brand** | Check `your-brand.com` | Black, gold, cream | Luxury, minimal |
| **your-agency** | Check `your-agency.agency` | Modern, dark | B2B tech |

**Without `input_image`:** generic AI art that could be for anyone.
**With `input_image`:** the image incorporates the brand's visual DNA.

## All Tools

### Discovery

```bash
mcp-cli call apple-image-playground list_engines '{}'
mcp-cli call apple-image-playground list_styles '{}'
mcp-cli call apple-image-playground list_presets '{}'
mcp-cli call apple-image-playground list_bundles '{}'
```

### Core Generation

```bash
# Single image — Apple Intelligence
mcp-cli call apple-image-playground generate_image '{"prompt":"a cat riding a bicycle","engine":"apple","style":"animation","count":1}'

# Single image — Apple Intelligence with brand input
mcp-cli call apple-image-playground generate_image '{"prompt":"luxury fashion store interior","engine":"apple","style":"illustration","input_image":"/tmp/brand_logo.png"}'

# Single image — Pollinations (photorealistic)
mcp-cli call apple-image-playground generate_image '{"prompt":"professional product photo of sneakers","engine":"pollinations","width":1024,"height":1024}'

# Social media pack — generate + crop for multiple platforms
mcp-cli call apple-image-playground generate_social_pack '{"prompt":"new blog post header","platforms":["blog_header","og_image","instagram_post"],"engine":"pollinations"}'

# Bundle — predefined platform groups
mcp-cli call apple-image-playground generate_bundle '{"prompt":"startup launch announcement","bundle":"startup_kit"}'

# Batch — multiple prompts at once
mcp-cli call apple-image-playground generate_batch '{"prompts":["sunset over ocean","mountain landscape","city skyline"],"engine":"pollinations","platforms":["instagram_post","twitter_post"]}'
```

### Post-Processing

```bash
# Add text overlay (quotes, CTAs, headlines)
mcp-cli call apple-image-playground add_text_overlay '{"image_path":"/path/to/image.png","text":"50% OFF TODAY","font_size":64,"font_color":"#FFFFFF","bg_color":"#000000","position":"center"}'

# Add watermark
mcp-cli call apple-image-playground add_watermark '{"image_path":"/path/to/image.png","text":"@brand","opacity":80,"position":"bottom-right"}'

# Create gradient background
mcp-cli call apple-image-playground create_gradient '{"width":1080,"height":1080,"color_top":"#1a1a2e","color_bottom":"#16213e"}'

# Create text post (gradient + text — ready to post)
mcp-cli call apple-image-playground create_text_post '{"text":"Your daily inspiration","width":1080,"height":1080,"gradient":true}'

# Apply filter
mcp-cli call apple-image-playground apply_filter '{"image_path":"/path/to/image.png","filter_name":"sepia","intensity":0.7}'
```

### Crop & Utility

```bash
# Smart crop (face-aware, uses Apple Vision framework)
mcp-cli call apple-image-playground smart_crop '{"image_path":"/path/to/photo.jpg","target_width":1080,"target_height":1080}'

# Detect faces
mcp-cli call apple-image-playground detect_faces '{"image_path":"/path/to/photo.jpg"}'

# Crop existing image to multiple platform sizes
mcp-cli call apple-image-playground crop_image '{"image_path":"/path/to/photo.jpg","platforms":["instagram_post","facebook_post","twitter_post"]}'

# Resize image
mcp-cli call apple-image-playground resize_image '{"image_path":"/path/to/image.png","width":800}'
```

## `absolute_path` — Force Output Location

Every tool that produces an image supports `absolute_path` to save to a specific location. If the file already exists, it returns an error (no accidental overwrites).

```bash
mcp-cli call apple-image-playground generate_image '{"prompt":"...","absolute_path":"/Users/me/project/images/hero.png"}'
```

## Platform Presets

| Preset | Dimensions | Use Case |
|--------|-----------|----------|
| `instagram_post` | 1080x1080 | Square feed post |
| `instagram_portrait` | 1080x1350 | Portrait feed post |
| `instagram_story` | 1080x1920 | Stories/Reels |
| `twitter_post` | 1600x900 | Tweet image |
| `linkedin_post` | 1200x627 | LinkedIn post |
| `facebook_post` | 1200x630 | Facebook feed |
| `pinterest_pin` | 1000x1500 | Pinterest pin |
| `youtube_thumbnail` | 1280x720 | YT thumbnail |
| `tiktok` | 1080x1920 | TikTok video |
| `og_image` | 1200x630 | Open Graph share |
| `blog_header` | 1600x800 | Blog hero |

Run `list_presets` to see all 40+ presets.

## Bundles

| Bundle | Platforms Included |
|--------|-------------------|
| `full_social` | instagram, facebook, twitter, linkedin, pinterest, youtube, tiktok |
| `instagram_set` | post, portrait, story, reel_cover, carousel |
| `blog_set` | header, inline, thumbnail, og_image, square_thumbnail |
| `startup_kit` | og_image, twitter, linkedin, blog_header, email_header |
| `short_form_video` | tiktok, reel_cover, facebook_reel, story |
| `youtube_set` | thumbnail, banner, community |

## Engine Selection Guide

| Use Case | Engine | Why |
|----------|--------|-----|
| Brand art, social graphics | `apple` | Stylized, unique look |
| Brand content with logo input | `apple` + `input_image` | Blends brand identity into result |
| Product photos, people | `pollinations` | Photorealistic |
| Quick concept art | `pollinations` | Fast, no setup |
| Consistent brand style | `apple` + same style | Repeatable visual language |

## Response Format

All tools return:
- `success`: boolean — check this first
- `path`: file path to generated image
- `next_steps`: suggestions for what to do next
- `error`: failure reason (when success=false)

## Dependencies

- Python: `pip install "mcp[cli]" pillow`
- Optional (Apple Intelligence): compiled Swift helper
- Pollinations.ai: works out of the box, no API key needed
