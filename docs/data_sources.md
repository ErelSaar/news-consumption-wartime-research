# Data Sources

## Current Status

All data in this version is **simulated** using `src/sample_data_generator.py`. The simulation is designed to demonstrate the research pipeline and produce plausible-looking patterns, but it does not constitute real evidence.

## Planned Real Data Sources

### 1. Telegram Public Channels

**Collection method:** Telethon Python library via the official Telegram API.

**Authentication required:** Yes — Telegram API ID, hash, and phone number (free, obtained at https://my.telegram.org/apps).

**Legal note:** Only public channels are to be collected. User data must not be collected. This must comply with Telegram's Terms of Service.

**Example public channels of interest:**
- IDF official spokesperson channel
- Major Israeli news broadcasters (Kan, N12, Channel 13)
- Home Front Command official channel
- Hostage family advocacy channels (if public)

**Columns collected:**
- `message_id`, `published_at`, `text`, `views`, `forwards`, `replies`, `has_media`, `channel_name`

**Limitations:**
- View counts reflect the channel's own estimate; may not equal unique users.
- Deleted messages are not retrievable retroactively.
- Telegram's API rate limits may restrict historical collection.

---

### 2. RSS Feeds — Israeli News Outlets

**Collection method:** `feedparser` Python library (pure Python, no API key).

**Authentication required:** No.

**Current feed list (may require verification before use):**

| Source | Feed URL |
|--------|---------|
| Ynet | https://www.ynet.co.il/Integration/StoryRss2.xml |
| Times of Israel | https://www.timesofisrael.com/feed/ |
| Haaretz | https://www.haaretz.com/cmlink/1.628752 |
| Mako | https://rss.mako.co.il/rss/news-military.xml |
| N12 News | (verify URL before use) |
| Kan News | https://www.kan.org.il/rss/?catid=40 |

**Limitations:**
- RSS feeds typically return only the most recent 20–50 articles.
- Historical RSS collection requires scraping archives or using third-party archives.
- Article read counts are not available via RSS.
- Category classification in RSS feeds is inconsistent across outlets.

---

### 3. Google Trends

**Collection method:** `pytrends` Python library (unofficial wrapper for Google Trends).

**Authentication required:** No. However, pytrends can be rate-limited or blocked.

**Keywords studied:**
- news
- siren (Hebrew: "azaka" / English transliteration varies)
- hostages
- home front command
- telegram news
- Israel news
- Iran attack

**Geo filter:** `IL` (Israel)

**Limitations:**
- Values are relative (0–100 within the requested period), not absolute volumes.
- Queries are sampled — not all searches are represented.
- pytrends is unofficial and may break if Google changes its interface.
- Historical daily data (daily granularity) is available only for periods under 270 days.

---

### 4. War Events (Manually Curated)

**Source:** Public news reports and Wikipedia.

**Format:** `data/sample/war_events.csv`

This table is created manually and does not require automated collection. It provides the reference dates for before/after analysis and event-window spike calculations.

---

## Future Data Sources to Consider

| Source | What it adds | Difficulty |
|--------|-------------|------------|
| YouTube (via YouTube Data API) | Video news consumption patterns | Medium (requires API key) |
| Twitter/X | Social media discourse | Hard (API access restricted) |
| Survey data (e.g., Reuters Institute Israel reports) | Self-reported news consumption | Low (manual entry) |
| TV ratings data | Broadcast news consumption | Hard (proprietary data) |
| Radio ratings | Radio news consumption | Hard (proprietary data) |
