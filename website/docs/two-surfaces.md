---
sidebar_position: 3
title: CLI ↔ Foundry
---

# The Two-Surface Approach

## Why Two Surfaces?

Building an AI agent is iterative. You need fast feedback loops during development, but enterprise distribution for business users. This accelerator demonstrates both:

- **GitHub Copilot CLI** — Zero infrastructure. Connect MCP servers, write skills, iterate in your terminal. Perfect for prototyping and SE demos.
- **Azure AI Foundry → M365/Teams** — Same backends registered as Foundry platform tools. Published as an Agent Application with Entra identity, RBAC, and enterprise distribution.

## Translation Mapping

| Capability | CLI (MCP Server) | Foundry (Platform Tool) | Same Backend? |
|---|---|---|---|
| Sales data queries | `wwi-sales-data` HTTP MCP | `FabricIQPreviewTool` | ✅ Same Data Agent |
| M365 activity | `@microsoft/workiq` MCP | `WorkIQPreviewTool` | ✅ Same WorkIQ service |
| Report generation | CLI skill (markdown) | Custom function + OneDrive | ✅ Same `generator.py` |
| Orchestration | Copilot CLI (built-in) | Foundry Responses API | Different — CLI is zero-code |

## From Prototype to Production

```text
Step 1: Build & test MCP servers locally
  └─ Copilot CLI discovers tools automatically
  └─ Fast iteration, no deployment needed

Step 2: Register same backends as Foundry tools  
  └─ FabricIQPreviewTool wraps the Data Agent MCP URL
  └─ WorkIQPreviewTool wraps WorkIQ via A2A protocol
  └─ Custom functions wrap report generator logic

Step 3: Publish Foundry Agent → M365/Teams
  └─ Agent Application with stable endpoint
  └─ Entra identity + RBAC
  └─ Users @mention the agent in M365 Copilot Chat
```
