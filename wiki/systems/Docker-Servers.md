---
title: Docker Servers
description: Infrastructure servers and containers
tags: [infrastructure, servers, docker]
created: 2026-04-11
---

# Docker Servers

## Overview

Infrastructure servers hosting Wael's businesses and services.

---

## 🖥️ Servers

| Server | Host IP | User | Purpose |
|--------|---------|------|---------|
| **multisaasdeploy** | 157.180.75.87 | vakandi | Main SaaS server |
| **accforge-io** | 165.227.229.50 | root | AccForge server |
| **elia-tunnel** | 65.21.177.242 | root | Elia tunnel |
| **mondialrelay** | 194.87.98.35 | root | MondialRelay server |

---

## 📁 MCP Server Names

```bash
# Main SaaS (Bene2Luxe, ZovaBoost, Netfluxe, OGBoujee)
ssh-server-multisaasdeploy

# AccForge
ssh-mpc-server-accforge-io

# Elia tunnel
ssh-mcp-elia-tunnel

# MondialRelay
ssh-mpc-server-mondialrelay
```

---

## ⚠️ Production Rules

**CRITICAL**: Before restarting Docker in production:
1. Explain reason on [[channels/Telegram]]
2. Update [[memory/MEMORY]]
3. Document the cause of changes

This applies to:
- Docker restarts
- Config modifications
- Deployments

---

## 🔧 Common Commands

```bash
# List running containers
mcp-cli call ssh-server-multisaasdeploy execute-command \
  '{"cmdString":"docker ps"}'

# Check container health
mcp-cli call ssh-server-multisaasdeploy execute-command \
  '{"cmdString":"docker ps --format \"{{.Names}}: {{.Status}}\""}'

# Check website
curl -s -o /dev/null -w "%{http_code}" https://bene2luxe.com
```

---

## 🔗 Related

- [[businesses/Bene2Luxe]]
- [[businesses/ZovaBoost]]
- [[businesses/Netfluxe]]
