import time
from collections import defaultdict, deque
from typing import List, Dict, Any
import structlog

log = structlog.get_logger()

class ContextTracker:
    def __init__(self, max_history: int = 20, ttl_seconds: int = 3600):
        self.max_history = max_history
        self.ttl_seconds = ttl_seconds
        self.history: Dict[int, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.timestamps: Dict[int, float] = {}

    def add_message(self, channel_id: int, message: Dict[str, Any]):
        now = time.time()
        self.history[channel_id].append(message)
        self.timestamps[channel_id] = now
        
        if now - self.timestamps.get(channel_id, 0) > self.ttl_seconds:
            self.history[channel_id].clear()

    def get_context(self, channel_id: int, limit: int = 10) -> List[str]:
        if channel_id not in self.history:
            return []
        
        recent = list(self.history[channel_id])[-limit:]
        context = []
        for msg in recent:
            author = msg.get("author", "Unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            is_reply = msg.get("is_reply", False)
            replied_to = msg.get("replied_to")
            
            if is_reply and replied_to:
                context.append(f"[{timestamp}] 💬 {author} → @{replied_to}: {content}")
            else:
                context.append(f"[{timestamp}] {author}: {content}")
        
        return context

    def clear_channel(self, channel_id: int):
        if channel_id in self.history:
            del self.history[channel_id]
        if channel_id in self.timestamps:
            del self.timestamps[channel_id]
