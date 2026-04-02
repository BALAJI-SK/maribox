"""Cell representation — the fundamental unit of a marimo notebook."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import NewType

CellId = NewType("CellId", str)


class CellStatus(StrEnum):
    """Execution status of a cell."""

    OK = "ok"
    RUNNING = "running"
    ERROR = "error"
    STALE = "stale"


@dataclass
class CellOutput:
    """Output from a cell execution."""

    type: str  # stdout | stderr | error | display_data
    text: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class Cell:
    """A single marimo notebook cell."""

    id: CellId
    code: str
    name: str | None = None
    outputs: list[CellOutput] = field(default_factory=list)
    status: CellStatus = CellStatus.OK
