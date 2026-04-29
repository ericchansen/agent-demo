# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - Unreleased

### Changed
- Simplified to Copilot CLI + Fabric Data Agent MCP architecture (v1)
- Web research now uses CLI's built-in `web_search`/`web_fetch` (replaces custom Researcher Agent MCP server)
- SharePoint retrieval now uses CLI's built-in SharePoint/OneDrive tools (replaces custom SharePoint Agent MCP server)
- MCP config reduced from 3 servers to 1 (Fabric Data Agent only)
- Skills updated to reference built-in tools instead of custom MCP servers

### Added
- `archive/` directory preserving custom MCP servers and orchestrator stubs for future v3/v4 tiers
- `[project.optional-dependencies] sdk` group for Copilot SDK (v2)

### Removed
- `azure-ai-agents`, `fabric-data-agent-client`, `mcp`, `aiohttp` dependencies (not needed for v1/v2)
- `serve-researcher` and `serve-sharepoint` Makefile targets
- `src/orchestrator/` (moved to `archive/` — belongs in v3/v4)

## [0.1.0] - Unreleased

### Added
- Initial project scaffolding
- Directory structure for sub-agents, orchestrator, CLI skills, IaC, docs, and demos
- Wide World Importers as demo dataset
- Fabric Data Agent configuration templates
- CI/CD with GitHub Actions
- Bicep IaC for Azure infrastructure
