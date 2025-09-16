"""Models for the Veris CLI."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Model for run status."""

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class SimulationStatus(str, Enum):
    """Model for simulation status."""

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class EvaluationEntry(BaseModel):
    """Model for evaluation entry."""

    eval_id: str
    status: RunStatus
    results: dict[str, Any] | None = None


class SimulationEntry(BaseModel):
    """Model for simulation entry."""

    id: str
    scenario_id: str
    scenario_name: str | None = None
    simulation_id: str | None = None
    simulation_status: SimulationStatus = SimulationStatus.pending
    logs: list[dict[str, Any]] | None = None
    eval_id: str | None = None
    evaluation_status: RunStatus | None = None
    evaluation_results: dict[str, Any] | None = None


class Run(BaseModel):
    """Model for run."""

    run_id: str
    created_at: str
    status: RunStatus
    evaluations: list[EvaluationEntry] = Field(default_factory=list)
    simulations: list[SimulationEntry] = Field(default_factory=list)
