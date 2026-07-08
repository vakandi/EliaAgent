---
title: Obsidian Wiki Linking Guide
description: How to create and maintain wiki links in the Elia vault
tags: [obsidian, wiki-links, guide]
created: 2026-04-11
---

# Obsidian Wiki Linking Guide

## Overview

This vault uses **Obsidian wiki links** (`[[link]]`) to create a connected knowledge graph. This guide explains how to properly create and maintain links.

---

## 📝 Link Syntax

### Basic Link
```markdown
[[page-name]]
```

### Link with Display Text
```markdown
[[page-name|Display Text]]
```

### Link to Section
```markdown
[[page-name#section-name]]
```

### Link to File in Subdirectory
```markdown
[[subdirectory/file-name]]
```

### External Link
```markdown
[Display Text](https://example.com)
```

---

## 🏗️ Vault Structure

```
EliaAI/
├── wiki/
│   ├── HOME.md              ← Main hub
│   ├── people/
│   │   ├── Index.md
│   │   ├── Wael.md
│   │   ├── Thomas-Cogne.md
│   │   ├── Rida.md
│   │   └── Ali.md
│   ├── businesses/
│   │   ├── Index.md
│   │   ├── Bene2Luxe.md
│   │   └── CoBou-Agency.md
│   ├── channels/
│   │   ├── Telegram.md
│   │   ├── WhatsApp-COBOU.md
│   │   └── Discord.md
│   ├── systems/
│   │   ├── Elia-System.md
│   │   ├── Jira.md
│   │   └── Docker-Servers.md
│   ├── docs/
│   │   └── Docs-Index.md
│   └── pages/
│       ├── concepts/
│       ├── entities/
│       └── sources/
├── brain/
│   └── index.md
├── context/
│   └── business.md
└── docs/
    └── YYYY-MM-DD/
```

---

## ✅ Linking Rules

### 1. Use Wiki Links for Internal Pages
```markdown
# ✅ Correct
See [[wiki/businesses/Bene2Luxe]] for details.

# ❌ Avoid
See the Bene2Luxe business page for details.
```

### 2. Use Full Path for Clarity
```markdown
# ✅ Better
[[wiki/businesses/Bene2Luxe]]

# ✅ Acceptable (if in same folder)
[[Bene2Luxe]]
```

### 3. Always Add Display Text for Readability
```markdown
# ✅ Good
See [[wiki/businesses/Bene2Luxe|Bene2Luxe]] details.

# ❌ Vague
See [[wiki/businesses/Bene2Luxe]] details.
```

### 4. Link Related Concepts
```markdown
When working with [[people/Wael]], remember to check [[wiki/businesses/Bene2Luxe]].
```

---

## 🏷️ Frontmatter Template

Every new page should include:

```yaml
---
title: Page Title
description: Brief description
tags: [tag1, tag2]
created: 2026-04-11
---
```

---

## 🔗 Link Categories

### People
```
[[wiki/people/Wael]]
[[wiki/people/Thomas-Cogne]]
[[wiki/people/Rida]]
[[wiki/people/Ali]]
[[wiki/people/Anass]]
[[wiki/people/Marco]]
[[wiki/people/Ronen]]
```

### Businesses
```
[[wiki/businesses/Bene2Luxe]]
[[wiki/businesses/CoBou-Agency]]
[[wiki/businesses/ZovaBoost]]
[[wiki/businesses/TikTok-YouTube-Auto]]
[[wiki/businesses/Netfluxe]]
[[wiki/businesses/OGBoujee]]
[[wiki/businesses/Account-Verification]]
[[wiki/businesses/SurfAI]]
```

### Channels
```
[[wiki/channels/Telegram]]
[[wiki/channels/WhatsApp-COBOU]]
[[wiki/channels/WhatsApp-B2LUXE]]
[[wiki/channels/WhatsApp-MAYAVANTA]]
[[wiki/channels/Discord]]
[[wiki/channels/Discord-Reports]]
[[wiki/channels/Email-IONOS]]
[[wiki/channels/Email-Proton]]
```

### Systems
```
[[wiki/systems/Elia-System]]
[[wiki/systems/Jira]]
[[wiki/tools/MCP-Tools]]
[[wiki/systems/Docker-Servers]]
```

### Index Pages
```
[[wiki/HOME]]
[[wiki/index]]
[[wiki/people/Index]]
[[wiki/businesses/Index]]
[[wiki/channels/Index]]
```

---

## 📋 Daily Workflow

When creating or updating a document:

1. **Add wiki links** at the top for related content
2. **Use display text** for readability
3. **Link people** when mentioning team members
4. **Link businesses** when discussing projects
5. **Link channels** when referencing communication

### Example Header
```markdown
> **📎 See also**: [[wiki/HOME|Welcome Hub]] | [[wiki/people/Wael|Wael]] | [[wiki/businesses/Bene2Luxe|Bene2Luxe]]
```

---

## 🔍 Finding Broken Links

To find broken links in Obsidian:
1. Open the vault in Obsidian
2. Go to Settings → Editor → Show broken links
3. Or use the "Check Links" community plugin

---

## 🎯 Best Practices

| Do | Don't |
|----|-------|
| Link to [[wiki/index]] for navigation | Use relative paths |
| Add display text: `[[page|Text]]` | Leave links bare: `[[page]]` |
| Link related concepts | Link unrelated pages |
| Use consistent naming | Mix naming conventions |
| Update links when moving files | Leave broken links |

---

## 🔗 Related

- [[wiki/HOME|Welcome Hub]]
- [[wiki/index|Wiki Index]]
