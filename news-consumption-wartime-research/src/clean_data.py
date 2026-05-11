"""
Data cleaning pipeline.

Reads raw/sample data, applies cleaning rules, and writes clean outputs
to data/clean/. Can be run as a standalone script.
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np

from utils import get_logger, save_csv, load_csv
from config import SAMPLE_DIR, CLEAN_DIR, STUDY_START, STUDY_END

logger = get_logger(__name__)

STUDY_RANGE = (pd.Timestamp(STUDY_START), pd.Timestamp(STUDY_END))


# ---------------------------------------------------------------------------
# Cleaning helpers
# ---------------------------------------------------------------------------

def _enforce_date_range(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Drop rows outside the study period."""
    df[date_col] = pd.to_datetime(df[date_col])
    mask = (df[date_col] >= STUDY_RANGE[0]) & (df[date_col] <= STUDY_RANGE[1])
    dropped = (~mask).sum()
    if dropped:
        logger.info(f"  Dropped {dropped} rows outside study range.")
    return df[mask].copy()


def _drop_duplicates(df: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=subset, keep="first")
    dropped = before - len(df)
    if dropped:
        logger.info(f"  Dropped {dropped} duplicate rows.")
    return df


def _clean_text(series: pd.Series) -> pd.Series:
    """Strip whitespace and replace empty strings with NaN."""
    return series.str.strip().replace("", pd.NA)


# ---------------------------------------------------------------------------
# Per-dataset cleaning functions
# ---------------------------------------------------------------------------

def clean_telegram(source: str = "sample") -> pd.DataFrame:
    """
    Clean the Telegram messages dataset.
    source: 'sample' uses data/sample/, 'real' uses data/raw/
    """
    logger.info("Cleaning Telegram data...")
    filename = "telegram_messages.csv" if source == "sample" else "telegram_real.csv"
    base_dir = SAMPLE_DIR if source == "sample" else Path(str(SAMPLE_DIR).replace("sample", "raw"))
    df = load_csv(base_dir / filename)

    df = _enforce_date_range(df, "published_at")
    df = _drop_duplicates(df, subset=["message_id"])

    # Clamp negative values
    for col in ["views", "forwards", "replies"]:
        if col in df.columns:
            df[col] = df[col].clip(lower=0).fillna(0).astype(int)

    df["text"] = _clean_text(df["text"].astype(str))
    df["date"] = df["published_at"].dt.date.astype(str)

    out = CLEAN_DIR / "telegram_clean.csv"
    save_csv(df, out)
    return df


def clean_rss(source: str = "sample") -> pd.DataFrame:
    """Clean the RSS articles dataset."""
    logger.info("Cleaning RSS data...")
    filename = "rss_articles.csv" if source == "sample" else "rss_real.csv"
    base_dir = SAMPLE_DIR if source == "sample" else Path(str(SAMPLE_DIR).replace("sample", "raw"))
    df = load_csv(base_dir / filename)

    df = _enforce_date_range(df, "published_at")
    df = _drop_duplicates(df, subset=["article_id"])

    df["title"] = _clean_text(df["title"].astype(str))
    df["summary"] = _clean_text(df["summary"].astype(str))
    df["category"] = df["category"].str.lower().str.strip()
    df["date"] = df["published_at"].dt.date.astype(str)

    out = CLEAN_DIR / "rss_clean.csv"
    save_csv(df, out)
    return df


def clean_trends(source: str = "sample") -> pd.DataFrame:
    """Clean the Google Trends dataset."""
    logger.info("Cleaning Google Trends data...")
    filename = "google_trends.csv" if source == "sample" else "google_trends_real.csv"
    base_dir = SAMPLE_DIR if source == "sample" else Path(str(SAMPLE_DIR).replace("sample", "raw"))
    df = load_csv(base_dir / filename)

    df["date"] = pd.to_datetime(df["date"])
    df = _enforce_date_range(df, "date")
    df["trend_value"] = df["trend_value"].clip(0, 100).fillna(0).round(1)
    df["date"] = df["date"].dt.date.astype(str)

    out = CLEAN_DIR / "trends_clean.csv"
    save_csv(df, out)
    return df


def clean_war_events() -> pd.DataFrame:
    """Load and lightly validate the war events table."""
    logger.info("Loading war events...")
    df = load_csv(SAMPLE_DIR / "war_events.csv")
    df["event_date"] = pd.to_datetime(df["event_date"])
    out = CLEAN_DIR / "war_events_clean.csv"
    save_csv(df, out)
    return df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(source: str = "sample") -> None:
    """
    Run the full cleaning pipeline.

    Args:
        source: 'sample' for generated sample data, 'real' for collected raw data.
    """
    logger.info(f"=== Cleaning pipeline (source='{source}') ===")
    clean_war_events()
    clean_telegram(source)
    clean_rss(source)
    clean_trends(source)
    logger.info("=== Cleaning complete ===")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    source_arg = sys.argv[1] if len(sys.argv) > 1 else "sample"
    main(source=source_arg)
