# News Consumption During Wartime in Israel — Portfolio Summary

## Project

**Research project** | Python, Pandas, Matplotlib, Jupyter | Sep–Dec 2023 (study period)

## What I Built

A data research pipeline investigating how news consumption patterns in Israel changed following the October 7, 2023 attack. The project combines three data sources — Telegram public channel metrics, RSS news feeds, and Google Trends — to build a multi-platform picture of information-seeking behavior during a sustained crisis.

## Research Question

How did news consumption patterns in Israel change during wartime, and what role did fast-moving platforms like Telegram play compared with search interest and traditional news websites?

## What I Did

- Designed and implemented a full research pipeline: data generation, cleaning, analysis, and visualization
- Built sample data generators that simulate realistic activity patterns around key war events
- Wrote collector templates for Telegram (via Telethon), RSS feeds (via feedparser), and Google Trends (via pytrends)
- Implemented five research analyses answering: before/after comparison, platform spike ranking, event-level spike ratios, source activity ranking, and topic dominance shifts
- Generated six portfolio-ready charts with consistent styling and clear "simulated data" labeling
- Wrote structured portfolio outputs (JSON, Markdown) for embedding in a personal website

## Tools Used

Python · Pandas · NumPy · Matplotlib · Jupyter · feedparser · python-dotenv

## Key Findings (Simulated Data)

- All platforms showed sharp activity spikes within 24 hours of October 7
- Telegram (real-time platform) showed the highest spike ratio in the simulation
- Activity remained elevated for the full study period — not just around the attack date
- Security, home front, and hostage categories grew fastest in news coverage
- Keywords like "siren" and "hostages" showed the sharpest search interest growth

## Status

Portfolio-ready research workflow · Sample data version complete · Real data collection templates included

## Origin

Inspired by a personal Telegram news bot I built that aggregated breaking news from Israeli public channels — which led to the broader question of how platform choice and news consumption shift during emergencies.
