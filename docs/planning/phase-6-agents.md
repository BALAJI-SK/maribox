# Phase 6: Agent System

## Objective

Implement a multi-agent architecture that wraps Google ADK's `LlmAgent` to provide specialized AI assistants for different Maribox workflows. The system uses a hierarchical pattern with an `OrchestratorAgent` that delegates to specialized sub-agents (notebook, UI, debug, session), each equipped with domain-specific tools. Agent profiles are loaded from TOML configuration files and support multiple LLM providers via LiteLLM wrappers.

## Files to Create

- `src/maribox/agents/__init__.py` — re-exports base agent classes and profile loader
- `src/maribox/agents/base.py` — `MariboxAgent` ABC wrapping Google ADK `LlmAgent`
- `src/maribox/agents/orchestrator.py` — `OrchestratorAgent` with sub-agent delegation
- `src/maribox/agents/notebook_agent.py` — notebook manipulation and code generation agent
- `src/maribox/agents/ui_agent.py` — UI component generation agent
- `src/maribox/agents/debug_agent.py` — error analysis and fix proposal agent
- `src/maribox/agents/session_agent.py` — session management agent
- `src/maribox/agents/profile.py` — agent profile loader from TOML configuration
- `src/maribox/agents/tools/__init__.py` — re-exports all tool modules
- `src/maribox/agents/tools/cell_tools.py` — tools for cell manipulation
- `src/maribox/agents/tools/notebook_tools.py` — tools for notebook-level operations
- `src/maribox/agents/tools/session_tools.py` — tools for session management
- `src/maribox/agents/tools/debug_tools.py` — tools for debugging and introspection
- `src/maribox/agents/tools/ui_tools.py` — tools for UI component generation
- `src/agents/profiles.toml` — default agent profile definitions (non-code resource)

## Key Interfaces

### `base.py`

```python
from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator, Any, Dict, List
from google.adk import Agent as AdkAgent
from google.adk.agents import LlmAgent

@dataclass
class AgentMessage:
    """A message from an agent, potentially containing text and/or tool calls."""
    role: str                       # "user" | "assistant" | "system"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResponse:
    """The final response from an agent invocation."""
    message: AgentMessage
    success: bool
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    duration_ms: float = 0.0
    model: str = ""
    tokens_used: Dict[str, int] = field(default_factory=dict)

class MariboxAgent(ABC):
    """
    Abstract base class for all Maribox agents.
    Wraps Google ADK's LlmAgent with Maribox-specific configuration,
    tool registration, and response handling.
    """

    def __init__(
        self,
        profile: AgentProfile,
        auth_manager: AuthManager,
        config: MariboxConfig,
    ) -> None: ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier matching the profile name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this agent does."""

    @abstractmethod
    def _register_tools(self) -> List[Dict[str, Any]]:
        """Return ADK-compatible tool definitions for this agent."""

    @abstractmethod
    def _system_prompt(self) -> str:
        """Return the system prompt for this agent."""

    def _build_adk_agent(self) -> LlmAgent:
        """
        Construct the underlying Google ADK LlmAgent.
        Uses LiteLlm wrapper for non-Google models (Anthropic, OpenAI, etc.).
        Registers tools from _register_tools().
        Applies system prompt from _system_prompt().
        """

    async def invoke(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Send a message to this agent and wait for the full response.
        `context` can include session_id, notebook state, etc.
        """

    async def stream(self, message: str, context: Optional[Dict[str, Any]] = None) -> AsyncIterator[AgentMessage]:
        """
        Send a message and stream the response as partial AgentMessage chunks.
        Useful for CLI streaming output (Rich spinner -> stream -> Rich table).
        """

    async def validate_api_key(self) -> bool:
        """Check that the API key for this agent's model provider is valid."""
```

### `orchestrator.py`

```python
class OrchestratorAgent(MariboxAgent):
    """
    Top-level agent that receives user requests and delegates to the
    appropriate sub-agent. Maintains conversation context across delegations.

    Sub-agents:
    - NotebookAgent: code generation, cell manipulation
    - UiAgent: UI component generation
    - DebugAgent: error analysis, fix proposals
    - SessionAgent: session lifecycle management
    """

    def __init__(self, sub_agents: Dict[str, MariboxAgent], **kwargs) -> None: ...

    def _route_request(self, message: str) -> str:
        """
        Analyze the user message and determine which sub-agent to delegate to.
        Returns the sub-agent name.
        Uses lightweight classification (keyword matching + optional LLM fallback).
        """

    async def invoke(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Route the message to the appropriate sub-agent and return its response.
        If the request spans multiple agents, coordinate sequentially.
        """

    async def invoke_with_agent(
        self,
        agent_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Directly invoke a specific sub-agent by name."""

    def list_agents(self) -> List[str]:
        """Return the names of all available sub-agents."""
```

### `notebook_agent.py`

```python
class NotebookAgent(MariboxAgent):
    """
    Agent specialized in notebook operations: creating cells, modifying code,
    explaining code, suggesting optimizations, and managing cell dependencies.
    """

    def _register_tools(self) -> List[Dict[str, Any]]:
        """
        Register tools from cell_tools and notebook_tools:
        - create_cell, edit_cell, delete_cell
        - run_cell, run_notebook
        - explain_cell, suggest_improvement
        - add_import, remove_import
        """

    def _system_prompt(self) -> str:
        """
        Returns a prompt that instructs the agent to:
        - Write clean, well-documented Python code
        - Respect Marimo's reactive programming model
        - Consider cell dependencies when making changes
        - Use appropriate variable names that work with the DAG
        """
```

### `ui_agent.py`

```python
class UiAgent(MariboxAgent):
    """
    Agent specialized in generating Marimo UI components:
    forms, tables, charts, layouts, and interactive widgets.
    """

    def _register_tools(self) -> List[Dict[str, Any]]:
        """
        Register tools from ui_tools:
        - generate_ui_component
        - preview_ui
        - list_available_components
        - suggest_layout
        """
```

### `debug_agent.py`

```python
class DebugAgent(MariboxAgent):
    """
    Agent specialized in debugging notebook cells:
    analyzing errors, proposing fixes, explaining tracebacks,
    and suggesting patches.
    """

    def _register_tools(self) -> List[Dict[str, Any]]:
        """
        Register tools from debug_tools:
        - analyze_error
        - propose_fix
        - explain_traceback
        - check_dependencies
        - suggest_debugging_steps
        """
```

### `session_agent.py`

```python
class SessionAgent(MariboxAgent):
    """
    Agent specialized in session management:
    creating sessions, switching between them, managing resources,
    and answering questions about session state.
    """

    def _register_tools(self) -> List[Dict[str, Any]]:
        """
        Register tools from session_tools:
        - create_session, list_sessions, kill_session
        - get_session_status
        - estimate_resource_usage
        """
```

### `profile.py`

```python
def load_profiles(config_root: Optional[Path] = None) -> Dict[str, AgentProfile]:
    """
    Load agent profiles from agents/profiles.toml.
    Merge with user overrides from config root.
    Returns a dict of profile_name -> AgentProfile.
    """

def get_default_profile() -> str:
    """Return the name of the default agent profile."""

def resolve_model(provider: str, model: str) -> str:
    """
    Convert a provider+model pair to a LiteLLM-compatible model string.
    Examples:
        ("anthropic", "claude-sonnet-4-20250514") -> "anthropic/claude-sonnet-4-20250514"
        ("google", "gemini-2.0-flash") -> "gemini/gemini-2.0-flash"
        ("openai", "gpt-4o") -> "openai/gpt-4o"
    """
```

### Tool modules

```python
# cell_tools.py
def create_cell_tool(cell_dag: CellDAG) -> Dict[str, Any]:
    """Return an ADK tool definition for creating a new cell."""

def edit_cell_tool(cell_dag: CellDAG) -> Dict[str, Any]:
    """Return an ADK tool definition for editing cell code."""

def delete_cell_tool(cell_dag: CellDAG) -> Dict[str, Any]:
    """Return an ADK tool definition for deleting a cell."""

def run_cell_tool(runtime: MarimoRuntime) -> Dict[str, Any]:
    """Return an ADK tool definition for running a cell."""

# notebook_tools.py
def run_notebook_tool(runtime: MarimoRuntime) -> Dict[str, Any]:
    """Return an ADK tool definition for running the entire notebook."""

def explain_cell_tool() -> Dict[str, Any]:
    """Return an ADK tool definition for explaining a cell's code."""

# session_tools.py, debug_tools.py, ui_tools.py — follow the same pattern
```

## Dependencies

- **Phase 2 (Config)** must be complete: agent profiles are loaded from config; `AgentProfile` dataclass is used throughout.
- **Phase 3 (Auth)** must be complete: agents need API keys from `AuthManager` to authenticate with LLM providers.
- **Phase 4 (Sandbox)** must be complete: session tools interact with `SessionManager`; execution tools use `SandboxClient`.
- **Phase 5 (Notebook)** must be complete: cell tools and notebook tools operate on `CellDAG` and `MarimoRuntime`.
- Runtime packages: `google-adk` (Google Agent Development Kit), `litellm` (multi-provider LLM wrapper), `tomli` (profile parsing).

## Testing Strategy

- **Unit tests for profile loading**: Parse a test `profiles.toml`, verify all fields are correctly loaded. Test merge with user overrides. Test missing fields fall back to defaults.
- **Unit tests for tool registration**: Each tool function returns a valid ADK tool definition schema. Verify parameter descriptions, required fields, and return types.
- **Unit tests for OrchestratorAgent routing**: Provide messages like "fix the error in cell 3" and verify routing to `DebugAgent`. Test multi-keyword overlap ("create a UI component that shows the data") routes to `UiAgent`.
- **Integration tests with mocked LLM**: Mock the `LlmAgent.invoke()` method to return canned responses. Test full agent invocation cycle: message -> routing -> tool call -> response.
- **Integration tests with real LLM** (optional, `@pytest.mark.llm`): Use a real API key to test end-to-end agent behavior. Verify the agent can create a cell and explain code.
- **Unit tests for LiteLLM model resolution**: Verify `resolve_model()` produces correct strings for Anthropic, Google, and OpenAI providers.
- **Edge cases**: Empty message, very long message (>10k chars), message with no clear routing signal, simultaneous multi-agent coordination.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google ADK API is new and may change | Breaking changes require refactoring | Isolate ADK interactions behind `MariboxAgent._build_adk_agent()`; pin the ADK version; write adapter tests |
| LiteLLM provider format mismatches | API calls fail for certain models | Maintain a tested model registry with known-good format strings; validate model strings at profile load time |
| Agent routing misroutes requests | Wrong agent handles the request, poor UX | Log routing decisions; allow users to explicitly specify the agent via CLI flag (e.g., `--agent debug`) |
| Tool execution takes too long | Agent response is delayed, poor UX | Set timeouts on tool execution; stream intermediate results; show progress in CLI |
| API key not available for requested model | Agent fails at invocation time | Check API key availability at agent construction time; fail fast with a clear error message |
| Concurrent agent invocations on same session | Race conditions in cell DAG | Serialize agent invocations per session using an async lock; queue pending requests |
| Agent generates invalid Python code | Code execution fails in sandbox | Validate generated code with `ast.parse()` before execution; return clear syntax errors to the agent for retry |

## Acceptance Criteria

- [ ] `MariboxAgent` ABC is implemented with `invoke()` and `stream()` methods
- [ ] `OrchestratorAgent` correctly routes messages to sub-agents based on content analysis
- [ ] `NotebookAgent` can create, edit, and delete cells via registered tools
- [ ] `UiAgent` can generate Marimo UI component code
- [ ] `DebugAgent` can analyze errors and propose fixes
- [ ] `SessionAgent` can create, list, and kill sessions via tools
- [ ] Agent profiles load correctly from `profiles.toml` with user overrides
- [ ] `resolve_model()` produces correct LiteLLM format strings for all supported providers
- [ ] `_build_adk_agent()` constructs a valid `LlmAgent` with tools and system prompt
- [ ] API key validation happens at construction time, not invocation time
- [ ] Streaming responses produce incremental `AgentMessage` chunks
- [ ] Unit test coverage >= 80% for `agents/base.py` and `agents/profile.py`
- [ ] All tool definitions conform to the ADK tool schema
