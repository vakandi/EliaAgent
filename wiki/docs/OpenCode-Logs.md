---
title: OpenCode Session Logs
description: System logs for OpenCode sessions
tags: [logs, system, opencode]
created: 2026-04-11
---

# OpenCode Session Logs

## Overview

System logs tracking OpenCode agent execution.

---

## 📁 Log Locations

```
logs/
├── opencode_interactive_*.log  # Interactive sessions
├── opencode_run_*.log          # Cron runs
├── opencode_morning_run_*.log  # Morning cron
├── prompt_*.txt               # Prompt inputs
└── worker_output_*.txt        # Worker outputs
```

---

## 📊 Log Types

| Pattern | Frequency | Purpose |
|---------|-----------|---------|
| `opencode_interactive_*` | ~100s intervals | User-interactive sessions |
| `opencode_run_*` | Periodic | Background runs |
| `opencode_morning_run_*` | Daily morning | Morning routine |
| `cron_*` | Scheduled | Cron job logs |

---

## 🔧 Access

```bash
# Recent logs
tail -50 logs/opencode_interactive_*.log | tail -1 | xargs tail -50

# Search for errors
grep "ERROR\|CRITICAL" logs/*.log | tail -30
```

---

## 🔗 Related

- [[docs/Docs-Index]]
