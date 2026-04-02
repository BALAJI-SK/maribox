"""Tests for the orchestrator agent's routing logic."""

from maribox.agents.orchestrator import _ROUTING_RULES


class TestRouting:
    def test_routes_to_notebook(self) -> None:
        # Create a minimal orchestrator-like object for testing routing
        class _FakeOrchestrator:
            def _route_request(self, message: str) -> str:
                lower = message.lower()
                scores: dict[str, int] = {}
                for agent_name, keywords in _ROUTING_RULES.items():
                    score = sum(1 for kw in keywords if kw in lower)
                    if score > 0:
                        scores[agent_name] = score
                if scores:
                    return max(scores, key=lambda k: scores[k])
                return "notebook"

        orch = _FakeOrchestrator()

        assert orch._route_request("create a new cell with x = 1") == "notebook"
        assert orch._route_request("write a function to sort a list") == "notebook"

    def test_routes_to_ui(self) -> None:
        class _FakeOrchestrator:
            def _route_request(self, message: str) -> str:
                lower = message.lower()
                scores: dict[str, int] = {}
                for agent_name, keywords in _ROUTING_RULES.items():
                    score = sum(1 for kw in keywords if kw in lower)
                    if score > 0:
                        scores[agent_name] = score
                if scores:
                    return max(scores, key=lambda k: scores[k])
                return "notebook"

        orch = _FakeOrchestrator()
        assert orch._route_request("add a table widget to display data") == "ui"
        assert orch._route_request("create a form with a slider") == "ui"

    def test_routes_to_debug(self) -> None:
        class _FakeOrchestrator:
            def _route_request(self, message: str) -> str:
                lower = message.lower()
                scores: dict[str, int] = {}
                for agent_name, keywords in _ROUTING_RULES.items():
                    score = sum(1 for kw in keywords if kw in lower)
                    if score > 0:
                        scores[agent_name] = score
                if scores:
                    return max(scores, key=lambda k: scores[k])
                return "notebook"

        orch = _FakeOrchestrator()
        assert orch._route_request("fix the error in cell 3") == "debug"
        assert orch._route_request("debug this traceback") == "debug"

    def test_routes_to_session(self) -> None:
        class _FakeOrchestrator:
            def _route_request(self, message: str) -> str:
                lower = message.lower()
                scores: dict[str, int] = {}
                for agent_name, keywords in _ROUTING_RULES.items():
                    score = sum(1 for kw in keywords if kw in lower)
                    if score > 0:
                        scores[agent_name] = score
                if scores:
                    return max(scores, key=lambda k: scores[k])
                return "notebook"

        orch = _FakeOrchestrator()
        assert orch._route_request("create a new session") == "session"
        assert orch._route_request("stop session abc123") == "session"

    def test_default_routes_to_notebook(self) -> None:
        class _FakeOrchestrator:
            def _route_request(self, message: str) -> str:
                lower = message.lower()
                scores: dict[str, int] = {}
                for agent_name, keywords in _ROUTING_RULES.items():
                    score = sum(1 for kw in keywords if kw in lower)
                    if score > 0:
                        scores[agent_name] = score
                if scores:
                    return max(scores, key=lambda k: scores[k])
                return "notebook"

        orch = _FakeOrchestrator()
        assert orch._route_request("hello world") == "notebook"
        assert orch._route_request("what is 2+2") == "notebook"
