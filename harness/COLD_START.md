# Cold Start Procedure

Trigger: `.memory/` directory does not exist and project work is requested.

## Steps

```
1. ANNOUNCE: "⚡ COLD START — no memory state found"
2. CHECK {SKILLS_ROOT}\harness\MISTAKES.md for project hints
3. ASK user (one at a time):
   a. "Project name and one-sentence description?"
   b. "Tech stack? (frontend, backend, database)"
   c. "Current priority — what should we work on first?"
4. CREATE .memory/ structure:
   .memory/projectbrief.md (from MEMORY_TEMPLATE/T-projectbrief.md)
   .memory/activeContext.md (from MEMORY_TEMPLATE/T-activeContext.md)
   .memory/progress.md (from MEMORY_TEMPLATE/T-progress.md)
   .memory/techContext.md (from MEMORY_TEMPLATE/T-techContext.md)
   .memory/systemPatterns.md (from MEMORY_TEMPLATE/T-systemPatterns.md)
   .memory/SESSIONS.md (stub with type: sessions-index)
   .memory/ill/ directory with captures.md, wins.md, patterns.md
5. SET HARNESS_PROJECT_ROOT env var to project root
6. RE-RUN boot sequence
7. OUTPUT Boot Status Report
```

## .memory/ Directory Structure

| Directory/File | Purpose |
|----------------|---------|
| `.memory/projectbrief.md` | Project overview, goals, status |
| `.memory/activeContext.md` | Current session focus, decisions, next actions |
| `.memory/progress.md` | Task completion history |
| `.memory/techContext.md` | Technology stack, architecture |
| `.memory/systemPatterns.md` | Patterns and best practices |
| `.memory/SESSIONS.md` | Session index |
| `.memory/ill/captures.md` | ILL inefficiency captures |
| `.memory/ill/wins.md` | ILL efficiency wins |
| `.memory/ill/patterns.md` | Synthesized patterns |
| `.memory/ill/changelog.md` | Approved changes log |

## Global Context

Project: `.memory/` — per-project memory
Global: `.global/` — cross-project patterns and mistakes