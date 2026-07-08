---
name: tiktok-analytics
description: "TikTok account analytics and content monitoring using agent-browser. Use when: (1) Check TikTok business account performance, (2) Get views/comments/engagement metrics, (3) Verify if content was posted, (4) Monitor account health and growth, (5) Generate TikTok performance reports for YourName's businesses. Triggers: check TikTok, tiktok analytics, how are my TikToks doing, was content posted, TikTok engagement, views on TikTok, TikTok report."
---

# TikTok Analytics Skill

Monitor TikTok business accounts using agent-browser to check content performance, engagement metrics, and posting status.

## ✅ VERIFIED WORKING (2026-03-19)

Tested and confirmed working:
- ✅ Extract likes, comments, shares from video feed
- ✅ Get account followers, following, total likes from profile
- ✅ Navigate to profiles and videos
- ✅ Snapshot extracts all metrics correctly

## Core Tool: agent-browser

**ALWAYS use agent-browser** (not Playwright MCP):
```bash
PROFILE="--profile ~/.agent-browser-profile"
```

## Account Configuration

TikTok accounts are stored in:
- `@context/business.md` - Business TikTok accounts
- `@context/TOOLS.md` - Tool configuration

**If no accounts configured yet**: Ask YourName to provide TikTok account credentials/usernames.

## Workflow: Check TikTok Analytics

### 1. Navigate to TikTok

```bash
agent-browser $PROFILE open https://www.tiktok.com
agent-browser $PROFILE wait --load networkidle
agent-browser $PROFILE snapshot
```

### 2. Login (if not authenticated)

```bash
# Click login button
agent-browser $PROFILE find text "Log in" click

# Choose login method (email, phone, social)
# Follow the specific login flow for the account
```

### 3. Access Creator/Pro Account Dashboard

```bash
# Navigate to analytics (for Pro/Creator accounts)
agent-browser $PROFILE open https://www.tiktok.com/creator-center/
agent-browser $PROFILE wait --load networkidle
agent-browser $PROFILE snapshot
```

### 4. Get Video Performance

```bash
# Navigate to your videos
agent-browser $PROFILE open https://www.tiktok.com/<username>/video
agent-browser $PROFILE wait --load networkidle
agent-browser $PROFILE snapshot

# Look for: views, likes, comments, shares, date posted
```

### 5. Extract Key Metrics

Use `snapshot` to find:
- **Views**: "播放" or "views" in Chinese, "K" or "M" for thousands/millions
- **Likes**: "点赞" or "likes"
- **Comments**: "评论" or "comments"
- **Shares**: "分享" or "shares"
- **Post date**: "发布" or "posted"

## Workflow: Check Specific Video Performance

### Method 1: Direct Video URL

```bash
agent-browser $PROFILE open https://www.tiktok.com/@<username>/video/<video_id>
agent-browser $PROFILE wait --load networkidle
agent-browser $PROFILE snapshot
```

### Method 2: Profile Video List

```bash
agent-browser $PROFILE open https://www.tiktok.com/@<username>
agent-browser $PROFILE click "Videos"  # or find the Videos tab
agent-browser $PROFILE wait --load networkidle
agent-browser $PROFILE snapshot
```

## Workflow: Verify Content Was Posted

```bash
# Check profile for latest video
agent-browser $PROFILE open https://www.tiktok.com/@<username>
agent-browser $PROFILE wait --load networkidle

# Scroll to find videos
agent-browser $PROFILE scroll down
agent-browser $PROFILE snapshot

# Look for "Just now", "1h ago", today's date as post indicator
```

## Workflow: Generate Performance Report

### Report Structure

```markdown
# TikTok Analytics Report - [DATE]

## Account Overview
- **Account**: @[username]
- **Total Views**: [number]
- **Total Likes**: [number]
- **Engagement Rate**: [percentage]

## Recent Videos
| Video | Views | Likes | Comments | Posted |
|-------|-------|-------|---------|--------|
| [title] | [K/M] | [K/M] | [number] | [date] |

## Top Performer
- **Video**: [title/description]
- **Views**: [number]
- **Why**: [analysis]

## Engagement Alerts
- 🚀 **Skyrocketing**: [video with huge views]
- 💬 **Hot Discussion**: [video with high comments]
- ⚠️ **Low Engagement**: [video with few views despite posting]

## Action Items
- [ ] Check viral video comments
- [ ] Repost high-engagement content
- [ ] Analyze low-performer timing
```

## Verified Working Selectors

From testing, these selectors work:

### Video Feed Stats (on main page)
```
Likes:    button "Like video 1.3M likes"       → Extract: 1.3M
Comments: button "Read or add comments 2922 comments" → Extract: 2922
Shares:   button "Share video 33.6K shares"    → Extract: 33.6K
```

### Profile Stats
```
Profile heading: heading "1 Following 2225 Followers 1.5M Likes"
- Following: First number before "Following"
- Followers: Number before "Followers" 
- Total Likes: Number before "Likes"
```

### Extract Numbers from Snapshot
```
- Look for patterns like: "1.3M", "2922", "33.6K", "2225"
- K = thousands (33.6K = 33,600)
- M = millions (1.3M = 1,300,000)
```

## Common XPath/Selectors for TikTok

```css
/* Views counter */
[data-e2e="video-views"], .video-count

/* Like button */
[data-e2e="like-count"], .like-icon

/* Comment counter */
[data-e2e="comment-count"]

/* Share counter */
[data-e2e="share-count"]

/* Video timestamp */
.video-meta-item

/* Profile stats */
.author-card-hot, .author-tabs-icon
```

## TikTok Accounts (from @context/business.md)

| Business | Username | Purpose |
|----------|----------|---------|
| **YourBrand** | @luxe2bene | Drive traffic to WhatsApp for luxury fashion sales |

## Business Context

### YourBrand (@luxe2bene)
- **Purpose**: Drive traffic to WhatsApp for luxury fashion sales
- **Target**: France & Switzerland audiences
- **Success metric**: Views → WhatsApp conversions

## Tips

1. **Chinese interface**: TikTok often shows Chinese characters. Key terms:
   - 播放 = views
   - 点赞 = likes  
   - 评论 = comments
   - 分享 = shares
   - 关注 = followers

2. **Number formatting**: 
   - 1.2K = 1,200
   - 1.2M = 1,200,000
   - 10万 = 100,000 (100K in Chinese)

3. **Mobile vs Desktop**: Some metrics only visible on mobile or Pro accounts

4. **Timing**: TikTok analytics update with delay (1-24 hours)

## Error Handling

- **Login required**: Navigate to login, then retry analytics
- **Pro account needed**: Some metrics require TikTok Pro/Creator account
- **Rate limiting**: Wait 30 seconds between requests
- **Session expired**: Re-authenticate and continue
