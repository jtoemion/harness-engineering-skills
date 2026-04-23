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
