"""Initialize a Veris project."""

from __future__ import annotations

from pathlib import Path

import typer
from rich import print as rprint

from veris_cli.config import save_config
from veris_cli.fs import ensure_veris_dir, write_text_if_missing
from veris_cli.models.config import VerisConfig

init_app = typer.Typer(add_completion=False, no_args_is_help=False)


AGENT_JSON_DEFAULT = """
{
  "agent_id": "local-agent",
  "name": "local-agent",
  "description": "Barebones local agent specification",
  "version": "0.1.0",
  "entity_types": [],
  "use_cases": [],
  "tool_use": { "tools": [], "general_guidelines": [] },
  "agent_specific_metrics": [],
  "policies": [],
  "preferences": []
}
"""

SCENARIO_MINIMAL_JSON = """
{
  "title": "Example Scenario",
  "description": "Barebones scenario skeleton",
  "initial_human_prompt": "Hello",
  "agent_name": "local-agent",
  "personas": [],
  "setting": { "time_context": "", "location": "", "environment_description": "" },
  "expected_tools": [],
  "objectives": [],
  "constraints": [],
  "skeleton_metadata": { "use_case_name": "Example", "tool_name": null, "urgency": "routine", "complexity": "easy" },
  "max_turns": 15,
  "scenario_id": "example-01"
}
"""  # noqa: E501


@init_app.callback(invoke_without_command=True)
def init(
    force: bool = typer.Option(False, "--force", help="Overwrite existing files if present"),
):
    """Create .veris directory with agent.json, scenarios/, runs/."""
    project_dir = Path.cwd()
    veris_dir = ensure_veris_dir(project_dir)

    agent_path = veris_dir / "agent.json"
    scenarios_dir = veris_dir / "scenarios"
    runs_dir = veris_dir / "runs"

    scenarios_dir.mkdir(exist_ok=True)
    runs_dir.mkdir(exist_ok=True)

    scenario_example = scenarios_dir / "example-scenario.json"

    write_text_if_missing(agent_path, AGENT_JSON_DEFAULT.strip() + "\n", force=force)
    write_text_if_missing(scenario_example, SCENARIO_MINIMAL_JSON.strip() + "\n", force=force)

    # Create config.json from the VerisConfig model (no hard-coded JSON template)
    config = VerisConfig(api_key=None, agent=None)
    config_path = save_config(project_dir, config, overwrite=force)

    rprint("[green]Initialized .veris/ with agent.json, scenarios/, runs/[/green]")

    # If config fields look empty, guide the user to set them.
    try:
        parsed = VerisConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
        if not parsed.api_key or not parsed.agent:
            rprint(
                "[yellow]Next step:[/yellow] Update [bold].veris/config.json[/bold] with your credentials."
            )
            rprint(
                "Set [bold]api_key[/bold] and the agent's public URL (under the 'agent' section). "
                'If you don\'t have them yet, temporarily set them to "TEMP CONFIG BY <your name>".'
            )
            rprint(
                "Tip: run [bold]veris setup[/bold] to get a public URL, then use `veris config public_url <URL>`."
            )
    except Exception:
        # Non-fatal; initialization succeeded
        pass

    rprint("[green]Initialized .veris/ with agent.json, scenarios/, runs/[/green]")
