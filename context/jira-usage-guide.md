# Jira MCP Usage Guide for EliaIA Agents

**Generated**: Auto-updated when running `node scripts/sync-jira-projects.js`  
**Purpose**: Quick reference for agents to use MCP Jira tools with correct project keys

---

## 🎯 Quick Reference

## 🧭 Default Jira Inbox for EliaIA (Critical)

- If you cannot confidently choose the correct business Jira project (or a project is missing/unavailable), create the issue in the fallback Jira project:
  - Project Key: `ELIA`
  - Board: https://bsbagency.atlassian.net/jira/software/projects/ELIA/boards/267
- Include enough context so a human can later move the issue to the right project (business name, links, acceptance criteria, next steps).

### Business → Jira Project Mapping

| Business Name | Jira Project Key | Project URL | Board URL |
|--------------|------------------|-------------|-----------|
| **ZovaBoost** | `ZOVAPANEL` or `ZOVAB2B` | [ZOVAPANEL Project](https://bsbagency.atlassian.net/jira/software/projects/ZOVAPANEL) | [ZOVAPANEL Board](https://bsbagency.atlassian.net/jira/software/projects/ZOVAPANEL/boards) |
| **ZovaBoost B2B** | `ZOVAB2B` | [ZOVAB2B Project](https://bsbagency.atlassian.net/jira/software/projects/ZOVAB2B) | [ZOVAB2B Board](https://bsbagency.atlassian.net/jira/software/projects/ZOVAB2B/boards) |
| **Bene2luxe / Bene2Luxe** | `BEN` | [BEN Project](https://bsbagency.atlassian.net/jira/software/projects/BEN) | [BEN Board](https://bsbagency.atlassian.net/jira/software/projects/BEN/boards) |
| **CoBou Agency** | `COBOUAGENC` | [COBOUAGENC Project](https://bsbagency.atlassian.net/jira/software/projects/COBOUAGENC) | [COBOUAGENC Board](https://bsbagency.atlassian.net/jira/software/projects/COBOUAGENC/boards) |
| **TikTok & YouTube Automation** | `TIKYT` | [TIKYT Project](https://bsbagency.atlassian.net/jira/software/projects/TIKYT) | [TIKYT Board](https://bsbagency.atlassian.net/jira/software/projects/TIKYT/boards) |
| **Netfluxe** | Check `jira-projects.json` | - | - |
| **Account Verification** | Check `jira-projects.json` | - | - |

---

## 🔧 MCP Jira Tool Usage

### 1. Query Tickets by Project

**Tool**: `mcp_atlassian_jira_search_issues`

**Example for Bene2Luxe**:
```json
{
  "jql": "project = BEN ORDER BY updated DESC",
  "maxResults": 50
}
```

**Example for CoBou Agency**:
```json
{
  "jql": "project = COBOUAGENC AND status != Done ORDER BY updated DESC",
  "maxResults": 50
}
```

### 2. Create New Ticket

**Tool**: `mcp_atlassian_jira_create_issue`

**Example**:
```json
{
  "project": "BEN",
  "summary": "Task description",
  "description": "Detailed task information",
  "issuetype": "Task"
}
```

### 3. Update Ticket

**Tool**: `mcp_atlassian_jira_update_issue`

**Example**:
```json
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
```json
{
  "projectKey": "BEN"
}
```

---

## 📋 Common JQL Queries

### Get Open Tickets for a Project
```
project = BEN AND status != Done AND status != Closed ORDER BY updated DESC
```

### Get Tickets Assigned to Someone
```
project = COBOUAGENC AND assignee = currentUser() AND status != Done
```

### Get High Priority Tickets
```
project = TIKYT AND priority = High ORDER BY created DESC
```

### Get Recent Tickets (Last 7 Days)
```
project = BEN AND updated >= -7d ORDER BY updated DESC
```

---

## 🚀 Quick Actions for Agents

### When Working on Bene2Luxe:
- **Project Key**: `BEN`
- **Query**: `project = BEN`
- **Board**: https://bsbagency.atlassian.net/jira/software/projects/BEN/boards

### When Working on CoBou Agency:
- **Project Key**: `COBOUAGENC`
- **Query**: `project = COBOUAGENC`
- **Board**: https://bsbagency.atlassian.net/jira/software/projects/COBOUAGENC/boards

### When Working on TikTok/YouTube Automation:
- **Project Key**: `TIKYT`
- **Query**: `project = TIKYT`
- **Board**: https://bsbagency.atlassian.net/jira/software/projects/TIKYT/boards

### When Working on ZovaBoost:
- **Project Keys**: `ZOVAPANEL` or `ZOVAB2B`
- **Query**: `project IN (ZOVAPANEL, ZOVAB2B)`
- **ZOVAPANEL Board**: https://bsbagency.atlassian.net/jira/software/projects/ZOVAPANEL/boards
- **ZOVAB2B Board**: https://bsbagency.atlassian.net/jira/software/projects/ZOVAB2B/boards

---

## 📝 Best Practices

1. **Always use project keys** from this guide when querying Jira
2. **Check `context/jira-projects.json`** for the complete list of all projects
3. **Use JQL queries** to filter tickets by status, assignee, priority, etc.
4. **Link tickets in context** by including the ticket key (e.g., `BEN-123`)
5. **Update tickets** when tasks are completed or status changes

---

## 🔄 Updating This Guide

Run the sync script to update project information:
```bash
node scripts/sync-jira-projects.js
```

This will:
- Fetch all projects from Jira
- Update `context/jira-projects.json`
- Update `context/jira-projects.md`
- Update this guide if needed

---

**Last Updated**: Auto-generated  
**See Also**: `context/jira-projects.md` for detailed project information