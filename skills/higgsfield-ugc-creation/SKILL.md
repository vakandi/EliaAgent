---
name: higgsfield-ugc-creation
description: Create authentic UGC style videos using Higgsfield.ai. ALWAYS enable unlimited mode + visible browser with captcha alerts. BATCH PROCESSING - generate multiple UGC videos in sequence. Use when user wants to (1) create realistic lifestyle content, (2) generate influencer-style videos, (3) produce unboxing/showcase content, (4) make lip-sync videos with voiceovers. Uses agent-browser CLI.
---

# Higgsfield UGC Creation

## ⚠️ ALWAYS CLOSE BROWSER WHEN DONE

```bash
# ✅ ALWAYS close browser when finished
agent-browser close
```

**IMPORTANT:** Always run `agent-browser close` when done to properly release the headed mode session.

---

## ⚠️ CRITICAL: BROWSER MUST BE VISIBLE 👁️

**Use `--headed` AND `--profile` together!**

```bash
# ✅ CORRECT - Visible browser + persists login/cookies
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/lipsync-studio"

# ❌ WRONG - Headless mode, user cannot see/interact
agent-browser open "https://higgsfield.ai/lipsync-studio"
```

**User MUST see the browser to:**
- Monitor generation progress
- **Solve CAPTCHA if it appears** ⭐
- Verify video quality

## KEY: Batch Processing

**DO NOT refresh between generations!**
1. Enable unlimited toggle ONCE
2. Upload avatar → Enter text → Select voice → Generate
3. Wait for result
4. Upload new avatar → Enter new text → Generate
5. Repeat without refreshing

## URLs
- **Lipsync Studio**: https://higgsfield.ai/lipsync-studio
- **UGC Factory**: https://higgsfield.ai/lipsync-studio?ugc-studio=true
- **Create/Edit**: https://higgsfield.ai/create/edit

## Tools
```bash
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/lipsync-studio"
agent-browser snapshot
agent-browser screenshot /path/to/output.png
agent-browser click @eXX
agent-browser type @eXX "text"
```

## UNLIMITED Toggle

**Location:** LAST control on the right, AFTER quantity +/- buttons.

**Enable ONCE, reuse many times:**
1. Select unlimited model
2. Click switch with `aria-checked="false"`
3. Verify `aria-checked="true"`
4. **DO NOT refresh** - just change content and regenerate

## Image Hosting for Upload

**tmpfiles.org API:**
```bash
curl -F "file=@/path/to/avatar.png" https://tmpfiles.org/api/v1/upload
```

## UGC Types

### 1. Lipsync Videos
URL: https://higgsfield.ai/lipsync-studio
- Upload avatar (image/video)
- Enter text script
- Select voice
- Generate

### 2. UGC Factory
URL: https://higgsfield.ai/lipsync-studio?ugc-studio=true
- Authentic UGC style
- Multiple templates
- Brand-ready output

### 3. Lifestyle Video
- Use Seedance 1.5 Pro in Video tab
- Paris/cafe scenes
- Shopping moments

## Bene2Luxe Mascot Character ⚠️

**Mascot Image Path:**
```
/Users/vakandi/Documents/HiggsField.ai-API-Wraper/mascott_bene2luxe.png
```

**⚠️ ERROR HANDLING:**

If user asks to use the mascot in UGC generation, you will see:
```
Cannot read "mascott_bene2luxe.png" (this model does not support image input)
```

**Solution:** Use text prompts to describe mascot lipsync/animation scenes.

**Example prompts for mascot UGC:**
- "The mascot character lipsyncing to luxury fashion narration"
- "Animated Bene2Luxe mascot in a Paris boutique, luxury vibes"
- "Cartoon mascot showing off designer bags, fun UGC style"

**Never try to inject the mascot image as input.**

## Voice Options

### Installed Custom Voice:
- **ArabicFemaleFR1-Marwa** - French/Arabic (user installed)

### Built-in:
- Various English/French voices
- Character voices

## Batch Workflow: Lipsync

```bash
# 1. Open Lipsync Studio (visible + persists cookies)
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/lipsync-studio"
sleep 3

# 2. Enable unlimited (ONE TIME)
agent-browser click @unlimited_switch
sleep 1

# 3. Select voice (ONE TIME)
agent-browser click @voice_dropdown
agent-browser type @voice_dropdown "Marwa"
agent-browser click @arabic_female_marwa
sleep 1

# 4. Generate UGC 1
# Upload avatar
curl -F "file=@avatar1.png" https://tmpfiles.org/api/v1/upload
# Use JS to inject...

agent-browser type @text_field "French hook text 1"
agent-browser click @generate_button
echo "Generated UGC 1"

# 5. Generate UGC 2 (NO REFRESH!)
curl -F "file=@avatar2.png" https://tmpfiles.org/api/v1/upload
# Use JS to inject...

agent-browser type @text_field "French hook text 2"
agent-browser click @generate_button
echo "Generated UGC 2"

# 6. Repeat for more UGC videos...
```

## JavaScript Avatar Injection

```javascript
// Upload to tmpfiles.org first, then:
const avatarUrl = "https://tmpfiles.org/xxx/avatar.png";
const fileInput = document.querySelector('input[type="file"]');
const blob = await fetch(avatarUrl).then(r => r.blob());
const file = new File([blob], 'avatar.png', {type: 'image/png'});
const dt = new DataTransfer();
dt.items.add(file);
fileInput.files = dt.files;
fileInput.dispatchEvent(new Event('change', {bubbles: true}));
```

## Model Selection for UGC

| Style | Model | URL/Method |
|--------|-------|-------------|
| Lifestyle | Seedance 1.5 Pro | Video tab |
| Unboxing | Wan 2.2 | Video tab |
| POV | DoP Lite | Video tab |
| Lipsync | Built-in | Lipsync Studio |
| UGC Factory | Built-in | ?ugc-studio=true |

## CAPTCHA HANDLING ⭐ CRITICAL

**IMPORTANT:** Higgsfield WILL show CAPTCHA after clicking Generate for UGC videos.

### When CAPTCHA appears, you MUST:

1. **Play alert sound:**
```bash
python3 -c "import os; [os.system('printf \"\\a\" * 3)' for _ in range(1)]" 2>/dev/null || echo -e "\a\a\a"
```

2. **Speak to user:**
```bash
elia-speak -e "Captcha detected! Please fill the captcha in the browser window, then I'll continue."
```

3. **Wait for user to solve:**
```bash
sleep 10
```

4. **After captcha solved, RE-CLICK Generate:**
```bash
agent-browser click @generate_button
```

### Full Captcha Alert Script:
```bash
# Check if captcha appeared
if agent-browser snapshot | grep -qi "captcha\|verification\|verify"; then
    echo -e "\a\a\a"  # Beep beep
    elia-speak -e "Captcha detected! Please fill the captcha in the browser window, then I'll continue."
    echo "Waiting for user to solve captcha..."
    sleep 10  # Give user time to solve
    # Re-click Generate after solving
    agent-browser click @generate_button
fi
```

### After Captcha Resolution:

```bash
# Wait for page load
sleep 3

# Wait for generation (lipsync takes time)
sleep 60

# Check Downloads
ls -lath ~/Downloads/hf_*.mp4
```

## Tips
- **NO REFRESH** between generations
- Select voice ONCE, reuse for all videos
- Use ArabicFemaleFR1-Marwa for French/Arabic content
- Take screenshot after batch complete
- **After captcha, RE-CLICK Generate to trigger UGC creation**

---

## DOWNLOADING UGC VIDEOS

### Where Downloads Go
- Files save to `~/Downloads/` (not configurable)
- Filename pattern: `hf_[YYYYMMDD]_[HHMMSS]_[UUID].mp4`

### Method: Bulk Download from Assets Folder

**Steps:**
1. Navigate to: `https://higgsfield.ai/assets`
2. Click on your project folder
3. Select UGC videos using checkboxes
4. Click "Download" button
5. Files save to `~/Downloads/`

**HTML Structure for Video Assets:**
```html
<!-- Video in folder (inside <figure>) -->
<figure>
  <Video/>
  <button/>  <!-- play/overlay button -->
  <LabelText>
    <checkbox [checked=true/false]/>  <!-- selection checkbox -->
  </LabelText>
</figure>
```

### Checking Downloaded Files

```bash
# List recent UGC downloads
ls -lath ~/Downloads/hf_*.mp4 | head -10

# Copy to project folder
cp ~/Downloads/hf_*.mp4 /path/to/project/
```

---

## Tips
- **NO REFRESH** between generations
- Select voice ONCE, reuse for all videos
- Use ArabicFemaleFR1-Marwa for French/Arabic content
- Take screenshot after batch complete
- **Download from Assets page** - select checkboxes, click Download
- Files save to `~/Downloads/` automatically with UUID in filename
