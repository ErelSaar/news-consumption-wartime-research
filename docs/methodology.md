# Methodology

## Research Design

This project uses a **before/after comparative design** with event-window analysis. The study period runs from September 1, 2023 to December 31, 2023, with October 7, 2023 serving as the primary intervention date.

## Data Sources

Three types of data are combined to build a multi-platform picture of news consumption:

1. **Telegram public channel data** — Proxy for real-time platform engagement (messages, views, forwards).
2. **RSS feeds from Israeli news outlets** — Proxy for traditional web news supply and consumption.
3. **Google Trends data** — Proxy for public search interest and information-seeking behavior.

All data in the current version is simulated. See `docs/data_sources.md` for details on future real collection.

## Study Period

| Period | Date Range | Purpose |
|--------|-----------|---------|
| Pre-war baseline | Sep 1 – Oct 6, 2023 | Establish normal activity patterns |
| Attack day | Oct 7, 2023 | Primary event date |
| Early war | Oct 7 – Oct 27, 2023 | Immediate wartime pattern |
| Ground operation | Oct 27 – Dec 31, 2023 | Sustained wartime pattern |

## Before/After Comparison

For each platform and metric, we compare:
- **Before mean**: average daily value for the period before WAR_START (September 1 – October 6)
- **After mean**: average daily value for the period starting from WAR_START (October 7 – December 31)
- **Change ratio**: `after_mean / before_mean`

## Event-Window Spike Analysis

For each key war event, we calculate a spike ratio:

```
spike_ratio = event_window_average / baseline_average
```

Where:
- **Baseline**: 14 days immediately preceding the event date
- **Event window**: Event date through 3 days after (4 days total)

A spike ratio of 2.0 means activity doubled compared to the 14-day baseline.

## Platform Normalization

When comparing platforms with different absolute scales (e.g., raw Telegram views vs. normalized Google Trends values 0–100), we normalize each time series to [0, 1] for visual comparison. Analysis tables use raw values.

## Spike Ratio Calculation

```python
baseline = series[baseline_start : event_date].mean()
event_window = series[event_date : event_date + 3 days].mean()
spike_ratio = event_window / baseline
```

## Limitations of Proxy Metrics

| Metric | What it measures | What it doesn't measure |
|--------|-----------------|------------------------|
| Telegram message count | Content supply | Audience size or real consumption |
| Telegram views | Estimated reach on Telegram | Unique users or cross-platform sharing |
| RSS article count | Publication output | Article reads or time spent |
| Google Trends value | Relative search interest | Absolute search volume |

## Sample Data Design

The simulated data is designed to be:
- **Internally consistent**: Spikes are correlated across platforms, since real crises tend to affect multiple platforms simultaneously.
- **Realistic in scale**: Message counts and view ranges reflect plausible public channel activity.
- **Clearly labeled**: All charts and outputs carry a "simulated data" disclaimer.
- **Replaceable**: The same analysis pipeline runs identically on real collected data.
