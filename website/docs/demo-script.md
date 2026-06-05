---
sidebar_position: 4
title: Demo Script
---

# Demo Script — NCR Voyix QBR Prep

## Scene
You're an Account Executive at Wide World Importers preparing for a Quarterly Business Review with Tailspin Toys. You need a quota forecast brief.

## Act 1 — CLI Prototype (Developer Audience)

> "Let's start where every agent begins — prototyping with Copilot CLI."

**Query 1: Sales Data**
```
@wwi-sales-data What were Tailspin Toys' total sales by product category for the last 12 months?
```
*Expected: Agent queries Fabric Data Agent → returns sales breakdown table*

**Query 2: Quota Forecast**
```
Based on that data, generate a quota forecast for Tailspin Toys for FY27
```
*Expected: Agent calls forecast skill → produces inline markdown report with projections*

> "That's the prototype. Same MCP servers, zero custom orchestration code. Now let's see this in the business user's world."

## Act 2 — M365 Copilot (Business User Audience)

> "Same agent, now published to M365 Copilot via Azure AI Foundry."

**Query 1: Customer Brief**
```
@WWISalesAgent Brief me on Tailspin Toys — what's our recent engagement and sales activity?
```
*Expected: Agent pulls Fabric sales data + WorkIQ activity data → combined summary*

**Query 2: Forecast Report**
```
@WWISalesAgent Generate an FY27 quota forecast report for Tailspin Toys
```
*Expected: Agent generates DOCX → uploads to OneDrive → returns download link*

> "Same Data Agent backend. But now with M365 identity, WorkIQ activity context, and a downloadable report."

## Fallback Table

| Failure | Recovery |
|---|---|
| Cross-tenant OAuth prompt | Pre-auth all surfaces 10 min before demo |
| WorkIQ not responding | Show pre-cached activity summary |
| Agent not visible in M365 | Use Foundry playground instead |
| DOCX upload fails | Show pre-generated DOCX from local run |
| Fabric capacity paused | Resume 15 min before: `az fabric capacity resume` |
