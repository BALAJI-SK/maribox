# Coding Conventions

**Analysis Date:** 2026-04-05

## Code Style

**Formatting (ruff):**
- Target: Python 3.11
- Line length: 120 characters
- Rule set: `E, F, I, N, UP, B, SIM, RUF` (pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, flake8-bugbear, flake8-simplify, ruff-specific)
- Import sorting enforced by isort rules

**Type checking (mypy):**
- Mode: `--strict` (full strict mode)
- All functions have typed parameters and return types
- No `Any` without explicit justification
- `from __future__ import annotations` used consistently across all files

**Naming:**
- Modules: `snake_case.py` (e.g., `cell_tools.py`, `session_manager.py`)
- Classes: `PascalCase` (e.g., `MariboxAgent`, `OrchestratorAgent`, `ChatScreen`)
- Functions/methods: `snake_case` (e.g., `_route_request()`, `get_dependencies()`)
- Private members: `_leading_underscore` (e.g., `_cells`, `_process`, `_register_tools()`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `_ROUTING_RULES`, `DEFAULT_CONFIG`)
- Type aliases: `PascalCase` (e.g., `CellId = NewType("CellId", str)`)

## Structural Patterns

**ABC pattern for agents:**
```python
class MariboxAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    @abstractmethod
    def description(self) -> str: ...
    @abstractmethod
    def _register_tools(self) -> list[dict[str, Any]]: ...
    @abstractmethod
    def _system_prompt(self) -> str: ...
```
All agent subclasses (NotebookAgent, UIAgent, DebugAgent, SessionAgent) follow this interface. The OrchestratorAgent additionally receives a `sub_agents` dict.

**Dataclass pattern for config/models:**
```python
@dataclass
class MariboxSection:
    version: str = "1"
    ...
    @classmethod
    def from_toml(cls, data: dict[str, object]) -> MariboxSection: ...
    def to_toml(self) -> dict[str, object]: ...
```
All config schema types use `@dataclass` with `from_toml()` / `to_toml()` serialization methods.

**Tool definition pattern:**
```python
def _register_tools(self) -> list[dict[str, Any]]:
    return [
        {
            "name": "tool_name",
            "description": "...",
            "parameters": {
                "type": "object",
                "properties": { ... },
                "required": [...],
            },
        }
    ]
```
Tool definitions follow OpenAI function-calling JSON schema format.

**Command pattern:**
CLI commands are functions decorated with `@app.command()` in individual modules under `src/maribox/commands/`. Each command function instantiates required services, performs the operation, and returns output.

## Error Handling

**Exception hierarchy:**
```
MariboxError (base)
├── ConfigError
├── AuthError
├── SessionError
├── AgentError
└── EncryptionError
```

**Patterns:**
- Custom exceptions raised with descriptive messages including remediation hints
  - `raise AgentError(f"No API key configured for provider '{self._profile.provider}'. Run: maribox auth set {self._profile.provider}")`
- `try/except` with specific exception types, re-raising as domain exceptions
  - `except Exception as e: raise EncryptionError(f"Failed to load key store: {e}") from e`
- Error chaining with `from e` to preserve stack traces
- `log_mask.py` masks API key patterns (`sk-ant-*`, `AIza*`, `sk-*`) in output

## Import Patterns

- Standard library → third-party → local imports (enforced by ruff isort)
- `from __future__ import annotations` at the top of every file
- Lazy imports inside functions for heavy dependencies (e.g., `from maribox.config.io import ...` inside MCP tool closures)
- No wildcard imports

## Docstrings

- Module-level docstrings with triple-quoted strings
- Single-line format: `"""Brief description of what this module/class/function does."""`
- No comprehensive argument/return docstrings (type hints serve this purpose under `--strict`)

## Security Patterns

- Key material is zeroed with `ctypes.memset` immediately after use
- Encryption uses AES-256-GCM with Argon2id key derivation (3 iterations, 64 MB memory)
- Atomic file writes (write to `.tmp`, then `rename`)
- Key patterns masked in all log output
- API keys never appear in env vars, subprocess args, temp files, or logs

---

*Convention analysis: 2026-04-05*
