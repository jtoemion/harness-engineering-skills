---
name: browser-agent
description: Browser automation with auto-discovery, deterministic recipes, and autonomous repair. Use when automating web tasks, mapping sites, or need browser-based workflows.
---

# browser-agent

Browser automation skill that discovers site structure, executes deterministic recipes, and repairs failures autonomously.

## Quick Start

```bash
# Map a new site
browser-harness <<'PY'
import sys
sys.path.insert(0, "C:/Users/jtoem/.config/opencode/skills/browser-agent/_tools")
from map_site import map_site
map_site("students.ezralms.com")
PY

# Run a recipe
browser-harness <<'PY'
import sys
sys.path.insert(0, "C:/Users/jtoem/.config/opencode/skills/browser-agent/_tools")
from run_recipe import run_recipe
run_recipe("students.ezralms.com", "login")
PY
```

## Architecture

```
browser-agent/
├── _global-failures.yaml    # Cross-site fix index
├── _tools/
│   ├── map-site.py          # Auto-discover site structure
│   ├── run-recipe.py        # Execute deterministic recipe
│   └── heal.py              # Autorepair with LLM + 2 retries
└── domain-skills/           # Per-site knowledge (auto-created)
    └── <site>/
        ├── README.md        # Site overview
        ├── nav.md           # Navigation recipes
        ├── forms.md         # Form recipes
        ├── apis.md          # Discovered endpoints
        ├── failures.md      # Site-specific failures
        └── _meta.yaml       # Auto-generated metadata
```

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
3. [type] #username → {USERNAME}
4. [type] #password → {PASSWORD}
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

## Reference

- Design: `DESIGN.md`
- Browser harness helpers: `C:\Users\jtoem\Repo\browser-harness\helpers.py`
