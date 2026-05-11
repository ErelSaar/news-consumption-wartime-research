"""
Central configuration for the research project.
Loads environment variables and defines shared constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
FINAL_DIR = DATA_DIR / "final"
SAMPLE_DIR = DATA_DIR / "sample"
OUTPUTS_DIR = ROOT_DIR / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"
TABLES_DIR = OUTPUTS_DIR / "tables"
PORTFOLIO_EXPORTS_DIR = OUTPUTS_DIR / "portfolio_exports"
PORTFOLIO_DIR = ROOT_DIR / "portfolio"

# Ensure output directories exist at import time
for _dir in [RAW_DIR, CLEAN_DIR, FINAL_DIR, SAMPLE_DIR, CHARTS_DIR, TABLES_DIR, PORTFOLIO_EXPORTS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

# --- Research period ---
STUDY_START = "2023-09-01"
STUDY_END = "2023-12-31"
WAR_START = "2023-10-07"          # October 7 attack
BASELINE_DAYS = 14                 # days before event used as baseline
EVENT_WINDOW_DAYS = 3              # days after event included in spike window

# --- Key events ---
WAR_EVENTS = [
    {
        "event_date": "2023-10-07",
        "event_name": "October 7 Attack",
        "event_type": "attack",
        "description": "Hamas launched a large-scale surprise attack from Gaza into southern Israel.",
    },
    {
        "event_date": "2023-10-27",
        "event_name": "Ground Operation Begins",
        "event_type": "military_operation",
        "description": "Israel launched a ground operation inside Gaza.",
    },
    {
        "event_date": "2023-11-24",
        "event_name": "First Hostage Release Deal Begins",
        "event_type": "hostage_deal",
        "description": "A temporary ceasefire and initial hostage release deal took effect.",
    },
    {
        "event_date": "2023-12-01",
        "event_name": "Temporary Ceasefire Ends",
        "event_type": "ceasefire_end",
        "description": "The temporary ceasefire expired and fighting resumed.",
    },
]

# --- Simulated Telegram channels ---
TELEGRAM_CHANNELS = [
    {"name": "IsraelNewsLive", "category": "breaking_news", "base_messages_per_day": 30},
    {"name": "GazaUpdates", "category": "military", "base_messages_per_day": 25},
    {"name": "HomeFrontAlerts", "category": "home_front", "base_messages_per_day": 20},
    {"name": "HostageFamilies", "category": "hostages", "base_messages_per_day": 10},
    {"name": "ILPoliticsChannel", "category": "politics", "base_messages_per_day": 15},
    {"name": "InternationalIsrael", "category": "international", "base_messages_per_day": 18},
]

# --- Simulated RSS sources ---
RSS_SOURCES = [
    {"name": "Ynet", "base_articles_per_day": 40},
    {"name": "Haaretz", "base_articles_per_day": 25},
    {"name": "Times of Israel", "base_articles_per_day": 35},
    {"name": "Mako", "base_articles_per_day": 30},
    {"name": "N12 News", "base_articles_per_day": 28},
    {"name": "Kan News", "base_articles_per_day": 22},
]

RSS_CATEGORIES = ["security", "politics", "home_front", "hostages", "international", "breaking_news"]

# --- Google Trends keywords ---
TRENDS_KEYWORDS = [
    "news",
    "siren",
    "hostages",
    "home front command",
    "telegram news",
    "Israel news",
    "Iran attack",
]

# --- Optional API credentials (loaded from .env) ---
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
