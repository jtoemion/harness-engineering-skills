# Memory Lifecycle — File Schemas

**CORE DIRECTIVE:** Memory resets every session. Read the files.

## Project .memory/ Files

| File | Purpose | Update Trigger |
|------|---------|----------------|
| `projectbrief.md` | Project definition | Never (manual) |
| `systemPatterns.md` | Architecture conventions | Architectural change |
| `techContext.md` | Tech stack details | Stack change |
| `activeContext.md` | Current task/blockers | Every task change |
| `progress.md` | Task tracking | Every completed task |
| `SESSIONS.md` | Session history | Every session end |
| `.memory/ill/captures.md` | Inefficiency captures | Manual + reflection |
| `.memory/ill/wins.md` | Efficiency wins | Manual + reflection |
| `.memory/ill/patterns.md` | Synthesized patterns | On synthesize |
| `.memory/ill/changelog.md` | Approved changes | On approval |

## Obsidian Mirror Mapping

```
Project vault: 00_Memory/ → project vault (local)
Session notes: 01_Sessions/ → project vault (local)
Mistake notes: 02_Mistakes/ → project vault (local)
Pattern notes: 03_Patterns/ → project vault (local)
Index/Dashboard: 04_Index/ → project vault (local)
Templates: 05_Templates/ → project vault (local)
Global vault: C:\Users\jtoem\Obsidian\AntigravityV\ (cross-project)
```

See `VAULT_SCHEMA.md` for complete vault directory specification.

## File Schemas

### projectbrief.md
```markdown
# Project Brief
- **Name**: [project name]
- **Description**: [one-sentence description]
- **Goals**: [bullet list of goals]
- **Non-Goals**: [what we are NOT building]
```

### activeContext.md
```markdown
# Active Context
- **Current Task**: [what we are doing right now]
- **Blockers**: [anything blocking progress]
- **Last Agent**: [tool name]
- **Updated**: [YYYY-MM-DD HH:MM]
```

### progress.md
```markdown
# Progress
## Completed
- [x] [task]

## In Progress
- [/] [task]

## Backlog
- [ ] [task]
```

### techContext.md
```markdown
# Tech Context
- **Frontend**: [framework, styling]
- **Backend**: [runtime, framework]
- **Database**: [DB name and ORM]
- **Infra**: [hosting, CI/CD]
- **Key Decisions**: [major architectural decisions]
```

### systemPatterns.md
```markdown
# System Patterns
- **Architecture**: [overall pattern]
- **Conventions**: [naming, file structure]
- **Known Gotchas**: [things that caused bugs]
- **Lessons Learned**: [from retrospectives]
```

### SESSIONS.md
```markdown
# Session History

---
[YYYY-MM-DD HH:MM] | [TASK NAME]

**Task**    : [Clear description of what was attempted/done]
**Files**   : [Complete list of all files touched with full paths]
**Process** :
  - [Step 1: What was done]
  - [Step 2: How it was approached]
  - [Step 3: Any debugging/research performed]
**Decisions**: [Key choices made and why]
**Outcome** : [SUCCESS | PARTIAL | BLOCKED | FAILED - with details]
**Next**    : [Specific next steps required]

---
```