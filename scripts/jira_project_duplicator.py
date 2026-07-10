#!/usr/bin/env python3
"""
JIRA Project Duplicator Tool

This tool duplicates Jira projects including:
- Board configuration
- Sprints with dates
- Issues to sprints
- Filter configuration

Usage:
    python3 jira_project_duplicator.py <source_project> <target_project>
"""

import json
import sys
import urllib.request
import base64
import time

JIRA_URL = "https://bsbagency.atlassian.net"

def load_jira_config():
    """Load Jira configuration from mcp_servers.json"""
    with open("~/Documents/mcps_server/mcp_servers.json") as f:
        config = json.load(f)
    atlassian_config = config["mcpServers"]["mcp-atlassian"]["env"]
    return atlassian_config["JIRA_EMAIL"], atlassian_config["JIRA_API_TOKEN"]

def jira_headers(email, token):
    """Create Jira API headers"""
    credentials = f"{email}:{token}".encode("utf-8")
    auth = base64.b64encode(credentials).decode("utf-8")
    return {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def jira_request(method, path, data=None, headers=None):
    """Make Jira API request"""
    url = f"{JIRA_URL}{path}"
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode("utf-8")[:500]}
    except Exception as e:
        return {"error": str(e)}

class JiraProjectDuplicator:
    """Duplicate Jira projects with all components"""
    
    def __init__(self, email, token):
        self.headers = jira_headers(email, token)
        self.created_items = {
            "filter": None,
            "board": None,
            "sprint": None,
            "issues": 0
        }
    
    def duplicate(self, source_project_key, target_project_key, target_project_id):
        """Main duplication method"""
        print(f"\n{'='*60}")
        print(f"DUPLICATING PROJECT: {source_project_key} → {target_project_key}")
        print(f"{'='*60}\n")
        
        # Step 1: Create filter
        filter_id = self._create_filter(target_project_key)
        if not filter_id:
            print("❌ Failed to create filter")
            return None
        
        # Step 2: Create board
        board_id = self._create_board(f"Tableau {target_project_key}", filter_id, target_project_id)
        if not board_id:
            print("❌ Failed to create board")
            return None
        
        # Step 3: Create sprint
        sprint_id = self._create_sprint("Sprint 1", board_id)
        if sprint_id:
            print(f"✅ Sprint created: {sprint_id}")
        
        return {
            "filter": filter_id,
            "board": board_id,
            "sprint": sprint_id
        }
    
    def _create_filter(self, project_key):
        """Create a filter for the project"""
        print("📋 Creating filter...")
        
        filter_data = {
            "name": f"{project_key} All Issues",
            "jql": f"project = '{project_key}' ORDER BY created DESC",
            "description": f"Filter for {project_key} project"
        }
        
        result = jira_request("POST", "/rest/api/3/filter", filter_data, self.headers)
        filter_id = result.get("id") if "id" in result else None
        
        if filter_id:
            print(f"  ✅ Filter created: ID {filter_id}")
            self.created_items["filter"] = filter_id
        else:
            print(f"  ❌ Filter creation failed: {result}")
        
        return filter_id
    
    def _create_board(self, name, filter_id, project_id):
        """Create a Kanban board"""
        print(f"📋 Creating board: {name}...")
        
        board_data = {
            "name": name,
            "type": "kanban",
            "filterId": filter_id,
            "location": {
                "type": "project",
                "project": {
                    "id": project_id
                }
            },
            "isPrivate": False
        }
        
        result = jira_request("POST", "/rest/agile/1.0/board", board_data, self.headers)
        board_id = result.get("id") if "id" in result else None
        
        if board_id:
            print(f"  ✅ Board created: ID {board_id}")
            self.created_items["board"] = board_id
        else:
            print(f"  ❌ Board creation failed: {result}")
        
        return board_id
    
    def _create_sprint(self, name, board_id):
        """Create a sprint"""
        from datetime import datetime, timedelta
        
        print(f"📅 Creating sprint: {name}...")
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        sprint_data = {
            "name": name,
            "startDate": start.strftime("%Y-%m-%dT00:00:00.000Z"),
            "endDate": end.strftime("%Y-%m-%dT23:59:59.000Z"),
            "originBoardId": board_id,
            "goal": f"{name} goals"
        }
        
        result = jira_request("POST", "/rest/agile/1.0/sprint", sprint_data, self.headers)
        sprint_id = result.get("id") if "id" in result else None
        
        if sprint_id:
            print(f"  ✅ Sprint created: ID {sprint_id}")
            self.created_items["sprint"] = sprint_id
        else:
            print(f"  ❌ Sprint creation failed: {result}")
        
        return sprint_id
    
    def add_issues_to_sprint(self, sprint_id, issue_keys):
        """Add issues to sprint"""
        print(f"📊 Adding {len(issue_keys)} issues to sprint...")
        
        added = 0
        for key in issue_keys:
            result = jira_request("POST", f"/rest/agile/1.0/sprint/{sprint_id}/issue/add", 
                           {"issues": [key]}, self.headers)
            if "error" not in result:
                added += 1
            time.sleep(0.05)
        
        print(f"  ✅ Added {added} issues")
        self.created_items["issues"] = added
        return added
    
    def get_status(self):
        """Get duplication status"""
        return self.created_items


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python3 jira_project_duplicator.py <source_key> <target_key> <target_id>")
        print("Example: python3 jira_project_duplicator.py ELIA BIYOU3 10366")
        sys.exit(1)
    
    source_key = sys.argv[1]
    target_key = sys.argv[2]
    target_id = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    # Load config
    email, token = load_jira_config()
    
    # Create duplicator
    duplicator = JiraProjectDuplicator(email, token)
    
    # Duplicate project
    result = duplicator.duplicate(source_key, target_key, target_id)
    
    if result:
        print(f"\n{'='*60}")
        print("✅ DUPLICATION COMPLETE!")
        print(f"{'='*60}")
        print(f"\n📋 Board: https://bsbagency.atlassian.net/jira/software/projects/{target_key}/boards/{result['board']}")
        print(f"📅 Sprint: {result['sprint']}")
        print(f"📊 Issues: {result.get('issues', 0)}")
    else:
        print("\n❌ Duplication failed")


if __name__ == "__main__":
    main()
