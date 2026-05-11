# Future Work

## Phase 1 — Connect Real Data (Near Term)

### 1.1 Replace Sample Telegram Data with Real Public Channel Data
- Obtain Telegram API credentials at https://my.telegram.org/apps
- Enable `src/collect_telegram.py` with credentials in `.env`
- Collect messages from selected public channels for the September–December 2023 period (if archived)
- Validate real data against the simulated patterns

### 1.2 Replace Sample Google Trends with Real Exports
- Install `pytrends` and run `src/collect_google_trends.py`
- Alternatively, manually download CSV exports from https://trends.google.com
- Re-run the analysis and charts with real normalized trend values
- Add Hebrew-language keyword variants

### 1.3 Add Live RSS Collection
- Run `src/collect_rss.py` to fetch current articles from configured feeds
- Set up a scheduled run (e.g., cron job or GitHub Actions) to collect going forward
- Build a historical RSS archive using the Wayback Machine CDX API

## Phase 2 — Expand Data Sources

### 2.1 YouTube News Channel Data
- Use the YouTube Data API (free tier) to collect video titles, view counts, and publish dates for Israeli news channels
- Correlate video publication spikes with the same event dates

### 2.2 Survey and Report Integration
- Add data from the Reuters Institute Digital News Report (Israel section) as contextual annotations
- Add Israel Democracy Index public opinion data where available

### 2.3 Multilingual Analysis
- Add Hebrew-language keyword tracking to Google Trends
- Consider Hebrew NLP tools for category classification of Hebrew-language titles

## Phase 3 — Improved Analysis

### 3.1 Statistical Testing
- Replace visual before/after comparisons with formal statistical tests (t-test, Mann-Whitney U)
- Calculate confidence intervals for spike ratios

### 3.2 Time Series Decomposition
- Separate trend, seasonality, and residual components
- Identify whether elevated activity decayed back to a new baseline or continued to rise

### 3.3 Sentiment Analysis
- Apply a lightweight sentiment/topic classifier to RSS article titles and Telegram message text
- Track how emotional tone of coverage evolved over the war period

## Phase 4 — Portfolio Presentation

### 4.1 Interactive Dashboard
- Build a Streamlit or Dash web app using the same data and analysis code
- Allow users to explore the data by date range, platform, and source

### 4.2 Portfolio Website Page
- Embed charts from `outputs/charts/` as static images
- Use `portfolio/findings.json` to populate a dynamic project page
- Write a narrative case study derived from `portfolio/case_study.md`

### 4.3 Shareable Research Post
- Write a public blog post or LinkedIn article summarizing findings
- Include methodology notes and limitations prominently
