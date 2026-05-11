"""
Chart generation module.

Generates all portfolio-ready charts and saves them to outputs/charts/.
Also writes outputs/portfolio_exports/charts_manifest.json.
"""

import json
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for script execution
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from utils import get_logger, load_csv
from config import (
    WAR_EVENTS, WAR_START,
    CLEAN_DIR, CHARTS_DIR, TABLES_DIR, PORTFOLIO_EXPORTS_DIR,
)

logger = get_logger(__name__)

# --- Shared style ---
STYLE = {
    "figure.figsize": (12, 5),
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
}
plt.rcParams.update(STYLE)

WAR_COLOR = "#d62728"          # red for Oct 7 line
EVENT_COLORS = {
    "attack": "#d62728",
    "military_operation": "#ff7f0e",
    "hostage_deal": "#2ca02c",
    "ceasefire_end": "#9467bd",
}
PLATFORM_COLORS = {
    "Telegram": "#229ED9",
    "RSS / News Websites": "#E63946",
    "Google Trends": "#2ca02c",
}


def _add_event_lines(ax, events: list[dict], y_pos_frac: float = 0.92) -> None:
    """Draw vertical lines and labels for war events on an axis."""
    ymin, ymax = ax.get_ylim()
    y_label = ymin + (ymax - ymin) * y_pos_frac
    for event in events:
        edt = pd.Timestamp(event["event_date"])
        color = EVENT_COLORS.get(event["event_type"], "#888888")
        ax.axvline(edt, color=color, linewidth=1.4, linestyle="--", alpha=0.8)
        ax.text(edt, y_label, event["event_name"].replace(" ", "\n"),
                fontsize=7.5, color=color, ha="left", va="top",
                rotation=0, bbox=dict(fc="white", alpha=0.6, edgecolor="none", pad=1))


def _save(fig, filename: str) -> Path:
    path = CHARTS_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved chart: {path}")
    return path


# ---------------------------------------------------------------------------
# 1. Daily activity timeline
# ---------------------------------------------------------------------------

def chart_daily_activity_timeline() -> Path:
    """All-platform normalized daily activity with event markers."""
    # Load data
    tg = load_csv(CLEAN_DIR / "telegram_clean.csv")
    rss = load_csv(CLEAN_DIR / "rss_clean.csv")
    trends = load_csv(CLEAN_DIR / "trends_clean.csv")

    tg["date_dt"] = pd.to_datetime(tg["date"])
    rss["date_dt"] = pd.to_datetime(rss["date"])
    trends["date_dt"] = pd.to_datetime(trends["date"])

    tg_day = tg.groupby("date_dt").size()
    rss_day = rss.groupby("date_dt").size()
    tr_day = trends.groupby("date_dt")["trend_value"].mean()

    # Normalize each to 0–1
    def norm01(s):
        return (s - s.min()) / (s.max() - s.min())

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(norm01(tg_day).index, norm01(tg_day).values,
            label="Telegram (messages)", color=PLATFORM_COLORS["Telegram"], linewidth=1.8, alpha=0.85)
    ax.plot(norm01(rss_day).index, norm01(rss_day).values,
            label="RSS / News websites (articles)", color=PLATFORM_COLORS["RSS / News Websites"],
            linewidth=1.8, alpha=0.85)
    ax.plot(norm01(tr_day).index, norm01(tr_day).values,
            label="Google Trends (avg search interest)", color=PLATFORM_COLORS["Google Trends"],
            linewidth=1.8, alpha=0.85)

    ax.axvline(pd.Timestamp(WAR_START), color=WAR_COLOR, linewidth=2.5, linestyle="-", label="Oct 7 Attack")
    ax.set_ylim(-0.05, 1.2)
    _add_event_lines(ax, WAR_EVENTS[1:], y_pos_frac=0.88)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax.set_xlabel("Date (Sep–Dec 2023)")
    ax.set_ylabel("Normalized activity (0–1)")
    ax.set_title("Daily News Activity Across Platforms — Simulated Data, Sep–Dec 2023", fontweight="bold")
    ax.legend(loc="upper left", framealpha=0.8)
    fig.text(0.99, 0.01, "Note: All data is simulated for portfolio demonstration.",
             ha="right", fontsize=8, color="gray", style="italic")

    return _save(fig, "daily_activity_timeline.png")


# ---------------------------------------------------------------------------
# 2. Google Trends keywords
# ---------------------------------------------------------------------------

def chart_google_trends_keywords() -> Path:
    """Line chart of individual keyword trend values over time."""
    trends = load_csv(CLEAN_DIR / "trends_clean.csv")
    trends["date_dt"] = pd.to_datetime(trends["date"])

    keywords = trends["keyword"].unique()
    cmap = matplotlib.colormaps.get_cmap("tab10").resampled(len(keywords))

    fig, ax = plt.subplots(figsize=(13, 6))
    for i, kw in enumerate(keywords):
        subset = trends[trends["keyword"] == kw].sort_values("date_dt")
        ax.plot(subset["date_dt"], subset["trend_value"],
                label=kw, color=cmap(i), linewidth=1.6, alpha=0.85)

    ax.axvline(pd.Timestamp(WAR_START), color=WAR_COLOR, linewidth=2.5, linestyle="-",
               label="Oct 7 Attack", zorder=5)
    ax.set_ylim(-2, 110)
    _add_event_lines(ax, WAR_EVENTS[1:], y_pos_frac=0.90)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax.set_xlabel("Date")
    ax.set_ylabel("Trend value (0–100, relative)")
    ax.set_title("Google Trends Search Interest by Keyword — Simulated Data (Israel)", fontweight="bold")
    ax.legend(loc="upper left", framealpha=0.8, fontsize=9)
    fig.text(0.99, 0.01, "Note: All data is simulated for portfolio demonstration.",
             ha="right", fontsize=8, color="gray", style="italic")

    return _save(fig, "google_trends_keywords.png")


# ---------------------------------------------------------------------------
# 3. Telegram views over time
# ---------------------------------------------------------------------------

def chart_telegram_views() -> Path:
    """Daily total Telegram views stacked by channel."""
    tg = load_csv(CLEAN_DIR / "telegram_clean.csv")
    tg["date_dt"] = pd.to_datetime(tg["date"])

    pivot = (
        tg.groupby(["date_dt", "source_name"])["views"]
        .sum()
        .unstack(fill_value=0)
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(13, 5))
    cmap = matplotlib.colormaps.get_cmap("tab10").resampled(len(pivot.columns))
    bottom = np.zeros(len(pivot))
    for i, col in enumerate(pivot.columns):
        ax.bar(pivot.index, pivot[col].values / 1000,
               bottom=bottom / 1000, label=col, color=cmap(i), alpha=0.85, width=0.9)
        bottom += pivot[col].values

    ax.axvline(pd.Timestamp(WAR_START), color=WAR_COLOR, linewidth=2.5, linestyle="-",
               label="Oct 7 Attack", zorder=5)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total views (thousands)")
    ax.set_title("Daily Telegram Views by Channel — Simulated Data, Sep–Dec 2023", fontweight="bold")
    ax.legend(loc="upper left", framealpha=0.8, fontsize=9, ncol=2)
    fig.text(0.99, 0.01, "Note: All data is simulated for portfolio demonstration.",
             ha="right", fontsize=8, color="gray", style="italic")

    return _save(fig, "telegram_views_over_time.png")


# ---------------------------------------------------------------------------
# 4. RSS articles by source
# ---------------------------------------------------------------------------

def chart_rss_articles_by_source() -> Path:
    """Daily article count stacked by news source."""
    rss = load_csv(CLEAN_DIR / "rss_clean.csv")
    rss["date_dt"] = pd.to_datetime(rss["date"])

    pivot = (
        rss.groupby(["date_dt", "source_name"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(13, 5))
    cmap = matplotlib.colormaps.get_cmap("Set2").resampled(len(pivot.columns))
    bottom = np.zeros(len(pivot))
    for i, col in enumerate(pivot.columns):
        ax.bar(pivot.index, pivot[col].values,
               bottom=bottom, label=col, color=cmap(i), alpha=0.85, width=0.9)
        bottom += pivot[col].values

    ax.axvline(pd.Timestamp(WAR_START), color=WAR_COLOR, linewidth=2.5, linestyle="-",
               label="Oct 7 Attack", zorder=5)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax.set_xlabel("Date")
    ax.set_ylabel("Articles published")
    ax.set_title("Daily Article Volume by News Source (RSS) — Simulated Data", fontweight="bold")
    ax.legend(loc="upper left", framealpha=0.8, fontsize=9, ncol=2)
    fig.text(0.99, 0.01, "Note: All data is simulated for portfolio demonstration.",
             ha="right", fontsize=8, color="gray", style="italic")

    return _save(fig, "rss_articles_by_source.png")


# ---------------------------------------------------------------------------
# 5. Event impact spike ratio
# ---------------------------------------------------------------------------

def chart_event_spike_ratio() -> Path:
    """Horizontal bar chart of spike ratios per event per platform."""
    spike_path = TABLES_DIR / "q3_event_spikes.csv"
    if not spike_path.exists():
        logger.warning("q3_event_spikes.csv not found — run analysis.py first.")
        return None

    df = load_csv(spike_path)
    df = df.dropna(subset=["spike_ratio"])

    events = df["event_name"].unique()
    platforms = df["platform"].unique()
    x = np.arange(len(events))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 5))
    cmap = [PLATFORM_COLORS.get(p, "#888888") for p in ["Telegram", "RSS / News Websites"]]
    for i, (plat, color) in enumerate(zip(["Telegram", "RSS"], cmap)):
        subset = df[df["platform"] == plat].set_index("event_name").reindex(events)
        bars = ax.bar(x + i * width - width / 2, subset["spike_ratio"].fillna(0),
                      width, label=plat, color=color, alpha=0.85)
        for bar, val in zip(bars, subset["spike_ratio"].fillna(0)):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05,
                    f"{val:.1f}x", ha="center", va="bottom", fontsize=9)

    ax.axhline(1.0, color="black", linewidth=1.2, linestyle="--", alpha=0.6, label="Baseline (1.0x)")
    ax.set_xticks(x)
    ax.set_xticklabels([e.replace(" ", "\n") for e in events], fontsize=9)
    ax.set_ylabel("Spike ratio (event window / baseline)")
    ax.set_title("Activity Spike Ratio by War Event — Simulated Data", fontweight="bold")
    ax.legend(framealpha=0.8)
    fig.text(0.99, 0.01, "Note: All data is simulated for portfolio demonstration.",
             ha="right", fontsize=8, color="gray", style="italic")

    return _save(fig, "event_impact_spike_ratio.png")


# ---------------------------------------------------------------------------
# 6. Platform comparison
# ---------------------------------------------------------------------------

def chart_platform_comparison() -> Path:
    """Side-by-side bar chart comparing platform spike ratios."""
    spike_path = TABLES_DIR / "q2_platform_spike.csv"
    if not spike_path.exists():
        logger.warning("q2_platform_spike.csv not found — run analysis.py first.")
        return None

    df = load_csv(spike_path)
    df = df.sort_values("spike_ratio", ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: spike ratio bars
    colors = [PLATFORM_COLORS.get(p, "#888888") for p in df["platform"]]
    bars = axes[0].barh(df["platform"], df["spike_ratio"], color=colors, alpha=0.85)
    axes[0].axvline(1.0, color="black", linewidth=1.2, linestyle="--", alpha=0.6)
    for bar, val in zip(bars, df["spike_ratio"]):
        axes[0].text(val + 0.02, bar.get_y() + bar.get_height() / 2,
                     f"{val:.1f}x", va="center", fontsize=10)
    axes[0].set_xlabel("Spike ratio (first 7 days after Oct 7 vs baseline)")
    axes[0].set_title("Platform Spike Ratios", fontweight="bold")

    # Right: before/after grouped bar
    x = np.arange(len(df))
    w = 0.35
    axes[1].bar(x - w / 2, df["baseline_avg"], w, label="Baseline (pre Oct 7)", color="#aec7e8", alpha=0.85)
    axes[1].bar(x + w / 2, df["spike_window_avg"], w, label="Spike window (7d post Oct 7)",
                color="#ff7f0e", alpha=0.85)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([p.replace("/", "/\n") for p in df["platform"]], fontsize=9)
    axes[1].set_ylabel("Daily activity (raw units)")
    axes[1].set_title("Before vs. After (First 7 Days)", fontweight="bold")
    axes[1].legend(framealpha=0.8, fontsize=9)

    fig.suptitle("Platform Comparison — Simulated Data (Oct 7 Effect)", fontweight="bold", y=1.01)
    fig.text(0.99, -0.02, "Note: All data is simulated for portfolio demonstration.",
             ha="right", fontsize=8, color="gray", style="italic")
    plt.tight_layout()

    return _save(fig, "platform_comparison.png")


# ---------------------------------------------------------------------------
# Charts manifest
# ---------------------------------------------------------------------------

CHARTS_MANIFEST = [
    {
        "chart_title": "Daily Activity Timeline — All Platforms",
        "filename": "daily_activity_timeline.png",
        "explanation": "Normalized daily activity across Telegram, RSS news websites, and Google Trends from September to December 2023.",
        "key_insight": "All platforms show a dramatic and synchronized spike immediately after October 7, with Telegram showing the sharpest initial reaction.",
        "portfolio_section": "Overview / Key Findings",
    },
    {
        "chart_title": "Google Trends — Search Interest by Keyword",
        "filename": "google_trends_keywords.png",
        "explanation": "Relative search interest (0–100) for crisis-related keywords in Israel over the study period.",
        "key_insight": "Keywords like 'siren', 'hostages', and 'home front command' spike sharply around October 7, reflecting heightened public search behavior during emergencies.",
        "portfolio_section": "Platform Analysis / Google Trends",
    },
    {
        "chart_title": "Telegram Daily Views by Channel",
        "filename": "telegram_views_over_time.png",
        "explanation": "Total daily Telegram message views broken down by simulated public channel.",
        "key_insight": "Breaking news and home front channels dominate view counts. The October 7 period shows a 10–15x increase in total daily views.",
        "portfolio_section": "Platform Analysis / Telegram",
    },
    {
        "chart_title": "RSS Article Volume by News Source",
        "filename": "rss_articles_by_source.png",
        "explanation": "Daily article publication volume across six simulated Israeli news sources.",
        "key_insight": "RSS article output increased sharply after October 7 and remained elevated through December, with consistent contributions from all major outlets.",
        "portfolio_section": "Platform Analysis / News Websites",
    },
    {
        "chart_title": "Event Impact — Activity Spike Ratios",
        "filename": "event_impact_spike_ratio.png",
        "explanation": "Spike ratio for each major war event: average activity in the event window divided by the 14-day pre-event baseline.",
        "key_insight": "The October 7 attack produced by far the largest spike ratio. Subsequent events (ground operation, hostage deal, ceasefire end) show progressively smaller but still measurable spikes.",
        "portfolio_section": "Key Findings / Event Analysis",
    },
    {
        "chart_title": "Platform Comparison — Spike Ratios and Before/After",
        "filename": "platform_comparison.png",
        "explanation": "Compares the spike ratio and raw before/after activity across Telegram, RSS, and Google Trends.",
        "key_insight": "Telegram shows the highest spike ratio among the three platforms, consistent with its role as a real-time alert medium. RSS output also increases substantially. Google Trends shows a large but slightly delayed reaction.",
        "portfolio_section": "Key Findings / Platform Comparison",
    },
]


def save_charts_manifest() -> Path:
    out = PORTFOLIO_EXPORTS_DIR / "charts_manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(CHARTS_MANIFEST, f, indent=2)
    logger.info(f"Saved charts manifest to {out}")
    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    logger.info("=== Generating charts ===")
    chart_daily_activity_timeline()
    chart_google_trends_keywords()
    chart_telegram_views()
    chart_rss_articles_by_source()
    chart_event_spike_ratio()
    chart_platform_comparison()
    save_charts_manifest()
    logger.info("=== Chart generation complete ===")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    main()
