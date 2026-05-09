---
name: browser-agent
description: Browser automation with auto-discovery, deterministic recipes, and autonomous repair. Use when automating web tasks, mapping sites, or need browser-based workflows.
---

# browser-agent

Browser automation skill that discovers site structure, executes deterministic recipes, and repairs failures autonomously.

## Core Focus

browser-agent is the **automation framework** — map sites, run recipes, heal failures.

| Capability | Description |
|------------|-------------|
| `map_site` | Auto-discover site structure (Playwright, headless) |
| `run_recipe` | Execute stored navigation/form recipes |
| `heal` | Autorepair failures with LLM + 2 retries |

**Not** a scraping tool — that's the domain-skills' job.

## Quick Start

```bash
# Map a new site
python -m _tools.map_site students.ezralms.com

# Run a recipe
python -m _tools.run_recipe students.ezralms.com login

# Heal after failure
python -m _tools.heal students.ezralms.com
```

## Architecture

```
browser-agent/
├── _backends/                    # Browser automation backends
│   ├── chrome_backend.py         # opencode-browser (real Chrome, login walls)
│   ├── playwright_backend.py      # Playwright (headless, public pages)
│   └── selector_parser.py        # Semantic selector parsing
├── _tools/                       # Core framework tools
│   ├── map_site.py               # Site structure discovery
│   ├── run_recipe.py             # Recipe executor
│   ├── heal.py                   # Autorepair failures
│   └── demo_chrome_backend.py    # Backend demo/test
├── domain-skills/                # Per-site knowledge (extends framework)
│   └── <site>/
│       ├── _meta.yaml            # Backend: chrome|playwright
│       ├── README.md             # Site overview
│       ├── nav.md                # Navigation recipes
│       ├── forms.md              # Form recipes
│       ├── selectors.md          # Verified selectors
│       ├── failures.md           # Site-specific failures
│       └── apis.md               # Discovered endpoints
└── _global-failures.yaml         # Cross-site fix index
```

## Site-Specific Scraping

Site-specific scraping scripts live in their domain-skill folder:

| Site | Scraping Tool | Location |
|------|---------------|----------|
| x.com | Tweet extraction | `domain-skills/x-com/scrape_tweets.py` |
| bbc-sport | Article scraping | `domain-skills/bbc-sport/scrape_articles.py` |

## ⚠️ MANDATORY: Failure-Retry Loop

**Every failure MUST trigger an immediate failure-retry loop.**

```python
# 1. On failure, write to failures.md
def log_failure(site, error, context):
    with open(f"domain-skills/{site}/failures.md", "a") as f:
        f.write(f"\n## {datetime.now()}\n")
        f.write(f"**Error:** {error}\n")
        f.write(f"**Context:** {context}\n")

# 2. Read failures.md immediately
def get_last_failure(site):
    with open(f"domain-skills/{site}/failures.md", "r") as f:
        content = f.read()
    # Parse and return last failure dict

# 3. Retry with failure knowledge
def retry_with_knowledge(site, func, *args):
    failures = get_last_failure(site)
    if failures:
        fix = extract_fix_from_failure(failures)
        # Apply fix before retry
    return func(*args)
```

**This is NOT optional.** Any scraping/tool script must implement failure-retry-loop.

### Failure-Retry Flow

```
Attempt → Fail
    ↓
Write failure to domain-skills/<site>/failures.md
    ↓
Read failures.md (parse last entry)
    ↓
Extract fix/mitigation from failure entry
    ↓
Retry with applied fix
    ↓
Succeed → Done
    ↓
Still fail → Write new failure, retry up to 3×
```

### Required Fields in failures.md

```markdown
## YYYY-MM-DD HH:MM

**Error:** <exact error message>
**Tool:** <which tool failed>
**URL:** <target URL>
**Context:** <what was being attempted>
**Fix Applied:** <what we tried to fix it>
**Status:** RESOLVED|RETRYING|PERSISTENT
```

## Backend Selection

browser-agent supports two backends:

| Backend | Use case | Command |
|---------|----------|---------|
| Playwright (default) | Headless, cross-platform, CI/CD, public pages | `BROWSER_BACKEND=playwright` |
| Chrome (opencode-browser) | Real Chrome with profile, login walls, bot detection | `BROWSER_BACKEND=chrome` |

### ⚠️ MANDATORY RULE: Backend Tag Enforcement

**THIS IS NOT OPTIONAL. ALL TOOLS MUST FOLLOW THIS.**

When a site has `backend: chrome` in its `_meta.yaml` file:
- **ALWAYS use opencode-browser CLI** via `_backends/chrome_backend.py`
- **NEVER use playwright_browser_*** tools (Playwright MCP)
- **NEVER use chrome-devtools_* tools (CDP)**

The `_meta.yaml` tag is the source of truth. If it says `chrome`, you MUST use opencode-browser.

```python
# CORRECT for backend: chrome
from _backends.chrome_backend import ChromeBackend
backend = ChromeBackend()
await backend.launch()
await backend.goto(url)

# WRONG - will fail on x.com and similar
playwright_browser_navigate(url)  # Playwright MCP - NOT allowed
chrome-devtools_navigate_page(url)  # CDP - NOT allowed
```

### Site-based backend selection

Each site in `domain-skills/<site>/_meta.yaml` can declare its backend:

```yaml
backend: playwright  # Default - headless CDP
backend: chrome      # Real Chrome via opencode-browser (for login walls)
```

When `get_backend(site="x.com")` is called, it checks site metadata first, then falls back to `BROWSER_BACKEND` env var, then default (playwright).

**Rule of thumb:**
- **Playwright** — public pages, no login, CI/CD, token-efficient exploration
- **Chrome (opencode-browser)** — login walls, bot detection (Cloudflare, DataDome), sites that fingerprint headless browsers, x.com, banking sites

### Chrome backend setup

1. Install opencode-browser:
   ```bash
   bunx @different-ai/opencode-browser@latest install
   ```

2. Set backend and socket:
   ```bash
   export BROWSER_BACKEND=chrome
   export OPENCODE_BROWSER_SOCKET=/tmp/opencode-browser.sock
   ```

3. Start broker (in separate terminal):
   ```bash
   opencode-browser broker
   ```

### Selector helpers

Both backends support semantic selectors that map to accessibility attributes:

| Syntax | CSS equivalent |
|--------|----------------|
| `label:Email` | `[aria-label="Email"]` |
| `aria:Submit` | `[aria-label="Submit"]` |
| `placeholder:Search` | `[placeholder="Search"]` |
| `name:email` | `[name="email"]` |
| `role:button` | `[role="button"]` |
| `text:Submit` | `text:contains("Submit")` |

## Key Principles

1. **Screenshots first** — understand page before acting
2. **Coordinate clicks default** — bypasses React/framework complexity
3. **DOM as fallback** — only when coordinates won't work
4. **LLM only on failure** — deterministic execution is the happy path
5. **Fix once, reuse** — failures go to domain-skills + global index

## Autorepair Flow

```
Failure detected → Capture context (URL, screenshot, DOM) →
LLM diagnose → Write fix → Retry × 2 → Still fail → Ask user
```

## Recipe Step Format

Steps in nav.md / forms.md use this format:

```markdown
## Login flow

1. [goto] https://site.com/login
2. [wait] #username field visible
3. [type] #username -> {USERNAME}
4. [type] #password -> {PASSWORD}
5. [click] button[type=submit]
6. [wait] .dashboard loaded
7. [verify] url contains /dashboard
```

Supported actions: `goto`, `wait`, `type`, `click`, `verify`, `wait_url`

## Adding a Recipe Manually

1. Edit `domain-skills/<site>/nav.md` or `forms.md`
2. Add a `## <RecipeName>` section
3. Add numbered steps using the format above
4. Commit

## How Failures Are Logged

When a recipe step fails:
1. Context is captured (screenshot, DOM snippet, URL)
2. LLM proposes a fix
3. Fix is written to `domain-skills/<site>/failures.md`
4. If cross-site, fix is also added to `_global-failures.yaml`
5. Retry up to 2×

## ⚠️ MANDATORY: Entity Tracking & Wikilinking

**Every extracted article MUST track and wikilink ALL entities. No exceptions.**

### Entity Tracking Rules

After extracting any article (news, tweets, etc.):

1. **Identify ALL entities** mentioned:
   - Clubs: `[[Arsenal-FC]]`, `[[Real-Madrid]]`
   - Players: `[[Erling-Haaland]]`, `[[Bukayo-Saka]]`
   - Managers/Coaches: `[[Pep-Guardiola]]`, `[[Mikel-Arteta]]`
   - Competitions: `[[Premier-League]]`, `[[Champions-League]]`
   - Nations: `[[England]]`, `[[Brazil]]`
   - Other: `[[Referee-Name]]`, `[[Stadium-Name]]`

2. **Frontmatter entities array** — list every entity:
   ```yaml
   entities:
     - "[[Erling-Haaland]]"
     - "[[Manchester-City]]"
     - "[[Norway]]"
     - "[[Premier-League]]"
   ```

3. **Inline wikilinks** — wikilink every entity in text:
   ```markdown
   ## Summary
   [[Erling-Haaland]] scored twice as [[Manchester-City]] beat [[Arsenal-FC]] 3-1.
   ```

### Entity → Folder Mapping

| Entity Type | Folder |
|-------------|--------|
| Clubs | `entities/clubs/` |
| Players | `entities/players/` |
| Managers/Coaches/Pundits | `entities/persons/` |
| Leagues | `entities/leagues/` |
| Competitions (Cups, UCL, etc.) | `entities/competitions/` |
| Nations | `entities/nations/` |
| Concepts (Title-Race, Transfer, etc.) | `entities/concepts/` |

### Wikilink Conventions

- **Bare wikilinks only**: `[[Manchester-City]]` NOT `[[Clubs/Manchester-City]]`
- **Directory IS the category** — no prefix needed
- **Filenames**: `Premier-League.md`, `Arsenal-FC.md`, `Erling-Haaland.md`
- **Hyphenate everything**: `Premier-League` not `Premier League`

### Entity Management System

```
browser-agent/
├── entities/
│   ├── registry.yaml     # Central entity mapping (source of truth)
│   └── entity_manager.py  # Registry loader + auto-creation
```

**How it works:**
1. `registry.yaml` contains all known entities (clubs, players, managers, competitions, nations)
2. When scraping text, `wikilink_text()` replaces known entities with `[[wikilink]]`
3. Unknown entities trigger `auto_discover_and_create()` → creates entity note in appropriate folder
4. New entities are logged for review and manual categorization

**Registry format** (`registry.yaml`):
```yaml
_clubs:
  Manchester City: Manchester-City
  Arsenal: Arsenal-FC

_players:
  Erling Haaland: Erling-Haaland
  Kylian Mbappe: Kylian-Mbappe

_managers:
  Pep Guardiola: Pep-Guardiola

_competitions:
  Premier League: Premier-League
  Champions League: Champions-League

_auto_create: true  # Enable auto-creation for unknown entities
```

**Entity type → folder mapping:**
| Type | Folder |
|------|--------|
| clubs | `entities/clubs/` |
| players | `entities/players/` |
| persons | `entities/persons/` |
| leagues | `entities/leagues/` |
| competitions | `entities/competitions/` |
| nations | `entities/nations/` |

**Adding new entities:**
1. Edit `entities/registry.yaml` under appropriate category (`_clubs`, `_players`, etc.)
2. Format: `Display Name: wikilink-name`
3. Auto-create creates notes with basic template, manual review needed for full data

### Example: Correct News Note

```markdown
---
type: news
date: 2026-04-25
source: FabrizioRomano
url: https://x.com/FabrizioRomano/status/123
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

## football-news (subskill)

**Trigger:** User says "football-news" or requests football news scraping

**Knowledge Base:** `SkillsRoot/browser-agent/Knowledgebase/` — load before EVERY football-news task. Covers both Obsidian vault management AND football news gathering.

Files in knowledgebase:
- `obsidian-football-vault-structure.md` — vault folder architecture, YAML frontmatter schema, Dataview patterns
- `obsidian-player-note-templates.md` — player note template (Full + Lightweight), nation squad overview, update workflow
- `obsidian-competition-club-nation-templates.md` — competition/club/nation templates (Full + Lightweight), relationship map, update triggers
- `football-reference-2026-LIVE.md` — live league standings, WC2026 groups, UCL/European clubs, Arab leagues data

### OBSIDIAN FOOTBALL NEWS VAULT — SCRAPING RULES

When scraping articles for `C:\Users\jtoem\Assets\News\football\`, these rules are MANDATORY:

#### News Note Structure
```markdown
---
type: news
date: YYYY-MM-DD
source: {Source}
url: {FULL_URL}
processed: true
entities:
  - "[[Entity1]]"
  - "[[Entity2]]"
tags: [news, tag1, tag2, tag3]
---

## Summary
{Full 3-4 sentence summary. Wikilink EVERY entity mentioned inline: clubs, players, managers, competitions, concepts, etc.}
```

#### Rules (No Exceptions)
1. **FULL article text** — not headlines, not excerpts. Full paragraph summaries.
2. **Always include `url:`** — source URL of the article.
3. **Wikilink every entity** — every named thing gets `[[...]]`: `[[Arsenal-FC]]`, `[[Pep-Guardiola]]`, `[[Premier-League]]`, `[[Title-Race]]`, etc.
4. **Entities FIRST, tags SECOND** — `entities:` before `tags:` in frontmatter.
5. **New entity?** → Create it on-the-fly in the correct folder:
   - Managers/coaches/pundits → `Persons/`
   - Players → `Players/`
   - Clubs → `Clubs/`
   - Leagues → `Leagues/`
   - Competitions → `Competitions/`
   - Abstract concepts → `Concepts/`

#### Folder Structure
```
football/
├── Nations/       # country files
├── Clubs/        # clubs
├── Leagues/      # domestic leagues
├── Competitions/ # cups, UCL, WC, etc.
├── Players/      # footballers
├── Persons/      # managers, pundits, owners, referees
└── Concepts/     # Title-Race, Relegation, Transfer, etc.
```

#### WikiLink Conventions
- Bare wikilinks only: `[[Manchester-City]]` NOT `[[Clubs/Manchester-City]]`
- Directory IS the category — no prefix needed
- Filenames: `Premier-League.md`, `Arsenal-FC.md`, `Erling-Haaland.md`

## Reference

- Design: `DESIGN.md`
- Tech stack: Playwright (`playwright.async_api`)

## Session Close Workflow

### Session Close = Document Everything

When the user says "close session" or equivalent, the agent must:

1. **Read `_meta.yaml` fallback log** — check for any fallback selectors that worked during the session
2. **Update `selectors.md`** — for each fallback that succeeded, update the selector priority table
3. **Log new failures** — any failures that occurred go to `troubleshooting.md` (or `_global-failures.yaml` if cross-site)
4. **Update nav.md/forms.md** — any new navigation patterns or forms discovered
5. **Update apis.md** — any new API endpoints observed
6. **Update `_meta.yaml`** — set `last_session_closed`, clear fallback_log

### Session Close Checklist

```markdown
## Session Close Checklist

On "close session":
- [ ] Read _meta.yaml fallback_log
- [ ] Update selectors.md with confirmed working fallbacks
- [ ] Log new failures to troubleshooting.md
- [ ] If cross-site failure → also add to _global-failures.yaml
- [ ] Update nav.md if new navigation patterns discovered
- [ ] Update forms.md if new forms discovered
- [ ] Update apis.md with observed API endpoints
- [ ] Set last_session_closed in _meta.yaml
- [ ] Clear fallback_log in _meta.yaml
```

### Why This Matters

- After exploration mode, documentation should be complete enough that future sessions can run purely from docs, no snapshots
- Fallback usage during a session = confirmed working selectors = update priority tables
- Every session should improve the domain skill for next time
