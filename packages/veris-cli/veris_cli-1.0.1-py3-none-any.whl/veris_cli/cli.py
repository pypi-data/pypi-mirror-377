"""CLI for the Veris CLI."""

import typer
from dotenv import load_dotenv

from veris_cli.commands.config import config_app
from veris_cli.commands.init import init_app
from veris_cli.commands.scenario import scenario_app
from veris_cli.commands.setup import setup_app
from veris_cli.commands.sim import sim_app

load_dotenv()


app = typer.Typer(help="Veris CLI")
app.add_typer(init_app, name="init", help="Initialize .veris project files")
app.add_typer(setup_app, name="setup", help="Run local FastAPI and expose via ngrok")
app.add_typer(sim_app, name="sim", help="Run simulations (launch/status/kill)")
app.add_typer(scenario_app, name="scenario", help="Scenario generation (generate/status/get)")
app.add_typer(config_app, name="config", help="Get/set CLI configuration values")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
