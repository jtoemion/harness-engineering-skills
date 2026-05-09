# Sessions Schema — Individual Session Notes

Sessions are stored as **individual notes** in `01_Sessions/`, not as a single flat file.

`00_Memory/SESSIONS.md` serves as an **index** of `[[links]]` to individual session notes.

## Session Note Frontmatter

Every session note must include this YAML frontmatter:

```yaml
---
type: session
project: [PROJECT_CODE]
date: YYYY-MM-DD
duration: [Xm | Xh]
outcome: [SUCCESS | PARTIAL | BLOCKED | FAILED]
task: [Clear description]
mistakes:
  - "[[CODE-M###-slug]]"
  - ...
decisions:
  - "[[CODE-D###-slug]]"
  - ...
patterns:
  - "[[CODE-P###-slug]]"
  - ...
---
```

### Required Fields

| Field | Type | Values |
|-------|------|--------|
| type | string | Always `session` |
| project | string | Project code (e.g. `FW`, `BMW`) |
| date | date | `YYYY-MM-DD` |
| duration | string | `Xm` or `Xh` |
| outcome | enum | `SUCCESS`, `PARTIAL`, `BLOCKED`, `FAILED` |
| task | string | Clear description of what was attempted |
| mistakes | list | `[[]]` links to mistake notes |
| decisions | list | `[[]]` links to decision notes |
| patterns | list | `[[]]` links to pattern notes |

## Session Note Body

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

## SESSIONS.md Index Format

`00_Memory/SESSIONS.md` is an **index** — NOT the session log itself.

```yaml
---
type: sessions-index
project: [PROJECT_CODE]
total: [N]
last: "[[YYYY-MM-DD-slug]]"
---
```

Body contains `[[links]]` to individual session notes in chronological order:

```markdown
## Session History

- [[2026-04-23-task-slug]]
- [[2026-04-22-another-task]]
- [[2026-04-21-bugfix-thing]]
```

## Outcome Emoji

| Outcome | Symbol |
|---------|--------|
| SUCCESS | ✅ |
| PARTIAL | ⚠️ |
| BLOCKED | 🚫 |
| FAILED | ❌ |

## Session Types That MUST Be Recorded

- ✅ Code implementation (any size)
- ✅ Bug fixes and debugging sessions
- ✅ Research and investigation
- ✅ Architecture and design decisions
- ✅ Refactoring work
- ✅ Configuration changes
- ✅ Documentation updates
- ✅ Code review responses
- ✅ Testing and verification
- ⚠️ Even "quick questions" if they led to action

**NO EXCEPTIONS. NO SHORTCUTS. EVERY SESSION LEAVES A TRAIL.**