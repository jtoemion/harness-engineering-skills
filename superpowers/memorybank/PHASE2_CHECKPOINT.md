# Phase 2 — Checkpoint (Task Completion)

Trigger: Any completed task, code commit, architectural change, feature implementation.

## HARNESS ENFORCEMENT (Pre-Checkpoint)

```
1. CHECK {SKILLS_ROOT}\harness\MISTAKES.md
2. IF relevant mistakes found → surface lesson:
   "Previously, X caused Y. This time I will..."
3. IF same approach failed before → STOP → ask user
4. LOG any new mistakes to {SKILLS_ROOT}\harness\MISTAKES.md
```

## Checkpoint Steps

```
1. UPDATE 00_Memory/activeContext.md
2. UPDATE 00_Memory/progress.md
3. IF architectural change → UPDATE 00_Memory/techContext.md
4. IF system patterns changed → UPDATE 00_Memory/systemPatterns.md
5. CREATE individual session note in 01_Sessions/:
   - Filename: YYYY-MM-DD-slug.md
   - Frontmatter: type, project, date, duration, outcome, task, mistakes, decisions, patterns
   - Body: Task, Files, Process, Decisions, Outcome, Next
   → see SESSIONS_SCHEMA.md for full format
6. UPDATE 00_Memory/SESSIONS.md:
   - APPEND [[link]] to new session note
7. IF mistakes were made or avoided:
   - CREATE mistake notes in 02_Mistakes/ (ID format: {CODE}-M###-slug.md)
   - Frontmatter: type, id, project, category, status, created, resolved, lessons, related
   - Status: ACTIVE (unresolved) or RESOLVED (fixed)
8. IF new patterns discovered:
   - CREATE pattern notes in 03_Patterns/ (ID format: {CODE}-P###-slug.md)
   - Frontmatter: type, id, project, category, applies_to, created
9. IF architectural decisions made:
   - CREATE decision notes in 03_Patterns/ (ID format: {CODE}-D###-slug.md)
   - Frontmatter: type, id, project, domain, status, created, context
10. UPDATE 04_Index/Dashboard.md:
    - Refresh task counts, recent sessions, active mistakes
11. SYNC to global vault (if available):
    - Copy cross-cutting mistakes → {ANTIGRAVITY_GLOBAL_VAULT}/00_Global/Mistakes/
    - Create/update patterns → {ANTIGRAVITY_GLOBAL_VAULT}/00_Global/Patterns/
12. OUTPUT Checkpoint Confirmation
```

## Checkpoint Confirmation

```
⚡ CHECKPOINT
  Context  : [updated summary]
  Progress : [what changed in progress.md]
  Session  : 01_Sessions/YYYY-MM-DD-slug.md
  Mistakes : [N] avoided | [N] made → [list note IDs]
  Patterns : [N] new → [list note IDs]
  Global   : [SYNCED | LOCAL-ONLY | UNAVAILABLE]
```

## Session Note Frontmatter

```yaml
---
type: session
project: [PROJECT_CODE]
date: YYYY-MM-DD
duration: [Xm | Xh]
outcome: [SUCCESS | PARTIAL | BLOCKED | FAILED]
task: [Clear description]
mistakes:
  - [CODE-M###-slug or none]
decisions:
  - [CODE-D###-slug or none]
patterns:
  - [CODE-P###-slug or none]
---
```

## Session Note Body Format

```markdown
## Task
[Clear description of what was attempted/done]

## Files
[Complete list of all files touched with full paths]

## Process
- [Step 1: What was done]
- [Step 2: How it was approached]
- [Step 3: Any debugging/research performed]
- [Any dead ends or alternatives considered]

## Decisions
[Key choices made and why]

## Outcome
[SUCCESS | PARTIAL | BLOCKED | FAILED — with details]

## Next
[Specific next steps required]
```

## Task Completion Triggers

- Code implementation (any size)
- Bug fixes and debugging
- Research and investigation
- Architecture and design decisions
- Refactoring work
- Configuration changes
- Documentation updates
- Code review responses
- Testing and verification