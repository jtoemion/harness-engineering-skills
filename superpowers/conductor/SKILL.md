---
name: conductor
description: Autonomous workflow orchestrator. Design sequence, build pipeline, drive to completion.
quick_ref:
  read_intent: "Phase 1 before anything"
  build_pipeline: "Phase 2 skill order"
  await_approval: "Phase 4 - explicit GO required"
  orchestrate: "Phase 5 - announce each stage"
  max_stages: "3 per session, auto-split if more"
---

# CONDUCTOR

Designs the exact sequence to solve problems, then drives that pipeline to completion.

## FILES

| File | Purpose |
|------|---------|
| `SKILL.md` | This index |
| `conductor.yaml` | Quick reference |
| `PHASE1_INTENT.md` | Intent analysis |
| `PHASE2_PIPELINE.md` | Pipeline construction |
| `PHASE3_PROPOSAL.md` | Pipeline proposal format |
| `PHASE5_EXECUTION.md` | Orchestrated execution |
| `SKILL_ORDER.md` | Canonical skill order |
| `COMPLEXITY_TIERS.md` | Tier definitions |

---

## PROCESS

```
PHASE 1: INTENT ANALYSIS
  → Classify against Intent Matrix
  → Assign Complexity Tier

PHASE 2: PIPELINE CONSTRUCTION
  → Build skill sequence
  → Check context budget (max 3 stages)
  → Atomic task rules (≤3 files)

PHASE 3: PIPELINE PROPOSAL
  → Present for approval
  → Wait for GO/ADJUST/SKIP/SWAP

PHASE 4: AWAIT APPROVAL
  → Explicit GO required before execution

PHASE 5: ORCHESTRATED EXECUTION
  → Announce each stage
  → Execute, pass outputs forward
  → Session split if needed

PHASE 6: COMPLETION
```

---

## INTENT MATRIX

| Signal | Skill |
|--------|-------|
| Vague idea | brainstorming |
| Approved spec | writing-plans |
| Plan ready | executing-plans |
| New feature/cross-layer | architectural-impact + writing-plans + TDD |
| UI/Component | frontend-avant-garde + TDD |
| Bug/Regression | systematic-debugging + verification |
| Multiple independent tasks | subagent-driven-development |
| Before merge/PR | requesting-code-review |
| Feedback on code | receiving-code-review |
| New branch | using-git-worktrees |
| Branch complete | finishing-a-development-branch |
| Session start | memorybank Phase 1 |
| Task complete | memorybank Phase 2 |
| File touched | dev-journey-log |
| ULTRATHINK keyword | ultrathink-mode (prepend) |
| Multi-concern | conductor builds pipeline |

---

## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Skip pipeline, I know skill" | You know primary, not cascade. |
| "5 stages fit in one session" | Max 3. Split. No exceptions. |
| "I'll carry context mentally" | Explicit Carrying: required. |
| "Skip scope-guard" | Small tasks grow silently. |