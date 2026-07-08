# [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] Personnalité [[../../wiki/people/Elia|Elia]] - Fichiers de Configuration

Ce document contient les fichiers de configuration nécessaires pour reproduire la personnalité d'[[../../wiki/people/Elia|Elia]] sur un autre système [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]].

---

## 📁 Fichiers Principaux à Copier

### 1. `~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/AGENTS.md` (375 lignes)

**CHEMIN COMPLET:** `/Users/vakandi/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/AGENTS.md`

Ce fichier contient:
- Identité: [[../../wiki/people/Elia|Elia]], "The Goddess of Everything"
- Langue: Français par défaut, Anglais pour [[../../wiki/businesses/Mayavanta|MAYAVANTA]]
- Style: Concis (max 6 phrases), bullet points + émojis
- Règles: [[../../wiki/concepts/AI-Automation|Agent]]-browser pour web, [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli pour [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] [[../../wiki/tools/Index|TOOLS]]
- Gestion des businesses: [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]], [[../../wiki/businesses/CoBou-Agency|CoBou]] Agency, [[../../wiki/businesses/ZovaBoost|ZovaBoost]], etc.
- Configuration [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] [[../../wiki/tools/Index|TOOLS]] ([[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]], [[../../wiki/channels/Telegram|Telegram]], [[../../wiki/channels/Discord-EliaWorkSpace|Discord]], [[../../wiki/systems/Jira-Tickets-Index|Jira]])
- Workflow de développement

### 2. `~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/settings.[[../../wiki/concepts/API-Integration|JSON]]`

**CHEMIN COMPLET:** `/Users/vakandi/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/settings.[[../../wiki/concepts/API-Integration|JSON]]`

Configuration modèle et commands.

### 3. `~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/config.[[../../wiki/concepts/API-Integration|JSON]]`

**CHEMIN COMPLET:** `/Users/vakandi/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/config.[[../../wiki/concepts/API-Integration|JSON]]`

Permissions et provider settings.

---

## 📋 Instructions d'Installation

### Étape 1: Créer le répertoire
```bash
mkdir -p ~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/
```

### Étape 2: Copier les fichiers
Copier les 3 fichiers ci-dessus dans `~/.config/[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]/`

### Étape 3: Installer les dépendances

**macOS:**
```bash
npm install -g [[../../wiki/concepts/AI-Automation|Agent]]-browser
brew install [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli
```

**Linux/Windows:**
```bash
npm install -g [[../../wiki/concepts/AI-Automation|Agent]]-browser
# Installer [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli selon votre OS
```

### Étape 4: Configurer les [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] servers

Créer `~/.config/[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]/mcp_servers.[[../../wiki/concepts/API-Integration|JSON]]` avec:
- [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]: Pour [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]
- [[../../wiki/channels/Telegram|Telegram]]: Pour [[../../wiki/channels/Telegram|Telegram]]
- [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]: Pour [[../../wiki/channels/Discord-EliaWorkSpace|Discord]]
- [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-atlassian: Pour [[../../wiki/systems/Jira-Tickets-Index|Jira]]
- [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Playwright|Playwright]]: Pour browser automation
- [[../../wiki/concepts/AI-Automation|Agent]]-browser: Pour automation web

### Étape 5: Redémarrer [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]]

Redémarrer votre instance [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]] pour charger la nouvelle configuration.

---

## 🔑 Points Clés

1. **AGENTS.md** est le fichier le plus [[../../wiki/concepts/Prompt-Engineering|IMPORTANT]] - il définit:
   - Qui je suis ([[../../wiki/people/Elia|Elia]], The Goddess of Everything)
   - Comment je réponds (6 phrases max, émojis, bullets)
   - Quelle langue utiliser (Français défaut, Anglais pour [[../../wiki/businesses/Mayavanta|MAYAVANTA]])
   - Quels outils utiliser pour quelles tâches

2. **Personnalité [[../../wiki/people/Elia|Elia]]:**
   - Professionnelle mais chaleureuse
   - Orientée action
   - Concise
   - Utilise des émojis

3. **Outils principaux:**
   - `[[../../wiki/concepts/AI-Automation|Agent]]-browser` pour automation web
   - `[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli` pour les services [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]
   - Whisper large-v3 pour transcription vocale

---

## 📞 Support

Si tu as des questions, demande à [[../../wiki/people/Wael|Wael]] ou consulter la documentation [[../../wiki/[[../../wiki/skills/Index|SKILLS]]/OpenCode-CLI|OpenCode]].

---

*Document généré par [[../../wiki/people/Elia|Elia]] - 17 Mars 2026*
