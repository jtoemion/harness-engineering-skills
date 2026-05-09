# Test Quality Review — Findings Report Template

## Summary

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Determinism | — | 30% | — |
| Isolation | — | 30% | — |
| Maintainability | — | 25% | — |
| Performance | — | 15% | — |
| **Overall** | | | **—** |

**Framework:** [identified test framework]
**Total Tests:** [count]
**Test Types:** [unit/integration/e2e breakdown]

### Key Takeaway
[1–2 sentence summary of the most important thing to know about this test suite]

---

## Dimension Details

### Determinism (Score: —)
[2–4 sentences describing the overall state of determinism. Reference specific files/patterns if issues exist.]

### Isolation (Score: —)
[2–4 sentences describing test isolation. Note any state leakage or ordering dependencies.]

### Maintainability (Score: —)
[2–4 sentences describing readability, naming, and DRY adherence. Note any major pain points.]

### Performance (Score: —)
[2–4 sentences describing test speed and efficiency. Note any bottlenecks.]

---

## Findings

### [CRITICAL | IMPORTANT | MINOR] — [Finding Title]

**Location:** `path/to/file:line` or pattern description
**Dimension:** [Determinism | Isolation | Maintainability | Performance]
**Description:** [What is the issue and why does it matter?]
**Recommendation:** [Specific, actionable fix]

[Repeat for each finding]

---

## Quick Wins

| # | Finding | Effort | Impact | Dimension |
|---|---------|--------|--------|-----------|
| 1 | [Brief description] | Low | High | [Dimension] |
| 2 | [Brief description] | Low | High | [Dimension] |

---

## Long-Term Improvements

| # | Improvement | Effort | Impact | Dimension |
|---|------------|--------|--------|-----------|
| 1 | [Brief description] | High | High | [Dimension] |
| 2 | [Brief description] | Medium | Medium | [Dimension] |