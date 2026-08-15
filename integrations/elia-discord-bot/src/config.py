from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
import re

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DISCORD_BOT_TOKEN: str = Field(..., description="Discord Bot Token")
    DISCORD_GUILD_ID: int | None = Field(None, description="Discord Server ID")
    DISCORD_ERROR_CHANNEL_ID: int = Field(..., description="Channel ID for error reports")
    DISCORD_ALLOWED_USER_IDS: str = Field(
        "",
        description="Comma-separated Discord user IDs allowed to use Elia",
    )

    OPENCODE_HOST: str = Field("http://localhost:4096", description="OpenCode API Host")
    OPENCODE_API_KEY: str | None = Field(None, description="OpenCode API Key")
    OPENCODE_MODEL: str = Field("big-pickle", description="Model ID to use")
    OPENCODE_AGENT: str = Field("elia", description="Agent ID to use")

    MAX_CONCURRENT_REQUESTS: int = Field(3, description="Max concurrent OpenCode requests")
    CONTEXT_HISTORY_LIMIT: int = Field(20, description="Max messages to keep in context")

    BOT_DIR: Path = Path(__file__).parent.parent
    LOG_DIR: Path = BOT_DIR / "logs"

    @property
    def allowed_discord_user_ids(self) -> set[int]:
        raw_ids = self.DISCORD_ALLOWED_USER_IDS.strip()
        if not raw_ids:
            return set()

        user_ids: set[int] = set()
        for token in re.split(r"[\s,]+", raw_ids):
            if not token:
                continue
            try:
                user_ids.add(int(token))
            except ValueError as exc:
                raise ValueError(
                    "DISCORD_ALLOWED_USER_IDS must contain only numeric Discord user IDs"
                ) from exc

        return user_ids

    def is_discord_user_allowed(self, user_id: int) -> bool:
        allowed_user_ids = self.allowed_discord_user_ids
        return user_id in allowed_user_ids if allowed_user_ids else False

def get_settings() -> Settings:
    settings = Settings()
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    return settings
