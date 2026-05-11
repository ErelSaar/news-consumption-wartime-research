# Limitations

## 1. Simulated Data

The current version uses entirely simulated data. No conclusions about real-world behavior should be drawn from this version of the project. The sample data is designed to demonstrate the research workflow and produce visually meaningful patterns, not to document actual news consumption behavior.

When replaced with real data, the same analytical code will run without modification.

## 2. Platform Coverage

The three platforms studied (Telegram, RSS/news websites, Google Search) do not represent all news consumption channels. Missing channels include:

- **Television** — TV ratings data in Israel is proprietary and not publicly available.
- **Radio** — Similarly proprietary.
- **Print / paid subscriptions** — Paywall-protected content is not accessible via public APIs.
- **Social media (Twitter/X, Facebook, TikTok)** — API access has become severely restricted or costly.
- **WhatsApp** — Private by design; no data is accessible.

## 3. Telegram Coverage

Even with real Telegram data:
- Only public channels can be legally and technically collected.
- Private groups, which may be significant during crises, are inaccessible.
- View counts are channel-level estimates and do not represent unique users.
- Forwarding behavior across groups creates double-counting in view metrics.

## 4. Google Trends Limitations

- Values are relative to the peak within the requested time period (not absolute).
- The geo filter `IL` includes all searches from Israel, regardless of language or demographics.
- Not all searches are sampled — Google Trends uses a sample of all search queries.
- Hebrew-language search terms would capture a different audience segment than English terms.

## 5. RSS as a Proxy for Consumption

RSS article counts measure the **supply** of published content, not the **demand** (actual reads, time on page, unique visitors). A high article count may reflect editorial decisions to publish more, not necessarily increased audience consumption.

## 6. Correlation vs. Causation

Even with real data, the observed spikes in activity around October 7 reflect correlation with the event date, not a controlled experiment. Many factors changed simultaneously (scale of the attack, media coverage, social mobilization), making it impossible to isolate individual causal drivers.

## 7. Selection Bias in Telegram Channels

The Telegram channels selected for analysis are chosen by the researcher and may not be representative of all Telegram news consumption in Israel. Different channel selections would produce different results.

## 8. Normalization Effects in Google Trends

Because Google Trends values are normalized to the maximum within the query period, the inclusion or exclusion of other periods or keywords can change the relative values significantly. All comparisons should use the same query parameters.
