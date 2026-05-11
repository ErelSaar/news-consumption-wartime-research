"""
Sample data generator for the wartime news consumption research project.

Generates realistic but entirely simulated datasets covering 2023-09-01 to 2023-12-31.
All data is fictional and intended for portfolio / research workflow demonstration only.
"""

import random
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    STUDY_START, STUDY_END, WAR_START, WAR_EVENTS,
    TELEGRAM_CHANNELS, RSS_SOURCES, RSS_CATEGORIES, TRENDS_KEYWORDS,
    SAMPLE_DIR, FINAL_DIR,
)
from utils import get_logger, save_csv, date_range, normalize_series

logger = get_logger(__name__)

rng = np.random.default_rng(42)  # fixed seed for reproducibility


# ---------------------------------------------------------------------------
# Helper: build a daily multiplier array that spikes around key dates
# ---------------------------------------------------------------------------

def _build_multiplier(dates: pd.DatetimeIndex, events: list[dict]) -> np.ndarray:
    """
    Build a per-day activity multiplier.
    Baseline = 1.0.  Each event injects a decaying spike.
    """
    multipliers = np.ones(len(dates))
    date_index = {d: i for i, d in enumerate(dates.date)}

    for event in events:
        edate = pd.Timestamp(event["event_date"]).date()
        peak = {"attack": 15.0, "military_operation": 6.0,
                "hostage_deal": 5.0, "ceasefire_end": 4.0}.get(event["event_type"], 4.0)
        for lag in range(-1, 14):          # -1 day lead-up, 13 days decay
            d = edate + pd.Timedelta(days=lag).to_pytimedelta()
            if d in date_index:
                decay = peak * np.exp(-0.35 * max(lag, 0))
                multipliers[date_index[d]] = max(multipliers[date_index[d]], decay)

    # Add gentle background noise
    multipliers += rng.uniform(0, 0.15, size=len(multipliers))
    return multipliers


# ---------------------------------------------------------------------------
# 1. War events
# ---------------------------------------------------------------------------

def generate_war_events() -> pd.DataFrame:
    """Create the manually curated war events table."""
    df = pd.DataFrame(WAR_EVENTS)
    out = SAMPLE_DIR / "war_events.csv"
    save_csv(df, out)
    return df


# ---------------------------------------------------------------------------
# 2. Telegram sample data
# ---------------------------------------------------------------------------

_TELEGRAM_TEXTS = [
    "Breaking: Sirens activated in {area}. Residents should enter shelters immediately.",
    "UPDATE: {count} rockets intercepted by Iron Dome over {area}.",
    "IDF announces overnight operations in northern Gaza.",
    "Prime Minister holds emergency security cabinet meeting.",
    "New hostage update: families await news as negotiations continue.",
    "Home Front Command issues updated shelter guidelines for residents.",
    "Massive rally held in Tel Aviv in support of hostage families.",
    "International condemnation grows as humanitarian situation worsens.",
    "Ground forces advance into {area} district according to IDF spokesperson.",
    "Ceasefire negotiations reportedly stalled over key conditions.",
    "Red Alert: Incoming fire detected in {area} region.",
    "LIVE: Watch the latest press conference from the IDF spokesperson.",
    "Exclusive: Behind the scenes of the hostage negotiations.",
    "Hospitals in southern Israel on high alert following rocket fire.",
    "UN Security Council holds emergency session on Israel-Gaza conflict.",
]

_AREAS = ["Tel Aviv", "Ashkelon", "Beer Sheva", "Sderot", "Kiryat Gat", "Ashdod", "Jerusalem"]


def _random_telegram_text() -> str:
    template = random.choice(_TELEGRAM_TEXTS)
    return template.format(area=random.choice(_AREAS), count=random.randint(3, 40))


def generate_telegram_data() -> pd.DataFrame:
    """Generate simulated Telegram channel message data."""
    dates = date_range(STUDY_START, STUDY_END)
    multipliers = _build_multiplier(dates, WAR_EVENTS)

    records = []
    msg_id = 1

    for i, day in enumerate(dates):
        mult = multipliers[i]
        for ch in TELEGRAM_CHANNELS:
            n_messages = max(1, int(rng.poisson(ch["base_messages_per_day"] * mult)))
            for _ in range(n_messages):
                # Spread messages across the day
                hour = rng.integers(0, 24)
                minute = rng.integers(0, 60)
                ts = day + pd.Timedelta(hours=int(hour), minutes=int(minute))

                base_views = rng.integers(500, 8000)
                views = int(base_views * mult * rng.uniform(0.6, 1.4))
                forwards = int(views * rng.uniform(0.01, 0.12))
                replies = int(views * rng.uniform(0.001, 0.03))

                records.append({
                    "platform": "telegram",
                    "source_name": ch["name"],
                    "channel_category": ch["category"],
                    "message_id": msg_id,
                    "published_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "text": _random_telegram_text(),
                    "views": views,
                    "forwards": forwards,
                    "replies": replies,
                    "has_media": bool(rng.integers(0, 2)),
                    "url": f"https://t.me/{ch['name']}/{msg_id}",
                })
                msg_id += 1

    df = pd.DataFrame(records)
    out = SAMPLE_DIR / "telegram_messages.csv"
    save_csv(df, out)
    logger.info(f"Telegram sample: {len(df):,} messages across {df['source_name'].nunique()} channels")
    return df


# ---------------------------------------------------------------------------
# 3. RSS / news website sample data
# ---------------------------------------------------------------------------

_RSS_TITLE_TEMPLATES = {
    "security":      "IDF reports {n} rockets intercepted over {area}",
    "politics":      "Cabinet emergency session addresses {topic}",
    "home_front":    "Home Front Command updates shelter protocols for {area}",
    "hostages":      "Families demand updates on {n} hostages held in Gaza",
    "international": "World leaders react to latest developments in Israel-Gaza war",
    "breaking_news": "BREAKING: Situation escalates as sirens sound in {area}",
}

_TOPICS = ["war cabinet decisions", "ceasefire negotiations", "ground operation", "Hamas leadership", "hostage deal"]


def _rss_title(category: str) -> str:
    template = _RSS_TITLE_TEMPLATES.get(category, "Latest news from Israel")
    return template.format(area=random.choice(_AREAS), n=random.randint(2, 50), topic=random.choice(_TOPICS))


def generate_rss_data() -> pd.DataFrame:
    """Generate simulated RSS / news article data."""
    dates = date_range(STUDY_START, STUDY_END)
    multipliers = _build_multiplier(dates, WAR_EVENTS)

    records = []
    article_id = 1

    for i, day in enumerate(dates):
        mult = multipliers[i]
        for src in RSS_SOURCES:
            n_articles = max(1, int(rng.poisson(src["base_articles_per_day"] * mult)))
            for _ in range(n_articles):
                hour = rng.integers(6, 24)
                minute = rng.integers(0, 60)
                ts = day + pd.Timedelta(hours=int(hour), minutes=int(minute))
                cat = random.choices(
                    RSS_CATEGORIES,
                    weights=[25, 15, 20, 20, 10, 10],  # weighted toward security/home_front/hostages post-war
                    k=1
                )[0]

                records.append({
                    "platform": "rss",
                    "source_name": src["name"],
                    "article_id": article_id,
                    "published_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "title": _rss_title(cat),
                    "summary": f"Simulated article summary for category '{cat}' from {src['name']}.",
                    "category": cat,
                    "url": f"https://{src['name'].lower().replace(' ', '')}.co.il/article/{article_id}",
                })
                article_id += 1

    df = pd.DataFrame(records)
    out = SAMPLE_DIR / "rss_articles.csv"
    save_csv(df, out)
    logger.info(f"RSS sample: {len(df):,} articles across {df['source_name'].nunique()} sources")
    return df


# ---------------------------------------------------------------------------
# 4. Google Trends sample data
# ---------------------------------------------------------------------------

def generate_trends_data() -> pd.DataFrame:
    """Generate simulated Google Trends data (normalized 0–100)."""
    dates = date_range(STUDY_START, STUDY_END)
    multipliers = _build_multiplier(dates, WAR_EVENTS)

    # Keyword-specific sensitivity to the war
    sensitivity = {
        "news": 0.5,
        "siren": 0.9,
        "hostages": 0.95,
        "home front command": 0.85,
        "telegram news": 0.75,
        "Israel news": 0.6,
        "Iran attack": 0.4,
    }

    records = []
    for keyword in TRENDS_KEYWORDS:
        base = rng.uniform(5, 25)
        sens = sensitivity.get(keyword, 0.7)
        raw_values = base + (multipliers - 1) * sens * 80 + rng.uniform(-3, 3, len(dates))
        raw_values = np.clip(raw_values, 0, None)
        normalized = normalize_series(pd.Series(raw_values)).round(1)

        for day, val in zip(dates, normalized):
            records.append({
                "date": day.strftime("%Y-%m-%d"),
                "keyword": keyword,
                "trend_value": val,
                "geo": "IL",
            })

    df = pd.DataFrame(records)
    out = SAMPLE_DIR / "google_trends.csv"
    save_csv(df, out)
    logger.info(f"Google Trends sample: {len(df):,} rows for {df['keyword'].nunique()} keywords")
    return df


# ---------------------------------------------------------------------------
# 5. Unified daily activity dataset
# ---------------------------------------------------------------------------

def generate_unified_daily(
    telegram_df: pd.DataFrame,
    rss_df: pd.DataFrame,
    trends_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build data/final/news_activity_daily.csv from the three sample datasets.
    Schema: date | platform | source_name | metric_name | metric_value
    """
    records = []

    # Telegram: message count and total views per channel per day
    telegram_df["date"] = pd.to_datetime(telegram_df["published_at"]).dt.date.astype(str)
    tg_day = (
        telegram_df.groupby(["date", "source_name"])
        .agg(msg_count=("message_id", "count"), total_views=("views", "sum"))
        .reset_index()
    )
    for _, row in tg_day.iterrows():
        records.append({"date": row["date"], "platform": "telegram",
                        "source_name": row["source_name"],
                        "metric_name": "telegram_message_count",
                        "metric_value": row["msg_count"]})
        records.append({"date": row["date"], "platform": "telegram",
                        "source_name": row["source_name"],
                        "metric_name": "telegram_total_views",
                        "metric_value": row["total_views"]})

    # RSS: article count per source per day
    rss_df["date"] = pd.to_datetime(rss_df["published_at"]).dt.date.astype(str)
    rss_day = (
        rss_df.groupby(["date", "source_name"])
        .agg(article_count=("article_id", "count"))
        .reset_index()
    )
    for _, row in rss_day.iterrows():
        records.append({"date": row["date"], "platform": "rss",
                        "source_name": row["source_name"],
                        "metric_name": "rss_article_count",
                        "metric_value": row["article_count"]})

    # Google Trends: one row per keyword per day
    for _, row in trends_df.iterrows():
        records.append({"date": row["date"], "platform": "google_trends",
                        "source_name": row["keyword"],
                        "metric_name": "google_trend_value",
                        "metric_value": row["trend_value"]})

    df = pd.DataFrame(records)
    out = FINAL_DIR / "news_activity_daily.csv"
    save_csv(df, out)
    logger.info(f"Unified daily dataset: {len(df):,} rows")
    return df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    logger.info("=== Generating all sample data ===")
    generate_war_events()
    tg = generate_telegram_data()
    rss = generate_rss_data()
    trends = generate_trends_data()
    generate_unified_daily(tg, rss, trends)
    logger.info("=== Sample data generation complete ===")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    main()
