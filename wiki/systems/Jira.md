---
title: Jira Projects
description: Task management and durable memory
tags: [system, jira, tasks]
created: 2026-04-11
---

# Jira Projects

## Overview

**Jira** is the ONLY source of truth for tasks and the durable memory of EliaIA.

---

## 📁 Project Mappings

| Business | Project Key | URL |
|----------|-------------|-----|
| Elia IA | ELIA | https://bsbagency.atlassian.net/browse/ELIA |
| Bene2Luxe | BEN | https://bsbagency.atlassian.net/browse/BEN |
| CoBou Agency | COBOUAGENC | https://bsbagency.atlassian.net/browse/COBOUAGENC |
| ZovaBoost (B2C) | ZOVAPANEL | https://bsbagency.atlassian.net/browse/ZOVAPANEL |
| ZovaBoost (B2B) | ZOVAB2B | https://bsbagency.atlassian.net/browse/ZOVAB2B |
| TikTok/YouTube | TIKYT | https://bsbagency.atlassian.net/browse/TIKYT |

---

## 📋 Jira Workflow

### Task Creation
```
Telegram message → Create Jira ticket → Include TG_MSG_ID
WhatsApp message → Create Jira ticket → Add context
Decision needed → Create Jira ticket → Wait for response
```

### MCP Commands
```bash
# Get project issues
mcp-cli call mcp-atlassian jira_get_project_issues '{"project_key":"BEN"}'

# Create issue
mcp-cli call mcp-atlassian create_issue \
  '{"project":"BEN","summary":"...","description":"...","issue_type":"Task"}'
```

---

## ⚠️ Critical Rules

1. **Include Telegram Message ID** in every ticket description
2. **Search before creating** to prevent duplicates
3. **Issue Type** must be exact: `Task`, `Epic`, `Sub-task`, `Bug` (not "Tâche")

---

## 🔗 Related

- [[systems/Elia-System]]
- [[channels/Telegram]]
