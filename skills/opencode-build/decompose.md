---
name: opencode-build/decompose
description: Use when a task is too large for a single atomic cycle. Decompose into minimal tracer bullets.
---

# Decompose into Atomic Tasks

## Rule

One atomic task = one diff = one behavior = one TDD cycle.
If it takes more than 3 cycles, it needs decomposition.

## How to Decompose

```
Large task
    ↓
"what is the smallest slice that proves the path works?"
    ↓
One behavior per slice
    ↓
Each slice: RED test → GREEN impl → next slice
```

## Signal to Decompose

```
[ ] Task mentions "and", "also", "plus", "including"
[ ] More than 3 files to touch
[ ] More than 1 conceptual change
[ ] Not a single user-facing behavior
```

## Example

```
WRONG: "Add auth + cart + checkout to the app"
RIGHT: "Add login with email/password" → next cycle: "Protect cart route"

WRONG: "Refactor the checkout flow"
RIGHT: "Extract payment processor into separate module" → next: "Update checkout to use new module"
```

## Minimal Acceptable Atomic Task

```
Given [input]
When [action]
Then [observable result]
```

Testable in one RED→GREEN cycle. No speculation about what comes next.

## Next Steps

- Task decomposed? → back to `opencode-build/SKILL.md`
- Need to verify decomposition is right? → `opencode-build/verify-decompose.md`
