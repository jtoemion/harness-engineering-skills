---
name: test-review
description: Use when evaluating test quality, reviewing test suites for determinism, isolation, maintainability, and performance
quick_ref:
  purpose: "Review test quality across 4 dimensions and produce actionable findings"
  trigger: "review tests | evaluate test quality | test review"
  produces: "Structured findings report with dimension scores and improvement recommendations"
---

# Test Quality Review

Review test suites for structural quality, reliability, and maintainability.
This skill evaluates **test quality** — not code quality (use `requesting-code-review` for that).

## When to Use

- "review tests" / "evaluate test quality" / "test review"
- Before merging significant test additions
- When test suites are flaky, slow, or hard to maintain
- As part of PR review when test changes are substantial

## Review Dimensions

Tests are evaluated across 4 dimensions (see `REVIEW_DIMENSIONS.md`):

| Dimension | Focus | Weight |
|-----------|-------|--------|
| Determinism | Same results every run | 30% |
| Isolation | Any order, no leakage | 30% |
| Maintainability | Easy to understand and update | 25% |
| Performance | Fast enough, no unnecessary waits | 15% |

## Review Process

See `REVIEW_PROCESS.md` for the full process:

1. **Discovery** — Find test files, identify framework, count tests
2. **Analysis** — Evaluate each test against the 4 dimensions
3. **Scoring** — Rate each dimension 0–100, calculate weighted overall score
4. **Report** — Generate structured findings using `FINDINGS_TEMPLATE.md`

## Quick Reference

See `test-review.yaml` for the condensed reference card.

## Execution

1. Read `REVIEW_DIMENSIONS.md` to understand evaluation criteria
2. Follow `REVIEW_PROCESS.md` step by step
3. Use `FINDINGS_TEMPLATE.md` to structure your output
4. Assign dimension scores and overall score
5. Deliver findings directly — no excessive prompts or confirmations

## Key Principles

- Work with ANY project — no assumptions about domain or framework
- Focus on structural test quality, not feature coverage
- Score objectively based on observable criteria
- Prioritize findings: Critical → Important → Minor
- Be autonomous: read files, analyze, report — don't ask permission for each step

## Output

Produces a structured findings report containing:
- Per-dimension scores with justification
- Specific findings with file/line references where possible
- Severity-rated improvement recommendations
- Overall weighted quality score