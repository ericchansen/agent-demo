"""Azure AI Foundry orchestrator built on the Azure AI Projects SDK."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FabricIQPreviewTool,
    FunctionTool,
    MCPTool,
    PromptAgentDefinition,
    WorkIQPreviewTool,
)
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from src.orchestrator.config import OrchestratorConfig

AGENT_NAME = "WWISalesAgent"
DEFAULT_REPORT_TEMPLATE = "account_plan.md"
MAX_FUNCTION_CALL_ROUNDS = 8

AGENT_INSTRUCTIONS = """You are a sales analyst for Wide World Importers (WWI), a wholesale novelty goods company.

Your capabilities:
1. SALES DATA: Query the WWI data warehouse via Fabric IQ for sales transactions,
   customers, products, geography, and employees. Write correct T-SQL for Fabric.
2. ACTIVITY DATA: When WorkIQ is available, retrieve M365 activity signals
   (emails, meetings, engagement) for customer context.
3. QUOTA FORECAST: Generate FY quota projections based on trailing 12-month sales trends.
4. REPORTS: Generate formatted DOCX reports with charts and citations.

Guidelines:
- Use markdown tables for multi-row results
- Round currency to 2 decimal places
- Include totals/averages where appropriate
- Cite data sources
- Proactively surface insights the user might not have asked for
- When comparing time periods, show both absolute values and percentage change"""

ToolDefinition = FabricIQPreviewTool | WorkIQPreviewTool | FunctionTool | MCPTool
ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


def mock_workiq_func(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return mock M365 activity data when WorkIQ is not available."""
    customer = arguments.get("customer_name", "Unknown")
    return {
        "customer": customer,
        "source": "mock (WorkIQ not available on this tenant)",
        "recent_activity": [
            {
                "type": "email",
                "subject": f"Re: FY27 Planning - {customer}",
                "date": "2026-05-28",
                "participants": ["AE", "Champion"],
            },
            {
                "type": "meeting",
                "subject": f"QBR Prep - {customer}",
                "date": "2026-05-15",
                "duration_min": 60,
            },
            {
                "type": "email",
                "subject": f"Updated pricing proposal - {customer}",
                "date": "2026-05-10",
                "participants": ["AE", "Procurement"],
            },
            {
                "type": "meeting",
                "subject": f"Technical deep dive - {customer}",
                "date": "2026-04-22",
                "duration_min": 90,
            },
        ],
        "engagement_score": "High",
        "last_contact": "2026-05-28",
    }


def forecast_quota_func(arguments: dict[str, Any]) -> dict[str, Any]:
    """Generate FY quota forecast stub with structured data."""
    customer = arguments.get("customer_name", "Unknown")
    items = [
        {
            "category": "Novelty Items",
            "current_fy_revenue": 450000,
            "growth_rate": 0.12,
            "projected_fy_revenue": 504000,
        },
        {
            "category": "Clothing",
            "current_fy_revenue": 320000,
            "growth_rate": 0.12,
            "projected_fy_revenue": 358400,
        },
        {
            "category": "Computing Novelties",
            "current_fy_revenue": 280000,
            "growth_rate": 0.10,
            "projected_fy_revenue": 308000,
        },
        {
            "category": "Toys",
            "current_fy_revenue": 200000,
            "growth_rate": 0.15,
            "projected_fy_revenue": 230000,
        },
    ]
    return {
        "customer": customer,
        "current_fy_total": sum(item["current_fy_revenue"] for item in items),
        "projected_fy_total": sum(item["projected_fy_revenue"] for item in items),
        "overall_growth_rate": 0.12,
        "methodology": "Trailing 12-month sales trend with category-specific growth rates (demo data)",
        "items": items,
    }


def generate_report_func(arguments: dict[str, Any]) -> dict[str, Any]:
    """Generate a DOCX report using the real report generator."""
    from src.agents.report_generator.generator import (
        ForecastData,
        ForecastItem,
        ReportData,
        generate_docx,
    )

    title = arguments.get("title", "Sales Report")
    customer = arguments.get("customer_name", "Unknown")
    sections = arguments.get("sections", [])
    forecast_raw = arguments.get("forecast_data")

    forecast = None
    if isinstance(forecast_raw, dict):
        forecast = ForecastData(
            customer_name=customer,
            current_fy_total=forecast_raw.get("current_fy_total", 0),
            projected_fy_total=forecast_raw.get("projected_fy_total", 0),
            overall_growth_rate=forecast_raw.get("overall_growth_rate", 0),
            methodology=forecast_raw.get("methodology", ""),
            items=[ForecastItem(**item) for item in forecast_raw.get("items", [])],
        )

    data = ReportData(
        title=title,
        customer_name=customer,
        generated_at=datetime.now(),
        pipeline_data=sections if isinstance(sections, list) else [],
        forecast_data=forecast,
    )

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{_slugify_filename(title)}.docx"

    generate_docx(data, DEFAULT_REPORT_TEMPLATE, str(output_path))

    return {
        "status": "generated",
        "file_path": str(output_path),
        "format": "docx",
        "title": title,
        "has_forecast": forecast is not None,
        "has_chart": forecast is not None,
    }


def _slugify_filename(value: str) -> str:
    """Convert a report title into a filesystem-safe stem."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip().lower()).strip("._")
    return cleaned or "sales_report"


def _build_function_tool(name: str, description: str, parameters: dict[str, Any]) -> FunctionTool:
    """Create a strongly validated function tool definition."""
    return FunctionTool(name=name, description=description, parameters=parameters, strict=True)


def _build_tools(config: OrchestratorConfig) -> tuple[list[ToolDefinition], dict[str, ToolHandler]]:
    """Build the tool list and local function handlers for the prompt agent."""
    tools: list[ToolDefinition] = [
        FabricIQPreviewTool(
            project_connection_id=config.fabric_iq_connection_id,
            require_approval="never",
        )
    ]
    handlers: dict[str, ToolHandler] = {
        "forecast_quota": forecast_quota_func,
        "generate_report": generate_report_func,
    }

    if config.workiq_connection_id:
        tools.append(WorkIQPreviewTool(project_connection_id=config.workiq_connection_id))
    else:
        tools.append(
            _build_function_tool(
                name="get_account_activity",
                description="Retrieve recent M365 activity signals for a customer account.",
                parameters={
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Customer or prospect account name.",
                        }
                    },
                    "required": ["customer_name"],
                    "additionalProperties": False,
                },
            )
        )
        handlers["get_account_activity"] = mock_workiq_func

    tools.extend(
        [
            _build_function_tool(
                name="forecast_quota",
                description="Generate an FY quota projection for a named customer account.",
                parameters={
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Customer or prospect account name.",
                        }
                    },
                    "required": ["customer_name"],
                    "additionalProperties": False,
                },
            ),
            _build_function_tool(
                name="generate_report",
                description="Generate a formatted DOCX sales report for a customer account.",
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title for the generated report."},
                        "customer_name": {
                            "type": "string",
                            "description": "Customer or prospect account name.",
                        },
                        "sections": {
                            "type": "array",
                            "description": "List of section dictionaries to include in the report.",
                            "items": {"type": "object", "additionalProperties": True},
                        },
                        "forecast_data": {
                            "type": "object",
                            "description": "Optional quota forecast payload to render in the DOCX report.",
                            "additionalProperties": True,
                        },
                    },
                    "required": ["customer_name"],
                    "additionalProperties": False,
                },
            ),
        ]
    )

    return tools, handlers


def _create_agent(project_client: AIProjectClient, config: OrchestratorConfig) -> Any:
    """Create a new prompt agent version backed by the configured tools."""
    tools, handlers = _build_tools(config)
    agent = project_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=config.model_deployment_name,
            instructions=AGENT_INSTRUCTIONS,
            tools=tools,
        ),
    )
    setattr(agent, "_local_function_handlers", handlers)
    return agent


def _get_or_create_agent(project_client: AIProjectClient, config: OrchestratorConfig) -> Any:
    """Get the latest agent definition or create it if it does not exist yet."""
    try:
        agent = project_client.agents.get(AGENT_NAME)
    except (HttpResponseError, ResourceNotFoundError):
        return _create_agent(project_client, config)

    _, handlers = _build_tools(config)
    setattr(agent, "_local_function_handlers", handlers)
    return agent


def _item_value(item: Any, field: str, default: Any = None) -> Any:
    """Read a field from either a pydantic model or a plain dict."""
    if isinstance(item, dict):
        return item.get(field, default)
    return getattr(item, field, default)


def _execute_local_functions(agent: Any, response: Any) -> list[dict[str, str]]:
    """Execute any local function calls requested by the response."""
    handlers: dict[str, ToolHandler] = getattr(agent, "_local_function_handlers", {})
    tool_outputs: list[dict[str, str]] = []

    for item in getattr(response, "output", []) or []:
        if _item_value(item, "type") != "function_call":
            continue

        name = _item_value(item, "name", "")
        raw_arguments = _item_value(item, "arguments", "{}")
        call_id = _item_value(item, "call_id") or _item_value(item, "id")
        handler = handlers.get(name)

        try:
            arguments = json.loads(raw_arguments) if isinstance(raw_arguments, str) else raw_arguments
        except json.JSONDecodeError:
            arguments = {}

        if handler is None:
            result = {"error": f"Unknown function: {name}"}
        else:
            result = handler(arguments if isinstance(arguments, dict) else {})

        if call_id:
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": str(call_id),
                    "output": json.dumps(result, default=str),
                }
            )

    return tool_outputs


def _extract_output_text(response: Any) -> str:
    """Return the text content from a responses API payload."""
    output_text = getattr(response, "output_text", "")
    if output_text:
        return output_text

    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        if _item_value(item, "type") != "message":
            continue
        for content in _item_value(item, "content", []) or []:
            text = _item_value(content, "text")
            if isinstance(text, str):
                chunks.append(text)
                continue
            text_value = _item_value(text, "value")
            if isinstance(text_value, str):
                chunks.append(text_value)

    return "\n".join(chunk for chunk in chunks if chunk) or "(no response text returned)"


def run_query(question: str, config: OrchestratorConfig | None = None) -> str:
    """Send a question to the agent and return the response."""
    if config is None:
        config = OrchestratorConfig.from_env()

    credential = DefaultAzureCredential()
    project_client = AIProjectClient(
        endpoint=config.foundry_project_endpoint,
        credential=credential,
        allow_preview=True,
    )
    openai_client = project_client.get_openai_client()

    agent = _get_or_create_agent(project_client, config)
    extra_body = {"agent_reference": {"name": agent.name, "type": "agent_reference"}}

    response = openai_client.responses.create(
        input=question,
        extra_body=extra_body,
    )

    for _ in range(MAX_FUNCTION_CALL_ROUNDS):
        tool_outputs = _execute_local_functions(agent, response)
        if not tool_outputs:
            break

        response = openai_client.responses.create(
            input=tool_outputs,
            previous_response_id=response.id,
            extra_body=extra_body,
        )

    return _extract_output_text(response)
