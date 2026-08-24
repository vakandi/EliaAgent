# Chrome Extension Testing Guide

This document describes the testing workflow for the Snapchat Auto Add Chrome extension, including how to load the extension, interact with it, register devices with the your-brand backend, and access logs.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Loading the Extension](#loading-the-extension)
3. [Interacting with the Extension](#interacting-with-the-extension)
4. [Registering a Device](#registering-a-device)
5. [Accessing Logs](#accessing-logs)
6. [Troubleshooting](#troubleshooting)
7. [Useful Commands](#useful-commands)

---

## Prerequisites

### Tools Required

| Tool | Installation | Purpose |
|------|--------------|---------|
| `agent-browser` | `brew install agent-browser` | Browser automation for testing |
| `curl` | Pre-installed | API testing |
| Chrome/Chromium | Pre-installed | Browser for extension |

### Master Key

Before testing, you need a valid master key from the your-brand admin panel:

1. Go to: `https://your-brand.com/admin?section=channels`
2. Click **Master Key** button
3. Click **Régénérer** to generate a new key
4. Copy the key (e.g., `tSinZmbOZu-Glet4wjJbM-HDNgUafmFXQ_r9sWfPAIw`)

---

## Loading the Extension

### Method 1: Using agent-browser (Recommended)

The `agent-browser` tool supports loading Chrome extensions via the `--extension` flag:

```bash
# Load the extension and open a blank page
agent-browser --profile ~/.agent-browser-profile \
  --extension "~/Documents/MultiSaasDeploy/snapchat_army/snapchat_ecommerce_chrome_extension" \
  open about:blank
```

**Note:** The extension ID changes each time you reload the extension in developer mode.

### Method 2: Using Chrome Directly

```bash
# Open Chrome with extension loaded via command line
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --extension="~/Documents/MultiSaasDeploy/snapchat_army/snapchat_ecommerce_chrome_extension" \
  --user-data-dir=/tmp/chrome-with-ext \
  --no-first-run \
  --no-default-browser-check
```

### Finding the Extension ID

The extension ID changes on each reload. To find it:

1. Open chrome://extensions in the browser
2. Look for "Snapchat Auto Add Friends"
3. Note the ID (e.g., `dfkkgfhglfmebdmlnijgggbadjekamlg`)

---

## Interacting with the Extension

### Opening the Extension Popup

Once loaded, open the popup at:

```
chrome-extension://{EXTENSION_ID}/popup.html
```

Using agent-browser:

```bash
# Replace with actual extension ID
agent-browser --profile ~/.agent-browser-profile \
  open "chrome-extension://dfkpgfhglfmebdmlnijgggbadjekamlg/popup.html"
```

### Taking a Screenshot

```bash
agent-browser --profile ~/.agent-browser-profile screenshot /tmp/ext.png
```

### Viewing the Accessibility Tree

This helps identify clickable elements:

```bash
agent-browser --profile ~/.agent-browser-profile snapshot
```

### Common Interactions

| Action | Command |
|--------|---------|
| Click button | `agent-browser click "ref=e12"` |
| Fill input | `agent-browser fill "ref=e9" "value"` |
| Get current URL | `agent-browser get url` |
| Reload page | `agent-browser reload` |

---

## Registering a Device

### Step-by-Step Process

1. **Load the extension** (see above)

2. **Open the extension popup**:
   ```bash
   agent-browser --profile ~/.agent-browser-profile \
     open "chrome-extension://{EXTENSION_ID}/popup.html"
   ```

3. **Fill in the Master Key**:
   ```bash
   # Fill the Master Key field (ref=e10)
   agent-browser fill "ref=e10" "tSinZmbOZu-Glet4wjJbM-HDNgUafmFXQ_r9sWfPAIw"
   ```

4. **Fill in the Snapchat Account**:
   ```bash
   # Fill the Snapchat Account field (ref=e11)
   agent-browser fill "ref=e11" "your-agency.dev"
   ```

5. **Click Register Button**:
   ```bash
   # Click "Enregistrer ce device" button (ref=e12)
   agent-browser click "ref=e12"
   ```

6. **Wait for registration**:
   ```bash
   sleep 3
   ```

7. **Check logs**:
   ```bash
   # Click the Logs button
   agent-browser click "ref=e7"
   
   # View logs in snapshot
   agent-browser snapshot
   ```

### Expected Success Logs

Look for these entries in the logs:
```
[15:16:41.106] [BXL] Enregistrement du device...
[15:16:42.785] [BXL] ✅ Device enregistré. Heartbeat démarré.
[15:16:43.269] [Backend] Configuration mise à jour: ...
```

### Verifying Registration via API

```bash
# Test the registration endpoint directly
curl -X POST "https://your-brand.com/api/snapchat-ext/register" \
  -H "Content-Type: application/json" \
  -H "X-Snapchat-Extension-Key: YOUR_MASTER_KEY" \
  -d '{
    "device_id": "a1b2c3d4-e5f6-4a90-abcd-ef1234567890",
    "device_name": "Test-Device",
    "extension_version": "1.0.0",
    "browser": "chrome",
    "os": "MacIntel",
    "snapchat_account_hint": "your-agency.dev"
  }'
```

---

## Accessing Logs

### Popup Logs (popup.js)

The popup has a built-in log viewer:

1. Open the extension popup
2. Click the **📋 Logs** button
3. View logs in the log section

**Log types visible:**
- `[BXL]` - Device registration and heartbeat messages
- `[Backend]` - Configuration sync messages
- `[Queue]` - Task queue operations
- `[DM Inbox]` - DM checking operations

### Background Service Worker Logs (background.js)

**⚠️ Note:** Service worker logs require manual access via Chrome DevTools:

1. Open `chrome://extensions`
2. Find "Snapchat Auto Add Friends"
3. Click **"service worker"** under "Inspect views"
4. Open the **Console** tab in the DevTools window

**Common background logs:**
```
[BXL] Heartbeat sent
[BXL] Config outdated (heartbeat): server=X, local=Y - fetching latest config
[BXL] Config applied from heartbeat check, version=Z
[BXL] trigger_dm_fetch true, calling runDmCheckInbox
[BXL] trigger_keyword_fetch true, calling runTriggerKeywordFetchOnly
[Queue] Processing task type=X
```

### Accessing Logs Programmatically

Unfortunately, Chrome MV3 service workers cannot be accessed programmatically via CDP easily. Options:

1. **Manual access** via chrome://extensions → Inspect service worker
2. **Modify code** to write logs to chrome.storage.local and read from popup
3. **Use Chrome DevTools Protocol** with a properly configured Chrome instance

---

## Troubleshooting

### Extension Not Loading

- Make sure `--extension` path is correct and absolute
- Check the extension ID has changed (re-fetch from chrome://extensions)
- Try closing all Chrome instances first: `pkill -f "Google Chrome"`

### Popup Not Opening

- Extension popup only works when opened via extension icon OR `chrome-extension://{id}/popup.html`
- Direct file URLs won't work: `file:///.../popup.html`

### Registration Fails

- Verify master key is valid (not expired)
- Check network connectivity to `https://your-brand.com`
- Look at popup logs for error messages

### Service Worker Inactive

- Service workers may go inactive after periods of inactivity
- Opening the popup or triggering an action will wake it up
- Check "service worker (Inactive)" vs "service worker" in chrome://extensions

---

## Useful Commands

### Start agent-browser with extension

```bash
agent-browser --profile ~/.agent-browser-profile \
  --extension "~/Documents/MultiSaasDeploy/snapchat_army/snapchat_ecommerce_chrome_extension" \
  open about:blank
```

### Get extension ID

```bash
# Open extensions page
agent-browser open chrome://extensions

# Find ID in snapshot
agent-browser snapshot | grep "ID:"
```

### Open extension popup

```bash
# Find extension ID first, then:
agent-browser open "chrome-extension://{EXTENSION_ID}/popup.html"
```

### Test API registration

```bash
curl -X POST "https://your-brand.com/api/snapchat-ext/register" \
  -H "Content-Type: application/json" \
  -H "X-Snapchat-Extension-Key: YOUR_KEY" \
  -d '{"device_id":"UUID","device_name":"Test","extension_version":"1.0.0","browser":"chrome","os":"MacIntel"}'
```

### Get current page snapshot

```bash
agent-browser snapshot > /tmp/snapshot.txt
cat /tmp/snapshot.txt
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `manifest.json` | Extension manifest (permissions, host permissions) |
| `popup.html` | Extension popup UI |
| `popup.js` | Popup logic, event handlers, logging |
| `background.js` | Service worker, heartbeat, queue processing |
| `content.js` | Content script for Snapchat web pages |
| `dashboard.html` | Dashboard view |

---

## API Endpoints Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/snapchat-ext/register` | POST | Master Key | Register device |
| `/api/snapchat-ext/heartbeat` | POST | Device Token | Heartbeat/config sync |
| `/api/snapchat-ext/pull-jobs` | POST | Device Token | Get pending jobs |
| `/api/admin/snapchat/devices` | GET | Admin | List devices |
| `/api/admin/snapchat/stats` | GET | Admin | Get stats |

---

## Notes

- Extension ID changes on each reload in developer mode
- The popup must be open to use chrome.storage.local
- Service workers are MV3 and run in isolated context
- Heartbeat runs periodically (configurable in backend)
- Master key can be regenerated from admin panel

---

*Last Updated: March 2026*
