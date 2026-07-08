# Discord Server - EliaAI Memory

> **📎 See also**: [[MEMORY|Wiki Hub]] | [[wiki/channels/Index|Channels Wiki]]

---

## ⚠️ CRITICAL RULE: NEVER LEAVE A MESSAGE WITHOUT RESPONSE

**Elia has been FAILING this rule consistently. This is a KNOWN PROBLEM.**

### The Rule:
When ANY message is posted in ANY channel on the Discord server:

1. **ALWAYS respond** - Even if it's just to acknowledge, provide guidelines, ask questions, or update the memory folder
2. **Never ignore user messages** - If someone posts and it's not addressed to Elia, respond anyway
3. **Response types acceptable**:
   - ✅ Acknowledgment + guidelines
   - ✅ Questions to understand the context
   - ✅ "I'll update my memory on this" + update MEMORY file
   - ✅ Direct answer if Elia knows the answer
   - ❌ NEVER: Nothing (no response is unacceptable)

### Why This Matters:
Discord is a communication channel, not just a reporting tool. Users expect responses.

---

## 📋 Server Information

| Field | Value |
|-------|-------|
| **Server** | EliaWorkSpace / AccForge |
| **Purpose** | Development, reports, team coordination |

---

## 📋 Channel Structure

### ELIA-HQ
| Channel | ID | Purpose |
|---------|-----|---------|
| 💡-urgent | 1489244806310793216 | Urgent items |
| 📊-reports | 1489244810777727046 | **Regular reports** |
| 📝-activity-logs | 1489244812107317402 | Activity tracking |
| ✅-tasks-tracker | 1489244818134794330 | Task status |
| 🖥️-health-checks | 1489247935807099020 | Server health |

### COBOU
| Channel | ID | Purpose |
|---------|-----|---------|
| 💻-dev-work | 1489244916352684045 | Development |

### MAYAVANTA
| Channel | ID | Purpose |
|---------|-----|---------|
| 💻-dev | 1489246953861546115 | Development |

### ZOVABOOST
| Channel | ID | Purpose |
|---------|-----|---------|
| 💻-panel | 1489244946673176618 | Panel development |

### TEAM
| Channel | ID | Purpose |
|---------|-----|---------|
| general | 1489244970983624824 | General discussion |
| announcements | 1489244980051710162 | Announcements |

---

## 📊 Channel Splitting Rules

Before sending ANY Discord report, analyze content and send to APPROPRIATE channel:

| Content | Channel | Channel ID |
|---------|---------|------------|
| **URGENT: Blockers, Wael inputs, Team urgent** | #urgent (ELIA-HQ) | `1489244806310793216` |
| Server/MCP status | #health-checks | `1489247935807099020` |
| Bene2Luxe orders | #orders | `1489244862871244950` |
| Bene2Luxe products | #products | `1489244857250615416` |
| Bene2Luxe clients | #clients | `1489244868235755580` |
| CoBou projects | #projects | `1489244906013593642` |
| ZovaBoost panel | #panel | `1489244946673176618` |
| TikTok/YouTube content | #content | `1489244954646679662` |
| MayaVanta concierge | #concierge | `1489244961269485711` |
| Summary (3-5 bullets) | #reports | `1489244810777727046` |

### When to use #urgent:
- Blocker prevents next run (MCP down, auth issue, etc.)
- Wael sent direct input requiring action
- Team urgent request needing immediate attention

---

## 🔧 Discord MCP Tools

```bash
# Check DMs
mcp-cli call discord-mcp discord_get_dms '{"limit":10}'

# Send DM to user
mcp-cli call discord-mcp discord_send_dm '{"user_id":"USER_ID","message":"Hello"}'

# Execute operation on server (via discord-server-mcp)
mcp-cli call discord-server-mcp discord_execute '{"operation":"messages.send","params":{"channel_id":"CHANNEL_ID","content":"Message"}}'

# Send file to channel
mcp-cli call discord-server-mcp discord_send_file '{"channel_id":"CHANNEL_ID","file_path":"/path/to/file.pdf","content":"Caption"}'
```

---

## ❌ NEVER DO THIS

- ❌ Leave any Discord message without acknowledgment
- ❌ Ignore messages not addressed to Elia
- ❌ Send file paths instead of files directly
- ❌ Use wrong channel for content

---

## ✅ ALWAYS DO THIS

- ✅ Respond to every message (even if just "I'll look into this")
- ✅ Ask clarifying questions if message is unclear
- ✅ Send files directly, never file paths
- ✅ Use the correct channel for content type
- ✅ Update memory folder when new information is learned

---

*Last Updated: 16 Avril 2026*
*Rule Added: NEVER LEAVE A MESSAGE WITHOUT RESPONSE*
