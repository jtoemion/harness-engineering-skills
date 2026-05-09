# Mistakes Tracking — Anti-Repeat System

**CORE DIRECTIVE:** Previous mistakes MUST be tracked and referenced before implementing solutions.

## Pre-Implementation Check (MANDATORY — ALWAYS)

```
BEFORE writing any code or dispatching subagent:
1. READ {SKILLS_ROOT}\harness\MISTAKES.md
2. SEARCH for similar mistake patterns
3. IF found:
   a. SURFACE: "Previously, X caused Y because Z. This time I will..."
   b. MARK assumption as checked
4. IF attempting same approach that failed before:
   a. STOP
   b. ASK user: "Previous attempt failed. Suggest alternative approach?"
```

## Mistake Recording (POST-MORTEM — ALWAYS)

After any failed attempt, bug discovery, or subagent failure:

```markdown
## [YYYY-MM-DD] | [MISTAKE CATEGORY]
**Error**     : [What went wrong — specific]
**Cause**     : [Why it happened — root cause]
**Lesson**    : [How to prevent — concrete action]
**References**: [Files:line numbers affected]
**Assumption**: [What was incorrectly assumed]
**Status**    : [ACTIVE | RESOLVED | SUPERSEDED]
```

## Mistakes Log Location

`{SKILLS_ROOT}\harness\MISTAKES.md`

## Schema Fields

| Field | Description |
|-------|-------------|
| Error | What went wrong — specific |
| Cause | Why it happened — root cause |
| Lesson | How to prevent — concrete action |
| References | Files:line numbers affected |
| Assumption | What was incorrectly assumed |
| Status | ACTIVE \| RESOLVED \| SUPERSEDED |

## After Any Failure — Mandatory Steps

1. Log to `MISTAKES.md` with full context
2. Tag the assumption that failed
3. Update harness component to prevent recurrence
4. If main agent made mistake → it did not follow commander pattern

## Common Failure Patterns (Check These First)

- Subagent returned raw file content instead of summary → SUBAGENT_RESULT.md breach
- Main agent read files directly instead of dispatching explore → Commander pattern violation
- Task claimed fixed but didn't work → Mistake tracking not consulted
- Same mistake repeated → MISTAKES.md not checked before implementation