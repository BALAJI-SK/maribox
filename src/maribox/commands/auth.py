"""Auth CLI commands — API key management."""

from __future__ import annotations

import getpass

import typer
from rich import print as rprint
from rich.table import Table

from maribox.auth.manager import AuthManager


def _get_manager() -> AuthManager:
    return AuthManager()


def auth_set(
    provider: str = typer.Argument(help="Provider: anthropic | google | openai | glm | custom."),
) -> None:
    """Store an API key for a provider (hidden prompt)."""
    manager = _get_manager()
    api_key = getpass.getpass(f"Enter API key for {provider}: ")
    if not api_key.strip():
        rprint("[red]No key entered. Aborting.[/red]")
        raise typer.Exit(1)
    manager.set_key(provider, api_key)
    rprint(f"[green]API key stored for {provider}[/green]")


def auth_list() -> None:
    """Show masked keys and status per provider."""
    manager = _get_manager()
    providers = manager.list_keys()

    table = Table(title="API Keys")
    table.add_column("Provider", style="bold")
    table.add_column("Status", style="bold")
    table.add_column("Masked Key")

    for info in providers:
        status = "[green]configured[/green]" if info.has_key else "[dim]not set[/dim]"
        table.add_row(info.provider, status, info.masked_key if info.has_key else "—")

    from rich.console import Console
    Console().print(table)


def auth_use(
    provider: str = typer.Argument(help="Provider to activate."),
    model: str | None = typer.Option(None, "--model", help="Default model for this provider."),
    project: bool = typer.Option(False, "--project", help="Set for current project only."),
) -> None:
    """Set the active provider globally or for the current project."""
    manager = _get_manager()
    manager.set_active_provider(provider, model=model, project=project)
    scope = "project" if project else "global"
    rprint(f"[green]Active provider set to {provider}[/green] ({scope})")


def auth_rotate(
    provider: str = typer.Argument(help="Provider whose key to rotate."),
) -> None:
    """Replace the API key for a provider."""
    manager = _get_manager()
    new_key = getpass.getpass(f"Enter new API key for {provider}: ")
    if not new_key.strip():
        rprint("[red]No key entered. Aborting.[/red]")
        raise typer.Exit(1)
    manager.rotate_key(provider, new_key)
    rprint(f"[green]API key rotated for {provider}[/green]")


def auth_revoke(
    provider: str = typer.Argument(help="Provider whose key to revoke."),
) -> None:
    """Wipe the API key for a provider."""
    if not typer.confirm(f"Remove API key for {provider}?"):
        rprint("[dim]Aborted.[/dim]")
        raise typer.Exit(0)
    manager = _get_manager()
    manager.revoke_key(provider)
    rprint(f"[green]API key revoked for {provider}[/green]")


def glm_setup(
    api_key: str | None = typer.Option(None, "--api-key", help="GLM API key (prompted if omitted)."),
    set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Set GLM as default provider."),
) -> None:
    """Configure GLM 5.1 (z.ai / Zhipu AI) as the AI provider.

    Sets up the zhipuai SDK, stores the API key, and optionally sets
    GLM 5.1 as the default provider and model for maribox.
    """
    manager = _get_manager()

    # Get API key
    if api_key is None:
        api_key = getpass.getpass("Enter your GLM API key (from open.bigmodel.cn): ")
    if not api_key.strip():
        rprint("[red]No key entered. Aborting.[/red]")
        raise typer.Exit(1)

    # Store key
    manager.set_key("glm", api_key)
    rprint("[green]GLM API key stored.[/green]")

    # Set as default provider
    if set_default:
        manager.set_active_provider("glm", model="glm-5.1")
        rprint("[green]Default provider set to GLM 5.1 (z.ai)[/green]")

    # Verify SDK is importable
    try:
        import zhipuai
        rprint(f"[green]zhipuai SDK ready (version {zhipuai.__version__}).[/green]")
    except ImportError:
        rprint("[yellow]Warning: zhipuai SDK not installed. Run: uv add zhipuai[/yellow]")

    rprint("\n[bold]GLM 5.1 configuration complete![/bold]")
    rprint("  Provider: [cyan]glm[/cyan]")
    rprint("  Model: [cyan]glm-5.1[/cyan]")
    rprint("  SDK: [cyan]zhipuai[/cyan]")
    rprint("\nUse [bold]maribox auth list[/bold] to verify, or [bold]maribox session new[/bold] to start.")
