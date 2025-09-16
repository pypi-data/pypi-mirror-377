"""Scenario generation commands."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.live import Live
from rich.text import Text

from veris_cli.api import ApiClient
from veris_cli.loaders import load_agent_spec

scenario_app = typer.Typer(add_completion=False, no_args_is_help=False)


def _save_scenarios(scenarios: list[dict], dest_dir: Path) -> int:
    dest_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in scenarios:
        scenario_id = item.get("scenario_id")
        if not scenario_id:
            # Skip malformed entries
            continue
        out_path = dest_dir / f"{scenario_id}.json"
        out_path.write_text(json.dumps(item, indent=2, ensure_ascii=False), encoding="utf-8")
        count += 1
    return count


def _normalize_status(value: str | None) -> str:
    if not value:
        return "unknown"
    return value.lower()


@scenario_app.command("generate")
def generate(
    agent: Annotated[
        Path | None,
        typer.Option("--agent", help="Path to agent spec JSON (defaults to .veris/agent.json)"),
    ] = None,
    config_path: Annotated[
        Path | None,
        typer.Option("--config", help="Path to generator config JSON"),
    ] = None,
    variations_per_skeleton: Annotated[
        int | None, typer.Option("--variations-per-skeleton", help="Scenarios per skeleton")
    ] = None,
    random_subset: Annotated[
        int | None, typer.Option("--random-subset", help="Randomly sample this many skeletons")
    ] = None,
    model: Annotated[str | None, typer.Option("--model", help="LLM model name")] = None,
    temperature: Annotated[
        float | None, typer.Option("--temperature", help="Sampling temperature")
    ] = None,
    max_parallel_calls: Annotated[
        int | None, typer.Option("--max-parallel-calls", help="Parallelism for LLM calls")
    ] = None,
    max_retries: Annotated[
        int | None, typer.Option("--max-retries", help="Retry attempts for LLM calls")
    ] = None,
    watch: Annotated[
        bool, typer.Option("--watch", help="Watch until generation completes")
    ] = False,
    save: Annotated[
        bool, typer.Option("--save", help="Save scenarios to .veris/scenarios when done")
    ] = False,
):
    """Start scenario generation from an agent spec."""
    project_dir = Path.cwd()
    veris_dir = project_dir / ".veris"
    scenarios_dir = veris_dir / "scenarios"

    # Resolve agent spec path
    if agent is None:
        default_agent = veris_dir / "agent.json"
        if default_agent.exists():
            agent = default_agent
    if agent is None or not agent.exists():
        rprint("[red]Agent spec not found. Provide --agent or create .veris/agent.json[/red]")
        raise typer.Exit(code=1)

    spec = load_agent_spec(agent)
    payload: dict = {"agent_spec": spec.model_dump(mode="json")}

    # Merge config from file + CLI overrides
    config: dict = {}
    if config_path and config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
    if variations_per_skeleton is not None:
        config["variations_per_skeleton"] = variations_per_skeleton
    if random_subset is not None:
        config["random_subset"] = random_subset
    if model is not None:
        config["model"] = model
    if temperature is not None:
        config["temperature"] = temperature
    if max_parallel_calls is not None:
        config["max_parallel_calls"] = max_parallel_calls
    if max_retries is not None:
        config["max_retries"] = max_retries
    if config:
        payload["config"] = config

    api = ApiClient()
    result = api.start_scenario_generation(payload)
    generation_id = result.get("generation_id")
    if not generation_id:
        rprint("[red]Server did not return generation_id[/red]")
        raise typer.Exit(code=1)

    status_text = result.get("status")
    rprint(f"[bold]Generation started[/bold] id=[cyan]{generation_id}[/cyan] status={status_text}")

    if not watch:
        rprint(
            "Check status with: veris scenario status --gen "
            f"{generation_id} and fetch with: veris scenario get --gen {generation_id}"
        )
        return

    try:
        with Live("", refresh_per_second=4, transient=False) as live:
            while True:
                time.sleep(2.0)
                status = api.get_generation_status(generation_id)
                st = _normalize_status(status.get("status"))

                header = "[cyan]Watching generation. Press Ctrl+C to stop.[/cyan]"

                base_lines = [
                    f"Generation: [cyan]{generation_id}[/cyan]",
                    f"Status: [bold]{st}[/bold]",
                ]
                progress = status.get("progress") or {}
                if progress:
                    completed = progress.get("completed")
                    total = progress.get("total")
                    pct = progress.get("percentage")
                    base_lines.append(f"Progress: {completed}/{total} ({pct}%)")
                err = status.get("error")
                if err:
                    base_lines.append(f"Error: [red]{err}[/red]")

                live.update(Text.from_markup(header + "\n" + "\n".join(base_lines)))

                if st in {"completed", "failed"}:
                    break

        if st == "completed" and save:
            resp = api.get_generated_scenarios(generation_id, include_failed=False)
            items = resp.get("scenarios", [])
            saved = _save_scenarios(items, scenarios_dir)
            rprint(f"[green]Saved {saved} scenarios to {scenarios_dir}[/green]")
    except KeyboardInterrupt:
        rprint(
            "[yellow]Stopped watching. Check later with: "
            f"veris scenario status --gen {generation_id}[/yellow]"
        )


@scenario_app.command("status")
def status(generation_id: Annotated[str, typer.Option("--gen", help="Generation ID")]):
    """Get status for a scenario generation job."""
    api = ApiClient()
    status = api.get_generation_status(generation_id)
    rprint(status)


@scenario_app.command("get")
def get(
    generation_id: Annotated[str, typer.Option("--gen", help="Generation ID")],
    include_failed: Annotated[
        bool, typer.Option("--include-failed", help="Include failed parses")
    ] = False,
    save: Annotated[bool, typer.Option("--save", help="Save scenarios to .veris/scenarios")] = True,
    out_dir: Annotated[
        Path | None,
        typer.Option("--out-dir", help="Directory to save scenarios to"),
    ] = None,
):
    """Fetch generated scenarios for a generation ID."""
    api = ApiClient()
    resp = api.get_generated_scenarios(generation_id, include_failed=include_failed)
    scenarios = resp.get("scenarios", [])
    rprint(f"[bold]{len(scenarios)}[/bold] scenarios for generation [cyan]{generation_id}[/cyan]")

    if save:
        project_dir = Path.cwd()
        dest = out_dir or (project_dir / ".veris" / "scenarios")
        saved = _save_scenarios(scenarios, dest)
        rprint(f"[green]Saved {saved} scenarios to {dest}[/green]")
    else:
        # Print JSON payload when not saving
        rprint(json.dumps(resp, indent=2, ensure_ascii=False))
