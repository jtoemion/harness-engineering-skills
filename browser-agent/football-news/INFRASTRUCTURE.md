# Football-News Subskill — Infrastructure Documentation

**Location:** `browser-agent/football-news/`
**Status:** Production Ready

---

## Overview

The **football-news** subskill handles scraping, tracking, and scoring football news articles for an Obsidian vault. It's a self-contained system within the browser-agent skill.

---

## Files

```
football-news/
├── SKILL.md            # Main skill documentation (entry point)
├── news-tracker.py     # Duplicate detection across sessions
├── news-tracker.json   # Persisted tracker state
├── score.py           # News value scorer (v2.1)
├── score_news.py       # Extended scoring
├── init-tracker.py     # Tracker initializer
├── news-value.yaml    # News value weights
└── docs/
    └── 2026-04-26-scoring-matrix-plan.md
```

---

## Core Components

### 1. News Tracker (`news-tracker.py`)

**Purpose:** Persists across sessions to detect duplicates.

**Data Structure (`news-tracker.json`):**
```json
{
  "news": [
    {
      "key": "unique-url-or-title-date",
      "title": "...",
      "date": "2026-04-26",
      "source": "FabrizioRomano",
      "entities": ["[[Manchester-City]]", "[[Erling-Haaland]]"],
      "added": "2026-04-26T10:30:00"
    }
  ],
  "last_updated": "2026-04-26T10:30:00"
}
```

**Duplicate Detection:**
- By exact URL match
- By title + date match
- By key entities + same date (e.g., "Haaland to Real Madrid" on same day)

**CLI:**
```bash
python news-tracker.py stats      # Show tracker stats
python news-tracker.py check <url> <title>  # Check if duplicate
```

---

### 2. News Scorer (`score.py` v2.1)

**Purpose:** Score news files by value to prioritize reading.

**Scoring Formula:**
```
total = reliability + news_type + recency + uniqueness
max = 30 + 25 + 10 + 10 = 75
```

**Reliability (by source trust):**
| Tier | Score | Sources |
|------|-------|----------|
| Tier 1 | 30 | Fabrizio Romano, David Ornstein, BBC, Sky, ESPN, The Athletic |
| Tier 2 | 20 | Teamtalk, CaughtOffside, Marca, Goal, Gazzetta |
| Tier 3 | 10 | Yahoo Sports, OneFootball |
| Unknown | 5 | Everything else |

**News Type:**
| Type | Score | Example |
|------|-------|---------|
| Breaking | 25 | "Here we go!", official confirmed |
| Transfer | 20 | Active negotiation |
| Result | 18 | Match final score |
| Update | 15 | Contract, injury news |
| Analysis | 12 | Tactical breakdown |
| Opinion | 8 | Pundit takes |
| Rumor | 3 | "could sign" |
| Gossip | 2 | Unverified |

**Recency:**
- Today: +10
- Yesterday: +8
- 2-3 days: +6
- 4+ days: +2

**Uniqueness:**
- NEW (not in tracker): +10
- Already tracked: +2

**Grades:**
- A+ (90+): MUST READ
- A (80+): Important
- B+ (70+): Worth reading
- B (60+): Standard news
- C (40+): Skip unless interested
- D/F (<30): Skip - LOW VALUE

**CLI:**
```bash
python score.py C:/Users/jtoem/Assets/News/football
```

**Output:**
```
=======================================================
FOOTBALL NEWS VALUE (v2.1)
=======================================================
Files: 47 | Tracker: 31

TOP 15:
 1.  75 [A+] 2026-04-26-haaland-city-renew.md  breaking
 2.  72 [A+] 2026-04-25-mbappe-real-madrid.md   transfer
...

Avg: 52.3
LOW: 5
```

---

### 3. Score News (`score_news.py`)

**Purpose:** Extended scoring with more detailed analysis.

**Features:**
- Entity relevance scoring
- Cross-referencing with existing entities
- Value trend analysis

---

### 4. News Value Weights (`news-value.yaml`)

**Purpose:** Configurable weights for news scoring.

---

## Workflow

### Standard News Scraping Flow

```
1. Check existing news
   Get-ChildItem C:/Users/jtoem/Assets/News/football/entities/news -File

2. Run scorer to prioritize
   python score.py C:/Users/jtoem/Assets/News/football

3. Search for news
   websearch numResults=15 query="football transfers today"

4. Create news files (see format below)

5. Update tracker
   python init-tracker.py
```

### News File Format

```markdown
---
type: news
date: 2026-04-26
source: FabrizioRomano
url: https://x.com/FabrizioRomano/status/123456789
processed: true
entities:
  - "[[Manchester-City]]"
  - "[[Erling-Haaland]]"
  - "[[Pep-Guardiola]]"
  - "[[Premier-League]]"
tags: [transfer, contract, man-city]
---

## Summary

[[Manchester-City]] have agreed a new contract with [[Erling-Haaland]] until 2030,
reports [[Fabrizio-Romano]]. [[Pep-Guardiola]] confirmed the striker is "completely
committed" to the club as they push for [[Premier-League]] glory.
```

**Required Fields:**
- `type: news`
- `date: YYYY-MM-DD`
- `source: {SourceName}`
- `url: {FULL_URL}`
- `processed: true`
- `entities:` (wikilinks, entities FIRST)
- `tags:` (tags SECOND)

**MANDATORY Rules:**
1. Wikilink EVERY entity: `[[Arsenal-FC]]`, `[[Bukayo-Saka]]`, `[[Pep-Guardiola]]`
2. Entities FIRST, tags SECOND in frontmatter
3. Include source URL
4. File naming: `YYYY-MM-DD-{topic}-{source}.md`

---

## Entity → Folder Mapping

| Entity Type | Vault Folder | Example |
|------------|--------------|----------|
| Clubs | `Clubs/` | `Manchester-City.md` |
| Players | `Players/` | `Erling-Haaland.md` |
| Managers/Coaches | `Persons/` | `Pep-Guardiola.md` |
| Leagues | `Leagues/` | `Premier-League.md` |
| Competitions | `Competitions/` | `Champions-League.md` |
| Nations | `Nations/` | `England.md` |
| Concepts | `Concepts/` | `Title-Race.md` |

---

## Primary Sources

### Transfer & Breaking News
- Fabrizio Romano (X.com)
- David Ornstein (The Athletic, BBC)
- Sky Sports Transfer Centre
- Football Transfers sites

### Premier League
- BBC Sport Football
- The Athletic Football
- Sky Sports Football

### European Leagues
- Serie A: Tutto Sport, Gianluca Di Marzio
- La Liga: Marca, AS
- Bundesliga: Kicker
- Ligue 1: L'Équipe

### Match Results
- Champions League: UEFA official
- Domestic leagues: Respective league sites

---

## Vault Location

```
C:/Users/jtoem/Assets/News/football/entities/news/
```

---

## Integration with Browser-Agent

The football-news subskill is invoked when:
- User says "scrape football news" or "football news"
- User wants latest transfers, match results
- User specifies league (Premier League, La Liga, etc.)

It uses browser-agent's:
- `entities/registry.yaml` for entity wikilinking
- `Knowledgebase/` for reference data
- Domain skills for source navigation

---

## Summary

| Component | Purpose |
|-----------|---------|
| `SKILL.md` | Entry point + documentation |
| `news-tracker.py` | Duplicate detection across sessions |
| `news-tracker.json` | Persisted state file |
| `score.py` | News value scorer (v2.1) |
| `score_news.py` | Extended scoring |
| `init-tracker.py` | Tracker initializer |
| `news-value.yaml` | Configurable weights |

**Key Features:**
- ✅ Duplicate detection (URL, title+date, entities)
- ✅ News value scoring by reliability + type + recency
- ✅ Grade system (A+ to F)
- ✅ Mandatory entity wikilinking
- ✅ Obsidian vault integration