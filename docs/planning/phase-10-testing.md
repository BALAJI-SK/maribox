# Phase 10: Testing, Quality, and Hardening

## Objective

Establish comprehensive test coverage across all Maribox components, implement integration tests that exercise end-to-end workflows, and enforce quality gates that must pass before any merge. This phase targets >=80% line coverage on critical packages, validates all cross-phase interactions, and ensures the 500ms startup requirement holds under real conditions.

## Files to Create

- `tests/integration/__init__.py` — integration test package
- `tests/integration/test_session_lifecycle.py` — session create -> use -> teardown flow
- `tests/integration/test_notebook_flow.py` — notebook load -> edit -> run -> export flow
- `tests/integration/test_agent_collaboration.py` — multi-agent coordination flow
- `tests/integration/test_mcp_e2e.py` — MCP server end-to-end with all 25 tools
- `tests/integration/test_auth_flow.py` — full login -> use key -> logout cycle
- `tests/integration/test_config_resolution.py` — three-tier config resolution across scenarios
- `tests/conftest.py` — shared fixtures (temp config roots, mock Docker, mock LLM)
- `tests/performance/__init__.py` — performance test package
- `tests/performance/test_startup_time.py` — CLI import and startup timing
- `tests/performance/test_tui_rendering.py` — TUI frame rate benchmarks
- `tests/quality/__init__.py` — quality gate test package
- `tests/quality/test_coverage_gates.py` — coverage threshold assertions
- `tests/quality/test_type_checking.py` — mypy strict validation
- `tests/quality/test_lint.py` — ruff lint validation
- `scripts/run_quality_gates.sh` — script to run all quality checks

## Key Interfaces

### `tests/conftest.py`

```python
import pytest
from pathlib import Path
from typing import Generator

@pytest.fixture
def temp_config_root(tmp_path: Path) -> Path:
    """
    Create a temporary config root with the standard directory structure:
      .maribox/
        config.toml
        sessions/
        keys.enc (if needed)
    Returns the path to the .maribox/ directory.
    """

@pytest.fixture
def mock_docker(monkeypatch) -> None:
    """
    Mock the Docker SDK to prevent actual container creation.
    Mocks docker.from_env() to return a fake Docker client
    that records API calls for assertion.
    """

@pytest.fixture
def mock_llm_response(monkeypatch) -> None:
    """
    Mock the LLM agent to return canned responses.
    Useful for testing agent command flows without API calls.
    """

@pytest.fixture
async def running_session(temp_config_root, mock_docker) -> AsyncGenerator[SessionInfo, None]:
    """
    Create and yield a session in ACTIVE state.
    Automatically tears down after the test.
    """

@pytest.fixture
def sample_notebook() -> List[Cell]:
    """Return a list of Cells forming a simple notebook with known dependencies."""

@pytest.fixture
def rich_output() -> Generator[str, None, None]:
    """
    Capture Rich console output as a string.
    Returns the captured output after the test.
    """
```

### `tests/integration/test_session_lifecycle.py`

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_session_create_and_teardown(temp_config_root, mock_docker):
    """
    Full session lifecycle:
    1. Create a session via SessionManager
    2. Verify session directory exists with meta.toml, notebook.py, run.log
    3. Verify session state is ACTIVE
    4. Kill the session
    5. Verify session state is STOPPED and sandbox is removed
    """

@pytest.mark.asyncio
@pytest.mark.integration
async def test_session_resume(temp_config_root, mock_docker):
    """
    Session resume flow:
    1. Create a session
    2. Add cells to the notebook
    3. Kill the session (simulating a crash)
    4. Resume the session
    5. Verify cells are preserved and sandbox is re-created
    """

@pytest.mark.asyncio
@pytest.mark.integration
async def test_session_idle_cleanup(temp_config_root, mock_docker):
    """
    Idle cleanup:
    1. Create a session
    2. Set last_active to > 30 minutes ago
    3. Run cleanup_idle()
    4. Verify the session is torn down
    """

@pytest.mark.asyncio
@pytest.mark.integration
async def test_concurrent_sessions(temp_config_root, mock_docker):
    """
    Create 5 sessions simultaneously.
    Verify all have unique IDs and independent sandbox containers.
    """
```

### `tests/integration/test_notebook_flow.py`

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notebook_create_edit_run(running_session, mock_llm_response):
    """
    Notebook workflow:
    1. Create cells with dependencies (cell A defines x, cell B uses x)
    2. Edit cell A's code
    3. Verify cell B is marked STALE
    4. Run cells in topological order
    5. Verify outputs are correct
    """

@pytest.mark.asyncio
@pytest.mark.integration
async def test_notebook_export_round_trip(running_session, sample_notebook):
    """
    Export flow:
    1. Create a notebook with cells
    2. Export to .py file via write_notebook()
    3. Read back via read_notebook()
    4. Verify all cells, code, and ordering match
    """

@pytest.mark.asyncio
@pytest.mark.integration
async def test_notebook_cycle_detection(running_session):
    """
    Cycle detection:
    1. Create cells A, B, C where A uses B, B uses C, C uses A
    2. Verify CyclicDependencyError is raised
    3. Verify the error message includes the cycle path
    """
```

### `tests/integration/test_agent_collaboration.py`

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_orchestrator_routes_to_notebook_agent(mock_llm_response):
    """
    Agent routing:
    1. Send "create a cell that plots sin(x)" to OrchestratorAgent
    2. Verify it routes to NotebookAgent
    3. Verify NotebookAgent calls create_cell tool
    """

@pytest.mark.asyncio
@pytest.mark.integration
async def test_orchestrator_routes_to_debug_agent(mock_llm_response):
    """
    Debug routing:
    1. Send "fix the error in cell 3" to OrchestratorAgent
    2. Verify it routes to DebugAgent
    3. Verify DebugAgent calls analyze_error and propose_fix tools
    """

@pytest.mark.asyncio
@pytest.mark.integration
async def test_multi_agent_coordination(mock_llm_response):
    """
    Multi-agent:
    1. Send "create a dashboard with a chart" to OrchestratorAgent
    2. Verify it coordinates between NotebookAgent and UiAgent
    3. Verify the final response includes both code generation and UI setup
    """
```

### `tests/integration/test_mcp_e2e.py`

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_mcp_all_tools_respond(temp_config_root, mock_docker, mock_llm_response):
    """
    Call all 25 MCP tools and verify:
    - Each returns a non-empty string
    - No tool raises an unhandled exception
    - Error cases return proper MCP error responses
    """

@pytest.mark.asyncio
@pytest.mark.integration
async def test_mcp_session_workflow(temp_config_root, mock_docker):
    """
    MCP session workflow:
    1. session_create -> verify session_id in response
    2. notebook_create_cell with the session_id
    3. notebook_run_cell
    4. debug_last_error (expect "no errors")
    5. session_kill
    """
```

### `tests/performance/test_startup_time.py`

```python
import time
import subprocess

def test_cli_import_time():
    """
    Verify that importing maribox.cli takes less than 500ms.
    Measures a fresh Python process importing the module.
    """
    start = time.perf_counter()
    result = subprocess.run(
        ["python", "-c", "import maribox.cli"],
        capture_output=True,
        text=True,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert elapsed_ms < 500, f"CLI import took {elapsed_ms:.0f}ms (limit: 500ms)"

def test_cli_help_time():
    """
    Verify that `maribox --help` completes in under 1 second.
    """
    start = time.perf_counter()
    result = subprocess.run(
        ["python", "-m", "maribox.cli", "--help"],
        capture_output=True,
        text=True,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert result.returncode == 0
    assert elapsed_ms < 1000, f"`maribox --help` took {elapsed_ms:.0f}ms (limit: 1000ms)"
```

### `tests/quality/test_coverage_gates.py`

```python
def test_config_coverage(coverage_data):
    """Assert >= 80% coverage on config/ package."""
    assert coverage_data["config/"] >= 0.80

def test_security_coverage(coverage_data):
    """Assert >= 80% coverage on security/ package."""
    assert coverage_data["security/"] >= 0.80

def test_sandbox_coverage(coverage_data):
    """Assert >= 80% coverage on sandbox/ package."""
    assert coverage_data["sandbox/"] >= 0.80

def test_notebook_coverage(coverage_data):
    """Assert >= 80% coverage on notebook/ package."""
    assert coverage_data["notebook/"] >= 0.80

def test_agents_base_coverage(coverage_data):
    """Assert >= 80% coverage on agents/base.py."""
    assert coverage_data["agents/base.py"] >= 0.80

def test_agents_profile_coverage(coverage_data):
    """Assert >= 80% coverage on agents/profile.py."""
    assert coverage_data["agents/profile.py"] >= 0.80

def test_mcp_coverage(coverage_data):
    """Assert >= 80% coverage on mcp/ package."""
    assert coverage_data["mcp/"] >= 0.80
```

### `scripts/run_quality_gates.sh`

```bash
#!/usr/bin/env bash
# Run all quality gates for Maribox.
# Exit on first failure.

set -euo pipefail

echo "=== Quality Gate 1: Ruff Lint ==="
ruff check src/ tests/

echo "=== Quality Gate 2: MyPy Strict ==="
mypy --strict src/maribox/

echo "=== Quality Gate 3: Pytest with Coverage ==="
pytest tests/ \
    --cov=src/maribox/ \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-fail-under=80 \
    -v \
    --tb=short

echo "=== Quality Gate 4: Startup Time ==="
python -c "
import time, subprocess
start = time.perf_counter()
subprocess.run(['python', '-c', 'import maribox.cli'], check=True, capture_output=True)
elapsed = (time.perf_counter() - start) * 1000
assert elapsed < 500, f'Startup took {elapsed:.0f}ms (limit: 500ms)'
print(f'Startup time: {elapsed:.0f}ms')
"

echo "=== All Quality Gates Passed ==="
```

## Dependencies

- **All Phases (1-9)** must be complete: integration tests exercise cross-phase workflows. Quality gates validate all packages.
- Runtime packages: `pytest` (test runner), `pytest-asyncio` (async test support), `pytest-cov` (coverage), `pytest-mock` (mocking), `ruff` (linting), `mypy` (type checking), `textual` (TUI test tools, `pytest-textual-snapshot`).

## Testing Strategy

- **Layered testing approach**:
  1. **Unit tests** (per-phase, already defined): Each package has its own unit tests co-located or in `tests/unit/`.
  2. **Integration tests** (this phase): Cross-package flows in `tests/integration/`.
  3. **Performance tests** (this phase): Timing benchmarks in `tests/performance/`.
  4. **Quality gates** (this phase): Coverage, lint, and type-check assertions in `tests/quality/`.

- **Test markers**:
  - `@pytest.mark.integration` — requires Docker or external services
  - `@pytest.mark.llm` — requires real API keys (skipped in CI by default)
  - `@pytest.mark.slow` — takes > 5 seconds
  - `@pytest.mark.perf` — performance benchmarks

- **CI configuration**:
  - Run unit tests on every PR
  - Run integration tests on merge to main
  - Run quality gates on merge to main
  - Skip `@pytest.mark.llm` in CI (run manually or in nightly)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Integration tests are flaky due to Docker timing | CI failures that are not real bugs | Use generous timeouts (30s for container ops); retry failed assertions up to 3 times; mock Docker in fast tests, use real Docker only in dedicated integration suite |
| Coverage targets are too aggressive | Developers spend time gaming coverage instead of writing good tests | Focus coverage requirements on critical packages only; allow <80% on CLI commands and TUI screens where testing is harder; use `# pragma: no cover` sparingly for truly untestable code |
| MyPy strict mode rejects valid patterns | Constant mypy errors slow development | Maintain a `pyproject.toml` mypy config that enables strict mode but allows specific per-module overrides with documented reasons |
| Startup time regresses as more code is added | 500ms target becomes impossible | Measure startup time in CI on every PR; profile import chains quarterly; split heavy imports into lazy-loaded subpackages |
| Test suite takes too long to run | Developers skip running tests | Target < 60 seconds for unit tests, < 5 minutes for integration tests; parallelize with `pytest-xdist`; use `--lf` (last-failed) for quick iterations |
| Mocking Docker hides real bugs | Tests pass but real usage fails | Run a subset of integration tests against real Docker weekly; maintain a "smoke test" script that exercises the real CLI end-to-end |

## Acceptance Criteria

- [ ] Integration tests cover session lifecycle (create, resume, kill, cleanup)
- [ ] Integration tests cover notebook flow (create cells, edit, run, export)
- [ ] Integration tests cover agent collaboration (routing, multi-agent coordination)
- [ ] Integration tests cover MCP end-to-end (all 25 tools)
- [ ] Integration tests cover auth flow (login, get key, logout)
- [ ] Integration tests cover config resolution (all three tiers)
- [ ] Performance test verifies CLI import < 500ms
- [ ] Performance test verifies `maribox --help` < 1000ms
- [ ] Quality gate: `ruff check src/ tests/` passes with zero errors
- [ ] Quality gate: `mypy --strict src/maribox/` passes with zero errors
- [ ] Quality gate: `pytest --cov` reports >= 80% on `config/`, `security/`, `sandbox/`, `notebook/`, `agents/base.py`, `agents/profile.py`, `mcp/`
- [ ] `scripts/run_quality_gates.sh` passes end-to-end
- [ ] All test markers (`integration`, `llm`, `slow`, `perf`) are correctly applied
- [ ] CI configuration runs appropriate test suites on PR and merge events
- [ ] Test suite completes in < 60 seconds (unit) and < 5 minutes (integration)
