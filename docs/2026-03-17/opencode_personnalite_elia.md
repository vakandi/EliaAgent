# OpenCode Personnalité Elia - Fichiers de Configuration

Ce document contient les fichiers de configuration nécessaires pour reproduire la personnalité d'Elia sur un autre système OpenCode.

---

## 📁 Fichiers Principaux à Copier

### 1. `~/.config/opencode/AGENTS.md` (375 lignes)

**CHEMIN COMPLET:** `/Users/vakandi/.config/opencode/AGENTS.md`

Ce fichier contient:
- Identité: Elia, "The Goddess of Everything"
- Langue: Français par défaut, Anglais pour MayaVanta
- Style: Concis (max 6 phrases), bullet points + émojis
- Règles: agent-browser pour web, mcp-cli pour MCP tools
- Gestion des businesses: Bene2Luxe, CoBou Agency, ZovaBoost, etc.
- Configuration MCP tools (WhatsApp, Telegram, Discord, Jira)
- Workflow de développement

### 2. `~/.config/opencode/settings.json`

**CHEMIN COMPLET:** `/Users/vakandi/.config/opencode/settings.json`

Configuration modèle et commands.

### 3. `~/.config/opencode/config.json`

**CHEMIN COMPLET:** `/Users/vakandi/.config/opencode/config.json`

Permissions et provider settings.

---

## 📋 Instructions d'Installation

### Étape 1: Créer le répertoire
```bash
mkdir -p ~/.config/opencode/
```

### Étape 2: Copier les fichiers
Copier les 3 fichiers ci-dessus dans `~/.config/opencode/`

### Étape 3: Installer les dépendances

**macOS:**
```bash
npm install -g agent-browser
brew install mcp-cli
```

**Linux/Windows:**
```bash
npm install -g agent-browser
# Installer mcp-cli selon votre OS
```

### Étape 4: Configurer les MCP servers

Créer `~/.config/mcp/mcp_servers.json` avec:
- whatsapp: Pour WhatsApp
- telegram: Pour Telegram
- discord-mcp: Pour Discord
- mcp-atlassian: Pour Jira
- playwright: Pour browser automation
- agent-browser: Pour automation web

### Étape 5: Redémarrer OpenCode

Redémarrer votre instance OpenCode pour charger la nouvelle configuration.

---

## 🔑 Points Clés

1. **AGENTS.md** est le fichier le plus important - il définit:
   - Qui je suis (Elia, The Goddess of Everything)
   - Comment je réponds (6 phrases max, émojis, bullets)
   - Quelle langue utiliser (Français défaut, Anglais pour MayaVanta)
   - Quels outils utiliser pour quelles tâches

2. **Personnalité Elia:**
   - Professionnelle mais chaleureuse
   - Orientée action
   - Concise
   - Utilise des émojis

3. **Outils principaux:**
   - `agent-browser` pour automation web
   - `mcp-cli` pour les services MCP
   - Whisper large-v3 pour transcription vocale

---

## 📞 Support

Si tu as des questions, demande à Wael ou consulter la documentation OpenCode.

---

*Document généré par Elia - 17 Mars 2026*
