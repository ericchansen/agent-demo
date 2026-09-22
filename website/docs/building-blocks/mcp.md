---
sidebar_position: 3
title: MCP (Model Context Protocol)
---

# Model Context Protocol (MCP)

MCP is the wire protocol that connects agents to tools. It defines how an agent discovers what tools are available, what inputs they expect, and how to call them. In this accelerator, MCP is the bridge between Copilot CLI and backend services like the Fabric Data Agent and WorkIQ.

## Why MCP matters

Before MCP, every agent framework had its own way of defining tools — different schemas, different calling conventions, different discovery mechanisms. MCP standardizes this:

- **Tool discovery** — the agent asks "what can you do?" and gets a structured list
- **Typed inputs/outputs** — JSON Schema for parameters and return values
- **Transport-agnostic** — works over HTTP, stdio, WebSocket
- **Server-side logic** — the tool implementation lives in the server, not the agent

This means you can write a tool server once and connect it to any MCP-compatible agent.

> 📖 [MCP specification](https://modelcontextprotocol.io/) · [MCP concepts: tools](https://modelcontextprotocol.io/docs/concepts/tools)

## MCP in this accelerator

### Tool servers

| Server | Transport | What it does |
|---|---|---|
| `wwi-sales-data` | HTTP | Fabric Data Agent — WWI sales Lakehouse |
| `market-data-agent` | HTTP | Fabric Data Agent — SEC EDGAR financials |
| `workiq` | npm (stdio) | M365 activity signals |
| `researcher` | stdio | Web search for market intelligence |
| `sharepoint-agent` | stdio | SharePoint / Graph document access |

### Registration

Tools are registered in `.github/mcp.json` (workspace-scoped) or via `copilot mcp add` (user-scoped):

```json
{
  "mcpServers": {
    "wwi-sales-data": {
      "type": "http",
      "url": "https://api.fabric.microsoft.com/v1/mcp/workspaces/{id}/dataagent"
    }
  }
}
```

> 📖 [Copilot CLI MCP configuration](https://docs.github.com/copilot/github-copilot-in-the-cli/using-mcp-servers-with-copilot-cli) · [MCP server types](https://modelcontextprotocol.io/docs/concepts/transports)

## HTTP vs stdio transport

MCP supports two primary transports:

| Transport | How it works | Best for |
|---|---|---|
| **HTTP** | Agent makes HTTP requests to a URL | Cloud-hosted services (Fabric, APIs) |
| **stdio** | Agent spawns a local process and communicates via stdin/stdout | Local tools, npm packages |

The Fabric Data Agent uses HTTP (it's a cloud service). WorkIQ uses stdio via npm (it runs as a local process).

## Writing your own MCP server

The local Python servers use MCP SDK 2 (`>=2.2.0,<3`). Low-level servers register callbacks and return explicit result types. Unlike SDK 1, SDK 2 does **not** automatically validate tool arguments: validate the advertised schema before looking up data, making requests, or writing files.

```python
import asyncio

from mcp.server import Server, ServerRequestContext
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
    Tool,
)

from src.agents.mcp_validation import tool_error, validate_tool_arguments

tool = Tool(
    name="lookup_customer",
    description="Return the customer name supplied to this example tool",
    input_schema={
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    },
)


async def list_tools(ctx: ServerRequestContext, params: PaginatedRequestParams | None) -> ListToolsResult:
    return ListToolsResult(tools=[tool])


async def call_tool(ctx: ServerRequestContext, params: CallToolRequestParams) -> CallToolResult:
    if params.name != tool.name:
        return tool_error(f"Unknown tool: {params.name}")
    arguments = params.arguments or {}
    if error := validate_tool_arguments(tool, arguments):
        return error
    return CallToolResult(
        content=[TextContent(type="text", text=f"Customer: {arguments['name']}")],
        is_error=False,
    )


server = Server("my-tool", on_list_tools=list_tools, on_call_tool=call_tool)


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
```

This example runs from the installed accelerator repository and reuses its `jsonschema`-based validation helper. The helper returns `CallToolResult(is_error=True)` on schema violations, without coercion or default insertion. Python fields use `input_schema` and `is_error`; the JSON protocol still sends `inputSchema` and `isError`.

Expected operational failures should also return explicit error tool results through narrowly scoped exception handling. Unexpected programmer errors use the SDK 2 protocol-error path; do not hide them behind a blanket catch or a success-shaped fallback. The project's stdio integration tests exercise both cases.

See the [SDK 2 migration guide](https://github.com/modelcontextprotocol/python-sdk/blob/v2.2.0/docs/migration.md) for the callback, validation, and error-handling changes.

> 📖 [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) · [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) · [Building MCP servers](https://modelcontextprotocol.io/docs/guides/building-servers)

## MCP vs Foundry tools

MCP is the protocol used in the CLI surface. In the Foundry surface, the same capabilities are registered as Foundry tool types:

| MCP Concept | Foundry Equivalent |
|---|---|
| MCP server | Platform tool or function tool |
| Tool discovery (list_tools) | Tool registration in agent config |
| Tool call (call_tool) | Function calling via Responses API |

The key difference: MCP is a runtime discovery protocol (the agent asks "what tools exist?"), while Foundry tools are registered at agent creation time.

## Further reading

- [MCP specification](https://modelcontextprotocol.io/)
- [MCP concepts: tools](https://modelcontextprotocol.io/docs/concepts/tools)
- [MCP concepts: transports](https://modelcontextprotocol.io/docs/concepts/transports)
- [Copilot CLI MCP docs](https://docs.github.com/copilot/github-copilot-in-the-cli/using-mcp-servers-with-copilot-cli)
- [Foundry tool types](https://learn.microsoft.com/azure/ai-foundry/concepts/agents-tools)
