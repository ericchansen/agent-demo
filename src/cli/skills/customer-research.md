---
name: Research Customer
description: >
  Research a customer using the web. Returns recent news, earnings data,
  strategy insights, and key metrics with citations.
---

# Research Customer

## What this skill does

Uses Copilot CLI's built-in `web_search` and `web_fetch` tools to investigate
a company from multiple angles — news, financials, strategy, competitive
landscape. Produces a structured summary with citations for every claim.

## How it works

1. Run multiple web searches to cover different angles:
   - `"<customer>" recent news` — latest developments
   - `"<customer>" earnings revenue` — financial health
   - `"<customer>" strategy expansion` — strategic direction
   - `"<customer>" competitors` — competitive landscape
2. For the most promising results, use `web_fetch` to read the full page
   content (not just snippets) for deeper insight.
3. Synthesize findings into a structured report:
   - **Company Overview** — what the company does, market position
   - **Recent News** — notable developments with dates and source URLs
   - **Financial Highlights** — revenue, growth, key metrics
   - **Strategic Direction** — where the company is headed
   - **Competitive Landscape** — key competitors and differentiation
4. Cite every factual claim with its source URL.

## Example invocations

```
Research Tailspin Toys — focus on recent news and expansion
```

```
Research NCR Voyix — earnings, digital transformation strategy, competitors
```

```
What's going on with Contoso Ltd lately?
```

## Prerequisites

- Internet access (Copilot CLI's `web_search` tool must be available)

```
Research Contoso Ltd with a focus on earnings and strategy
```

```
What's the latest news on Adventure Works?
```

## Focus areas

You can optionally specify focus areas to refine the search:

| Focus area   | What it emphasizes                        |
|-------------|-------------------------------------------|
| `news`      | Recent press coverage and announcements    |
| `earnings`  | Financial results and revenue metrics      |
| `strategy`  | Business strategy and competitive moves    |
| `expansion` | New markets, offices, and partnerships     |

## Prerequisites

- `researcher-agent` MCP server available
- `SEARCH_PROVIDER` env var set to `bing`, `tavily`, or `mock` (default: `mock`)
- `SEARCH_API_KEY` env var set if using a live search provider
