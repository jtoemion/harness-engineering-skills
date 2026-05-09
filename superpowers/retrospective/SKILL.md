---
name: retrospective
description: Post-pipeline learning extraction — runs after Complex/Ultrathink pipelines to capture what went wrong, what was unexpected, and what patterns emerged
---

# Retrospective

## Overview

The retrospective skill is a closing protocol that extracts lessons from completed pipelines. It runs after Complex and Ultrathink tier pipelines and writes findings to `.memory/systemPatterns.md` so future sessions inherit the learning.

**Without this skill, the system makes the same mistakes in session 50 that it made in session 1.**

**Announce at start:** "Running retrospective to capture lessons from this pipeline."

## When It Fires

- **Always** after Complex or Ultrathink tier pipelines
- **Optionally** after Moderate tier if something unexpected happened
- **Never** after Simple tier (not enough signal to extract)
- Runs **after** verification-before-completion, **before** dev-journey-log and memorybank Phase 2

## The Process

### Step 1: Pipeline Review (2 minutes)

Answer these questions about the pipeline that just completed:

1. **What was the original plan?** (stages, scope, estimated effort)
2. **What actually happened?** (stages completed, scope changes, actual effort)
3. **Where did plan ≠ reality?** (list every deviation)

### Step 2: Extract Lessons (3 minutes)

For each deviation, classify:

| Category | Question | Example |
|---|---|---|
| **Estimation** | Did we underestimate complexity? | "Auth was Medium but should have been Large" |
| **Scope** | Did scope drift occur? How many times? | "3 scope expansions — task wasn't atomic" |
| **Tooling** | Did a tool or command behave unexpectedly? | "Build failed due to missing dependency" |
| **Pattern** | Did we discover a reusable pattern? | "All API routes need error middleware" |
| **Anti-pattern** | Did we do something we should never repeat? | "Edited shared config without checking consumers" |
| **Blocker** | What blocked progress? | "Waited on user for 2 hours for DB credentials" |

### Step 3: Write to systemPatterns.md

Append findings to `.memory/systemPatterns.md` in this format:

```markdown
## [DATE] — [Pipeline Summary]

**Tier:** [Complex/Ultrathink]
**Stages planned:** [N] | **Stages actual:** [N]
**Scope expansions:** [N]

### Lessons
- [ESTIMATION] [lesson]
- [PATTERN] [lesson]
- [ANTI-PATTERN] [lesson]

### Rules Discovered
- [New rule or constraint that should apply to future work]
```

### Step 4: Check for Recurring Issues

Before finishing, scan previous entries in `systemPatterns.md`:

- **Same lesson appearing 2+ times?** → Escalate: "This issue has occurred [N] times. Consider creating a new rule or skill to prevent it."
- **Same file causing problems repeatedly?** → Flag: "[file] has been involved in [N] incidents. May need refactoring."
- **Same estimation error repeating?** → Adjust: "Tasks involving [type] are consistently underestimated. Default to Large."

## Output Format

```
⚡ RETROSPECTIVE COMPLETE
  Pipeline    : [summary]
  Deviations  : [N] found
  Lessons     : [N] captured
  Recurring   : [N] patterns flagged
  Written to  : .memory/systemPatterns.md
```

## Integration

- **Conductor** includes retrospective in canonical order for Complex/Ultrathink
- **memorybank** Phase 2 runs after retrospective (retrospective feeds into memory)
- **systemPatterns.md** is read by memorybank Phase 1 on boot, so lessons persist

## Anti-Rationalization

| Rationalization | Why It's Wrong |
|---|---|
| "The pipeline went smoothly, nothing to capture" | Smooth pipelines have patterns worth replicating. Capture what went right. |
| "I'll remember this for next time" | You won't. You're stateless. Write it down. |
| "This lesson is obvious" | If it's obvious, writing it takes 10 seconds. If it's not, you just proved why it needs writing. |
| "systemPatterns.md is getting long" | Long = lots of lessons = system improving. Trim only if entries are truly obsolete. |
