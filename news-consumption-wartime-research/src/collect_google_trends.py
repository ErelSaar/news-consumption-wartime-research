"""
Google Trends data collector template.

Uses pytrends (unofficial Google Trends API wrapper).
IMPORTANT: pytrends is unofficial and can be rate-limited or blocked by Google.
Use responsibly with delays between requests.

To enable real collection:
1. pip install pytrends
2. Run: python src/collect_google_trends.py
3. The script will save results to data/raw/google_trends_real.csv

Limitations:
- Values are relative (0–100), not absolute search volumes.
- Geo filter defaults to "IL" (Israel).
- pytrends may stop working if Google changes its interface.
"""

import time
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from utils import get_logger, save_csv
from config import TRENDS_KEYWORDS, RAW_DIR

logger = get_logger(__name__)


def check_pytrends() -> bool:
    """Return True if pytrends is installed."""
    try:
        import pytrends  # noqa: F401
        return True
    except ImportError:
        logger.warning(
            "pytrends is not installed. Run: pip install pytrends\n"
            "Note: pytrends is an unofficial package and may be rate-limited."
        )
        return False


def collect_keyword(
    keyword: str,
    start_date: str,
    end_date: str,
    geo: str = "IL",
    delay_seconds: float = 3.0,
) -> Optional[pd.DataFrame]:
    """
    Collect daily trend data for a single keyword.

    Args:
        keyword: Search term to query.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        geo: Country code (IL = Israel).
        delay_seconds: Polite delay after the request.

    Returns:
        DataFrame with columns [date, keyword, trend_value, geo], or None on failure.
    """
    if not check_pytrends():
        return None

    from pytrends.request import TrendReq

    try:
        pytrends = TrendReq(hl="en-US", tz=120)  # IST = UTC+3, tz param is offset in minutes
        timeframe = f"{start_date} {end_date}"
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo)
        interest_df = pytrends.interest_over_time()
    except Exception as e:
        logger.warning(f"Failed to fetch trends for '{keyword}': {e}")
        return None

    if interest_df.empty:
        logger.warning(f"Empty response for keyword '{keyword}'")
        return None

    interest_df = interest_df.reset_index().rename(columns={keyword: "trend_value", "date": "date"})
    interest_df["keyword"] = keyword
    interest_df["geo"] = geo
    interest_df = interest_df[["date", "keyword", "trend_value", "geo"]]
    interest_df["date"] = interest_df["date"].dt.strftime("%Y-%m-%d")

    logger.info(f"Collected {len(interest_df)} data points for '{keyword}'")
    time.sleep(delay_seconds)
    return interest_df


def collect_all(
    start_date: str = "2023-09-01",
    end_date: str = "2023-12-31",
    geo: str = "IL",
    output_filename: str = "google_trends_real.csv",
) -> None:
    """
    Collect Google Trends data for all configured keywords.

    Args:
        start_date: Study period start.
        end_date: Study period end.
        geo: Country/region code.
        output_filename: Output filename inside data/raw/.
    """
    if not check_pytrends():
        logger.info("Skipping Google Trends collection — pytrends not available.")
        return

    all_dfs = []
    for keyword in TRENDS_KEYWORDS:
        logger.info(f"Querying: '{keyword}'")
        df = collect_keyword(keyword, start_date, end_date, geo)
        if df is not None:
            all_dfs.append(df)

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        out = RAW_DIR / output_filename
        save_csv(combined, out)
        logger.info(f"Saved {len(combined):,} trend data points to {out}")
    else:
        logger.warning("No trend data collected.")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    collect_all()
