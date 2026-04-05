# Technical Concerns

**Analysis Date:** 2026-04-05

## Broken Tests

### Critical: `tests/tui/test_widgets.py` — Collection Error

**File:** `tests/tui/test_widgets.py`

Imports three deleted widget modules:
- `maribox.tui.widgets.agent_feed.AgentFeed` — deleted
- `maribox.tui.widgets.cell_panel.CellPanel` — deleted
- `maribox.tui.widgets.session_card.SessionCard` — deleted

**Impact:** Prevents test suite from running. 139 tests collect but the error halts execution.

**Fix needed:** Complete rewrite of `test_widgets.py` to test the new TUI widget classes: `MessagesList`, `MessageDisplay`, `InputBar`, `Sidebar`, `StatusBar`, `WelcomeWidget`.

### Medium: `tests/conftest.py` — Stale `sandbox` Section

**File:** `tests/conftest.py`

The `mock_config` fixture includes a `sandbox` section:
```python
"sandbox": {
    "base_url": "",
    "timeout_seconds": 300,
},
```

The `sandbox` section was removed from `config/schema.py` and `config/defaults.py`. Tests that load this fixture and pass it to schema parsing may fail.

**Fix needed:** Remove `sandbox` from `mock_config` fixture.

## Stub Implementations

### Agent LLM Integration — Placeholder Responses

**Files:** `src/maribox/agents/base.py`, all agent subclasses

`MariboxAgent.invoke()` returns a placeholder response:
```python
return AgentResponse(
    message=AgentMessage(role="assistant", content=f"[{self.name}] Received: {message[:200]}"),
    success=True, ...)
```

No actual LLM calls are made. The `stream()` method also yields a single placeholder chunk.

**Impact:** CLI `maribox agent run`, TUI chat, and MCP `agent_run` tool all return canned responses. The agent architecture (routing, tool definitions) is in place but not connected to an LLM backend.

**What's needed:** Integrate `litellm.acompletion()` into `MariboxAgent.invoke()`, passing system prompt, messages, and tool definitions. Handle tool call loops (agent calls tool → gets result → continues).

### TUI `_process_message()` — Canned Response

**File:** `src/maribox/tui/screens/chat.py`

`ChatScreen._process_message()` returns a fixed string instead of routing through `OrchestratorAgent`:
```python
async def _process_message(self, text: str) -> None:
    ...
    assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content="I'm your AI assistant...")
```

**What's needed:** Wire `_process_message()` to `OrchestratorAgent.invoke()` with streaming support.

### MarimoRuntime — Subprocess Fallback

**File:** `src/maribox/notebook/runtime.py`

`MarimoRuntime.start()` uses `subprocess.Popen` with `--headless` flag but returns a placeholder URL. Cell execution (`run_cell`) doesn't actually execute code — returns `[executed {cell_id}]` string.

**What's needed:** Implement WebSocket communication with marimo kernel for real cell execution, reactive updates, and output streaming.

## Architectural Concerns

### Legacy Module Name: `sandbox/`

**File:** `src/maribox/sandbox/session.py`

The module path `maribox.sandbox.session` was kept as a legacy name after removing AIO Sandbox. The `SessionManager` class inside is now purely local/directory-based with no container dependencies. The name "sandbox" is misleading for new contributors.

**Options:** Rename to `maribox.session.manager` or `maribox.sessions` in a future refactor.

### Google ADK — Dependency Without Usage

**File:** `pyproject.toml`

`google-adk>=0.5` is listed as a dependency but is never imported in the codebase. The agent system uses `litellm` for LLM calls and hand-rolled tool definitions instead of ADK's agent framework.

**Impact:** Unnecessary dependency increasing install size. Either integrate ADK properly or remove it.

### No Streaming Support in TUI

**File:** `src/maribox/tui/screens/chat.py`

Assistant messages appear as complete blocks rather than streaming token-by-token. The `MariboxAgent.stream()` method exists but is not called from the TUI.

**What's needed:** Use `stream()` method, update `MessageDisplay` widget incrementally as tokens arrive.

## Security Concerns

### No Concerns Found

- Key encryption uses AES-256-GCM with Argon2id — appropriate for the threat model
- Key zeroing with `ctypes.memset` — correct implementation
- Atomic file writes for `keys.enc` — prevents corruption
- Log masking covers known key patterns
- `keys.enc` is in `.gitignore`

## Performance Concerns

### No Baseline Measurements

- CLI startup time target: <500ms (per CLAUDE.md) — not measured
- TUI rendering target: ≥30fps (per CLAUDE.md) — not measured
- No benchmark tests exist

---

*Concerns analysis: 2026-04-05*
