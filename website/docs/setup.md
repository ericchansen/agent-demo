---
sidebar_position: 5
title: Setup Guide
---

# Setup Guide

See the full [setup guide](https://github.com/ericchansen/agent-demo/blob/main/docs/setup-guide.md) in the repository.

## Quick Start (CLI Surface)

1. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/ericchansen/agent-demo.git
   cd agent-demo
   pip install -r requirements.txt
   ```

2. Add the Fabric Data Agent MCP server to your Copilot CLI config (`~/.copilot/mcp-config.json`):
   ```json
   {
     "mcpServers": {
       "wwi-sales-data": {
         "type": "http",
         "url": "https://api.fabric.microsoft.com/v1/mcp/workspaces/<your-workspace-id>/dataagent"
       }
     }
   }
   ```

3. Start asking questions in Copilot CLI.

## Foundry Surface Setup

See the [full setup guide](https://github.com/ericchansen/agent-demo/blob/main/docs/setup-guide.md) for Azure AI Foundry configuration, Fabric IQ connections, and M365 publishing.
