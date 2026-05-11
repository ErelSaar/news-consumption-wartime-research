"""
Research analysis functions.

Answers the five core research questions using the cleaned data.
All results are saved to outputs/tables/.
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from utils import get_logger, save_csv, load_csv
from config import (
    WAR_START, WAR_EVENTS, BASELINE_DAYS, EVENT_WINDOW_DAYS,
    CLEAN_DIR, TABLES_DIR, PORTFOLIO_EXPORTS_DIR,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_all_clean() -> dict[str, pd.DataFrame]:
    """Load all clean datasets. Returns a dict keyed by dataset name."""
    data = {}
    for name, fname in [
        ("telegram", "telegram_clean.csv"),
        ("rss", "rss_clean.csv"),
        ("trends", "trends_clean.csv"),
        ("events", "war_events_clean.csv"),
    ]:
        path = CLEAN_DIR / fname
        if path.exists():
            data[name] = load_csv(path, parse_dates=["published_at"] if "published_at" in fname else [])
        else:
            logger.warning(f"Clean file not found: {path}  (run clean_data.py first)")
    return data


# ---------------------------------------------------------------------------
# Q1: Did activity increase after October 7?
# ---------------------------------------------------------------------------

def q1_before_after_comparison(data: dict) -> pd.DataFrame:
    """
    Compare average daily activity before and after WAR_START.
    Returns a summary DataFrame.
    """
    logger.info("Q1: Before/after comparison...")
    war_dt = pd.Timestamp(WAR_START)
    rows = []

    # Telegram
    tg = data.get("telegram")
    if tg is not None:
        tg["date_dt"] = pd.to_datetime(tg["date"])
        tg_day = tg.groupby("date_dt").agg(messages=("message_id", "count"), total_views=("views", "sum"))
        for metric, col in [("telegram_messages_per_day", "messages"),
                             ("telegram_views_per_day", "total_views")]:
            before = tg_day.loc[tg_day.index < war_dt, col].mean()
            after = tg_day.loc[tg_day.index >= war_dt, col].mean()
            rows.append({"metric": metric, "before_mean": round(before, 1),
                         "after_mean": round(after, 1),
                         "change_ratio": round(after / before, 2) if before else None})

    # RSS
    rss = data.get("rss")
    if rss is not None:
        rss["date_dt"] = pd.to_datetime(rss["date"])
        rss_day = rss.groupby("date_dt").size().rename("articles")
        before = rss_day[rss_day.index < war_dt].mean()
        after = rss_day[rss_day.index >= war_dt].mean()
        rows.append({"metric": "rss_articles_per_day", "before_mean": round(before, 1),
                     "after_mean": round(after, 1),
                     "change_ratio": round(after / before, 2) if before else None})

    # Trends
    trends = data.get("trends")
    if trends is not None:
        trends["date_dt"] = pd.to_datetime(trends["date"])
        tr_day = trends.groupby("date_dt")["trend_value"].mean()
        before = tr_day[tr_day.index < war_dt].mean()
        after = tr_day[tr_day.index >= war_dt].mean()
        rows.append({"metric": "google_trends_avg_value", "before_mean": round(before, 1),
                     "after_mean": round(after, 1),
                     "change_ratio": round(after / before, 2) if before else None})

    df = pd.DataFrame(rows)
    save_csv(df, TABLES_DIR / "q1_before_after.csv")
    logger.info(f"\n{df.to_string(index=False)}")
    return df


# ---------------------------------------------------------------------------
# Q2: Which platform showed the strongest spike?
# ---------------------------------------------------------------------------

def q2_platform_spike(data: dict) -> pd.DataFrame:
    """
    Compare normalized daily activity across platforms around WAR_START.
    Returns platform-level spike summary.
    """
    logger.info("Q2: Platform spike comparison...")
    war_dt = pd.Timestamp(WAR_START)
    window = pd.Timedelta(days=7)
    rows = []

    # Telegram daily messages (normalized to pre-war mean = 1)
    tg = data.get("telegram")
    if tg is not None:
        tg["date_dt"] = pd.to_datetime(tg["date"])
        tg_day = tg.groupby("date_dt").agg(val=("message_id", "count"))["val"]
        baseline = tg_day[tg_day.index < war_dt].mean()
        spike_window = tg_day[(tg_day.index >= war_dt) & (tg_day.index < war_dt + window)].mean()
        rows.append({"platform": "Telegram", "metric": "daily_messages",
                     "baseline_avg": round(baseline, 1), "spike_window_avg": round(spike_window, 1),
                     "spike_ratio": round(spike_window / baseline, 2) if baseline else None})

    # RSS daily articles
    rss = data.get("rss")
    if rss is not None:
        rss["date_dt"] = pd.to_datetime(rss["date"])
        rss_day = rss.groupby("date_dt").size()
        baseline = rss_day[rss_day.index < war_dt].mean()
        spike_window = rss_day[(rss_day.index >= war_dt) & (rss_day.index < war_dt + window)].mean()
        rows.append({"platform": "RSS / News Websites", "metric": "daily_articles",
                     "baseline_avg": round(baseline, 1), "spike_window_avg": round(spike_window, 1),
                     "spike_ratio": round(spike_window / baseline, 2) if baseline else None})

    # Google Trends (average across all keywords)
    trends = data.get("trends")
    if trends is not None:
        trends["date_dt"] = pd.to_datetime(trends["date"])
        tr_day = trends.groupby("date_dt")["trend_value"].mean()
        baseline = tr_day[tr_day.index < war_dt].mean()
        spike_window = tr_day[(tr_day.index >= war_dt) & (tr_day.index < war_dt + window)].mean()
        rows.append({"platform": "Google Trends", "metric": "avg_trend_value",
                     "baseline_avg": round(baseline, 1), "spike_window_avg": round(spike_window, 1),
                     "spike_ratio": round(spike_window / baseline, 2) if baseline else None})

    df = pd.DataFrame(rows).sort_values("spike_ratio", ascending=False)
    save_csv(df, TABLES_DIR / "q2_platform_spike.csv")
    logger.info(f"\n{df.to_string(index=False)}")
    return df


# ---------------------------------------------------------------------------
# Q3: Which events produced the strongest reaction?
# ---------------------------------------------------------------------------

def q3_event_spike_ratios(data: dict) -> pd.DataFrame:
    """
    For each war event, compute:
        spike_ratio = event_window_avg / baseline_avg
    Baseline = 14 days before the event.
    Window = event date + 3 days.
    """
    logger.info("Q3: Event spike ratios...")

    # Build combined daily series (all platforms normalized)
    tg = data.get("telegram")
    rss = data.get("rss")

    tg_day = None
    rss_day = None
    if tg is not None:
        tg["date_dt"] = pd.to_datetime(tg["date"])
        tg_day = tg.groupby("date_dt").agg(val=("message_id", "count"))["val"]
    if rss is not None:
        rss["date_dt"] = pd.to_datetime(rss["date"])
        rss_day = rss.groupby("date_dt").size().rename("val")

    rows = []
    for event in WAR_EVENTS:
        edt = pd.Timestamp(event["event_date"])
        baseline_start = edt - pd.Timedelta(days=BASELINE_DAYS)
        window_end = edt + pd.Timedelta(days=EVENT_WINDOW_DAYS)

        for label, series in [("Telegram", tg_day), ("RSS", rss_day)]:
            if series is None:
                continue
            baseline = series[(series.index >= baseline_start) & (series.index < edt)].mean()
            spike = series[(series.index >= edt) & (series.index <= window_end)].mean()
            ratio = round(spike / baseline, 2) if baseline and baseline > 0 else None
            rows.append({
                "event_name": event["event_name"],
                "event_date": event["event_date"],
                "platform": label,
                "baseline_avg": round(baseline, 1) if baseline else None,
                "event_window_avg": round(spike, 1) if spike else None,
                "spike_ratio": ratio,
            })

    df = pd.DataFrame(rows).sort_values(["event_date", "platform"])
    save_csv(df, TABLES_DIR / "q3_event_spikes.csv")
    logger.info(f"\n{df.to_string(index=False)}")
    return df


# ---------------------------------------------------------------------------
# Q4: Which sources were most active?
# ---------------------------------------------------------------------------

def q4_top_sources(data: dict) -> dict[str, pd.DataFrame]:
    """
    Rank Telegram channels and RSS sources by total activity.
    Returns {'telegram': df, 'rss': df}.
    """
    logger.info("Q4: Top sources by activity...")
    results = {}

    tg = data.get("telegram")
    if tg is not None:
        tg_src = (
            tg.groupby("source_name")
            .agg(total_messages=("message_id", "count"),
                 total_views=("views", "sum"),
                 avg_views_per_msg=("views", "mean"))
            .round(1)
            .sort_values("total_messages", ascending=False)
            .reset_index()
        )
        save_csv(tg_src, TABLES_DIR / "q4_telegram_top_sources.csv")
        results["telegram"] = tg_src
        logger.info(f"Telegram sources:\n{tg_src.to_string(index=False)}")

    rss = data.get("rss")
    if rss is not None:
        rss_src = (
            rss.groupby("source_name")
            .agg(total_articles=("article_id", "count"))
            .sort_values("total_articles", ascending=False)
            .reset_index()
        )
        save_csv(rss_src, TABLES_DIR / "q4_rss_top_sources.csv")
        results["rss"] = rss_src
        logger.info(f"RSS sources:\n{rss_src.to_string(index=False)}")

    return results


# ---------------------------------------------------------------------------
# Q5: Which topics became more dominant?
# ---------------------------------------------------------------------------

def q5_topic_dominance(data: dict) -> pd.DataFrame:
    """
    Compare category/keyword distribution before and after WAR_START.
    Uses RSS categories and Google Trends keywords.
    """
    logger.info("Q5: Topic dominance shifts...")
    war_dt = pd.Timestamp(WAR_START)
    rows = []

    # RSS categories
    rss = data.get("rss")
    if rss is not None:
        rss["date_dt"] = pd.to_datetime(rss["date"])
        for cat in rss["category"].unique():
            subset = rss[rss["category"] == cat]
            before = len(subset[subset["date_dt"] < war_dt])
            after = len(subset[subset["date_dt"] >= war_dt])
            total_before_days = len(pd.date_range(start="2023-09-01", end="2023-10-06"))
            total_after_days = len(pd.date_range(start="2023-10-07", end="2023-12-31"))
            rows.append({
                "source": "RSS",
                "topic": cat,
                "before_per_day": round(before / total_before_days, 2),
                "after_per_day": round(after / total_after_days, 2),
                "growth_ratio": round((after / total_after_days) / (before / total_before_days), 2)
                if before > 0 else None,
            })

    # Google Trends keywords
    trends = data.get("trends")
    if trends is not None:
        trends["date_dt"] = pd.to_datetime(trends["date"])
        for kw in trends["keyword"].unique():
            subset = trends[trends["keyword"] == kw]
            before_avg = subset[subset["date_dt"] < war_dt]["trend_value"].mean()
            after_avg = subset[subset["date_dt"] >= war_dt]["trend_value"].mean()
            rows.append({
                "source": "Google Trends",
                "topic": kw,
                "before_per_day": round(before_avg, 2),
                "after_per_day": round(after_avg, 2),
                "growth_ratio": round(after_avg / before_avg, 2) if before_avg > 0 else None,
            })

    df = pd.DataFrame(rows).sort_values("growth_ratio", ascending=False).reset_index(drop=True)
    save_csv(df, TABLES_DIR / "q5_topic_dominance.csv")
    logger.info(f"\n{df.head(10).to_string(index=False)}")
    return df


# ---------------------------------------------------------------------------
# Summary JSON for portfolio
# ---------------------------------------------------------------------------

def build_findings_summary(
    q1: pd.DataFrame,
    q2: pd.DataFrame,
    q3: pd.DataFrame,
) -> dict:
    """Extract key numeric findings for the portfolio JSON."""
    findings = {}

    # Q1
    if not q1.empty:
        tg_row = q1[q1["metric"] == "telegram_messages_per_day"]
        if not tg_row.empty:
            findings["telegram_message_increase_ratio"] = float(tg_row.iloc[0]["change_ratio"])
        rss_row = q1[q1["metric"] == "rss_articles_per_day"]
        if not rss_row.empty:
            findings["rss_article_increase_ratio"] = float(rss_row.iloc[0]["change_ratio"])

    # Q2 — strongest platform
    if not q2.empty:
        top = q2.iloc[0]
        findings["strongest_platform_spike"] = {
            "platform": top["platform"],
            "spike_ratio": float(top["spike_ratio"]) if top["spike_ratio"] else None,
        }

    # Q3 — highest spike event
    if not q3.empty:
        top_event = q3.sort_values("spike_ratio", ascending=False).iloc[0]
        findings["highest_spike_event"] = {
            "event": top_event["event_name"],
            "platform": top_event["platform"],
            "spike_ratio": float(top_event["spike_ratio"]) if top_event["spike_ratio"] else None,
        }

    return findings


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    logger.info("=== Running analysis pipeline ===")
    data = load_all_clean()
    if not data:
        logger.error("No clean data found. Run clean_data.py first.")
        return

    q1 = q1_before_after_comparison(data)
    q2 = q2_platform_spike(data)
    q3 = q3_event_spike_ratios(data)
    q4_top_sources(data)
    q5_topic_dominance(data)

    summary = build_findings_summary(q1, q2, q3)
    summary_path = PORTFOLIO_EXPORTS_DIR / "analysis_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Analysis summary saved to {summary_path}")
    logger.info("=== Analysis complete ===")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    main()
