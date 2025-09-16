"""Config commands for setting CLI configuration values."""

from __future__ import annotations

import typer
from rich import print as rprint

from veris_cli.config import derive_url_stub, load_config, save_config
from veris_cli.models.config import AgentConnection

config_app = typer.Typer(add_completion=False, no_args_is_help=True)


@config_app.command("public_url")
def set_public_url(value: str = typer.Argument(..., help="Public URL for your agent (ngrok)")):
    """Set the public agent URL and derive an AgentConnection entry."""
    from pathlib import Path

    project_dir = Path.cwd()
    cfg = load_config(project_dir)

    stub = derive_url_stub(value)
    cfg.agent = AgentConnection(
        agent_id=stub,
        name=stub,
        mcp_url=value,
        mcp_transport="http",
        timeout_seconds=300,
    )

    save_config(project_dir, cfg, overwrite=True)
    rprint("[green]agent public URL updated in .veris/config.json[/green]")
