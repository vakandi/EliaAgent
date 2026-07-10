---
name: blog-photo-yourapp
description: >
  Generate image prompts for YourApp blog posts. Use this skill whenever:
  - The user asks to create/generate blog post images or hero images for YourApp
  - The user wants to find YourApp blog posts that are missing photos/images
  - The user needs image prompt ideas for YourApp blog content about payment cloaking, Stripe bans, Shopify/WooCommerce payments
  - The user says "make images for the blog", "generate prompts for blog photos", "check which posts need images"
  - The user wants to create featured images following YourApp's visual style (dramatic 3D illustrations, split-screen X-ray, financial-tech aesthetic)
  - Any task involving YourApp blog visual content, even if the user doesn't explicitly name the skill
  - TRIGGER PROACTIVELY: If the user mentions blog posts and YourApp in the same context, suggest checking which posts need images
compatibility: "python3 (for the bundled fetch script), curl (for quick ad-hoc queries)"
---

# YourApp Blog Photo Generator

This skill helps you generate **SEO-optimized, conversion-driven image prompts** for YourApp blog articles. The workflow is:

1. **Query Directus** to find which published blog posts don't have a featured image
2. **List them** with title, slug, description
3. **Generate custom image prompts** for each post (or a selected one) following YourApp's visual branding

### Why blog images matter for SEO and conversions

| Factor | Impact |
|--------|--------|
| **Social sharing** | Tweets with images get **150% more retweets**. LinkedIn posts with images have **2× higher engagement**. |
| **OG image (Open Graph)** | Controls how your article appears when shared on Facebook, Twitter/X, LinkedIn, Discord. A poor OG image = no one clicks. |
| **Pinterest traffic** | Pinterest is a visual search engine. Well-pinned articles can drive traffic for **years** after publication. |
| **Backlinks** | People link to articles that look professional. A blog post without a hero image looks unfinished and less authoritative. |
| **Time on page** | A compelling hero image increases time-on-page and reduces bounce rate — both signals that help SEO rankings. |
| **Brand recognition** | Consistent visual style across all blog images builds recognizable brand authority. When backlinkers see a YourApp image style, they associate it with quality. |
| **Click-through rate** | Articles with relevant, high-quality images get **94% more views** than those without. The image is the first thing readers see. |

---

## 📡 Step 1: Find Blog Posts Without Images

Use the bundled Python script:

```bash
python3 /path/to/blog-photo-skill/scripts/fetch_blog_posts.py
```

This queries the YourApp Directus instance (`https://dash.[your-app].com`) and returns only published posts where `image` is `null`.

**Options:**
- `--all` — list ALL published posts (including ones that already have images)
- `--slug=my-post-slug` — get details + full content for a single post
- `--full` — include the **full rich-text content** field (needed for context to generate accurate prompts)

**Always use `--full` when you need the article body to craft relevant prompts.** The full content field contains the complete article text which is essential for understanding the article's message, sections, and tone.

**Example output (basic):**
```json
[
  {
    "id": "42",
    "title": "Why Your International Shopify Sales Fail 34% of the Time",
    "slug": "international-shopify-sales-fail",
    "description": "Hidden conversion fees and currency mismatches are silently killing your cross-border sales.",
    "published_at": "2026-06-28T10:00:00.000Z",
    "has_image": false
  }
]
```

**Example output (with `--full`):**
```json
[
  {
    "id": "42",
    "title": "Why Your International Shopify Sales Fail 34% of the Time",
    "slug": "international-shopify-sales-fail",
    "description": "Hidden conversion fees and currency mismatches are silently killing your cross-border sales.",
    "published_at": "2026-06-28T10:00:00.000Z",
    "has_image": false,
    "content": "<h2>The Hidden Trap of Dynamic Currency Conversion</h2><p>When a customer from Switzerland sees your prices in EUR...</p>..."
  }
]
```

### Quick curl alternative (ad-hoc)

```bash
curl -s "https://dash.[your-app].com/items/posts?filter=%7B%22_and%22%3A%5B%7B%22status%22%3A%7B%22_eq%22%3A%22published%22%7D%7D%2C%7B%22image%22%3A%7B%22_null%22%3Atrue%7D%7D%5D%7D&sort=-published_at&fields=id,title,slug,description,published_at,image&limit=25" \
  -H "Authorization: Bearer sp-admin-token-2026-190c1875aec049db" | python3 -m json.tool
```

---

## 🎨 Step 2: Understand the Article Content (Read the Full Post)

**Before generating any image prompts, always retrieve the full article content** to understand what the post is about — its core message, key sections, tone, and the specific pain points it addresses.

```bash
python3 /path/to/blog-photo-skill/scripts/fetch_blog_posts.py --slug=post-slug-here --full
```

Extract key themes from the content:
- What is the **core problem** the article addresses? (e.g., hidden fees, Stripe bans, cart abandonment)
- What **metaphors or analogies** does the article use?
- What is the **target audience**? (merchants/B2B or end customers)
- What **emotion** should the image convey? (urgency, relief, trust, clarity)
- What **keyword or phrase** would someone search to find this article? (this influences the image concept for Pinterest/Image search)

## 🎨 Step 3: Generate the Single Best Image Prompt — Output Directly in Messages

For each blog post that needs an image, generate **exactly one image prompt — the single best option**. No alternatives. No "Option 1, Option 2, Option 3...". Just the one optimal prompt that maximizes SEO + conversion + brand consistency for that specific article.

**CRITICAL: Output the prompt directly in your response message.** Do NOT write it to files. The user needs to copy it directly from the chat to use with Midjourney/DALL-E/Stable Diffusion. The prompt should be clearly formatted and ready to copy-paste.

### YourApp Visual Branding

The YourApp visual identity follows these patterns:
- **Dramatic storytelling** — The problem is shown in dark/moody red tones, the solution (YourApp) in clean blue/white
- **Metaphors**: funhouse mirrors, labyrinths, roulette wheels, crumbling cliffs, leaky pipes — always with YourApp as the clear fix
- **Audience split**: Some images target merchants (B2B, technical, dashboard-focused), others target customers (emotional, trust-focused)
- **Style range**: offer a mix — cinematic 3D, abstract isometric, split-screen X-ray, flat vector
- **Format**: always 16:9 (1200×630px for OG images)
- **Always include** `YourApp.com` logo in the image as the solution element

### SEO Optimization for Each Image

Every prompt option MUST include these SEO elements:

1. **Suggested file name** — Descriptive, keyword-rich, hyphens. Example: `hidden-currency-conversion-fees-shopify-checkout.jpg`
2. **Alt text** — 120-125 characters, describes what the image shows, includes target keyword naturally. Example: *"Dramatic 3D illustration of hidden currency conversion fees trapping a Shopify merchant with confusing exchange rates and percentage symbols."*
3. **OG image suitability** — The image must work as a 1200×630 Open Graph card. This means:
   - Clear focal point centered or on the left third (where text overlay would go)
   - High contrast so thumbnails are readable at small sizes
   - No critical details in the outer 10% (safe zone for platform cropping)
   - YourApp branding visible even at 150px thumbnail size

### Conversion Psychology for Each Image

Each image prompt must serve a specific conversion goal:

| Goal | Visual Strategy | When to Use |
|------|----------------|-------------|
| **Click-through** | Create curiosity gap — show the problem but not the full solution | Paid social, email newsletters |
| **Social share** | Bold, emotionally charged, easy to understand in 1 second | Viral/content marketing posts |
| **Trust building** | Professional, clean, branded, authoritative | Tutorials, guides, "how to" articles |
| **Urgency/action** | Red/amber tones, countdown or stats, problem-focused | "Why you're losing money" articles |
| **Brand recall** | Strong YourApp blue/white presence, mirror metaphor visible | Any post, build recognition over time |

**Rule**: Every image should pass the "1-second test" — someone scrolling on LinkedIn/Twitter should understand what the article is about within 1 second of seeing the image.

### Prompt Template Structure

The single best prompt MUST include ALL of these elements:

1. **Style rationale** — 1 sentence explaining why this style matches the article's dominant angle
2. **SEO file name** — `keyword-rich-descriptive-name.jpg`
3. **Alt text** — 120-125 chars, keyword-inclusive, describes the image for screen readers and image search
4. **OG check** — Confirm the image will work at 1200×630 and at thumbnail size
5. **The prompt** — A detailed image generation prompt (200-400 words) that includes:
   - The problem visual (what the customer/merchant is struggling with)
   - The YourApp solution visual (clean, blue, transparent)
   - Lighting/mood/color palette instructions
   - Technical quality tags (e.g., "hyper-detailed, 8k resolution, dramatic lighting")

### Best Option Selection Logic — Pick the Right Style for the Article

Analyze the article's dominant angle and pick **one** style from this table. Don't mix — commit to one:

| If the article is mostly about... | Pick this style |
|----------------------------------|-----------------|
| **Money loss, fees, hidden costs** (urgency/action) | Dramatic 3D — cinematic, red/amber warning tones, problem-focused |
| **Technical setup, configuration, step-by-step** | Clean flat vector / 2.5D isometric — educational, professional |
| **Trust, security, compliance (PCI-DSS)** | Cinematic 3D with shield/security metaphors — authoritative, blue |
| **Customer psychology, abandonment, UX** | Emotional lifestyle (shallow DoF, warm interior) — relatable |
| **Complex concepts (currency flow, data)** | Conceptual isometric — minimalist, infographic-like |
| **Before/after comparison, ROI** | Split-screen X-ray — before (red) vs after (blue) |

### Platform-Specific Parameters

Always append platform-specific parameters to each prompt:
- **Midjourney**: `--ar 16:9 --q 2 --style raw`
- **DALL-E 3**: Specify "16:9 aspect ratio"
- **Stable Diffusion**: Prefix with "professional marketing material, high-end e-commerce ad"

### Pinterest-Specific Optimization (Major Traffic Source)

Pinterest is a visual search engine that can drive blog traffic for years. When generating prompts:
- **Vertical pins (2:3 ratio)** work best on Pinterest — suggest a Pinterest-specific crop of the main image
- **Text overlay on the image** increases saves by 30% — suggest a short, punchy text overlay idea (e.g., "34% of Sales Fail at Checkout")
- **Bright, high-contrast images** perform better on Pinterest than dark/moody ones
- **Before/after comparisons** get 2× more saves than single-scene images

If the user is interested in Pinterest traffic, suggest how the single prompt could be adapted: a vertical crop suggestion and text overlay idea.

---

## 📋 Output Format — Output Everything Directly in the Message

Present the results in this order. **All output must be directly in your response message** for the user to copy. No file writes.

### 1. Posts Needing Images

Briefly list the posts found without images with their slug (so the user can reference which one they want).

### 2. Per-Post: Context Summary

For each post, read the full content with `--full`, then write a **1-2 sentence context summary** showing you understood the article's core message.

### 3. Image Prompt (for each post)

For EACH post, output this exact format in the message:

```
## [Post Title]

*Context: [1-2 sentence summary of the article's core message]*
**Style rationale:** [1 sentence explaining why you picked this style]

### The Prompt

**SEO file name:** `keyword-rich-descriptive-name.jpg`
**Alt text:** [120-125 chars, includes target keyword naturally]
**OG check:** ✅ Works at 1200×630 and thumbnail size — focal point is centered

**Prompt:**
> [single detailed 200-400 word prompt, ready to copy-paste to Midjourney/DALL-E/Stable Diffusion]
```

---

## 🔨 Task Examples

**Example 1: "Check which blog posts need images"**
→ Run the script → list posts → ask user which one to work on

**Example 2: "Generate an image for the XYZ article"**
→ Fetch post by slug with `--full` to read the content → understand the article's message → generate the single best prompt directly in the message

**Example 3: "Make hero images for all blog posts"**
→ Run script → for each post without image, fetch its full content → generate one best prompt per post directly in the message

**Example 4: "The prompts should be in the messages so I can copy them"**
→ This is the default behavior. All prompts are output directly in the response message, clearly formatted with `>` blocks for easy copy-paste to Midjourney/DALL-E/Stable Diffusion

**Example 5: "Generate an image optimized for social sharing and backlinks"**
→ Focus on bold, emotional concepts with strong contrast that work at thumbnail size → include alt text and file name
