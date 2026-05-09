# 🏆 Obsidian Football Vault — Competition, Club & Nation Templates

> Same "Frozen Body, Live Veins" principle applies to all three.
> YAML = state. Dataview = live surface. Log = append-only history.

---

# ══════════════════════════════════════════════
# PART 1 — COMPETITION TEMPLATES
# ══════════════════════════════════════════════

## 1A — Domestic League
*File: `entities/competitions/Premier League.md`*

```markdown
---
# ═══════════════════════════════
# IDENTITY
# ═══════════════════════════════
type: competition
subtype: domestic_league
name: Premier League
abbreviation: PL
country: "[[England]]"
confederation: UEFA
tier: 1
promotion_from: "[[EFL Championship]]"
relegation_to: "[[EFL Championship]]"

# ═══════════════════════════════
# CURRENT SEASON STATE
# ═══════════════════════════════
season: 2025-26
matchday_current: 34
matchday_total: 38
status: active        # active | completed | suspended | break

# ═══════════════════════════════
# CURRENT STANDINGS SNAPSHOT
# (Update weekly — just the top / battle zones)
# ═══════════════════════════════
leader: "[[Manchester City]]"
leader_pts: 70
title_race:
  - "[[Manchester City]]"
  - "[[Arsenal FC]]"
ucl_spots: 4          # top N qualify for UCL
uel_spot: 5
uecl_spot: 6
relegation_zone:
  - "[[Wolverhampton Wanderers]]"
  - "[[Burnley FC]]"
  - "[[Tottenham Hotspur]]"

# ═══════════════════════════════
# META
# ═══════════════════════════════
top_scorer_player: "[[Erling Haaland]]"
top_scorer_goals: 28
most_assists_player: "[[Mohamed Salah]]"
most_assists_count: 17
tags:
  - competition
  - domestic-league
  - england
  - epl
  - tier-1
---

# 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League 2025–26

> **England** · Tier 1 · 20 clubs · 38 matchdays

---

## 📊 Live Standings

```dataview
TABLE wins AS W, draws AS D, losses AS L, points AS Pts
FROM "data/standings"
WHERE competition = [[Premier League]] AND season = "2025-26"
SORT points DESC
```

---

## 🏟️ Clubs This Season

```dataview
TABLE country, manager, stadium
FROM "entities/clubs"
WHERE league = [[Premier League]]
SORT file.name ASC
```

---

## ⚽ Recent Results

```dataview
TABLE date, home, away, home_score + "-" + away_score AS Score
FROM "events/matches"
WHERE competition = [[Premier League]]
SORT date DESC
LIMIT 10
```

---

## 📅 Upcoming Fixtures

```dataview
TABLE date, home, away
FROM "events/matches"
WHERE competition = [[Premier League]]
  AND home_score = null
SORT date ASC
LIMIT 10
```

---

## 🏆 Title Race

| Club | Pts | GD | Form |
|------|-----|----|------|
| [[Manchester City]] | 70 | +41 | W W D W W |
| [[Arsenal FC]] | 70 | +38 | W W W D W |

---

## ⚠️ Relegation Battle

```dataview
TABLE points, wins, losses
FROM "entities/clubs"
WHERE contains(league, [[Premier League]])
  AND contains([[Premier League]].relegation_zone, file.link)
SORT points ASC
```

---

## 📰 Competition News

```dataview
LIST WITHOUT ID "**[" + date + "]** " + file.name
FROM "entities/news" OR "events"
WHERE contains(file.outlinks, [[Premier League]])
SORT date DESC
LIMIT 12
```

---

## 📋 Log
*Season narrative — append only*

- 2026-04-24 · GW34: Man City and Arsenal still level on 70pts with 4 games left
- 2026-04-01 · Arsenal went top after 2-1 win at Anfield
- 2025-12-26 · Boxing Day: Man City 3-0 Liverpool — title race opened up
- 2025-08-16 · Season opener: Arsenal 2-0 Wolves
```

---

## 1B — European Club Competition
*File: `entities/competitions/Champions League.md`*

```markdown
---
type: competition
subtype: european_club
name: Champions League
abbreviation: UCL
organizer: UEFA
tier: 1           # 1=UCL, 2=UEL, 3=UECL
format: league_phase_then_knockout
clubs_count: 36
season: 2025-26
status: active
current_phase: quarter_finals    # league_phase | r32 | r16 | qf | sf | final

# Current phase details
qf_legs_played: 1
sf_date_first_leg: 2026-04-29
sf_date_second_leg: 2026-05-06
final_date: 2026-05-31
final_venue: "[[Allianz Arena]], Munich"

# Remaining clubs (update each round)
clubs_remaining:
  - "[[Arsenal FC]]"
  - "[[Bayern Munich]]"
  - "[[Real Madrid]]"
  - "[[Inter Milan]]"
  - "[[Paris Saint-Germain]]"
  - "[[FC Barcelona]]"
  - "[[Liverpool FC]]"
  - "[[Borussia Dortmund]]"

league_phase_winner: "[[Arsenal FC]]"   # null until decided
holder: "[[Real Madrid]]"

tags:
  - competition
  - european
  - ucl
  - uefa
---

# 🏆 Champions League 2025–26

> **UEFA** · 36 clubs · League Phase → R16 → QF → SF → Final
> Final: 31 May 2026 · Allianz Arena, Munich

---

## 🗺️ Current Phase: Quarter-Finals

| Tie | Leg 1 | Leg 2 | Agg |
|-----|-------|-------|-----|
| [[Arsenal FC]] vs [[Bayern Munich]] | 2–1 (H) | TBD | 2-1 |
| [[Real Madrid]] vs [[Inter Milan]] | 0–1 (A) | TBD | 0-1 |
| [[Liverpool FC]] vs [[PSG]] | 3–1 (H) | TBD | 3-1 |
| [[Barcelona]] vs [[Dortmund]] | 2–2 (A) | TBD | 2-2 |

---

## 📊 League Phase — Final Standings (Top 10)

| # | Club | W | D | L | Pts |
|---|------|---|---|---|-----|
| 1 | [[Arsenal FC]] | 8 | 0 | 0 | 24 |
| 2 | [[Bayern Munich]] | 7 | 0 | 1 | 21 |
| 3 | [[Liverpool FC]] | 6 | 0 | 2 | 18 |
| 4 | [[Tottenham Hotspur]] | 5 | 2 | 1 | 17 |
| 5 | [[FC Barcelona]] | 5 | 1 | 2 | 16 |

---

## 🏟️ All 36 Clubs This Season

```dataview
TABLE country, league, league_tier
FROM "entities/clubs"
WHERE ucl_2025_26 = true
SORT file.name ASC
```

---

## ⚽ Recent Results

```dataview
TABLE date, home, away, home_score + "-" + away_score AS Score, phase
FROM "events/matches"
WHERE competition = [[Champions League]]
SORT date DESC
LIMIT 10
```

---

## 📰 News

```dataview
LIST WITHOUT ID "**[" + date + "]** " + file.name
FROM "entities/news" OR "events"
WHERE contains(file.outlinks, [[Champions League]])
SORT date DESC
LIMIT 12
```

---

## 📋 Log

- 2026-04-16 · QF Draw: Arsenal-Bayern, Madrid-Inter, Liverpool-PSG, Barca-Dortmund
- 2026-03-18 · R16: Arsenal 5-1 agg vs Sporting CP — dominant
- 2026-01-29 · League phase completed — Arsenal finish 1st (perfect 8/8)
- 2025-09-17 · League phase begins — new 36-club format second season
```

---

## 1C — International Tournament
*File: `entities/competitions/WC 2026.md`*

```markdown
---
type: competition
subtype: international_tournament
name: WC 2026
full_name: FIFA World Cup 2026
abbreviation: WC26
organizer: FIFA
hosts:
  - "[[United States]]"
  - "[[Canada]]"
  - "[[Mexico]]"
teams_count: 48
groups_count: 12
teams_per_group: 4
format: group_then_knockout
status: upcoming       # upcoming | active | completed

# Key dates
date_start: 2026-06-11
date_end: 2026-07-19
final_venue: MetLife Stadium, New Jersey

# Qualified nations by confederation
uefa_count: 16
caf_count: 10
afc_count: 9
conmebol_count: 6
concacaf_count: 6
ofc_count: 1

# Favorites (update as odds shift)
favorites:
  - "[[France]]"
  - "[[England]]"
  - "[[Brazil]]"
  - "[[Spain]]"
  - "[[Argentina]]"
  - "[[Germany]]"

tags:
  - competition
  - international
  - wc2026
  - fifa
---

# 🌍 FIFA World Cup 2026

> 🇺🇸🇨🇦🇲🇽 · 48 nations · 12 groups · Jun 11 – Jul 19, 2026

---

## 🗺️ Groups

| Group | Teams |
|-------|-------|
| A | [[Mexico]] · [[South Korea]] · [[South Africa]] · [[Czech Republic]] |
| B | [[Canada]] · [[Switzerland]] · [[Qatar]] · [[Bosnia & Herzegovina]] |
| C | [[Brazil]] · [[Morocco]] · [[Haiti]] · [[Scotland]] |
| D | [[USA]] · [[Paraguay]] · [[Australia]] · [[Türkiye]] |
| E | [[Germany]] · [[Curaçao]] · [[Ivory Coast]] · [[Ecuador]] |
| F | [[Netherlands]] · [[Japan]] · [[Sweden]] · [[Tunisia]] |
| G | [[Belgium]] · [[Egypt]] · [[Iran]] · [[New Zealand]] |
| H | [[Spain]] · [[Cape Verde]] · [[Saudi Arabia]] · [[Uruguay]] |
| I | [[France]] · [[Senegal]] · [[Iraq]] · [[Norway]] |
| J | [[Argentina]] · [[Algeria]] · [[Austria]] · [[Jordan]] |
| K | [[Portugal]] · [[DR Congo]] · [[Uzbekistan]] · [[Colombia]] |
| L | [[England]] · [[Croatia]] · [[Ghana]] · [[Panama]] |

---

## 🌡️ Risk Watch — Injured / Doubtful WC Stars

```dataview
TABLE nationality, club, status, injury_detail, wc2026_risk
FROM "entities/players"
WHERE wc2026 = true
  AND (status != "fit" OR wc2026_risk != "low")
SORT wc2026_risk DESC
```

---

## 🏆 Qualified Nations

```dataview
TABLE wc2026_group, confederation, fifa_rank, manager
FROM "entities/nations"
WHERE wc2026 = true
SORT wc2026_group ASC
```

---

## 📰 WC2026 News

```dataview
LIST WITHOUT ID "**[" + date + "]** " + file.name
FROM "entities/news" OR "events"
WHERE contains(file.outlinks, [[WC 2026]])
SORT date DESC
LIMIT 15
```

---

## 📋 Log

- 2026-04-01 · Norway confirmed participation — first WC since 1998
- 2026-02-01 · Group draw ceremony in Miami
- 2025-11-21 · 48th qualifier confirmed
- 2025-09-10 · Host venues finalised — 16 stadiums across 3 nations
```

---

# ══════════════════════════════════════════════
# PART 2 — CLUB TEMPLATES
# ══════════════════════════════════════════════

## 2A — Full Club Note (Top League)
*File: `entities/clubs/Arsenal FC.md`*

```markdown
---
# ═══════════════════════════════
# IDENTITY (Never changes)
# ═══════════════════════════════
type: club
name: Arsenal FC
abbreviation: ARS
nickname: The Gunners
founded: 1886
country: "[[England]]"
city: London
confederation: UEFA

# ═══════════════════════════════
# CURRENT STATE
# ═══════════════════════════════
league: "[[Premier League]]"
league_tier: 1
league_rank: 2
league_pts: 70
manager: "[[Mikel Arteta]]"
stadium: Emirates Stadium
stadium_capacity: 60704
shirt_colors: red, white

# ═══════════════════════════════
# SEASON STATE (Update weekly)
# ═══════════════════════════════
season: 2025-26
season_wins: 21
season_draws: 7
season_losses: 5
goals_for: 68
goals_against: 29
goal_diff: 39
form_last5: [W, W, W, D, W]

# ═══════════════════════════════
# EUROPEAN COMPETITION
# ═══════════════════════════════
ucl_2025_26: true
ucl_phase: quarter_finals
ucl_opponent: "[[Bayern Munich]]"
uel_2025_26: false
uecl_2025_26: false

# ═══════════════════════════════
# WC2026 PLAYERS
# ═══════════════════════════════
wc2026_nations_represented:
  - "[[England]]"
  - "[[Spain]]"
  - "[[Brazil]]"
  - "[[Norway]]"
  - "[[Ghana]]"

# ═══════════════════════════════
# TRANSFER WINDOW
# ═══════════════════════════════
transfer_budget_est_eur: 150000000
key_targets: []
outgoing_rumors: []

tags:
  - club
  - epl
  - england
  - london
  - ucl
  - tier-1
---

# 🔴 Arsenal FC

> **[[Premier League]]** · Rank 2 · 70pts · [[Emirates Stadium]]
> Manager: [[Mikel Arteta]] · UCL: Quarter-Finals

---

## 🧬 Club Profile

| | |
|--|--|
| **Founded** | 1886 |
| **Stadium** | Emirates Stadium (60,704) |
| **City** | London, [[England]] |
| **Manager** | [[Mikel Arteta]] |
| **Colors** | Red & White |
| **Rivals** | [[Tottenham Hotspur]] · [[Chelsea FC]] · [[Manchester United]] |

---

## 📊 2025–26 Season

| | |
|--|--|
| **League** | [[Premier League]] |
| **Rank** | 2nd |
| **Record** | `= this.season_wins`W `= this.season_draws`D `= this.season_losses`L |
| **GD** | `= this.goal_diff` |
| **Form** | `= this.form_last5` |
| **UCL Phase** | `= this.ucl_phase` |

---

## 👥 First Team Squad

```dataview
TABLE nationality, position, status, goals, assists
FROM "entities/players"
WHERE club = [[Arsenal FC]]
SORT position ASC, file.name ASC
```

---

## 🌍 WC2026 Players at This Club

```dataview
TABLE nationality, position, wc2026_group, wc2026_risk
FROM "entities/players"
WHERE club = [[Arsenal FC]]
  AND wc2026 = true
SORT nationality ASC
```

---

## ⚽ Recent Results

```dataview
TABLE date, home, away, home_score + "-" + away_score AS Score, competition
FROM "events/matches"
WHERE home = [[Arsenal FC]] OR away = [[Arsenal FC]]
SORT date DESC
LIMIT 10
```

---

## 📅 Upcoming Fixtures

```dataview
TABLE date, home, away, competition
FROM "events/matches"
WHERE (home = [[Arsenal FC]] OR away = [[Arsenal FC]])
  AND home_score = null
SORT date ASC
LIMIT 5
```

---

## 🔄 Transfer Activity

```dataview
TABLE date, summary, type
FROM "events/transfers"
WHERE club = [[Arsenal FC]]
SORT date DESC
LIMIT 8
```

---

## 🩺 Injury Room

```dataview
TABLE player, injury_detail, return_date
FROM "events/injuries"
WHERE club = [[Arsenal FC]]
  AND return_date >= date(today)
```

---

## 📰 News Feed

```dataview
LIST WITHOUT ID "**[" + date + "]** " + file.name
FROM "entities/news" OR "events"
WHERE contains(file.outlinks, [[Arsenal FC]])
SORT date DESC
LIMIT 15
```

---

## 🏆 Honours (Static Reference)

| Trophy | Count | Last Won |
|--------|-------|----------|
| Premier League | 13 | 2004 |
| FA Cup | 14 | 2020 |
| Champions League | 0 | — |
| UEFA Cup Winners' Cup | 1 | 1994 |

---

## 📋 Log
*Append-only. Season narrative + key events.*

- 2026-04-24 · UCL QF first leg: Arsenal 2-1 Bayern Munich (home)
- 2026-04-20 · PL GW34: Arsenal 2-1 Man City — back level on points
- 2026-03-05 · UCL R16: Arsenal 5-1 agg vs Sporting CP (qualified)
- 2025-11-10 · Arteta signs contract extension through 2028
- 2025-08-16 · Season opener: Arsenal 2-0 Wolves
```

---

## 2B — Lightweight Club Note
*For clubs you track but don't deep-dive — Saudi Pro, Arab leagues, Championship, etc.*

*File: `entities/clubs/Al-Hilal.md`*

```markdown
---
type: club
name: Al-Hilal
abbreviation: HIL
country: "[[Saudi Arabia]]"
city: Riyadh
league: "[[Saudi Pro League]]"
league_tier: 1
manager: "[[Jorge Jesus]]"
stadium: Kingdom Arena
founded: 1957
form_last5: [W, W, W, D, W]
tags:
  - club
  - saudi-pro-league
  - saudi-arabia
  - arab-league
---

# 🔵 Al-Hilal

> **[[Saudi Pro League]]** · [[Saudi Arabia]] · Manager: [[Jorge Jesus]]

## Key Players
- [[Neymar Jr]] *(if fit)*
- [[Rúben Neves]]
- [[Kalidou Koulibaly]]
- [[Aleksandar Mitrović]]

## News
```dataview
LIST WITHOUT ID "**[" + date + "]** " + file.name
FROM "entities/news" OR "events"
WHERE contains(file.outlinks, [[Al-Hilal]])
SORT date DESC
LIMIT 8
```

## Log
- 2026-04-10 · 3-0 vs Al-Ittihad — top of SPL with 5 games to go
```

---

# ══════════════════════════════════════════════
# PART 3 — NATION TEMPLATES
# ══════════════════════════════════════════════

## 3A — Full Nation Note (WC2026 Qualifier)
*File: `entities/nations/France.md`*

```markdown
---
# ═══════════════════════════════
# IDENTITY
# ═══════════════════════════════
type: nation
name: France
emoji: 🇫🇷
confederation: UEFA
fa_name: FFF
fifa_rank: 2

# ═══════════════════════════════
# WC2026 STATE
# ═══════════════════════════════
wc2026: true
wc2026_group: I
wc2026_group_opponents:
  - "[[Senegal]]"
  - "[[Iraq]]"
  - "[[Norway]]"
wc2026_seeded: true
wc2026_win_odds: 6.0     # decimal odds — update as tournament approaches
wc2026_risk_assessment: low

# ═══════════════════════════════
# MANAGEMENT
# ═══════════════════════════════
manager: "[[Didier Deschamps]]"
manager_since: 2012-07-08
assistant_manager: "[[Guy Stephan]]"

# ═══════════════════════════════
# TACTICAL PROFILE
# ═══════════════════════════════
preferred_formation: 4-3-3
tactical_style: possession_counter   # possession | counter | high_press | direct
defensive_strength: 9    # 1-10
attacking_strength: 9
set_piece_threat: 8
squad_depth: 10

# ═══════════════════════════════
# KEY INJURY FLAGS (Update when news breaks)
# ═══════════════════════════════
key_player_status:
  - player: "[[Kylian Mbappé]]"
    status: fit
  - player: "[[Antoine Griezmann]]"
    status: fit
  - player: "[[Aurélien Tchouaméni]]"
    status: doubt

tags:
  - nation
  - wc2026
  - uefa
  - group-i
  - favorite
---

# 🇫🇷 France — WC 2026

> **Group I** · vs [[Senegal]] · [[Iraq]] · [[Norway]]
> Manager: [[Didier Deschamps]] · FIFA Rank: #2

---

## 🗺️ Group I Overview

| Nation | FIFA Rank | WC2026 Odds | Strength |
|--------|-----------|-------------|----------|
| [[France]] | 2 | 6.0 | ⭐⭐⭐⭐⭐ |
| [[Senegal]] | 18 | 90.0 | ⭐⭐⭐ |
| [[Norway]] | 26 | 40.0 | ⭐⭐⭐ |
| [[Iraq]] | 58 | 500.0 | ⭐⭐ |

*France are heavy favorites to top this group.*

---

## 🧠 Tactical Profile

**Formation:** 4-3-3 / 4-2-3-1

France under Deschamps prioritize defensive solidity as the foundation, with
rapid transitions through [[Kylian Mbappé]] and wide runners. Set pieces are
a genuine weapon. Mid-block, then explode on turnover.

Relevant for [[Chaos Model]]: high defensive_strength (9) should translate to
low goals-against λ in predictions.

---

## 👥 WC2026 Squad — Key Men

```dataview
TABLE club, position, status, wc2026_risk
FROM "entities/players"
WHERE nationality = [[France]]
  AND wc2026 = true
SORT position ASC
```

---

## ⚠️ Injury & Risk Watch

```dataview
TABLE name, club, status, injury_detail, wc2026_risk
FROM "entities/players"
WHERE nationality = [[France]]
  AND (status != "fit" OR wc2026_risk != "low")
```

---

## ⚽ Recent International Results

```dataview
TABLE date, home, away, home_score + "-" + away_score AS Score, competition
FROM "events/matches"
WHERE (home = [[France]] OR away = [[France]])
  AND type = "match"
SORT date DESC
LIMIT 8
```

---

## 🆚 Head-to-Head vs Group Opponents

### vs [[Senegal]]
```dataview
TABLE date, home, away, home_score + "-" + away_score AS Score
FROM "events/matches"
WHERE (home = [[France]] AND away = [[Senegal]])
  OR (home = [[Senegal]] AND away = [[France]])
SORT date DESC
LIMIT 5
```

### vs [[Norway]]
```dataview
TABLE date, home, away, home_score + "-" + away_score AS Score
FROM "events/matches"
WHERE (home = [[France]] AND away = [[Norway]])
  OR (home = [[Norway]] AND away = [[France]])
SORT date DESC
LIMIT 5
```

### vs [[Iraq]]
```dataview
TABLE date, home, away, home_score + "-" + away_score AS Score
FROM "events/matches"
WHERE (home = [[France]] AND away = [[Iraq]])
  OR (home = [[Iraq]] AND away = [[France]])
SORT date DESC
LIMIT 5
```

---

## 📰 News Feed

```dataview
LIST WITHOUT ID "**[" + date + "]** " + file.name
FROM "entities/news" OR "events"
WHERE contains(file.outlinks, [[France]])
SORT date DESC
LIMIT 12
```

---

## 🏆 Tournament History

| Tournament | Year | Result |
|-----------|------|--------|
| World Cup | 2022 | 🥈 Runner-Up |
| World Cup | 2018 | 🥇 Champions |
| World Cup | 2014 | QF |
| World Cup | 2010 | Group Stage |
| Euro 2024 | 2024 | SF |

---

## 📋 Log
*Append-only. International window results + key squad news.*

- 2026-04-01 · Mbappé confirmed fit after knee scare — WC2026 risk back to low
- 2026-03-28 · Friendly vs Germany: France 2-1. Deschamps tests 4-2-3-1
- 2026-02-01 · WC2026 Draw: France in Group I — softest possible group
- 2025-11-15 · Final qualifier confirmed 2-0 vs Denmark
```

---

## 3B — Lightweight Nation Note
*For nations you track for WC2026 context but not deep analytics.*

*File: `entities/nations/Iraq.md`*

```markdown
---
type: nation
name: Iraq
emoji: 🇮🇶
confederation: AFC
fifa_rank: 58
wc2026: true
wc2026_group: I
wc2026_group_opponents:
  - "[[France]]"
  - "[[Senegal]]"
  - "[[Norway]]"
wc2026_seeded: false
manager: "[[Jesús Casas]]"
preferred_formation: 4-4-2
tactical_style: direct
defensive_strength: 5
attacking_strength: 5
squad_depth: 4
wc2026_win_odds: 500.0
wc2026_risk_assessment: high   # high = unlikely to advance
tags:
  - nation
  - wc2026
  - afc
  - group-i
---

# 🇮🇶 Iraq — WC 2026

> **Group I** · vs [[France]] · [[Senegal]] · [[Norway]]
> Manager: [[Jesús Casas]] · FIFA Rank: #58

## Context
Iraq's WC2026 debut — qualified through AFC play-offs.
First World Cup since 1986. Expected group stage exit.

## Key Players
- [[Amjad Attwan]] — striker, top scorer in qualification
- [[Bashar Resan]] — captain, defensive linchpin

## News
```dataview
LIST
FROM "entities/news" OR "events"
WHERE contains(file.outlinks, [[Iraq]])
SORT date DESC
LIMIT 8
```

## Log
- 2026-02-01 · Drawn into Group I with France, Senegal, Norway
- 2025-11-20 · Qualified via AFC third round — historic
```

---

# ══════════════════════════════════════════════
# PART 4 — RELATIONSHIP MAP
# ══════════════════════════════════════════════
# How all four note types link to each other:

## Wikilink Graph

```
[[WC 2026]]
  └── contains group → [[France]] (nation)
        └── wc2026_group_opponents → [[Norway]], [[Senegal]], [[Iraq]]
        └── has player → [[Kylian Mbappé]] (player)
              └── plays for → [[Real Madrid]] (club)
                    └── competes in → [[Champions League]] (competition)
                          └── current_phase → quarter_finals
                                └── match note → [[2026-04-15-Real Madrid-vs-Arsenal]]

News note → [[_inbox/2026-04-20-mbappe-injury-scare]]
  └── outlinks → [[Kylian Mbappé]], [[France]], [[WC 2026]], [[Real Madrid]]
  └── auto-surfaces in:
        - Mbappé's ## News Feed (Dataview)
        - France's ## News Feed (Dataview)
        - WC 2026's ## News (Dataview)
        - Real Madrid's ## News Feed (Dataview)
```

One news note. Four entity notes updated. Zero manual work.

---

# ══════════════════════════════════════════════
# PART 5 — QUICK REFERENCE: WHAT UPDATES WHEN
# ══════════════════════════════════════════════

| Event | Notes to update | Fields |
|-------|----------------|--------|
| Match result | Match note (create) | All scores, stats |
| | Club note | `form_last5`, `league_rank`, `league_pts` + Log |
| | Competition note | Log only |
| Injury confirmed | Player note | `status`, `injury_detail`, `return_date`, `wc2026_risk` |
| | Club note | Nothing (Dataview pulls it) |
| | Nation note | `key_player_status` array |
| Transfer done | Player note | `club`, `club_since`, `contract_until` |
| | Old club note | Remove from squad (or Dataview handles it) |
| | New club note | Log entry |
| News article | Inbox note (create) | Add wikilinks — everything else is Dataview |
| Standings update | Club note | `league_rank`, `league_pts`, `season_wins/draws/losses` |
| | Competition note | `leader`, `leader_pts` + Log |
| Squad injury wave | Nation note | `key_player_status` + `wc2026_risk_assessment` |
| Tournament result | Competition note | `current_phase`, `clubs_remaining` + Log |

---

*The vault is a living database, not a document archive.*
*Add wikilinks generously — every link is an edge in your graph.*
*Python reads the YAML. Obsidian reads the graph. You read the analysis.*
