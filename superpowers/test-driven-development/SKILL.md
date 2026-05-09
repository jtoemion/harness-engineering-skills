---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code.
quick_ref:
  iron_law: "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"
  cycle: "RED → GREEN → REFACTOR → repeat"
  verify_red: "Watch test fail for expected reason"
  verify_green: "Watch test pass, all tests pass"
---

# Test-Driven Development (TDD)

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

## FILES

| File | Purpose |
|------|---------|
| `SKILL.md` | This index |
| `test-driven-development.yaml` | Quick reference |
| `RED_GREEN_REFACTOR.md` | The cycle |
| `RATIONALIZATIONS.md` | Common excuses + reality |
| `ANTI_PATTERNS.md` | Testing anti-patterns (external file) |

---

## THE IRON LAW

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before test? Delete it. Start over.
No exceptions.

---

## QUICK REF

### Red-Green-Refactor Cycle

```
RED     → Write failing test
        → Verify fails correctly
GREEN   → Write minimal code to pass
        → Verify passes
REFACTOR → Clean up (keep tests green)
        → Next failing test
```

### Verification Checklist

Before marking complete:
- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for expected reason
- [ ] Wrote minimal code to pass
- [ ] All tests pass
- [ ] Output pristine (no errors/warnings)
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered

---

## WHEN STUCK

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write wished-for API. Write assertion first. |
| Test too complicated | Design too complicated. Simplify interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup huge | Extract helpers. Still complex? Simplify design. |

---

## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Unverified code = technical debt. |
| "TDD will slow me down" | TDD faster than debugging. |
| "Existing code has no tests" | You're improving it. Add tests for existing code. |