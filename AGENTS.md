# Agent Instructions (AGENTS.md)

## Project Overview

**Fabric Sales Agent Accelerator** is an open-source reference implementation demonstrating how to combine Microsoft Fabric Data Agent with agentic AI workflows. It uses the Wide World Importers sample dataset (wholesale novelty goods).

The repo demonstrates progressive architecture tiers — from a simple Copilot CLI demo to enterprise multi-agent orchestration — letting users choose the approach that fits their team.

## Current Architecture (v1 + v2)

### v1: Copilot CLI
- **Fabric Data Agent** — NL→SQL/DAX queries over OneLake data (built-in MCP server)
- **Web research** — handled by Copilot CLI's built-in `web_search` and `web_fetch` tools
- **SharePoint docs** — handled by Copilot CLI's built-in SharePoint/OneDrive tools
- **Report Generator** — template-based DOCX/PPTX generation with citations
- **Skills** — CLI skill files that orchestrate the workflow

### v2: Copilot SDK
Same capabilities as v1, wrapped in the GitHub Copilot SDK (`github-copilot-sdk`) for
programmatic invocation from standalone apps.

### Future Tiers (not yet implemented)
- **v3:** Copilot SDK → Docker → Foundry Hosted Agents → M365 publish
- **v4:** Microsoft Agent Framework multi-agent orchestration with upgraded custom agents

## Coding Standards

- **Language:** Python 3.11+
- **Linting:** Ruff (rules: E, F, I, N, W, UP). Line length 120.
- **Type checking:** mypy strict for `src/agents/report_generator/`
- **Testing:** pytest. Unit tests mock external services.
- **Formatting:** Ruff formatter
- **IaC:** Bicep (Azure-native). Modules in `infra/modules/`.
- **Commits:** Conventional commits (`feat:`, `fix:`, `docs:`, `infra:`, `test:`)

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/agents/report_generator/` | DOCX/PPTX report generation with citations |
| `src/cli/skills/` | Copilot CLI skill definitions |
| `src/sdk/` | Copilot SDK agent wrapper (v2) |
| `fabric/` | Fabric Data Agent config, instructions, few-shot examples |
| `infra/` | Bicep IaC (Fabric capacity, Key Vault, Entra app) |
| `demo/` | Sample data (WWI), demo scripts |
| `docs/` | Architecture, security, setup, surfaces comparison |
| `tests/` | Unit and eval tests |
| `archive/` | Preserved v3/v4 code: custom Researcher + SharePoint MCP servers, orchestrator stubs |

## Important Notes

- **LLM-agnostic** — never hardcode a model provider. Config accepts any endpoint.
- **Citations first-class** — every generated report must include source attribution.
- **Fabric MCP is built-in** — use the Data Agent's native MCP server, not a custom wrapper.
- **CLI built-in tools preferred** — web research and SharePoint retrieval use CLI's native capabilities, not custom MCP servers.
- **No customer data in repo** — all data is Wide World Importers (Microsoft sample).
