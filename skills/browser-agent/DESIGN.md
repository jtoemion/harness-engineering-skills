# Browser-Agent Design

**Date:** 2026-04-23
**Status:** Approved

---

## Problem

Browser automation today is brittle — selectors break, sites change, and every failure is re-debugged from scratch. No systematic auto-discovery, no autonomous repair, no consistent per-site organization.

---

## Architecture

```
~/.config/opencode/skills/browser-agent/
├── SKILL.md                    # Main skill doc (entry point)
├── _global-failures.yaml       # Cross-site failure index (root level)
├── _tools/
│   ├── map-site.py             # Site auto-discovery + documentation
│   ├── run-recipe.py           # Execute deterministic recipe
│   └── heal.py                 # Failure detection + LLM repair + retry
└── domain-skills/              # Per-site knowledge (auto-created on map)
    └── <site>/
        ├── README.md           # Site overview (URL, auth, framework)
        ├── nav.md              # Navigation recipes
        ├── forms.md            # Form filling recipes
        ├── apis.md             # Discovered endpoints
        ├── failures.md         # Site-specific failures + fixes
        └── _meta.yaml          # Auto-generated metadata
```

---

## Core Principles

1. **Deterministic execution, LLM for recovery** — navigation/forms/clicks are code paths; LLM only steps in when they fail
2. **Coordinate clicks + screenshots first** — matches browser-harness philosophy; DOM only when coordinates won't work
3. **Domain skill is the single source of truth** — all site knowledge lives in `domain-skills/<site>/`
4. **Fixes are append-only** — never delete a failure entry, only append the fix
5. **Cross-site fixes live once** — `_global-failures.yaml` prevents duplication

---

## Component 1: Site Mapping (`map-site.py`)

**Purpose:** Auto-discover a site's structure and output documentation.

### Process

```
1. goto URL
2. Crawl       → follow same-origin links, collect URL patterns
3. Intercept   → capture XHR/fetch endpoints via CDP network events
4. Inspect DOM → find forms, buttons, inputs, navigation elements
5. Classify    → group by type (auth, listing, detail, form, etc.)
6. Write       → populate domain-skills/<site>/ files
```

### Auto-created folder structure (per site)

| File | Purpose |
|------|---------|
| `README.md` | Site overview, URL, auth method, framework, entry points |
| `nav.md` | Discovered routes and navigation patterns |
| `forms.md` | Form structures with selectors, submission quirks |
| `apis.md` | Intercepted endpoints, request/response shapes |
| `failures.md` | Site-specific failures (empty on first map) |
| `_meta.yaml` | Timestamp, mapped pages count, endpoint count |

### YAML frontmatter format

```yaml
---
site: students.ezralms.com
url: https://students.ezralms.com
framework: Unknown
auth: Unknown
mapped: 2026-04-23
pages: 8
endpoints: 3
---
```

### Invocation

```bash
browser-harness <<'PY'
from _tools.map_site import map_site
map_site("students.ezralms.com")
PY
```

---

## Component 2: Recipe Execution (`run-recipe.py`)

**Purpose:** Load a domain skill and execute it deterministically.

### Execution flow

```
1. Load domain-skills/<site>/nav.md, forms.md
2. Parse steps (each step = action + selector + verification)
3. Execute step by step
4. On failure → record → call heal.py
5. Retry up to 2×
6. Still failing → stop + ask user
```

### Step format (in nav.md / forms.md)

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

### Verification

- After each step: screenshot + check expected state
- `wait_for_load()` after navigation
- DOM assertion after interaction

---

## Component 3: Autorepair (`heal.py`)

**Purpose:** Detect failure → LLM diagnose → write fix → retry (up to 2×) → escalate if still failing.

### Flow

```
1. Failure detected (exception, selector missing, assertion failed)
2. Capture context:
   - Current URL
   - Screenshot
   - Last step that failed
   - DOM snapshot (js("document.body.innerHTML")[:500])
3. Query LLM: "Step <step> failed. Error: <error>. Domain skill excerpt: <relevant>.
   Suggest a fix. Format: ## Failure\n### Symptom\n### Fix\n### Confidence (high/medium/low)"
4. If confidence HIGH:
   - Write fix to domain-skills/<site>/failures.md
   - If cross-site applicable, write to _global-failures.yaml
   - Retry the step
5. Retry 1 fails → attempt fix again with deeper context
6. Retry 2 fails → stop + ask user
7. If confidence LOW at any point → stop + ask user immediately
```

### Failure entry format (`failures.md`)

```markdown
## github: star button not clickable

### First seen
2026-04-23

### Symptom
Coordinate click on [data-testid=star-button] succeeds but star count does not increment.
DOM shows two buttons matching selector; first has zero geometry.

### Fix
Use `form[action$="/star"].submit()` instead of coordinate click.

### Retry after fix
✓ Verified 2026-04-23
```

### Global failure entry format (`_global-failures.yaml`)

```yaml
failures:
  - id: react-combobox-no-commit
    symptom: "Dropdown selection not committing on click"
    sites: [github, linkedin, salesforce]
    fix: "Press Escape after selection to commit"
    confidence: high
    first_seen: 2026-04-23
    last_verified: 2026-04-23
```

---

## Component 4: Global Failure Index (`_global-failures.yaml`)

**Purpose:** Single lookup for cross-site reusable fixes.

### When to add globally

- Fix applies to 2+ different sites
- Fix is framework-level (e.g., "React combobox needs Escape to commit")
- Fix is interaction-level (e.g., "file upload needs DOM.setFileInputFiles")

### When NOT to add globally

- Fix is site-specific
- Fix is one-off anomaly

---

## Interaction with browser-harness

- Uses `helpers.py` from `C:\Users\jtoem\Repo\browser-harness\helpers.py` for all CDP operations
- Uses `daemon.py` for browser connection
- `_tools/map-site.py` etc. are additive, non-breaking
- Domain skills are compatible with existing SKILL.md conventions

---

## Mapping Sequence (New Site)

```
user: "map students.ezralms.com"
  → map-site.py crawls, intercepts, inspects
  → writes domain-skills/students-ezralms-com/ (live)

user: "login to students.ezralms.com"
  → run-recipe.py loads domain-skill
  → executes login steps
  → fail on step 3 (selectors changed)

  → heal.py: diagnose → write fix → retry × 2
  → success → continue
  OR
  → still failing → stop + ask user
```

---

## Success Criteria

- New site fully mapped in < 5 minutes (crawl + docs)
- Same failure never debugged twice — fix written once, reused
- Autonomous retry handles 80%+ of common failures without escalation
- Human escalation only for genuinely new/unpredictable site changes
- All domain-skills files are human-readable and editable

---

## Not in Scope

- Browser launch/attachment (handled by browser-harness)
- Secret/credential storage
- Visual regression testing
- Parallel multi-tab workflows (v1)
- Cloud browser management
