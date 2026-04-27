#!/usr/bin/env python3
"""
EliaDiscord Bot - Discord integration for EliaAI
Uses opencode-ai library with message queue for handling multiple channels.

Stability features:
- All OpenCode API calls run in thread pool to avoid blocking asyncio event loop
- Exponential backoff for Discord reconnection
- Heartbeat monitoring to detect event loop blocking
- Graceful handling of network failures
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import discord
from dotenv import load_dotenv
from opencode_ai import Opencode

BOT_DIR = Path(__file__).parent
SESSIONS_FILE = BOT_DIR / "sessions.json"
LOG_FILE = BOT_DIR / "logs" / "bot.log"

ERROR_CHANNEL_ID = int(os.getenv("DISCORD_ERROR_CHANNEL_ID", "1497426963084611654"))
ERROR_GUILD_ID = os.getenv("DISCORD_GUILD_ID", "1489242790444662885")

DEFAULT_OPENCODE_PORTS = [4096, 8080, 3000, 8000]
OPENCODE_HOST = os.getenv("OPENCODE_HOST", "http://localhost:4096")
USE_PROXY = os.getenv("USE_PROXY", "0") == "1" or (Path.home() / ".proxy_enabled").exists()
_last_proxy_reload = 0
PROXY_RELOAD_INTERVAL = 60  # Reload proxy every 60 seconds max

def _load_proxy_settings():
    """Load proxy from proxychains.conf - called at startup AND before each OpenCode request."""
    if not USE_PROXY:
        log.info("Proxy disabled (USE_PROXY=0 or no .proxy_enabled)")
        return None
    proxy_conf = Path.home() / ".proxychains.conf"
    if proxy_conf.exists():
        try:
            for line in proxy_conf.read_text().splitlines():
                line = line.strip()
                if line.startswith("http ") or line.startswith("https ") or line.startswith("socks4 ") or line.startswith("socks5 "):
                    parts = line.split()
                    if len(parts) >= 3:
                        proxy_type = parts[0]
                        ip = parts[1]
                        port = parts[2]
                        user = parts[3] if len(parts) > 3 else ""
                        pwd = parts[4] if len(parts) > 4 else ""
                        if user and pwd:
                            proxy_url = f"{proxy_type}://{user}:{pwd}@{ip}:{port}"
                        else:
                            proxy_url = f"{proxy_type}://{ip}:{port}"
                        os.environ["HTTPS_PROXY"] = proxy_url
                        os.environ["HTTP_PROXY"] = proxy_url
                        log.info(f"Proxy loaded: {ip}:{port}")
                        return proxy_url
        except Exception as e:
            log.warning(f"Failed to load proxy: {e}")
    return None

def _ensure_proxy_fresh():
    """Reload proxy if stale - call this before OpenCode API requests."""
    global _last_proxy_reload
    import time
    now = time.time()
    if USE_PROXY and (now - _last_proxy_reload) > PROXY_RELOAD_INTERVAL:
        _load_proxy_settings()
        _last_proxy_reload = now
        log.info("Proxy refreshed for request")

from logging.handlers import RotatingFileHandler
log_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding='utf-8'
)
log_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        log_handler,
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("elia-discord")


@dataclass
class QueuedMessage:
    content: str
    channel: discord.TextChannel
    original_message: discord.Message
    event: asyncio.Event
    context_messages: List[str] = None


class MessageTracker:
    def __init__(self):
        self.messages: dict = {}
        self.sent_to_elia: set = set()
    
    def add_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        channel_id = message.channel.id
        
        is_reply = message.reference and message.reference.message_id
        replied_to_author = None
        if is_reply and message.reference:
            try:
                replied_to_author = message.reference.resolved.author.name if message.reference.resolved else "Unknown"
            except:
                replied_to_author = "Unknown"
        
        msg_entry = {
            "id": message.id,
            "author": message.author.name,
            "content": message.content,
            "timestamp": message.created_at.isoformat(),
            "is_reply": is_reply,
            "replied_to": replied_to_author,
        }
        
        if channel_id not in self.messages:
            self.messages[channel_id] = []
        self.messages[channel_id].append(msg_entry)
    
    def mark_sent(self, message_id: int):
        self.sent_to_elia.add(message_id)
    
    def get_recent_context(self, channel_id: int, limit: int = 10) -> List[str]:
        if channel_id not in self.messages:
            return []
        
        recent = self.messages[channel_id][-limit:]
        result = []
        for msg in recent:
            content = msg["content"].strip()
            if not content:
                continue
            
            ts = msg["timestamp"]
            if "T" in ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    ts = dt.strftime("%H:%M")
                except:
                    pass
            
            author = msg["author"]
            is_reply = msg.get("is_reply", False)
            replied_to = msg.get("replied_to")
            
            if is_reply and replied_to:
                result.append(f"[{ts}] 💬 {author} → @{replied_to}: {content}")
            else:
                result.append(f"[{ts}] {author}: {content}")
        
        return result


class MessageQueue:
    def __init__(self, session_manager, bot=None):
        self.session_manager = session_manager
        self.bot = bot
        self.queue: asyncio.Queue = asyncio.Queue()
        self.processing = False
        self._task = None

    async def start(self):
        if not self.processing:
            self.processing = True
            self._task = asyncio.create_task(self._process_queue())

    async def stop(self):
        self.processing = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def add(self, content: str, channel: discord.TextChannel, original_message: discord.Message) -> str:
        event = asyncio.Event()
        queued = QueuedMessage(content, channel, original_message, event)
        await self.queue.put(queued)
        log.info(f"Queued message from {channel.name}, queue size: {self.queue.qsize()}, content_len={len(content)}")
        
        await event.wait()
        log.info(f"Queue event wait completed, response: {queued.response[:50] if queued.response else 'None'}...")
        return queued.response

    async def _process_queue(self):
        log.info("Queue processor started")
        while self.processing:
            try:
                queued = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            try:
                channel = queued.channel
                log.info(f"Processing message from #{getattr(channel, 'name', 'unknown')}")
                
                async with channel.typing():
                    response = await self.session_manager.send_message(queued.content)
                    queued.response = response
                    
                    while not response or response in ["...", "No response", "No response received", "None", ""]:
                        log.info(f"Waiting for OpenCode response...")
                        await asyncio.sleep(2)
                        try:
                            response = await self.session_manager.send_message(queued.content)
                        except Exception as e:
                            log.error(f"Error polling response: {e}")
                            break
                        if response and response not in ["...", "No response", "No response received", "None", ""]:
                            break
                    
                    queued.response = response
                    
                    if response and response not in ["...", "No response", "No response received", "None", ""]:
                        await self._send_response(channel, queued.original_message, queued.response)
                    else:
                        log.info(f"Skipping response send - empty or no response")

            except asyncio.TimeoutError:
                log.error(f"Message processing timed out")
                try:
                    await self.bot._send_error_to_channel("Timeout processing message", getattr(channel, 'name', 'unknown'))
                except:
                    pass
            except Exception as e:
                log.error(f"Error processing queue message: {e}")
                try:
                    await self.bot._send_error_to_channel(str(e), getattr(channel, 'name', 'unknown'))
                except:
                    pass
            finally:
                queued.event.set()

    async def _send_response(self, channel, original_message, response):
        try:
            if not response or response in ["...", "No response", "No response received", "None"]:
                log.info(f"Skipping empty response")
                return
            if len(response) > 1900:
                for i in range(0, len(response), 1900):
                    await original_message.reply(response[i:i + 1900])
            else:
                await original_message.reply(response)
        except Exception as e:
            log.error(f"Error sending response: {e}")


class SessionManager:
    def __init__(self, sessions_file: Path):
        self.sessions_file = sessions_file
        self.session_id: Optional[str] = None
        
        detected_host = self._detect_opencode_host()
        if detected_host != OPENCODE_HOST:
            log.info(f"OpenCode auto-detected at {detected_host}, using instead of {OPENCODE_HOST}")
        self.client = Opencode(base_url=detected_host)
        self._load()
        
        self._executor = None
        self._lock = asyncio.Lock()
    
    def _detect_opencode_host(self) -> str:
        for port in DEFAULT_OPENCODE_PORTS:
            try:
                import httpx
                response = httpx.get(f"http://localhost:{port}/session/status", timeout=2.0)
                if response.status_code == 200:
                    log.info(f"OpenCode found at port {port}")
                    return f"http://localhost:{port}"
            except:
                pass
        return OPENCODE_HOST
    
    def _run_sync_call(self, callable_fn):
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, callable_fn)

    def _load(self) -> None:
        if self.sessions_file.exists():
            try:
                data = json.loads(self.sessions_file.read_text())
                self.session_id = data.get("session_id")
                log.info(f"Loaded session: {self.session_id}")
            except Exception as e:
                log.error(f"Failed to load sessions: {e}")
                self.session_id = None

    def _save(self) -> None:
        try:
            self.sessions_file.write_text(json.dumps({"session_id": self.session_id}))
        except Exception as e:
            log.error(f"Failed to save session: {e}")

    async def create_new_session(self, title: str = "Discord Session") -> Optional[str]:
        try:
            def _create():
                return self.client.session.create(
                    extra_body={"title": title}
                )
            result = await self._run_sync_call(_create)
            self.session_id = result.id
            self._save()
            log.info(f"Created new session: {self.session_id}")
            return self.session_id
        except Exception as e:
            log.error(f"Error creating session: {e}")
            return None

    async def is_session_busy_check(self) -> bool:
        if not self.session_id:
            return False
        try:
            import httpx
            response = httpx.get(f"{OPENCODE_HOST}/session/status", timeout=5.0)
            if response.status_code == 200:
                statuses = response.json()
                session_status = statuses.get(self.session_id, {})
                return session_status.get("type") == "busy"
        except Exception as e:
            log.error(f"Error checking session status: {e}")
        return False

    def _sync_is_session_busy(self) -> bool:
        if not self.session_id:
            return False
        try:
            import httpx
            response = httpx.get(f"{OPENCODE_HOST}/session/status", timeout=5.0)
            if response.status_code == 200:
                statuses = response.json()
                session_status = statuses.get(self.session_id, {})
                return session_status.get("type") == "busy"
        except Exception as e:
            log.error(f"Error checking session status: {e}")
        return False
        
    def _sync_send_message(self, content: str) -> Optional[str]:
        if not self.session_id:
            return None
            
        try:
            result = self.client.session.chat(
                id=self.session_id,
                model_id="opencode/big-pickle",
                provider_id="opencode",
                parts=[{"type": "text", "text": content}],
                extra_body={"agent": "elia"},
            )
            
            if result and result.parts:
                text_parts = [
                    part.get('text', '') for part in result.parts 
                    if part.get('type') == 'text' and part.get('text')
                ]
                return "\n".join(text_parts) if text_parts else "No response"
            return "No response received"
        except Exception as e:
            log.error(f"Error sending message: {e}")
            return None

    async def send_message(self, content: str, max_wait_seconds: int = 300) -> Optional[str]:
        _ensure_proxy_fresh()
        if not self.session_id:
            log.info("No session_id, creating new session...")
            await self.create_new_session()

        wait_time = 0
        check_interval = 2
        log.info(f"Checking session {self.session_id} busy status...")
        while True:
            is_busy = await self._run_sync_call(self._sync_is_session_busy)
            if not is_busy:
                log.info(f"Session {self.session_id} is free, sending message")
                break
            if wait_time >= max_wait_seconds:
                log.warning(f"Session {self.session_id} still busy after {max_wait_seconds}s, skipping message")
                return None
            log.info(f"Session {self.session_id} is busy, waiting... ({wait_time}s)")
            await asyncio.sleep(check_interval)
            wait_time += check_interval
        
        try:
            log.info(f"Sending message to OpenCode...")
            result = await self._run_sync_call(lambda: self._sync_send_message(content))
            return result
        except Exception as e:
            log.error(f"Error sending message: {e}")
            return None

    async def list_sessions(self) -> List[dict]:
        try:
            def _list():
                return self.client.session.list()
            sessions = await self._run_sync_call(_list)
            return [
                {"id": s.id, "title": s.title, "created": s.time.created if s.time else None}
                for s in sessions
            ]
        except Exception as e:
            log.error(f"Error listing sessions: {e}")
            return []

    async def select_session(self, session_id: str) -> bool:
        try:
            def _select():
                return self.client.session.list()
            sessions = await self._run_sync_call(_select)
            session = next((s for s in sessions if s.id == session_id), None)
            if session:
                self.session_id = session_id
                self._save()
                log.info(f"Selected session: {session_id}")
                return True
        except Exception as e:
            log.error(f"Error selecting session: {e}")
        return False

    async def delete_session(self) -> bool:
        if not self.session_id:
            return True
        try:
            def _delete():
                self.client.session.delete(id=self.session_id)
            await self._run_sync_call(_delete)
            self.session_id = None
            self._save()
            return True
        except Exception as e:
            log.error(f"Error deleting session: {e}")
            return False


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


class EliaDiscordBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(intents=intents)
        self.session_manager = SessionManager(SESSIONS_FILE)
        self.message_queue = MessageQueue(self.session_manager, bot=self)
        self.message_tracker = MessageTracker()
        self.bot_mention = None
    
    async def _send_error_to_channel(self, error_msg: str, channel_name: str = ""):
        try:
            guild = self.get_guild(int(ERROR_GUILD_ID))
            if guild:
                channel = guild.get_channel(ERROR_CHANNEL_ID)
                if channel:
                    msg = f"""━━━━━━━━━━━━━━━━━━━━━━━��━━━━━━
⚠️ Elia Discord Error
Channel: {channel_name}
Error: {error_msg}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                    await channel.send(msg)
        except Exception as e:
            log.error(f"Failed to send error to error channel: {e}")

    async def setup_hook(self):
        log.info("EliaDiscord bot starting...")

        await self.message_queue.start()
        log.info("Message queue started")

        self.tree = discord.app_commands.CommandTree(self)
        log.info("CommandTree created")

        @self.tree.command(name="elia-reset", description="Reset Elia session and start fresh")
        async def reset_command(interaction: discord.Interaction):
            await interaction.response.defer()
            await self.session_manager.delete_session()
            new_session = await self.session_manager.create_new_session()
            if new_session:
                await interaction.followup.send(f"Session reset! New session: `{new_session[:16]}...`")
            else:
                await interaction.followup.send("Failed to create new session")

        @self.tree.command(name="elia-new", description="Create a new Elia session")
        async def new_command(interaction: discord.Interaction):
            await interaction.response.defer()
            await self.session_manager.delete_session()
            new_session = await self.session_manager.create_new_session()
            if new_session:
                await interaction.followup.send(f"New session created: `{new_session[:16]}...`")
            else:
                await interaction.followup.send("Failed to create new session")

        @self.tree.command(name="elia-session-list", description="List all OpenCode sessions")
        async def session_list_command(interaction: discord.Interaction):
            await interaction.response.defer()
            sessions = await self.session_manager.list_sessions()
            
            if not sessions:
                await interaction.followup.send("No sessions found")
                return
            
            current = self.session_manager.session_id
            msg = "**Sessions:**\n"
            for i, s in enumerate(sessions[:10], 1):
                marker = "👉 " if s["id"] == current else f"{i}. "
                title = s.get("title", "Untitled")[:30]
                msg += f"{marker}`{s['id']}` - {title}\n"
            
            await interaction.followup.send(msg)

        @self.tree.command(name="elia-session-select", description="Select an OpenCode session by ID")
        @discord.app_commands.describe(session_id="The session ID to select")
        async def session_select_command(interaction: discord.Interaction, session_id: str):
            await interaction.response.defer()
            success = await self.session_manager.select_session(session_id)
            if success:
                await interaction.followup.send(f"Selected session: `{session_id[:16]}...`")
            else:
                await interaction.followup.send("Failed to select session. Check the ID.")

        @self.tree.command(name="elia", description="Talk to Elia")
        @discord.app_commands.describe(message="Your message to Elia")
        async def elia_command(interaction: discord.Interaction, message: str):
            await interaction.response.defer()
            
            guild = interaction.guild
            channel = interaction.channel
            
            formatted = format_discord_message(
                content=message,
                author_name=interaction.user.name,
                author_id=str(interaction.user.id),
                channel_name=channel.name if channel else "DM",
                channel_id=channel.id if channel else 0,
                guild_name=guild.name if guild else "DM",
                message_id=str(interaction.id),
                message_url=f"https://discord.com/channels/{guild.id if guild else '@me'}/{channel.id if channel else 'DM'}/{interaction.id}",
            )
            
            response = await self.message_queue.add(formatted, channel, interaction.message)
            if response:
                if len(response) > 1900:
                    for i in range(0, len(response), 1900):
                        await interaction.followup_send(response[i:i + 1900])
                else:
                    await interaction.followup.send("Response sent to channel!")
            else:
                await interaction.followup.send("Failed to get response from Elia")

        try:
            await asyncio.sleep(2)
            await self.tree.sync()
            log.info("Slash commands synced")
        except Exception as e:
            log.warning(f"Slash command sync failed (rate limited?): {e}")
            try:
                await asyncio.sleep(30)
                await self.tree.sync()
                log.info("Slash commands synced (retry)")
            except Exception as e2:
                log.warning(f"Slash command sync retry failed: {e2}")

    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        self.bot_mention = f"<@{self.user.id}>"

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            return

        channel_id = message.channel.id
        
        self.message_tracker.add_message(message)

        content = message.content.strip()
        
        bot_mentioned = self.bot_mention and self.bot_mention in content
        
        is_reply_to_elia = False
        if message.reference and message.reference.message_id:
            try:
                ref_message = message.reference.resolved
                if ref_message and ref_message.author.id == self.user.id:
                    is_reply_to_elia = True
            except:
                pass
        
        if not bot_mentioned and not is_reply_to_elia:
            return
        
        trigger_type = "reply" if is_reply_to_elia else "mention"
        log.info(f"Triggered via {trigger_type}: bot_mentioned={bool(bot_mentioned)}, is_reply={is_reply_to_elia}")
        
        if bot_mentioned:
            content = content.replace(self.bot_mention, "").strip()
            if not content:
                content = "Hello!"
        
        guild = message.guild
        channel = message.channel
        
        is_reply = message.reference and message.reference.message_id
        replied_to_id = None
        replied_to_author = None
        
        try:
            if is_reply:
                ref_message = await channel.fetch_message(message.reference.message_id)
                replied_to_id = str(ref_message.id)
                replied_to_author = ref_message.author.name
        except:
            pass

        context_msgs = self.message_tracker.get_recent_context(channel_id, limit=15)
        context_section = ""
        if context_msgs:
            context_section = f"""[CONTEXTE - Messages récents du channel #{channel.name} que tu as manqués]:
""" + "\n".join(context_msgs) + "\n"

        formatted = format_discord_message(
            content=content,
            author_name=message.author.name,
            author_id=str(message.author.id),
            channel_name=channel.name,
            channel_id=channel_id,
            guild_name=guild.name if guild else "Unknown",
            message_id=str(message.id),
            message_url=message.jump_url,
            is_reply=is_reply,
            replied_to_id=replied_to_id,
            replied_to_author=replied_to_author,
        )

        if context_section:
            formatted = context_section + "\n" + formatted
        
        log.info(f"Message from {message.author} in #{channel.name}: {content[:50]}...")

        try:
            self.message_tracker.mark_sent(message.id)
            await self.message_queue.add(formatted, channel, message)
        except Exception as e:
            log.error(f"Error in on_message: {e}")

    async def close(self):
        await self.message_queue.stop()
        await super().close()


async def main():
    load_dotenv(BOT_DIR / ".env")

    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        log.error("DISCORD_BOT_TOKEN not set in .env")
        sys.exit(1)

    log.info("Starting EliaDiscord bot...")
    bot = EliaDiscordBot()
    
    max_retries = 10
    base_delay = 1
    max_delay = 60
    retry_count = 0
    
    while True:
        try:
            log.info("Connecting to Discord...")
            await bot.start(token, reconnect=True)
            break
        except discord.errors.ConnectionClosed as e:
            retry_count += 1
            if retry_count > max_retries:
                log.error(f"Max retries ({max_retries}) reached, exiting")
                break
                
            delay = min(base_delay * (2 ** retry_count), max_delay)
            log.warning(f"Discord disconnected: {e}. Reconnecting in {delay}s (attempt {retry_count}/{max_retries})")
            
            try:
                await bot.close()
            except Exception:
                pass
            
            await asyncio.sleep(delay)
            
            bot = EliaDiscordBot()
            log.info("Recreating bot instance for reconnect...")
            
        except KeyboardInterrupt:
            log.info("Shutting down...")
            await bot.close()
            break
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            retry_count += 1
            if retry_count > max_retries:
                log.error(f"Max retries reached, exiting")
                break
                
            delay = min(base_delay * (2 ** retry_count), max_delay)
            log.warning(f"Error occurred: {e}. Retrying in {delay}s")
            await asyncio.sleep(delay)


if __name__ == "__main__":
    asyncio.run(main())