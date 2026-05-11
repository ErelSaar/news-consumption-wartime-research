"""
RSS news feed collector template.

Fetches articles from public RSS feeds of Israeli news outlets.
Uses feedparser (pure Python, no API key required).
If a feed fails to load, it logs the error and continues.

To run real collection:
1. pip install feedparser requests
2. Verify the feed URLs are active
3. Run: python src/collect_rss.py
"""

import time
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from utils import get_logger, save_csv
from config import RAW_DIR

logger = get_logger(__name__)

# Public RSS feed URLs for Israeli news outlets
# These are example URLs and may change — verify before real collection
RSS_FEEDS = {
    "Ynet":            "https://www.ynet.co.il/Integration/StoryRss2.xml",
    "Times of Israel": "https://www.timesofisrael.com/feed/",
    "Haaretz":         "https://www.haaretz.com/cmlink/1.628752",
    "Mako":            "https://rss.mako.co.il/rss/news-military.xml",
    "N12 News":        "https://www.mako.co.il/rss/31750a2610f26110VgnVCM1000005201000aRCRD.xml",
    "Kan News":        "https://www.kan.org.il/rss/?catid=40",
}


def _parse_date(entry) -> Optional[str]:
    """Try to extract a clean datetime string from an RSS entry."""
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                dt = datetime(*val[:6], tzinfo=timezone.utc)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
    return None


def collect_feed(source_name: str, feed_url: str, article_id_start: int = 1) -> list[dict]:
    """
    Fetch and parse a single RSS feed.

    Args:
        source_name: Human-readable name of the news source.
        feed_url: URL of the RSS/Atom feed.
        article_id_start: Starting integer for article IDs in this batch.

    Returns:
        List of article record dicts.
    """
    try:
        import feedparser
    except ImportError:
        logger.error("feedparser is not installed. Run: pip install feedparser")
        return []

    logger.info(f"Fetching feed: {source_name} — {feed_url}")
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        logger.warning(f"Failed to fetch {source_name}: {e}")
        return []

    if feed.bozo and feed.bozo_exception:
        logger.warning(f"Feed parse warning for {source_name}: {feed.bozo_exception}")

    records = []
    for i, entry in enumerate(feed.entries):
        pub_date = _parse_date(entry)
        records.append({
            "platform": "rss",
            "source_name": source_name,
            "article_id": article_id_start + i,
            "published_at": pub_date,
            "title": getattr(entry, "title", ""),
            "summary": getattr(entry, "summary", "")[:500],
            "category": "uncategorized",    # assign manually or via feed tags
            "url": getattr(entry, "link", ""),
        })

    logger.info(f"  -> {len(records)} articles from {source_name}")
    return records


def collect_all(output_filename: str = "rss_real.csv", delay_seconds: float = 1.5) -> None:
    """
    Collect from all configured RSS feeds and save to data/raw/.

    Args:
        output_filename: Output CSV filename inside data/raw/.
        delay_seconds: Polite delay between feed requests.
    """
    all_records = []
    article_counter = 1

    for source_name, feed_url in RSS_FEEDS.items():
        records = collect_feed(source_name, feed_url, article_id_start=article_counter)
        all_records.extend(records)
        article_counter += len(records)
        time.sleep(delay_seconds)

    if all_records:
        df = pd.DataFrame(all_records)
        out = RAW_DIR / output_filename
        save_csv(df, out)
        logger.info(f"Total: {len(df):,} articles from {df['source_name'].nunique()} sources")
    else:
        logger.warning("No articles collected. Check feed URLs.")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    collect_all()
