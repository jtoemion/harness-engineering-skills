# Phase 4: Generate

Produce markdown synthesis document with pattern → cost → fix structure.

## Document Structure

```markdown
# ILL Synthesis — YYYY-MM-DD

## Summary
- **Total captures**: N
- **Patterns identified**: N
- **Total time cost**: N min
- **Total token cost**: N tokens
- **Promotion candidates**: N

## Patterns

### [TAG] Pattern Name

**Occurrences**: N sessions across M projects
**Time cost**: N min
**Token cost**: N tokens
**Severity breakdown**: X FRICTION, Y BLOCKER
**Root cause**: [derived from capture descriptions — what caused this pattern]
**Fix**: [specific, actionable — agent can execute this without further guidance]
**Example**: [brief example from actual captures, if available]

---

### [TAG] Next Pattern
...
```

## Root Cause Derivation

From capture descriptions, extract the common failure mechanism:
- Look for repeating phrases across captures
- Identify the decision point or step where failure occurred
- Frame as a system/agent behavior, not a one-off mistake

## Fix Prescription Rules

1. **Specific**: Agent can act on it immediately, no interpretation needed
2. **Actionable**: Direct instruction, not a principle
3. **Preventive**: Prevents recurrence, not just documents the issue
4. **Measurable**: Agent can verify fix was applied

## Example

**Bad fix**: "Be more careful with subagent briefs"
**Good fix**: "If SUBAGENT_BRIEF.md exceeds 1 page, split into 2 separate briefs before dispatch"

## Next Phase

Pass draft synthesis to Phase 5 (Promote).