---
name: vault-ops
description: Core Obsidian vault read/write/query/patch/link/sync operations
quick_ref:
  boot: "vault-ops → detect vault → load memory → query mistakes → load global"
  read: "vault_read(path, type, filters) — parse YAML + content"
  write: "vault_write(path, template, data) — create from template"
  query: "vault_query(vault, type, filters) — scan + filter across vault"
  patch: "vault_patch(path, field, value) — update specific frontmatter field"
  link: "vault_link(from, to) — add [[link]] to note body"
  search: "vault_search(text) — full-text search across vault"
  sync: "vault_sync(project, global) — bidirectional sync"
  atomic: "vault_close_staging() → validate → move → sync → commit"
---

# VAULT-OPS — Obsidian Vault Operations

## Overview

Core operations for reading, writing, querying, and syncing Obsidian vault notes. Works in FILE-ONLY mode by default. ENHANCED mode available when Obsidian + Local REST API is running.

**Principle:** The vault is just a folder of Markdown files. Every operation works without Obsidian running. REST API is a bonus, not a requirement.

**See also:** `harness/VAULT_SCHEMA.md` for folder structure, frontmatter schema, and ID format.

## Mode Detection

```
BOOT: PROBE REST API
  curl -k -s https://127.0.0.1:27124/ -H "Authorization: Bearer $OBSIDIAN_REST_KEY"
  IF 200 → ENHANCED MODE (set flag: rest_api=true)
  IF timeout/refused → FILE-ONLY MODE (set flag: rest_api=false)
  Continue boot either way, never block.
```

## Vault Paths

| Variable | Path | Purpose |
|----------|------|---------|
| VAULT_ROOT | Project root (where .obsidian/ lives) | Base path |
| VAULT_MEMORY | {VAULT_ROOT}/00_Memory/ | Core 5 memory files |
| VAULT_SESSIONS | {VAULT_ROOT}/01_Sessions/ | Individual session notes |
| VAULT_MISTAKES | {VAULT_ROOT}/02_Mistakes/ | Individual mistake notes |
| VAULT_PATTERNS | {VAULT_ROOT}/03_Patterns/ | Individual pattern + decision notes |
| VAULT_INDEX | {VAULT_ROOT}/04_Index/ | Dashboard + MOCs |
| VAULT_TEMPLATES | {VAULT_ROOT}/05_Templates/ | Note templates |
| GLOBAL_VAULT | $ANTIGRAVITY_GLOBAL_VAULT | Cross-project knowledge |

---

## Operations

### vault_read(path, type, filters)

Read a single note from the vault. Returns `{ frontmatter, body, links }`.

**FILE-ONLY:**
1. Read `.md` file at path using filesystem
2. Parse YAML frontmatter: split on `\n---\n` (first `---` opens, second closes)
3. Extract body content: everything after the second `---` delimiter
4. Extract `[[links]]` from body: regex `\[\[([^\]|#^]+)` — captures link target without aliases/headings
5. Apply filters: for each filter `key=value`, check `frontmatter[key] == value`; for `key!=value`, check inequality; for `key contains value`, check substring
6. Return `{ frontmatter: object, body: string, links: string[] }`

**ENHANCED (REST API):**
```bash
curl -k -s https://127.0.0.1:27124/vault/{path} \
  -H "Authorization: Bearer $OBSIDIAN_REST_KEY"
```

**Default filter for mistakes:** `status != RESOLVED` (tombstone pattern)

---

### vault_write(path, template, data)

Create a new note from a template.

**Steps:**

**1. Template Reading**
- Read template file from `VAULT_TEMPLATES/T-{type}.md`
- Template types: `mistake`, `pattern`, `decision`, `session`

**2. Placeholder Replacement**
- Pattern: `__PLACEHOLDER__` → replace with `data[PLACEHOLDER]`
- Process all `__KEY__` patterns left-to-right
- No replacement → leave as-is (don't error)

**3. ID Generation**
- Scan existing notes in target folder (glob `*.md`)
- Extract numeric prefixes (e.g., `001-`, `017-`)
- Find maximum ID, increment by 1
- Format: zero-padded 3-digit minimum (e.g., `001`, `018`)

**4. Filename Generation**
- Mistakes/Patterns/Decisions: `{ID}-{slug}.md`
  - Slug: lowercase, hyphenated, extracted from `title` field
  - Example: `017-improper-error-handling.md`
- Sessions: `{date}-{slug}.md`
  - Date: `YYYY-MM-DD` from frontmatter `created` field
  - Example: `2026-04-23-debugging-session.md`

**5. Template Field Mappings by Note Type**

| Note Type | Required Fields | Template Field |
|-----------|-----------------|----------------|
| mistake | id, title, category, status, created | `__ID__`, `__TITLE__`, `__CATEGORY__`, `__STATUS__`, `__CREATED__` |
| pattern | id, title, applies_to, status, created | `__ID__`, `__TITLE__`, `__APPLIES_TO__`, `__STATUS__`, `__CREATED__` |
| decision | id, title, context, outcome, created | `__ID__`, `__TITLE__`, `__CONTEXT__`, `__OUTCOME__`, `__CREATED__` |
| session | id, date, outcome, project, created | `__ID__`, `__DATE__`, `__OUTCOME__`, `__PROJECT__`, `__CREATED__` |

**6. YAML Validation**
- Required fields must be non-empty after replacement
- Parse frontmatter with YAML parser before write
- If parse fails → abort, do not write

**7. Write**
- FILE-ONLY: write `.md` file to target path
- ENHANCED (REST API):
```bash
curl -k -s -X PUT https://127.0.0.1:27124/vault/{path} \
  -H "Authorization: Bearer $OBSIDIAN_REST_KEY" \
  -H "Content-Type: text/markdown" \
  -d "{content}"
```

---

### vault_query(vault, type, filters)

Query notes across the vault by type and filters. Returns array of `{ path, frontmatter, body_summary }`.

**Type-to-Folder Mapping:**

| type | Folder |
|------|--------|
| mistake | `02_Mistakes/` |
| pattern | `03_Patterns/` |
| decision | `03_Patterns/` (Decisions subfolder) |
| session | `01_Sessions/` |
| index | `04_Index/` |
| template | `05_Templates/` |

**Filter Syntax:**
- `key=value` → exact match: `frontmatter[key] === value`
- `key!=value` → inequality: `frontmatter[key] !== value`
- `key contains value` → substring: `frontmatter[key].includes(value)`

**FILE-ONLY:**
1. GLOB: `{vault}/**/{type_folder}/*.md`
2. Parse YAML frontmatter for each matching file
3. Apply filter conditions in order (AND logic)
4. Sort by frontmatter `created` field descending
5. Return array

**ENHANCED (REST API) — Dataview DQL:**
```bash
curl -k -s -X POST https://127.0.0.1:27124/search/ \
  -H "Authorization: Bearer $OBSIDIAN_REST_KEY" \
  -H "Content-Type: application/vnd.olrapi.dataview.dql+txt" \
  -d "TABLE id, status, category, project FROM \"{type_folder}\" WHERE {filters}"
```

**Dataview DQL Examples by Query Type:**

| Query | DQL |
|-------|-----|
| All active mistakes | `TABLE id, title, category FROM "02_Mistakes" WHERE status = "ACTIVE"` |
| Mistakes by category | `TABLE id, title, status FROM "02_Mistakes" WHERE category = "assumption"` |
| Patterns for React | `TABLE id, title, applies_to FROM "03_Patterns" WHERE applies_to CONTAINS "React"` |
| Failed sessions | `TABLE id, date, outcome, project FROM "01_Sessions" WHERE outcome = "FAILED"` |
| Decisions with context | `TABLE id, title, outcome FROM "03_Patterns" WHERE context CONTAINS "architecture"` |
| Multi-filter | `TABLE id, status, category FROM "02_Mistakes" WHERE status = "ACTIVE" AND category != "configuration"` |

---

### vault_patch(path, field, value)

Update a specific frontmatter field without rewriting the entire file.

**FILE-ONLY:**
1. Read file at path
2. Parse YAML frontmatter (split on `\n---\n`)
3. Modify target field: `frontmatter[field] = value`
4. Serialize YAML back: reconstruct frontmatter block with proper formatting
5. Write file: combine frontmatter + body

**ENHANCED (REST API):**
```bash
curl -k -s -X PATCH https://127.0.0.1:27124/vault/{path} \
  -H "Authorization: Bearer $OBSIDIAN_REST_KEY" \
  -H "Operation: replace" \
  -H "Target-Type: frontmatter" \
  -H "Target: {field}" \
  -H "Content-Type: application/json" \
  -d "\"{value}\""
```

**Example PATCH for status change:**
```bash
curl -k -s -X PATCH https://127.0.0.1:27124/vault/02_Mistakes/017-improper-error-handling.md \
  -H "Authorization: Bearer $OBSIDIAN_REST_KEY" \
  -H "Operation: replace" \
  -H "Target-Type: frontmatter" \
  -H "Target: status" \
  -H "Content-Type: application/json" \
  -d "\"RESOLVED\""
```

---

### vault_link(from, to)

Add a `[[link]]` to a note's body in the appropriate section.

**Insertion Point Rules:**

| Link Target Type | Insert Section | Position |
|-----------------|----------------|-----------|
| mistake | `## Related` | Append under heading |
| pattern | `## Related` | Append under heading |
| pattern (from mistake) | `## Observed In` | Append under heading |
| decision | `## Decisions` | Append under heading |
| file path | `## Files` | Append under heading |
| session | `## Related` | Append under heading |

**Algorithm:**
1. Read from-note body
2. Locate insertion section by heading (case-insensitive match)
3. If section doesn't exist → create it at end of body
4. Check if `[[to]]` already exists in target section (no duplicates)
5. Append `- [[to]]` to section
6. Write back

**Important:** Only add links that don't already exist.

---

### vault_search(text)

Full-text search across the vault.

**FILE-ONLY:**
```bash
# Basic grep
rg -n "{text}" {vault_root}/**/*.md

# Case-insensitive
rg -in "{text}" {vault_root}/**/*.md

# With context (2 lines before/after)
rg -in -B 2 -A 2 "{text}" {vault_root}/**/*.md
```

**ENHANCED (REST API):**
```bash
curl -k -s -X POST https://127.0.0.1:27124/search/simple/ \
  -H "Authorization: Bearer $OBSIDIAN_REST_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{text}"}'
```

---

### vault_sync(project, global)

Bidirectional sync between project vault and global vault.

**Sync Rules (EXACT):**

| Entity | Condition | Action |
|--------|-----------|--------|
| Mistake | `category in [assumption, scope-creep, configuration]` | Copy to global |
| Mistake | `category in [dependency, api, logic, performance, security, ux]` | Keep local only |
| Pattern | `applies_to.length > 1` | Update global |
| Pattern | `applies_to.length === 1` | Keep local only |
| Decision | cross-project relevance | Copy to global |
| Decision | project-specific | Keep local only |
| Session | always | Never copy |

**Project → Global (at session close):**
1. Read project note
2. Check if note qualifies for global sync (see rules above)
3. If qualifies:
   a. Check if note already exists in global vault (match by ID or slug)
   b. If exists: merge frontmatter (update fields, append to `applies_to` array for patterns)
   c. If not: copy note to global vault, add bidirectional `[[links]]`
4. Update `global/04_Index/Projects.md` with new/changed notes

**Global → Project (at boot):**
1. Query global vault for mistakes where `category` matches project context
2. Query global vault for patterns where `applies_to` includes project tech stack
3. Surface relevant knowledge in boot status report
4. Do NOT auto-copy to project (knowledge surfaces, doesn't migrate)

**Bidirectional Update Logic:**
- When updating existing note in global: preserve `created`, update `modified`, increment revision
- When copying new note to global: set `created = now`, `global_source = project_name`
- Bidirectional links: add `[[to]]` in both directions where applicable

---

## REST API Enhancement

**Note:** REST API detection happens at boot. If Obsidian is not running or Local REST API plugin is disabled, the agent falls back to FILE-ONLY mode transparently.

### Dataview Queries (ENHANCED MODE)

```
Endpoint: POST https://127.0.0.1:27124/search/
Authorization: Bearer $OBSIDIAN_REST_KEY
Content-Type: application/vnd.olrapi.dataview.dql+txt
```

**Examples:**

```dataview
// All active mistakes
TABLE id, category, status, created
FROM "02_Mistakes"
WHERE status = "ACTIVE"

// Patterns by stack
TABLE id, applies_to, category
FROM "03_Patterns"
WHERE contains(applies_to, "React")

// Recent sessions
TABLE date, outcome, task, mistakes
FROM "01_Sessions"
SORT date DESC
LIMIT 10
```

### Targeted Frontmatter Patch (ENHANCED MODE)

```
PATCH https://127.0.0.1:27124/vault/{path}
Authorization: Bearer $OBSIDIAN_REST_KEY
Operation: replace
Target-Type: frontmatter
Target: {field_name}
Content-Type: application/json
Body: "{new_value}"
```

### Open in UI (ENHANCED MODE)

```
POST https://127.0.0.1:27124/open/{path}
Authorization: Bearer $OBSIDIAN_REST_KEY
```

---

## Atomic Close Integration

See `harness/ATOMIC_CLOSE.md` for the full staging pattern.

**Key rule:** Never write directly to vault locations during session close. Always stage, validate, then move.

---

## Anti-Rationalization

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "REST API is required" | FILE-ONLY mode always works. REST is a bonus, not a requirement. |
| "Skip validation" | Malformed frontmatter corrupts the graph and breaks queries. |
| "Write directly during close" | Atomic close requires staging. Never write directly. |
| "Skip global sync" | Cross-project knowledge is the whole point of the vault. |
| "Resolved mistakes should be deleted" | Tombstone pattern. Keep for history, filter from queries. |
| "ID generation is optional" | IDs enable tracking, linking, and deduplication across vaults. |
| "Links don't need deduplication" | Duplicate `[[links]]` cause visual clutter and query noise. Check before append. |
| "Session notes need global sync" | Sessions are project-local by design. Never copy to global vault. |
| "Filter-less queries are fine" | Unfiltered queries on large vaults are slow and return irrelevant results. |
| "Slug generation doesn't matter" | Slugs affect link readability and Dataview queries. Generate consistently. |
| "Template placeholders are optional" | Placeholder replacement ensures consistency. Missing placeholders = malformed notes. |
| "Partial YAML updates are safe" | Manual field edits without full YAML serialization can corrupt the file. |