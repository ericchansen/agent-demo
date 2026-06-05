"""Orchestrator configuration for the Azure AI Projects SDK."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class OrchestratorConfig:
    """Configuration for the Azure AI Foundry orchestrator."""

    foundry_project_endpoint: str
    model_deployment_name: str
    fabric_iq_connection_id: str
    workiq_connection_id: str | None = None

    @classmethod
    def from_env(cls) -> OrchestratorConfig:
        """Build config from environment variables."""
        load_dotenv()
        return cls(
            foundry_project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            model_deployment_name=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o"),
            fabric_iq_connection_id=os.environ["FABRIC_IQ_CONNECTION_ID"],
            workiq_connection_id=os.environ.get("WORK_IQ_CONNECTION_ID"),
        )
