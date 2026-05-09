# Phase 5 — Orchestrated Execution

## Stage Announcement

Before each stage:
```
⚡ STAGE [N] of [TOTAL] | [skill-name] [ANTIGRAVITY/SUPERPOWERS]
  Goal  : [stage goal]
  Scope : [declared files]
```

## Execution

```
- Read the skill file, execute fully
- Pass outputs forward explicitly (announce what you're carrying)
- Scope guard check: before each file edit, verify file is in declared scope
- On blocking issue → pause, surface options, await decision
```

## Stage Completion

```
✓ STAGE [N] COMPLETE
  Produced : [what was created]
  Carrying : [context for next stage]
```

## Session Boundary

If session must split:
```
⚠ SESSION SPLIT — Stages [N+1 to M] deferred
  Resume with: "Continue pipeline from Stage [N+1]"
  Carry forward: [minimal artifact/decision list]
  ⚡ CHECKPOINT SAVED
```