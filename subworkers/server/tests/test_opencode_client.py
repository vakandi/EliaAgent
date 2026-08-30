"""Tests for utils/exceptions.py and utils/opencode_client.py."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.utils.exceptions import (
    AlertError,
    ConfigError,
    OpenCodeConnectionError,
    OpenCodeError,
    OpenCodeSessionError,
    OpenCodeTimeoutError,
    RateLimitError,
    SchedulerError,
    SubworkerError,
)
from app.utils.opencode_client import OpenCodeClient, DEFAULT_MCP_SERVERS


class TestExceptionHierarchy:
    def test_all_extend_subworker_error(self) -> None:
        assert issubclass(OpenCodeError, SubworkerError)
        assert issubclass(OpenCodeConnectionError, SubworkerError)
        assert issubclass(OpenCodeTimeoutError, SubworkerError)
        assert issubclass(OpenCodeSessionError, SubworkerError)
        assert issubclass(RateLimitError, SubworkerError)
        assert issubclass(ConfigError, SubworkerError)
        assert issubclass(SchedulerError, SubworkerError)
        assert issubclass(AlertError, SubworkerError)

    def test_open_code_subclasses_extend_open_code_error(self) -> None:
        assert issubclass(OpenCodeConnectionError, OpenCodeError)
        assert issubclass(OpenCodeTimeoutError, OpenCodeError)
        assert issubclass(OpenCodeSessionError, OpenCodeError)
        assert issubclass(RateLimitError, OpenCodeError)

    def test_exceptions_carry_status_code(self) -> None:
        exc = OpenCodeError("test", status_code=500)
        assert exc.status_code == 500

    def test_exceptions_carry_detail(self) -> None:
        exc = OpenCodeError("test", detail="some detail")
        assert exc.detail == "some detail"


class TestDefaultMCPServers:
    def test_default_list_has_six_servers(self) -> None:
        assert len(DEFAULT_MCP_SERVERS) == 6

    def test_expected_servers_present(self) -> None:
        expected = ["codegraph", "context7", "grep_app", "lsp", "parallel-browser-mcp", "websearch"]
        assert DEFAULT_MCP_SERVERS == expected


class TestOpenCodeClientInit:
    def test_default_url(self) -> None:
        client = OpenCodeClient()
        assert client._base_url == "http://127.0.0.1:5655"

    def test_custom_url(self) -> None:
        client = OpenCodeClient(base_url="http://localhost:8080")
        assert client._base_url == "http://localhost:8080"

    def test_strips_trailing_slash(self) -> None:
        client = OpenCodeClient(base_url="http://localhost:8080/")
        assert client._base_url == "http://localhost:8080"


class TestOpenCodeClientContextManager:
    @pytest.mark.asyncio
    async def test_context_manager_creates_client(self) -> None:
        async with OpenCodeClient() as client:
            assert client._client is not None

    @pytest.mark.asyncio
    async def test_context_manager_closes_client(self) -> None:
        client = OpenCodeClient()
        async with client:
            pass
        assert client._client is None

    @pytest.mark.asyncio
    async def test_ensure_client_raises_without_context(self) -> None:
        client = OpenCodeClient()
        with pytest.raises(OpenCodeConnectionError, match="not initialized"):
            client._ensure_client()


class TestOpenCodeClientHealth:
    @pytest.mark.asyncio
    async def test_health_connection_error(self) -> None:
        async with OpenCodeClient(base_url="http://127.0.0.1:59999") as client:
            with pytest.raises(OpenCodeConnectionError):
                await client.health()

    @pytest.mark.asyncio
    async def test_is_healthy_returns_false_on_connection_error(self) -> None:
        async with OpenCodeClient(base_url="http://127.0.0.1:59999") as client:
            assert await client.is_healthy() is False


class TestOpenCodeClientListSessions:
    @pytest.mark.asyncio
    async def test_list_sessions_passes_limit_param(self) -> None:
        async with OpenCodeClient(base_url="http://127.0.0.1:59999") as client:
            with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
                mock_req.return_value = []
                await client.list_sessions(limit=2000)
                mock_req.assert_called_once_with("GET", "/session/", params={"limit": 2000})

    @pytest.mark.asyncio
    async def test_list_sessions_default_limit_is_100(self) -> None:
        async with OpenCodeClient(base_url="http://127.0.0.1:59999") as client:
            with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
                mock_req.return_value = []
                await client.list_sessions()
                mock_req.assert_called_once_with("GET", "/session/", params={"limit": 100})

    @pytest.mark.asyncio
    async def test_list_sessions_returns_empty_on_non_list_response(self) -> None:
        async with OpenCodeClient(base_url="http://127.0.0.1:59999") as client:
            with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
                mock_req.return_value = {"unexpected": "dict"}
                assert await client.list_sessions() == []
