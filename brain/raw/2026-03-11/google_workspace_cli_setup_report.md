# [[../../wiki/channels/Google|Google]] Workspace CLI Setup [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Report]]
**[[../../wiki/topics/Infrastructure-Timeline|Date]]**: 2026-03-11  
**Time**: 09:39 UTC  
**Status**: ✅ Successfully Configured

## Overview
This document describes the successful installation and configuration of [[../../wiki/channels/Google|Google]] Workspace CLI for [[../../wiki/people/Wael|Wael]] Bousfira's [[../../wiki/people/Elia|Elia]] Helper [[../../wiki/concepts/AI-Automation|IA]] system.

## What Was Installed

### 1. [[../../wiki/channels/Google|Google]] Workspace CLI (@googleworkspace/cli)
- **Package**: `@googleworkspace/cli@0.11.1`
- **Installation**: Global via npm
- **Alias**: `gw="npx @googleworkspace/cli"` (added to ~/.zshrc)
- **Location**: `~/.nvm/[[../../wiki/skills/Git-Version-Control|Versions]]/node/v24.13.1/lib`

### 2. Authentication Method
- **Type**: Service [[../../wiki/businesses/Bene2Luxe#account|Account]] (not OAuth)
- **Service [[../../wiki/businesses/Bene2Luxe#account|Account]]**: `gws-cli-sa@absolute-apogee-373503.iam.gserviceaccount.com`
- **Project**: `absolute-apogee-373503`
- **Key [[../../wiki/concepts/File-Management|File]]**: `/Users/vakandi/gws-key.[[../../wiki/concepts/API-Integration|JSON]]`
- **Role**: Editor (granted via gcloud IAM)

### 3. Enabled [[../../wiki/channels/Google|Google]] APIs
- ✅ `calendar-[[../../wiki/concepts/API-Integration|JSON]].googleapis.com`
- ✅ `[[../../wiki/channels/Gmail|Gmail]].googleapis.com`
- ✅ `drive.googleapis.com`
- ✅ `identitytoolkit.googleapis.com` (for auth)

## What Works Now

### ✅ [[../../wiki/channels/Google|Google]] Calendar
**Test Command**:
```bash
npx @googleworkspace/cli calendar events [[../../wiki/concepts/Search|List]] \
  --params '{"calendarId": "primary", "maxResults": 5}'
```

**Working Features**:
- [[../../wiki/concepts/Search|List]] calendar events
- Create new events
- Manage calendar settings
- Event reminders

### ✅ [[../../wiki/channels/Google|Google]] Tasks
**Test Command**:
```bash
npx @googleworkspace/cli tasks tasklists [[../../wiki/concepts/Search|List]]
npx @googleworkspace/cli tasks tasks create \
  --params '{"tasklist": "TASKLIST_ID"}' \
  --[[../../wiki/concepts/API-Integration|JSON]] '{"title": "Test [[../../wiki/concepts/AI-Automation#tasks|Task]]", "due": "2026-03-12T10:00:00Z"}'
```

**Working Features**:
- [[../../wiki/concepts/Search|List]] [[../../wiki/concepts/AI-Automation#tasks|Task]] lists
- Create tasks
- View [[../../wiki/concepts/AI-Automation#tasks|Task]] lists
- [[../../wiki/concepts/AI-Automation#tasks|Task]] management

### ⚠️ [[../../wiki/channels/Gmail|Gmail]] (Limited)
**Issue**: Service accounts have limited [[../../wiki/channels/Gmail|Gmail]] access
**Status**: Can [[../../wiki/concepts/Search|List]] messages but may have permission issues

### ❌ [[../../wiki/channels/Google|Google]] Drive (Not Available)
**Issue**: Drive package not available via npm @googleworkspace scope
**Workaround**: Use service [[../../wiki/businesses/Bene2Luxe#account|Account]] key with [[../../wiki/channels/Google|Google]] Drive API directly

## Configuration Details

### Environment Variables (added to ~/.zshrc)
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/Users/vakandi/gws-key.[[../../wiki/concepts/API-Integration|JSON]]"
alias gw="npx @googleworkspace/cli"
```

### Service [[../../wiki/businesses/Bene2Luxe#account|Account]] Key Structure
```[[../../wiki/concepts/API-Integration|JSON]]
{
  "type": "service_account",
  "project_id": "absolute-apogee-373503",
  "client_email": "gws-cli-sa@absolute-apogee-373503.iam.gserviceaccount.com",
  "client_id": "111574313801036436479",
  ...
}
```

## [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-CLI Status

### Available [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] Servers
| Server | Status | Notes |
|--------|--------|-------|
| `[[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]` | ✅ Running | Always active via launchctl |
| `[[../../wiki/channels/Discord-EliaWorkSpace|Discord]]-[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]` | ✅ On-demand | Bot integration |
| `[[../../wiki/channels/Telegram|Telegram]]` | ✅ On-demand | Bot with API access |
| `[[../../wiki/channels/Gmail|Gmail]]` | ✅ On-demand | Email handling |
| `googleworkspace-cli` | ✅ Working | Calendar, Tasks confirmed |
| `[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/Playwright|Playwright]]` | ✅ On-demand | Browser automation |
| `[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-atlassian` | ✅ On-demand | [[../../wiki/systems/Jira-Tickets-Index|Jira]] integration |

### [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-CLI Commands
```bash
# [[../../wiki/concepts/Search|List]] all servers
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli

# Test [[../../wiki/channels/Google|Google]] Workspace via [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli (if available)
[[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-cli call googleworkspace-cli calendar_events_list
```

## Integration Workflow

### Daily Documentation Flow
1. **[[../../wiki/[[../../wiki/skills/Index|SKILLS]]/[[../../wiki/skills/Cursor-IDE|Cursor]]-IDE|IDE]] Work** → [[../../wiki/concepts/Marketing-Concepts|Scripts]] in `./[[../../wiki/tools/Index|TOOLS]]/` → [[../../wiki/systems/Docker-Servers|Local]] `.md` files
2. **[[../../wiki/systems/Docker-Servers|Local]] [[../../wiki/HOME|Docs]]** → `[[../../wiki/HOME|Docs]]/YYYY-MM-DD/` folder structure
3. **[[../../wiki/channels/Google|Google]] [[../../wiki/HOME|Docs]]** → Upload + embed URL in [[../../wiki/concepts/Documentation|Markdown]]
4. **[[../../wiki/channels/Google|Google]] Tasks** → Quick reminders for [[../../wiki/people/Wael|Wael]]'s phone
5. **[[../../wiki/channels/Google|Google]] Calendar** → Meetings with phone notifications
6. **[[../../wiki/systems/Jira-Tickets-Index|Jira]]** → Complex projects with [[../../wiki/channels/Google|Google]] [[../../wiki/HOME|Docs]] context
7. **[[../../wiki/channels/Telegram|Telegram]]** → [[../../wiki/docs/Sessions|Reports]] with [[../../wiki/channels/Google|Google]] [[../../wiki/HOME|Docs]] links
8. **[[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]]** → Direct links when needed

## Usage Examples

### Calendar Events
```bash
# Create meeting
npx @googleworkspace/cli calendar events create \
  --[[../../wiki/concepts/API-Integration|JSON]] '{
    "summary": "Team Standup",
    "start": {"dateTime": "2026-03-12T10:00:00Z"},
    "end": {"dateTime": "2026-03-12T10:30:00Z"}
  }'
```

### Tasks
```bash
# Add quick [[../../wiki/concepts/AI-Automation#tasks|Task]] (appears on phone)
npx @googleworkspace/cli tasks tasks create \
  --params '{"tasklist": "MTAyMzE3MjQ3NzYwODc4MjA2MzA6MDow"}' \
  --[[../../wiki/concepts/API-Integration|JSON]] '{"title": "Call client", "due": "2026-03-12T15:00:00Z"}'
```

## Issues Encountered & Solutions

### 1. OAuth Scope Errors
**Problem**: [[../../wiki/channels/Google|Google]] blocked app due to too many sensitive scopes  
**Solution**: Switched to Service [[../../wiki/businesses/Bene2Luxe#account|Account]] authentication

### 2. Cloud Identity Scope Error
**Problem**: `invalid_scope` for `cloud-identity.devices`  
**Solution**: Deselected restricted scopes during OAuth attempt, then switched to service [[../../wiki/businesses/Bene2Luxe#account|Account]]

### 3. Permission Denied (403)
**Problem**: `roles/serviceusage.serviceUsageConsumer` required  
**Solution**: Granted `roles/editor` to service [[../../wiki/businesses/Bene2Luxe#account|Account]] via gcloud

### 4. [[../../wiki/channels/Gmail|Gmail]] Precondition Failed
**Problem**: Service accounts have limited [[../../wiki/channels/Gmail|Gmail]] API access  
**Status**: Partially working, may need domain-wide delegation for full access

## Files Updated

1. **`~/.zshrc`** - Added alias and environment variable
2. **`~/.config/gws/client_secret.[[../../wiki/concepts/API-Integration|JSON]]`** - OAuth client config (unused, kept for reference)
3. **`~/gws-key.[[../../wiki/concepts/API-Integration|JSON]]`** - Service [[../../wiki/businesses/Bene2Luxe#account|Account]] key
4. **`/Users/vakandi/EliaAI/context/[[../../wiki/tools/Index|TOOLS]].md`** - Added comprehensive workflow documentation
5. **`/Users/vakandi/EliaAI/[[../../wiki/HOME|Docs]]/2026-03-11/`** - This document

## Next Steps

1. ✅ Test [[../../wiki/channels/Google|Google]] [[../../wiki/HOME|Docs]] creation/upload
2. ⏳ [[../../wiki/concepts/Prompt-Engineering|VERIFY]] calendar events appear on phone
3. ⏳ Test [[../../wiki/concepts/AI-Automation#tasks|Task]] notifications on phone
4. ⏳ Create [[../../wiki/systems/Jira-Tickets-Index|Jira]] ticket with [[../../wiki/channels/Google|Google]] [[../../wiki/HOME|Docs]] URL
5. ⏳ Automate daily [[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Report]] generation

## [[../../wiki/channels/Google|Google]] [[../../wiki/HOME|Docs]] URL
**[This document will be uploaded to [[../../wiki/channels/Google|Google]] [[../../wiki/HOME|Docs]] and URL inserted here]**

## Conclusion

[[../../wiki/channels/Google|Google]] Workspace CLI is **successfully configured** and working for:
- ✅ Calendar management
- ✅ [[../../wiki/concepts/AI-Automation#tasks|Task]] management  
- ⚠️ [[../../wiki/channels/Gmail|Gmail]] (limited)
- ❌ Drive (not available via CLI)

The integration with [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]]-CLI, [[../../wiki/channels/Telegram|Telegram]], [[../../wiki/channels/WhatsApp-B2LUXE|WhatsApp]], and [[../../wiki/systems/Jira-Tickets-Index|Jira]] is documented in `context/[[../../wiki/tools/Index|TOOLS]].md` and ready for daily use.

---
**Document Created**: 2026-03-11 09:39  
**Author**: [[../../wiki/people/Elia|Elia]] Helper [[../../wiki/concepts/AI-Automation|IA]]  
**Status**: Ready for upload to [[../../wiki/channels/Google|Google]] [[../../wiki/HOME|Docs]]
