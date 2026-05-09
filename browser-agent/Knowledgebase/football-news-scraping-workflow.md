# ⚽ Football News Scraping — Sub-Skill Documentation

> Replicable workflow for scraping football news articles and saving them to an Obsidian vault.

---

## 🎯 What This Does

Scrapes football news from multiple sources and saves them as markdown files to:
```
C:\Users\jtoem\Assets\News\football\entities\news\
```

**Important:** The `_inbox/` folder was **removed entirely** from the vault. All articles go directly to `entities/news/`. The old path `entities/news/_inbox/` no longer exists.

---

## 🏗️ Architecture

```
browser-agent/
├── SKILL.md                           # Main skill (trigger + rules)
├── _tools/
│   ├── news_signals.yaml              # Filter config (EXCLUDE/INCLUDE patterns)
│   ├── scrape_articles.py             # Automated scraper (BBC, TeamTalk, etc.)
│   ├── map_site.py                    # Site structure discovery
│   └── run_recipe.py                  # Deterministic recipe runner
└── Knowledgebase/
    ├── obsidian-football-vault-structure.md  # Vault schema (for reference)
    ├── obsidian-player-note-templates.md
    ├── obsidian-competition-club-nation-templates.md
    ├── football-reference-2026-LIVE.md
    └── football-news-scraping-workflow.md  # THIS FILE
```

---

## 📝 Article Markdown Format

### Actual Frontmatter Schema (Used in Practice)

```markdown
---
title: "Article Headline Here"
source: BBC Sport
date: 2026-04-24
tags: [transfer, premier-league, chelsea]
---

Article body text goes here. Full paragraph content, not excerpts.
```

**Note:** We use `title/source/date/tags` — NOT the more complex `entities:` field from the vault-structure.md template. The vault-structure.md shows the ideal schema but our actual implementation is simpler.

### Content Cleaning Rules

These are automatically removed from article text:
- Cookie banners
- Sign-in / log-in prompts
- Subscribe / newsletter blocks
- "Add GOAL.com as a preferred source" prompts
- "Sign up for the latest news" blocks
- Terms & conditions links
- Privacy policy links
- Any line under 30 characters (after stripping)
- Any line containing: `sign in`, `log in`, `subscribe`, `cookie`, `privacy`, `terms`, `get sky sports`, `download the app`

Minimum content length: **80 characters per paragraph**, **200+ chars total article**

---

## 🔄 Two Workflows

### Workflow A: Automated (scrape_articles.py)
**For:** Sites that render server-side (BBC, TeamTalk)

```bash
cd C:\Users\jtoem\.config\opencode\skills\browser-agent\_tools
python scrape_articles.py "BBC Gossip" "https://www.bbc.com/sport/football/gossip" "C:\Users\jtoem\Assets\News\football\entities\news" 10
```

**Process:**
1. Load `news_signals.yaml` filter patterns
2. Visit homepage, extract article links via selectors
3. Filter each article title (EXCLUDE patterns first, then INCLUDE signals)
4. Scrape full content from approved articles
5. Apply content cleaning (remove banners, short lines)
6. Save as `.md` with YAML frontmatter + extracted tags

### Workflow B: Manual (Playwright Browser)
**For:** JS-rendered sites (Goal.com) or when automated scraper fails

**Step 1: Navigate + Extract**
```javascript
// In Playwright evaluate():
() => {
  const title = document.querySelector('h1')?.innerText || document.title;
  const paragraphs = document.querySelectorAll('article p');
  const content = Array.from(paragraphs)
    .map(p => p.innerText)
    .filter(t => t.length > 50)
    .join('\n\n');
  return { title, content, length: content.length };
}
```

**Step 2: Save to Vault**
```powershell
@"
---
title: "{title}"
source: Goal.com
date: 2026-04-24
tags: [transfer, premier-league]
---

{content}
"@ | Out-File -FilePath "C:\Users\jtoem\Assets\News\football\entities\news\slug.md" -Encoding UTF8
```

---

## 📋 Filter Configuration (`news_signals.yaml`)

### EXCLUDE Patterns (filter_out)

**Trackers/Updates:**
- tracker, latest goals, score update, score updates, live, live blog, updates, running blog, minute-by-minute

**Women's Football (EXCLUDE ALL):**
- women's football, women's soccer, women's world cup, wsl, womens super league, nwsl, women's champions league, women's league, women's cup, womens, women's

**Non-Article Pages:**
- terms and conditions, privacy policy, cookie policy, terms of service, legal, sitemap, sign in, log in, register, subscribe

**Match Content:**
- vs, preview, build-up, talking points, talking point

**Transfer Gossip:**
- transfer news, transfer rumours, transfer gossip, transfer talk, transfer update, transfers live, transfer latest, transfer centre, loan, signed, joins, leaves

**Rankings/Standings:**
- rankings, power rankings, standings, tables, leaderboard, form guide

**Betting/Fantasy:**
- odds, betting, betting tips, fantasy, fantasy football, fantasy premier league, fpl, draft, fantasy team, fantasy tips

**Live & Gossip:**
- latest news, latest:, transfer latest, news latest, paper talk, papers, daily mail, express, mirror, star, record, telegraph

**Match Result Patterns (in title):**
- wins over, beat, defeats, lose to, beaten by, thrash, thrashed, see off, come from behind, hold on, hang on, scrape, grind out, edge past, snatching, late winner, last minute, 95th minute, stoppage time, injury time winner, brace, hat-trick, four goals, five goals, goals galore, social media, viral, reaction, responds to

**Team News:**
- team news, predicted lineups, lineups, injuries, suspensions, injury news, injury update

**Statistics:**
- depth charts, watchability, scout report, stat packed, by the numbers, numbers dont lie

### INCLUDE Signals (filter_in)

Only articles containing these signals get scraped (unless excluded by above):

**Breaking/Exclusive:**
- breaking, exclusive, exclusive story

**Transfers:**
- done deal, here we go, signed, signs for, joins, leaves, sold, transfer complete, medical today, agree fee, bid accepted, bid rejected, buyout, release clause, personal terms agreed, contract signed

**Managerial:**
- sacked, dismisses, fires, appoints, appointed, resigns, resigns from, steps down, leaves club, new manager

**Records/Milestones:**
- record, milestone, all time, first time in history, becomes, surpasses, breaks record, reaches milestone, centenary, anniversary

**Deaths/Tragedies:**
- dies, passed away, tragically, in memoriam, obituary, condolences, funeral, killed, accident, collapse

**Major Competitions:**
- wins, champions, wins cup, wins league, win the cup, qualify, qualified, eliminated, knocked out, relegated, promoted

**Scandals/Discipline:**
- investigation, investigation into, scandal, corruption, banned, suspended, sanction, allegations, charges, arrest, lawsuit

**Stadium/Finance:**
- new stadium, stadium plans, ground move, stadium expansion, takeover, takeover bid, sold to, bought by, investment, merger, debt, profit, loss

---

## ✅ Article Quality Rules

1. **Full content only** — no headlines/excerpts, must be 200+ chars
2. **Always include `url`** — source URL in frontmatter
3. **No women's football** — filtered out by default
4. **No match schedules** — unless article has storytelling
5. **No paper talk** — daily mail, express, mirror, star, record, telegraph
6. **No video content** — video, podcast, watch
7. **No transfer gossip roundups** — only individual transfer articles with full reporting

---

## 🧪 Source Status

| Source | Status | URL | Notes |
|--------|--------|-----|-------|
| BBC Gossip | ✅ Working | bbc.com/sport/football/gossip | 8 articles per run. BBC uses `/articles/` URLs for full stories. |
| BBC General | ✅ Working | bbc.com/sport/football | 16 articles. Good for general PL news. |
| TeamTalk | ✅ Working | teespot.co.uk/category/football | Found 3 transfer articles. Initial scrape only got 2 links — needed multiple passes. |
| **Goal.com** | ⚠️ Manual | goal.com/en-us/news | JS-rendered, use Playwright Workflow B. Article titles often include player names first. |
| Sky Sports | ❌ Blocked | skysports.com/football/news | Times out on `/football/news` but direct article URLs work. Selectors need work. |
| ESPN | ❌ Blocked | espn.com/football | Returns NFL/NBA mixed with soccer. Selectors grab wrong sports content. |
| The Athletic | ❌ Blocked | theathletic.com | Paywall. Now redirects to `nytimes.com/athletic`. All content behind subscription. |
| Guardian | ❌ Blocked | theguardian.com/football | Timeouts. |
| Mirror | ❌ Blocked | mirror.co.uk/sport/football | Timeouts. |
| Standard | ❌ Blocked | standard.co.uk/sport/football | Timeouts. |
| Marca | ❌ Blocked | marca.com/futbol | 0 article links found on initial attempts. |
| Transfermarkt | ❌ Blocked | transfermarkt.com | 0 article links found. |

---

## 📁 Vault Structure

```
football/
├── entities/
│   ├── news/          ← ARTICLES GO HERE (NOT _inbox/)
│   │   ├── bbc-*.md
│   │   ├── goal-*.md
│   │   └── teamtalk-*.md
│   ├── clubs/         # Arsenal-FC.md, Real-Madrid.md
│   ├── players/        # Erling-Haaland.md, Lionel-Messi.md
│   ├── nations/        # England.md, Brazil.md
│   ├── coaches/        # Pep-Guardiola.md
│   └── competitions/  # Premier-League.md, Champions-League.md
├── events/
│   ├── matches/
│   ├── transfers/
│   └── injuries/
└── analysis/
```

**Important:** `_inbox/` folder has been **removed entirely**. Do not use `entities/news/_inbox/` — it no longer exists.

---

## 🔧 Working Selectors by Source

### BBC Sport
```yaml
selectors:
  - "a[href*='/sport/football/articles/']"  # Full article links
  - "a[href*='/sport/football/']"            # General football links
article_containers:
  - "article"
  - ".article-body"
  - ".story-body"
```

### TeamTalk / Teespot
```yaml
selectors:
  - "article a"
  - ".headline a"
  - "h2 a"
  - "h3 a"
article_containers:
  - "article"
  - ".content"
```

### Goal.com (JS-rendered - use Playwright)
```yaml
selectors:
  - "article a"
  - ".headline a"
  - "a[href*='/news/']"
  - "a[href*='/lists/']"   # Goal uses /lists/ for articles
article_containers:
  - "article"
  - ".article-body"
```
**Note:** Goal.com requires `page.evaluate()` to extract content — `scrape_articles.py` won't work directly.

---

## 🐍 Python Scraper Usage

```bash
# Basic usage
python scrape_articles.py <source_name> <homepage> [output_dir] [max_articles]

# Scrape BBC gossip
python scrape_articles.py "BBC Gossip" "https://www.bbc.com/sport/football/gossip" "C:\Users\jtoem\Assets\News\football\entities\news" 10

# Scrape TeamTalk transfers
python scrape_articles.py "TeamTalk" "https://www.teespot.co.uk/category/football" "C:\Users\jtoem\Assets\News\football\entities\news" 5
```

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Timeout on page load | Add `wait_until='networkidle'` or increase `page.wait_for_timeout()` |
| No article links found | Check selectors in `news_signals.yaml`; try fallback `a[href*="/articles/"]` |
| Content too short (<200 chars) | Increase min length check (default 80 chars in `clean_content`) |
| JS-rendered content empty | Use Playwright `evaluate()` instead of `scrape_articles.py` |
| Filter blocking valid article | Adjust `filter_in_signals` in `news_signals.yaml` |
| ESPN returns NFL/NBA content | Site mixes sports — use BBC/TeamTalk instead |
| The Athletic paywall | Site redirects to `nytimes.com/athletic` — cross off list |
| Only 2 links from TeamTalk | Initial scrape finds few links — run multiple times or expand selectors |
| Sky Sports times out | Try direct article URLs instead of listing page |

---

## 📝 Session Close Checklist

When done scraping for the session:

- [ ] Count articles in vault — confirm new articles added
- [ ] Spot-check 1-2 articles for full content (not just headlines)
- [ ] Confirm url field is populated in frontmatter
- [ ] Verify no `_inbox/` articles remain (folder removed)
- [ ] Log any failures/skipped sources
- [ ] Update source status table if new sources tested
- [ ] Note any new selectors that worked for future reference

---

## 🔑 Key Decisions Made (For Reference)

- BBC `/sport/football/gossip` page reliable for Premier League transfer rumors
- TeamTalk provides good backup for transfer coverage
- Content minimum raised to 200 chars to filter out empty/short scraped pages
- Filter OUT transfer gossip list pages (roundups, paper talk) — only scrape individual articles
- Goal.com article titles often lead with player name first
- ESPN selector grabs NFL/NBA content first — need soccer-specific path filtering
- The Athletic now redirects to `nytimes.com/athletic` — paywall confirmed
- `_inbox/` removed from vault — articles go directly to `entities/news/`

---

*Last updated: 2026-04-25*