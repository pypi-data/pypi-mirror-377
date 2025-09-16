"""Setup commands."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import httpx
import typer
from rich import print as rprint

from veris_cli.config import derive_url_stub, load_config, save_config
from veris_cli.models.config import AgentConnection

setup_app = typer.Typer(add_completion=False, no_args_is_help=False)


# -------------------------
# Paths and state utilities
# -------------------------
def _veris_dir(project_dir: Path) -> Path:
    d = project_dir / ".veris"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _state_file_path(project_dir: Path) -> Path:
    return _veris_dir(project_dir) / "setup_state.json"


def _logs_dir(project_dir: Path) -> Path:
    d = _veris_dir(project_dir) / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _is_port_available(host: str, port: int) -> bool:
    """Return True if the TCP port is available to bind on the given host."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def _load_state(project_dir: Path) -> dict | None:
    fp = _state_file_path(project_dir)
    if not fp.exists():
        return None
    try:
        return json.loads(fp.read_text())
    except Exception:
        return None


def _save_state(project_dir: Path, state: dict) -> None:
    fp = _state_file_path(project_dir)
    fp.write_text(json.dumps(state, indent=2))


def _delete_state(project_dir: Path) -> None:
    try:
        _state_file_path(project_dir).unlink(missing_ok=True)
    except Exception:
        pass


def _is_process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we don't have permissions; consider it running
        return True
    except Exception:
        return False
    return True


def _ensure_command_available(command: str) -> None:
    """Ensure a command is available."""
    try:
        subprocess.run(
            [command, "--help"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except Exception as err:
        rprint(f"[red]Required command not found: {command}[/red]")
        if command == "ngrok":
            rprint(
                "Install ngrok from https://ngrok.com/download and run 'ngrok config add-authtoken <token>'"  # noqa: E501
            )
        elif command == "uvicorn":
            rprint(
                "Install uvicorn in your FastAPI environment, e.g. 'pip install uvicorn' or 'uv pip install uvicorn'"  # noqa: E501
            )
        raise typer.Exit(1) from err


def _start_uvicorn_process(
    app_import_path: str,
    host: str,
    port: int,
    reload: bool,
    workers: int | None,
    *,
    detached: bool = False,
    stdout: int | None | object = None,
    stderr: int | None | object = None,
) -> subprocess.Popen:
    """Start a uvicorn process.

    When detached=True, start the process in a new session to allow group termination.
    """
    uvicorn_cmd = "uvicorn"
    try:
        subprocess.run(
            [uvicorn_cmd, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        cmd = [uvicorn_cmd, app_import_path, "--host", host, "--port", str(port)]
    except Exception:
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            app_import_path,
            "--host",
            host,
            "--port",
            str(port),
        ]
    if reload:
        cmd.append("--reload")
    if workers and workers > 0:
        cmd.extend(["--workers", str(workers)])

    popen_kwargs: dict = {
        "stdout": stdout,
        "stderr": stderr,
        "cwd": os.getcwd(),
        # text flag not needed unless we capture and parse; logs are binary-safe
    }
    if detached and hasattr(os, "setsid"):
        popen_kwargs["preexec_fn"] = os.setsid  # type: ignore[assignment]
    process = subprocess.Popen(cmd, **popen_kwargs)
    return process


def _wait_for_http(url: str, timeout_seconds: float = 30.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            # A HEAD is sufficient to confirm the server is responding
            with httpx.Client(timeout=2.0) as client:
                response = client.get(url)
                if response.status_code < 500:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def _start_ngrok_tunnel(
    port: int,
    *,
    detached: bool = False,
    stdout: int | None | object = None,
) -> subprocess.Popen:
    """Start a ngrok tunnel."""
    ngrok_cmd = ["ngrok", "http", str(port), "--log=stdout"]
    popen_kwargs: dict = {
        "stdout": stdout if stdout is not None else subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
    }
    if detached and hasattr(os, "setsid"):
        popen_kwargs["preexec_fn"] = os.setsid  # type: ignore[assignment]
    process = subprocess.Popen(ngrok_cmd, **popen_kwargs)
    return process


def _get_ngrok_public_url(timeout_seconds: float = 30.0) -> str | None:
    deadline = time.time() + timeout_seconds
    api_url = "http://localhost:4040/api/tunnels"
    while time.time() < deadline:
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    tunnels = data.get("tunnels", [])
                    if tunnels:
                        # Prefer https tunnel if present
                        https_tunnels = [
                            t for t in tunnels if t.get("public_url", "").startswith("https:")
                        ]
                        chosen = https_tunnels[0] if https_tunnels else tunnels[0]
                        return chosen.get("public_url")
        except Exception:
            pass
        time.sleep(0.5)
    return None


def _terminate_process(process: subprocess.Popen | None) -> None:
    if process is None:
        return
    if process.poll() is not None:
        return
    try:
        process.terminate()
        process.wait(timeout=5)
    except Exception:
        try:
            process.kill()
        except Exception:
            pass


@setup_app.callback(invoke_without_command=True)
def setup(
    ctx: typer.Context,
    app: str | None = typer.Option(None, "--app", help="ASGI app import path, e.g. 'app.main:app'"),
    port: int = typer.Option(8000, "--port", help="Local port to run the FastAPI app on"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host interface for the FastAPI app"),
    reload: bool = typer.Option(False, "--reload", help="Enable autoreload for local development"),
    workers: int | None = typer.Option(None, "--workers", help="Number of worker processes"),
    detached: bool = typer.Option(
        False,
        "-d",
        "--detached",
        help="Run in background and persist PIDs to .veris/setup_state.json",
    ),
    no_override_public_url: bool = typer.Option(
        False,
        "--no_override_public_url",
        help="Do not update .veris/config.json with the discovered public URL",
    ),
):
    """Run a local FastAPI app with uvicorn and expose it via an ngrok tunnel.

    Example:
      veris setup --app app.main:app --port 8000
    """
    # If a subcommand is invoked (e.g. 'veris setup stop'), skip main run logic
    if ctx.invoked_subcommand is not None:
        return

    if not app:
        rprint("[red]Missing option '--app'. Example: --app app.main:app[/red]")
        raise typer.Exit(1)

    # Pre-flight: ensure desired port is available before starting uvicorn
    if not _is_port_available(host, port):
        rprint(
            "[red]❌ Port "
            f"{host}:{port} "
            "is already in use. Choose a different port or stop the process using it.[/red]"
        )
        raise typer.Exit(1)

    # Ensure external commands exist in the environment
    _ensure_command_available("ngrok")
    _ensure_command_available("uvicorn")

    project_dir = Path.cwd()

    # If detached is requested, ensure no existing active detached run
    if detached:
        existing = _load_state(project_dir)
        if existing:
            uv_pid = existing.get("uvicorn_pid")
            ng_pid = existing.get("ngrok_pid")
            uv_running = isinstance(uv_pid, int) and _is_process_running(uv_pid)
            ng_running = isinstance(ng_pid, int) and _is_process_running(ng_pid)
            if uv_running or ng_running:
                rprint(
                    "[red]A detached setup is already running. Run 'veris setup stop' "
                    "before starting another.[/red]"
                )
                raise typer.Exit(1)
            else:
                _delete_state(project_dir)

    rprint("[cyan]🚀 Starting FastAPI app with uvicorn...[/cyan]")
    # Configure logging for detached mode
    uvicorn_stdout = None
    uvicorn_stderr = None
    ngrok_stdout = None

    logs_dir = _logs_dir(project_dir)
    ngrok_log_path = logs_dir / "ngrok.log"
    ngrok_stdout = open(ngrok_log_path, "a")  # noqa: PTH123

    if detached:
        uvicorn_log_path = logs_dir / "uvicorn.log"
        # Open in append mode to preserve history
        uvicorn_stdout = open(uvicorn_log_path, "a")  # noqa: PTH123
        uvicorn_stderr = uvicorn_stdout

    try:
        uvicorn_proc = _start_uvicorn_process(
            app,
            host,
            port,
            reload,
            workers,
            detached=detached,
            stdout=uvicorn_stdout,
            stderr=uvicorn_stderr,
        )
    except Exception as err:
        # If uvicorn fails to start, ensure we exit cleanly
        if uvicorn_stdout:
            try:
                uvicorn_stdout.flush()
                uvicorn_stdout.close()
            except Exception:
                pass
        rprint(
            "[red]❌ Failed to start FastAPI server (uvicorn). "
            "Check the logs above for details.[/red]"
        )
        raise typer.Exit(1) from err

    # Wait for the FastAPI server to respond
    started = _wait_for_http(f"http://{host}:{port}")
    if not started:
        _terminate_process(uvicorn_proc)
        if detached and uvicorn_stdout:
            try:
                uvicorn_stdout.flush()
                uvicorn_stdout.close()
            except Exception:
                pass
        rprint("[red]❌ FastAPI app failed to start or is not responding[/red]")
        raise typer.Exit(1)

    rprint("[cyan]🌐 Starting ngrok tunnel...[/cyan]")
    rprint(f"[cyan]Ngrok logs: {logs_dir}/ngrok.log[/cyan]")
    try:
        ngrok_proc = _start_ngrok_tunnel(port, detached=detached, stdout=ngrok_stdout)
    except Exception as err:  # noqa: F841
        _terminate_process(uvicorn_proc)
        if detached and uvicorn_stdout:
            try:
                uvicorn_stdout.flush()
                uvicorn_stdout.close()
            except Exception:
                pass
        rprint(
            "[red]❌ Failed to start ngrok tunnel. Verify ngrok is installed "
            "and authenticated.[/red]"
        )
        rprint(f"[yellow]See ngrok logs for details: {ngrok_log_path}[/yellow]")
        raise

    # Wait for ngrok to initialize and provide a public URL
    public_url = _get_ngrok_public_url()
    if not public_url:
        _terminate_process(ngrok_proc)
        _terminate_process(uvicorn_proc)
        if detached and ngrok_stdout:
            try:
                ngrok_stdout.flush()
                ngrok_stdout.close()
            except Exception:
                pass
        if detached and uvicorn_stdout:
            try:
                uvicorn_stdout.flush()
                uvicorn_stdout.close()
            except Exception:
                pass
        rprint(
            "[red]❌ Failed to obtain ngrok public URL. Is ngrok installed and authenticated?[/red]"
        )
        rprint(f"[yellow]See ngrok logs for details: {ngrok_log_path}[/yellow]")
        raise typer.Exit(1)

    rprint("")
    rprint("[green]✅ FastAPI app is running![/green]")
    rprint(f"[bold]🌍 Public URL:[/bold] {public_url}")
    rprint(f"[bold]📚 API Docs:[/bold] {public_url}/docs")
    rprint("")
    # Persist discovered public URL into config unless explicitly disabled
    try:
        if no_override_public_url:
            rprint("[yellow]Skipping config update due to --no_override_public_url flag[/yellow]")
        else:
            cfg = load_config(project_dir)
            stub = derive_url_stub(public_url)
            cfg.agent = AgentConnection(
                agent_id=stub,
                name=stub,
                mcp_url=public_url + "/mcp",
                mcp_transport="http",
                timeout_seconds=300,
            )
            save_config(project_dir, cfg, overwrite=True)
            rprint("[green]Updated .veris/config.json with agent public URL[/green]")
    except Exception:
        # Best-effort; don't fail setup if config write fails
        rprint("[yellow]Warning: failed to update .veris/config.json[/yellow]")

    # In detached mode, write state and exit immediately
    if detached:
        state = {
            "uvicorn_pid": uvicorn_proc.pid,
            "ngrok_pid": ngrok_proc.pid,
            "public_url": public_url,
            "app": app,
            "host": host,
            "port": port,
            "reload": reload,
            "workers": workers,
            "logs": {
                "uvicorn": str((_logs_dir(project_dir) / "uvicorn.log").resolve()),
                "ngrok": str((_logs_dir(project_dir) / "ngrok.log").resolve()),
            },
            "started_at": time.time(),
        }
        _save_state(project_dir, state)
        # Close log handles in parent process, children keep FD open
        if uvicorn_stdout:
            try:
                uvicorn_stdout.flush()
                uvicorn_stdout.close()
            except Exception:
                pass
        if ngrok_stdout:
            try:
                ngrok_stdout.flush()
                ngrok_stdout.close()
            except Exception:
                pass
        rprint("[green]🟢 Running in detached mode (-d). Use 'veris setup stop' to stop.[/green]")
        logs_dir = _logs_dir(project_dir)
        rprint(f"[dim]Logs: {logs_dir}/uvicorn.log, {logs_dir}/ngrok.log[/dim]")
        raise typer.Exit(0)

    rprint("Press Ctrl+C to stop all services")

    def _stop_services_and_exit(exit_code: int) -> None:
        rprint("")
        rprint("[yellow]🛑 Stopping services...[/yellow]")
        _terminate_process(ngrok_proc)
        _terminate_process(uvicorn_proc)
        # Attempt to flush and close log handles
        try:
            if uvicorn_stdout:
                uvicorn_stdout.flush()
                uvicorn_stdout.close()
        except Exception:
            pass
        try:
            if ngrok_stdout:
                ngrok_stdout.flush()
                ngrok_stdout.close()
        except Exception:
            pass
        rprint("[green]✅ Cleanup complete[/green]")
        raise typer.Exit(exit_code)

    def handle_sigterm(signum, frame):  # noqa: ARG001
        # Graceful shutdown on signals
        _stop_services_and_exit(0)

    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)

    # Stream processes output to user's console while running to aid debugging
    try:
        while True:
            # If either process exits unexpectedly, stop the other and exit
            if uvicorn_proc.poll() is not None:
                rprint("[red]Uvicorn process exited[/red]")
                _stop_services_and_exit(1)
            if ngrok_proc.poll() is not None:
                rprint("[red]ngrok process exited[/red]")
                rprint(f"[yellow]See ngrok logs for details: {ngrok_log_path}[/yellow]")
                _stop_services_and_exit(1)
            time.sleep(0.5)
    except Exception:
        rprint("[red]Unexpected error while running services[/red]")
        _stop_services_and_exit(1)


def _terminate_by_pid(pid: int) -> None:
    try:
        # Try killing the whole process group if possible (when started with setsid)
        try:
            os.killpg(pid, signal.SIGTERM)
        except Exception:
            os.kill(pid, signal.SIGTERM)
        deadline = time.time() + 5
        while time.time() < deadline and _is_process_running(pid):
            time.sleep(0.1)
        if _is_process_running(pid):
            try:
                os.killpg(pid, signal.SIGKILL)
            except Exception:
                try:
                    os.kill(pid, signal.SIGKILL)
                except Exception:
                    pass
    except Exception:
        pass


@setup_app.command("stop")
def stop() -> None:
    """Stop background uvicorn and ngrok started via 'veris setup -d'."""
    project_dir = Path.cwd()
    state = _load_state(project_dir)
    if not state:
        rprint("[yellow]No detached setup state found at .veris/setup_state.json[/yellow]")
        raise typer.Exit(0)

    uv_pid = state.get("uvicorn_pid")
    ng_pid = state.get("ngrok_pid")

    if isinstance(ng_pid, int) and _is_process_running(ng_pid):
        rprint("[cyan]Stopping ngrok...[/cyan]")
        _terminate_by_pid(ng_pid)

    if isinstance(uv_pid, int) and _is_process_running(uv_pid):
        rprint("[cyan]Stopping uvicorn...[/cyan]")
        _terminate_by_pid(uv_pid)

    _delete_state(project_dir)
    rprint("[green]✅ Stopped detached services and cleared state[/green]")
