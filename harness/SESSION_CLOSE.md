# Session Close — MANDATORY

**TRIGGER:** User says "close session" or any equivalent

**NOT OPTIONAL.** Write complete session documentation.

## ILL Status Check (Before Closing)

1. Read `.memory/ill/captures.md` and `.global/ill/captures.md`
2. Count captures since last synthesis
3. If captures >= 3: add to Summary Output: "ILL: N captures since last synthesis — consider `synthesize`"

## Session Close Procedure

```
STEP 1: CREATE staging directory
  mkdir -p 00_Memory/.session-close-staging/

STEP 2: WRITE session note to staging
  01_Sessions/[YYYY-MM-DD-HHMM]-session.md (from template)

STEP 3: UPDATE canonical memory files in staging
  - 00_Memory/projectbrief.md (if changed)
  - 00_Memory/activeContext.md (always)
  - 00_Memory/progress.md (always)
  - 00_Memory/techContext.md (if changed)
  - 00_Memory/systemPatterns.md (if changed)

STEP 4: CREATE individual mistake notes in 02_Mistakes/
  - One note per mistake with frontmatter (status, category, lesson)
  - Use MISTAKE_TEMPLATE from 05_Templates/

STEP 5: CREATE/update individual pattern notes in 03_Patterns/
  - One note per pattern discovered
  - Use PATTERN_TEMPLATE from 05_Templates/

STEP 6: CREATE individual decision notes
  - One note per key decision with rationale
  - Link back to session note

STEP 7: VALIDATE staging
  - Check all files written without errors
  - Check all frontmatter valid
  - IF validation fails → STOP → report error

STEP 8: MOVE staging to vault (atomic)
  mv 00_Memory/.session-close-staging/* → final locations
  Remove staging directory

STEP 9: SYNC to global vault
  a. Copy mistake notes → {GLOBAL_VAULT}/00_Global/Mistakes/
  b. Copy pattern notes → {GLOBAL_VAULT}/00_Global/Patterns/
  c. Append session entry → {GLOBAL_VAULT}/00_Global/Sessions/

STEP 10: UPDATE 04_Index/Dashboard.md (refresh links)

STEP 11: GIT COMMIT (if in repo):
  git add . && git commit -m "chore: session close [YYYY-MM-DD HH:MM]"

STEP 12: OUTPUT summary
```

## SESSION_CLOSE.md Content

```markdown
# Session Close: [YYYY-MM-DD HH:MM]

## Session Metadata
- **Agent**     : [tool name]
- **Started**   : [time]
- **Ended**     : [current time]
- **Project**   : [from memory]
- **Task**      : [what was being worked on]

## Detailed Process Log
- [Timestamp] : [Action taken]
- [Timestamp] : [Result of action]
- [Timestamp] : [Next action decided]
...

## Files Modified
| File | Change | Lines |
|------|--------|-------|
| path/to/file | description | N |

## Mistakes Made
- [Any errors or incorrect assumptions during session]

## Mistakes Avoided (Referenced from MISTAKES.md)
- [Checked and avoided mistake X that was logged]

## Decisions Made
- [Choice A] → chose [option] because [reason]
- [Choice B] → chose [option] because [reason]

## State of Work
- **Completed** : [what finished successfully]
- **In Progress**: [what was interrupted]
- **Blocked**   : [any blockers]

## Next Session Starting Point
- **First Action**: [specific first step]
- **Files to Read**: [memory files to reload]
- **Context**: [1-paragraph handoff for incoming agent]
```

## Reflection Checkpoint
- **What went well**: [1-2 sentences]
- **What was inefficient**: [reference capture or brief note]
- **Any protocol gaps noticed**: [yes/no — if yes, log to captures.md]

## Summary Output

```
⚡ SESSION CLOSED
Agent  : [tool]
Time   : [start] → [end]
Files  : [N] modified
Mistakes: [N] made | [N] avoided
Stored : SESSIONS.md ✓ | progress.md ✓ | activeContext.md ✓ | Obsidian ✓ | Git ✓
```