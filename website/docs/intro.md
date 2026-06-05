---
sidebar_position: 1
title: Overview
---

# Fabric Sales Agent Accelerator

An open-source reference implementation showing how to build AI sales agents powered by Microsoft Fabric data. Demonstrates a **two-surface approach**: prototype with GitHub Copilot CLI, then deploy to M365 Copilot + Teams via Azure AI Foundry.

## What It Does

A sales user asks about a customer → the agent:
1. **Queries sales data** via Fabric Data Agent (NL→SQL over a Lakehouse)
2. **Pulls M365 activity** via WorkIQ (emails, meetings, engagement signals)
3. **Generates a report** with FY quota forecast, embedded charts, and citations

## The Two-Surface Approach

| | CLI (Prototype) | M365/Teams (Production) |
|---|---|---|
| **Audience** | Developers, SEs | Business users |
| **Orchestration** | Copilot CLI (built-in) | Azure AI Foundry Agent |
| **Data access** | MCP servers | Platform tools (Fabric IQ, WorkIQ) |
| **Report output** | Inline markdown | DOCX via OneDrive link |
| **Auth** | Interactive OAuth | OBO (on-behalf-of) |

Same backends. Same business logic. Different distribution surfaces.

## Tech Stack

- **Microsoft Fabric** — Lakehouse, Data Agent, Fabric IQ
- **Azure AI Foundry** — Agent Service, Responses API, platform tools
- **MCP** — Model Context Protocol for tool integration
- **Python** — Orchestrator, report generator, custom tools
- **GitHub Copilot CLI** — Developer-facing agent surface
