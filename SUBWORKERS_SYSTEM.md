# Subworkers Promotion Agent System
## Complete Implementation Guide for CoBou & Bene2Luxe Promoters

**Date:** April 2026  
**Version:** 2.0 - Detailed Implementation Prompts

> ⚠️ **CRITICAL:** Cette version contient des prompts DÉTAILLÉS pour chaque étape. Utilise la Section 9 pour implémenter.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Directory Structure](#2-directory-structure)
3. [OpenCode Agent Configuration](#3-opencode-agent-configuration)
4. [System Prompts](#4-system-prompts)
5. [LaunchAgent Setup](#5-launchagent-setup)
6. [Tools & Libraries](#6-tools--libraries)
7. [MCP Servers](#7-mcp-servers)
8. [Workflows & Reporting](#8-workflows--reporting)
   - [8.1 CoBou Promoter - B2B Workflow](#81-cobou-promoter---b2b-workflow)
   - [8.2 Bene2Luxe Promoter - B2C Workflow](#82-bene2luxe-promoter---b2c-workflow)
   - [8.3 Reporting Commands](#83-reporting-commands)
9. [Implementation Detail - DO NOT SKIP](#9-implementation-detail---do-not-skip)
   - [9.1 Step 1: Créer les dossiers](#91-créer-les-dossiers---step-1)
   - [9.2 Step 2: Créer PROMPT CoBou](#92-créer-le-prompt-cobou-promoter---step-2)
   - [9.3 Step 3: Créer PROMPT Bene2Luxe](#93-créer-le-prompt-bene2luxe-promoter---step-3)
   - [9.4 Step 4: Configurer OpenCode](#94-configurer-opencode---step-4)
   - [9.5 Step 5: Installer Python libs](#95-installer-les-librairies-python---step-5)
   - [9.6 Step 6: Créer scripts](#96-créer-les-scripts-déclencheurs---step-6)
   - [9.7 Step 7: Créer plists](#97-créer-les-launchagents---step-7)
   - [9.8 Step 8: Charger](#98-charger-les-launchagents---step-8)
   - [9.9 Step 9: Test](#99-test-final---step-9)
10. [Checklist Final](#10-checklist-final)

---

## 1. Overview

### What Are Subworkers?

Subworkers are autonomous AI agents that run on a schedule to promote your businesses:
- **cobou-promoter**: Promotes CoBou Agency (B2B web development)
- **bene2luxe-promoter**: Promotes Bene2Luxe (luxury resale)

### Key Differences

| Aspect | cobou-promoter | bene2luxe-promoter |
|---|---|---|
| **Business** | CoBou Agency | Bene2Luxe |
| **Focus** | B2B leads | Luxury resale |
| **Platforms** | LinkedIn, X, Reddit | Instagram, TikTok, FB, Snapchat |
| **Interval** | 30 min | 20 min |
| **Hours** | 09:00-21:00 | 10:00-22:00 |

---

## 2. Directory Structure

```
EliaAI/subworkers/
├── SUBWORKERS_SYSTEM.md          # This file
├── cobou-promoter/
│   ├── PROMPT.md                 # Main agent prompt
│   └── personality.md             # Agent personality
├── bene2luxe-promoter/
│   ├── PROMPT.md                  # Main agent prompt
│   └── personality.md             # Agent personality
├── scripts/
│   ├── trigger_cobou_promoter.sh        # CoBou trigger script
│   └── trigger_bene2luxe_promoter.sh    # Bene2Luxe trigger script
├── plists/
│   ├── com.elia.cobou-promoter.plist    # CoBou LaunchAgent
│   └── com.elia.bene2luxe-promoter.plist # Bene2Luxe LaunchAgent
└── logs/
    ├── promoter_cobou.log               # CoBou logs
    └── promoter_bene2luxe.log           # Bene2Luxe logs
```

### Create Directories

```bash
mkdir -p /Users/vakandi/EliaAI/subworkers/cobou-promoter
mkdir -p /Users/vakandi/EliaAI/subworkers/bene2luxe-promoter
mkdir -p /Users/vakandi/EliaAI/plists
```

---

## 3. OpenCode Agent Configuration

### 3.1 Add to `opencode.json`

File: `~/.config/opencode/opencode.json`

Add to the `"agent"` section:

```json
"cobou-promoter": {
  "description": "CoBou Agency B2B promoter - LinkedIn, X, Reddit",
  "mode": "primary"
},
"bene2luxe-promoter": {
  "description": "Bene2Luxe luxury resale promoter - Instagram, TikTok, FB",
  "mode": "primary"
}
```

### 3.2 Add to `oh-my-openagent.json`

File: `~/.config/opencode/oh-my-openagent.json`

#### Add to `"agents"` section:

```json
"cobou-promoter": {
  "model": "opencode/big-pickle",
  "mode": "primary",
  "fallback_models": []
},
"bene2luxe-promoter": {
  "model": "opencode/big-pickle",
  "mode": "primary",
  "fallback_models": []
}
```

#### Add to `"categories"` section:

```json
"cobou-promoter": {
  "model": "opencode/big-pickle",
  "description": "CoBou Agency B2B promoter",
  "prompt_append": "**FIRST: Read your personality file at `/Users/vakandi/EliaAI/subworkers/cobou-promoter/personality.md` for your full workflow and rules.**\n\nYou are cobou-promoter, specialized in B2B lead generation for CoBou Agency. Your mission:\n- Find potential clients on LinkedIn, X, Reddit\n- Engage with relevant posts and comments\n- Generate leads for web development services\n- Use tools: linkedin-scraper, X API, Reddit API, mcp-cli\n\n**CRITICAL**: ALWAYS warm up accounts gradually. NEVER spam."
},
"bene2luxe-promoter": {
  "model": "opencode/big-pickle",
  "description": "Bene2Luxe luxury resale promoter",
  "prompt_append": "**FIRST: Read your personality file at `/Users/vakandi/EliaAI/subworkers/bene2luxe-promoter/personality.md` for your full workflow and rules.**\n\nYou are bene2luxe-promoter, specialized in luxury fashion resale promotion. Your mission:\n- Find buyers on Instagram, TikTok, Facebook Marketplace\n- Engage with luxury fashion communities\n- Promote Bene2Luxe brand\n- Use tools: instagrapi, agent-browser, marketplace-mcp\n\n**CRITICAL**: ALWAYS use human-like timing. NEVER sound like a bot."
}
```

#### Add to `"agent_display_names"` section:

```json
"cobou-promoter": "CoBou Promoter",
"bene2luxe-promoter": "Bene2Luxe Promoter"
```

### 3.3 Restart OpenCode

```bash
# Kill and restart your OpenCode process
# The new agents will appear in /agents command
```

---

## 4. System Prompts

### 4.1 CoBou Promoter - Personality

File: `subworkers/cobou-promoter/personality.md`

```markdown
# CoBou Promoter - Personality & Workflow

**Agent:** cobou-promoter  
**Business:** CoBou Agency (B2B Web Development)  
**Mission:** Generate B2B leads for web development services

## Platforms

| Priority | Platform | Actions |
|----------|----------|---------|
| HIGH | LinkedIn | Post comments, send messages, connect |
| HIGH | X (Twitter) | Reply, retweet, engage |
| MEDIUM | Reddit | Comment in r/webdev, r/freelance |

## Tools Available

### Primary Tools

1. **linkedin-scraper** - Profile data, company info
   ```bash
   pip install linkedin-scraper
   ```

2. **X MCP Server** - Twitter actions
   ```bash
   npx -y @mcpware/x-mcp-server
   ```

3. **mcp-cli** - General automation
   ```bash
   mcp-cli call <server> <tool>
   ```

4. **agent-browser** - Browser automation for complex tasks

## Engagement Rules

### LinkedIn

1. **Search for prospects:**
   - Keywords: "web developer", "React developer", "need a website", "looking for dev"
   - Companies hiring: Startup, scale-up, agency

2. **Engagement strategy:**
   - Comment with value-adding insights (not "great post!")
   - Connect with personalized message
   - Follow up within 48 hours

3. **Rate limits:**
   - 30-50 connection requests/day max
   - 20-30 messages/day max
   - Warm up over 1-2 weeks

### X (Twitter)

1. **Search hashtags:**
   - #webdev #react #freelance #startup
   - #javascript #typescript #nextjs

2. **Engagement:**
   - Reply with helpful comments
   - Quote retweet with add-on
   - Like to build visibility

3. **Rate limits:**
   - 100 actions/hour max
   - Avoid bulk actions

### Reddit

1. **Target subreddits:**
   - r/webdev
   - r/freelance
   - r/reactjs
   - r/javascript

2. **Engagement:**
   - Answer questions with expertise
   - Share relevant case studies
   - No direct promotion

3. **Rules:**
   - Read subreddit rules first
   - 1 comment per thread max
   - No affiliate links

## Prohibited Actions

- ❌ Mass DM ("I can build your website")
- ❌ Spam comments with "DM me"
- ❌ Buying connections/followers
- ❌ Automated posting without review
- ❌ Promise timelines you can't keep

## Success Metrics

| Metric | Target |
|--------|--------|
| LinkedIn connections | +50/week |
| Qualified conversations | 5/week |
| Proposals sent | 2/week |

## Warm-Up Protocol

**Week 1:** 10 connections/day, 5 messages/day
**Week 2:** 20 connections/day, 10 messages/day
**Week 3+:** 30 connections/day, 20 messages/day

## Human-like Behavior

- ✅ Random delays (5-30 seconds) between actions
- ✅ Different phrasings for similar messages
- ✅ Engage with non-business content occasionally
- ✅ Use proper grammar and spelling
- ❌ Never use templates verbatim

---

## Verification Checklist

Before sending any message/comment:
- [ ] Does this provide value?
- [ ] Is this personalized?
- [ ] Would I say this in real life?
- [ ] Does this violate platform ToS?
- [ ] Is this sustainable?
```

### 4.2 Bene2Luxe Promoter - Personality

File: `subworkers/bene2luxe-promoter/personality.md`

```markdown
# Bene2Luxe Promoter - Personality & Workflow

**Agent:** bene2luxe-promoter  
**Business:** Bene2Luxe (Luxury Fashion Resale)  
**Mission:** Promote luxury fashion resale to French/Swiss market

## Platforms

| Priority | Platform | Actions |
|----------|----------|---------|
| HIGH | Instagram | Like, comment, DM, story |
| HIGH | TikTok | Comment, engage |
| HIGH | Facebook Marketplace | Browse, message sellers |
| MEDIUM | Snapchat | Add users, stories |

## Tools Available

### Primary Tools

1. **instagrapi** - Instagram automation
   ```bash
   pip install instagrapi
   ```

2. **agent-browser** - Browser automation for TikTok comments
   ```bash
   # Use with Kameleo or Multilogin
   ```

3. **facebook-marketplace-mcp** - FB Marketplace
   ```bash
   npx -y @jdcodes1/facebook-marketplace-mcp
   ```

4. **TikTokApi** - Read-only TikTok data
   ```bash
   pip install TikTokApi
   ```

## Engagement Rules

### Instagram

1. **Search targets:**
   - Hashtags: #luxuryfashion #designerbags #hermes #chanel #louisvuitton #balenciaga
   - Accounts: Luxury resellers, fashion influencers
   - Locations: Paris, Geneva, Zurich, Lausanne

2. **Engagement strategy:**
   - Like and comment on relevant posts
   - DM interested buyers who comment
   - Story replies

3. **Rate limits (instagrapi):**
   - ~200 actions/hour for new accounts
   - ~500 actions/hour for aged accounts
   - USE DELAY: `Client(delay_range=[10, 30])`

4. **Caption examples (French):**
   - "Magnifique pièces ! 🎀" (Beautiful piece!)
   - "SuperbeFindeswahl! Welches Farbe?" (Great choice! Which color?)
   - "Encore dispo?" (Still available?)

### TikTok

⚠️ **CRITICAL:** No public API for commenting. Use browser automation only.

1. **Target content:**
   - #luxuryfashion #designer #handbag
   - Luxury fashion review videos
   - "Get ready with me" fashion videos

2. **Browser automation:**
   - Use agent-browser with anti-detect profile
   - Manual comment typing (simulate human)
   - Random timing (30-120 seconds between)

3. **Rate limits:**
   - 10-20 comments/day max
   - Spread throughout the day

### Facebook Marketplace

⚠️ **CRITICAL:** No public API for posting. Read-only + messaging.

1. **Search for:**
   - Keywords: Hermès, Chanel, Louis Vuitton, Cartier
   - Locations: Paris, Lyon, Genève
   - Price range: €500-5000

2. **Strategy:**
   - Browse listings (no automated posting)
   - Message sellers with interest
   - Build relationships

3. **Messaging template:**
   - "Bonjour! Je suis intéressé(e) par cet article. Est-il toujours disponible?"
   - (Hello! I'm interested in this item. Is it still available?)

### Snapchat

⚠️ **LIMITED:** No public API for adding users.

1. **Strategy:**
   - Use Snapchat Ads (Marketing API) for reach
   - Manual user adding via device only
   - Focus on Ad campaigns, not organic

## Prohibited Actions

- ❌ Selling counterfeit items
- ❌ Posting fake luxury items
- ❌ Spam DMs
- ❌ Price deception
- ❌ Buying fake followers

## Success Metrics

| Metric | Target |
|--------|--------|
| Instagram engagement | +100 likes/day |
| DM conversations | 10/day |
| Sales leads | 3/week |

## Warm-Up Protocol

**Week 1:** 20 likes/day, 5 comments/day
**Week 2:** 40 likes/day, 10 comments/day
**Week 3+:** 60 likes/day, 15 comments/day

## Human-like Behavior (CRITICAL)

- ✅ Use French in comments (the target market)
- ✅ Varied, natural language
- ✅ Mix of short and long comments
- ✅ Respond to stories
- ❌ NEVER USE EMOJIS EXCESSIVELY (1-2 max)
- ❌ Don't sound like a bot

## Language Guidelines (French Market)

| English | French |
|---------|--------|
| "Great bag!" | "Superbe sac !" |
| "Love this" | "J'adore !" |
| "What price?" | "Quel prix ?" |
| "Is it available?" | "Encore dispo ?" |
| "Beautiful" | "Magnifique" |
```

---

## 5. LaunchAgent Setup

### 5.1 Install CoBou Promoter

```bash
cd /Users/vakandi/EliaAI

# Create plist for CoBou Promoter (every 30 min, 09:00-21:00)
cat > plists/com.elia.cobou-promoter.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.elia.cobou-promoter</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>/Users/vakandi/EliaAI/scripts/trigger_cobou_promoter.sh</string>
    </array>
    
    <key>RunAtLoad</key>
    <false/>
    
    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>11</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>16</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>17</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>30</integer></dict>
    </array>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Users/vakandi/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>/Users/vakandi</string>
    </dict>
    
    <key>WorkingDirectory</key>
    <string>/Users/vakandi/EliaAI</string>
    
    <key>StandardOutPath</key>
    <string>/Users/vakandi/EliaAI/logs/promoter_cobou.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/vakandi/EliaAI/logs/promoter_cobou.log</string>
</dict>
</plist>
EOF

# Load the agent
launchctl load plists/com.elia.cobou-promoter.plist

echo "CoBou Promoter installed!"
```

### 5.2 Install Bene2Luxe Promoter

```bash
cd /Users/vakandi/EliaAI

# Create plist for Bene2Luxe Promoter (every 20 min, 10:00-22:00)
cat > plists/com.elia.bene2luxe-promoter.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.elia.bene2luxe-promoter</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>/Users/vakandi/EliaAI/scripts/trigger_bene2luxe_promoter.sh</string>
    </array>
    
    <key>RunAtLoad</key>
    <false/>
    
    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>11</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>11</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>16</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>16</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>17</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>17</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>40</integer></dict>
        <dict><key>Hour</key><integer>21</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>21</integer><key>Minute</key><integer>20</integer></dict>
        <dict><key>Hour</key><integer>21</integer><key>Minute</key><integer>40</integer></dict>
    </array>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Users/vakandi/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>/Users/vakandi</string>
    </dict>
    
    <key>WorkingDirectory</key>
    <string>/Users/vakandi/EliaAI</string>
    
    <key>StandardOutPath</key>
    <string>/Users/vakandi/EliaAI/logs/promoter_bene2luxe.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/vakandi/EliaAI/logs/promoter_bene2luxe.log</string>
</dict>
</plist>
EOF

# Load the agent
launchctl load plists/com.elia.bene2luxe-promoter.plist

echo "Bene2Luxe Promoter installed!"
```

### 5.3 Trigger Scripts

File: `scripts/trigger_cobou_promoter.sh`

```bash
#!/bin/zsh
# CoBou Promoter - Trigger Script

AGENT_DIR="/Users/vakandi/EliaAI"
LOG_FILE="$AGENT_DIR/logs/promoter_cobou.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting CoBou Promoter..." >> "$LOG_FILE"

# Set model from .opencode_model or default
if [[ -f "$AGENT_DIR/.opencode_model" ]]; then
    MODEL=$(cat "$AGENT_DIR/.opencode_model")
else
    MODEL="big-pickle"
fi

# Build the prompt for cobou-promoter
PROMPT="You are cobou-promoter. Run your promotion workflow for CoBou Agency (B2B web dev).

Execute ONE engagement action:
- LinkedIn: Find 1 relevant post and comment OR send 1 connection request with message
- X (Twitter): Find 1 relevant post and engage
- Reddit: Find 1 relevant thread and provide value

Focus on: web development, React, startups looking for developers.

Remember:
- ALWAYS be helpful, not salesy
- NEVER spam
- Use human-like language and timing

Complete your task and report what you did."

# Run with OpenCode
cd "$AGENT_DIR"
oh-my-opencode run -a cobou-promoter "$PROMPT"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] CoBou Promoter completed" >> "$LOG_FILE"
```

File: `scripts/trigger_bene2luxe_promoter.sh`

```bash
#!/bin/zsh
# Bene2Luxe Promoter - Trigger Script

AGENT_DIR="/Users/vakandi/EliaAI"
LOG_FILE="$AGENT_DIR/logs/promoter_bene2luxe.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Bene2Luxe Promoter..." >> "$LOG_FILE"

# Set model from .opencode_model or default
if [[ -f "$AGENT_DIR/.opencode_model" ]]; then
    MODEL=$(cat "$AGENT_DIR/.opencode_model")
else
    MODEL="big-pickle"
fi

# Build the prompt for bene2luxe-promoter
PROMPT="You are bene2luxe-promoter. Run your promotion workflow for Bene2Luxe (luxury fashion resale).

Execute ONE engagement action:
- Instagram: Find 1 relevant post (luxury bags/fashion), like AND comment in French
- TikTok: Browse and engage with luxury fashion content (if using browser)
- Facebook Marketplace: Browse luxury listings and message 1 seller

Focus on: Hermès, Chanel, Louis Vuitton, luxury fashion.

Remember:
- Use French language for comments
- Be authentic, not salesy
- NEVER use excessive emojis
- Use natural, varied language

Complete your task and report what you did."

# Run with OpenCode
cd "$AGENT_DIR"
oh-my-opencode run -a bene2luxe-promoter "$PROMPT"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bene2Luxe Promoter completed" >> "$LOG_FILE"
```

### 5.4 Make Scripts Executable

```bash
chmod +x /Users/vakandi/EliaAI/scripts/trigger_cobou_promoter.sh
chmod +x /Users/vakandi/EliaAI/scripts/trigger_bene2luxe_promoter.sh
```

---

## 6. Tools & Libraries

### 6.1 Installation

```bash
# Install Python libraries
pip install instagrapi
pip install linkedin-scraper
pip install TikTokApi

# Or use uv (faster)
uv pip install instagrapi linkedin-scraper TikTokApi
```

### 6.2 Configuration for instagrapi

```python
# ~/.instagrapi_config.py
from instagrapi import Client

cl = Client(
    delay_range=[10, 30],  # Random delay between actions
    username="your_username",
    password="your_password"
)

# Save session
cl.dump_settings("session.json")

# Load session (for reuse)
cl.load_settings("session.json")
```

### 6.3 Configuration for linkedin-scraper

```python
# Using li_at cookie
from linkedin_scraper import Linkedin

# Requires LinkedIn session cookie (li_at)
client = Linkedin(li_at="your_cookie_here")
profile = client.get_profile("target_username")
```

---

## 7. MCP Servers

### 7.1 Available MCP Servers

#### Social Media MCP Servers

| Server | NPM/GitHub | Platforms | Capabilities |
|--------|-----------|----------|------------|
| **@mcpware/instagram-mcp** | [npm](https://www.npmjs.com/package/@mcpware/instagram-mcp) | Instagram | 23 tools - posts, comments, DMs, stories, insights |
| **facebook-marketplace-mcp** | [GitHub](https://github.com/jdcodes1/facebook-marketplace-mcp) | Facebook Marketplace | Search listings, browse (read-only) |
| **x-mcp-server** | [GitHub](https://github.com/Lnxtanx/x-mcp-server) | X/Twitter | 54+ tools - post, delete, search, interact |
| **PostPulse** | [GitHub](https://github.com/PostPulse/mcp-server-postpulse) | Multi-platform | IG, FB, YouTube, TikTok, LinkedIn, X, Threads |
| **Outstand** | [mcphub.io](https://mcphub.io/servers/outstand) | Multi-platform | 10 platforms, 25 tools |
| **Publora** | [publora.com](https://publora.com) | Multi-platform | 10 platforms scheduling |

#### Browser Automation MCP

| Server | NPM/GitHub | Capabilities |
|--------|-----------|------------|
| **Playwright MCP** | `@playwright/mcp` | Navigation, clicking, forms, snapshots |
| **agent-browser-mcp** | [GitHub](https://github.com/quantmew/agent-browser-mcp) | Full Playwright API + 44 tools |

### 7.2 Installation Commands

```bash
# Instagram MCP (requires Business account)
npx -y @mcpware/instagram-mcp

# Facebook Marketplace MCP
npx -y @jdcodes1/facebook-marketplace-mcp

# X/Twitter MCP
npx -y @mcpware/x-mcp-server

# Playwright MCP (browser automation)
npx -y @playwright/mcp@latest

# agent-browser MCP (enhanced)
npm install -g agent-browser-mcp-server
```

### 7.3 MCP Configuration

File: `~/.config/mcp/mcp_servers.json`

```json
{
  "instagram": {
    "command": "npx",
    "args": ["-y", "@mcpware/instagram-mcp"],
    "env": {
      "INSTAGRAM_ACCESS_TOKEN": "your_token"
    }
  },
  "facebook-marketplace": {
    "command": "npx",
    "args": ["-y", "@jdcodes1/facebook-marketplace-mcp"]
  },
  "x-twitter": {
    "command": "npx",
    "args": ["-y", "@mcpware/x-mcp-server"],
    "env": {
      "X_API_KEY": "your_api_key"
    }
  },
  "agent-browser": {
    "command": "npx",
    "args": ["-y", "agent-browser-mcp-server"],
    "env": {
      "BROWSER_PROFILE": "~/.agent-browser-profile"
    }
  },
  "playwright": {
    "command": "npx",
    "args": ["-y", "@playwright/mcp"]
  }
}
```

### 7.4 Restart MCP CLI

```bash
# Kill existing MCP processes and restart
pkill -f mcp
mcp-cli &

# Verify servers are running
mcp-cli list
```

### 7.5 Using MCP Tools in Prompts

```python
# Example: Using mcp-cli to call Instagram MCP
mcp-cli call instagram get_media_posts '{"username": "luxuryfashion", "count": 10}'

# Example: Using Facebook Marketplace search
mcp-cli call facebook-marketplace search_listings '{"query": "Hermes bag", "location": "Paris"}'

# Example: Browser navigation
mcp-cli call playwright browser_navigate '{"url": "https://instagram.com"}'
```

### 7.6 Remote MCP Servers (No Install)

For MCP CLI with remote hosted servers:

```json
{
  "mcpServers": {
    "outstand": {
      "url": "https://mcp.outstand.so/mcp",
      "headers": {
        "Authorization": "Bearer ost_your_key"
      }
    },
    "postpulse": {
      "url": "https://mcp.post-pulse.com"
    }
  }
}
```

### 7.7 MCP Resources

| Resource | URL |
|----------|-----|
| **Official MCP Servers** | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **MCP Repository** | [mcprepository.com](https://mcprepository.com) |
| **Awesome MCP Servers** | [wong2/awesome-mcp](https://github.com/wong2/awesome-mcp) |
| **MCP Hub** | [mcphub.io](https://mcphub.io) |

---

## 8. Workflows & Reporting

### 8.1 CoBou Promoter - B2B Workflow

#### Objective
Generate B2B leads for CoBou Agency (web development, software, AI implementation services).

#### Reporting Channels

| Priority | Channel | When |
|----------|---------|------|
| **EMERGENCY** | WhatsApp - COBOU PowerRangers (`120363420711538035@g.us`) | Blockers, urgent issues, client emergencies |
| **REGULAR** | Discord - **COBOU AGENCY** category (`1489244768235028633`) | Leads contacted, negotiations, progress |
| **FALLBACK** | Discord - #reports (`1489244810777727046`) | Only if Discord fails |

#### Discord Channel IDs (COBOU AGENCY)

| Channel | ID | Purpose |
|---------|-----|---------|
| 🚀-projects | `1489244906013593642` | Active projects |
| 👥-clients | `1489244911449538680` | Client leads & negotiations |
| 💻-dev-work | `1489244916352684045` | Dev tasks |
| 💰-invoices | `1489244921180455035` | Invoices |

#### Workflow Steps

```
STEP 1: DISCOVERY (10 min)
├── Search LinkedIn for: "web developer", "React", "need a website", "startup"
├── Search X/Twitter for: #webdev #freelance #startup
├── Search Reddit for: r/webdev, r/freelance, r/reactjs
└── Identify potential client needs
    → Record leads to memory/context

STEP 2: QUALIFICATION (10 min)
├── Analyze: Do they need a website/app/AI?
├── Budget indicator: Startup stage, funding
├── Timeline: Urgent or exploratory?
├── Decision maker?
└── Score: Hot/Warm/Cold

STEP 3: ENGAGEMENT (15 min)
├── LinkedIn: Comment with value + connect request
├── X: Reply with helpful insight
├── Reddit: Answer question with expertise
└── Personalized message (NOT template)
    → Use mcp-cli for LinkedIn/Telegram/Discord

STEP 4: NURTURE (15 min)
├── Follow up within 48h if no response
├── Share relevant case study
├── Ask about their project
└── Propose consultation call
```

#### Report Format (Discord)

```markdown
# CoBou Promoter Report - {DATE}

## Leads Contacted: {N}
| Platform | Name | Company | Need | Status | Next Step |
|---------|------|--------|------|--------|---------|
| LinkedIn | [Name] | [Company] | [Need] | [Hot/Warm/Cold] | [Next Action] |

## Pipeline Update
- 🔥 Hot: {N}
- 🔶 Warm: {N}
- ❄️ Cold: {N}

## Conversations Started: {N}
[Brief summary of each conversation]

## Blockers/Issues
[Any issues needing attention]

## Tomorrow's Focus
[Priority targets for next run]
```

#### Client Needs Discovery Questions

When engaging, ask to understand pain:

| Question | Purpose |
|----------|---------|
| "What's your current process for X?" | Understand workflow |
| "What's the biggest pain point?" | Find problem |
| "How do you handle X today?" | Current solution |
| "What's your timeline?" | Urgency |
| "What's your budget range?" | Fit assessment |
| "Who makes the decision?" | Decision maker |

---

### 8.2 Bene2Luxe Promoter - B2C Workflow

#### Objective
Engage with luxury fashion community, find buyers, promote Bene2Luxe resale.

#### Reporting Channels

| Priority | Channel | When |
|----------|---------|------|
| **EMERGENCY** | WhatsApp - B2LUXE BUSINESS (`120363408208578679@g.us`) | Client wants product we don't have, supplier issue |
| **REGULAR** | Discord - **BEN2LUXE** category (`1489244764808417320`) | Engagement data, leads found, products talked about |
| **FALLBACK** | Discord - #reports (`1489244810777727046`) | Only if Discord fails |

#### Discord Channel IDs (BEN2LUXE)

| Channel | ID | Purpose |
|---------|-----|---------|
| 🛍️-products | `1489244857250615416` | Product updates |
| 📦-orders | `1489244862871244950` | Orders |
| 👥-clients | `1489244868235755580` | Client leads |
| 📱-social-media | `1489244873847734292` | Social engagement |
| 📤-marketing | `1489244878431846523` | Marketing campaigns |

#### Workflow Steps

```
STEP 1: COMMUNITY DISCOVERY (10 min)
├── Search Instagram: #luxuryfashion #designerbags #hermes #chanel
├── Search TikTok: luxury fashion, designer bags
├── Search FB Marketplace: Hermès, Chanel, LV (browse only)
└── Identify trending topics/products
    → Note communities talking about what

STEP 2: ENGAGEMENT (15 min)
├── Instagram: Like + comment (in French!)
├── TikTok: Comment on relevant videos (via browser)
├── FB Marketplace: Browse, message sellers (no posting)
└── Story replies
    → Use instagrapi + agent-browser

STEP 3: LEAD IDENTIFICATION (10 min)
├── Who is asking about products we have?
├── Who wants something we DON'T have?
├── Who is looking for specific brand?
└── Flag: "Wants X, we don't have" → URGENT report to WhatsApp
    → Check supplier list (yupo store)

STEP 4: OPPORTUNITY (10 min)
├── DM interested buyers
├── Share relevant inventory
├── Offer to find specific items
└── If can't find: Report to WhatsApp with margin inquiry
    → "Client wants [ITEM] - margin potential [€X] - escalate?"
```

#### Supplier Flag (URGENT to WhatsApp)

When a client wants a product we don't have:

```
Message to B2LUXE BUSINESS (WhatsApp):
⚠️ LEAD: [Client interest]
- Product: [Item]
- Brand: [Brand]
- Budget: [Client's budget]
- Our margin: [If known]
- Supplier needed: YES - check yupo store + contacts
ACTION REQUIRED: Can we source this?
```

#### Report Format (Discord)

```markdown
# Bene2Luxe Promoter Report - {DATE}

## Engagement: {N}
| Platform | Type | Content | Result |
|---------|------|--------|--------|
| IG | Comment | [On post] | [Response?] |
| TikTok | Comment | [On video] | [Response?] |
| FB | Message | [To seller] | [Response?] |

## Products in Demand: {N}
| Brand | Item | Demand Level |
|-------|------|------------|
| [Brand] | [Item] | High/Medium |

## Supplier Gaps: {N}
[Items clients want but we don't have - escalate to team]

## Leads to Follow: {N}
[Names + what they want + contact]

## Tomorrow's Focus
[Priority hashtags, accounts, products]
```

---

### 8.3 Reporting Commands

#### Send to Discord (via mcp-cli)

```bash
# COBU AGENCY - clients channel
mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244911449538680","content":"# CoBou Promoter Report - {DATE}\n\n[Your report content]"}'

# BEN2LUXE - clients channel  
mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244868235755580","content":"# Bene2Luxe Promoter Report - {DATE}\n\n[Your report content]"}'
```

#### Send to WhatsApp (Emergency Only)

```bash
# CoBou PowerRangers (emergency)
mcp-cli call whatsapp send_message '{"chat_jid":"120363420711538035@g.us","message":"[Report]"}'

# B2LUXE BUSINESS (emergency)
mcp-cli call whatsapp send_message '{"chat_jid":"120363408208578679@g.us","message":"[Report]"}'
```

---

## 9. Implementation Detail - DO NOT SKIP

**CRITICAL: Avant de commencer l'implémentation, lis d'abord TOUTE cette section 9.**

Cette section contient des prompts détaillés pour implémenter chaque partie du système. Chaque étape doit être exécutée dans l'ordre.

---

### 9.1 CRÉER LES DOSSIERS - Step 1

**Objectif:** Créer la structure de dossiers pour les subworkers.

**Action à exécuter dans ton terminal:**

```bash
mkdir -p /Users/vakandi/EliaAI/subworkers/cobou-promoter
mkdir -p /Users/vakandi/EliaAI/subworkers/bene2luxe-promoter
mkdir -p /Users/vakandi/EliaAI/subworkers/scripts
mkdir -p /Users/vakandi/EliaAI/subworkers/plists
mkdir -p /Users/vakandi/EliaAI/subworkers/logs
```

**Vérification:**
```bash
ls -la /Users/vakandi/EliaAI/subworkers/
# Doit afficher:
# - cobou-promoter/
# - bene2luxe-promoter/
# - scripts/
# - plists/
# - logs/
```

---

### 9.2 CRÉER LE PROMPT COBOU PROMOTER - Step 2

**Objectif:** Générer le fichier PROMPT.md complet pour l'agent CoBou Promoter.

**Contexte à lire d'abord:**
- Lis la section 8.1 de CE document (workflow CoBou)
- Lis la section 7 (Tools & Libraries) pour les outils disponibles
- Lis TOOLS.md pour les commandes MCP

**Prompt détaillé à copier dans OpenCode:**

```
/ulw-loop

Tu dois créer le fichier /Users/vakandi/EliaAI/subworkers/cobou-promoter/PROMPT.md

CONTEXTE À UTILISER:
1. Lis d'abord /Users/vakandi/EliaAI/subworkers/SUBWORKERS_SYSTEM.md section 8.1 (workflow CoBou B2B)
2. Lis /Users/vakandi/EliaAI/context/TOOLS.md sections MCP-CLI et Discord

STRUCTURE DU FICHIERÀ CRÉER:

# CoBou Promoter - PROMPT.md

## Identity
Tu es COBOU PROMOTER, agent IA autonome pour CoBou Agency.
Mission: Générer des leads B2B pour services web dev/AI/logiciels.

## Platforms Cibles
| Priority | Platform | Actions |
|----------|----------|---------|
| HIGH | LinkedIn | Comment, Connect, Message |
| HIGH | X (Twitter) | Reply, Engage |
| MEDIUM | Reddit | Answer, Comment |

## Outils Disponibles
1. **linkedin-scraper** (pip install linkedin-scraper) - Profiles, companies
2. **X MCP Server** - Twitter actions
3. **mcp-cli** - WhatsApp, Discord, Telegram
4. **agent-browser** - Browser automation

## Canaux de Reporting
| Canal | ID | Usage |
|-------|-----|-------|
| Discord #clients COBOU | 1489244911449538680 | Rapports réguliers |
| WhatsApp COBOU PowerRangers | 120363420711538035@g.us | URGENT uniquement |

## Workflow (Section 8.1 référence)
```
DISCOVERY (10min) → QUALIFICATION (10min) → ENGAGEMENT (15min) → NURTURE (15min)
```

## Questions Découverte Client
| Question | Objectif |
|----------|---------|
| "Quel est votre process actuel pour X?" | Comprendre workflow |
| "Quel est le plus gros problème?" | Trouver douleur |
| "Comment gérez-vous X aujourd'hui?" | Solution actuelle |
| "Quelle est votre timeline?" | Urgence |
| "Quelle est votre budget?" | Évaluation fit |
| "Qui décide?" | Decision maker |

## Lead Scoring
| Score | Criteria |
|-------|----------|
| 🔥 Hot | Budget + Timeline + Decision maker identifié |
| 🔶 Warm | Besoin clair mais no timeline/budget |
| ❄️ Cold | Exploratoire, pas de besoin clair |

## Warm-Up Protocol
- Semaine 1: 10 connexions/jour, 5 messages/jour
- Semaine 2: 20 connexions/jour, 10 messages/jour
- Semaine 3+: 30 connexions/jour, 20 messages/jour

## Actions Interdites
- ❌ Mass DM génériques
- ❌ Templatescopiés-collés
- ❌ Achat de connexions
- ❌ Promesses de timeline impossibles

## Format Report (Discord)
```markdown
# CoBou Promoter Report - {DATE}

## Leads Contactés: {N}
| Platform | Name | Company | Need | Status | Next Step |
|---------|------|--------|------|--------|---------|
| LinkedIn | [Name] | [Company] | [Need] | [Hot/Warm/Cold] | [Next Action] |

## Pipeline
- 🔥 Hot: {N}
- 🔶 Warm: {N}
- ❄️ Cold: {N}

## Conversations: {N}
[Résumé]

## Blockers
[Issues�� attention]

## Demain
[Priority]
```

## Commandes Reporting (depuis TOOLS.md)
```bash
# Discord
mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244911449538680","content":"[REPORT]"}'

# WhatsApp URGENT
mcp-cli call whatsapp send_message '{"chat_jid":"120363420711538035@g.us","message":"[URGENT]"}'
```

CRÉER LE FICHIER MAINTENANT.
--completion-promise DONE --max-iterations 0
```

**Vérification après création:**
```bash
cat /Users/vakandi/EliaAI/subworkers/cobou-promoter/PROMPT.md | head -50
# Doit contenir: Identity, Platforms, Outils, Workflow, etc.
```

---

### 9.3 CRÉER LE PROMPT BENE2LUXE PROMOTER - Step 3

**Objectif:** Générer le fichier PROMPT.md complet pour l'agent Bene2Luxe Promoter.

**Contexte à lire d'abord:**
- Lis la section 8.2 de CE document (workflow Bene2Luxe B2C)
- Lis section 7 (Tools & Libraries)
- Lis TOOLS.md

**Prompt détaillé à copier dans OpenCode:**

```
/ulw-loop

Tu dois créer le fichier /Users/vakandi/EliaAI/subworkers/bene2luxe-promoter/PROMPT.md

CONTEXTE À UTILISER:
1. Lis d'abord /Users/vakandi/EliaAI/subworkers/SUBWORKERS_SYSTEM.md section 8.2 (workflow Bene2Luxe B2C)
2. Lis /Users/vakandi/EliaAI/context/TOOLS.md sections MCP-CLI, WhatsApp, Discord

STRUCTURE DU FICHIERÀ CRÉER:

# Bene2Luxe Promoter - PROMPT.md

## Identity
Tu es BENE2LUXE PROMOTER, agent IA autonome pour Bene2Luxe.
Mission: Engager avec la communauté mode luxe, trouver des acheteurs, promouvoir revente.

## Platforms Cibles
| Priority | Platform | Actions |
|----------|----------|---------|
| HIGH | Instagram | Like, Comment, DM, Story |
| HIGH | TikTok | Comment (browser only) |
| HIGH | FB Marketplace | Browse, Message |
| MEDIUM | Snapchat | Ads uniquement |

## Outils Disponibles
1. **instagrapi** (pip install instagrapi) - IG automation
2. **TikTokApi** (pip install TikTokApi) - TikTok (read-only)
3. **agent-browser** - Browser automation for TikTok comments
4. **mcp-cli** - WhatsApp, Discord

## Canaux de Reporting
| Canal | ID | Usage |
|-------|-----|-------|
| Discord #clients BEN2LUXE | 1489244868235755580 | Rapports réguliers |
| WhatsApp B2LUXE BUSINESS | 120363408208578679@g.us | URGENT - produits manquants |

## Workflow (Section 8.2 référence)
```
DISCOVERY (10min) → ENGAGEMENT (15min) → LEAD ID (10min) → OPPORTUNITY (10min)
```

## Langue Guidelines (Marché Français)
| English | French |
|---------|--------|
| "Great bag!" | "Superbe sac !" |
| "Love this" | "J'adore !" |
| "What price?" | "Quel prix ?" |
| "Still available?" | "Encore dispo ?" |

## Warm-Up Protocol
- Semaine 1: 20 likes/jour, 5 commentaires/jour
- Semaine 2: 40 likes/jour, 10 commentaires/jour
- Semaine 3+: 60 likes/jour, 15 commentaires/jour

## PROTOCOLE SUPPLIER FLAG (CRITICAL)
Quand un client veut un produit QUE NOUS N'AVONS PAS:
1. NOTER: Produit, Marque, Budget client
2. Envoyer URGENT à WhatsApp B2LUXE BUSINESS:
   "⚠️ LEAD: [produit] - [marque] - budget [€X]"
3. Demander si on peut sourcer + marge

## Actions Interdites
- ❌ Vente de contrefaçon
- ❌ Spam DMs
- ❌ Trop d'emojis (1-2 max)
- ❌ Sons robotiques

## Format Report (Discord)
```markdown
# Bene2Luxe Promoter Report - {DATE}

## Engagement: {N}
| Platform | Type | Content | Result |
|---------|------|--------|--------|
| IG | Comment | [Sur post] | [Réponse?] |
| TikTok | Comment | [Sur video] | [Réponse?] |
| FB | Message | [À vendeur] | [Réponse?] |

## Produits en Demand: {N}
| Marque | Item | Demande |
|-------|------|---------|
| [Marque] | [Item] | High/Medium |

## Supplier Gaps: {N}
[Items clients veulent mais on a pas - escalader]

## Leads: {N}
[Names + quoi ils veulent + contact]

## Demain
[Priority hashtags, comptes]
```

## Commandes Reporting
```bash
# Discord
mcp-cli call discord-server-mcp discord_send_message '{"channel_id":"1489244868235755580","content":"[REPORT]"}'

# WhatsApp URGENT
mcp-cli call whatsapp send_message '{"chat_jid":"120363408208578679@g.us","message":"[SUPPLIER ISSUE]"}'
```

CRÉER LE FICHIER MAINTENANT.
--completion-promise DONE --max-iterations 0
```

**Vérification après création:**
```bash
cat /Users/vakandi/EliaAI/subworkers/bene2luxe-promoter/PROMPT.md | head -50
```

---

### 9.4 CONFIGURER OPENCOD - Step 4

**Objectif:** Ajouter les agents dans la configuration OpenCode.

**Fichier 1:** `~/.config/opencode/opencode.json`

Ajouter dans la section `"agent"`:

```json
"cobou-promoter": {
  "description": "CoBou Agency B2B promoter - LinkedIn, X, Reddit",
  "mode": "primary"
},
"bene2luxe-promoter": {
  "description": "Bene2Luxe luxury resale promoter - IG, TikTok, FB",
  "mode": "primary"
}
```

**Fichier 2:** `~/.config/opencode/oh-my-openagent.json`

Ajouter dans `"agents"`:

```json
"cobou-promoter": {
  "model": "opencode/big-pickle",
  "mode": "primary",
  "fallback_models": []
},
"bene2luxe-promoter": {
  "model": "opencode/big-pickle",
  "mode": "primary",
  "fallback_models": []
}
```

Ajouter dans `"categories"`:

```json
"cobou-promoter": {
  "model": "opencode/big-pickle",
  "description": "CoBou Agency B2B promoter",
  "prompt_append": "**FIRST: Read /Users/vakandi/EliaAI/subworkers/cobou-promoter/PROMPT.md pour ton workflow complet.**
\n\nTu es cobou-promoter. Utilise les outils de LinkedIn, X, Discord pour générer des leads B2B."
},
"bene2luxe-promoter": {
  "model": "opencode/big-pickle",
  "description": "Bene2Luxe luxury resale promoter",
  "prompt_append": "**FIRST: Read /Users/vakandi/EliaAI/subworkers/bene2luxe-promoter/PROMPT.md pour ton workflow complet.**
\n\nTu es bene2luxe-promoter. Utilise instagrapi, agent-browser pour promouvoir Bene2Luxe."
}
```

Ajouter dans `"agent_display_names"`:

```json
"cobou-promoter": "CoBou Promoter",
"bene2luxe-promoter": "Bene2Luxe Promoter"
```

**Vérification:**
```bash
# Redémarrer OpenCode puis:
# /agents
# Doit afficher cobou-promoter et bene2luxe-promoter
```

---

### 9.5 INSTALLER LES LIBRAIRIES PYTHON - Step 5

```bash
pip install instagrapi
pip install linkedin-scraper
pip install TikTokApi
```

**Alternative plus rapide:**
```bash
uv pip install instagrapi linkedin-scraper TikTokApi
```

**Vérification:**
```bash
python3 -c "from instagrapi import Client; print('instagrapi OK')"
python3 -c "from linkedin_scraper import Linkedin; print('linkedin-scraper OK')"
python3 -c "from TikTokApi import TikTokApi; print('TikTokApi OK')"
```

---

### 9.6 CRÉER LES SCRIPTS DÉCLENCHEURS - Step 6

**Fichier:** `/Users/vakandi/EliaAI/subworkers/scripts/trigger_cobou_promoter.sh`

```bash
#!/bin/zsh
# CoBou Promoter - Trigger Script

AGENT_DIR="/Users/vakandi/EliaAI"
LOG_FILE="$AGENT_DIR/subworkers/logs/promoter_cobou.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting CoBou Promoter..." >> "$LOG_FILE"

# Set model
MODEL=$(cat "$AGENT_DIR/.opencode_model" 2>/dev/null || echo "big-pickle")

# Load the prompt
PROMPT=$(cat "$AGENT_DIR/subworkers/cobou-promoter/PROMPT.md")

# Run with OpenCode - First read the prompt from file, then execute task
cd "$AGENT_DIR"
oh-my-opencode run -a cobou-promoter "Execute ONE promotion task now:
- LinkedIn: Find 1 relevant post, comment + connect
- X: Find 1 relevant post, engage
- Reddit: Answer 1 relevant question

Remember:
- Use French language only when appropriate
- Always be helpful, not salesy
- Report to Discord #clients after

$PROMPT"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] CoBou Promoter completed" >> "$LOG_FILE"
```

**Fichier:** `/Users/vakandi/EliaAI/subworkers/scripts/trigger_bene2luxe_promoter.sh`

```bash
#!/bin/zsh
# Bene2Luxe Promoter - Trigger Script

AGENT_DIR="/Users/vakandi/EliaAI"
LOG_FILE="$AGENT_DIR/subworkers/logs/promoter_bene2luxe.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Bene2Luxe Promoter..." >> "$LOG_FILE"

# Set model
MODEL=$(cat "$AGENT_DIR/.opencode_model" 2>/dev/null || echo "big-pickle")

# Run
cd "$AGENT_DIR"
oh-my-opencode run -a bene2luxe-promoter "Execute ONE promotion task now:
- Instagram: Find 1 luxury post, like + comment in French
- TikTok: Browse luxury fashion content (if browser available)
- FB Marketplace: Browse 1 listing, message seller

Remember:
- Use French for comments
- Use human-like language
- Report to Discord #clients after"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bene2Luxe Promoter completed" >> "$LOG_FILE"
```

**Rendre exécutable:**
```bash
chmod +x /Users/vakandi/EliaAI/subworkers/scripts/trigger_cobou_promoter.sh
chmod +x /Users/vakandi/EliaAI/subworkers/scripts/trigger_bene2luxe_promoter.sh
```

---

### 9.7 CRÉER LES LAUNCHAGENTS - Step 7

**Fichier plist pour CoBou (30 min, 09:00-21:00):**

Voir Section 5.1 dans CE document pour le XML complet. Sauvegarder dans:
`/Users/vakandi/EliaAI/subworkers/plists/com.elia.cobou-promoter.plist`

**Fichier plist pour Bene2Luxe (20 min, 10:00-22:00):**

Voir Section 5.2 dans CE document pour le XML complet. Sauvegarder dans:
`/Users/vakandi/EliaAI/subworkers/plists/com.elia.bene2luxe-promoter.plist`

---

### 9.8 CHARGER LES LAUNCHAGENTS - Step 8

```bash
cd /Users/vakandi/EliaAI/subworkers

# Charger CoBou
launchctl load plists/com.elia.cobou-promoter.plist

# Charger Bene2Luxe
launchctl load plists/com.elia.bene2luxe-promoter.plist

# Vérifier
launchctl list | grep -i promoter
```

---

### 9.9 TEST FINAL - Step 9

```bash
# Tester CoBou manuellement
cd /Users/vakandi/EliaAI/subworkers
./scripts/trigger_cobou_promoter.sh

# Voir le log
tail -f logs/promoter_cobou.log

# Tester Bene2Luxe
./scripts/trigger_bene2luxe_promoter.sh

# Voir le log
tail -f logs/promoter_bene2luxe.log
```

---

## 10. Checklist Final

- [ ] Step 1: Dossiers créés
- [ ] Step 2: PROMPT.md CoBou créé
- [ ] Step 3: PROMPT.md Bene2Luxe créé
- [ ] Step 4: OpenCode configuré
- [ ] Step 5: Librairies Python installées
- [ ] Step 6: Scripts trigger créés + exécutables
- [ ] Step 7: LaunchAgent plists créés
- [ ] Step 8: LaunchAgents chargés
- [ ] Step 9: Test passé

---

## 11. MCP Servers for Reporting (WhatsApp & Discord)

### 11.1 Existing MCP Servers (Already Configured)

From your TOOLS.md:

| Service | Command | For |
|---------|---------|-----|
| WhatsApp | `mcp-cli call whatsapp send_message` | Emergency alerts |
| Discord | `mcp-cli call discord-server-mcp discord_send_message` | Regular reports |

### 11.2 Additional MCP Servers (Optional)

| Server | Install | For |
|--------|---------|-----|
| `@pasympa/discord-mcp` | `npx -y @pasympa/discord-mcp` | 90+ Discord tools |
| `whatsapp-mcp-extended` | Docker | 41 WhatsApp tools |

### 11.3 Configuration

Add to `~/.config/mcp/mcp_servers.json`:

```json
{
  "discord-report": {
    "command": "npx", 
    "args": ["-y", "@pasympa/discord-mcp"],
    "env": {
      "DISCORD_TOKEN": "YOUR_BOT_TOKEN"
    }
  }
}
```

---

## 12. Verification & Testing

### 12.1 Test CoBou Promoter Manually

```bash
cd /Users/vakandi/EliaAI
./scripts/trigger_cobou_promoter.sh
```

Check logs:
```bash
tail -f logs/promoter_cobou.log
```

### 8.2 Test Bene2Luxe Promoter Manually

```bash
cd /Users/vakandi/EliaAI
./scripts/trigger_bene2luxe_promoter.sh
```

Check logs:
```bash
tail -f logs/promoter_bene2luxe.log
```

### 8.3 Verify LaunchAgents

```bash
# Check if running
launchctl list | grep -i promoter

# Show current agents
launchctl list | grep "com.elia"
```

---

## 9. Troubleshooting

### Issue: Account Ban

**Solution:**
1. Stop the LaunchAgent immediately
2. Wait 24-48 hours
3. Reduce action rate
4. Use longer delays between actions
5. Warm up account gradually

### Issue: Rate Limited

**Solution:**
1. Use exponential backoff
2. Add more delay between actions
3. Rotate accounts
4. Use residential proxies

### Issue: MCP Not Connecting

**Solution:**
1. Check MCP server is running: `mcp-cli list`
2. Restart MCP: `pkill -f mcp && mcp-cli &`
3. Verify config: `mcp-cli call <server> list_tools`

---

## 10. Checklist Final

Coche chaque étape quand elle est COMPLÉTÉE:

- [ ] **Step 1:** Dossiers créés
  ```bash
  ls /Users/vakandi/EliaAI/subworkers/
  # Doit显示: cobou-promoter/ bene2luxe-promoter/ scripts/ plists/ logs/
  ```

- [ ] **Step 2:** PROMPT.md CoBou créé
  ```bash
  cat /Users/vakandi/EliaAI/subworkers/cobou-promoter/PROMPT.md | head -30
  ```

- [ ] **Step 3:** PROMPT.md Bene2Luxe créé
  ```bash
  cat /Users/vakandi/EliaAI/subworkers/bene2luxe-promoter/PROMPT.md | head -30
  ```

- [ ] **Step 4:** OpenCode configuré + redémarré
  ```bash
  # Après redémarrage: /agents doit montrer les 2 nouveaux agents
  ```

- [ ] **Step 5:** Librairies Python installées
  ```bash
  python3 -c "import instagrapi, linkedin_scraper, TikTokApi; print('OK')"
  ```

- [ ] **Step 6:** Scripts trigger créés + exécutables
  ```bash
  ls -la /Users/vakandi/EliaAI/subworkers/scripts/
  # Doit montrer: trigger_cobou_promoter.sh, trigger_bene2luxe_promoter.sh (avec *)
  ```

- [ ] **Step 7:** LaunchAgent plists créés
  ```bash
  ls /Users/vakandi/EliaAI/subworkers/plists/
  # Doit montrer: com.elia.cobou-promoter.plist, com.elia.bene2luxe-promoter.plist
  ```

- [ ] **Step 8:** LaunchAgents chargés et actifs
  ```bash
  launchctl list | grep -i promoter
  # Doit montrer: com.elia.cobou-promoter, com.elia.bene2luxe-promoter
  ```

- [ ] **Step 9:** Test réussi - rapport Discord envoyé
  ```bash
  # Vérifier dans Discord #clients: rapport received
  tail -50 /Users/vakandi/EliaAI/subworkers/logs/promoter_cobou.log
  ```

---

**QUESTIONS FRÉQUENTES**

| Question | Réponse |
|----------|---------|
| Le bot ne répond pas | Vérifier: `launchctl list \| grep -i promoter` |
| MCP pas connect | `mcp-cli list` + restart si besoin |
| Rate limit atteint | Attendre 1h + réduire fréquence |
| Ban account | Arrêter immédiatement, attendre 24-48h |

---

**End of Guide**