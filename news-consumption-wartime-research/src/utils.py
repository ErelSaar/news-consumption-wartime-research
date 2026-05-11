"""
Shared utility functions used across the project.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import pandas as pd


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a consistently formatted logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
        )
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def date_range(start: str, end: str) -> pd.DatetimeIndex:
    """Return a daily DatetimeIndex between start and end (inclusive)."""
    return pd.date_range(start=start, end=end, freq="D")


def save_csv(df: pd.DataFrame, path: Path, index: bool = False) -> None:
    """Save a DataFrame to CSV, creating parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)
    logger = get_logger("utils")
    logger.info(f"Saved {len(df):,} rows to {path}")


def load_csv(path: Path, parse_dates: Optional[list] = None) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Expected file not found: {path}")
    df = pd.read_csv(path, parse_dates=parse_dates or [])
    logger = get_logger("utils")
    logger.info(f"Loaded {len(df):,} rows from {path}")
    return df


def normalize_series(s: pd.Series, low: float = 0.0, high: float = 100.0) -> pd.Series:
    """Min-max normalize a numeric series to [low, high]."""
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series([low] * len(s), index=s.index)
    return low + (s - mn) / (mx - mn) * (high - low)


def days_from_war_start(dates: pd.Series, war_start: str = "2023-10-07") -> pd.Series:
    """Return integer days relative to the war start date."""
    war_dt = pd.Timestamp(war_start)
    return (pd.to_datetime(dates) - war_dt).dt.days
