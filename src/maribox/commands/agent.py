"""Agent CLI commands — list and run agents."""

from __future__ import annotations

import asyncio

from rich import print as rprint
from rich.table import Table

from maribox.agents.profile import load_profiles


def agent_list() -> None:
    """List all available agent profiles."""
    profiles = load_profiles()
    table = Table(title="Agent Profiles")
    table.add_column("Role", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Model")
    for name, profile in sorted(profiles.items()):
        table.add_row(name, profile.provider, profile.model)
    rprint(table)


def agent_run(role: str, prompt: str, session: str | None = None) -> None:
    """Run an agent with the given prompt."""
    profiles = load_profiles()
    profile = profiles.get(role)
    if profile is None:
        available = ", ".join(sorted(profiles.keys()))
        rprint(f"[red]Unknown agent role: {role}[/red]")
        rprint(f"[dim]Available: {available}[/dim]")
        raise SystemExit(1)

    rprint(f"[cyan]Running {role} agent ({profile.provider}/{profile.model})...[/cyan]")
    rprint(f"[dim]Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}[/dim]")

    # Full agent invocation requires an active session and LLM connection.
    # This will be wired up in Phase 7 (remaining CLI commands).
    rprint("[yellow]Agent execution requires an active session. Connect with `maribox session attach` first.[/yellow]")


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)
