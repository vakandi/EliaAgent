---
name: higgsfield-video-editing
description: Edit and enhance videos using Higgsfield.ai editing tools. ALWAYS enable unlimited mode + visible browser with captcha alerts. BATCH PROCESSING - edit multiple videos in sequence. Use when user wants to (1) extend video duration, (2) add effects, (3) loop videos, (4) enhance quality, (5) add subtitles. Uses agent-browser CLI.
---

# Higgsfield Video Editing

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
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/create/edit"

# ❌ WRONG - Headless mode, user cannot see/interact
agent-browser open "https://higgsfield.ai/create/edit"
```

**User MUST see the browser to:**
- Monitor edit progress
- **Solve CAPTCHA if it appears** ⭐
- Verify output quality

## KEY: Batch Processing

**DO NOT refresh between edits!**
1. Enable unlimited toggle ONCE
2. Upload video → Select edit mode → Apply
3. Wait for result
4. Upload new video → Apply
5. Repeat without refreshing

## URLs
- **Edit/Create**: https://higgsfield.ai/create/edit
- **Cinema Studio**: https://higgsfield.ai/cinema-studio

## Tools
```bash
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/create/edit"
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
4. **DO NOT refresh** - just upload new video and edit

## Image Hosting for Upload

**tmpfiles.org API:**
```bash
curl -F "file=@/path/to/video.mp4" https://tmpfiles.org/api/v1/upload
```

## Edit Modes

| Mode | Function | Model |
|------|----------|-------|
| Extend | Add duration | Seedance |
| Loop | Make seamless | Any |
| Enhance | Upscale quality | Pro models |
| Subtitles | Add text overlay | Auto |
| Crop | Change aspect | All |

## Bene2Luxe Mascot Character ⚠️

**Mascot Image Path:**
```
/Users/vakandi/Documents/HiggsField.ai-API-Wraper/mascott_bene2luxe.png
```

**⚠️ ERROR HANDLING:**

If user asks to use the mascot, you will see:
```
Cannot read "mascott_bene2luxe.png" (this model does not support image input)
```

**Solution:** Use text prompts to describe mascot scenes instead.

## Batch Workflow

```bash
# 1. Open edit page (visible + persists cookies)
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/create/edit"
sleep 3

# 2. Enable unlimited (ONE TIME)
agent-browser click @unlimited_switch
sleep 1

# 3. Edit video 1
# Upload video via drag-drop or file input
agent-browser click @upload_zone
# Select video file...

agent-browser click @edit_mode_dropdown
agent-browser click @extend_mode
agent-browser click @apply_button
echo "Edited video 1"

# 4. Edit video 2 (NO REFRESH!)
agent-browser click @upload_zone
# Select new video...

agent-browser click @edit_mode_dropdown
agent-browser click @loop_mode
agent-browser click @apply_button
echo "Edited video 2"

# 5. Continue for more videos...
```

## CAPTCHA HANDLING ⭐ CRITICAL

**IMPORTANT:** Higgsfield WILL show CAPTCHA after clicking Apply/Edit button.

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

4. **After captcha solved, RE-CLICK Apply:**
```bash
agent-browser click @apply_button
```

### Full Captcha Alert Script:
```bash
# Check if captcha appeared
if agent-browser snapshot | grep -qi "captcha\|verification\|verify"; then
    echo -e "\a\a\a"  # Beep beep
    elia-speak -e "Captcha detected! Please fill the captcha in the browser window, then I'll continue."
    echo "Waiting for user to solve captcha..."
    sleep 10  # Give user time to solve
    # Re-click Apply after solving
    agent-browser click @apply_button
fi
```

### After Captcha Resolution:

```bash
# Wait for page load
sleep 3

# Wait for edit to complete
sleep 60

# Check Downloads
ls -lath ~/Downloads/hf_*.mp4
```

## Tips
- **NO REFRESH** between edits
- Always enable unlimited toggle for free models
- Take screenshot after batch complete
- **After captcha, RE-CLICK Apply to trigger edit**

---

## DOWNLOADING VIDEOS

### Where Downloads Go
- Files save to `~/Downloads/` (not configurable)
- Filename pattern: `hf_[YYYYMMDD]_[HHMMSS]_[UUID].mp4`

### Method: Bulk Download from Assets Folder

**Steps:**
1. Navigate to: `https://higgsfield.ai/assets`
2. Click on your project folder
3. Select edited videos using checkboxes
4. Click "Download" button
5. Files save to `~/Downloads/`

### Checking Downloaded Files

```bash
# List recent video downloads
ls -lath ~/Downloads/hf_*.mp4 | head -10

# Copy to project folder
cp ~/Downloads/hf_*.mp4 /path/to/project/
```

---

## Tips
- **NO REFRESH** between edits
- Always enable unlimited toggle for free models
- Take screenshot after batch complete
- **Download from Assets page** - select checkboxes, click Download
- Files save to `~/Downloads/` automatically with UUID in filename
