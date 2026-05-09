# Vault Schema

## Project Codes

| Project | Code | Vault Path |
|---------|------|------------|
| forgeWhisper | FW | C:\Users\jtoem\Repo\forgeWhisper\ |
| LP-bmw | BMW | C:\Users\jtoem\Repo\LP-bmw\ |
| LPPastpapr | PP | C:\Users\jtoem\Repo\LPPastpapr\ |
| student-portal | SP | C:\Users\jtoem\Repo\pastpapr\student-portal\ |
| question-extractor | QE | C:\Users\jtoem\Repo\question-extractor\ |
| n8n-ytdlp-setup | N8 | C:\Users\jtoem\Repo\n8n-ytdlp-setup\ |

## ID Format

- Mistakes: `{CODE}-M###` (e.g. BMW-M001, FW-M003)
- Patterns: `{CODE}-P###` (e.g. BMW-P001)
- Decisions: `{CODE}-D###` (e.g. BMW-D012)
- Sessions: `YYYY-MM-DD-slug` (no project code needed, sessions are project-scoped by folder)

## Global Vault

- Path: Defined by `ANTIGRAVITY_GLOBAL_VAULT` env variable
- Default: `C:\Users\jtoem\Obsidian\AntigravityV\`
- Global notes use unscoped IDs with `project:` prefix in frontmatter

## Vault Structure (Per Project)

```
{PROJECT_ROOT}/
├── 00_Memory/          # Replaces .memory/ — core 5 files + SESSIONS.md
├── 01_Sessions/        # Individual session notes
├── 02_Mistakes/        # Individual mistake notes ({CODE}-M###-slug.md)
├── 03_Patterns/        # Individual pattern notes ({CODE}-P###-slug.md)
├── 04_Index/           # Dashboard.md + MOCs
├── 05_Templates/       # Note templates (T-*.md)
└── .obsidian/          # Obsidian config (committed, gitignore workspace.json + cache/)
```

## Global Vault Structure

```
{ANTIGRAVITY_GLOBAL_VAULT}/
├── 00_Global/
│   ├── Mistakes/       # Cross-project mistake notes
│   ├── Patterns/       # Cross-project pattern notes
│   └── Decisions/      # Cross-project decision notes
├── 01_Templates/       # Shared templates
├── 02_Index/
│   ├── Projects.md     # Links to all project vaults
│   ├── Mistakes.md     # Dataview: all ACTIVE mistakes
│   └── Patterns.md     # Dataview: all patterns by frequency
└── 03_Daily/           # Daily notes (cross-project view)
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `ANTIGRAVITY_GLOBAL_VAULT` | Path to global vault | `C:\Users\jtoem\Obsidian\AntigravityV\` |
| `OBSIDIAN_REST_KEY` | Local REST API key | (gitignored, never hardcoded) |

## Frontmatter Schema

Every note has YAML frontmatter with a `type` field:

| Type | Folder | Required Fields |
|------|--------|----------------|
| projectbrief | 00_Memory/ | type, project, project_code, status, created, updated, stack, priority |
| activeContext | 00_Memory/ | type, project, task, blockers, last_agent, updated |
| progress | 00_Memory/ | type, project, updated, total, completed |
| techContext | 00_Memory/ | type, project, frontend, backend, database, infra, key_decisions |
| systemPatterns | 00_Memory/ | type, project, architectural_style, conventions, known_gotchas, updated |
| sessions-index | 00_Memory/ | type, project, total, last |
| session | 01_Sessions/ | type, project, date, duration, outcome, task, mistakes, decisions, patterns |
| mistake | 02_Mistakes/ | type, id, project, category, status, created, resolved, lessons, related |
| pattern | 03_Patterns/ | type, id, project, category, applies_to, created |
| decision | 03_Patterns/ | type, id, project, domain, status, created, context |
| dashboard | 04_Index/ | type, project, updated |

## Tombstone Pattern

Resolved mistakes remain in `02_Mistakes/` with `status: RESOLVED` and `resolved: YYYY-MM-DD`.
`vault_query` defaults to filtering out resolved mistakes (`status != RESOLVED`).
This preserves historical context without cluttering active queries.

## Atomic Close

See `harness/ATOMIC_CLOSE.md` for the write-to-temp-then-move pattern.