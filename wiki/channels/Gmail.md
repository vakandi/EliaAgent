---
title: Gmail (wael.bousfira@gmail.com)
description: Personal Gmail account
tags: [channels, email, personal]
created: 2026-04-11
---

# Gmail

## Overview

| Field | Value |
|-------|-------|
| **Address** | wael.bousfira@gmail.com |
| **Type** | Personal Gmail |
| **Access** | MCP Gmail |

---

## 🔧 MCP Tools

```bash
# Search emails
mcp-cli call gmail search_emails '{"query":"in:inbox newer_than:7d","maxResults":20}'

# Send email
mcp-cli call gmail send_email '{"to":["recipient@email.com"],"subject":"Subject","body":"Body"}'
```

---

## 🔗 Related

- [[channels/Email-Proton]] — Primary business
- [[channels/Email-IONOS]] — Central business
