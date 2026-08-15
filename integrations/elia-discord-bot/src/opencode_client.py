import httpx
import structlog
from typing import Optional, List, Dict, Any

log = structlog.get_logger()

class OpenCodeClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/").replace("localhost", "127.0.0.1")
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=30.0,
            proxy=None,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )

    async def close(self):
        await self.client.aclose()

    async def health_check(self) -> bool:
        try:
            response = await self.client.get("/session/status")
            return response.status_code == 200
        except Exception as e:
            log.error("opencode.health_check_failed", error=str(e))
            return False

    async def create_session(self, title: str = "Discord Session") -> Optional[str]:
        try:
            response = await self.client.post("/session", json={"title": title})
            if response.status_code == 200:
                data = response.json()
                return data.get("id")
            log.error(
                "opencode.create_session_http_error",
                status=response.status_code,
                body=response.text[:500],
                title=title,
            )
        except Exception as e:
            log.error("opencode.create_session_failed", error=str(e))
        return None

    async def send_message(
        self, 
        session_id: str, 
        content: str, 
        model_id: str, 
        agent_id: str
    ) -> Optional[str]:
        try:
            payload = {
                "parts": [{"type": "text", "text": content}],
                "modelID": model_id,
                "providerID": "opencode",
                "mode": agent_id,
            }
            response = await self.client.post(f"/session/{session_id}/message", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                parts = data.get("parts", [])
                text_parts = [
                    part.get("text", "") 
                    for part in parts 
                    if part.get("type") == "text" and part.get("text")
                ]
                return "\n".join(text_parts) if text_parts else "No response"
            
            log.error("opencode.send_message_http_error",
                session_id=session_id,
                status=response.status_code,
                body=response.text[:500])
        except Exception as e:
            log.error("opencode.send_message_failed", session_id=session_id, error=str(e))
        return None

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = await self.client.get("/session/status")
            if response.status_code == 200:
                statuses = response.json()
                return statuses.get(session_id, {})
        except Exception as e:
            log.error("opencode.get_status_failed", error=str(e))
        return None

    async def list_sessions(self) -> List[Dict[str, Any]]:
        try:
            response = await self.client.get("/session")
            if response.status_code == 200:
                return response.json()
            log.error(
                "opencode.list_sessions_http_error",
                status=response.status_code,
                body=response.text[:500],
            )
        except Exception as e:
            log.error("opencode.list_sessions_failed", error=str(e))
        return []

    async def delete_session(self, session_id: str) -> bool:
        try:
            response = await self.client.delete(f"/session/{session_id}")
            return response.status_code == 204
        except Exception as e:
            log.error("opencode.delete_session_failed", session_id=session_id, error=str(e))
        return False
