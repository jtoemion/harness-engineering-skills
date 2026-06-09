---
name: opencode-build/verify-decompose
description: Use after decomposing a task to verify each atomic piece is actually atomic.
---

# Verify Decomposition

## Checklist per Atomic Piece

```
[ ] One input → one action → one observable result
[ ] Testable in a single RED→GREEN cycle
[ ] No dependency on next piece to verify
[ ] Can ship independently without breaking anything
[ ] Name describes WHAT not HOW
```

## Anti-Patterns

```
"validate user input and save to DB"    → two things (validate + save)
"check auth then redirect"              → two things (check + redirect)
"add loading state and error handling" → two things (loading + error)
```

Each = separate atomic task.

## Review the Full Slice Chain

After decomposing, review the full chain:
```
Can piece 1 be tested and shipped alone? YES → atomic
Does piece 2 depend on piece 1 being done?  YES → correct order
Does any piece assume future pieces exist?  YES → not atomic
```

## When Decomposition Fails

If a piece can't be tested alone → it needs to be smaller.
If a piece depends on another → reorder.
If a piece assumes future state → rewrite to be self-contained.

## Next Steps

- Decomposition verified? → `opencode-build/SKILL.md`
- Found issue during decomposition? → `opencode-build/decompose.md`
