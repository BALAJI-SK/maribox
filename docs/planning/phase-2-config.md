# Phase 2: Configuration System

## Objective

Build the foundational configuration layer that provides a three-tier resolution chain for Maribox settings. This system must handle project-level overrides, user-level defaults, and environment-variable-driven paths so that every subsequent phase has a single, validated source of truth for how Maribox behaves. All configuration is persisted as TOML and validated through strict dataclass schemas before any component reads a value.

## Files to Create

- `src/maribox/config/__init__.py` — re-exports `MariboxConfig`, `load_config`, `save_config`
- `src/maribox/config/resolution.py` — three-tier config root resolution logic
- `src/maribox/config/schema.py` — dataclass definitions for all config sections
- `src/maribox/config/defaults.py` — factory functions that produce sensible defaults
- `src/maribox/config/io.py` — TOML load/save with validation round-trip
- `src/maribox/commands/config.py` — CLI subcommands: `maribox config get`, `set`, `list`, `init`

## Key Interfaces

### `resolution.py`

```python
def resolve_config_root() -> Path:
    """
    Resolution order:
    1. MARIBOX_HOME environment variable (if set, highest priority)
    2. Project-local .maribox/ directory (if it exists in cwd or any parent)
    3. User-level ~/.config/maribox/ (fallback default)

    Returns the Path to the effective config root directory.
    Raises ConfigurationError if no valid root can be resolved.
    """

def find_project_root(start: Path) -> Optional[Path]:
    """Walk up from `start` looking for .maribox/ or pyproject.toml."""

def ensure_config_dir(root: Path) -> Path:
    """Create the config directory tree if it does not exist."""
```

### `schema.py`

```python
@dataclass
class SandboxSection:
    runtime: str = "docker"               # docker | podman | local
    image: str = "maribox/sandbox:latest"
    memory_limit: str = "2g"
    cpu_limit: float = 2.0
    timeout_seconds: int = 300
    auto_teardown_minutes: int = 30

@dataclass
class MarimoSection:
    port: int = 0                         # 0 = auto-assign
    headless: bool = True
    hot_reload: bool = True

@dataclass
class TuiSection:
    theme: str = "dark"
    refresh_rate: int = 30                # fps target
    mouse_support: bool = True

@dataclass
class AgentProfile:
    name: str
    model: str                            # e.g. "gemini-2.0-flash"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = ""

@dataclass
class MariboxSection:
    default_agent: str = "notebook"
    log_level: str = "WARNING"
    telemetry: bool = False

@dataclass
class MariboxConfig:
    maribox: MariboxSection
    sandbox: SandboxSection
    marimo: MarimoSection
    tui: TuiSection
    agents: Dict[str, AgentProfile]       # profile_name -> AgentProfile

@dataclass
class ProjectConfig:
    """Project-level overrides stored in .maribox/config.toml."""
    name: str
    description: str = ""
    agents: Optional[Dict[str, AgentProfile]] = None
    sandbox: Optional[SandboxSection] = None
```

### `defaults.py`

```python
def default_config() -> MariboxConfig:
    """Return a MariboxConfig populated with all default values."""

def default_agent_profiles() -> Dict[str, AgentProfile]:
    """Return built-in agent profiles (notebook, ui, debug, session)."""
```

### `io.py`

```python
class ConfigLoadError(Exception): ...
class ConfigSaveError(Exception): ...

def load_config(path: Optional[Path] = None) -> MariboxConfig:
    """
    Load and validate configuration from the resolved config root.
    Merges user-level and project-level configs (project wins on conflict).
    Falls back to defaults for any missing sections.
    """

def save_config(config: MariboxConfig, path: Optional[Path] = None) -> None:
    """
    Serialize a MariboxConfig to TOML and write atomically.
    Uses write-to-temp-then-rename to avoid partial writes.
    """

def merge_configs(base: MariboxConfig, override: ProjectConfig) -> MariboxConfig:
    """Deep-merge project overrides into the base config."""
```

### `commands/config.py`

```python
def config_get(key: str) -> None:
    """Print the resolved value of a dotted config key (e.g. sandbox.runtime)."""

def config_set(key: str, value: str) -> None:
    """Set a dotted config key in the appropriate config file."""

def config_list() -> None:
    """Print the fully-resolved config as TOML."""

def config_init() -> None:
    """Create .maribox/config.toml in the current project with defaults."""
```

## Dependencies

- **Phase 1** must be complete: project scaffolding, `pyproject.toml`, directory layout, and `src/maribox/__init__.py` must all exist.
- Runtime: Python >=3.11, `tomllib` (stdlib) for reading, `tomli_w` for writing, `typing` for dataclass type hints.

## Testing Strategy

- **Unit tests for resolution order**: Mock `os.environ`, temp directories for project-local `.maribox/`, and `~/.config/maribox/`. Assert priority: `MARIBOX_HOME` > project local > user home.
- **Unit tests for schema validation**: Construct `MariboxConfig` with invalid values (negative port, empty agent name) and assert `ValidationError` or `TypeError`.
- **Unit tests for TOML round-trip**: Save a config, load it back, assert deep equality.
- **Unit tests for merge logic**: Project overrides replace base values; unset fields inherit from base.
- **CLI integration tests**: `maribox config init` creates files; `maribox config get sandbox.runtime` prints the expected value.
- **Edge cases**: Missing config file (should produce defaults), corrupt TOML (should raise `ConfigLoadError`), read-only filesystem (should raise `ConfigSaveError`).

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| `tomllib` read-only (no write) in stdlib | Cannot write TOML without extra dep | Pin `tomli_w` as a required dependency for writing |
| Three-tier resolution produces confusing results | User does not know which config is active | `maribox config list` always prints the resolved source for each key; `config get --verbose` shows the resolution chain |
| Dataclass mutation after load | Config objects silently drift from disk | `MariboxConfig` uses `frozen=True` on leaf sections; `save_config` is the only mutation path |
| Project root detection walks into home dir | Accidentally picks up unrelated `.maribox/` | Stop walking at `$HOME` boundary; require explicit `MARIBOX_HOME` for overrides beyond the project |
| TOML does not support all Python types | Loss of typed data on round-trip | Validate at load time; store complex types (e.g. `Path`) as strings and convert at access time |

## Acceptance Criteria

- [ ] `resolve_config_root()` returns the correct path for all three tiers
- [ ] `load_config()` returns a fully-populated `MariboxConfig` with defaults for missing sections
- [ ] `save_config()` produces valid TOML that round-trips through `load_config()`
- [ ] Project-level overrides correctly merge into user-level defaults
- [ ] `maribox config init` creates a valid `.maribox/config.toml` in the current directory
- [ ] `maribox config get <key>` prints the resolved value
- [ ] `maribox config set <key> <value>` persists the change to the correct config file
- [ ] `maribox config list` displays the full resolved configuration
- [ ] All config files are valid TOML that can be hand-edited
- [ ] Unit test coverage >= 90% for `config/` package
- [ ] No config values are hardcoded outside of `defaults.py`
