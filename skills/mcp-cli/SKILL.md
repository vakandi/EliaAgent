---
name: mcp-cli
description: Access external services via mcp-cli wrapper (WhatsApp, Discord, Jira, SSH, Gmail, Coolify, GSC). Use skill(name="mcp-cli") to load this skill before calling any mcp-cli commands. Full tool reference: ~/EliaAI/context/TOOLS.md
---

# MCP-CLI Skill

## ⚠️ CRITICAL: How to Call

**ALWAYS use the `bash` tool** to execute mcp-cli commands:

```
<invoke name="bash">
  <command>mcp-cli call <server> <tool> '<json-arguments>'</command>
</invoke>
```

### ⚠️ NEVER use `mcp-cli list` — it's useless

To see all available servers, just run bare `mcp-cli` (no arguments). `mcp-cli list` does NOT work.

### 📖 Full tool reference lives in `~/EliaAI/context/TOOLS.md`

That file is the **single source of truth** for every MCP server, tool, parameter, and example. Always check it first.

## Coolify CLI & MCP

### Coolify CLI (installed at ~/.local/bin/coolify)

```bash
# Configure context (run once)
~/.local/bin/coolify context add \
  --name production \
  --url https://dashboard.your-agency.agency \
  --token YOUR_COOLIFY_API_TOKEN

# List projects
~/.local/bin/coolify project list

# List applications in a project
~/.local/bin/coolify app list --project <project-id>

# Deploy an application
~/.local/bin/coolify deploy <application-uuid>

# Delete an application
~/.local/bin/coolify app delete <application-uuid>

# List servers
~/.local/bin/coolify server list

# List services
~/.local/bin/coolify service list

# Output as JSON for scripting
~/.local/bin/coolify project list --format json
```

### Coolify via mcp-cli (if MCP server configured)

```bash
# List all MCP servers (check if coolify is available)
mcp-cli

# If coolify MCP is configured:
mcp-cli call coolify list_projects
mcp-cli call coolify get_project '{"project_id":"..."}'
mcp-cli call coolify list_applications '{"project_id":"..."}'
mcp-cli call coolify deploy_application '{"application_id":"..."}'
```

### When to use which

| Task | Use |
|---|---|
| Quick project/app listing | `coolify CLI` |
| Deploy/delete operations | `coolify CLI` |
| Complex queries with filters | `mcp-cli call coolify` |
| Scripting/automation | `coolify CLI --format json` |

### Available Servers & Tools

### WhatsApp
```bash
mcp-cli call whatsapp list_chats '{"limit":20}'
mcp-cli call whatsapp list_messages '{"chat_jid":"120363408208578679@g.us","limit":30}'
mcp-cli call whatsapp send_message '{"recipient":"120363420711538035@g.us","message":"Hello"}'
mcp-cli call whatsapp download_media '{"message_id":"...","chat_jid":"..."}'
```

### Jira
```bash
mcp-cli call mcp-atlassian create_issue '{"project":"BEN","summary":"...","description":"...","issue_type":"Task"}'
mcp-cli call mcp-atlassian jira_get_project_issues '{"project_key":"BEN"}'
```

### Discord
```bash
mcp-cli call discord-mcp discord_get_dms '{"limit":10}'
mcp-cli call discord-mcp discord_send_dm '{"user_id":"...","message":"..."}'
```

### SSH Servers

#### Multi-SaaS Deploy (Production)
```bash
mcp-cli call ssh-server-multisaasdeploy execute-command '{"cmdString":"docker ps"}'
mcp-cli call ssh-server-multisaasdeploy execute-command '{"cmdString":"ls -la /app"}'
```

#### AccForge.io
```bash
mcp-cli call ssh-mpc-server-accforge.io execute-command '{"cmdString":"ls"}'
```

#### Angerscar.ma
```bash
mcp-cli call ssh-mcp-server-angerscar.ma execute-command '{"cmdString":"ls"}'
```

### Gmail
```bash
mcp-cli call gmail search_emails '{"query":"in:inbox newer_than:7d","maxResults":20}'
mcp-cli call gmail send_email '{"to":["email@example.com"],"subject":"Subject","body":"Body"}'
```

### Email: contact@your-agency.agency (IONOS)
```bash
mcp-cli call mail_contact_your-agency_agency list_emails_metadata '{"limit":20}'
mcp-cli call mail_contact_your-agency_agency get_emails_content '{"email_id":"..."}'
mcp-cli call mail_contact_your-agency_agency send_email '{"to":"...","subject":"...","body":"..."}'
```

### Email: your-agency_distribution (Distribution)
```bash
mcp-cli call mail_contact_cofibou_distribution list_emails_metadata '{"limit":20}'
mcp-cli call mail_contact_cofibou_distribution send_email '{"to":"...","subject":"...","body":"..."}'
```

### GitHub Copilot
```bash
mcp-cli call github-copilot get_me
mcp-cli call github-copilot list_issues '{"repo":"owner/repo"}'
mcp-cli call github-copilot create_issue '{"repo":"owner/repo","title":"...","body":"..."}'
```

### Playwright (Browser Automation — single session)
```bash
mcp-cli call playwright browser_navigate '{"url":"https://example.com"}'
mcp-cli call playwright browser_snapshot
mcp-cli call playwright browser_click '{"selector":"button"}'
```

### Parallel Browser MCP (Multi-Session — 26 tools)

**⚠️ SESSION ISOLATION:** Each agent MUST create its own session with a distinct name. Never reuse sessions — assume another agent is using the MCP. Close your session when done.

**⚠️ mcp-cli Limitation:** `mcp-cli call` spawns a new process per call → session state lost. Use **native MCP** in OpenCode for multi-step workflows. `get_sessions` works via mcp-cli (no state needed).

```bash
# Quick check (works via mcp-cli — no state needed)
mcp-cli call parallel-browser-mcp get_sessions '{}'

# Full workflow — use native MCP tool_call in OpenCode:
# 1. start_session → {"id":1,"provider":"playwright"}
# 2. browser_navigate → {"sessionId":1,"url":"https://..."}
# 3. browser_snapshot / browser_click / browser_fill / browser_screenshot / browser_evaluate
# 4. close_session → {"sessionId":1,"closed":true}
```

**Session naming:** `{agent}_{task}` — e.g. `elia_morning`, `bene2_scrape`, `gilfoyle_deploy`

**Providers:** `playwright` (local, default), `browserbase`, `anchor`, `cloudflare`

### your-brand API (Full Backend)
```bash
# Orders
mcp-cli call your-brand_mcp get_orders '{"limit":20}'
mcp-cli call your-brand_mcp get_order_by_id '{"order_id":123}'
mcp-cli call your-brand_mcp update_order_status '{"order_id":123,"status":"shipped"}'

# Products
mcp-cli call your-brand_mcp get_products '{"limit":20}'
mcp-cli call your-brand_mcp search_products '{"query":"Stone Cargo"}'
mcp-cli call your-brand_mcp get_all_brands

# Users
mcp-cli call your-brand_mcp get_users '{"limit":20}'
mcp-cli call your-brand_mcp get_new_users '{"days":7}'

# Analytics
mcp-cli call your-brand_mcp get_order_stats
mcp-cli call your-brand_mcp get_analytics
mcp-cli call your-brand_mcp get_financial_summary

# Snapchat
mcp-cli call your-brand_mcp get_snapchat_army_info
mcp-cli call your-brand_mcp get_snapchat_device_health
mcp-cli call your-brand_mcp get_snapchat_campaigns
mcp-cli call your-brand_mcp get_snapchat_leads

# WhatsApp
mcp-cli call your-brand_mcp get_whatsapp_chats
mcp-cli call your-brand_mcp get_whatsapp_messages '{"chat_id":123}'
mcp-cli call your-brand_mcp send_whatsapp_message '{"chat_id":123,"message":"..."}'

# System
mcp-cli call your-brand_mcp get_system_health
mcp-cli call your-brand_mcp get_recent_notifications
```

### Apple Image Generator (Apple Intelligence + Pollinations — 16 tools)

**Full reference:** `skill(name="apple-image-generator")` → reads `~/.config/opencode/skills/apple-image-generator/SKILL.md`

Two engines: Apple Intelligence (on-device stylized art) and Pollinations.ai (cloud photorealistic). 40+ platform presets, text overlay, watermark, smart crop, batch generation.

```bash
# Check what's available
mcp-cli call apple_intelligence list_engines '{}'

# Generate photorealistic image (Pollinations — free, no API key)
mcp-cli call apple_intelligence generate_image '{"prompt":"professional product photo","engine":"pollinations"}'

# Generate stylized art (Apple Intelligence — on-device)
mcp-cli call apple_intelligence generate_image '{"prompt":"cute robot","engine":"apple","style":"illustration"}'

# Generate + crop for multiple social platforms
mcp-cli call apple_intelligence generate_social_pack '{"prompt":"product launch","platforms":["instagram_post","twitter_post","linkedin_post"]}'

# Use predefined bundle
mcp-cli call apple_intelligence generate_bundle '{"prompt":"startup announcement","bundle":"startup_kit"}'

# Add text overlay to existing image
mcp-cli call apple_intelligence add_text_overlay '{"image_path":"/path/to/img.png","text":"SALE 50% OFF","font_size":64}'

# Crop existing image to platform sizes
mcp-cli call apple_intelligence crop_image '{"image_path":"/path/to/photo.jpg","platforms":["instagram_post","facebook_post"]}'
```

### Vision MCP (Multi-Provider Image Analysis)
```bash
# Single image analysis
mcp-cli call vision-mcp analyze_image '{"image_paths": ["/path/to/image.jpg"], "prompt": "Describe this image", "model": "nvidia/nemotron-nano-12b-v2-vl:free"}'

# Multi-image comparison — supports Qwen VL, Gemma 3, Mistral, Llama vision
# Useful for marketing content comparison (A/B test visuals, before/after, competitor analysis)
mcp-cli call vision-mcp analyze_image '{"image_paths": ["img1.jpg","img2.jpg"], "prompt": "Compare these two marketing images"}'
```

### Zernio (Multi-Platform Social Media Engine — 44 tools)
**Use for:** Posting, scheduling, and managing content across 15+ social platforms (Twitter/X, Instagram, Facebook, LinkedIn, TikTok, YouTube, Pinterest, Reddit, Bluesky, Threads, Snapchat, Telegram, WhatsApp, Discord, Google Business).

**📖 Full reference:** `~/EliaAI/context/ZERNIO_TOOLS.md` — Complete tool schemas, platform-specific data formats, and examples for every platform.

**Architecture:** Multi-account with per-account proxies. 3 accounts:
- `account-1` (tweetsyncai) → Instagram, Pinterest
- `account-2` (leitarvisku) → Reddit, YouTube
- `account-3` (waionshredder) → Facebook, LinkedIn

**All tools require `account_id`** (except `zernio_get_accounts` and `zernio_sync_platforms`).

**Media upload:** Local files via `media_paths` (jpg, png, gif, webp, mp4, mov). Presigned upload internally. `media_urls` also available for public URLs.

**Queue scheduling:** Pass `queued_from_profile` (profile ID) instead of `scheduled_for` to auto-assign next queue slot.

```bash
# Account & Config
mcp-cli call zernio zernio_get_accounts '{}'
mcp-cli call zernio zernio_create_profile '{"account_id":"account-1","name":"Mon Projet"}'
mcp-cli call zernio zernio_list_profiles '{"account_id":"account-1"}'
mcp-cli call zernio zernio_list_connected_accounts '{"account_id":"account-1"}'
mcp-cli call zernio zernio_sync_platforms '{}'

# Post Creation
mcp-cli call zernio zernio_schedule_post '{"account_id":"account-1","content":"Post text","platforms":[{"platform":"instagram","accountId":"6a48062e9d9472faae6a33f7"}],"publish_now":true,"media_paths":["/path/to/image.jpg"]}'
mcp-cli call zernio zernio_quick_post '{"account_id":"account-1","content":"Quick post","platform":"instagram","profile_id":"6a480557fdeebb08400c9730","publish_now":true}'

# Post Management
mcp-cli call zernio zernio_list_posts '{"account_id":"account-1","limit":10,"status":"published"}'
mcp-cli call zernio zernio_get_post '{"account_id":"account-1","post_id":"..."}'
mcp-cli call zernio zernio_delete_post '{"account_id":"account-1","post_id":"..."}'
mcp-cli call zernio zernio_retry_post '{"account_id":"account-1","post_id":"..."}'
mcp-cli call zernio zernio_unpublish_post '{"account_id":"account-1","post_id":"...","platform":"twitter"}'
mcp-cli call zernio zernio_update_post '{"account_id":"account-1","post_id":"...","content":"Updated text"}'
mcp-cli call zernio zernio_edit_published_post '{"account_id":"account-1","post_id":"...","platform":"twitter","content":"Edited text"}'
mcp-cli call zernio zernio_update_post_metadata '{"account_id":"account-1","post_id":"...","platform":"youtube","title":"New title","tags":["tag1"]}'

# Comment Management
mcp-cli call zernio zernio_list_commented_posts '{"account_id":"account-1","limit":10}'
mcp-cli call zernio zernio_get_post_comments '{"account_id":"account-1","post_id":"...","limit":20}'
mcp-cli call zernio zernio_reply_to_comment '{"account_id":"account-1","post_id":"...","message":"Thanks!","comment_id":"..."}'
mcp-cli call zernio zernio_delete_comment '{"account_id":"account-1","post_id":"...","comment_id":"..."}'
mcp-cli call zernio zernio_like_comment '{"account_id":"account-1","post_id":"...","comment_id":"..."}'
mcp-cli call zernio zernio_hide_comment '{"account_id":"account-1","post_id":"...","comment_id":"..."}'
mcp-cli call zernio zernio_unhide_comment '{"account_id":"account-1","post_id":"...","comment_id":"..."}'
mcp-cli call zernio zernio_private_reply_to_comment '{"account_id":"account-1","post_id":"...","comment_id":"...","message":"DM text"}'

# Queue Scheduling
mcp-cli call zernio zernio_list_queue_slots '{"account_id":"account-1","profile_id":"6a480557fdeebb08400c9730"}'
mcp-cli call zernio zernio_create_queue_slot '{"account_id":"account-1","profile_id":"6a480557fdeebb08400c9730","name":"Mon Queue","timezone":"Europe/Paris","slots":[{"dayOfWeek":1,"time":"10:00"},{"dayOfWeek":3,"time":"14:30"}]}'
mcp-cli call zernio zernio_delete_queue_slot '{"account_id":"account-1","profile_id":"6a480557fdeebb08400c9730","queue_id":"..."}'
mcp-cli call zernio zernio_preview_queue_slots '{"account_id":"account-1","profile_id":"6a480557fdeebb08400c9730","count":5}'
mcp-cli call zernio zernio_next_queue_slot '{"account_id":"account-1","profile_id":"6a480557fdeebb08400c9730"}'

# Analytics
mcp-cli call zernio zernio_get_post_analytics '{"account_id":"account-1","post_id":"..."}'
mcp-cli call zernio zernio_get_analytics_timeline '{"account_id":"account-1","post_id":"..."}'
mcp-cli call zernio zernio_get_daily_metrics '{"account_id":"account-1","from_date":"2026-06-01","to_date":"2026-07-03"}'
mcp-cli call zernio zernio_get_best_time_to_post '{"account_id":"account-1"}'
mcp-cli call zernio zernio_get_follower_stats '{"account_id":"account-1"}'
```

**Notes:**
- Connected account IDs come from `zernio_list_connected_accounts`. Profile IDs come from `zernio_list_profiles`.
- Proxy strategy: Each account has its own HTTPS proxy + user-agent. Free tier = 2 platforms per account.
- All errors return `{ success: false, error: "description" }`. 401/403/429 throw, everything else returns clean error response.

### HeyGen MCP (Video Generation — 12 tools)
**Use for:** AI video generation, avatars, text-to-speech, video translation, and video editing via HeyGen API.

**📖 Full reference:** `~/EliaAI/context/HEYGEN_TOOLS.md` — Complete tool schemas, avatar list, voice options, and workflow examples.

```bash
# List available avatars
mcp-cli call heygen-mcp list_avatars '{}'

# Generate video from text
mcp-cli call heygen-mcp create_video '{"title":"Product Demo","input":[{"voice":{"voice_id":"..."},"text":"Hello world"}]}'

# Check video status
mcp-cli call heygen-mcp get_video_status '{"video_id":"..."}'

# List video templates
mcp-cli call heygen-mcp list_templates '{}'
```

### Discord Server MCP
```bash
mcp-cli call discord-server-mcp discord_discover
mcp-cli call discord-server-mcp discord_execute '{"action":"send_message","channel":"...","content":"..."}'
```

### Telegram (Standard Messaging)

```bash
# Lire les messages
mcp-cli call telegram get_default_group_messages '{"limit":20}'
mcp-cli call telegram get_personal_dms_only '{"limit":20}'
mcp-cli call telegram get_personal_dms_and_groups '{"limit":20}'
mcp-cli call telegram get_mentions_of_me '{"limit":20}'

# Envoyer des messages
mcp-cli call telegram send_msg_to_default_group '{"message":"Texte"}'
mcp-cli call telegram send_msg_to_group '{"group_id":"...","message":"..."}'
mcp-cli call telegram send_msg_to_dm '{"user_id":"...","message":"..."}'
mcp-cli call telegram send_msg_to_recipient '{"recipient":"@username","message":"..."}'

# Envoyer fichiers/voix
mcp-cli call telegram send_voice_file '{"file_path":"/path/to/audio.ogg"}'
mcp-cli call telegram send_document_file '{"file_path":"/path/to/doc.pdf"}'
mcp-cli call telegram send_voice_to_recipient '{"recipient":"@username","file_path":"..."}'
mcp-cli call telegram send_file_to_recipient '{"recipient":"@username","file_path":"..."}'

# Recherche et infos
mcp-cli call telegram resolve_contact '{"username":"@username"}'
mcp-cli call telegram api_search_channel '{"query":"stripe maroc"}'
mcp-cli call telegram api_get_channel_info '{"channel_username":"stripemaroc"}'
mcp-cli call telegram api_scrape_channel '{"channel_username":"stripemaroc","limit":100}'

# Approbations
mcp-cli call telegram send_approval_request '{"tool_name":"send_msg_to_default_group","reason":"..."}'
mcp-cli call telegram get_approval_responses '{}'
```

### 21st.dev Magic (UI Component Generation)
```bash
# Generate a UI component from description
mcp-cli call "@21st-dev/magic" 21st_magic_component_builder '{"message":"Create a modern pricing table","searchQuery":"pricing table","absolutePathToCurrentFile":"/path/to/file.tsx","absolutePathToProjectDirectory":"/path/to/project","standaloneRequestQuery":"Pricing table with 3 tiers"}'

# Get component inspiration
mcp-cli call "@21st-dev/magic" 21st_magic_component_inspiration '{"message":"Show me button components","searchQuery":"button"}'

# Refine an existing component
mcp-cli call "@21st-dev/magic" 21st_magic_component_refiner '{"userMessage":"Make the button more modern","absolutePathToRefiningFile":"/path/to/button.tsx","context":"Button component"}'

# Search for logos
mcp-cli call "@21st-dev/magic" logo_search '{"query":"Stripe payment logo"}'
```

### Telegram Scraper (Recrutement de Masse)

```bash
# Découvrir des channels similaires à des seeds
mcp-cli call telegram-scraper discover_similar_channels \
  '{"seed_channels":["https://t.me/stripemaroc","https://t.me/shopifyfrance"],"max_results":30}'

# Scraper les membres d'un channel
mcp-cli call telegram-scraper scrape_members \
  '{"channel_url":"https://t.me/stripemaroc","max_members":500}'

# Rejoindre un groupe
mcp-cli call telegram-scraper join_group \
  '{"group_url":"https://t.me/stripemaroc"}'

# Inviter des membres scrapés vers ton channel
mcp-cli call telegram-scraper invite_members \
  '{"target_channel":"https://t.me/MirrorPayChannel","max_invites":20,"speed":"slow"}'

# Options partagées:
#   account_index (optional): 0=owner (read-only), 1+=scrapers (par défaut)
#   speed: "slow" (30-45s entre invites) ou "normal"
```

### Google Search Console MCP (58 tools)

**Server:** `gsc-mcp` — Full docs in `~/EliaAI/context/TOOLS.md` (section "🔍 GSC MCP")

```bash
# Inspect URL (tested: uses "site" + "url")
mcp-cli call gsc-mcp inspect_url '{"site":"sc-domain:your-saas.com","url":"https://your-saas.com/stripe-cloaking"}'

# Submit URL for indexing (tested: only needs "url")
mcp-cli call gsc-mcp submit_url '{"url":"https://your-saas.com/stripe-cloaking"}'

# Batch submit
mcp-cli call gsc-mcp submit_batch '{"urls":["https://your-saas.com/stripe-cloaking","https://your-saas.com/pricing"]}'

# Performance overview
mcp-cli call gsc-mcp get_performance_overview '{"site":"sc-domain:your-saas.com"}'

# Quick wins (pages ready to push to page 1)
mcp-cli call gsc-mcp quick_wins '{"site":"sc-domain:your-saas.com"}'

# List sitemaps
mcp-cli call gsc-mcp list_sitemaps '{"site":"sc-domain:your-saas.com"}'
```

### ⚠️ GSC Pitfalls (tested)
| Pitfall | Fix |
|---------|-----|
| `inspect_url` expects `site` + `url` | NOT `site_url` + `inspection_url` |
| `submit_url` / `submit_batch` | Only need `url`/`urls`, no `site` param |
| GA4 tools ignore `site` | Use `account` directly |

## Common Issues

| Issue | Solution |
|-------|----------|
| `SERVER_NOT_FOUND: ssh-mpc-server...` | Use correct name: `ssh-server-multisaasdeploy` (NOT `ssh-mpc-server-multisaasdeploy`) |
| Tool not found | Check server name spelling exactly |
| `mcp-cli list` returns nothing | Run bare `mcp-cli` (no args) to list all servers |

## Business Groups (WhatsApp JIDs)
- B2B Group: `120363420711538035@g.us`
- Your Brand Group: `120363408208578679@g.us`
- Partner Group: `120363405622746597@g.us`

## Jira Projects
- your-brand: `YOURBRAND`
- your-agency: `YOURAGENCY`
- TikTok/YouTube: `TIKYT`
- Your SaaS: `YOURSAAS`
