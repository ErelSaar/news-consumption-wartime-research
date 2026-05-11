# News Consumption During Wartime in Israel

A data research project examining how news consumption patterns shifted following the October 7, 2023 Hamas attack. Built as a portfolio artifact demonstrating data collection, analysis, and research storytelling using Python.

> **Note:** The current version uses entirely simulated data. All outputs are clearly labeled. The pipeline is designed to accept real collected data without modification.

---

## Research Question

**How did news consumption patterns in Israel change during wartime, and what role did fast-moving platforms like Telegram play compared with search interest and traditional news websites?**

---

## Repository Structure

```
news-consumption-wartime-research/
├── README.md
├── project_brief.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/              # Real collected data (gitignored)
│   ├── clean/            # Cleaned outputs
│   ├── final/            # Unified daily dataset
│   └── sample/           # Generated sample data
├── notebooks/
│   ├── 01_generate_sample_data.ipynb
│   ├── 02_collect_data_templates.ipynb
│   ├── 03_clean_and_prepare_data.ipynb
│   ├── 04_exploratory_analysis.ipynb
│   └── 05_final_charts_and_findings.ipynb
├── src/
│   ├── config.py                  # Central config, paths, constants
│   ├── utils.py                   # Shared utilities
│   ├── sample_data_generator.py   # Generates all sample datasets
│   ├── collect_telegram.py        # Telegram collection template
│   ├── collect_rss.py             # RSS collection template
│   ├── collect_google_trends.py   # Google Trends collection template
│   ├── clean_data.py              # Data cleaning pipeline
│   ├── analysis.py                # Research analysis (5 questions)
│   └── visualization.py           # Chart generation
├── outputs/
│   ├── charts/                    # Generated PNG charts
│   ├── tables/                    # Analysis result tables (CSV)
│   └── portfolio_exports/         # JSON manifest + analysis summary
├── portfolio/
│   ├── case_study.md              # Full polished case study
│   ├── portfolio_summary.md       # Short version for personal website
│   └── findings.json              # Structured findings (import-ready)
└── docs/
    ├── methodology.md
    ├── data_sources.md
    ├── limitations.md
    └── future_work.md
```

---

## Quick Start

### 1. Set Up Environment

```bash
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Generate Sample Data

```bash
python src/sample_data_generator.py
```

This creates:
- `data/sample/war_events.csv`
- `data/sample/telegram_messages.csv`
- `data/sample/rss_articles.csv`
- `data/sample/google_trends.csv`
- `data/final/news_activity_daily.csv`

### 3. Clean the Data

```bash
python src/clean_data.py
```

Output goes to `data/clean/`.

### 4. Run Analysis

```bash
python src/analysis.py
```

Output tables go to `outputs/tables/`.

### 5. Generate Charts

```bash
python src/visualization.py
```

Charts go to `outputs/charts/`. The manifest goes to `outputs/portfolio_exports/charts_manifest.json`.

### Run Everything in Sequence

```bash
python src/sample_data_generator.py && \
python src/clean_data.py && \
python src/analysis.py && \
python src/visualization.py
```

---

## How to Run Notebooks

```bash
source .venv/bin/activate
jupyter notebook notebooks/
```

Run notebooks in order:
1. `01_generate_sample_data.ipynb` — Generate all sample data with inline previews
2. `02_collect_data_templates.ipynb` — Review data collection templates
3. `03_clean_and_prepare_data.ipynb` — Run and inspect the cleaning pipeline
4. `04_exploratory_analysis.ipynb` — Explore all five research questions
5. `05_final_charts_and_findings.ipynb` — Generate and display final charts

---

## Data Sources

| Source | Type | Notes |
|--------|------|-------|
| Telegram public channels | Simulated | Template for real collection via Telethon |
| RSS feeds (Israeli news) | Simulated | Template for real collection via feedparser |
| Google Trends | Simulated | Template for real collection via pytrends |
| War events | Manually curated | Based on public news records |

---

## Methodology

The analysis uses a **before/after comparative design** centered on October 7, 2023.

**Before/after comparison:** Average daily activity is compared between September 1 – October 6 (pre-war baseline) and October 7 – December 31 (wartime period).

**Spike ratio:** For each war event:
```
spike_ratio = event_window_average / baseline_average
```
- Baseline: 14 days before the event
- Event window: Event date + 3 days

See `docs/methodology.md` for full details.

---

## Outputs

### Charts (`outputs/charts/`)

| File | Description |
|------|-------------|
| `daily_activity_timeline.png` | Normalized daily activity across all platforms |
| `google_trends_keywords.png` | Search interest per keyword over time |
| `telegram_views_over_time.png` | Daily Telegram views stacked by channel |
| `rss_articles_by_source.png` | Daily article volume stacked by source |
| `event_impact_spike_ratio.png` | Spike ratios for each war event |
| `platform_comparison.png` | Platform-level spike ratio comparison |

### Analysis Tables (`outputs/tables/`)

| File | Description |
|------|-------------|
| `q1_before_after.csv` | Before/after daily averages and change ratios |
| `q2_platform_spike.csv` | Platform spike ratios (first 7 days post Oct 7) |
| `q3_event_spikes.csv` | Event-level spike ratios for all events |
| `q4_telegram_top_sources.csv` | Telegram channel ranking by activity |
| `q4_rss_top_sources.csv` | RSS source ranking by article count |
| `q5_topic_dominance.csv` | Topic growth ratios before and after Oct 7 |

### Portfolio Exports (`outputs/portfolio_exports/`)

| File | Description |
|------|-------------|
| `charts_manifest.json` | Chart metadata with titles, insights, and portfolio sections |
| `analysis_summary.json` | Key numeric findings for programmatic use |

---

## Portfolio Usage

1. Copy charts from `outputs/charts/` to your website's image directory.
2. Use `portfolio/case_study.md` as the basis for a project page.
3. Import `portfolio/findings.json` into a website component (React, Vue, static HTML).
4. Use `outputs/portfolio_exports/charts_manifest.json` to dynamically populate a chart gallery.
5. Use `portfolio/portfolio_summary.md` as a short project card.

---

## Replacing Sample Data with Real Data

### Telegram
1. `pip install telethon`
2. Get credentials at https://my.telegram.org/apps
3. Add to `.env`:
   ```
   TELEGRAM_API_ID=your_id
   TELEGRAM_API_HASH=your_hash
   TELEGRAM_PHONE=+your_phone
   ```
4. Run: `python src/collect_telegram.py`
5. Then run: `python src/clean_data.py real`

### RSS Feeds
1. Run: `python src/collect_rss.py`
2. Output goes to `data/raw/rss_real.csv`
3. Then run: `python src/clean_data.py real`

### Google Trends
1. `pip install pytrends`
2. Run: `python src/collect_google_trends.py`
3. Output goes to `data/raw/google_trends_real.csv`
4. Then run: `python src/clean_data.py real`

After replacing data, re-run the full pipeline (steps 3–5 from Quick Start).

---

## Limitations

- All current data is simulated — no real-world conclusions should be drawn
- Telegram public channels are not representative of the full Israeli audience
- Google Trends values are relative (0–100), not absolute search volumes
- RSS volume measures content supply, not audience consumption
- Television and radio (primary broadcast channels) are absent from this analysis

See `docs/limitations.md` for the full list.

---

## Future Work

- Replace simulated data with real Telegram public channel collection
- Add real Google Trends exports (Hebrew and English keywords)
- Add YouTube news channel data
- Build a Streamlit interactive dashboard
- Create a portfolio website page with interactive chart embeds

See `docs/future_work.md` for full roadmap.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| pandas | Data processing |
| numpy | Numerical operations |
| matplotlib | Chart generation |
| Jupyter | Interactive exploration |
| feedparser | RSS collection |
| python-dotenv | Environment configuration |

---

## Origin

This project was inspired by a personal Telegram news bot that aggregated breaking news from Israeli public channels. The bot's behavior during October 7, 2023 — and the overwhelming volume of updates that day — raised the question this project attempts to answer systematically.
