import structlog
from datetime import datetime
from typing import Optional, List

log = structlog.get_logger()

def format_discord_message(
    content: str,
    author_name: str,
    author_id: str,
    channel_name: str,
    channel_id: int,
    guild_name: str,
    message_id: str,
    message_url: str,
    is_reply: bool = False,
    replied_to_id: Optional[str] = None,
    replied_to_author: Optional[str] = None,
) -> str:
    header = f"""[Discord Message]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Source: {guild_name} → #{channel_name} (ID: {channel_id})
👤 Author: {author_name} (ID: {author_id})
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🔗 Message ID: {message_id}
🔗 Message URL: {message_url}
"""
       
    if is_reply and replied_to_id:
        header += f"""💬 Reply: Yes (to message by {replied_to_author})
🔗 Replied to ID: {replied_to_id}
"""
    
    discord_tools = f"""📌 1) Reply NOW via mcp-cli: mcp-cli call discord-server-mcp discord_send_message '{{"channel_id":"{channel_id}","content":"msg"}}'
"""
    
    return header + "\n" + discord_tools + content

def format_context_section(channel_name: str, context_msgs: List[str]) -> str:
    if not context_msgs:
        return ""
    
    return f"""[CONTEXTE - Messages récents du channel #{channel_name} que tu as manqués]:
""" + "\n".join(context_msgs) + "\n"
