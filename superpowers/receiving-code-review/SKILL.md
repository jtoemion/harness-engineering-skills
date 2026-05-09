---
name: receiving-code-review
description: Use when receiving code review feedback, before implementing suggestions.
quick_ref:
  verify_first: "Check against codebase reality before implementing"
  no_performative: "No 'great point' or 'thanks' - state fix or pushback"
  clarify_first: "If any item unclear, STOP and ask"
---

# Receiving Code Review

**Core principle:** Verify before implementing. Ask before assuming. Technical correctness over social comfort.

## FILES

| File | Purpose |
|------|---------|
| `SKILL.md` | This index |
| `receiving-code-review.yaml` | Quick reference |
| `RESPONSE_PATTERN.md` | The response process |
| `PUSHBACK.md` | When and how to push back |
| `EXAMPLES.md` | Real examples |

---

## RESPONSE PATTERN

```
1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

---

## FORBIDDEN RESPONSES

**NEVER:**
- "You're absolutely right!" (explicit violation)
- "Great point!" / "Excellent feedback!" (performative)
- "Let me implement that now" (before verification)

**INSTEAD:**
- Restate the technical requirement
- Ask clarifying questions
- Push back with technical reasoning if wrong
- Just start working (actions > words)

---

## IMPLEMENTATION ORDER

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Test each fix individually
  4. Verify no regressions
```

---

## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Reviewer is right" | Verify against codebase. Check if breaks things. |
| "I'll implement now" | Verify first. Could break functionality. |
| "Thanks for feedback" | Delete. State fix instead. Actions speak. |