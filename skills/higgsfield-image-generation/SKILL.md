---
name: higgsfield-image-generation
description: Generate images using Higgsfield.ai free/unlimited models via agent-browser. CRITICAL: Use --profile for visible browser. Clear 'hf:image-form-upd' to reset prompt. Triggers: "generate image", "create frame", "product photo". Uses agent-browser CLI with visible mode + captcha alert system.
---

# Higgsfield Image Generation - QUICK START

**MUST DO THESE STEPS IN ORDER:**

```
1. Open page:
   agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/image/soul"
   sleep 3

2. Clear prompt field:
   agent-browser eval "localStorage.removeItem('hf:image-form-upd'); location.reload()"
   sleep 3

3. Enable unlimited toggle:
   agent-browser eval "document.querySelector('[role=\"switch\"]').click()"

4. Click on textbox:
   agent-browser find text "Upload image" click

5. Type prompt:
   agent-browser eval 'document.execCommand("insertText", false, "YOUR PROMPT HERE")'

6. VERIFY: Take screenshot to confirm text appears in textbox!
   agent-browser screenshot

7. Click Generate button:
   agent-browser find text "Unlimited" click
```

**CRITICAL NOTES:**
- Button says "Unlimited" not "Generate" - use: `agent-browser find text "Unlimited" click`
- MUST take screenshot AFTER typing to verify prompt is visible
- If prompt not visible, try step 4+5 again
- The textbox is tricky - click "Upload image" text first, then use eval to insert text

---

# Full Documentation

## ⚠️ ALWAYS CLOSE BROWSER WHEN DONE

```bash
# ✅ ALWAYS close browser when finished
agent-browser close
```

**IMPORTANT:** Always run `agent-browser close` when done to properly release the headed mode session.

---

## ⚠️ CRITICAL RULES

1. **Use `--profile` for VISIBLE browser** - User MUST see the browser
2. **Use direct URLs** to select unlimited models
3. **Always enable the unlimited toggle**
4. **Clear 'hf:image-form-upd'** before each generation
5. **ALERT user with beep + speak when captcha appears** ⭐

---

## BROWSER MODE: ALWAYS VISIBLE 👁️

**CRITICAL: Use `--headed` AND `--profile` together!**

```bash
# ✅ CORRECT - Visible browser + persists login/cookies
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/image/soul"

# ❌ WRONG - Headless mode, user cannot see/interact
agent-browser open "https://higgsfield.ai/image/soul"

# ❌ WRONG - Two separate commands don't work
agent-browser --profile ~/.agent-browser-profile open "..."
agent-browser --headed open "..."
```

**User MUST see the browser to:**
- Monitor generation progress
- **Solve CAPTCHA if it appears** ⭐
- Verify output quality

---

## UNLIMITED MODEL URLs

| Model | URL | Best For |
|-------|-----|----------|
| **Seedream** | `https://higgsfield.ai/image/seedream` | Visual reasoning |
| **Higgsfield Soul** | `https://higgsfield.ai/image/soul` | Fashion visuals |
| **Z-Image** | `https://higgsfield.ai/image/z-image` | Portraits |
| **Kling O1** | `https://higgsfield.ai/image/kling-o1-image` | Photorealistic |
| **FLUX.2 Pro** | `https://higgsfield.ai/image/flux_2` | Detail work |

---

## ⚠️ IMPORTANT: USE TEXT-BASED COMMANDS ONLY

**NEVER use @ref=X - these IDs change every page load!**

**ALWAYS use these commands:**
- ✅ `agent-browser find text "ButtonLabel" click`
- ✅ `agent-browser eval "document.querySelectorAll('[role=\"textbox\"]')[0].innerText = 'your prompt here'"`
- ❌ `agent-browser fill --name` - DOESN'T WORK
- ❌ `agent-browser click @ref=X` - NEVER THIS

---

## HIGGSFIELD SOUL - COMPLETE UI REFERENCE

The Higgsfield Soul model (`https://higgsfield.ai/image/soul`) has these UI elements:

| Element | How to Interact |
|---------|-----------------|
| **Text Prompt** | `agent-browser eval "document.querySelectorAll('[role=\"textbox\"]')[0].innerText = 'your prompt'"` |
| **Unlimited Toggle** | `agent-browser eval "document.querySelector('[role=\"switch\"]').click()"` |
| **CHARACTER Button** | `agent-browser find text "CHARACTER" click` |
| **Generate Button** | `agent-browser find text "Generate" click` |

### Character Selection (Optional)
1. Click CHARACTER button: `agent-browser find text "CHARACTER" click`
2. Click "All" tab: `agent-browser find text "All" click`
3. Select your character from the list - use: `agent-browser find text "CharacterName" click`
4. If no character needed, close popup by clicking anywhere outside or reload page

### Style Selection (Optional)
1. Click "GENERAL" link: `agent-browser find text "GENERAL" click`
2. Browse available styles and click to select

### Upload Image as Input (Optional)
1. Click the upload button (image icon next to textbox)
2. Use file input or drag & drop

---

## WORKFLOW (Higgsfield Soul) - DO EXACTLY IN ORDER

### STEP 1: Open the page
```bash
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/image/soul"
sleep 3
```

### STEP 2: Clear prompt field (REQUIRED!)
```bash
agent-browser eval "localStorage.removeItem('hf:image-form-upd'); location.reload()"
sleep 3
```

### STEP 3: Enable unlimited toggle
```bash
agent-browser eval "document.querySelector('[role=\"switch\"]').click()"
sleep 1
```

### STEP 4: Enter prompt - USE THIS EXACT COMMAND
```bash
agent-browser eval "document.querySelectorAll('[role=\"textbox\"]')[0].innerText = 'YOUR PROMPT HERE'"
```

### STEP 5: Click Generate - USE THIS EXACT COMMAND
```bash
agent-browser find text "Generate" click
```

### STEP 6: Wait for generation
```bash
sleep 30
```

### STEP 7: Check for captcha
```bash
agent-browser snapshot | grep -i "captcha"
```
If captcha appears: alert user with beep + speak, wait for solve, then click Generate again

---

**OPTIONAL STEPS (only if user asks):**

### To select a character:
```bash
agent-browser find text "CHARACTER" click
sleep 2
agent-browser find text "All" click
sleep 1
agent-browser find text "YourCharacterName" click
```

### To select a style:
```bash
agent-browser find text "GENERAL" click
```

---

---

## CAPTCHA HANDLING ⭐ CRITICAL

**When CAPTCHA appears, you MUST:**

1. **Play alert sound:**
```bash
# Beep beep sound to get user's attention
python3 -c "import os; [os.system('printf \"\\a\" * 3)' for _ in range(1)]" 2>/dev/null || echo -e "\a\a\a"
```

2. **Speak to user:**
```bash
# Use elia-speak to alert user
elia-speak -e "Captcha detected! Please fill the captcha in the browser window, then I'll continue."
```

3. **Wait for user to solve:**
```bash
sleep 10
agent-browser snapshot | grep -i "captcha\|verification"
```

4. **After captcha solved, RE-CLICK Generate:**
```bash
agent-browser find text "Generate" click
```

### Full Captcha Alert Script:
```bash
# Check if captcha appeared
if agent-browser snapshot | grep -qi "captcha\|verification\|verify"; then
    echo -e "\a\a\a"  # Beep beep
    elia-speak -e "Captcha detected! Please fill the captcha in the browser window, then I'll continue."
    echo "Waiting for user to solve captcha..."
    sleep 10  # Give user time to solve
fi
```

---

## KEY TO CLEAR

**Image prompt stored in:** `hf:image-form-upd`

```bash
localStorage.removeItem('hf:image-form-upd')
```

---

## Bene2Luxe Mascot ⚠️

**Path:** `/Users/vakandi/Documents/HiggsField.ai-API-Wraper/mascott_bene2luxe.png`

**DO NOT use as image input.** Use text prompts only.

---

## 📂 WHERE IMAGES ARE SAVED

**Images are saved to the "WaelTest" folder by default!**

To view generated images:
1. Go to: `https://higgsfield.ai/assets`
2. **Click on "WaelTest"** folder in the left sidebar (NOT "All Assets" at root)
3. Your generated images will appear there

**Note:** The main "All Assets" view shows ROOT-level files only (empty by default). 
Your images are in the folder, not at root level.

---

## DOWNLOADING

1. Go to: `https://higgsfield.ai/assets`
2. **Click on "WaelTest"** folder in the left sidebar
3. Select images with checkboxes
4. Click "Download"
5. Files in: `~/Downloads/`

```bash
ls -lath ~/Downloads/hf_*.png | head -5
```

---

## COMPLETE EXAMPLE

```bash
# 1. Open page
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/image/soul"
sleep 3

# 2. Clear prompt field
agent-browser eval "localStorage.removeItem('hf:image-form-upd'); location.reload()"
sleep 3

# 3. Enable unlimited
agent-browser eval "document.querySelector('[role=\"switch\"]').click()"
sleep 1

# 4. Enter prompt - EXACT command!
agent-browser eval "document.querySelectorAll('[role=\"textbox\"]')[0].innerText = 'Luxury Dior B23 sneakers on pink background, professional product photography'"

# 5. Generate - EXACT command!
agent-browser find text "Generate" click

# 6. Wait
sleep 30

# 7. Check captcha
agent-browser snapshot | grep -i "captcha"

# Close
agent-browser close
```
