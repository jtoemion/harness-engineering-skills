# Review Dimensions

Tests are evaluated across 4 dimensions. Each dimension is scored 0–100.

## 1. Determinism (Weight: 30%)

Do tests produce the same results every run?

### Green Flags
- Results are identical across repeated runs
- No dependency on system clock or random values without seeding
- Async operations use proper await/promise patterns
- Date/time values are mocked or fixed
- External service calls are stubbed or mocked
- File system operations use temp directories with cleanup

### Red Flags
- `setTimeout` / `sleep` used to "wait for" async results
- Unseeded random number generation in assertions
- Race conditions in concurrent test execution
- Tests that pass locally but fail in CI (or vice versa)
- Time-dependent logic without time mocking
- Floating-point comparisons without epsilon tolerance
- Flaky test patterns: occasionally failing without code changes

### Scoring
| Score | Criteria |
|-------|----------|
| 90–100 | All tests deterministic, proper mocking patterns throughout |
| 70–89 | Minor issues: a few loose timing assumptions, mostly solid |
| 50–69 | Some flaky tests exist; occasional non-determinism observed |
| 30–49 | Multiple non-deterministic patterns; tests unreliable in CI |
| 0–29 | Widespread flakiness; results cannot be trusted |

---

## 2. Isolation (Weight: 30%)

Can tests run in any order without affecting each other?

### Green Flags
- Each test creates its own data and cleans up after itself
- Tests have no implicit ordering dependencies
- Database/state resets happen between tests or test suites
- Shared resources use proper locking or are avoided entirely
- Test runner can parallelize the suite safely
- `beforeEach`/`afterEach` properly manage state

### Red Flags
- Tests that only pass when run in a specific order
- Global or module-level mutable state shared between tests
- Tests that modify shared resources without cleanup
- Database records that accumulate across test runs
- Singleton patterns that carry state between tests
- Tests that depend on side effects of earlier tests

### Scoring
| Score | Criteria |
|-------|----------|
| 90–100 | Full isolation; any test can run standalone or in parallel |
| 70–89 | Minor coupling: shared fixtures that are properly reset |
| 50–69 | Some tests have implicit order dependencies |
| 30–49 | Significant state leakage between tests |
| 0–29 | Tests are tightly coupled; cannot run independently |

---

## 3. Maintainability (Weight: 25%)

Are tests easy to understand, modify, and extend?

### Green Flags
- Test names clearly describe the scenario and expected outcome
- Arrange-Act-Assert pattern is evident and consistent
- Magic values are named constants or test factories
- Helper functions reduce duplication without hiding intent
- Tests are resilient to minor implementation changes
- Comments explain *why*, not *what*

### Red Flags
- Hardcoded magic numbers with no explanation
- Copy-pasted setup code across many tests
- Test names like `test1`, `testFoo`, or vague descriptions
- Over-mocking: tests that mock everything and test nothing
- Brittle assertions tied to implementation details
- Fixture files that are never updated or documented
- Tests that break on minor refactors of production code

### Scoring
| Score | Criteria |
|-------|----------|
| 90–100 | Clear, DRY, well-named; easy to add new tests |
| 70–89 | Generally clear; some duplication or magic values |
| 50–69 | Readable but fragile; moderate duplication |
| 30–49 | Hard to follow; significant copy-paste; brittle |
| 0–29 | Opaque, unmaintainable; tests are a liability |

---

## 4. Performance (Weight: 15%)

Are tests fast enough to run frequently without friction?

### Green Flags
- Unit tests complete in milliseconds
- Integration tests use lightweight dependencies
- Fixture creation is efficient and purposeful
- Async operations use proper await, not polling loops
- Test suite completes in reasonable time (< 5 min for unit, < 15 min for integration)
- Slow tests are marked or grouped separately

### Red Flags
- `sleep()` / `setTimeout` waits instead of proper async handling
- Unnecessary network calls to real services
- Heavy fixture creation that could be simplified
- Database setup/teardown per test when per-suite would suffice
- Repeated expensive computations that could be cached
- Tests that scale poorly with data size

### Scoring
| Score | Criteria |
|-------|----------|
| 90–100 | Fast suite; runs in seconds; no unnecessary delays |
| 70–89 | Mostly fast; a few slow tests identified and acceptable |
| 50–69 | Noticeable delays; suite takes minutes; some low-hanging fruit |
| 30–49 | Slow suite; developers avoid running it; significant waste |
| 0–29 | Impractically slow; suite is a bottleneck in development |

---

## Overall Score Calculation

```
overall = (determinism × 0.30) + (isolation × 0.30)
        + (maintainability × 0.25) + (performance × 0.15)
```

Rounded to nearest integer.