"""Loaders for scenario and evaluation metrics."""

from __future__ import annotations

import json
from pathlib import Path

from veris_cli.models.scenarios.agent_spec import AgentSpec

from .types import EvaluationMetric


def load_agent_spec(path: Path) -> AgentSpec:
    """Load the agent spec from a file."""
    content = path.read_text(encoding="utf-8")
    data = json.loads(content)
    return AgentSpec.model_validate(data)


def load_scenarios(directory: Path) -> list[dict]:
    """Load the scenarios from a directory."""
    scenarios: list[dict] = []
    for file in sorted(directory.glob("*.json")):
        raw = json.loads(file.read_text(encoding="utf-8"))
        scenarios.append(raw)
    return scenarios


def load_evaluation_metrics() -> list[EvaluationMetric]:
    """Load the evaluation metrics."""
    return [
        EvaluationMetric(
            id="accuracy",
            name="Accuracy",
            description="Factual correctness of information provided",
        ),
        EvaluationMetric(
            id="helpfulness",
            name="Helpfulness",
            description="Effectiveness in addressing user needs and requests",
        ),
        EvaluationMetric(
            id="relevance",
            name="Relevance",
            description="Direct alignment with user questions and context",
        ),
        EvaluationMetric(
            id="clarity",
            name="Clarity",
            description="Communication quality and understandability",
        ),
    ]
