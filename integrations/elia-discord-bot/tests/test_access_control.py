import pytest

from src.bot import EliaDiscordBot
from src.config import Settings


def make_settings(allowed_ids: str = "123456789012345678") -> Settings:
    return Settings(
        _env_file=None,
        DISCORD_BOT_TOKEN="token",
        DISCORD_ERROR_CHANNEL_ID=1,
        DISCORD_ALLOWED_USER_IDS=allowed_ids,
    )


def test_settings_parses_allowed_user_ids():
    settings = make_settings("123, 456  ,789")

    assert settings.allowed_discord_user_ids == {123, 456, 789}
    assert settings.is_discord_user_allowed(456) is True
    assert settings.is_discord_user_allowed(999) is False


def test_settings_rejects_non_numeric_allowed_user_ids():
    settings = make_settings("123,abc")

    with pytest.raises(ValueError, match="DISCORD_ALLOWED_USER_IDS"):
        _ = settings.allowed_discord_user_ids


def test_bot_uses_allowlist():
    bot = EliaDiscordBot(settings=make_settings("42, 99"))

    assert bot._is_user_allowed(42) is True
    assert bot._is_user_allowed(99) is True
    assert bot._is_user_allowed(7) is False


@pytest.mark.asyncio
async def test_deny_access_sends_ephemeral_message():
    bot = EliaDiscordBot(settings=make_settings())

    captured = {}

    class Response:
        async def send_message(self, content: str, ephemeral: bool = False):
            captured["content"] = content
            captured["ephemeral"] = ephemeral

    class Interaction:
        response = Response()

    await bot._deny_access(Interaction())

    assert captured["content"] == "You are not authorized to use this Elia bot."
    assert captured["ephemeral"] is True
