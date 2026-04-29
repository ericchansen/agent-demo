# Fabric Sales Agent Accelerator

An open-source reference implementation showing how to combine **Microsoft Fabric Data Agent** with agentic AI workflows — surfaced through **progressive architecture tiers** from a simple CLI demo to enterprise multi-agent production.

> **Choose Your Architecture:** This repo demonstrates four tiers — pick the one that fits your team.

## What It Does

A sales user asks a natural language question like *"Prepare an account plan for Tailspin Toys"* and the system:

1. **Queries pipeline data** from Fabric OneLake via the Fabric Data Agent
2. **Researches the customer** on the open web (news, earnings, strategy)
3. **Pulls internal context** from SharePoint (prior proposals, playbooks)
4. **Generates a deliverable** (DOCX or PPTX) from templates with full source citations

## Architecture Tiers

| Tier | Runtime | Deploy | M365 | Status |
|------|---------|--------|------|--------|
| **v1: Copilot CLI** | Standard Copilot license | Local terminal | ❌ | ✅ Implemented |
| **v2: Copilot SDK** | `github-copilot-sdk` | Local app | ❌ | ✅ Implemented |
| **v3: Hosted Agents** | SDK + Docker | Foundry cloud | ✅ | 🔲 Planned |
| **v4: Multi-Agent** | Agent Framework + SDK | Foundry cloud | ✅ | 🔲 Planned |

## Quick Start (v1 — Copilot CLI)

```bash
# 1. Deploy Fabric infrastructure
make infra-deploy

# 2. Load Wide World Importers sample data
make load-data

# 3. Create a Fabric Data Agent in the portal, enable MCP
#    Copy the MCP URL and add it to src/cli/mcp-config.json

# 4. In Copilot CLI, ask:
#    "Prepare an account plan for Tailspin Toys"
```

## Quick Start (v2 — Copilot SDK)

```bash
pip install -e ".[sdk]"

# Set your Fabric MCP URL
export FABRIC_MCP_URL="https://..."

# Run programmatically
python -m src.sdk.cli "Prepare an account plan for Tailspin Toys"
```

## Dataset

Uses **Wide World Importers** — Microsoft's sample database for a wholesale novelty goods distributor. No customer-specific data. See [demo/](demo/) for details.

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Setup Guide](docs/setup-guide.md)
- [Security Model](docs/security-model.md)
- [Cost Model](docs/costs.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
