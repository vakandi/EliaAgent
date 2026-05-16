#!/usr/bin/env python3
"""
Discord Message Sender for EliaAI
Properly escapes JSON and sends messages to Discord channels.

Usage:
    python3 discord_send.py <channel_id> <message>
    python3 discord_send.py 1489244810777727046 "Hello World"
    python3 discord_send.py 1489244810777727046 "$(cat report.md)"

Or with file input:
    cat report.md | python3 discord_send.py 1489244810777727046 --stdin
"""

import sys
import json
import subprocess
import os


def send_discord_message(channel_id: str, message: str) -> bool:

    payload = json.dumps(
        {
            "operation": "messages.send",
            "params": {"channel_id": channel_id, "content": message},
        }
    )

    cmd = ["mcp-cli", "call", "discord-server-mcp", "discord_execute"]

    result = subprocess.run(
        cmd,
        input=payload,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )

    if result.returncode == 0 and "Message sent" in result.stdout:
        return True

    print(f"Error: {result.stderr}", file=sys.stderr)
    print(f"Stdout: {result.stdout}", file=sys.stderr)
    return False


def main():
    if len(sys.argv) < 3:
        if not os.isatty(sys.stdin.fileno()):
            message = sys.stdin.read().strip()
            if len(sys.argv) >= 2:
                channel_id = sys.argv[1]
            else:
                print("Error: Channel ID required", file=sys.stderr)
                sys.exit(1)
        else:
            print(__doc__)
            sys.exit(1)

    if "--stdin" in sys.argv:
        message = sys.stdin.read().strip()
        channel_id = sys.argv[1]
    else:
        channel_id = sys.argv[1]
        message = sys.argv[2]

    if not channel_id:
        print("Error: Channel ID required", file=sys.stderr)
        sys.exit(1)

    if not message:
        print("Error: Message required", file=sys.stderr)
        sys.exit(1)

    success = send_discord_message(channel_id, message)

    if success:
        print(f"✅ Message sent to channel {channel_id}")
        sys.exit(0)
    else:
        print(f"❌ Failed to send message to channel {channel_id}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
