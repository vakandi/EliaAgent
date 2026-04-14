#!/usr/bin/env python3
"""
Quick report sender for EliaAI
Usage:
  python3 send_report.py voice "transcription内容"
  python3 send_report.py business "report内容"
"""

import sys
import subprocess
import json


def send_telegram_message(message: str):
    """Send message via mcp-cli telegram"""
    cmd = [
        "mcp-cli",
        "call",
        "telegram",
        "send_msg_to_default_group",
        json.dumps({"message": message}),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 send_report.py <voice|business> <message>")
        sys.exit(1)

    report_type = sys.argv[1]
    message = sys.argv[2]

    # Add emoji prefix based on type
    if report_type == "voice":
        prefix = "🎤"
    else:
        prefix = "📋"

    full_message = f"{prefix} {message}"

    if send_telegram_message(full_message):
        print(f"✅ Sent {report_type} report")
    else:
        print(f"❌ Failed to send {report_type} report")
        sys.exit(1)
