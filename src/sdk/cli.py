#!/usr/bin/env python3
"""CLI entrypoint for the Copilot SDK Sales Agent (v2).

Usage:
    python -m src.sdk.cli "Prepare an account plan for Tailspin Toys"
    python -m src.sdk.cli --fabric-url https://... "What are our top customers?"
"""

from __future__ import annotations

import argparse
import asyncio

from src.sdk.agent import AgentConfig, SalesAgent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fabric Sales Agent — Copilot SDK (v2)",
        prog="python -m src.sdk.cli",
    )
    parser.add_argument("prompt", help="Natural language prompt for the agent")
    parser.add_argument(
        "--fabric-url",
        default="",
        help="Fabric Data Agent MCP URL (or set FABRIC_MCP_URL env var)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4.1",
        help="Model to use (default: gpt-4.1)",
    )
    parser.add_argument(
        "--foundry-url",
        default="",
        help="Azure AI Foundry resource URL for BYOK (or set AZURE_AI_FOUNDRY_RESOURCE_URL)",
    )
    parser.add_argument(
        "--managed-identity",
        action="store_true",
        help="Use Azure Managed Identity for BYOK auth",
    )

    args = parser.parse_args()

    config = AgentConfig(
        fabric_mcp_url=args.fabric_url,
        model=args.model,
        foundry_resource_url=args.foundry_url,
        use_managed_identity=args.managed_identity,
    )

    agent = SalesAgent(config=config)

    async def _run() -> str:
        try:
            await agent.start()
            return await agent.run(args.prompt)
        finally:
            await agent.stop()

    result = asyncio.run(_run())
    print(result)


if __name__ == "__main__":
    main()
