import discord
import asyncio
import structlog
from typing import Optional
from .config import get_settings
from .opencode_client import OpenCodeClient
from .session_manager import SessionManager
from .context_tracker import ContextTracker
from .message_handler import format_discord_message, format_context_section

log = structlog.get_logger()

class EliaDiscordBot(discord.Client):
    def __init__(self, settings=None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(intents=intents)
        
        self.settings = settings or get_settings()
        self.opencode_client = OpenCodeClient(
            base_url=self.settings.OPENCODE_HOST,
            api_key=self.settings.OPENCODE_API_KEY
        )
        self.session_manager = SessionManager(self.opencode_client)
        self.context_tracker = ContextTracker(max_history=self.settings.CONTEXT_HISTORY_LIMIT)
        self.semaphore = asyncio.Semaphore(self.settings.MAX_CONCURRENT_REQUESTS)
        self.bot_mention = None

    async def setup_hook(self):
        log.info("bot.starting")
        await self._register_commands()

    async def _register_commands(self):
        self.tree = discord.app_commands.CommandTree(self)

        @self.tree.command(name="elia", description="Talk to Elia")
        @discord.app_commands.describe(message="Your message to Elia")
        async def elia_command(interaction: discord.Interaction, message: str):
            await interaction.response.defer()
            
            async with self.semaphore:
                guild_id = str(interaction.guild_id)
                channel = interaction.channel
                guild = interaction.guild
                
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
                
                response = await self.session_manager.send_message(
                    guild_id=guild_id,
                    content=formatted,
                    model_id=self.settings.OPENCODE_MODEL,
                    agent_id=self.settings.OPENCODE_AGENT
                )
                
                if not response:
                    await interaction.edit_original_response(content="Failed to get response from Elia")
                    return

                if len(response) > 1900:
                    await interaction.edit_original_response(content=response[:1900])
                    for i in range(1900, len(response), 1900):
                        await interaction.followup.send(response[i:i + 1900])
                else:
                    await interaction.edit_original_response(content=response)

        @self.tree.command(name="elia-new", description="Create a fresh Elia session")
        async def new_command(interaction: discord.Interaction):
            await interaction.response.defer()
            guild_id = str(interaction.guild_id)
            self.session_manager.active_sessions.pop(guild_id, None)
            new_session = await self.session_manager.get_or_create_session(guild_id, title="New Session")
            if new_session:
                await interaction.edit_original_response(content=f"Fresh session created: `{new_session[:20]}...`")
            else:
                await interaction.edit_original_response(content="Failed to create new session")

        @self.tree.command(name="elia-reset", description="Reset Elia session and start fresh")
        async def reset_command(interaction: discord.Interaction):
            await interaction.response.defer()
            guild_id = str(interaction.guild_id)
            new_session = await self.session_manager.reset_session(guild_id)
            if new_session:
                await interaction.edit_original_response(content=f"Session reset! New session: `{new_session[:20]}...`")
            else:
                await interaction.edit_original_response(content="Failed to create new session")

        @self.tree.command(name="elia-session-list", description="List recent Elia sessions")
        async def session_list_command(interaction: discord.Interaction):
            await interaction.response.defer()
            sessions = await self.session_manager.list_sessions()
            if not sessions:
                await interaction.edit_original_response(content="No sessions found.")
                return
            filtered = [s for s in sessions if "codemem-observer" not in (s.get("title") or "").lower()
                        and "codemem-observer" not in (s.get("slug") or "").lower()]
            current = self.session_manager.active_sessions.get(str(interaction.guild_id))
            lines = []
            if current:
                lines.append(f"**Current:** `{current[:16]}...`")
            for s in filtered[:15]:
                sid = s.get("id", "?")[:20]
                title = s.get("title") or s.get("slug") or "untitled"
                lines.append(f"`{sid}...` — {title}")
            if len(filtered) > 15:
                lines.append(f"_...and {len(filtered) - 15} more_")
            await interaction.edit_original_response(content="\n".join(lines))

        try:
            await asyncio.sleep(2)
            await self.tree.sync()
            log.info("commands.synced")
        except Exception as e:
            log.warning("commands.sync_failed", error=str(e))

    async def on_ready(self):
        log.info("bot.logged_in", user=str(self.user), id=str(self.user.id))
        self.bot_mention = f"<@{self.user.id}>"
        self.bot_mention_nick = f"<@!{self.user.id}>"

    async def on_message(self, message: discord.Message):
        if message.author.bot or isinstance(message.channel, discord.DMChannel):
            return

        content = message.content.strip()
        mentioned = (self.bot_mention and self.bot_mention in content) or \
                    (self.bot_mention_nick and self.bot_mention_nick in content)
        if not mentioned:
            return

        log.info("message.received", author=str(message.author), channel=message.channel.name)
        
        clean_content = content.replace(self.bot_mention, "").replace(self.bot_mention_nick, "").strip() or "Hello!"
        
        self.context_tracker.add_message(
            channel_id=message.channel.id,
            message={
                "author": message.author.name,
                "content": clean_content,
                "timestamp": message.created_at.strftime("%H:%M"),
                "is_reply": bool(message.reference),
                "replied_to": str(message.reference.resolved.author.name) if message.reference and message.reference.resolved else None
            }
        )

        async with self.semaphore:
            guild_id = str(message.guild.id)
            context_msgs = self.context_tracker.get_context(message.channel.id)
            context_section = format_context_section(message.channel.name, context_msgs)
            
            formatted = context_section + format_discord_message(
                content=clean_content,
                author_name=message.author.name,
                author_id=str(message.author.id),
                channel_name=message.channel.name,
                channel_id=message.channel.id,
                guild_name=message.guild.name,
                message_id=str(message.id),
                message_url=message.jump_url,
                is_reply=bool(message.reference),
                replied_to_id=str(message.reference.message_id) if message.reference else None,
                replied_to_author=str(message.reference.resolved.author.name) if message.reference and message.reference.resolved else None
            )

            async with message.channel.typing():
                response = await self.session_manager.send_message(
                    guild_id=guild_id,
                    content=formatted,
                    model_id=self.settings.OPENCODE_MODEL,
                    agent_id=self.settings.OPENCODE_AGENT
                )

            if response:
                if len(response) > 1900:
                    for i in range(0, len(response), 1900):
                        await message.reply(response[i:i + 1900], mention_author=False)
                else:
                    await message.reply(response, mention_author=False)

    async def close(self):
        await self.opencode_client.close()
        await super().close()
