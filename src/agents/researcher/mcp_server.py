"""Researcher Agent — MCP server that researches companies on the open web."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server, ServerRequestContext

from src.agents.researcher.tools import research_company

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

_RESEARCH_TOOL = types.Tool(
    name="research_company",
    description=(
        "Research a company on the open web. Returns a summary, recent articles, "
        "and key metrics sourced from news and financial data."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "company_name": {
                "type": "string",
                "description": "Name of the company to research.",
            },
            "focus_areas": {
                "type": "string",
                "description": ("Optional focus for the research. One of: news, earnings, strategy, expansion."),
            },
        },
        "required": ["company_name"],
    },
)


async def handle_list_tools() -> list[types.Tool]:
    """Advertise available tools."""
    return [_RESEARCH_TOOL]


async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
    """Dispatch tool calls."""
    if name == "research_company":
        result = await research_company(
            company_name=arguments["company_name"],
            focus_areas=arguments.get("focus_areas"),
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    raise ValueError(f"Unknown tool: {name}")


async def _list_tools_handler(
    _context: ServerRequestContext[Any],
    _params: types.PaginatedRequestParams | None,
) -> types.ListToolsResult:
    return types.ListToolsResult(tools=await handle_list_tools())


async def _call_tool_handler(
    _context: ServerRequestContext[Any],
    params: types.CallToolRequestParams,
) -> types.CallToolResult:
    return types.CallToolResult(content=await handle_call_tool(params.name, params.arguments or {}))


server = Server(
    "researcher-agent",
    version="0.1.0",
    on_list_tools=_list_tools_handler,
    on_call_tool=_call_tool_handler,
)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run the Researcher MCP server over stdio."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
