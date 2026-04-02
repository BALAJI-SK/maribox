"""Config schema — typed dataclass models for maribox configuration."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MariboxSection:
    """[maribox] config section."""

    version: str = "1"
    default_provider: str = "anthropic"
    default_model: str = "claude-sonnet-4-6"
    auto_open_browser: bool = False
    log_level: str = "info"

    @classmethod
    def from_toml(cls, data: dict[str, object]) -> MariboxSection:
        return cls(
            version=str(data.get("version", cls.version)),
            default_provider=str(data.get("default_provider", cls.default_provider)),
            default_model=str(data.get("default_model", cls.default_model)),
            auto_open_browser=bool(data.get("auto_open_browser", cls.auto_open_browser)),
            log_level=str(data.get("log_level", cls.log_level)),
        )

    def to_toml(self) -> dict[str, object]:
        return {
            "version": self.version,
            "default_provider": self.default_provider,
            "default_model": self.default_model,
            "auto_open_browser": self.auto_open_browser,
            "log_level": self.log_level,
        }


@dataclass
class SandboxSection:
    """[sandbox] config section."""

    base_url: str = ""
    timeout_seconds: int = 300

    @classmethod
    def from_toml(cls, data: dict[str, object]) -> SandboxSection:
        return cls(
            base_url=str(data.get("base_url", cls.base_url)),
            timeout_seconds=int(data.get("timeout_seconds", cls.timeout_seconds)),
        )

    def to_toml(self) -> dict[str, object]:
        return {"base_url": self.base_url, "timeout_seconds": self.timeout_seconds}


@dataclass
class MarimoSection:
    """[marimo] config section."""

    port_range: tuple[int, int] = (7000, 7100)
    headless: bool = True

    @classmethod
    def from_toml(cls, data: dict[str, object]) -> MarimoSection:
        pr = data.get("port_range", cls.port_range)
        port_tuple = (int(pr[0]), int(pr[1])) if isinstance(pr, (list, tuple)) else cls.port_range
        return cls(
            port_range=port_tuple,
            headless=bool(data.get("headless", cls.headless)),
        )

    def to_toml(self) -> dict[str, object]:
        return {"port_range": list(self.port_range), "headless": self.headless}


@dataclass
class TuiSection:
    """[tui] config section."""

    theme: str = "dark"
    refresh_rate_ms: int = 250
    show_agent_thoughts: bool = True

    @classmethod
    def from_toml(cls, data: dict[str, object]) -> TuiSection:
        return cls(
            theme=str(data.get("theme", cls.theme)),
            refresh_rate_ms=int(data.get("refresh_rate_ms", cls.refresh_rate_ms)),
            show_agent_thoughts=bool(data.get("show_agent_thoughts", cls.show_agent_thoughts)),
        )

    def to_toml(self) -> dict[str, object]:
        return {
            "theme": self.theme,
            "refresh_rate_ms": self.refresh_rate_ms,
            "show_agent_thoughts": self.show_agent_thoughts,
        }


@dataclass
class MariboxConfig:
    """Top-level maribox configuration (config.toml)."""

    maribox: MariboxSection = field(default_factory=MariboxSection)
    sandbox: SandboxSection = field(default_factory=SandboxSection)
    marimo: MarimoSection = field(default_factory=MarimoSection)
    tui: TuiSection = field(default_factory=TuiSection)

    @classmethod
    def from_toml(cls, data: dict[str, dict[str, object]]) -> MariboxConfig:
        return cls(
            maribox=MariboxSection.from_toml(data.get("maribox", {})),
            sandbox=SandboxSection.from_toml(data.get("sandbox", {})),
            marimo=MarimoSection.from_toml(data.get("marimo", {})),
            tui=TuiSection.from_toml(data.get("tui", {})),
        )

    def to_toml(self) -> dict[str, dict[str, object]]:
        return {
            "maribox": self.maribox.to_toml(),
            "sandbox": self.sandbox.to_toml(),
            "marimo": self.marimo.to_toml(),
            "tui": self.tui.to_toml(),
        }


@dataclass
class AgentOverride:
    """Per-agent model/provider override from project.toml."""

    model: str | None = None
    provider: str | None = None

    @classmethod
    def from_toml(cls, data: dict[str, object]) -> AgentOverride:
        return cls(
            model=str(data["model"]) if "model" in data else None,
            provider=str(data["provider"]) if "provider" in data else None,
        )

    def to_toml(self) -> dict[str, str]:
        result: dict[str, str] = {}
        if self.model is not None:
            result["model"] = self.model
        if self.provider is not None:
            result["provider"] = self.provider
        return result


@dataclass
class ProjectConfig:
    """Per-project override config (project.toml)."""

    name: str = ""
    provider: str | None = None
    model: str | None = None
    agents: dict[str, AgentOverride] = field(default_factory=dict)

    @classmethod
    def from_toml(cls, data: dict[str, object]) -> ProjectConfig:
        project_data = data.get("project", {})
        agents_data = data.get("agents", {})
        agents = {k: AgentOverride.from_toml(v) for k, v in agents_data.items() if isinstance(v, dict)}
        return cls(
            name=str(project_data.get("name", "")),
            provider=str(project_data["provider"]) if "provider" in project_data else None,
            model=str(project_data["model"]) if "model" in project_data else None,
            agents=agents,
        )

    def to_toml(self) -> dict[str, object]:
        result: dict[str, object] = {}
        project: dict[str, str] = {"name": self.name}
        if self.provider is not None:
            project["provider"] = self.provider
        if self.model is not None:
            project["model"] = self.model
        result["project"] = project
        if self.agents:
            result["agents"] = {k: v.to_toml() for k, v in self.agents.items()}
        return result


@dataclass
class AgentProfile:
    """Single agent profile entry from agents/profiles.toml."""

    model: str
    provider: str

    @classmethod
    def from_toml(cls, data: dict[str, object]) -> AgentProfile:
        return cls(
            model=str(data["model"]),
            provider=str(data["provider"]),
        )

    def to_toml(self) -> dict[str, str]:
        return {"model": self.model, "provider": self.provider}
