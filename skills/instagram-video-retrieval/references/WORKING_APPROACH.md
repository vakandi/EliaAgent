# Instagram Video Extraction - Working Approach

## Verified Working Workflow (2026-03-26)

### Step 1: Extract Post URLs from Saved Page

Use JavaScript to extract post URLs:
```javascript
document.querySelectorAll('article a[href*="/p/"], article a[href*="/reel/"]')
```

Returns URLs like:
- `https://www.instagram.com/p/DWTJua8jvkG/`
- `https://www.instagram.com/reel/DWT8w0mALux/`

### Step 2: Download Video with yt-dlp

```bash
# Get video URL (prints download URLs)
yt-dlp --get-url "https://www.instagram.com/reel/DWTJua8jvkG/"

# Download video (merges video + audio)
yt-dlp -o "/tmp/instagram_videos/%(id)s.%(ext)s" "https://www.instagram.com/reel/DWTJua8jvkG/"
```

**Output files:**
- `/tmp/instagram_videos/DWTJua8jvkG.mp4` (merged video+audio)
- `/tmp/instagram_videos/DWTJua8jvkG.txt` (transcript if Whisper is used)

### Step 3: Transcribe with Whisper - AUTO LANGUAGE DETECTION

```bash
# ⚠️ CRITICAL: NEVER hardcode French!
# Wael's saved videos are mostly ENGLISH

# Auto-detect language (ALWAYS USE THIS)
whisper /tmp/instagram_videos/XXXXX.mp4 \
  --model large-v3 \
  --task transcribe \
  --output_dir /tmp/instagram_videos \
  --verbose False

# For EN+FR mixed content:
whisper /tmp/video.mp4 --model large-v3 --language en,fr --verbose False

# Model recommendations:
| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| large-v3 | Slowest | Best | Default for production |
| medium | Medium | High | If large-v3 is too slow |
| small | Fast | Good | Quick tests |

### Step 4: Extract Account/Bio Info

Navigate to the post page and extract from meta tags:
```javascript
const ogData = {};
document.querySelectorAll('meta[property*="og:"]').forEach(m => {
  ogData[m.getAttribute('property')] = m.getAttribute('content');
});
// Returns: og:title, og:description, og:url, og:image
```

## Content Filtering

### SKIP (Food/Personal):
- Keywords: recipe, food, cuisine, meal, dinner, lunch, breakfast, ingredients, cook, baking, chef
- Examples from @monsieur.brillant saved:
  - "Nouilles sautés 10min..." - food recipe
  - "Crispy rice chicken salad" - food
  - "Dubai chocolate" - food

### PROCESS (Business/Content):
- Keywords: sales, marketing, business, ai, tech, coding, startup, entrepreneurship, automation
- Examples:
  - "Sales psychology 101 #sales"
  - "Claw3D first release..."
  - "Activepieces - MIT license"

## Batch Processing Script

See `scripts/batch_process.js` for automated batch processing.

## Troubleshooting

### yt-dlp fails with "Login required"
- Instagram requires authentication for some content
- Ensure browser has active session

### Whisper returns minimal transcript
- Video might have mostly music/audio
- Check video has speech content
- Try different Whisper model

### Video URL is blob:https://
- Video loaded via JavaScript
- Use yt-dlp which handles this automatically

## Example Output

```json
{
  "post_id": "DWTJua8jvkG",
  "url": "https://www.instagram.com/reel/DWTJua8jvkG/",
  "username": "byeloya",
  "caption": "comment \"LYRC\" and i'll send u a code for 50% off",
  "likes": 37,
  "comments": 13,
  "posted_at": "20 hours ago",
  "video_path": "/tmp/instagram_videos/DWTJua8jvkG.mp4",
  "transcript": "c'est",
  "decision": "SKIP - Music promotion content, minimal speech"
}
```
