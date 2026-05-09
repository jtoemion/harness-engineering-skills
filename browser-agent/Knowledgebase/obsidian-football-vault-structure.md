# 🧠 Obsidian Football Analytics Vault — Structure Guide

> A single-vault design for football news ingestion, wikilink graph building,
> and data science pipeline feeding (e.g. Chaos prediction model).

---

## 📐 Design Philosophy

Obsidian works best for analytics when you treat it as **two things simultaneously**:

1. **Ontology layer** — the *entities* and *relationships* in your domain (clubs, players, competitions, events)
2. **Feature store** — YAML frontmatter acts as structured rows in a dataset

The wikilinks ARE your graph edges. Dataview is your in-vault SQL.
Python/pandas talks to the exported CSV — Obsidian is the *upstream* truth store.

---

## 🗂️ Vault Folder Structure

```
📦 Football Vault/
│
├── 📁 _templates/          ← Templater templates for each note type
│   ├── tpl-club.md
│   ├── tpl-player.md
│   ├── tpl-match.md
│   ├── tpl-nation.md
│   ├── tpl-news.md
│   └── tpl-analysis.md
│
├── 📁 entities/
│   ├── 📁 clubs/           ← One note per club (permanent)
│   │   ├── Arsenal FC.md
│   │   ├── Real Madrid.md
│   │   └── ...
│   ├── 📁 players/         ← One note per tracked player
│   │   ├── Erling Haaland.md
│   │   └── ...
│   ├── 📁 nations/         ← WC2026 + major footballing nations
│   │   ├── England.md
│   │   └── ...
│   ├── 📁 coaches/
│   │   ├── Pep Guardiola.md
│   │   └── ...
│   └── 📁 competitions/
│       ├── Premier League.md
│       ├── Champions League.md
│       └── WC 2026.md
│
├── 📁 events/
│   ├── 📁 matches/         ← Date-prefixed, one note per match
│   │   ├── 2026-04-20-Arsenal-vs-Man City.md
│   │   └── ...
│   ├── 📁 transfers/
│   │   └── 2026-01-15-Mbappe-to-Real Madrid.md
│   └── 📁 injuries/
│       └── 2026-03-10-Bellingham-hamstring.md
│
├── 📁 analysis/            ← Your analytical synthesis notes
│   ├── 📁 predictions/
│   │   └── 2026-WC-Group-C-prediction.md
│   ├── 📁 tactical/
│   │   └── Norway-high-press-system.md
│   └── 📁 form-reports/
│       └── 2026-04-W3-PL-form.md
│
├── 📁 data/                ← Periodic snapshots (queryable via Dataview)
│   ├── 📁 standings/
│   │   └── 2026-04-24-PL-standings.md
│   └── 📁 stats/
│       └── 2026-04-xG-tracker.md
│
└── 📁 _meta/               ← Vault config, MOCs, dashboards
    ├── MOC-Competitions.md
    ├── MOC-WC2026.md
    ├── Dashboard.md
    └── README.md
```

---

## 📝 YAML Frontmatter Templates

### Club Note — `entities/clubs/Arsenal FC.md`
```yaml
---
type: club
name: Arsenal FC
abbreviation: ARS
league: "[[Premier League]]"
league_tier: 1
country: "[[England]]"
confederation: UEFA
founded: 1886
stadium: Emirates Stadium
capacity: 60704
manager: "[[Mikel Arteta]]"
wc2026_nation_players:
  - "[[England]]"
  - "[[Spain]]"
  - "[[Brazil]]"
ucl_2025_26: true
current_form: [W, W, D, W, L]
tags: [club, epl, england, ucl]
---

## Overview
[[Arsenal FC]] are currently 2nd in the [[Premier League]] 2025-26.

## Key Players
- [[Bukayo Saka]] — winger, [[England]]
- [[Martin Ødegaard]] — captain, [[Norway]]
- [[Declan Rice]] — midfielder, [[England]]

## News
```dataview
LIST
FROM "events" OR "entities/news"
WHERE contains(file.outlinks, this.file.link)
SORT file.ctime DESC
LIMIT 10
```

## Matches
```dataview
TABLE home, away, home_score, away_score, competition
FROM "events/matches"
WHERE home = this.file.link OR away = this.file.link
SORT date DESC
LIMIT 10
```
```

---

### Match Note — `events/matches/2026-04-20-Arsenal-vs-ManCity.md`
```yaml
---
type: match
date: 2026-04-20
home: "[[Arsenal FC]]"
away: "[[Manchester City]]"
competition: "[[Premier League]]"
matchday: 34
home_score: 2
away_score: 1
home_xg: 1.84
away_xg: 1.21
home_possession: 48
away_possession: 52
result: home_win
tags: [match, epl, 2025-26]
---

## Summary
[[Arsenal FC]] defeated [[Manchester City]] 2-1 at the Emirates.

## Goals
- 23' [[Bukayo Saka]] (pen) — [[Arsenal FC]]
- 67' [[Gabriel Martinelli]] — [[Arsenal FC]]
- 71' [[Erling Haaland]] — [[Manchester City]]

## Analysis
[[Arsenal FC]] sat deep and hit on the counter. Relates to [[tactical/Arsenal-low-block-vs-top-6.md]].
```

---

### Player Note — `entities/players/Erling Haaland.md`
```yaml
---
type: player
name: Erling Haaland
nationality: "[[Norway]]"
club: "[[Manchester City]]"
position: ST
age: 25
wc2026: true
wc2026_group: I
market_value_eur: 200000000
goals_2025_26: 28
assists_2025_26: 6
tags: [player, striker, norway, epl, wc2026]
---
```

---

## News Note — `entities/news/2026-04-24-haaland-injury-scare.md`
```yaml
---
type: news
date: 2026-04-24
source: BBC Sport
url: https://www.bbc.com/sport/football/abc123
processed: true
entities:
  - "[[Erling Haaland]]"
  - "[[Manchester City]]"
  - "[[Norway]]"
  - "[[WC 2026]]"
tags: [news, injury, wc2026-risk]
---

## Summary
[[Erling Haaland]] limped off in the 78th minute during [[Manchester City]]'s 3-1 victory over [[Wolves FC|Wolves]] at the Etihad Stadium. Scans are pending for the [[Norway]] striker, whose absence could severely impact [[Norway]]'s [[WC 2026]] Group I campaign. The {{date}} defeat leaves City three points clear at the top of the [[Premier League]] table with five games remaining.

> Relates to [[analysis/predictions/2026-WC-Group-I-prediction.md]].
```

---

## 🔍 Dataview Queries (Power Examples)

### All WC2026 matches involving EPL clubs
```dataview
TABLE home, away, date, home_score, away_score
FROM "events/matches"
WHERE competition = [[WC 2026]]
  AND (contains(home.league, "Premier League") OR contains(away.league, "Premier League"))
SORT date ASC
```

### All injured players who are WC2026 participants
```dataview
TABLE player, club, nationality, injury_date
FROM "events/injuries"
WHERE player.wc2026 = true
SORT injury_date DESC
```

### Form table — last 5 matches by club
```dataview
TABLE club, current_form, sum(current_form) AS form_pts
FROM "entities/clubs"
WHERE league = [[Premier League]]
SORT form_pts DESC
```

### All news articles
```dataview
LIST
FROM "entities/news"
WHERE type = "news"
SORT date DESC
```

---

## 🔁 News Ingestion Workflow

```
[ RSS / Scraped Article ]
        ↓
  entities/news/YYYY-MM-DD-title.md
  (frontmatter: processed=true, full article text)
        ↓
  [ Immediate ]
  Wikilinks added inline → [[Club]], [[Player]], [[Competition]]
  Tag: injury / transfer / tactical / result
        ↓
  Update entity notes (player form, injury status, etc.)
        ↓
  [ Weekly ] Export via Dataview → CSV → Python / Chaos model
```

---

## 🐍 Data Science Bridge — Export to Python

Use the **Obsidian Dataview JS** export or a Python watcher script:

### Option A — Dataview JS snippet in vault
```javascript
// In a Dashboard note — exports to clipboard
const matches = dv.pages('"events/matches"')
  .where(p => p.type === "match")
  .map(p => ({
    date: p.date,
    home: p.home?.path,
    away: p.away?.path,
    home_score: p.home_score,
    away_score: p.away_score,
    home_xg: p.home_xg,
    away_xg: p.away_xg,
  }));
dv.paragraph("```json\n" + JSON.stringify(matches, null, 2) + "\n```");
```

### Option B — Python vault reader (runs outside Obsidian)
```python
import yaml, glob, json
from pathlib import Path

VAULT = Path("/path/to/Football Vault")

def read_notes(folder, note_type):
    records = []
    for f in (VAULT / folder).rglob("*.md"):
        text = f.read_text(encoding="utf-8")
        if text.startswith("---"):
            front = text.split("---")[1]
            try:
                data = yaml.safe_load(front)
                if data.get("type") == note_type:
                    records.append(data)
            except:
                pass
    return records

matches = read_notes("events/matches", "match")
players = read_notes("entities/players", "player")

# → Feed directly into pandas / your Chaos model λ function
import pandas as pd
df_matches = pd.DataFrame(matches)
df_matches["date"] = pd.to_datetime(df_matches["date"])
```

---

## 🧩 Recommended Obsidian Plugins

| Plugin | Purpose |
|--------|---------|
| **Dataview** | Query YAML frontmatter as a database |
| **Templater** | Auto-populate note templates on creation |
| **Tag Wrangler** | Manage tag taxonomy across the vault |
| **Periodic Notes** | Daily/weekly inbox + form reports |
| **QuickAdd** | Fast-capture news without breaking flow |
| **Graph Analysis** | Visualize entity relationship density |
| **Smart Connections** | AI-assisted wikilink suggestions |
| **DB Folder** | Table view of entity folders |

---

## 📊 Data Science Conceptual Model

```
┌─────────────────────────────────────────────────────┐
│                  OBSIDIAN VAULT                      │
│                                                      │
│  [Entities]    [Events]      [Analysis]              │
│  clubs/        matches/      predictions/            │
│  players/      transfers/    tactical/               │
│  nations/      injuries/     form-reports/           │
│                                                      │
│  YAML = structured rows                              │
│  Wikilinks = graph edges                             │
│  Dataview = in-vault SQL                             │
└──────────────────────┬──────────────────────────────┘
                       │ Python vault reader
                       ↓
┌─────────────────────────────────────────────────────┐
│               PANDAS / DATA LAYER                    │
│  df_matches, df_players, df_standings                │
│  Feature engineering, xG delta, form vectors        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────┐
│             CHAOS MODEL (λ Poisson)                  │
│  Attack/Defense strength, home advantage            │
│  Match outcome probability distributions            │
└─────────────────────────────────────────────────────┘
```

---

*Structure inspired by Zettelkasten + Domain-Driven Design principles*
*Optimized for football analytics and WC2026 prediction workflows*
