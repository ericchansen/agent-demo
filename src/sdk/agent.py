"""Copilot SDK agent — programmatic wrapper around the Fabric Sales Agent workflow.

Embeds the same capabilities as the Copilot CLI (v1) into a standalone Python app:
- Fabric Data Agent for pipeline queries (via MCP)
- Web research via built-in web_search/web_fetch
- Report generation (DOCX/PPTX) via local function tool

Usage:
    from src.sdk.agent import SalesAgent

    agent = SalesAgent(fabric_mcp_url="https://...")
    result = await agent.run("Prepare an account plan for Tailspin Toys")
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from src.agents.report_generator.generator import ReportData, generate_docx


@dataclass
class AgentConfig:
    """Configuration for the Sales Agent."""

    fabric_mcp_url: str = ""
    model: str = "gpt-4.1"

    # BYOK: point at your own Azure AI Foundry model
    foundry_resource_url: str = ""
    use_managed_identity: bool = False

    @classmethod
    def from_env(cls) -> AgentConfig:
        """Build config from environment variables."""
        return cls(
            fabric_mcp_url=os.environ.get("FABRIC_MCP_URL", ""),
            model=os.environ.get("COPILOT_MODEL", "gpt-4.1"),
            foundry_resource_url=os.environ.get("AZURE_AI_FOUNDRY_RESOURCE_URL", ""),
            use_managed_identity=os.environ.get("USE_MANAGED_IDENTITY", "").lower() == "true",
        )


def _build_mcp_config(fabric_mcp_url: str) -> dict[str, Any]:
    """Build the MCP server configuration for the Copilot SDK session."""
    if not fabric_mcp_url:
        return {}
    return {
        "wwi-sales-data": {
            "type": "http",
            "url": fabric_mcp_url,
            "description": "Wide World Importers sales data via Fabric Data Agent",
        },
    }


def _build_provider_config(config: AgentConfig) -> dict[str, Any] | None:
    """Build BYOK provider config if Foundry URL is set."""
    if not config.foundry_resource_url:
        return None

    provider: dict[str, Any] = {
        "type": "openai",
        "base_url": f"{config.foundry_resource_url.rstrip('/')}/openai/v1/",
        "wire_api": "responses",
    }

    if config.use_managed_identity:
        try:
            from azure.identity import DefaultAzureCredential

            credential = DefaultAzureCredential()
            token = credential.get_token("https://cognitiveservices.azure.com/.default").token
            provider["bearer_token"] = token
        except ImportError:
            raise ImportError(
                "azure-identity is required for Managed Identity BYOK. "
                "Install with: pip install azure-identity"
            )
    else:
        api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
        if api_key:
            provider["api_key"] = api_key

    return provider


def generate_report_tool(
    title: str,
    customer_name: str,
    pipeline_data: list[dict[str, Any]],
    research_data: dict[str, Any],
    sharepoint_docs: list[dict[str, Any]] | None = None,
    output_path: str | None = None,
) -> str:
    """Generate a DOCX account plan report. Registered as a Copilot SDK function tool.

    Returns the path to the generated DOCX file.
    """
    data = ReportData(
        title=title,
        customer_name=customer_name,
        generated_at=datetime.now(),
        pipeline_data=pipeline_data,
        research_data=research_data,
        sharepoint_docs=sharepoint_docs or [],
    )

    if output_path is None:
        safe_name = customer_name.replace(" ", "_")
        output_path = f"Account_Plan_{safe_name}_{datetime.now():%Y-%m-%d}.docx"

    output = Path(output_path)
    generate_docx(data, "account_plan.md", str(output))
    return str(output.resolve())


# ---------------------------------------------------------------------------
# Agent class — wraps Copilot SDK (imported lazily to allow mock testing)
# ---------------------------------------------------------------------------


class SalesAgent:
    """High-level wrapper for the Fabric Sales Agent using Copilot SDK.

    Example::

        agent = SalesAgent.from_env()
        result = await agent.run("Prepare an account plan for Tailspin Toys")
        print(result)
    """

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig.from_env()
        self._client = None
        self._started = False

    @classmethod
    def from_env(cls) -> SalesAgent:
        return cls(config=AgentConfig.from_env())

    async def start(self) -> None:
        """Initialize the Copilot SDK client."""
        try:
            from copilot import CopilotClient  # noqa: PLC0415
        except ImportError:
            raise ImportError(
                "github-copilot-sdk is required for v2. "
                "Install with: pip install github-copilot-sdk"
            )

        self._client = CopilotClient()
        await self._client.start()
        self._started = True

    async def stop(self) -> None:
        """Shut down the Copilot SDK client."""
        if self._client and self._started:
            await self._client.stop()
            self._started = False

    async def run(self, prompt: str) -> str:
        """Run a prompt through the Sales Agent and return the response.

        The agent has access to:
        - Fabric Data Agent (MCP) for pipeline queries
        - Built-in web_search/web_fetch for customer research
        - generate_report_tool for DOCX generation
        """
        if not self._started:
            await self.start()

        from copilot.session import PermissionHandler  # noqa: PLC0415

        session_kwargs: dict[str, Any] = {
            "model": self.config.model,
            "on_permission_request": PermissionHandler.approve_all,
            "instructions": (
                "You are a sales assistant for Wide World Importers. "
                "You help users prepare account plans by querying pipeline data "
                "from Fabric, researching customers on the web, finding internal "
                "documents, and generating DOCX reports with citations."
            ),
        }

        # BYOK provider config
        provider = _build_provider_config(self.config)
        if provider:
            session_kwargs["provider"] = provider

        # MCP servers
        mcp_config = _build_mcp_config(self.config.fabric_mcp_url)
        if mcp_config:
            session_kwargs["mcp_servers"] = mcp_config

        session = await self._client.create_session(**session_kwargs)

        try:
            response = await session.send_and_wait(prompt)
            return response.data.content if response else ""
        finally:
            await session.disconnect()
