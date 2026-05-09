# Phase 4 — Implementation

**Fix the root cause, not the symptom:**

## Steps

```
1. Create Failing Test Case
   - Simplest possible reproduction
   - Automated test if possible
   - One-off test script if no framework
   - MUST have before fixing
   - Use test-driven-development skill for writing proper failing tests

2. Implement Single Fix
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements
   - No bundled refactoring

3. Verify Fix
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved?

4. If Fix Doesn't Work
   - STOP
   - Count: How many fixes have you tried?
   - If < 3: Return to Phase 1, re-analyze with new information
   - If ≥ 3: STOP and question the architecture (see below)
   - DON'T attempt Fix #4 without architectural discussion

5. If 3+ Fixes Failed: Question Architecture

   Pattern indicating architectural problem:
   - Each fix reveals new shared state/coupling/problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   STOP and question fundamentals:
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

   Discuss with human partner before attempting more fixes

   This is NOT a failed hypothesis - this is a wrong architecture.
```

---

## Red Flags - STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals new problem in different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (see Phase 4.5)

---

## Human Partner's Signals You're Doing It Wrong

Watch for these redirections:
- "Is that not happening?" - You assumed without verifying
- "Will it show us...?" - You should have added evidence gathering
- "Stop guessing" - You're proposing fixes without understanding
- "Ultrathink this" - Question fundamentals, not just symptoms
- "We're stuck?" (frustrated) - Your approach isn't working

**When you see these:** STOP. Return to Phase 1.