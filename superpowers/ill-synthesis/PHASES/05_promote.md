# Phase 5: Promote

Evaluate patterns for global promotion. Full agent judgment required.

## Promotion Criteria

| Criterion | Threshold | Source |
|-----------|-----------|--------|
| Sessions | 3+ | From capture timestamps |
| Projects | 2+ | From global captures origin |

## Evaluation Process

For each pattern group where criteria are met:

1. **Read captures** in the group — understand what the pattern really is
2. **Assess generalization**: Does this pattern apply beyond the specific projects where it occurred?
   - If pattern is project-specific (technology, team structure, business domain) → do NOT flag
   - If pattern is agent/system-level (protocol, decision-making, behavior) → flag for promotion
3. **Judge severity**: Even if criteria met, is this worth promoting?
   - Minor friction that agents self-correct → do NOT flag
   - Systematic failure that causes repeated blockers → flag
4. **Formulate global rule**: If promoting, write the rule as it would appear in GLOBAL_VAULT

## Full Agent Judgment Criteria

Ask: "Would this rule prevent real failures in projects that have nothing to do with the ones I've seen this pattern in?"

| If yes | → Flag for promotion |
| If no | → Do not flag (even if criteria numerically met) |

## Output

### In Synthesis Document

```markdown
## Promotion Candidates

| Pattern | Sessions | Projects | Assessment | Status |
|---------|----------|----------|------------|--------|
| [delegation] context blowup | 5 | 3 | Generalizes to protocol issue | FLAG: needs approval |
| [cache] repeated exploration | 4 | 1 | Project-specific tech choice | NOT PROMOTED |
```

### Promotion Notes (for human approval)

Create note in `.memory/ill/promotion-queue/`:
- Pattern name
- Capture count and project count
- Assessment reasoning
- Proposed global rule text

## Next Phase

Pass final synthesis to Phase 6 (Archive).