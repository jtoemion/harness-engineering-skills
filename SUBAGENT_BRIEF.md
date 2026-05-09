# Subagent Brief: BUILD — Skill Skeleton

**Type**      : build
**Objective** : Create browser-agent skill skeleton with SKILL.md, _global-failures.yaml, _tools/__init__.py, and domain-skills/.gitkeep
**Constraints**: Must match existing skill folder format in ~/.config/opencode/skills/
**Success**   : All 4 files created, valid YAML/Markdown, committed

## Context
Building a new browser-agent skill at `C:\Users\jtoem\.config\opencode\skills\browser-agent\`.
Reference: `C:\Users\jtoem\.config\opencode\skills\browser-agent\DESIGN.md` (read first).
Reference helpers: `C:\Users\jtoem\Repo\browser-harness\helpers.py`.

## Files / Scope
- `C:\Users\jtoem\.config\opencode\skills\browser-agent\_global-failures.yaml` — Create with version: "1.0", failures: []
- `C:\Users\jtoem\.config\opencode\skills\browser-agent\_tools\__init__.py` — Empty module init
- `C:\Users\jtoem\.config\opencode\skills\browser-agent\domain-skills\.gitkeep` — Empty gitkeep
- `C:\Users\jtoem\.config\opencode\skills\browser-agent\SKILL.md` — Entry point doc (see spec below)

## SKILL.md content
```markdown
---
name: browser-agent
description: Browser automation with auto-discovery, deterministic recipes, and autonomous repair. Use when automating web tasks, mapping sites, or need browser-based workflows.
---

# browser-agent

Browser automation skill that discovers site structure, executes deterministic recipes, and repairs failures autonomously.

## Structure

```
browser-agent/
├── _global-failures.yaml    # Cross-site fix index
├── _tools/
│   ├── map-site.py          # Auto-discover site structure
│   ├── run-recipe.py        # Execute deterministic recipe
│   └── heal.py              # Autorepair with LLM + 2 retries
└── domain-skills/           # Per-site knowledge (auto-created)
    └── <site>/
        ├── README.md
        ├── nav.md
        ├── forms.md
        ├── apis.md
        ├── failures.md
        └── _meta.yaml
```

## Commands

| Action | Tool |
|--------|------|
| Map a site | `map-site.py` |
| Run a recipe | `run-recipe.py` |
| Repair after failure | `heal.py` (called automatically) |

## Reference
- Design: `DESIGN.md`
- Browser harness helpers: `C:\Users\jtoem\Repo\browser-harness\helpers.py`
```

## Steps
1. Read DESIGN.md at `C:\Users\jtoem\.config\opencode\skills\browser-agent\DESIGN.md`
2. Create `_global-failures.yaml`
3. Create `_tools/__init__.py`
4. Create `domain-skills/.gitkeep`
5. Create `SKILL.md` with content above
6. Commit with message: `feat: add browser-agent skill skeleton`

## Output
Write results to SUBAGENT_RESULT.md before returning.
