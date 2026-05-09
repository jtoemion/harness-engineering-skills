# football-news

## Trigger
Invoke when user says: **"football-news"** or requests football news scraping

## What It Does
1. Scrapes quality football articles from configured sources (BBC, Sky Sports, ESPN, etc.)
2. Filters using `news_signals.yaml` (96 OUT patterns, 84 IN signals)
3. Auto-generates Obsidian tags and wiki-links
4. Saves to `C:\Users\jtoem\Assets\News\football` vault

## Sources
- BBC Sport: `https://www.bbc.com/sport/football`
- Sky Sports: `https://www.skysports.com/football`
- ESPN: `https://www.espn.com/soccer`

## Filters
**OUT (not scraped):**
- Match results: "beat", "lose to", "thrash", "brace", "hat-trick"
- Trackers: "FPL", "fantasy", "live blog", "updates"
- Rankings: "standings", "tables", "power rankings"
- Rumors: "transfer gossip", "interested in"

**IN (scraped):**
- BREAKING, EXCLUSIVE, DONE DEAL, HERE WE GO
- Transfers: "signs", "joins", "sold", "agree fee"
- Records: "record", "milestone", "all-time"
- Tragedies: "dies", "passed away", "collapses"

## Usage
```bash
# Default - scrape 5 BBC articles
python _tools/scrape_articles.py bbc https://www.bbc.com/sport/football "C:/Users/jtoem/Assets/News/football" 5

# Sky Sports
python _tools/scrape_articles.py sky https://www.skysports.com/football "C:/Users/jtoem/Assets/News/football" 5

# ESPN
python _tools/scrape_articles.py espn https://www.espn.com/soccer "C:/Users/jtoem/Assets/News/football" 5
```

## Output Format
Each article saved as `{source}-{slug}-{date}.md` with:
- Frontmatter: source, url, date, author, tags, related
- Body: full article content
- Wiki-links: `[[linked articles]]`

## Files
- `_tools/scrape_articles.py` - Main scraper
- `_tools/news_signals.yaml` - Filter configuration
- `Assets/News/football/` - Vault location

## Rules (MANDATORY)

1. **One article = One file** - Never create summary files with multiple articles
2. **Full content** - Scrape complete article content, not just headlines
3. **Frontmatter** - Include source, url, date, author, scraped date, tags, related
4. **Tags for graph** - Extract topic tags (teams, players, leagues, events) for Obsidian graph visualization
5. **Wiki-links** - Add `[[internal links]]` to related scraped articles

## Frontmatter Template
```markdown
---
source: espn
url: https://...
date: 2026-04-24
author: Author Name
scraped: 2026-04-24
tags:
  - WorldCup2026
  - Ronaldo
  - AlNassr
  - Goals
  - Records
related: []
---

# Article Title

**By:** Author Name

**Published:** 2026-04-24

**Tags:** #WorldCup2026 #Ronaldo #Goals

[Full article content]

---

## Related

- [[other-article-name]]
```

## Example Usage

Scrape 5 latest ESPN football articles:
```bash
python _tools/scrape_articles.py espn https://www.espn.com/soccer "C:/Users/jtoem/Assets/News/football" 5
```

## Filter Configuration

See `_tools/news_signals.yaml` for complete filter rules.

**Filter OUT (50+ patterns):**
- Trackers: tracker, live blog, updates, running blog
- Rankings: rankings, power rankings, standings, tables
- Schedules: schedule, fixtures, preview, predictions
- Rumors: transfer gossip, transfer rumours, interested in
- Stats: depth charts, by the numbers, stat packed

**Filter IN signals (80+ patterns):**
- BREAKING, EXCLUSIVE, DONE DEAL, HERE WE GO
- Transfers: signs, joins, sold, agree fee, bid accepted
- Managerial: sacked, appoints, resigns, new manager
- Records: record, milestone, all-time, becomes, surpasses
- Tragic: dies, passed away, tragically, collapsed
- Competitions: wins, champions, qualified, relegated

**Source configs** for BBC, Sky Sports, The Athletic, Transfermarkt, Marca, Goal

Located at: `_tools/scrape_articles.py`

### Quality Filtering

Before scraping, articles are filtered using `news_signals.yaml`:

**Filter OUT (skip):**
- Routine updates: trackers, schedules, fixtures, standings, rankings
- Daily recaps without analysis
- Fantasy/betting tips

**Filter IN (scrape):**
- BREAKING, EXCLUSIVE, DONE DEAL, HERE WE GO
- Transfers, signings, sackings
- Records, milestones, achievements
- Deaths, tragedies
- Major match outcomes (wins finals, promotions)

**Signal Keywords by Category:**
- Transfers: signs, joins, leaves, sold, loan, medical, agree fee
- Managerial: sacked, appointed, resigns, dismissed
- Records: record, milestone, all-time, first time, becomes
- Tragic: dies, tragedy, passed away, hospitalized

### Usage
```python
from scrape_articles import ArticleScraper

scraper = ArticleScraper("espn", "https://www.espn.com", "C:/Users/jtoem/Assets/News/football")
scraper.run("https://www.espn.com/soccer", ['a[href*="/soccer/story"]'], max_articles=5)
```