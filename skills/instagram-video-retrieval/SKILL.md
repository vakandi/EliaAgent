---
name: instagram-video-retrieval
description: "Retrieve and analyze video content from Instagram saved posts. Also includes French influencer content collection (Nasdas, Tounsi, Samos). Use when: (1) Access saved videos from Instagram account, (2) Extract video transcripts from audio using Whisper, (3) Get post descriptions, captions, and account bios, (4) Analyze video content for business insights, (5) Process Instagram videos for content repurposing, (6) Download influencer promotional videos. Account:monsieur.brillant, URL: https://www.instagram.com/monsieur.brillant/saved/all-posts/. French Influencer Content: /tmp/influencer_videos/nasdas/ (14 videos, 983MB). Triggers: Instagram saved videos, extract video transcript, Instagram video data, Instagram content analysis, French influencer videos, Nasdas content, Tounsi content, Samos content."
---

# Instagram Video Retrieval Skill

Access and analyze video content from Instagram saved posts with full transcript extraction. **Updated 2026-03-30** with French influencer content collection.

## ✅ Verified Working Approach (2026-03-30)

**Workflow:**
1. Navigate to saved posts page with Playwright
2. Extract post URLs via JavaScript (scroll and collect)
3. Download videos with yt-dlp
4. Transcribe with Whisper (AUTO LANGUAGE DETECTION - critical!)
5. Filter content (skip food, process business)

**Key Tools:**
- `yt-dlp` - Downloads Instagram videos ✅ VERIFIED
- `whisper` - Transcribes video audio ✅ VERIFIED
- Playwright - Navigates and extracts URLs ✅ VERIFIED

**⚠️ CRITICAL: Auto Language Detection**
- Wael's saved videos are mostly ENGLISH
- NEVER hardcode `--language French`
- Always use `--task transcribe` without `--language` flag
- Whisper auto-detects language correctly

## Account Configuration

**Primary Account**: `monsieur.brillant`
**Saved Posts URL**: https://www.instagram.com/monsieur.brillant/saved/all-posts/
**Browser Profile**: `~/.agent-browser-profile`

## Core Tools

### 1. Playwright (via skill_mcp - For Instagram navigation)

**Extract post URLs from saved page:**
```javascript
skill_mcp(mcp_name="playwright", tool_name="browser_evaluate", arguments={
  "function": "() => { const links = document.querySelectorAll('article a[href*=\"/p/\"], article a[href*=\"/reel/\"]'); return Array.from(links).slice(0, 20).map(a => a.href); }"
})
```

**Extract post metadata:**
```javascript
skill_mcp(mcp_name="playwright", tool_name="browser_evaluate", arguments={
  "function": "() => { const metaTags = document.querySelectorAll('meta[property*=\"og:\"]'); const ogData = {}; metaTags.forEach(m => { ogData[m.getAttribute('property')] = m.getAttribute('content'); }); return ogData; }"
})
```

### 2. yt-dlp (For video downloading) - VERIFIED WORKING ✅

```bash
# Get video URL (prints download URLs)
yt-dlp --get-url "https://www.instagram.com/reel/DWTJua8jvkG/"

# Download video (merges video + audio automatically)
yt-dlp -o "/tmp/instagram_videos/%(id)s.%(ext)s" "https://www.instagram.com/reel/DWTJua8jvkG/"
```

### 3. Whisper (For video transcription) - AUTO LANGUAGE DETECTION

```bash
# ⚠️ CRITICAL: ALWAYS use auto-detection, NOT hardcoded language!
# Instagram videos can be in English, French, Arabic, etc.

# Auto-detect language (RECOMMENDED)
whisper /tmp/video.mp4 --model large-v3 --task transcribe --output_dir /tmp/videos --verbose False

# Alternative: Specify multiple languages if known
whisper /tmp/video.mp4 --model large-v3 --language en,fr --task transcribe --verbose False

# Model recommendations:
# - large-v3: Best accuracy (default)
# - medium: Faster, still good quality
# - small: Quick tests only
```

**Language Detection Priority:**
1. First try: Auto-detect (no --language flag)
2. If content is known to be EN/FR mix: `--language en,fr`
3. Never hardcode single language unless you're 100% sure

### 4. agent-browser (Alternative navigation)

```bash
PROFILE="--profile ~/.agent-browser-profile"

# Navigate to saved posts
agent-browser $PROFILE open https://www.instagram.com/monsieur.brillant/saved/all-posts/
agent-browser $PROFILE wait --load networkidle
agent-browser $PROFILE snapshot
```

## Workflow: Retrieve Instagram Saved Videos

### Step 1: Navigate to Saved Posts

```bash
# Open Instagram saved posts page
agent-browser $PROFILE open https://www.instagram.com/monsieur.brillant/saved/all-posts/
agent-browser $PROFILE wait --load networkidle
agent-browser $PROFILE wait --seconds 3  # Allow JS to fully render
agent-browser $PROFILE snapshot
```

### Step 2: Identify Video Posts

Look for these patterns in snapshot:
- **Video indicator**: "Video" badge, play button overlay
- **Post container**: `_aao7` class for posts
- **Video thumbnail**: `img` elements with video-like context
- **Link pattern**: `/p/` or `/reel/` URLs in href attributes

Extract video post URLs from the snapshot output.

### Step 3: Navigate to Individual Video

```bash
# Click on a video post to open it
agent-browser $PROFILE open "https://www.instagram.com/p/{POST_ID}/"
agent-browser $PROFILE wait --load networkidle
agent-browser $PROFILE wait --seconds 2
agent-browser $PROFILE snapshot
```

### Step 4: Extract Post Data

From the snapshot, extract:
- **Caption/Description**: Look for text content in post
- **Account info**: Username, display name, bio (if visible)
- **Post metadata**: Timestamp, likes, comments count
- **Hashtags/Mentions**: Extract `#tag` and `@mention` patterns

### Step 5: Download Video (for transcript)

```bash
# Get video URL from page or network requests
# Then download using yt-dlp
yt-dlp --write-auto-sub --sub-lang fr,en "https://www.instagram.com/p/{POST_ID}/"
```

### Step 6: Transcribe Video

```bash
# Download video first
VIDEO_PATH="/tmp/instagram_video.mp4"
yt-dlp -o "$VIDEO_PATH" "VIDEO_URL"

# Transcribe with Whisper (French audio expected)
whisper "$VIDEO_PATH" --model large-v3 --language French --task transcribe
```

### Step 7: Content Filtering (Skip Non-Business)

**SKIP videos that are:**
- Food/cooking content (check thumbnail, caption keywords: "recipe", "food", "cuisine", "meal", "dinner", "lunch", "breakfast")
- Personal/family content
- Entertainment without business relevance

**PROCESS videos that are:**
- Business tips/strategy
- Marketing/sales content
- Entrepreneurship insights
- Educational content
- Product/service showcases

**Decision process:**
1. Look at video thumbnail first (before clicking)
2. Check caption text for keywords
3. Check account bio for business context
4. Skip if unclear → report to user

## Data Extraction Template

For each video, collect:

```markdown
## Video #[N]
**URL**: https://www.instagram.com/p/{POST_ID}/
**Posted by**: @username
**Account Bio**: [extracted bio text]

### Content Preview
[Caption/description text]

### Keywords Detected
- [Keyword 1]
- [Keyword 2]

### Decision
- [ ] **PROCESS** - Business content (explain why)
- [x] **SKIP** - Reason: [food/personal/etc.]

### Transcript (if PROCESSED)
[Full transcription from Whisper]
```

## Verified Selectors for Instagram

### Saved Posts Page
```css
/* Post containers */
article._aao7
div._aagw

/* Video indicators */
span[aria-label="Video"]
div._ab8s

/* Links to posts */
article a[href*="/p/"]
article a[href*="/reel/"]

/* Grid layout */
div._aagw > div
```

### Single Post Page
```css
/* Caption text */
div._a9zs span
h1._ap3a

/* Account info */
header a.x1i10hfl
span.x1lliihq

/* Video element */
video.x1lliihq

/* Meta info */
section span

/* Bio (in profile) */
span._ap3a
```

## Common Patterns

### Extract Video URL from Network
```bash
# Intercept network requests to find video source
agent-browser $PROFILE open "POST_URL"
agent-browser $PROFILE network-requests
# Look for .mp4 URLs in the requests
```

### Scroll to Load More Posts
```bash
# Instagram loads posts on scroll
agent-browser $PROFILE scroll down
agent-browser $PROFILE wait --seconds 2
agent-browser $PROFILE snapshot
```

### Handle Login State
```bash
# If redirected to login, need browser with saved session
# Check current URL
agent-browser $PROFILE get url

# If login page, inform user to authenticate first
```

## Instagram URL Patterns

| Content Type | URL Pattern | Example |
|-------------|------------|---------|
| Saved posts | `/saved/all-posts/` | `/saved/all-posts/` |
| Single post | `/p/{POST_ID}/` | `/p/Abc123DEF/` |
| Reel | `/reel/{POST_ID}/` | `/reel/Abc123DEF/` |
| Profile | `/{username}/` | `/monsieur.brillant/` |

## Troubleshooting

### Login Required
```
Error: Redirected to /accounts/login/
Solution: User must be logged into Instagram in the agent-browser profile
Action: Ask Wael to open Instagram and log in manually first
```

### Video Not Loading
```
Issue: Video element exists but no src
Solution: Check if video is age-restricted or private
Action: Skip the video, report to user
```

### yt-dlp Download Fails
```
Error: "This video is unavailable"
Common causes:
- Video was deleted
- Account is private
- Regional restriction
Solution: Skip the video
```

### Whisper Transcription Fails
```
Issue: Audio unclear or silent video
Solution: Check video has audio track
Action: Note "No audio detected" in output
```

## Report Format

When processing is complete, present results:

```markdown
# Instagram Video Retrieval Report
**Account**: @monsieur.brillant
**Date**: [CURRENT_DATE]
**Videos Found**: [N]
**Processed**: [M]
**Skipped**: [K]

## Processed Videos (Business Content)

### 1. [Video Title/Description snippet]
- **URL**: [link]
- **Posted by**: @[username]
- **Bio**: [account bio]
- **Keywords**: [relevant keywords]
- **Transcript**: [full transcript]

---

## Skipped Videos

| # | URL | Reason |
|---|-----|--------|
| 1 | [link] | Food content |
| 2 | [link] | Personal post |
```

## Tips

1. **Check Before Processing**: Always preview video content before downloading/transcribing
2. **Prioritize Business Content**: Focus on entrepreneurship, marketing, sales content
3. **French Language**: Assume French audio unless indicated otherwise
4. **Report Each Skip**: Document why each video was skipped for user review
5. **Respect Rate Limits**: Wait 2-3 seconds between page navigations
6. **Handle Errors Gracefully**: Skip problematic videos and continue with next

---

# French Influencer Content Collection (Nasdas, Tounsi, Samos)

**Date Added**: 2026-03-30
**Total Videos Downloaded**: 14 videos (~983MB)
**Storage Location**: `/tmp/influencer_videos/nasdas/`

## Influencer Profiles

### 1. NASDAS (@nasdas_officiel)
- **Full Name**: Nasser Sari
- **Origin**: Perpignan, France (Saint-Jacques quarter)
- **Born**: June 3, 1996
- **Platform**: Snapchat #1 in France, Instagram, TikTok, YouTube
- **Team**: Team Nasdas (includes Samos, Tounsi)
- **Key Partnerships**: Chamas Tacos, La Maison des Sultans, The Platinum Barber (with Ninho)
- **Notable**: Auditioned at French National Assembly about TikTok (June 2025)

### 2. TOUNSI (@mehditounsi__)
- **Full Name**: Mehdi Tounsi
- **Origin**: Tunisia/France
- **Platform**: Instagram, Snapchat
- **Niche**: Business/entrepreneurship training, professional development
- **Key Focus**: Training organization creation, business development

### 3. SAMOS (@samosofficiell)
- **Full Name**: Samir
- **Origin**: Perpignan, France
- **Platform**: Snapchat (main), Instagram
- **Team**: Team Nasdas member
- **Niche**: Lifestyle influencer

---

## Downloaded Videos Collection

### Instagram Videos (from @nasdas_officiel and related accounts)

| Video ID | Source | Content | Promotional/Brand | Local File |
|----------|--------|---------|-------------------|------------|
| DV5yEyTsLjb | Instagram | Nasdas + Jeremstar immersion video | Media collaboration | DV5yEyTsLjb.mp4 (16.6MB) |
| CwSnerhhWHv | Instagram | Team NASDAS at Restaurant Le Nautile | Restaurant Le Nautile | CwSnerhhWHv.mp4 (11.6MB) |
| DA86-XaIFqK | Instagram | NASDAS & NINHO - The Platinum Barber opening | Barber shop partnership | DA86-XaIFqK.mp4 (3.8MB) |
| DHlF43ysyXv | Instagram | Restaurant Mevlana thanks Nasdas | Restaurant Mevlana | DHlF43ysyXv.mp4 (583KB) |
| DUjAxSBCPa7 | Instagram | Nasdas announces return to Snapchat | Personal/comeback | DUjAxSBCPa7.mp4 (14.3MB) |
| DClyQpdM1sE | Instagram | Samos ramène Mouna au resto | Restaurant content | DClyQpdM1sE.mp4 (4.8MB) |
| Cwhd0raoI9C | Instagram | Team Nasdas validated restaurant | Restaurant La Bonne Adresse | Cwhd0raoI9C.mp4 (6.0MB) |

### TikTok Videos (related to Nasdas/Team Nasdas)

| Video ID | Source | Content | Promotional/Brand | Local File |
|----------|--------|---------|-------------------|------------|
| 7528200758286617878 | TikTok | Promotion -50% restaurant Nasdas | Nasdas Restaurant promo | 7528200758286617878.mp4 (698KB) |
| 7617152078082755856 | TikTok | Team Nasdas content | Team Nasdas | 7617152078082755856.mp4 (6.8MB) |
| 7482844472053730582 | TikTok | Nasdas lifestyle #nasdas #lachiennete | Personal content | 7482844472053730582.mp4 (9.2MB) |
| 7588511774501244162 | TikTok | Sensas Toulouse restaurant | Sensas Toulouse | 7588511774501244162.mp4 (375KB) |
| 7472097211417906454 | TikTok | Nasdas loves Cava Smasher burgers | Cava Smasher | 7472097211417906454.mp4 (3.8MB) |
| 7584760512823446806 | TikTok | Luxelite Meubles - Nasdas promo | Luxelite Meubles | 7584760512823446806.mp4 (2.5MB) |

### YouTube Videos

| Video ID | Source | Content | Promotional/Brand | Local File |
|----------|--------|---------|-------------------|------------|
| XTPrX4YSuNA | YouTube | Jeremstar - Immersion chez les Algériens et Gitans avec Nasdas | Media collaboration | (in progress - 983MB) |
| 4HABh5dU938 | YouTube Short | 48H avec Nasdas - Jeremstar | Media collaboration | 4HABh5dU938.webm (7.0MB) |

---

## Video Details by Category

### 🍔 Restaurant/Food Promotion Videos
1. **Restaurant Le Nautile** - Team NASDAS video
   - URL: https://www.instagram.com/reel/CwSnerhhWHv/
   - Hashtags: #nasdas #lachienneté #teamnasdas #samos
   - Posted by: @restaurant_le_nautile

2. **Sensas Toulouse** - Restaurant mention
   - URL: https://www.tiktok.com/@sensas_toulouse/video/7588511774501244162
   - Context: Nasdas/Chienneté content

3. **La Bonne Adresse** - Team Nasdas validated
   - URL: https://www.instagram.com/reel/Cwhd0raoI9C/
   - Hashtags: #labonneadresse #teamnasdas #tounsi

4. **Restaurant Mevlana** - Thanks Nasdas
   - URL: https://www.instagram.com/reel/DHlF43ysyXv/
   - Posted by: @restaurant_mevlana_63

5. **Cava Smasher** - Nasdas loves their burgers
   - URL: https://www.tiktok.com/@cava_smasher/video/7472097211417906454
   - Hashtags: #cavasmasher

6. **Nasdas Restaurant promo** - -50% discount
   - URL: https://www.tiktok.com/@laclasseadallasbaba/video/7528200758286617878

### 💇 Business/Partnership Videos
1. **The Platinum Barber** - Opening with Ninho
   - URL: https://www.instagram.com/nasdas_officiel/reel/DA86-XaIFqK/
   - Collaboration: Nasdas + Ninho (rapper)
   - Location: 2 avenue Marcelin Albert, 66000 Perpignan
   - Date: Saturday October 12 (opening)

2. **Chamas Tacos Partnership** - Official partnership
   - Article: https://www.toute-la-franchise.com/news-chamas-tacos-s-associe-a-nasdas-un-partenariat-strategique-pour-booster-la-marque
   - Nasdas: #1 influencer on Snapchat France

3. **Luxelite Meubles** - Furniture promo
   - URL: https://www.tiktok.com/@luxelitemeubles/video/7584760512823446806

### 🎬 Media/Collaboration Videos
1. **Jeremstar x Nasdas** - Immersion video
   - URL: https://www.instagram.com/reel/DV5yEyTsLjb/
   - Hashtags: #JeremstarNasdas
   - Channel: JEREMSTAR YouTube (1.1M views)

2. **48H avec Nasdas** - Jeremstar short
   - URL: https://www.youtube.com/shorts/4HABh5dU938
   - Duration: 1:20

3. **Nasdas return announcement**
   - URL: https://www.instagram.com/reel/DUjAxSBCPa7/
   - Posted by: @instant_actu

### 👥 Team Nasdas Content
1. **Samos taking Mouna to restaurant**
   - URL: https://www.instagram.com/nasdas_familly/reel/DClyQpdM1sE/
   - Hashtags: #nasdas #nasdasofficiel #humour

2. **Team Nasdas heart content**
   - URL: https://www.tiktok.com/@nasdas414/video/7617152078082755856

---

## Download Commands Reference

```bash
# Create directories
mkdir -p /tmp/influencer_videos/nasdas /tmp/influencer_videos/tounsi /tmp/influencer_videos/samos

# Download Instagram reels
yt-dlp -o "/tmp/influencer_videos/nasdas/%(id)s.%(ext)s" "https://www.instagram.com/reel/DV5yEyTsLjb/"

# Download TikTok videos
yt-dlp -o "/tmp/influencer_videos/nasdas/%(id)s.%(ext)s" "https://www.tiktok.com/@laclasseadallasbaba/video/7528200758286617878"

# Download YouTube videos
yt-dlp -o "/tmp/influencer_videos/nasdas/%(id)s.%(ext)s" "https://www.youtube.com/watch?v=XTPrX4YSuNA"

# List all downloaded files
ls -la /tmp/influencer_videos/nasdas/
```

---

## Key Resources & Links

### Official Accounts
- **Nasdas Instagram**: https://www.instagram.com/nasdas_officiel/
- **Nasdas TikTok**: https://www.tiktok.com/@nasdasavant
- **Samos Snapchat**: https://www.snapchat.com/@samos-6633
- **Samos Snapchat 2**: https://www.snapchat.com/@samosofficiell

### Articles & Press
- **Le Parisien**: "Milliers d'euros par jour, restaurant parisien et téléréalité : comment Nasdas a bâti son empire" (2025-04-16)
- **Le Monde**: "Dans les pas de Nasdas, l'influenceur turbulent qui a changé la chienneté en or" (2025-04-13)
- **Chamas Tacos Partnership**: https://www.toute-la-franchise.com/news-chamas-tacos-s-associe-a-nasdas-un-partenariat-strategique-pour-booster-la-marque
- **Jeremstar Perpignan Article**: https://madeinperpignan.com/perpignan-snapchat-visite-jeremstar-nasdas/

### YouTube Channels
- **JEREMSTAR**: https://www.youtube.com/watch?v=XTPrX4YSuNA (En immersion chez les Algériens et Gitans avec Nasdas - 1M+ views)
