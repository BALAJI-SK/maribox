"""Tests for sandbox session management."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from maribox.sandbox.client import SandboxClient, SandboxInfo
from maribox.sandbox.session import SessionManager, SessionState, generate_session_id


class TestGenerateSessionId:
    def test_returns_12_chars(self) -> None:
        sid = generate_session_id()
        assert len(sid) == 12

    def test_hex_chars(self) -> None:
        sid = generate_session_id()
        assert all(c in "0123456789abcdef" for c in sid)

    def test_unique(self) -> None:
        ids = {generate_session_id() for _ in range(100)}
        assert len(ids) == 100


class TestSessionManager:
    def _make_manager(self, tmp_maribox_home: Path) -> SessionManager:
        mock_client = MagicMock(spec=SandboxClient)
        mock_client.create_sandbox = AsyncMock(
            return_value=SandboxInfo(sandbox_id="sb-test", url="http://sandbox.test"),
        )
        mock_client.teardown = AsyncMock()
        return SessionManager(config_root=tmp_maribox_home, sandbox_client=mock_client)

    @pytest.mark.asyncio
    async def test_create_session(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        info = await manager.create_session(name="test-session")
        assert info.name == "test-session"
        assert info.status == SessionState.RUNNING
        assert info.sandbox_url == "http://sandbox.test"
        assert (tmp_maribox_home / "sessions" / info.id / "meta.toml").is_file()
        assert (tmp_maribox_home / "sessions" / info.id / "notebook.py").is_file()

    @pytest.mark.asyncio
    async def test_list_sessions(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        await manager.create_session(name="s1")
        await manager.create_session(name="s2")
        sessions = await manager.list_sessions()
        assert len(sessions) == 2
        names = {s.name for s in sessions}
        assert "s1" in names
        assert "s2" in names

    @pytest.mark.asyncio
    async def test_get_session(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        created = await manager.create_session(name="fetch-me")
        fetched = await manager.get_session(created.id)
        assert fetched.name == "fetch-me"
        assert fetched.id == created.id

    @pytest.mark.asyncio
    async def test_stop_session(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        created = await manager.create_session(name="stop-me")
        await manager.stop_session(created.id)
        info = await manager.get_session(created.id)
        assert info.status == SessionState.STOPPED
        assert info.sandbox_url == ""

    @pytest.mark.asyncio
    async def test_kill_session(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        created = await manager.create_session(name="kill-me")
        await manager.kill_session(created.id)
        info = await manager.get_session(created.id)
        assert info.status == SessionState.STOPPED

    @pytest.mark.asyncio
    async def test_remove_session(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        created = await manager.create_session(name="rm-me")
        session_dir = tmp_maribox_home / "sessions" / created.id
        assert session_dir.is_dir()
        await manager.remove_session(created.id)
        assert not session_dir.exists()

    @pytest.mark.asyncio
    async def test_snapshot(self, tmp_maribox_home: Path, tmp_path: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        created = await manager.create_session(name="snap-me")
        out = tmp_path / "snapshot.tar.gz"
        result = await manager.snapshot_session(created.id, out)
        assert result == out
        assert out.is_file()

    @pytest.mark.asyncio
    async def test_list_empty(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        sessions = await manager.list_sessions()
        assert sessions == []
