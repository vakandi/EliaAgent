from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
import os

class Settings(BaseSettings):
    DISCORD_BOT_TOKEN: str = Field(..., description="Discord Bot Token")
    DISCORD_GUILD_ID: int | None = Field(None, description="Discord Server ID")
    DISCORD_ERROR_CHANNEL_ID: int = Field(..., description="Channel ID for error reports")

    OPENCODE_HOST: str = Field("http://localhost:4096", description="OpenCode API Host")
    OPENCODE_API_KEY: str | None = Field(None, description="OpenCode API Key")
    OPENCODE_MODEL: str = Field("big-pickle", description="Model ID to use")
    OPENCODE_AGENT: str = Field("elia", description="Agent ID to use")
    
    MAX_CONCURRENT_REQUESTS: int = Field(3, description="Max concurrent OpenCode requests")
    CONTEXT_HISTORY_LIMIT: int = Field(20, description="Max messages to keep in context")
    
    BOT_DIR: Path = Path(__file__).parent.parent
    LOG_DIR: Path = BOT_DIR / "logs"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> Settings:
    settings = Settings()
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    return settings
