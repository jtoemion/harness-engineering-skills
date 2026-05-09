# Supporting Techniques

These techniques are part of systematic debugging.

## Root Cause Tracing

Trace bugs backward through call stack to find original trigger.

See `root-cause-tracing.md` in this directory.

## Defense in Depth

Add validation at multiple layers after finding root cause.

See `defense-in-depth.md` in this directory.

## Condition-Based Waiting

Replace arbitrary timeouts with condition polling.

See `condition-based-waiting.md` in this directory.

---

## Related Skills

- **superpowers:test-driven-development** — For creating failing test case (Phase 4, Step 1)
- **superpowers:verification-before-completion** — Verify fix worked before claiming success

---

## When "No Root Cause" Is Found

If systematic investigation reveals issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

**But:** 95% of "no root cause" cases are incomplete investigation.