"""Tests for session management (local directory-based)."""

from __future__ import annotations

from pathlib import Path

import pytest

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
        return SessionManager(config_root=tmp_maribox_home)

    def test_create_session(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        info = manager.create_session(name="test-session")
        assert info.name == "test-session"
        assert info.status == SessionState.RUNNING
        assert (tmp_maribox_home / "sessions" / info.id / "meta.toml").is_file()
        assert (tmp_maribox_home / "sessions" / info.id / "notebook.py").is_file()

    def test_list_sessions(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        manager.create_session(name="s1")
        manager.create_session(name="s2")
        sessions = manager.list_sessions()
        assert len(sessions) == 2
        names = {s.name for s in sessions}
        assert "s1" in names
        assert "s2" in names

    def test_get_session(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        created = manager.create_session(name="fetch-me")
        fetched = manager.get_session(created.id)
        assert fetched.name == "fetch-me"
        assert fetched.id == created.id

    def test_stop_session(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        created = manager.create_session(name="stop-me")
        manager.stop_session(created.id)
        info = manager.get_session(created.id)
        assert info.status == SessionState.STOPPED

    def test_kill_session(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        created = manager.create_session(name="kill-me")
        manager.kill_session(created.id)
        info = manager.get_session(created.id)
        assert info.status == SessionState.STOPPED

    def test_remove_session(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        created = manager.create_session(name="rm-me")
        session_dir = tmp_maribox_home / "sessions" / created.id
        assert session_dir.is_dir()
        manager.remove_session(created.id)
        assert not session_dir.exists()

    def test_snapshot(self, tmp_maribox_home: Path, tmp_path: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        created = manager.create_session(name="snap-me")
        out = tmp_path / "snapshot.tar.gz"
        result = manager.snapshot_session(created.id, out)
        assert result == out
        assert out.is_file()

    def test_list_empty(self, tmp_maribox_home: Path) -> None:
        manager = self._make_manager(tmp_maribox_home)
        sessions = manager.list_sessions()
        assert sessions == []
