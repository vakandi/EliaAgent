---
name: higgsfield-video-generation
description: Generate videos using Higgsfield.ai free/unlimited models. CRITICAL: Use --profile for visible browser + https://higgsfield.ai/create/video. Triggers: "generate video", "create video". Uses agent-browser CLI with visible mode + captcha alert system.
---

# Higgsfield Video Generation

## ⚠️ ALWAYS CLOSE BROWSER WHEN DONE

```bash
# ✅ ALWAYS close browser when finished
agent-browser close
```

**IMPORTANT:** Always run `agent-browser close` when done to properly release the headed mode session.

---

## ⚠️ CRITICAL RULES

1. **Use `--profile` for VISIBLE browser** - User MUST see the browser
2. **Use URL:** `https://higgsfield.ai/create/video` (not /video/*)
3. **Always enable the unlimited toggle**
4. **Clear 'flow-create-video-*'** before each generation
5. **ALERT user with beep + speak when captcha appears** ⭐

---

## BROWSER MODE: ALWAYS VISIBLE 👁️

**CRITICAL: Use `--headed` AND `--profile` together!**

```bash
# ✅ CORRECT - Visible browser + persists login/cookies
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/create/video"

# ❌ WRONG - Headless mode, user cannot see/interact
agent-browser open "https://higgsfield.ai/create/video"

# ❌ WRONG - Two separate commands don't work
agent-browser --profile ~/.agent-browser-profile open "..."
agent-browser --headed open "..."
```

**User MUST see the browser to:**
- Monitor generation progress (60+ seconds)
- **Solve CAPTCHA if it appears** ⭐
- Verify video quality

---

## URL

**Video Generation:** `https://higgsfield.ai/create/video`

---

## WORKFLOW

### STEP 1: Navigate to Video Page
```bash
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/create/video"
sleep 3
```

### STEP 2: Clear Prompt Field ⚠️
```bash
agent-browser eval "
Object.keys(localStorage).filter(k => k.startsWith('flow-create-video')).forEach(k => localStorage.removeItem(k));
location.reload();
"
sleep 3
```

### STEP 3: Find Elements
```bash
agent-browser snapshot | grep -E "(textbox|Describe|switch|Generate)"
```

### STEP 4: Enable Unlimited Toggle
```bash
agent-browser click @switch_ref
```

### STEP 5: Enter Prompt
```bash
agent-browser fill @textbox_ref "Your video prompt here"
```

### STEP 6: Generate
```bash
agent-browser click @generate_ref
```

### STEP 7: Check for CAPTCHA ⭐
```bash
# After clicking Generate, ALWAYS check for captcha
agent-browser snapshot | grep -i "captcha\|verification\|verify"
```

### STEP 8: Wait 60+ seconds
```bash
sleep 60
```

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
agent-browser click @generate_ref
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

**Video prompt stored in:** `flow-create-video-*` (pattern match)

```javascript
Object.keys(localStorage)
  .filter(k => k.startsWith('flow-create-video'))
  .forEach(k => localStorage.removeItem(k));
```

---

## Bene2Luxe Mascot ⚠️

**Path:** `/Users/vakandi/Documents/HiggsField.ai-API-Wraper/mascott_bene2luxe.png`

**DO NOT use as image input.** Use text prompts only.

---

## DOWNLOADING

Files save to: `~/Downloads/`

```bash
ls -lath ~/Downloads/hf_*.mp4 | head -5
```

---

## EXAMPLE

```bash
agent-browser --profile ~/.agent-browser-profile --headed open "https://higgsfield.ai/create/video"
sleep 3
agent-browser eval "Object.keys(localStorage).filter(k => k.startsWith('flow-create-video')).forEach(k => localStorage.removeItem(k)); location.reload();"
sleep 3
agent-browser click @switch_ref
agent-browser fill @textbox_ref "Dior B23 luxury lifestyle video"
agent-browser click @generate_ref

# Check for captcha
if agent-browser snapshot | grep -qi "captcha\|verification"; then
    echo -e "\a\a\a"
    elia-speak -e "Captcha detected! Please fill the captcha in the browser window."
    read -p "Press Enter after solving captcha..."
fi

sleep 60
```
