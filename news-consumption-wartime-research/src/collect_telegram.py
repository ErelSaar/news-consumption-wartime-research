"""
Telegram public channel data collector template.

IMPORTANT: This module is a template for future real data collection.
It requires Telegram API credentials and the 'telethon' package.
If credentials are missing it prints a clear message and exits gracefully.

To enable real collection:
1. pip install telethon
2. Create a Telegram app at https://my.telegram.org/apps
3. Add TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE to your .env file
4. Replace PUBLIC_CHANNELS with the actual channel usernames you want to monitor

Legal note: Only collect data from public channels. Respect Telegram's ToS.
"""

import logging
from pathlib import Path
from datetime import datetime

from utils import get_logger, save_csv
from config import RAW_DIR, TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE

logger = get_logger(__name__)

# Public channels to monitor (replace with real channel usernames)
PUBLIC_CHANNELS = [
    "idfspokesperson",       # example public channel
    "kann_news",
    "ynet_news",
]


def check_credentials() -> bool:
    """Return True if all required Telegram credentials are present."""
    if not all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE]):
        logger.warning(
            "Telegram credentials not found in .env. "
            "Set TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE to enable real collection. "
            "Falling back to sample data."
        )
        return False
    return True


async def collect_channel_messages(
    client,
    channel_username: str,
    start_date: datetime,
    end_date: datetime,
    limit: int = 500,
) -> list[dict]:
    """
    Collect messages from a single public Telegram channel.
    Returns a list of message record dicts.

    Args:
        client: An authenticated Telethon TelegramClient.
        channel_username: The @username of the public channel.
        start_date: Collect messages from this date (UTC).
        end_date: Collect messages up to this date (UTC).
        limit: Maximum messages to collect per call.
    """
    try:
        from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
    except ImportError:
        logger.error("telethon is not installed. Run: pip install telethon")
        return []

    records = []
    async for message in client.iter_messages(channel_username, limit=limit, offset_date=end_date):
        if message.date.replace(tzinfo=None) < start_date:
            break
        records.append({
            "platform": "telegram",
            "source_name": channel_username,
            "channel_category": "unknown",      # label manually or via channel metadata
            "message_id": message.id,
            "published_at": message.date.strftime("%Y-%m-%d %H:%M:%S"),
            "text": message.text or "",
            "views": message.views or 0,
            "forwards": message.forwards or 0,
            "replies": message.replies.replies if message.replies else 0,
            "has_media": message.media is not None,
            "url": f"https://t.me/{channel_username}/{message.id}",
        })

    logger.info(f"Collected {len(records)} messages from @{channel_username}")
    return records


def collect_all(start_date: str = "2023-09-01", end_date: str = "2023-12-31") -> None:
    """
    Main collection entry point. Runs the async Telegram collection.
    Falls back gracefully if credentials are missing or telethon is not installed.
    """
    if not check_credentials():
        return

    try:
        import asyncio
        from telethon.sync import TelegramClient
    except ImportError:
        logger.error("telethon is not installed. Run: pip install telethon")
        return

    import pandas as pd
    start_dt = pd.Timestamp(start_date).to_pydatetime()
    end_dt = pd.Timestamp(end_date).to_pydatetime()
    all_records = []

    with TelegramClient("session_research", int(TELEGRAM_API_ID), TELEGRAM_API_HASH) as client:
        client.start(phone=TELEGRAM_PHONE)
        for channel in PUBLIC_CHANNELS:
            records = client.loop.run_until_complete(
                collect_channel_messages(client, channel, start_dt, end_dt)
            )
            all_records.extend(records)

    if all_records:
        import pandas as pd
        df = pd.DataFrame(all_records)
        out = RAW_DIR / "telegram_real.csv"
        save_csv(df, out)
        logger.info(f"Saved {len(df):,} real Telegram messages to {out}")
    else:
        logger.warning("No messages collected.")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    collect_all()
