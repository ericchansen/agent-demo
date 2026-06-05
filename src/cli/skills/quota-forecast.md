---
name: quota-forecast
description: Generate an FY quota forecast for a customer based on trailing 12-month sales data
---

# Quota Forecast Generator

You are generating a fiscal year quota forecast for a Wide World Importers customer.

## Steps

1. **Query sales data**: Use the `wwi-sales-data` MCP server to get the customer's trailing 12-month sales broken down by product category. Example query:
   ```
   What were [customer]'s total sales by product category (StockItem dimension) for the last 12 months? Show each category with total revenue and quantity.
   ```

2. **Calculate projections**: For each product category:
   - Apply a growth rate (default 10-15% for growing accounts, 5% for stable)
   - Project the next fiscal year revenue
   - Note any categories with declining trends

3. **Format the forecast**: Present as a markdown table:
   | Product Category | Current FY Revenue | Growth Rate | Projected FY Revenue |
   |---|---|---|---|
   | Category 1 | $X | Y% | $Z |
   | ... | ... | ... | ... |
   | **Total** | **$X** | **Y%** | **$Z** |

4. **Add insights**:
   - Highlight the top 3 growth categories
   - Flag any declining categories with recommendations
   - Include a methodology note: "Based on trailing 12-month sales trend from the WWI data warehouse"

5. **Summary**: Provide a 2-3 sentence executive summary suitable for a QBR deck.
