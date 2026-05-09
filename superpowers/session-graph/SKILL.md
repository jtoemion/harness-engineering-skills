---
name: session-graph
description: Session close with graph awareness — creates linked notes using atomic staging pattern
quick_ref:
  close: "session_create() → stage → validate → move → sync → commit"
  mistake: "mistake_create(error, cause, lesson, refs, links)"
  pattern: "pattern_create_or_update(pattern, observed_in, prevention)"
  decision: "decision_create(decision, rationale, alternatives, scope)"
  dashboard: "dashboard_update(project)"
---

# SESSION-GRAPH — Close with Knowledge Graph

## Overview

Replaces flat SESSIONS.md appends with individual linked notes. Creates mistakes, patterns, and decisions as first-class notes with `[[links]]`. Uses the atomic staging pattern from `harness/ATOMIC_CLOSE.md`.

**Dependency:** Uses `vault-ops` for all file operations. Uses `knowledge-graph` for related-note lookup.

**See also:**
- `harness/ATOMIC_CLOSE.md` for the staging → validate → move pattern
- `harness/VAULT_SCHEMA.md` for ID format and frontmatter schema

## Atomic Close Process

```
1. CREATE staging directory: VAULT_ROOT/00_Memory/.session-close-staging/
2. STAGE all new/updated notes
3. VALIDATE (frontmatter, links, IDs)
4. MOVE staged files to vault locations
5. SYNC to global vault
6. CLEANUP staging directory
7. GIT COMMIT
```

---

## Operations

### session_create(task, outcome, files, decisions, mistakes, patterns)

Create a new session note from the T-session.md template.

**Steps:**
1. Read `VAULT_TEMPLATES/T-session.md`
2. Determine project code from `00_Memory/projectbrief.md` frontmatter
3. Generate filename: `YYYY-MM-DD-slug.md` where slug is derived from task
4. Fill frontmatter:
   - type: session
   - project: from projectbrief
   - date: current date
   - duration: calculated from session start time
   - outcome: SUCCESS | PARTIAL | BLOCKED | FAILED
   - task: one-sentence description
   - mistakes: array of mistake IDs created this session
   - decisions: array of decision IDs created this session
   - patterns: array of pattern IDs referenced this session
5. Fill body sections:
   - Task, Files (with [[links]] to file paths), Process, Decisions, Mistakes, Patterns, Blockers, Next, Handoff
6. Add `[[links]]` to every mistake, pattern, decision, and file referenced
7. Write to staging: `.session-close-staging/01_Sessions/YYYY-MM-DD-slug.md`
8. Return path to staged session note

### mistake_create(error, cause, lesson, references, related_links)

Create a new mistake note from T-mistake.md template.

**Steps:**
1. Read `VAULT_TEMPLATES/T-mistake.md`
2. DETERMINE project code from projectbrief frontmatter
3. INCREMENT ID: scan existing notes in `02_Mistakes/`, find max M### number, increment
   - Format: `{CODE}-M###` (e.g. BMW-M001, BMW-M002, etc.)
4. Generate filename: `{CODE}-M{###}-{slug}.md`
5. Fill frontmatter:
   - type: mistake
   - id: {CODE}-M{###}
   - project: from projectbrief
   - category: from predefined categories (assumption, scope-creep, dependency, api, configuration, logic, performance, security, ux)
   - status: ACTIVE
   - created: current date
   - resolved: (empty)
   - lessons: array of lesson strings
   - related: array of [[links]] to patterns, decisions, sessions
6. Fill body: Error, Cause, Lesson, Reproduction, References, Related, Timeline
7. STAGE to `.session-close-staging/02_Mistakes/{CODE}-M{###}-{slug}.md`
8. Return ID and path

### pattern_create_or_update(pattern_name, observed_in, prevention)

Create a new pattern note or update an existing one.

**Steps:**
1. CHECK if pattern already exists:
   - `vault_query(VAULT_ROOT, "pattern", {})` — find all local patterns
   - Match by slug similarity (normalize name to kebab-case, compare)
2. IF exists:
   - Update frontmatter: add project to `applies_to` array
   - Update body: add new Observed In entry with [[link]]
   - STAGE update to `.session-close-staging/03_Patterns/{existing_filename}`
3. IF new:
   - Read `VAULT_TEMPLATES/T-pattern.md`
   - DETERMINE P### ID: scan existing notes in `03_Patterns/`, find max number, increment
   - Format: `{CODE}-P{###}`
   - Generate filename: `{CODE}-P{###}-{slug}.md`
   - Fill frontmatter: type, id, project, category, applies_to, created
   - Fill body: Pattern, Context, Observed In, Prevention, Related
   - STAGE to `.session-close-staging/03_Patterns/{CODE}-P{###}-{slug}.md`
4. Return ID and path

### decision_create(decision, rationale, alternatives, scope)

Create a new decision note from T-decision.md template.

**Steps:**
1. Read `VAULT_TEMPLATES/T-decision.md`
2. DETERMINE project code and D### ID (same increment pattern)
3. Generate filename: `{CODE}-D{###}-{slug}.md`
4. Fill frontmatter:
   - type: decision
   - id: {CODE}-D{###}
   - project: from projectbrief
   - domain: from predefined categories (auth, data, architecture, ux, infra, tooling)
   - status: active
   - created: current date
   - context: one-line problem statement
5. Fill body: Context, Decision, Rationale, Alternatives Considered, Consequences, Related
6. STAGE to `.session-close-staging/03_Patterns/{CODE}-D{###}-{slug}.md`
   (Decisions stored in 03_Patterns/ folder alongside patterns — both are knowledge notes)
7. Return ID and path

### dashboard_update(project)

Update the Dashboard.md index note.

**Steps:**
1. Read `VAULT_INDEX/Dashboard.md`
2. Update frontmatter: `updated: current_date`
3. Verify [[link]] to activeContext still resolves
4. Dataview queries auto-update but verify link integrity
5. Count completed/total from progress.md frontmatter
6. Update progress line in Dashboard body
7. STAGE update to `.session-close-staging/04_Index/Dashboard.md`
8. Return path

---

## Validation (Before Moving Staged Files)

Before moving from staging to vault locations, validate ALL staged notes:

| Check | Method |
|-------|--------|
| YAML parseable | Parse frontmatter, verify no syntax errors |
| Required fields | Each type has required fields (see VAULT_SCHEMA.md) |
| Link integrity | For each `[[link]]`, check target exists in vault OR staging |
| ID format | Regex: `^[A-Z]{2,3}-[MPD]\d{3}-[a-z0-9-]+$` |
| ID uniqueness | No duplicate IDs within staging batch |
| Status values | mistake: ACTIVE/RESOLVED. decision: active/superseded/deprecated |
| Outcome values | session: SUCCESS/PARTIAL/BLOCKED/FAILED |

If ANY validation fails, STOP and report errors. Do not move files.

---

## Session Close Sequence

```
1. CREATE staging directory
2. session_create() → staged session note
3. dashboard_update() → staged Dashboard
4. UPDATE 00_Memory/activeContext.md → staged
5. UPDATE 00_Memory/progress.md → staged
6. For each new mistake: mistake_create() → staged
7. For each new pattern: pattern_create_or_update() → staged
8. For each new decision: decision_create() → staged
9. UPDATE 00_Memory/SESSIONS.md → staged (add [[link]] to session note)
10. VALIDATE all staged files
11. MOVE staged files to vault locations
12. vault_sync(project, global) → sync cross-cutting notes
13. CLEANUP staging directory
14. UPDATE 00_Memory/systemPatterns.md (if patterns changed)
15. LOG mistakes to harness/MISTAKES.md
16. GIT COMMIT
17. OUTPUT session close summary
```

---

## Anti-Rationalization

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Skip staging" | Atomic close requires staging. No exceptions. |
| "Skip validation" | Malformed frontmatter corrupts the graph. |
| "Write directly to vault" | If interrupted mid-write, half the graph is corrupt. |
| "Delete resolved mistakes" | Tombstone pattern. Keep for history, filter from queries. |
| "Put decisions in separate folder" | Decisions and patterns are both knowledge notes. Same folder. |
| "Skip global sync" | Cross-project knowledge is the whole point. |