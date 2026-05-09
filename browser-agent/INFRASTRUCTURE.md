# Browser-Agent Skill — Complete Infrastructure Documentation

**Generated:** 2026-04-26
**Status:** Production Ready

---

## 1. High-Level Architecture

```
browser-agent/
├── SKILL.md                    # Main skill entry point (this file)
├── DESIGN.md                  # Design decisions & architecture
├── _global-failures.yaml       # Cross-site failure index
├── .env                      # Environment variables (API keys)
│
├── _backends/                 # Browser automation abstractions
│   ├── __init__.py           # BrowserBackend abstract class + get_backend()
│   ├── chrome_backend.py     # opencode-browser CLI integration
│   ├── playwright_backend.py # Playwright async API
│   ├── selector_parser.py     # Semantic selector parsing
│   └── CHROME_BACKEND.md    # Chrome backend docs
│
├── _tools/                   # Core framework tools
│   ├── map_site.py           # Site auto-discovery + documentation
│   ├── run_recipe.py        # Execute deterministic recipes
│   ├── heal.py              # Failure detection + LLM repair + retry
│   ├── scrape_articles.py   # Article scraping framework
│   ├── fetch_tweets.py     # X.com tweet extraction
│   └── self_test.py        # Backend self-test
│
├── domain-skills/             # Per-site knowledge (50+ sites)
│   ├── <site>/
│   │   ├── _meta.yaml      # Backend config, timestamps, fallback_log
│   │   ├── README.md     # Site overview
│   │   ├── nav.md       # Navigation recipes
│   │   ├── forms.md     # Form filling recipes
│   │   ├── selectors.md # Verified selectors + fallbacks
│   │   ├── apis.md     # Discovered endpoints
│   │   └── troubleshooting.md # Site-specific failures + fixes
│   │
│   ├── bbc-sport/
│   ├── sky-sports/
│   ├── x-com/
│   └── ... (50+ more sites)
│
├── entities/                 # Football entity management
│   ├── registry.yaml        # Central entity mapping (clubs, players, managers)
│   ├── entity_manager.py   # Registry loader + auto-creation
│   ├── check_missing.py    # Missing entity detector
│   └── scan_news.py        # News entity scanner
│
├── football-news/            # Football news tracking system
│   ├── news-tracker.py    # News article tracker
│   ├── init-tracker.py    # Tracker initializer
│   ├── score.py          # Article scoring
│   ├── news-value.yaml    # News value weights
│   └── SKILL.md          # Football news subskill
│
└── Knowledgebase/          # Football knowledge reference
    ├── obsidian-football-vault-structure.md
    ├── obsidian-player-note-templates.md
    ├── obsidian-competition-club-nation-templates.md
    └── football-reference-2026-LIVE.md
```

---

## 2. Core Components

### 2.1 Backend Abstraction (`_backends/`)

**Abstract Interface (BrowserBackend):**

```python
class BrowserBackend(ABC):
    async def launch(self, headless=False)        → BrowserBackend
    async def new_page(self)                     → Page
    async def goto(self, url, wait_until)     → Self
    async def query_selector(selector)      → Element | None
    async def click(selector)           → Bool
    async def fill(selector, value)      → Bool
    async def press(selector, key)       → Bool
    async def screenshot(path)           → Bool
    async def close(self)               → None
    
    @property
    def url(self)                     → String
```

#### Backend Implementations

| Backend | Use Case | Implementation |
|---------|---------|----------------|
| **Playwright** | Headless, CI/CD, public pages | `_backends/playwright_backend.py` |
| **Chrome** (opencode-browser) | Login walls, bot detection, x.com | `_backends/chrome_backend.py` |

**Backend Resolution Order:**
1. `_meta.yaml` → `backend:` field (site-specific)
2. Environment → `BROWSER_BACKEND` env var
3. Default → `playwright`

```python
# Usage
from _backends import get_backend
backend = get_backend(site="x.com")  # Returns ChromeBackend
backend = get_backend()            # Returns PlaywrightBackend
```

---

### 2.2 Site Mapping (`map_site.py`)

**Purpose:** Auto-discover a site's structure and output documentation.

**Process:**
```
1. goto URL
2. Crawl → follow same-origin links, collect URL patterns
3. Intercept → capture XHR/fetch endpoints via network events
4. Inspect DOM → find forms, buttons, inputs, navigation
5. Verify selectors → reload, test stability
6. Write → populate domain-skills/<site>/
```

**Output Files (per site):**
| File | Purpose |
|------|---------|
| `_meta.yaml` | Timestamps, pages count, endpoints, backend |
| `README.md` | Site overview, URL, framework, entry points |
| `nav.md` | Discovered routes and navigation patterns |
| `forms.md` | Form structures with selectors |
| `selectors.md` | Verified selectors with fallback priority |
| `apis.md` | Discovered API endpoints |

**Invocation:**
```bash
python -m _tools.map_site students.ezralms.com
# or
from _tools.map_site import map_site
await map_site("students.ezralms.com")
```

---

### 2.3 Recipe Execution (`run_recipe.py`)

**Purpose:** Load a domain skill and execute it deterministically.

**Step Format (in nav.md / forms.md):**
```markdown
## Login flow

1. [goto] https://site.com/login
2. [wait] #username field visible
3. [type] #username → {USERNAME}
4. [type] #password → {PASSWORD}
5. [click] button[type=submit]
6. [wait] .dashboard loaded
7. [verify] url contains /dashboard
```

**Supported Actions:**
- `[goto]` — Navigate to URL
- `[wait]` — Wait for selector
- `[type]` — Type into element
- `[click]` — Click element
- `[press_enter]` — Press Enter key
- `[submit]` — Submit form
- `[verify]` — Verify JS expression
- `[wait_url]` — Wait for URL pattern
- `[screenshot]` — Take screenshot

**Fallback System:**
- Loads `selectors.md` priority tables
- On primary selector failure, tries fallbacks
- Logs fallback usage to `_meta.yaml` → `fallback_log[]`

**Invocation:**
```bash
python -m _tools.run_recipe students.ezralms.com login
# or
from _tools.run_recipe import run_recipe
await run_recipe("students.ezralms.com", "login")
```

---

### 2.4 Autorepair (`heal.py`)

**Purpose:** Detect failure → LLM diagnose → write fix → retry (2×) → escalate.

**Flow:**
```
1. Failure detected
2. Capture context (URL, screenshot, DOM snippet)
3. Query LLM (OpenRouter/Gemini) for diagnosis
4. Write fix to troubleshooting.md
5. If cross-site fix → also write to _global-failures.yaml
6. Retry up to 2×
7. Still failing → escalate to user
```

**Failure Entry Format (troubleshooting.md):**
```markdown
## site: selector-not-found

### First seen
2026-04-26

### Recipe
login

### Failed step
[type] #username → {USERNAME}

### Symptom
Selector #username not found on page

### Fix
Use [name="email"] instead

### Confidence
high

### Status
Auto-repair verified
```

**LLM Integration:**
- Uses OpenRouter API (free tier) or Gemini as fallback
- Returns JSON: `{symptom, fix, confidence, is_cross_site}`

---

## 3. Domain Skills Structure

**Current Sites (50+):**

### English Sources
| Site | Purpose | Backend |
|------|---------|---------|
| `bbc-sport` | BBC Sport news | playwright |
| `sky-sports` | Sky Sports | playwright |
| `guardian-football` | Guardian Football | playwright |
| `football365` | Football365 | playwright |
| `bleacher-report` | Bleacher Report | playwright |
| `thesetpieces` | The Set Pieces | playwright |

### Spanish Sources
| Site | Purpose | Backend |
|------|---------|---------|
| `marca` | MARCA | playwright |
| `as-spain` | AS | playwright |
| `sport-spain` | Sport | playwright |
| `record-pt` | Record (PT) | playwright |

### Italian Sources
| Site | Purpose | Backend |
|------|---------|---------|
| `gazzetta-dello-sport` | Gazzetta dello Sport | playwright |
| `corriere-dellosport` | Corriere dello Sport | playwright |
| `tuttosport` | Tuttosport | playwright |
| `football-italia` | Football Italia | playwright |

### German Sources
| Site | Purpose | Backend |
|------|---------|---------|
| `kicker` | Kicker | playwright |
| `sport-bild` | Sport Bild | playwright |

### French Sources
| Site | Purpose | Backend |
|------|---------|---------|
| `lequipe` | L'Équipe | playwright |

### Data/Stats Sources
| Site | Purpose | Backend |
|------|---------|---------|
| `transfermarkt` | Transfermarkt | playwright |
| `fbref` | FBref | playwright |
| `whoscored` | WhoScored | playwright |
| `sofascore` | SofaScore | playwright |
| `opta` | Opta | playwright |
| `statsbomb` | Statsbomb | playwright |
| `squawka` | Squawka | playwright |

### Special Sources
| Site | Purpose | Backend |
|------|---------|---------|
| `x-com` | X.com (Twitter) | **chrome** |
| `students-ezralms-com` | LMS system | playwright |

---

## 4. Entity Management System

### 4.1 Registry (`entities/registry.yaml`)

**Central entity mapping for football wikilinking:**

```yaml
_clubs:
  Manchester City: Manchester-City
  Arsenal: Arsenal-FC
  ...

_players:
  Erling Haaland: Erling-Haaland
  Bukayo Saka: Bukayo-Saka
  ...

_managers:
  Pep Guardiola: Pep-Guardiola
  Mikel Arteta: Mikel-Arteta
  ...

_competitions:
  Premier League: Premier-League
  Champions League: Champions-League
  ...

_nations:
  England: England
  Spain: Spain
  ...

_auto_create: true  # Enable auto-creation
```

### 4.2 Entity → Folder Mapping

| Entity Type | Folder | Example |
|------------|--------|---------|
| clubs | `entities/clubs/` | `Manchester-City.md` |
| players | `entities/players/` | `Erling-Haaland.md` |
| managers/coaches | `entities/persons/` | `Pep-Guardiola.md` |
| competitions | `entities/competitions/` | `Champions-League.md` |
| nations | `entities/nations/` | `England.md` |

### 4.3 Wikilink Conventions

- **Bare wikilinks only:** `[[Manchester-City]]` NOT `[[Clubs/Manchester-City]]`
- **Directory IS the category** — no prefix needed
- **Filenames:** Hyphenated: `Premier-League.md`, `Erling-Haaland.md`

---

## 5. Football News Subskill

### 5.1 News Tracker (`football-news/`)

**Purpose:** Track and score football news articles from multiple sources.

**Components:**
- `news-tracker.py` — Main tracker (inserts scraped articles)
- `init-tracker.py` — Tracker initializer
- `score_news.py` — Article value scorer
- `news-value.yaml` — News value weights by source/relevance

**Scoring Matrix:**
| Factor | Weight |
|--------|-------|
| Breaking/Exclusive | +50 |
| Transfer news | +30 |
| Injury news | +25 |
| Contract renewal | +20 |
| Match result | +15 |
| Rumor | -10 |
| Quote-only | -20 |

---

## 6. Global Failure System

### 6.1 Cross-Site Failures (`_global-failures.yaml`)

**Purpose:** Single lookup for cross-site reusable fixes.

**When to add globally:**
- Fix applies to 2+ different sites
- Fix is framework-level (e.g., React combobox needs Escape)
- Fix is interaction-level (e.g., file upload needs DOM API)

**Entry Format:**
```yaml
failures:
  - id: react-combobox-no-commit
    symptom: "Dropdown selection not committing on click"
    sites: [github, linkedin, salesforce]
    fix: "Press Escape after selection to commit"
    confidence: high
    first_seen: 2026-04-23
    last_verified: 2026-04-26
```

---

## 7. Knowledgebase

### 7.1 Live League Data (`Knowledgebase/football-reference-2026-LIVE.md`)

**Contains:**
- WC2026 group standings
- Premier League table
- La Liga table
- Bundesliga table
- Serie A table
- Ligue 1 table
- MLS standings
- Arab leagues club lists
- UCL club list

### 7.2 Obsidian Templates

| File | Purpose |
|------|---------|
| `obsidian-football-vault-structure.md` | Vault architecture + Dataview |
| `obsidian-player-note-templates.md` | Player note template |
| `obsidian-competition-club-nation-templates.md` | Competition/Club/Nation templates |

---

## 8. Environment Variables

**From `.env`:**
```bash
# Browser Backend
BROWSER_BACKEND=playwright  # or chrome

# LLM APIs (for heal.py autorepair)
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=openrouter/free
GEMINI_API_KEY=...

# Chrome Backend
CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
CHROME_PROFILE=Default
OPENCODE_BROWSER_CLI=...  # path to cli.js
```

---

## 9. Key Principles

1. **Deterministic execution, LLM for recovery** — Navigation/forms are code paths; LLM only on failure
2. **Coordinate clicks + screenshots first** — DOM only when coordinates won't work
3. **Domain skill is single source of truth** — All site knowledge in `domain-skills/<site>/`
4. **Fixes are append-only** — Never delete failure entry, only append fix
5. **Cross-site fixes live once** — `_global-failures.yaml` prevents duplication
6. **Entity tracking mandatory** — All scraped articles must wikilink entities

---

## 10. Session Close Workflow

On "close session":
1. Read `_meta.yaml` → `fallback_log`
2. Update `selectors.md` with confirmed working fallbacks
3. Log new failures to `troubleshooting.md`
4. If cross-site → also add to `_global-failures.yaml`
5. Update `nav.md` if new navigation patterns discovered
6. Update `forms.md` if new forms discovered
7. Update `apis.md` with observed API endpoints
8. Set `last_session_closed` in `_meta.yaml`
9. Clear `fallback_log` in `_meta.yaml`

---

## Summary

The **browser-agent** skill is a comprehensive browser automation framework with:

- ✅ **Two backends** — Playwright (headless) + Chrome (real browser with profile)
- ✅ **Three core tools** — map_site, run_recipe, heal
- ✅ **50+ domain skills** — Per-site knowledge + selectors
- ✅ **Entity system** — Football entity registry for wikilinking
- ✅ **Global failure index** — Cross-site reusable fixes
- ✅ **Football news subskill** — News tracking + scoring
- ✅ **Knowledgebase** — Live league data + Obsidian templates
- ✅ **Autorepair** — LLM-powered failure diagnosis + retry