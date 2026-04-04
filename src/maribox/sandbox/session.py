"""Session lifecycle management — create, list, stop, kill, snapshot."""

from __future__ import annotations

import shutil
import tarfile
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

import tomli_w

from maribox.config.io import load_config
from maribox.config.resolution import resolve_config_root
from maribox.exceptions import SessionError


class SessionState(StrEnum):
    """Session status states."""

    CREATING = "creating"
    RUNNING = "running"
    IDLE = "idle"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class SessionInfo:
    """Metadata about a single session."""

    id: str
    name: str
    status: SessionState
    provider: str
    model: str
    marimo_url: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


def generate_session_id() -> str:
    """Generate a short, readable session ID."""
    return uuid.uuid4().hex[:12]


class SessionManager:
    """Manages the lifecycle of maribox sessions.

    Each session has its own directory under .maribox/sessions/<id>/
    containing meta.toml, notebook.py, and run.log.
    """

    def __init__(self, config_root: Path | None = None) -> None:
        self._root = config_root or resolve_config_root()
        self._sessions_dir = self._root / "sessions"

    @property
    def sessions_dir(self) -> Path:
        return self._sessions_dir

    def _session_dir(self, session_id: str) -> Path:
        return self._sessions_dir / session_id

    def _meta_path(self, session_id: str) -> Path:
        return self._session_dir(session_id) / "meta.toml"

    def _write_meta(self, session_id: str, info: SessionInfo) -> None:
        """Write session metadata to meta.toml."""
        meta = {
            "id": info.id,
            "name": info.name,
            "status": info.status.value,
            "provider": info.provider,
            "model": info.model,
            "marimo_url": info.marimo_url,
            "created_at": info.created_at,
        }
        self._session_dir(session_id).mkdir(parents=True, exist_ok=True)
        with open(self._meta_path(session_id), "wb") as f:
            tomli_w.dump(meta, f)

    def _read_meta(self, session_id: str) -> SessionInfo:
        """Read session metadata from meta.toml."""
        import tomllib

        meta_path = self._meta_path(session_id)
        if not meta_path.is_file():
            raise SessionError(f"Session not found: {session_id}")

        with open(meta_path, "rb") as f:
            data = tomllib.load(f)

        return SessionInfo(
            id=data["id"],
            name=data.get("name", ""),
            status=SessionState(data.get("status", "idle")),
            provider=data.get("provider", ""),
            model=data.get("model", ""),
            marimo_url=data.get("marimo_url", ""),
            created_at=data.get("created_at", ""),
        )

    def create_session(
        self,
        name: str | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> SessionInfo:
        """Create a new local session with a marimo kernel."""
        session_id = generate_session_id()

        # Load defaults from config
        config = load_config(self._root)
        provider = provider or config.maribox.default_provider
        model = model or config.maribox.default_model
        name = name or f"session-{session_id}"

        info = SessionInfo(
            id=session_id,
            name=name,
            status=SessionState.RUNNING,
            provider=provider,
            model=model,
        )
        self._write_meta(session_id, info)

        # Create empty notebook.py and run.log
        session_dir = self._session_dir(session_id)
        (session_dir / "notebook.py").write_text('"""maribox notebook"""\n')
        (session_dir / "run.log").write_text("")

        return info

    def list_sessions(self) -> list[SessionInfo]:
        """List all sessions."""
        if not self._sessions_dir.is_dir():
            return []

        sessions: list[SessionInfo] = []
        for session_dir in sorted(self._sessions_dir.iterdir()):
            if session_dir.is_dir() and (session_dir / "meta.toml").is_file():
                try:
                    sessions.append(self._read_meta(session_dir.name))
                except SessionError:
                    continue
        return sessions

    def get_session(self, session_id: str) -> SessionInfo:
        """Get a single session's metadata."""
        return self._read_meta(session_id)

    def stop_session(self, session_id: str) -> None:
        """Gracefully stop a session (marimo kernel)."""
        info = self._read_meta(session_id)
        info.status = SessionState.STOPPED
        info.marimo_url = ""
        self._write_meta(session_id, info)

    def kill_session(self, session_id: str) -> None:
        """Force-terminate a session without cleanup."""
        info = self._read_meta(session_id)
        info.status = SessionState.STOPPED
        info.marimo_url = ""
        self._write_meta(session_id, info)

    def snapshot_session(self, session_id: str, out_path: Path | None = None) -> Path:
        """Save notebook.py + run.log to a tarball archive."""
        info = self._read_meta(session_id)
        session_dir = self._session_dir(session_id)

        if out_path is None:
            out_path = Path.cwd() / f"maribox-snapshot-{session_id}.tar.gz"

        with tarfile.open(out_path, "w:gz") as tar:
            for name in ("meta.toml", "notebook.py", "run.log"):
                file_path = session_dir / name
                if file_path.is_file():
                    tar.add(file_path, arcname=f"{info.name}/{name}")

        return out_path

    def remove_session(self, session_id: str) -> None:
        """Remove a session directory."""
        session_dir = self._session_dir(session_id)
        if not session_dir.is_dir():
            raise SessionError(f"Session not found: {session_id}")

        shutil.rmtree(session_dir)
