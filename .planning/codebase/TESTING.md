# Testing

**Analysis Date:** 2026-04-05

## Framework

- **pytest** >=8 with **pytest-asyncio** >=0.24 and **pytest-cov** >=6
- Config: `[tool.pytest.ini_options]` in `pyproject.toml`
  - `testpaths = ["tests"]`
  - `asyncio_mode = "auto"` — all async tests auto-detected
- Coverage target: ≥80% on core modules (per CLAUDE.md)

## Test Structure

```
tests/
├── conftest.py                  # Shared fixtures (tmp_maribox_home, mock_config)
├── agents/
│   ├── test_base.py             # MariboxAgent ABC tests
│   ├── test_orchestrator.py     # Routing and delegation tests
│   ├── test_profile.py          # Profile loading tests
│   └── test_tools.py            # Tool definition validation
├── auth/
│   └── test_manager.py          # AuthManager CRUD tests
├── commands/                    # CLI command tests
├── config/
│   ├── test_io.py               # Config load/save tests
│   └── test_schema.py           # Schema serialization tests
├── integration/
│   └── test_integration.py      # Full workflow tests (config lifecycle, auth, session, DAG)
├── mcp/
│   ├── test_server.py           # MCP server creation tests
│   └── test_tools.py            # Tool helper tests
├── notebook/
│   ├── test_cell.py             # Cell model tests
│   ├── test_dag.py              # Dependency graph tests
│   └── test_export.py           # Notebook import/export tests
├── sandbox/
│   └── test_session.py          # SessionManager tests
├── security/
│   ├── test_encryption.py       # AES-256-GCM, KeyStore, zero_memory tests
│   └── test_log_mask.py         # Key masking pattern tests
└── tui/
    ├── test_app.py              # MariboxApp creation tests
    └── test_widgets.py          # Widget tests (BROKEN — references deleted widgets)
```

## Test Count

- ~139 tests collected (with 1 collection error in `tests/tui/test_widgets.py`)
- Test collection: `pytest --co -q` shows 139 tests + 1 error

## Fixtures

**`tmp_maribox_home`** (`conftest.py`):
```python
@pytest.fixture
def tmp_maribox_home(tmp_path: Path) -> Path:
    home = tmp_path / ".maribox"
    home.mkdir()
    (home / "sessions").mkdir()
    (home / "agents").mkdir()
    return home
```

**`mock_config`** (`conftest.py`):
Provides a default config dict with `maribox`, `marimo`, `tui` sections. **Note:** Still contains a stale `sandbox` section that was removed from the actual config schema.

## Testing Patterns

**Synchronous unit tests:**
```python
def test_store_and_retrieve(self, tmp_path: Path) -> None:
    store = KeyStore(tmp_path)
    store.store_key("anthropic", "sk-ant-test-key")
    result = store.retrieve_key("anthropic")
    assert result == "sk-ant-test-key"
```

**Async tests (auto-detected):**
```python
@pytest.mark.asyncio
async def test_add_and_run_cell(self) -> None:
    runtime = MarimoRuntime()
    cell = await runtime.add_cell("x = 42")
    assert cell.code == "x = 42"
```

**Integration tests (multi-step workflows):**
```python
def test_full_config_lifecycle(self, tmp_path: Path) -> None:
    config_root = init_config_dir(tmp_path, scope="project")
    config = load_config(config_root)
    config.maribox.default_provider = "glm"
    save_config(config_root, config)
    reloaded = load_config(config_root)
    assert reloaded.maribox.default_provider == "glm"
```

## Coverage

- Target: ≥80% on core modules
- Currently unmeasured (no baseline report available)
- Run: `uv run pytest --cov=maribox --cov-report=term-missing`

## Known Test Issues

1. **`tests/tui/test_widgets.py`** — BROKEN: Imports `AgentFeed`, `CellPanel`, `SessionCard` which were deleted during TUI redesign. Needs complete rewrite for new widgets.

2. **`tests/conftest.py`** — Contains stale `sandbox` section in `mock_config` fixture that no longer exists in config schema.

3. **Agent tests are stubs** — `test_orchestrator.py` tests routing keywords but doesn't test actual LLM invocation (agents return placeholder responses).

4. **No TUI visual tests** — Textual supports `app.run_test()` with `Pilot` for simulating key presses, but no such tests exist yet.

---

*Testing analysis: 2026-04-05*
