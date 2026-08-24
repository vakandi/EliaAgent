---
name: chrome-extension-tester
description: "Testing workflow for Chrome extensions with your-brand backend integration. Use when: (1) Testing Snapchat Auto Add extension features, (2) Registering devices with the your-brand backend, (3) Debugging extension behavior, (4) Accessing popup and service worker logs, (5) Running automation tests against the extension."
---

# Chrome Extension Tester

## Quick Start

### Load Extension with agent-browser

```bash
agent-browser --profile ~/.agent-browser-profile \
  --extension "~/Documents/MultiSaasDeploy/snapchat_army/snapchat_ecommerce_chrome_extension" \
  open about:blank
```

### Find Extension ID

```bash
agent-browser open chrome://extensions
agent-browser snapshot | grep "ID:"
```

### Open Extension Popup

```bash
# Replace {EXTENSION_ID} with actual ID
agent-browser open "chrome-extension://{EXTENSION_ID}/popup.html"
```

## Device Registration Workflow

1. Load extension → Open popup
2. Fill Master Key: `agent-browser fill "ref=e10" "MASTER_KEY"`
3. Fill Snapchat Account: `agent-browser fill "ref=e11" "your-agency.dev"`
4. Click Register: `agent-browser click "ref=e12"`
5. Wait 3s → Check logs: `agent-browser click "ref=e7"`

### Get Master Key

1. Go to `https://your-brand.com/admin?section=channels`
2. Click **Master Key** → **Régénérer**
3. Copy the key

### Expected Success Logs

```
[BXL] Enregistrement du device...
[BXL] ✅ Device enregistré. Heartbeat démarré.
[Backend] Configuration mise à jour: ...
```

## Common Interactions

| Action | Command |
|--------|---------|
| Click button | `agent-browser click "ref=e12"` |
| Fill input | `agent-browser fill "ref=e9" "value"` |
| Screenshot | `agent-browser screenshot /tmp/ext.png` |
| View DOM | `agent-browser snapshot` |
| Get URL | `agent-browser get url` |

## Accessing Logs

### Popup Logs

Open popup → Click **📋 Logs** button → View log section

### Service Worker Logs

1. Open `chrome://extensions`
2. Find extension → Click **"service worker"** under Inspect views
3. Open Console tab in DevTools

## API Testing

```bash
curl -X POST "https://your-brand.com/api/snapchat-ext/register" \
  -H "Content-Type: application/json" \
  -H "X-Snapchat-Extension-Key: YOUR_KEY" \
  -d '{"device_id":"UUID","device_name":"Test","extension_version":"1.0.0","browser":"chrome","os":"MacIntel"}'
```

Note: `device_id` must be a valid UUID v4.

## Extension Path

```
~/Documents/MultiSaasDeploy/snapchat_army/snapchat_ecommerce_chrome_extension/
```

## Key Files

- `manifest.json` - Extension manifest
- `popup.html` / `popup.js` - Extension popup UI and logic
- `background.js` - Service worker (heartbeat, queue)
- `content.js` - Content script for Snapchat web

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Extension not loading | Use absolute path, close Chrome first |
| Popup blocked | Use `chrome-extension://{id}/popup.html` |
| Registration fails | Verify master key valid |
| Service worker inactive | Open popup to wake it up |

## Advanced

See [references/TESTING.md](references/TESTING.md) for complete documentation.
