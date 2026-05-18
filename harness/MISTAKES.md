# Global Mistakes Log

This file tracks all mistakes made across projects to prevent repetition.
Format: `[DATE] | [CATEGORY]` — each entry encodes an assumption that failed.

## Schema
```markdown
## [YYYY-MM-DD] | [MISTAKE CATEGORY]
**Error**     : [What went wrong]
**Cause**     : [Why it happened]
**Lesson**    : [How to avoid it in future]
**References**: [Files/code affected]
**Status**    : [ACTIVE | RESOLVED | SUPERSEDED]
```

---

## Knowledge Infrastructure Status

| Component | Status | Notes |
|-----------|--------|-------|
| Variable tracking | ✅ Implemented | variables.json template with seed entries in runtime/templates/ |
| File-based KB (JSON) | ✅ Implemented | Templates in runtime/templates/; boot auto-creates skeletons in .memory/ |
| Mistake catching | ⚠️ Partial | MISTAKES.md exists; gate enforcement added; still depends on agent compliance |
| Boot receipt | ✅ Implemented | harness.py generates receipt at boot with knowledge file counts |
| Pre-task gates | ✅ Implemented | Queries JSON knowledge + permission error diagnosis protocol |
| Close verification gate | ✅ Implemented | Checks boot receipt, mistakes_checked, mistakes.json/patterns.json staleness |

---

## Entry Template (DO NOT DELETE THIS LINE)
<!-- New entries go below this line -->
## [2026-05-18] | SUBAGENT SCHEMA DIVERGENCE — DUPLICATE VS IMPORT
**Error**     : Build subagent created local copy of _write_incident() instead of importing from shared incident.py
**Cause**     : Brief showed code blocks from the plan spec. Subagent reproduced them as new functions rather than importing existing shared module.
**Lesson**    : Briefs for shared resources must explicitly state: "Import from [path]. Do NOT create new functions." Show the import statement, not the function body.
**References**: session_close.py (duplicated), incident.py (canonical), SUBAGENT_PROTOCOL.md (brief template)
**Status**    : ACTIVE

## [2026-05-17] | FIRESTORE SECURITY RULES — ANONYMOUS PROXY UID MISMATCH
**Error**     : FirebaseError: Missing or insufficient permissions when creating sessions
**Cause**     : `CreateSessionModal.tsx` passed `userProfile?.uid` as `tutorId`. For PIN login (anonymous proxy auth), `uid` is the anonymous Firebase UID, but Firestore `getRealUserId()` resolves to the real user ID via session doc lookup — causing a rule mismatch.
**Lesson**   : When using `getRealUserId()` in Firestore security rules to resolve anonymous → real UID, ALL writes must pass `actualUserId || uid` (not bare `uid`). This pattern must be applied consistently everywhere the resolved user ID is needed.
**References**: `firestore.rules:206-208` (package_sessions create rule), `CreateSessionModal.tsx:166` (the fix), `authService.ts:88-107` (PIN login creates anonymous session doc)
**Status**    : ACTIVE
