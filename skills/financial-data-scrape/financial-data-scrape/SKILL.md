---
name: financial-data-scrape
description: Scrape financial data for a stock ticker from stockanalysis.com and wisesheets.io. Use when the user wants to get/scrape/fetch financial data for a given stock ticker symbol, including overview, financials (income, balance sheet, cash flow), statistics, and PE ratio data.
---

# Financial Data Scraper

Scrape comprehensive financial data for a stock ticker and save it as a structured Markdown file.

## Workflow

### 1. Scrape stockanalysis.com

Use the chrome-mcp-server MCP server to navigate to https://stockanalysis.com/.

1. Search for the provided `{ticker}`.
2. On the main ticker page, scrape the **Overview** section. Ignore the rest of the page.
3. Navigate to the **Financials** page:
   - Scrape the **Income** data table.
   - Click **Balance Sheet** and scrape the data table.
   - Click **Cash Flow** and scrape the data table.
4. Navigate to the **Statistics** page and scrape the main data table.

### 2. Scrape wisesheets.io

For non-US tickers (e.g., EPA:EL, FRA:*, BIT:*, LON:*), do **not** guess the wisesheets ticker format. Instead:

1. Navigate to `https://www.wisesheets.io/pe-ratio/AAPL` (or any valid page).
2. Use the **search bar** to type the company name (e.g., "EssilorLuxottica").
3. Select the correct exchange-specific ticker from the dropdown (e.g., `EL.PA` for Euronext Paris).
4. This will navigate to the correct PE ratio page.

For US tickers, you can navigate directly to `https://www.wisesheets.io/pe-ratio/{ticker}`.

Once on the correct page, scrape:

- Annual Average/Median/Minimum/Maximum PE ratio.
- Annual PE ratio data table (last 10 years).
- 3-year, 5-year, and 10-year PE averages.
- PE Ratio vs. Peers data table.

### 3. Handle 404 errors

If a URL returns a 404 — and **only** in this case — perform a web search to find the correct URL, then return to using the chrome-mcp-server to continue scraping.

### 4. Save the data

If the user has not already specified a file path, ask them where to save the file (suggest `./financial_data/stock_data/{ticker}_{date}.md` as default).

Create the Markdown file with the following sections:

- Overview
- Financials:
  - Income table
  - Balance Sheet table
  - Cash Flow table
- Statistics
- PE ratio data (all scraped tables)

**Formatting rules:**

- Include complete scraped data — do not truncate.
- Preserve table format using standard Markdown tables.
- Preserve bold/italic formatting from the source.
