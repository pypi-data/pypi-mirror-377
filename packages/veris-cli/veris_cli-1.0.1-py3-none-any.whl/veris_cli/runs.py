"""Runs store."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from .fs import ensure_veris_dir
from .run_models import Run, RunStatus, SimulationEntry, SimulationStatus


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class RunsStore:
    """Runs store."""

    def __init__(self, project_dir: Path):
        """Initialize the runs store."""
        self.project_dir = project_dir
        self.veris_dir = ensure_veris_dir(project_dir)
        self.runs_dir = self.veris_dir / "runs"
        self.runs_dir.mkdir(exist_ok=True)

    def _run_file(self, run_id: str) -> Path:
        """Get the path to the run file."""
        return self.runs_dir / f"{run_id}.json"

    def create_run(self, selected_scenarios: list[dict]) -> Run:
        """Create a run."""
        run_id = str(uuid.uuid4())
        run = Run(
            run_id=run_id,
            created_at=_now_iso(),
            status=RunStatus.pending,
            simulations=[
                SimulationEntry(
                    id=str(uuid.uuid4()),
                    scenario_id=sc["scenario_id"],
                    scenario_name=sc.get("title"),
                    simulation_status=SimulationStatus.pending,
                )
                for sc in selected_scenarios
            ],
        )
        self.save_run(run)
        return run

    def save_run(self, run: Run) -> None:
        """Save a run."""
        path = self._run_file(run.run_id)
        path.write_text(run.model_dump_json(indent=2), encoding="utf-8")

    def load_run(self, run_id: str) -> Run:
        """Load a run."""
        data = json.loads(self._run_file(run_id).read_text(encoding="utf-8"))
        return Run.model_validate(data)
