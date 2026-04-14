#!/usr/bin/env python3
"""
Google Workspace OAuth Integration - Fixed Version
Full access with OAuth authentication for Drive and Docs
"""

import os
import sys
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
import io

# Configuration
CLIENT_SECRET_FILE = "/Users/vakandi/Downloads/client_secret_2_581399875521-slo2j3177ddh4ioth3nkkf6gi266o9cc.apps.googleusercontent.com.json"
CREDENTIALS_FILE = "/Users/vakandi/.config/gws/oauth_credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]


def get_oauth_credentials():
    """Get OAuth credentials with automatic refresh"""
    creds = None

    # Load existing credentials if they exist
    if os.path.exists(CREDENTIALS_FILE):
        try:
            creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)
        except Exception as e:
            print(f"Warning: Could not load credentials file: {e}")
            creds = None

    # If we have credentials, check if they need refresh
    if creds:
        if creds.valid:
            return creds
        elif creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed credentials
                os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
                with open(CREDENTIALS_FILE, "w") as token:
                    token.write(creds.to_json())
                return creds
            except Exception as e:
                print(f"Warning: Failed to refresh token: {e}")
                creds = None

    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

        # Save credentials for future runs
        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
        with open(CREDENTIALS_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def create_calendar_event(
    summary, description, start_time, end_time, timezone="Europe/Paris", reminders=None
):
    """Create an event in Google Calendar with optional reminders

    Args:
        summary: Event title
        description: Event description/details
        start_time: ISO format start time (e.g., "2026-04-15T10:00:00")
        end_time: ISO format end time
        timezone: Timezone (default: Europe/Paris)
        reminders: List of minutes before event to remind (e.g., [5, 15, 30, 60, 1440] for 5min, 15min, 30min, 1hour, 1day)

    Example:
        create_calendar_event(
            "Meeting with Team",
            "Discuss Q2 goals",
            "2026-04-15T14:00:00",
            "2026-04-15T15:00:00",
            reminders=[15, 60]  # 15 min and 1 hour before
        )
    """
    try:
        creds = get_oauth_credentials()
        calendar_service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time,
                "timeZone": timezone,
            },
        }

        # Add custom reminders if provided
        if reminders:
            event["reminders"] = {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": minutes} for minutes in reminders
                ],
            }

        event = (
            calendar_service.events().insert(calendarId="primary", body=event).execute()
        )
        return {
            "success": True,
            "event_id": event.get("id"),
            "url": f"https://calendar.google.com/calendar/event/{event.get('id')}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_task(title, notes="", due_date=None):
    """Create a task in Google Tasks"""
    try:
        creds = get_oauth_credentials()
        tasks_service = build("tasks", "v1", credentials=creds)

        task = {"title": title}
        if notes:
            task["notes"] = notes
        if due_date:
            task["due"] = due_date

        task = tasks_service.tasks().insert(tasklist="@default", body=task).execute()
        return {
            "success": True,
            "task_id": task.get("id"),
            "url": "https://tasks.google.com",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_document_from_markdown(title, markdown_content):
    """Create a Google Document from markdown content"""
    try:
        creds = get_oauth_credentials()
        docs_service = build("docs", "v1", credentials=creds)

        # Create empty document
        document = docs_service.documents().create(body={"title": title}).execute()
        doc_id = document.get("documentId")

        # Convert markdown to Google Docs format
        requests = []

        # Split markdown into lines and process
        lines = markdown_content.split("\n")
        index = 1

        for line in lines:
            if line.startswith("# "):
                # Heading 1
                text = line[2:] + "\n"
                requests.append(
                    {"insertText": {"location": {"index": index}, "text": text}}
                )
                requests.append(
                    {
                        "updateTextStyle": {
                            "range": {
                                "startIndex": index,
                                "endIndex": index + len(text),
                            },
                            "textStyle": {
                                "bold": True,
                                "fontSize": {"magnitude": 18, "unit": "PT"},
                            },
                            "fields": "bold,fontSize",
                        }
                    }
                )
                index += len(text)

            elif line.startswith("## "):
                # Heading 2
                text = line[3:] + "\n"
                requests.append(
                    {"insertText": {"location": {"index": index}, "text": text}}
                )
                requests.append(
                    {
                        "updateTextStyle": {
                            "range": {
                                "startIndex": index,
                                "endIndex": index + len(text),
                            },
                            "textStyle": {
                                "bold": True,
                                "fontSize": {"magnitude": 14, "unit": "PT"},
                            },
                            "fields": "bold,fontSize",
                        }
                    }
                )
                index += len(text)

            elif line.startswith("### "):
                # Heading 3
                text = line[4:] + "\n"
                requests.append(
                    {"insertText": {"location": {"index": index}, "text": text}}
                )
                requests.append(
                    {
                        "updateTextStyle": {
                            "range": {
                                "startIndex": index,
                                "endIndex": index + len(text),
                            },
                            "textStyle": {
                                "bold": True,
                                "fontSize": {"magnitude": 12, "unit": "PT"},
                            },
                            "fields": "bold,fontSize",
                        }
                    }
                )
                index += len(text)

            elif line.startswith("- ") or line.startswith("* "):
                # Bullet list
                text = line[2:] + "\n"
                requests.append(
                    {"insertText": {"location": {"index": index}, "text": "• " + text}}
                )
                index += len("• " + text)

            elif (
                line.startswith("1. ")
                or line.startswith("2. ")
                or line.startswith("3. ")
                or line.startswith("4. ")
                or line.startswith("5. ")
            ):
                # Numbered list
                text = line[3:] + "\n"
                requests.append(
                    {"insertText": {"location": {"index": index}, "text": text}}
                )
                index += len(text)

            elif line.strip() == "":
                # Empty line
                requests.append(
                    {"insertText": {"location": {"index": index}, "text": "\n"}}
                )
                index += 1

            else:
                # Regular text
                text = line + "\n"
                requests.append(
                    {"insertText": {"location": {"index": index}, "text": text}}
                )
                index += len(text)

        # Apply all formatting changes
        if requests:
            docs_service.documents().batchUpdate(
                documentId=doc_id, body={"requests": requests}
            ).execute()

        set_anyone_with_link_permission(doc_id)

        return {
            "success": True,
            "document_id": doc_id,
            "url": f"https://docs.google.com/document/d/{doc_id}/edit",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def import_markdown_to_docs(markdown_file_path, title=None):
    """Import a markdown file to Google Docs"""
    try:
        if not os.path.exists(markdown_file_path):
            return {"success": False, "error": f"File not found: {markdown_file_path}"}

        with open(markdown_file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        if not title:
            title = (
                os.path.basename(markdown_file_path)
                .replace(".md", "")
                .replace(".markdown", "")
            )

        return create_document_from_markdown(title, markdown_content)
    except Exception as e:
        return {"success": False, "error": str(e)}


def import_docx_to_docs(docx_file_path, title=None):
    """Import a DOCX file to Google Docs"""
    try:
        from googleapiclient.http import MediaFileUpload

        if not os.path.exists(docx_file_path):
            return {"success": False, "error": "File not found"}

        if not title:
            title = os.path.basename(docx_file_path).replace(".docx", "")

        creds = get_oauth_credentials()
        drive_service = build("drive", "v3", credentials=creds)

        # Upload DOCX to Drive
        file_metadata = {
            "name": title,
            "mimeType": "application/vnd.google-apps.document",
        }
        media = MediaFileUpload(
            docx_file_path,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        file = (
            drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        doc_id = file.get("id")

        style_table_borders(doc_id)
        set_anyone_with_link_permission(doc_id)

        return {
            "success": True,
            "document_id": doc_id,
            "url": f"https://docs.google.com/document/d/{doc_id}/edit",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def set_anyone_with_link_permission(file_id):
    try:
        creds = get_oauth_credentials()
        drive_service = build("drive", "v3", credentials=creds)

        permission = {
            "type": "anyone",
            "role": "writer",
        }

        drive_service.permissions().create(
            fileId=file_id,
            body=permission,
        ).execute()

        return True
    except Exception as e:
        print(f"⚠️ Warning: Could not set permission: {e}")
        return False
    """Style all table borders in a document to 1pt black"""
    try:
        creds = get_oauth_credentials()
        docs_service = build("docs", "v1", credentials=creds)

        doc = docs_service.documents().get(documentId=doc_id).execute()

        requests = []

        def find_tables(body):
            tables_found = []
            for element in body.get("content", []):
                if "table" in element:
                    table = element["table"]
                    table_start = element.get("startIndex", 0)
                    num_rows = len(table.get("tableRows", []))
                    num_cols = table.get("columns", 0)
                    if num_rows > 0 and num_cols > 0:
                        tables_found.append(
                            {"start": table_start, "rows": num_rows, "cols": num_cols}
                        )
            return tables_found

        tables = find_tables(doc)

        for table_info in tables:
            table_start = table_info["start"]
            rows = table_info["rows"]
            cols = table_info["cols"]

            r = border_color_rgb[0] / 255
            g = border_color_rgb[1] / 255
            b = border_color_rgb[2] / 255

            requests.append(
                {
                    "updateTableCellStyle": {
                        "tableStartLocation": {"index": table_start},
                        "tableRange": {
                            "sheetId": 0,
                            "startRowIndex": 0,
                            "endRowIndex": rows,
                            "startColumnIndex": 0,
                            "endColumnIndex": cols,
                        },
                        "tableCellStyle": {
                            "borderTop": {
                                "width": {"magnitude": border_width, "unit": "PT"},
                                "color": {
                                    "color": {
                                        "rgbColor": {"red": r, "green": g, "blue": b}
                                    }
                                },
                                "dashStyle": "SOLID",
                            },
                            "borderBottom": {
                                "width": {"magnitude": border_width, "unit": "PT"},
                                "color": {
                                    "color": {
                                        "rgbColor": {"red": r, "green": g, "blue": b}
                                    }
                                },
                                "dashStyle": "SOLID",
                            },
                            "borderLeft": {
                                "width": {"magnitude": border_width, "unit": "PT"},
                                "color": {
                                    "color": {
                                        "rgbColor": {"red": r, "green": g, "blue": b}
                                    }
                                },
                                "dashStyle": "SOLID",
                            },
                            "borderRight": {
                                "width": {"magnitude": border_width, "unit": "PT"},
                                "color": {
                                    "color": {
                                        "rgbColor": {"red": r, "green": g, "blue": b}
                                    }
                                },
                                "dashStyle": "SOLID",
                            },
                        },
                        "fields": "borderTop,borderBottom,borderLeft,borderRight",
                    }
                }
            )

        if requests:
            docs_service.documents().batchUpdate(
                documentId=doc_id, body={"requests": requests}
            ).execute()
            print(
                f"✓ Styled {len(tables)} table(s) with {border_width}pt black borders"
            )

    except Exception as e:
        print(f"⚠️ Warning: Could not style table borders: {e}")


def create_document(title, content=""):
    """Create a Google Document"""
    try:
        creds = get_oauth_credentials()
        docs_service = build("docs", "v1", credentials=creds)

        document = docs_service.documents().create(body={"title": title}).execute()

        doc_id = document.get("documentId")

        # If content provided, add text to document
        if content:
            requests = [
                {
                    "insertText": {
                        "location": {
                            "index": 1,
                        },
                        "text": content,
                    }
                }
            ]
            docs_service.documents().batchUpdate(
                documentId=doc_id, body={"requests": requests}
            ).execute()

        set_anyone_with_link_permission(doc_id)

        return {
            "success": True,
            "document_id": doc_id,
            "url": f"https://docs.google.com/document/d/{doc_id}/edit",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def upload_to_drive(filename, content, mime_type="text/plain", folder_id=None):
    """Upload file to Google Drive"""
    try:
        creds = get_oauth_credentials()
        drive_service = build("drive", "v3", credentials=creds)

        file_metadata = {"name": filename}

        if folder_id:
            file_metadata["parents"] = [folder_id]

        if isinstance(content, str) and content.startswith("@file:"):
            file_path = content[6:]
            with open(file_path, "rb") as f:
                file_content = f.read()
            if filename.endswith(".mp3"):
                mime_type = "audio/mpeg"
            elif filename.endswith(".m4a"):
                mime_type = "audio/mp4"
            elif filename.endswith(".wav"):
                mime_type = "audio/wav"
            elif filename.endswith(".txt"):
                mime_type = "text/plain"
            elif filename.endswith(".md"):
                mime_type = "text/markdown"
            else:
                mime_type = "application/octet-stream"
            media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype=mime_type)
        else:
            media = MediaIoBaseUpload(io.BytesIO(content.encode()), mimetype=mime_type)

        file = (
            drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id,name,webViewLink")
            .execute()
        )

        return {
            "success": True,
            "file_id": file.get("id"),
            "name": file.get("name"),
            "url": file.get("webViewLink"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_calendar_events(max_results=10):
    """List upcoming calendar events"""
    try:
        creds = get_oauth_credentials()
        calendar_service = build("calendar", "v3", credentials=creds)

        now = datetime.utcnow().isoformat() + "Z"
        events_result = (
            calendar_service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        return {"success": True, "events": events}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_tasks(max_results=10):
    """List tasks"""
    try:
        creds = get_oauth_credentials()
        tasks_service = build("tasks", "v1", credentials=creds)

        tasks_result = (
            tasks_service.tasks()
            .list(tasklist="@default", maxResults=max_results)
            .execute()
        )

        tasks = tasks_result.get("items", [])
        return {"success": True, "tasks": tasks}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_drive_files(max_results=100, folder_id=None):
    try:
        creds = get_oauth_credentials()
        drive_service = build("drive", "v3", credentials=creds)

        query = f"'{folder_id}' in parents" if folder_id else None

        results = (
            drive_service.files()
            .list(
                pageSize=max_results,
                q=query,
                fields="nextPageToken, files(id, name, mimeType, webViewLink)",
            )
            .execute()
        )

        files = results.get("files", [])
        return {"success": True, "files": files}
    except Exception as e:
        return {"success": False, "error": str(e)}


def download_file_from_folder(filename: str, folder_id: str, local_path: str):
    try:
        creds = get_oauth_credentials()
        drive_service = build("drive", "v3", credentials=creds)

        query = f"name = '{filename}' and '{folder_id}' in parents"

        results = (
            drive_service.files().list(q=query, fields="files(id, name)").execute()
        )
        files = results.get("files", [])

        if not files:
            return {"success": False, "error": f"File {filename} not found in folder"}

        file_id = files[0]["id"]

        request = drive_service.files().get_media(fileId=file_id)
        with open(local_path, "wb") as f:
            f.write(request.execute())

        return {"success": True, "path": local_path}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_document(file_id):
    try:
        creds = get_oauth_credentials()
        drive_service = build("drive", "v3", credentials=creds)
        drive_service.files().delete(fileId=file_id).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "  python3 google_workspace_oauth.py create-event 'Summary' 'Description'"
        )
        print("  python3 google_workspace_oauth.py create-task 'Task title' 'Notes'")
        print("  python3 google_workspace_oauth.py create-doc 'Document title'")
        print(
            "  python3 google_workspace_oauth.py import-md 'markdown_file.md' [title]"
        )
        print("  python3 google_workspace_oauth.py upload-file 'filename' 'content'")
        print("  python3 google_workspace_oauth.py list-events")
        print("  python3 google_workspace_oauth.py list-tasks")
        print("  python3 google_workspace_oauth.py list-files")
        print("\nNote: Uses OAuth authentication for full Google Workspace access")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create-event":
        summary = sys.argv[2] if len(sys.argv) > 2 else "Test Event"
        description = sys.argv[3] if len(sys.argv) > 3 else "Test Description"

        # Parse optional start time (ISO format) or use default (now + 1 hour)
        if len(sys.argv) > 4 and sys.argv[4]:
            try:
                start_time = datetime.fromisoformat(sys.argv[4])
            except ValueError:
                start_time = datetime.now() + timedelta(hours=1)
        else:
            start_time = datetime.now() + timedelta(hours=1)

        # Parse optional end time or use default (start + 1 hour)
        if len(sys.argv) > 5 and sys.argv[5]:
            try:
                end_time = datetime.fromisoformat(sys.argv[5])
            except ValueError:
                end_time = start_time + timedelta(hours=1)
        else:
            end_time = start_time + timedelta(hours=1)

        # Parse optional reminders (comma-separated: "5,15,30,60")
        reminders = None
        if len(sys.argv) > 6 and sys.argv[6]:
            try:
                reminders = [int(x.strip()) for x in sys.argv[6].split(",")]
            except ValueError:
                reminders = None

        result = create_calendar_event(
            summary,
            description,
            start_time.isoformat(),
            end_time.isoformat(),
            reminders=reminders,
        )

        if result["success"]:
            print(f"✅ Event created: {result['url']}")
            if reminders:
                print(f"   Reminders set: {reminders}")
        else:
            print(f"❌ Error: {result['error']}")

    elif command == "create-task":
        title = sys.argv[2] if len(sys.argv) > 2 else "Test Task"
        notes = sys.argv[3] if len(sys.argv) > 3 else ""

        result = create_task(title, notes)

        if result["success"]:
            print(f"✅ Task created: {result['url']}")
        else:
            print(f"❌ Error: {result['error']}")

    elif command == "create-doc":
        title = sys.argv[2] if len(sys.argv) > 2 else "Test Document"
        content = sys.argv[3] if len(sys.argv) > 3 else ""

        result = create_document(title, content)

        if result["success"]:
            print(f"✅ Document created: {result['url']}")
        else:
            print(f"❌ Error: {result['error']}")

    elif command == "import-md":
        markdown_file = sys.argv[2] if len(sys.argv) > 2 else ""
        title = sys.argv[3] if len(sys.argv) > 3 else None

        if not markdown_file:
            print("❌ Error: import-md requires markdown file path")
            print(
                "Usage: python3 google_workspace_oauth.py import-md 'file.md' [title]"
            )
            sys.exit(1)

        result = import_markdown_to_docs(markdown_file, title)

        if result["success"]:
            print(f"✅ Markdown imported: {result['url']}")
        else:
            print(f"❌ Error: {result['error']}")

    elif command == "import-docx":
        docx_file = sys.argv[2] if len(sys.argv) > 2 else ""
        title = sys.argv[3] if len(sys.argv) > 3 else None

        if not docx_file:
            print("❌ Error: import-docx requires DOCX file path")
            print(
                "Usage: python3 google_workspace_oauth.py import-docx 'file.docx' [title]"
            )
            sys.exit(1)

        result = import_docx_to_docs(docx_file, title)

        if result["success"]:
            print(f"✅ DOCX imported: {result['url']}")
        else:
            print(f"❌ Error: {result['error']}")

    elif command == "upload-file":
        filename = sys.argv[2] if len(sys.argv) > 2 else "test.txt"
        content = sys.argv[3] if len(sys.argv) > 3 else "Test content"
        folder_id = sys.argv[4] if len(sys.argv) > 4 else None

        result = upload_to_drive(filename, content, folder_id=folder_id)

        if result["success"]:
            print(f"✅ File uploaded: {result['url']}")
        else:
            print(f"❌ Error: {result['error']}")

    elif command == "list-events":
        result = list_calendar_events()
        if result["success"]:
            print(f"📅 Upcoming events ({len(result['events'])}):")
            for event in result["events"]:
                print(f"  - {event.get('summary', 'No title')}")
        else:
            print(f"❌ Error: {result['error']}")

    elif command == "list-tasks":
        result = list_tasks()
        if result["success"]:
            print(f"📝 Tasks ({len(result['tasks'])}):")
            for task in result["tasks"]:
                print(f"  - {task.get('title', 'No title')}")
        else:
            print(f"❌ Error: {result['error']}")

    elif command == "list-files":
        folder_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = list_drive_files(folder_id=folder_id)
        if result["success"]:
            print(f"📁 Drive files ({len(result['files'])}):")
            for file in result["files"]:
                print(
                    f"  - {file.get('name', 'No name')} ({file.get('mimeType', 'Unknown')})"
                )
        else:
            print(f"❌ Error: {result['error']}")

    elif command == "download-file":
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        folder_id = sys.argv[3] if len(sys.argv) > 3 else None
        local_path = sys.argv[4] if len(sys.argv) > 4 else None

        if not filename or not folder_id or not local_path:
            print("Usage: download-file <filename> <folder_id> <local_path>")
            sys.exit(1)

        result = download_file_from_folder(filename, folder_id, local_path)
        if result["success"]:
            print(f"✅ Downloaded: {result['path']}")
        else:
            print(f"❌ Error: {result['error']}")

    elif command == "delete-document":
        file_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not file_id:
            print("Usage: delete-document <file_id>")
            sys.exit(1)
        result = delete_document(file_id)
        if result["success"]:
            print(f"✅ Document deleted")
        else:
            print(f"❌ Error: {result['error']}")

    else:
        print(f"Unknown command: {command}")
        print(
            "\nAvailable commands: create-event, create-task, create-doc, import-md, upload-file, list-events, list-tasks, list-files"
        )
        sys.exit(1)
