---
name: football-news
description: Use when scraping football news from web sources to create news files for the Obsidian vault
---

# Football News Scraping Skill

## Overview

Scrapes football news from web sources and creates properly formatted news files in the Obsidian vault. Uses web search as the primary tool since X.com requires opencode-browser (not Playwright/CDP).

## When to Use

- User says "scrape football news" or "football news"
- User wants latest transfers, match results, or football updates
- User wants news from specific leagues (Premier League, La Liga, Serie A, etc.)

## Workflow

### 1. Before Scraping - Check for Duplicates
Run scorer first to see what's already in tracker:
```bash
python score.py C:/Users/jtoem/Assets/News/football
```

### 2. Check existing news
```bash
Get-ChildItem -Path "C:/Users/jtoem/Assets/News/football/entities/news" -File
```

### 3. Search for News
Use websearch queries.

### 4. Fetch Full Article (MANDATORY)
After finding a news URL, use webfetch to extract the FULL article content — NOT just the snippet/summary from search results. The search results only provide headlines; the actual article contains the full context, quotes, and details needed for quality news files.

### 5. Create News Files
Write to vault with required format.

### 5. Update Tracker (after scraping)
```bash
python init-tracker.py
```

### Scoring System (v2.1)

Run scorer:
```bash
python score.py C:/Users/jtoem/Assets/News/football
```

Shows:
- TOP 15 by READ VALUE
- Files vs Tracker count
- LOW value list (skip these)

### Metrics (News VALUE not Entity)
```
total = reliability + news_type + recency + uniqueness
max = 30 + 25 + 10 + 10 = 75
```

**Reliability** (source trust):
- Tier 1 (30): Fabrizio, David Ornstein, BBC, Sky, ESPN
- Tier 2 (20): Teamtalk, CaughtOffside, Marca
- Unknown (5)

**News Type** (what is it?):
| Type | Score | 
|------|-------|
| Breaking | 25 |
| Transfer | 20 |
| Result | 18 |
| Update | 15 |
| Analysis | 12 |
| Opinion | 8 |
| Rumor | 3 |
| Gossip | 2 |

**Recency**: Today=10, Yesterday=8, Older=2

**Uniqueness**: +10 if NEW (not in tracker), +2 if already tracked

### Grades: A+(90+), A(80+), B+(70+), B(60+), C(40+), D(20+), F(<20)

```markdown
---
type: news
date: 2026-04-26
source: {SourceName}
url: {FULL_URL}
processed: true
entities:
  - "[[Entity1]]"
  - "[[Entity2]]"
tags: [tag1, tag2, tag3]
---

{Full article text here - do NOT summarize. Include all details, quotes, context from the original article. Wikilink all entities.}
```

## Important Rules

### Entity Wikilinking (MANDATORY)
Every named entity MUST be wikilinked:
- Clubs: `[[Arsenal-FC]]`, `[[Manchester-United]]`, `[[Real-Madrid]]`
- Players: `[[Erling-Haaland]]`, `[[Bukayo-Saka]]`
- Managers: `[[Pep-Guardiola]]`, `[[Mikel-Arteta]]`
- Competitions: `[[Premier-League]]`, `[[Champions-League]]`, `[[La-Liga]]`

### Entity → Folder Mapping
| Type | Folder |
|------|--------|
| Clubs | `Clubs/` |
| Players | `Players/` |
| Managers/Coaches/Pundits | `Persons/` |
| Leagues | `Leagues/` |
| Competitions | `Competitions/` |
| Concepts | `Concepts/` |

### Frontmatter Order
Entities FIRST, then tags:
```yaml
entities:
  - "[[Manchester-City]]"
  - "[[Erling-Haaland]]"
tags: [transfer, contract, man-city]
```

### News File Naming
Use format: `YYYY-MM-DD-{topic}-{source}.md`
- `2026-04-26-nicolas-jackson-bayern.md`
- `2026-04-26-arsenal-top-pl.md`
- `2026-04-26-bayern-real-madrid-ucl.md`

## Sources to Search

### Transfer & Breaking News
- Fabrizio Romano, David Ornstein (via Teamtalk, CaughtOffside)
- Sky Sports Transfer Centre
- Football Transfers

### Premier League
- Premier League official
- BBC Sport Football
- The Athletic Football
- Sky Sports Football

### European Leagues
- Serie A: Tutto Sport, Gianluca Di Marzio
- La Liga: Marca, AS
- Bundesliga: Kicker
- Ligue 1: L'Equipe

### Match Results
- Champions League: UEFA
- Domestic leagues: Respective league sites

## Quick Reference

| Task | Command |
|------|---------|
| Check existing | `Get-ChildItem .../entities/news -File` |
| Search web | `websearch numResults=15 query="..."` |
| Score news | `python .../football-news/score.py --vault C:/Users/jtoem/Assets/News/football` |
| Count files | `(Get-ChildItem .../entities/news -File).Count` |

## Scoring System (v2 - by NEWS VALUE, not entity)

Run scorer to prioritize reading:

```bash
python C:/Users/jtoem/.config/opencode/skills/browser-agent/football-news/score.py C:/Users/jtoem/Assets/News/football
```

Output: TOP 15 by value, average, LOW value list (skip these)

### Scoring Formula
```
total = reliability + news_type + recency + uniqueness
max = 30 + 25 + 10 + 10 = 75
```

### Reliability (Source trust)
- **Tier 1 (30)**: Fabrizio Romano, David Ornstein, BBC, Sky, ESPN
- **Tier 2 (20)**: Teamtalk, CaughtOffside, Marca, Goal
- **Tier 3 (10)**: Yahoo, smaller aggregators
- **Unknown (5)**:

### News Type (What's being reported)
| Type | Score | Example |
|------|-------|----------|
| Breaking | 25 | "Here we go", official confirmed |
| Transfer | 20 | Active negotiation |
| Result | 18 | Match final score |
| Update | 15 | Contract, injury |
| Analysis | 12 | Tactical breakdown |
| Opinion | 8 | Pundit takes |
| Rumor | 3 | "could sign" |
| Gossip | 2 | Unverified |

### Grades
- A+ (90+): MUST READ
- A (80+): Important
- B+ (70+): Worth reading
- B (60+): Standard news
- C (40+): Skip unless interested
- D/F (<30): Skip - LOW VALUE

## Article Content (MANDATORY - FULL TEXT ONLY)

**CRITICAL: Always fetch the FULL article via webfetch. NEVER use search result snippets or summaries.**

Search results only provide headlines and brief teasers. The actual article content contains:
- Full match details, scores, timelines
- Direct quotes from managers and players
- Complete context and background
- Statistical details

Steps:
1. Find article URL from search/browse
2. Use `webfetch url={FULL_ARTICLE_URL}` to get complete content
3. Write the FULL article text to the file — do NOT summarize or condense
4. The news file should contain the complete article prose, not a summary

## Common Mistakes to Avoid

1. **Summarizing articles** - Write FULL article content, not summaries
2. **Forgetting to wikilink** - Every club, player, manager must have [[]]
3. **Wrong entity order** - entities before tags
4. **Using bare names** - Must be `[[Erling-Haaland]]` not `Erling Haaland`
5. **Missing source URL** - Always include the article URL
6. **Creating duplicates** - Check vault first

## Vault Location

```
C:/Users/jtoem/Assets/News/football/entities/news/
```

## File Count Target

Aim for 50+ news files per session when requested.