---
name: subagent-driven-development
description: Execute implementation plans with independent tasks. Fresh subagent per task, two-stage review.
quick_ref:
  flow: "extract tasks → CREATE BRIEF → dispatch implementer → spec review → quality review → checkpoint"
  brief: "SUBAGENT_BRIEF.md (max 1 page) → subagent → SUBAGENT_RESULT.md only"
  review_order: "spec compliance BEFORE code quality"
---

# Subagent-Driven Development

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

## FILES

| File | Purpose |
|------|---------|
| `SKILL.md` | This index |
| `subagent-driven-development.yaml` | Quick reference |
| `IMPLEMENTER_PROMPT.md` | Implementer subagent prompt |
| `SPEC_REVIEWER_PROMPT.md` | Spec compliance reviewer |
| `CODE_QUALITY_REVIEWER_PROMPT.md` | Code quality reviewer |

## HARNESS INTEGRATION

**Boot:** Run harness boot sequence BEFORE any task.

**Mistakes check:** Before each task, check `harness/MISTAKES.md`.

**Subagent protocol:** Uses `harness/SUBAGENT_PROTOCOL.md` — compacted briefs only.

---

## PROCESS (PER TASK)

```
1. Create TodoWrite for all tasks
2. Extract full task text + context (never let subagent read plan)
3. CREATE SUBAGENT_BRIEF.md (compact)
4. DISPATCH implementer subagent
5. SUBAGENT writes SUBAGENT_RESULT.md
6. READ RESULT only, UPDATE memory
7. CHECK MISTAKES.md
8. DISPATCH spec reviewer subagent
9. If issues → implementer fixes → re-review
10. DISPATCH code quality reviewer
11. If issues → implementer fixes → re-review
12. MARK task complete, LOG to SESSIONS.md
13. REPEAT for next task
```

---

## RED FLAGS

**NEVER:**
- Start on main/master without consent
- Skip spec OR code quality reviews
- Proceed with unfixed issues
- Dispatch multiple implementers in parallel
- Make subagent read plan (provide full text)
- Skip review loops
- Start quality review before spec compliance
- Move to next task with open issues
- Ignore harness mistakes check

---

## REQUIRED SKILLS

- `superpowers:using-git-worktrees` — Set up isolated workspace
- `superpowers:writing-plans` — Creates plan
- `superpowers:requesting-code-review` — Code review template
- `superpowers:finishing-a-development-branch` — Complete development

**Subagents should use:** `superpowers:test-driven-development`