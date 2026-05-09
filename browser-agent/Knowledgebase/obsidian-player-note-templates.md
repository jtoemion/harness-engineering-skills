# 🧠 Obsidian Player Note System — Design & Templates

---

## ⚡ Core Philosophy: The "Frozen Body, Live Veins" Model

The biggest mistake people make is **pasting news INTO the player note**.
That way madness lies — the note becomes a 400-line blob in two weeks.

Instead, think of it like this:

```
Player Note = Wikipedia article (stable facts + current state)
News Notes  = Newspaper archive (events that REFERENCE the player)
Dataview    = The glue that surfaces news INSIDE the player note dynamically
```

The player note has TWO kinds of content:

| Layer | What it is | How it updates |
|-------|-----------|----------------|
| **YAML frontmatter** | Structured facts & current state | Manual, only on real state change (transfer, injury, form shift) |
| **Static sections** | Bio, style, club history | Rarely — maybe monthly |
| **Dataview blocks** | Live queries pulling from news/match notes | Automatic — zero maintenance |
| **Log section** | One-liner dated entries for quick facts | Append-only, never rewrite |

---

## 📄 TEMPLATE 1 — Full Player Note

*File: `entities/players/Erling Haaland.md`*

```markdown
---
# ═══════════════════════════════
# IDENTITY (Never changes)
# ═══════════════════════════════
type: player
name: Erling Haaland
dob: 2000-07-21
age: 25
nationality: "[[Norway]]"
birthplace: Leeds, England
height_cm: 194
preferred_foot: left
position: ST
position_alt: []

# ═══════════════════════════════
# CURRENT STATE (Updates on change)
# ═══════════════════════════════
club: "[[Manchester City]]"
club_since: 2022-07-01
shirt_number: 9
contract_until: 2027-06-30
market_value_eur: 200000000
status: fit          # fit | injured | suspended | doubt | recovering
injury_detail: null
return_date: null

# ═══════════════════════════════
# WC 2026 CONTEXT
# ═══════════════════════════════
wc2026: true
wc2026_nation: "[[Norway]]"
wc2026_group: I
wc2026_group_opponents:
  - "[[France]]"
  - "[[Senegal]]"
  - "[[Iraq]]"
wc2026_risk: low      # low | medium | high | out

# ═══════════════════════════════
# SEASON STATS 2025-26 (Update weekly)
# ═══════════════════════════════
season: 2025-26
appearances: 32
goals: 28
assists: 6
yellow_cards: 3
red_cards: 0
minutes_played: 2712
avg_goals_per_90: 0.93
xg_total: 26.4
xg_diff: 1.6          # goals minus xG — positive = overperforming

# ═══════════════════════════════
# FORM (Rolling 5 matches — update after each game)
# ═══════════════════════════════
form_last5: [G, G, -, G, G]   # G=goal, A=assist, -=blank, M=missed, I=injured off
form_rating_last5: 8.2         # avg match rating

# ═══════════════════════════════
# TAGS
# ═══════════════════════════════
tags:
  - player
  - striker
  - epl
  - wc2026
  - norway
  - ucl
  - tier-world-class
---

# Erling Haaland

> **[[Manchester City]]** · ST · 🇳🇴 [[Norway]] · #9
> Status: `= this.status` | WC2026 Risk: `= this.wc2026_risk`

---

## 🧬 Profile

| | |
|--|--|
| **Full name** | Erling Braut Haaland |
| **DOB** | 21 July 2000 (age 25) |
| **Birthplace** | Leeds, England |
| **Nationality** | [[Norway]] |
| **Height** | 194 cm |
| **Foot** | Left |
| **Position** | ST |
| **Club** | [[Manchester City]] (since 2022) |
| **Contract** | Until June 2027 |

---

## 📊 2025–26 Season Stats

| Stat | Value |
|------|-------|
| Apps | `= this.appearances` |
| Goals | `= this.goals` |
| Assists | `= this.assists` |
| Goals/90 | `= this.avg_goals_per_90` |
| xG | `= this.xg_total` |
| xG diff | `= this.xg_diff` |
| Mins | `= this.minutes_played` |

**Form (last 5):** `= this.form_last5`

---

## 🎯 Playing Style

Haaland is a pure penalty-box striker defined by explosive acceleration over short distances and clinical finishing. His movement off the ball — particularly blind-side runs and timing of late arrivals — is elite. Weak areas: link-up play under pressure, left-sided wide build-up.

Relevant to [[Chaos Model]] inputs: high xG overperformance (+1.6) suggests sustainable finishing quality rather than luck.

---

## 🏟️ Club History

| Club | From | To | Goals | Apps |
|------|------|-----|-------|------|
| [[Bryne FK]] | 2016 | 2017 | 0 | 16 |
| [[Molde FK]] | 2017 | 2019 | 14 | 50 |
| [[Red Bull Salzburg]] | 2019 | 2020 | 29 | 27 |
| [[Borussia Dortmund]] | 2020 | 2022 | 86 | 89 |
| [[Manchester City]] | 2022 | now | 120+ | 145+ |

---

## 🌍 International

**[[Norway]]** — WC2026 Group I
Opponents: [[France]] · [[Senegal]] · [[Iraq]]

Norway qualified for WC2026 for the first time in 24 years — Haaland is the single biggest reason.

```dataview
TABLE date, home, away, home_score, away_score, competition
FROM "events/matches"
WHERE (home = [[Norway]] OR away = [[Norway]])
  AND type = "match"
SORT date DESC
LIMIT 8
```

---

## 🩺 Injury History

```dataview
TABLE date, injury_detail, games_missed, return_date
FROM "events/injuries"
WHERE player = [[Erling Haaland]]
SORT date DESC
```

---

## 🔄 Transfer Rumours

```dataview
LIST WITHOUT ID "**" + date + "** — " + summary
FROM "events/transfers"
WHERE contains(players, [[Erling Haaland]])
SORT date DESC
```

---

## 📰 News Feed

```dataview
TABLE WITHOUT ID
  ("[[" + file.name + "]]") AS News,
  date AS Date,
  source AS Source
FROM "entities/news" OR "events"
WHERE contains(file.outlinks, [[Erling Haaland]])
  AND type = "news"
SORT date DESC
LIMIT 15
```

---

## ⚽ Recent Matches

```dataview
TABLE date, home, away, home_score, away_score, competition, result
FROM "events/matches"
WHERE contains(players_notable, [[Erling Haaland]])
SORT date DESC
LIMIT 10
```

---

## 📋 Log
*Append-only. One line per entry. Never delete.*

- 2026-04-20 · Scored vs Arsenal (pen, 71') — Man City lost 1-2
- 2026-04-13 · Hattrick vs Brighton — 3 goals, 90 mins
- 2026-04-06 · Rested for UCL — squad rotation
- 2026-03-28 · Norway 2-0 Sweden — goal + assist, WC2026 prep
- 2026-03-10 · Hamstring scare vs Wolves — subbed 78', scan clear
- 2026-01-15 · New contract rumors to Real Madrid — club denies
```

---

## 📄 TEMPLATE 2 — Lightweight / Fringe Player

*For squad players, WC2026 nations' key men, non-EPL players you're tracking but not deeply.*

*File: `entities/players/Amine Adli.md`*

```markdown
---
type: player
name: Amine Adli
nationality: "[[Morocco]]"
club: "[[Bayer Leverkusen]]"
position: AM
wc2026: true
wc2026_group: C
status: fit
tags: [player, wc2026, morocco, bundesliga]
---

# Amine Adli

> **[[Bayer Leverkusen]]** · AM · 🇲🇦 [[Morocco]] · WC2026 Group C

## Key Facts
- Morocco's creative hub alongside [[Hakim Ziyech]]
- Bundesliga: 8 goals, 11 assists in 2025-26

## News
```dataview
LIST
FROM "entities/news" OR "events"
WHERE contains(file.outlinks, [[Amine Adli]])
SORT file.ctime DESC
LIMIT 8
```

## Log
- 2026-04-10 · Two assists vs Frankfurt
```

---

## 📄 TEMPLATE 3 — Nation Squad Overview

*Not a player note — but this is what lives in `entities/nations/Norway.md`*
*It queries ALL your players dynamically, so you never manually list them.*

```markdown
---
type: nation
name: Norway
confederation: UEFA
wc2026: true
wc2026_group: I
wc2026_group_opponents:
  - "[[France]]"
  - "[[Senegal]]"
  - "[[Iraq]]"
fifa_rank: 26
manager: "[[Stale Solbakken]]"
tags: [nation, wc2026, uefa]
---

# 🇳🇴 Norway — WC 2026

**Group I** · vs [[France]] · [[Senegal]] · [[Iraq]]

## 🔢 Squad (Auto — from player notes)

```dataview
TABLE club, position, status, wc2026_risk
FROM "entities/players"
WHERE nationality = [[Norway]]
  AND wc2026 = true
SORT position ASC
```

## ⚠️ Injury / Risk Watch

```dataview
TABLE name, club, status, injury_detail, wc2026_risk
FROM "entities/players"
WHERE nationality = [[Norway]]
  AND (status != "fit" OR wc2026_risk != "low")
```

## 📰 Latest News

```dataview
LIST
FROM "entities/news" OR "events"
WHERE contains(file.outlinks, [[Norway]])
SORT file.ctime DESC
LIMIT 10
```
```

---

## 🔄 Daily News Update Workflow

### When news comes in, you do THIS:

```
1. Create note in entities/news/
   Filename: 2026-04-24-haaland-injury-doubt.md

2. Fill frontmatter (mandatory):
   type: news
   date: 2026-04-24
   source: Sky Sports
   url: https://source.url/article
   processed: true
   entities:
     - "[[Erling Haaland]]"
     - "[[Manchester City]]"
   tags: [news, injury, wc2026-risk]

3. Write FULL article summary in ## Summary section (3-4 sentences).
   Wikilink EVERY entity mentioned: [[Erling Haaland]] [[Manchester City]] [[Norway]] [[WC 2026]]

4. If it's a STATE CHANGE (injury confirmed, transfer done):
    → Open the player note
    → Update ONLY the relevant YAML fields:
      status: injured
      injury_detail: hamstring strain
      return_date: 2026-05-10
      wc2026_risk: medium
    → Add one line to ## Log section

5. Mark processed: true in the frontmatter.

That's it. The Dataview queries do the rest.
```

### What you NEVER do:
- Copy-paste article text into the player note
- Manually update the "News Feed" section (Dataview handles it)
- Duplicate information across notes
- Use _inbox/ — news goes directly to entities/news/ with full content

---

## 🗓️ Update Schedule

| Frequency | Task |
|-----------|------|
| **Daily** | Process scraped articles — add wikilinks, update status if state changed |
| **After each matchday** | Update `goals`, `assists`, `form_last5` in YAML, add Log entry |
| **Weekly** | Update `market_value_eur`, `wc2026_risk` assessments |
| **On transfer** | Update `club`, `club_since`, `contract_until` |
| **Monthly** | Review `playing_style` notes, update club history table |

---

## 🐍 Python Bridge — What This Exports

When your Python script reads the vault, each player note becomes a row:

```python
{
  "name": "Erling Haaland",
  "nationality": "Norway",        # cleaned from [[Norway]]
  "club": "Manchester City",
  "position": "ST",
  "status": "fit",
  "wc2026": True,
  "wc2026_group": "I",
  "wc2026_risk": "low",
  "goals": 28,
  "xg_total": 26.4,
  "xg_diff": 1.6,
  "form_last5": ["G","G","-","G","G"],
  "market_value_eur": 200000000
}
```

Your Chaos model can then use `xg_diff`, `form_last5`, `status`, and `wc2026_risk`
as direct feature inputs for match prediction λ calculations.

---

*Key principle: the player note is the single source of truth for STATE.
News notes are the archive. Dataview is the bridge. Python is the consumer.*
