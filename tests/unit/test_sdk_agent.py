"""Unit tests for the Copilot SDK agent wrapper (v2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.sdk.agent import (
    AgentConfig,
    SalesAgent,
    _build_mcp_config,
    _build_provider_config,
    generate_report_tool,
)

# ---------------------------------------------------------------------------
# AgentConfig
# ---------------------------------------------------------------------------


class TestAgentConfig:
    def test_from_env_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("FABRIC_MCP_URL", raising=False)
        monkeypatch.delenv("COPILOT_MODEL", raising=False)
        monkeypatch.delenv("AZURE_AI_FOUNDRY_RESOURCE_URL", raising=False)
        monkeypatch.delenv("USE_MANAGED_IDENTITY", raising=False)

        config = AgentConfig.from_env()
        assert config.fabric_mcp_url == ""
        assert config.model == "gpt-4.1"
        assert config.foundry_resource_url == ""
        assert config.use_managed_identity is False

    def test_from_env_with_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FABRIC_MCP_URL", "https://fabric.example.com/mcp")
        monkeypatch.setenv("COPILOT_MODEL", "gpt-5")
        monkeypatch.setenv("AZURE_AI_FOUNDRY_RESOURCE_URL", "https://foundry.example.com")
        monkeypatch.setenv("USE_MANAGED_IDENTITY", "true")

        config = AgentConfig.from_env()
        assert config.fabric_mcp_url == "https://fabric.example.com/mcp"
        assert config.model == "gpt-5"
        assert config.foundry_resource_url == "https://foundry.example.com"
        assert config.use_managed_identity is True


# ---------------------------------------------------------------------------
# MCP config builder
# ---------------------------------------------------------------------------


class TestBuildMcpConfig:
    def test_empty_url_returns_empty(self) -> None:
        assert _build_mcp_config("") == {}

    def test_valid_url_returns_server_config(self) -> None:
        result = _build_mcp_config("https://fabric.example.com/mcp")
        assert "wwi-sales-data" in result
        assert result["wwi-sales-data"]["type"] == "http"
        assert result["wwi-sales-data"]["url"] == "https://fabric.example.com/mcp"


# ---------------------------------------------------------------------------
# Provider config builder
# ---------------------------------------------------------------------------


class TestBuildProviderConfig:
    def test_no_foundry_url_returns_none(self) -> None:
        config = AgentConfig(foundry_resource_url="")
        assert _build_provider_config(config) is None

    def test_with_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        config = AgentConfig(foundry_resource_url="https://foundry.example.com")
        result = _build_provider_config(config)

        assert result is not None
        assert result["type"] == "openai"
        assert result["base_url"] == "https://foundry.example.com/openai/v1/"
        assert result["api_key"] == "test-key"

    def test_trailing_slash_stripped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "k")
        config = AgentConfig(foundry_resource_url="https://foundry.example.com/")
        result = _build_provider_config(config)
        assert result["base_url"] == "https://foundry.example.com/openai/v1/"


# ---------------------------------------------------------------------------
# Report generation function tool
# ---------------------------------------------------------------------------


class TestGenerateReportTool:
    def test_generates_docx(self, tmp_path: Path) -> None:
        output = str(tmp_path / "test_report.docx")
        result = generate_report_tool(
            title="Test Account Plan",
            customer_name="Contoso Ltd",
            pipeline_data=[{"deal": "Deal A", "value": 100_000, "stage": "Proposal"}],
            research_data={"articles": [], "key_metrics": {}},
            output_path=output,
        )
        assert Path(result).exists()
        assert result.endswith(".docx")

    def test_default_filename(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        result = generate_report_tool(
            title="Test Plan",
            customer_name="Tailspin Toys",
            pipeline_data=[],
            research_data={},
        )
        assert "Tailspin_Toys" in result
        assert Path(result).exists()


# ---------------------------------------------------------------------------
# SalesAgent construction (no SDK import needed)
# ---------------------------------------------------------------------------


class TestSalesAgent:
    def test_from_env_creates_instance(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("FABRIC_MCP_URL", raising=False)
        agent = SalesAgent.from_env()
        assert isinstance(agent, SalesAgent)
        assert agent.config.fabric_mcp_url == ""

    def test_custom_config(self) -> None:
        config = AgentConfig(fabric_mcp_url="https://test.com/mcp", model="gpt-5")
        agent = SalesAgent(config=config)
        assert agent.config.model == "gpt-5"
        assert agent._started is False
