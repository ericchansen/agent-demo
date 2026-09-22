"""Explicit input validation for the low-level MCP servers."""

from __future__ import annotations

from typing import Any

import jsonschema
from mcp.types import CallToolResult, TextContent, Tool


def tool_error(message: str) -> CallToolResult:
    """Return an error the caller can handle as a tool result."""
    return CallToolResult(content=[TextContent(type="text", text=message)], is_error=True)


def validate_tool_arguments(tool: Tool, arguments: dict[str, Any]) -> CallToolResult | None:
    """Apply the advertised schema before dispatch, without coercion or defaults."""
    try:
        jsonschema.validate(instance=arguments, schema=tool.input_schema)
    except jsonschema.ValidationError as exc:
        return tool_error(f"Input validation error: {exc.message}")
    return None
