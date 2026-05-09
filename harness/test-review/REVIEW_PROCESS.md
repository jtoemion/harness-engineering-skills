# Review Process

## Step 1: Discovery

Gather context about the test suite before analyzing.

### Actions
1. Find all test files in the project
2. Identify the test framework(s) used
3. Count total tests and categorize by type (unit, integration, e2e)
4. Note test directory structure and naming conventions

### Key Questions
- Where are the tests? (`__tests__/`, `*.test.*`, `*.spec.*`, `tests/`, `test/`)
- What framework? (Jest, Vitest, pytest, Go test, etc.)
- How many tests exist?
- Are there separate unit/integration/e2e suites?

---

## Step 2: Analysis

Evaluate each test file (or representative sample if the suite is large) against the 4 review dimensions.

### Approach
- Read test files directly — don't just look at test names
- For large suites (100+ tests), sample the most critical or most recently changed files
- Check for patterns: if one file has a problem, search for the same pattern elsewhere
- Note file paths and line numbers for specific findings

### Per-Dimension Analysis

**Determinism:**
- Search for `sleep`, `setTimeout`, `wait`, `delay`, `retry` patterns
- Check for unseeded random usage
- Look for time-dependent assertions
- Verify async patterns use proper await, not timing hacks

**Isolation:**
- Check for global mutable state
- Look at `beforeAll`/`beforeEach`/`afterEach` patterns
- Verify test data independence
- Check for shared state between describe blocks
- Look for test-ordering hints (e.g., "run this test first")

**Maintainability:**
- Evaluate test naming conventions
- Check for magic numbers/strings
- Look for copy-paste patterns
- Assess assertion quality (specific vs. loose)
- Check coupling to implementation details

**Performance:**
- Identify `sleep`/`wait` calls that indicate polling
- Check for unnecessary real network calls
- Look for heavy fixture creation per-test vs per-suite
- Identify tests that could run in parallel but don't

---

## Step 3: Scoring

Rate each dimension 0–100 using the criteria in `REVIEW_DIMENSIONS.md`.

### Rules
- Score based on the **overall** state of the suite, not just the worst file
- A few minor issues don't sink a dimension — look at patterns, not outliers
- A single critical pattern (e.g., pervasive flakiness) can drag a score below 50
- Be honest: a 90+ score means the suite is genuinely excellent in that dimension

### Overall Score

```
overall = (determinism × 0.30) + (isolation × 0.30)
        + (maintainability × 0.25) + (performance × 0.15)
```

---

## Step 4: Report

Produce a structured findings report using `FINDINGS_TEMPLATE.md`.

### Report Structure
1. **Summary** — Overall score, dimension scores, key takeaway
2. **Dimension Details** — Per-dimension analysis with specific evidence
3. **Findings List** — Each finding with severity, description, location, and recommendation
4. **Quick Wins** — Changes that are high-impact and low-effort
5. **Long-Term Improvements** — Strategic investments in test quality

### Severity Ratings
- **Critical** — Tests produce incorrect or unreliable results. Must fix before relying on the suite.
- **Important** — Tests are fragile or hard to maintain. Should fix soon to avoid developer pain.
- **Minor** — Tests work but could be improved. Fix when convenient.

### Findings Guidance
- Every finding must reference a specific file or pattern
- Provide actionable recommendations, not just "this is bad"
- Prioritize findings by severity and ease of fix
- Include code snippets or patterns to illustrate where possible