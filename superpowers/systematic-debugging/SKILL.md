---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes.
quick_ref:
  iron_law: "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"
  phase1: "Root cause - read errors, reproduce, check changes"
  phase2: "Pattern - find working examples, compare"
  phase3: "Hypothesis - form theory, test minimally"
  phase4: "Implementation - create test, fix, verify"
---

# Systematic Debugging

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

## FILES

| File | Purpose |
|------|---------|
| `SKILL.md` | This index |
| `systematic-debugging.yaml` | Quick reference |
| `PHASE1_ROOT_CAUSE.md` | Root cause investigation |
| `PHASE2_PATTERN.md` | Pattern analysis |
| `PHASE3_HYPOTHESIS.md` | Hypothesis and testing |
| `PHASE4_IMPLEMENTATION.md` | Implementation + architecture question |
| `SUPPORTING.md` | Root cause tracing, defense in depth, condition-based waiting |

---

## THE IRON LAW

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

---

## FOUR PHASES

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |

---

## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Quick fix for now" | First fix sets pattern. Do it right. |
| "Just try X and see" | First fix sets pattern. Do it right. |
| "I see the problem" | Seeing symptoms ≠ root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. |
| "Reference too long, I'll adapt" | Partial understanding guarantees bugs. |