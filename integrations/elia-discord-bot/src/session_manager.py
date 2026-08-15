import structlog
from typing import Optional, List, Dict, Any
from .opencode_client import OpenCodeClient

log = structlog.get_logger()

class SessionManager:
    def __init__(self, client: OpenCodeClient):
        self.client = client
        self.active_sessions: Dict[str, str] = {}

    async def get_or_create_session(self, guild_id: str, title: str = "Discord Session") -> Optional[str]:
        if guild_id in self.active_sessions:
            return self.active_sessions[guild_id]
        
        session_id = await self.client.create_session(title)
        if session_id:
            self.active_sessions[guild_id] = session_id
            log.info("session.created", guild_id=guild_id, session_id=session_id)
        return session_id

    async def send_message(self, guild_id: str, content: str, model_id: str, agent_id: str) -> Optional[str]:
        session_id = await self.get_or_create_session(guild_id)
        if not session_id:
            return None
        
        return await self.client.send_message(session_id, content, model_id, agent_id)

    async def reset_session(self, guild_id: str) -> Optional[str]:
        if guild_id in self.active_sessions:
            old_id = self.active_sessions.pop(guild_id)
            await self.client.delete_session(old_id)
            log.info("session.reset", guild_id=guild_id, old_id=old_id)
        
        return await self.get_or_create_session(guild_id, title="Reset Session")

    async def list_sessions(self) -> List[Dict[str, Any]]:
        return await self.client.list_sessions()
