"""Config CLI commands."""

from __future__ import annotations

from pathlib import Path

from rich import print as rprint
from rich.pretty import pprint

from maribox.config.io import (
    init_config_dir,
    resolve_merged_config,
    set_config_value,
)
from maribox.config.resolution import resolve_config_root


def config_init(global_scope: bool = False, project_scope: bool = False) -> None:
    """Scaffold a .maribox/ directory with defaults."""
    if global_scope:
        import platformdirs
        root = Path(platformdirs.user_config_dir("maribox"))
        config_root = init_config_dir(root, scope="global")
    else:
        # Project scope: create .maribox/ in current directory
        config_root = init_config_dir(Path.cwd(), scope="project")

    rprint(f"[green]Initialized maribox config at[/green] {config_root}")


def config_show() -> None:
    """Print resolved config (merged global + project, secrets redacted)."""
    config, project = resolve_merged_config()
    rprint("[bold]Resolved maribox configuration:[/bold]\n")
    pprint(config.to_toml())
    if project is not None:
        rprint("\n[bold]Project overrides:[/bold]\n")
        pprint(project.to_toml())


def config_set(key: str, value: str, global_scope: bool = False, project_scope: bool = False) -> None:
    """Update a single config key."""
    root = resolve_config_root()
    set_config_value(key, value, root=root, project=project_scope)
    rprint(f"[green]Set[/green] {key} = {value}")


def config_path() -> None:
    """Print the resolved config root."""
    root = resolve_config_root()
    rprint(str(root))
