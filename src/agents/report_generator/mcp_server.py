"""Report Generator MCP Server — generates DOCX/PPTX reports via MCP protocol."""

from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from src.agents.report_generator.generator import ReportData, generate_docx, generate_pptx

_DOCX_TEMPLATE = "account_plan.md"
_PPTX_TEMPLATE = "qbr_deck.md"

server = Server("report-generator")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Advertise available report generation tools."""
    return [
        Tool(
            name="generate_report",
            description=(
                "Generate a formatted DOCX or PPTX report from structured data. "
                "Provide a title, customer name, and data sections. "
                "Returns the file path of the generated report."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Report title"},
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "format": {"type": "string", "enum": ["docx", "pptx"], "default": "docx"},
                    "pipeline_data": {
                        "type": "array",
                        "description": (
                            "Sales pipeline data as list of objects with deal_name, value, stage, close_date"
                        ),
                        "items": {"type": "object"},
                    },
                    "additional_context": {"type": "string", "description": "Additional context or notes"},
                },
                "required": ["title", "customer_name"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch MCP tool calls to the report generator."""
    if name != "generate_report":
        raise ValueError(f"Unknown tool: {name}")

    title = arguments.get("title", "Untitled Report")
    customer = arguments.get("customer_name", "Unknown")
    fmt = arguments.get("format", "docx")
    pipeline_data = arguments.get("pipeline_data", [])
    context = arguments.get("additional_context")

    data = ReportData(
        title=title,
        customer_name=customer,
        generated_at=datetime.now(),
        pipeline_data=pipeline_data,
        additional_context=context,
    )

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    safe_title = _slugify_filename(title)
    output_path = output_dir / f"{safe_title}.{fmt}"

    if fmt == "pptx":
        file_path = generate_pptx(data, _PPTX_TEMPLATE, str(output_path))
    else:
        file_path = generate_docx(data, _DOCX_TEMPLATE, str(output_path))

    return [
        TextContent(
            type="text",
            text=json.dumps(
                {
                    "status": "success",
                    "file_path": file_path,
                    "format": fmt,
                    "title": title,
                }
            ),
        )
    ]


def _slugify_filename(value: str) -> str:
    """Convert a report title into a filesystem-safe stem."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip().lower()).strip("._")
    return cleaned or "report"


async def main() -> None:
    """Run the Report Generator MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
