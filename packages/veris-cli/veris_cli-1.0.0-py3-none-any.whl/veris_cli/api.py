"""API client for the Veris CLI."""

from __future__ import annotations

import os
from typing import Any

import httpx


class ApiClient:
    """API client for the Veris CLI."""

    def __init__(self, base_url: str | None = None, *, timeout: float = 30.0):
        """Initialize API client."""
        self.base_url = base_url or os.environ.get(
            "VERIS_API_URL", "https://simulator.dev.api.veris.ai/"
        )
        # Read API key from environment variable
        api_key = os.environ.get("VERIS_API_KEY")
        default_headers: dict[str, str] = {}
        if api_key:
            default_headers["X-API-Key"] = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=default_headers,
        )

    # Scenario generation (V2)
    def start_scenario_generation(self, payload: dict[str, Any]) -> dict[str, str]:
        """Kick off scenario generation and return generation metadata.

        Expected response: { generation_id: str, status: str, message: str }
        """
        response = self._client.post("/v2/scenarios/generate", json=payload)
        response.raise_for_status()
        return response.json()

    def get_generation_status(self, generation_id: str) -> dict[str, Any]:
        """Get status for a generation job."""
        response = self._client.get(f"/v2/scenarios/generation/{generation_id}/status")
        response.raise_for_status()
        return response.json()

    def get_generated_scenarios(
        self, generation_id: str, include_failed: bool = False
    ) -> dict[str, Any]:
        """Retrieve generated scenarios for a generation job."""
        params = {"include_failed": str(include_failed).lower()}
        response = self._client.get(
            f"/v2/scenarios/generation/{generation_id}/scenarios", params=params
        )
        response.raise_for_status()
        return response.json()

    # Simulations
    def start_simulation(self, run_id: str, payload: dict[str, Any]) -> str:
        """Start a simulation."""
        response = self._client.post(
            "/v2/simulations",
            json=payload,
            headers={"X-Run-Id": run_id},
        )
        response.raise_for_status()
        data = response.json()
        simulation_id = data.get("simulation_id") or data.get("session_id")
        if not simulation_id:
            raise ValueError("Missing simulation_id/session_id in response")
        return simulation_id

    def get_simulation_status(self, simulation_id: str) -> str:
        """Get the status of a simulation."""
        response = self._client.get(f"/v2/simulations/{simulation_id}/status")
        response.raise_for_status()
        data = response.json()
        # Expect e.g. { status: PENDING|IN_PROGRESS|COMPLETED|FAILED }
        return data.get("status", "UNKNOWN")

    def get_simulation_logs(self, simulation_id: str) -> dict[str, Any]:
        """Get the logs of a simulation."""
        response = self._client.get(f"/v2/simulations/{simulation_id}/logs")
        response.raise_for_status()
        return response.json()

    def kill_simulation(self, simulation_id: str) -> None:
        """Kill a simulation."""
        response = self._client.post(f"/v2/simulations/{simulation_id}/kill")
        response.raise_for_status()

    # Evaluations
    def start_evaluation(self, session_id: str) -> str:
        """Start an evaluation."""
        response = self._client.post("/evals/evaluate", json={"session_id": session_id})
        response.raise_for_status()
        data = response.json()
        eval_id = data.get("evaluation_id") or data.get("eval_id")
        if not eval_id:
            raise ValueError("Missing eval_id/evaluation_id in response")
        return eval_id

    def get_evaluation_status(self, eval_id: str) -> str:
        """Get the status of an evaluation."""
        response = self._client.get(f"/evals/{eval_id}/status")
        response.raise_for_status()
        data = response.json()
        return data.get("status", "UNKNOWN")

    def get_evaluation_results(self, eval_id: str) -> dict[str, Any]:
        """Get the results of an evaluation."""
        response = self._client.get(f"/evals/{eval_id}")
        response.raise_for_status()
        return response.json()

    def kill_evaluation(self, eval_id: str) -> None:
        """Kill an evaluation."""
        response = self._client.post(f"/evals/{eval_id}/kill")
        response.raise_for_status()
