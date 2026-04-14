#!/usr/bin/env python3
"""
Higgsfield Image Task Queue Manager
Usage: python3 image_tasks.py status|add|complete|fail|list
"""

import json
import sys
from pathlib import Path
from datetime import datetime

QUEUE_FILE = Path(__file__).parent.parent.parent / "HiggsField.ai-API-Wraper" / "higgsfield_image_tasks.json"
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "HiggsField.ai-API-Wraper" / "scripts"

def load_queue():
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE) as f:
            return json.load(f)
    return {"tasks": [], "last_updated": None}

def save_queue(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def cmd_status():
    data = load_queue()
    tasks = data.get("tasks", [])
    pending = [t for t in tasks if t["status"] == "pending"]
    generating = [t for t in tasks if t["status"] == "generating"]
    completed = [t for t in tasks if t["status"] == "completed"]
    failed = [t for t in tasks if t["status"] == "failed"]
    
    print(f"\n=== IMAGE TASK QUEUE ===")
    print(f"Pending: {len(pending)}")
    print(f"Generating: {len(generating)}")
    print(f"Completed: {len(completed)}")
    print(f"Failed: {len(failed)}")
    print(f"Total: {len(tasks)}")
    
    if generating:
        print(f"\nCurrently generating:")
        for t in generating:
            print(f"  - {t['task_id']}")

def cmd_add(script_name, frame_type, prompt):
    data = load_queue()
    task_id = f"{script_name}_{frame_type}"
    
    task = {
        "task_id": task_id,
        "script_name": script_name,
        "frame_type": frame_type,
        "prompt": prompt,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "output_path": None,
        "error": None
    }
    
    if not any(t["task_id"] == task_id for t in data["tasks"]):
        data["tasks"].append(task)
        save_queue(data)
        print(f"Added task: {task_id}")
    else:
        print(f"Task already exists: {task_id}")

def cmd_complete(task_id, output_path):
    data = load_queue()
    for task in data["tasks"]:
        if task["task_id"] == task_id:
            task["status"] = "completed"
            task["output_path"] = output_path
            save_queue(data)
            print(f"Completed: {task_id}")
            return
    print(f"Task not found: {task_id}")

def cmd_fail(task_id, error):
    data = load_queue()
    for task in data["tasks"]:
        if task["task_id"] == task_id:
            task["status"] = "failed"
            task["error"] = error
            save_queue(data)
            print(f"Failed: {task_id} - {error}")
            return
    print(f"Task not found: {task_id}")

def cmd_list():
    data = load_queue()
    print("\n=== ALL TASKS ===")
    for task in data["tasks"]:
        print(f"{task['task_id']}: {task['status']}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "status":
        cmd_status()
    elif cmd == "add" and len(sys.argv) >= 5:
        cmd_add(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "complete" and len(sys.argv) >= 4:
        cmd_complete(sys.argv[2], sys.argv[3])
    elif cmd == "fail" and len(sys.argv) >= 4:
        cmd_fail(sys.argv[2], sys.argv[3])
    elif cmd == "list":
        cmd_list()
    else:
        print("Usage: python3 image_tasks.py status|add|list|complete|fail")
