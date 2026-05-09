# Phase 3 — Subagent Result Checkpointing

When subagent completes via `SUBAGENT_RESULT.md`:

## Parent Process

```
1. READ SUBAGENT_RESULT.md (ONLY this — no raw files)
2. EXTRACT:
   - Status
   - Summary
   - Evidence
   - Next
   - Files
3. LOG any mistakes from subagent to 02_Mistakes/:
   - Create individual mistake notes (ID: {CODE}-M###-slug.md)
   - Set status: ACTIVE for unresolved, RESOLVED for fixed
4. UPDATE 00_Memory/activeContext.md with subagent findings
5. CREATE individual session note in 01_Sessions/:
   - Filename: YYYY-MM-DD-subagent-[task-slug].md
   - Frontmatter: type, project, date, outcome, task, mistakes
   - Body: Subagent task, status, key outputs, mistakes surfaced
6. UPDATE 00_Memory/SESSIONS.md:
   - APPEND [[link]] to new session note
7. IF new patterns from subagent:
   - CREATE pattern notes in 03_Patterns/
8. UPDATE 04_Index/Dashboard.md
9. SYNC to global vault (if available)
10. CONTINUE parent task
```

## Subagent Result Schema

```markdown
# Subagent Result: [TASK NAME]
**Status**   : [SUCCESS | PARTIAL | FAILED]
**Summary**  : [What was done — max 500 words]
**Evidence** : [Key findings with file:line references]
**Next**     : [Recommended parent actions]
**Files**    : [Any files created/modified — path only]
**Mistakes** : [Any mistakes made during work]
```

## Harness Subagent Protocol

The harness skill defines the subagent protocol:
- Parent creates `SUBAGENT_BRIEF.md`
- Subagent writes `SUBAGENT_RESULT.md`
- Parent reads RESULT only

See `harness/SUBAGENT_PROTOCOL.md`