---
sidebar_position: 2
title: Architecture
---

# Architecture

## System Diagram

```text
┌─ CLI Surface (Prototype) ─────────────────────────┐
│ GitHub Copilot CLI → MCP Servers                   │
│   → wwi-sales-data (Fabric Data Agent HTTP MCP)    │
│   → workiq (@microsoft/workiq MCP)                 │
│   → quota-forecast skill (inline report)           │
└────────────────────────────────────────────────────┘

┌─ M365 Surface (Production) ────────────────────────┐
│ M365 Copilot Chat / Teams → Foundry Agent App      │
│   → Fabric IQ (FabricIQPreviewTool, NL→SQL)        │
│   → WorkIQ (WorkIQPreviewTool, OBO auth)           │
│   → Report Generator (DOCX + OneDrive link)        │
└────────────────────────────────────────────────────┘

Shared backend: Fabric Lakehouse (6 WWI tables)
```

## Data Flow

1. User asks a question (CLI or M365 Copilot)
2. Orchestrator (Copilot CLI or Foundry) selects tools
3. Fabric IQ / Data Agent translates NL→SQL, queries Lakehouse
4. WorkIQ retrieves M365 activity signals (OBO)
5. Report generator produces DOCX with forecast + charts
6. Response returned to user with data + report link

## Key Components

| Component | Purpose | Location |
|---|---|---|
| Fabric Data Agent | NL→SQL over Lakehouse | Fabric portal (deployed) |
| Foundry Agent | Multi-tool orchestration | `src/orchestrator/` |
| Report Generator | DOCX/PPTX with citations | `src/agents/report_generator/` |
| CLI Skills | Copilot CLI prompt templates | `src/cli/skills/` |
| MCP Config | MCP server registry | `src/cli/mcp-config.json` |
