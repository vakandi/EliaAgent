# [[../../wiki/systems/Jira-Tickets-Index|Jira]] [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] Usage Guide for EliaIA [[../../wiki/concepts/AI-Automation|Agents]]

**Generated**: Auto-updated when running `node scripts/sync-[[../../wiki/systems/Jira-Tickets-Index|Jira]]-projects.js`  
**Purpose**: Quick reference for [[../../wiki/concepts/AI-Automation|Agents]] to use [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] [[../../wiki/systems/Jira-Tickets-Index|Jira]] [[../../wiki/tools/Index|TOOLS]] with correct project keys

---

## 🎯 Quick Reference

## 🧭 Default [[../../wiki/systems/Jira-Tickets-Index|Jira]] Inbox for EliaIA (Critical)

- If you cannot confidently choose the correct [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] [[../../wiki/systems/Jira-Tickets-Index|Jira]] project (or a project is missing/unavailable), [[../../wiki/concepts/File-Management|Create]] the issue in the fallback [[../../wiki/systems/Jira-Tickets-Index|Jira]] project:
  - Project Key: `[[../../wiki/people/Elia|Elia]]`
  - Board: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/[[../../wiki/people/Elia|Elia]]/boards/267
- Include enough [[../../wiki/concepts/Prompt-Engineering|CONTEXT]] so a human can later move the issue to the right project ([[../../wiki/businesses/B2LUXE-BUSINESS|Business]] name, links, acceptance criteria, next steps).

### [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] → [[../../wiki/systems/Jira-Tickets-Index|Jira]] Project Mapping

| [[../../wiki/businesses/B2LUXE-BUSINESS|Business]] Name | [[../../wiki/systems/Jira-Tickets-Index|Jira]] Project Key | Project URL | Board URL |
|--------------|------------------|-------------|-----------|
| **[[../../wiki/businesses/ZovaBoost|ZovaBoost]]** | `ZOVAPANEL` or `ZOVAB2B` | [ZOVAPANEL Project]([[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/ZOVAPANEL) | [ZOVAPANEL Board]([[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/ZOVAPANEL/boards) |
| **[[../../wiki/businesses/ZovaBoost|ZovaBoost]] B2B** | `ZOVAB2B` | [ZOVAB2B Project]([[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/ZOVAB2B) | [ZOVAB2B Board]([[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/ZOVAB2B/boards) |
| **[[../../wiki/businesses/Bene2Luxe|Bene2Luxe]] / [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]** | `BEN` | [BEN Project]([[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/BEN) | [BEN Board]([[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/BEN/boards) |
| **[[../../wiki/businesses/CoBou-Agency|CoBou]] Agency** | `COBOUAGENC` | [COBOUAGENC Project]([[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/COBOUAGENC) | [COBOUAGENC Board]([[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/COBOUAGENC/boards) |
| **[[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]] & YouTube Automation** | `TIKYT` | [TIKYT Project]([[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/TIKYT) | [TIKYT Board]([[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/TIKYT/boards) |
| **[[../../wiki/businesses/Netfluxe|Netfluxe]]** | Check `[[../../wiki/systems/Jira-Tickets-Index|Jira]]-projects.[[../../wiki/concepts/API-Integration|JSON]]` | - | - |
| **[[../../wiki/businesses/[[../../wiki/businesses/Bene2Luxe#account|Account]]-Verification|[[../../wiki/businesses/Bene2Luxe#account|Account]] Verification]]** | Check `[[../../wiki/systems/Jira-Tickets-Index|Jira]]-projects.[[../../wiki/concepts/API-Integration|JSON]]` | - | - |

---

## 🔧 [[../../wiki/[[../../wiki/tools/Index|TOOLS]]/MCP-[[../../wiki/tools/Index|TOOLS]]|MCP]] [[../../wiki/systems/Jira-Tickets-Index|Jira]] Tool Usage

### 1. Query Tickets by Project

**Tool**: `mcp_atlassian_jira_search_issues`

**Example for [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]**:
```[[../../wiki/concepts/API-Integration|JSON]]
{
  "jql": "project = BEN [[../../wiki/businesses/B2LUXE-BUSINESS#orders|Order]] BY updated DESC",
  "maxResults": 50
}
```

**Example for [[../../wiki/businesses/CoBou-Agency|CoBou]] Agency**:
```[[../../wiki/concepts/API-Integration|JSON]]
{
  "jql": "project = COBOUAGENC AND status != Done [[../../wiki/businesses/B2LUXE-BUSINESS#orders|Order]] BY updated DESC",
  "maxResults": 50
}
```

### 2. [[../../wiki/concepts/File-Management|Create]] New Ticket

**Tool**: `mcp_atlassian_jira_create_issue`

**Example**:
```[[../../wiki/concepts/API-Integration|JSON]]
{
  "project": "BEN",
  "[[../../wiki/docs/Sessions|Summary]]": "[[../../wiki/concepts/AI-Automation#tasks|Task]] description",
  "description": "Detailed [[../../wiki/concepts/AI-Automation#tasks|Task]] information",
  "issuetype": "[[../../wiki/concepts/AI-Automation#tasks|Task]]"
}
```

### 3. Update Ticket

**Tool**: `mcp_atlassian_jira_update_issue`

**Example**:
```[[../../wiki/concepts/API-Integration|JSON]]
{
  "issueKey": "BEN-123",
  "fields": {
    "status": "In Progress",
    "assignee": {"accountId": "..."}
  }
}
```

### 4. Get Project Information

**Tool**: `mcp_atlassian_jira_get_project`

**Example**:
```[[../../wiki/concepts/API-Integration|JSON]]
{
  "projectKey": "BEN"
}
```

---

## 📋 Common JQL Queries

### Get Open Tickets for a Project
```
project = BEN AND status != Done AND status != Closed [[../../wiki/businesses/B2LUXE-BUSINESS#orders|Order]] BY updated DESC
```

### Get Tickets Assigned to Someone
```
project = COBOUAGENC AND assignee = currentUser() AND status != Done
```

### Get High Priority Tickets
```
project = TIKYT AND priority = High [[../../wiki/businesses/B2LUXE-BUSINESS#orders|Order]] BY created DESC
```

### Get Recent Tickets (Last 7 Days)
```
project = BEN AND updated >= -7d [[../../wiki/businesses/B2LUXE-BUSINESS#orders|Order]] BY updated DESC
```

---

## 🚀 Quick Actions for [[../../wiki/concepts/AI-Automation|Agents]]

### When Working on [[../../wiki/businesses/Bene2Luxe|Bene2Luxe]]:
- **Project Key**: `BEN`
- **Query**: `project = BEN`
- **Board**: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/BEN/boards

### When Working on [[../../wiki/businesses/CoBou-Agency|CoBou]] Agency:
- **Project Key**: `COBOUAGENC`
- **Query**: `project = COBOUAGENC`
- **Board**: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/COBOUAGENC/boards

### When Working on [[../../wiki/businesses/TikTok-YouTube-Auto|TikTok]]/YouTube Automation:
- **Project Key**: `TIKYT`
- **Query**: `project = TIKYT`
- **Board**: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/TIKYT/boards

### When Working on [[../../wiki/businesses/ZovaBoost|ZovaBoost]]:
- **Project Keys**: `ZOVAPANEL` or `ZOVAB2B`
- **Query**: `project IN (ZOVAPANEL, ZOVAB2B)`
- **ZOVAPANEL Board**: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/ZOVAPANEL/boards
- **ZOVAB2B Board**: [[../../wiki/topics/Infrastructure-Timeline|HTTPS]]://bsbagency.atlassian.net/[[../../wiki/systems/Jira-Tickets-Index|Jira]]/software/projects/ZOVAB2B/boards

---

## 📝 Best Practices

1. **Always use project keys** from this guide when querying [[../../wiki/systems/Jira-Tickets-Index|Jira]]
2. **Check `[[../../wiki/concepts/Prompt-Engineering|CONTEXT]]/[[../../wiki/systems/Jira-Tickets-Index|Jira]]-projects.[[../../wiki/concepts/API-Integration|JSON]]`** for the complete [[../../wiki/concepts/[[../../wiki/channels/Google|Search]]|List]] of all projects
3. **Use JQL queries** to [[../../wiki/concepts/Search|Filter]] tickets by status, assignee, priority, etc.
4. **Link tickets in [[../../wiki/concepts/Prompt-Engineering|CONTEXT]]** by including the ticket key (e.g., `BEN-123`)
5. **Update tickets** when tasks are completed or status changes

---

## 🔄 Updating This Guide

[[../../wiki/[[../../wiki/HOME|Docs]]/Sessions|Run]] the sync [[../../wiki/concepts/Marketing-Concepts|Script]] to update project information:
```bash
node scripts/sync-[[../../wiki/systems/Jira-Tickets-Index|Jira]]-projects.js
```

This will:
- Fetch all projects from [[../../wiki/systems/Jira-Tickets-Index|Jira]]
- Update `[[../../wiki/concepts/Prompt-Engineering|CONTEXT]]/[[../../wiki/systems/Jira-Tickets-Index|Jira]]-projects.[[../../wiki/concepts/API-Integration|JSON]]`
- Update `[[../../wiki/concepts/Prompt-Engineering|CONTEXT]]/[[../../wiki/systems/Jira-Tickets-Index|Jira]]-projects.md`
- Update this guide if needed

---

**Last Updated**: Auto-generated  
**See Also**: `[[../../wiki/concepts/Prompt-Engineering|CONTEXT]]/[[../../wiki/systems/Jira-Tickets-Index|Jira]]-projects.md` for detailed project information