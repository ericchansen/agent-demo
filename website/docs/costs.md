---
sidebar_position: 6
title: Costs
---

# Cost Model

| Resource | Monthly Cost | Notes |
|---|---|---|
| Fabric F2 capacity | ~$262 | **Pause when not demoing** to save ~70% |
| Azure OpenAI (gpt-4o) | ~$5–15 | Demo-scale (~50 queries/day) |
| Foundry Agent Service | Per-call | No standing cost for prompt agents |
| Key Vault | &lt;$1 | Negligible |
| Storage | &lt;$1 | Negligible |
| **Total (active)** | **~$270–280/mo** | |
| **Total (paused)** | **~$5–15/mo** | Fabric paused |

## Pause & Resume

```bash
# Pause (stops Fabric billing)
az fabric capacity suspend --resource-group rg-fabric-agent --capacity-name fabricagentdemo

# Resume (~1-2 min)
az fabric capacity resume --resource-group rg-fabric-agent --capacity-name fabricagentdemo
```
