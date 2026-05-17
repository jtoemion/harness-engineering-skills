# Vault Schema — DEPRECATED

> **⚠️ DEPRECATED:** This document describes the Obsidian vault approach. The system now uses a **file-based JSON knowledge graph** stored in `.memory/`. This file is kept for historical reference only.
>
> **Active system:** See `.memory/mistakes.json`, `.memory/patterns.json`, `.memory/variables.json`, `.memory/knowledge.json`
> **ID Format:** Still used by session-graph redirects (now absorbed into memorybank Phase 4)

---

## Project Codes

| Project | Code | Project Root |
|---------|------|-------------|
| forgeWhisper | FW | `C:\Users\jtoem\Repo\forgeWhisper\` |
| LP-bmw | BMW | `C:\Users\jtoem\Repo\LP-bmw\` |
| LPPastpapr | PP | `C:\Users\jtoem\Repo\LPPastpapr\` |
| student-portal | SP | `C:\Users\jtoem\Repo\pastpapr\student-portal\` |
| question-extractor | QE | `C:\Users\jtoem\Repo\question-extractor\` |
| n8n-ytdlp-setup | N8 | `C:\Users\jtoem\Repo\n8n-ytdlp-setup\` |

## ID Format (Still Used)

- Mistakes: `{CODE}-M###` (e.g. BMW-M001, FW-M003)
- Patterns: `{CODE}-P###` (e.g. BMW-P001)
- Decisions: `{CODE}-D###` (e.g. BMW-D012)
- Sessions: `YYYY-MM-DD-slug` (no project code needed, sessions are project-scoped)

## JSON Knowledge Graph (Active System)

The active system uses flat JSON files in `.memory/`:

```
.memory/
├── mistakes.json      # Active mistakes with error/cause/lesson/status/category
├── patterns.json      # Reusable patterns with pattern/applies_to/prevention
├── variables.json     # Variable-level insights with type/behavior/depends_on/affects
├── knowledge.json     # Main index with version and summary counts
├── sessions.json      # Session history (JSONL format)
└── decisions.json     # Architectural decisions
```

## Environment Variables (Obsolete)

| Variable | Status | Notes |
|----------|--------|-------|
| `ANTIGRAVITY_GLOBAL_VAULT` | ❌ Removed | No global vault — project-local `.memory/` only |
| `OBSIDIAN_REST_KEY` | ❌ Removed | No Obsidian MCP dependency |

## Frontmatter Schema (Obsolete)

The Obsidian frontmatter schema is deprecated. JSON knowledge files use flat JSON schema:

```json
{
  "id": "BMW-M001",
  "error": "...",
  "cause": "...",
  "lesson": "...",
  "status": "ACTIVE",
  "category": "backend"
}
```

## Tombstone Pattern

Resolved mistakes remain in `mistakes.json` with `status: RESOLVED`. Query filters by default to `status != RESOLVED`.

## See Also

- `harness/NEWSPAPER_LOGIC.md` — Document format standard
- `harness/SYSTEMPATTERNS_TEMPLATE.md` — Template for retrospective entries
- `harness/QUICK_MODE_BUFFER.md` — Quick mode learning buffer mechanism
- `runtime/templates/` — JSON schema templates

---

*This file was kept to preserve the ID format naming convention. All Obsidian-specific content is deprecated.*