# Subworkers Tools Setup - Complete Prompt

---

Tu dois installer et configurer TOUS les outils nécessaires pour les promoters afin qu'ils puissent:

1. **Instagram**: Liker, commenter, poster, récupérer photos/vidéos de posts
2. **TikTok**: Commenter, liker, récupérer vidéos
3. **Facebook Marketplace**: Poster des annonces, gérer listings, messenger
4. **X/Twitter**: Poster, liker, commenter, retweeter
5. **LinkedIn**: Post, commenter, connexions, messages
6. **MCP Vision**: Analyser les photos des posts (via skill vision-mcp)

---

## 1. MCP Servers - Installer

```bash
# Core Social Media
npx -y @mcpware/instagram-mcp          # Instagram: posts, comments, DMs, stories, media
npx -y @mcpware/x-mcp-server            # X/Twitter: post, like, retweet, reply, search
npx -y @jdcodes1/facebook-marketplace-mcp # FB Marketplace: post, search, message

# Browser Automation (pour TikTok + actions complexes)
npx -y @playwright/mcp@latest           # Navigation, clicks, forms, screenshots
npm install -g agent-browser-mcp-server  # 44 tools - full browser control

# MCP Vision (pour analyser les photos)
# Voir skill vision-mcp pour configuration
```

---

## 2. Configuration MCP - ~/.config/mcp/mcp_servers.json

```json
{
  "instagram": {
    "command": "npx",
    "args": ["-y", "@mcpware/instagram-mcp"],
    "env": {
      "INSTAGRAM_USERNAME": "ton_username",
      "INSTAGRAM_PASSWORD": "ton_password"
    }
  },
  "x-twitter": {
    "command": "npx", 
    "args": ["-y", "@mcpware/x-mcp-server"],
    "env": {
      "X_API_KEY": "ton_api_key",
      "X_API_SECRET": "ton_api_secret",
      "X_BEARER_TOKEN": "ton_bearer_token"
    }
  },
  "facebook-marketplace": {
    "command": "npx",
    "args": ["-y", "@jdcodes1/facebook-marketplace-mcp"],
    "env": {
      "FB_ACCESS_TOKEN": "ton_token"
    }
  },
  "playwright": {
    "command": "npx",
    "args": ["-y", "@playwright/mcp"]
  },
  "agent-browser": {
    "command": "npx",
    "args": ["-y", "agent-browser-mcp-server"],
    "env": {
      "BROWSER_PROFILE": "~/.agent-browser-profile"
    }
  }
}
```

---

## 3. Skills à Activer

Charge ces skills pour les promoters:

```
/skill vision-mcp      # Pour analyser les photos des posts
/skill dev-browser     # Pour browser automation
/skill mcp-cli         # Pour appeler les MCP servers
```

---

## 4. Credentials à Récupérer

| Platform | Credentials Needed |
|----------|-------------------|
| **Instagram** | Username + Password (ou session token) |
| **X/Twitter** | API Key, API Secret, Bearer Token, Access Token |
| **Facebook** | Access Token (Marketing API) |
| **LinkedIn** | li_at cookie (pour linkedin-scraper) |
| **TikTok** | Session (no public API - utiliser browser) |

---

## 5. Python Libraries

```bash
pip3 install instagrapi linkedin-scraper TikTokApi
```

---

## 6. Vérification - Commands à Tester

```bash
# MCP servers running?
mcp-cli list

# Instagram - get recent post
mcp-cli call instagram get_user_media '{"username": "luxuryfashion", "amount": 5}'

# X - search tweets
mcp-cli call x-twitter search_tweets '{"query": "#webdev", "amount": 10}'

# FB Marketplace - search
mcp-cli call facebook-marketplace search_listings '{"query": "Hermes bag", "location": "Paris"}'

# Vision - analyser une image
mcp-cli call vision-mcp analyze_image '{"image_url": "https://..."}'
```

---

## 7. Capabilities Requises par Agent

### cobou-promoter:
- ✅ LinkedIn: Post, comment, connect, message
- ✅ X: Post, like, retweet, reply, search
- ✅ Reddit: Comment, post (via browser)
- ✅ Discord: Send reports (mcp-cli)
- ✅ WhatsApp: Alerts (mcp-cli)

### bene2luxe-promoter:
- ✅ Instagram: Like, comment, post, DM, story, get media
- ✅ TikTok: Comment, like (via browser)
- ✅ FB Marketplace: Post listings, search, message
- ✅ MCP Vision: Analyser photos luxury
- ✅ Discord/WhatsApp: Reports

---

## Output Attendu

Pour chaque outil:
```
✅ [Nom Tool] - Configuré et fonctionnel
   Commands testées: [list]
   
❌ [Nom Tool] - ERREUR
   Error: [message]
   Fix: [solution]
```

Finish avec: **"SETUP COMPLETE - ALL TOOLS READY"**

---

## Fichiers à Mettre à Jour Après

- `~/.config/mcp/mcp_servers.json`
- `~/.instagrapi_config.py`
- OpenCode skills config