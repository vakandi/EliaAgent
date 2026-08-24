"""Tests for alert_manager.py — mocked subprocess + HTTP."""
from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.alert_manager import (
    AlertManager,
    AlertPayload,
    AlertResult,
    AlertType,
)


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def mgr() -> AlertManager:
    return AlertManager(
        electron_url="http://localhost:9999",
        ntfy_url="https://ntfy.sh/test-topic",
        debounce_window=300,
        http_timeout=2.0,
        enable_beep=False,
    )


@pytest.fixture
def payload() -> AlertPayload:
    return AlertPayload(
        title="Test Alert",
        message="Something happened",
        alert_type=AlertType.SUBWORKER_FAILED,
        urgent=True,
    )


def _make_httpx_response(status: int = 200) -> httpx.Response:
    return httpx.Response(status_code=status, request=httpx.Request("POST", "http://test"))


# ── AlertType ────────────────────────────────────────────────────────────────


class TestAlertType:
    def test_seven_types(self) -> None:
        assert len(AlertType) == 7

    def test_all_values_unique(self) -> None:
        vals = [t.value for t in AlertType]
        assert len(vals) == len(set(vals))


# ── AlertPayload ─────────────────────────────────────────────────────────────


class TestAlertPayload:
    def test_to_dict(self, payload: AlertPayload) -> None:
        d = payload.to_dict()
        assert d["title"] == "Test Alert"
        assert d["message"] == "Something happened"
        assert d["type"] == "subworker_failed"
        assert d["urgent"] is True

    def test_defaults(self) -> None:
        p = AlertPayload(title="x", message="y")
        assert p.alert_type == AlertType.GENERIC
        assert p.urgent is False


# ── AlertResult ──────────────────────────────────────────────────────────────


class TestAlertResult:
    def test_has_timestamp(self) -> None:
        r = AlertResult(sent=True, destination="electron")
        assert r.timestamp > 0
        assert r.error is None


# ── Debouncing ───────────────────────────────────────────────────────────────


class TestDebouncing:
    def test_not_debounced_first_time(self, mgr: AlertManager) -> None:
        assert mgr._is_debounced(AlertType.GENERIC) is False

    def test_debounced_after_sent(self, mgr: AlertManager) -> None:
        mgr._last_sent["generic"] = time.time()
        assert mgr._is_debounced(AlertType.GENERIC) is True

    def test_not_debounced_after_window(self, mgr: AlertManager) -> None:
        mgr._last_sent["generic"] = time.time() - 400
        assert mgr._is_debounced(AlertType.GENERIC) is False

    def test_different_types_independent(self, mgr: AlertManager) -> None:
        mgr._last_sent["subworker_failed"] = time.time()
        assert mgr._is_debounced(AlertType.SUBWORKER_FAILED) is True
        assert mgr._is_debounced(AlertType.SUBWORKER_COMPLETED) is False


# ── play_beep ────────────────────────────────────────────────────────────────


class TestPlayBeep:
    def test_disabled_returns_false(self, mgr: AlertManager) -> None:
        assert mgr.play_beep() is False

    def test_enabled_calls_afplay(self) -> None:
        mgr = AlertManager(enable_beep=True)
        mock_proc = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock_proc):
            result = mgr.play_beep()
        assert result is True

    def test_handles_exception(self) -> None:
        mgr = AlertManager(enable_beep=True)
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = mgr.play_beep()
        assert result is False


# ── post_electron_alert ──────────────────────────────────────────────────────


class TestPostElectronAlert:
    @pytest.mark.asyncio
    async def test_success(self, mgr: AlertManager, payload: AlertPayload) -> None:
        mock_client = AsyncMock()
        mock_client.post.return_value = _make_httpx_response(200)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("app.services.alert_manager.httpx.AsyncClient", return_value=mock_client):
            result = await mgr.post_electron_alert(payload)
        assert result.sent is True
        assert result.destination == "electron"

    @pytest.mark.asyncio
    async def test_http_error(self, mgr: AlertManager, payload: AlertPayload) -> None:
        mock_client = AsyncMock()
        mock_client.post.return_value = _make_httpx_response(500)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("app.services.alert_manager.httpx.AsyncClient", return_value=mock_client):
            result = await mgr.post_electron_alert(payload)
        assert result.sent is False
        assert "500" in result.error

    @pytest.mark.asyncio
    async def test_timeout(self, mgr: AlertManager, payload: AlertPayload) -> None:
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.TimeoutException("timed out")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("app.services.alert_manager.httpx.AsyncClient", return_value=mock_client):
            result = await mgr.post_electron_alert(payload)
        assert result.sent is False
        assert "timeout" in result.error


# ── post_ntfy_alert ──────────────────────────────────────────────────────────


class TestPostNtfyAlert:
    @pytest.mark.asyncio
    async def test_success(self, mgr: AlertManager, payload: AlertPayload) -> None:
        mock_client = AsyncMock()
        mock_client.post.return_value = _make_httpx_response(200)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("app.services.alert_manager.httpx.AsyncClient", return_value=mock_client):
            result = await mgr.post_ntfy_alert(payload)
        assert result.sent is True
        assert result.destination == "ntfy"

    @pytest.mark.asyncio
    async def test_timeout_fallback(self, mgr: AlertManager, payload: AlertPayload) -> None:
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.TimeoutException("timed out")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("app.services.alert_manager.httpx.AsyncClient", return_value=mock_client):
            result = await mgr.post_ntfy_alert(payload)
        assert result.sent is False
        assert "timeout" in result.error


# ── trigger_alert ────────────────────────────────────────────────────────────


class TestTriggerAlert:
    @pytest.mark.asyncio
    async def test_electron_success_no_ntfy(self, mgr: AlertManager, payload: AlertPayload) -> None:
        mock_client = AsyncMock()
        mock_client.post.return_value = _make_httpx_response(200)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("app.services.alert_manager.httpx.AsyncClient", return_value=mock_client):
            results = await mgr.trigger_alert(payload)
        assert len(results) == 1
        assert results[0].destination == "electron"

    @pytest.mark.asyncio
    async def test_electron_fail_fallback_ntfy(self, mgr: AlertManager, payload: AlertPayload) -> None:
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _make_httpx_response(500)
            return _make_httpx_response(200)

        mock_client = AsyncMock()
        mock_client.post.side_effect = side_effect
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("app.services.alert_manager.httpx.AsyncClient", return_value=mock_client):
            results = await mgr.trigger_alert(payload)
        assert len(results) == 2
        assert results[0].destination == "electron"
        assert results[1].destination == "ntfy"

    @pytest.mark.asyncio
    async def test_debounced_returns_empty(self, mgr: AlertManager, payload: AlertPayload) -> None:
        mgr._last_sent["subworker_failed"] = time.time()
        results = await mgr.trigger_alert(payload)
        assert results == []

    @pytest.mark.asyncio
    async def test_history_recorded(self, mgr: AlertManager, payload: AlertPayload) -> None:
        mock_client = AsyncMock()
        mock_client.post.return_value = _make_httpx_response(200)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("app.services.alert_manager.httpx.AsyncClient", return_value=mock_client):
            await mgr.trigger_alert(payload)
        assert len(mgr.history) == 1
        assert mgr.history[0].sent is True
