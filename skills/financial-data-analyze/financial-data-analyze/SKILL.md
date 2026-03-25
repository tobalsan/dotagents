---
name: financial-data-analyze
description: Analyze existing financial/stock data and produce an investment analysis report. Use when the user wants to run fundamental analysis (FA) for a stock, analyze financial data, evaluate a stock's investment potential, or generate a financial analysis report (markdown, HTML, or PDF).
---

# Financial Data Analyst

Analyze scraped financial data for a stock and produce an actionable investment analysis report.

## Workflow

### 1. Load data

Read the stock data file. If the user specifies a path, use it. Otherwise, look in `./financial_data/stock_data/` for a matching `{ticker}_*.md` file. If multiple matches exist, ask which one to use.

### 2. Analyze

Perform the following analyses on the loaded data:

- **Valuation:** Compare current/forward PE ratio to historical averages and sector peers. Assess Operating Cash Flow ratio vs. historical values. Flag potential undervaluation (buy signal: current/forward PE below 5-year average).
- **DCF Model:** Run a quick discounted cash flow model.
- **Growth Metrics:** Evaluate Revenue CAGR, YoY Revenue Growth, and EPS Growth.
- **Cash Flow Health:** Assess Net Income, Free Cash Flow (FCF), and Gross Profit Growth trends.
- **Financial Health:** Evaluate cash position and balance sheet strength.

### 3. Output

Ask the user for their preferred output format if not already specified: **Markdown**, **HTML**, or **PDF**.

If the user has not specified an output path, ask where to save (suggest `./financial_data/analysis/{ticker}_FA_{date}.{ext}` as default).

**Format rules:**

- **Markdown:** Use advanced Markdown syntax for clean, structured analysis.
- **HTML:** Create a beautifully crafted interactive report. Use chart.js for visuals.
- **PDF:** Use the PDF skill to create a professional report with charts and graphs.
