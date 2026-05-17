---
name: retrospective
description: "Mandatory closing protocol that extracts pipeline lessons AND synthesizes ILL captures. Fires at every session close. Two-section output: Pipeline Lessons + Moment Captures."
quick_ref:
  trigger: "EVERY session close (mandatory) OR user asks for lessons learned"
  sections: "Pipeline Lessons (always) + Moment Captures (if captures >= 1)"
  outputs: ".memory/mistakes.json, .memory/patterns.json, .memory/ill/synthesis.md"
---

# Retrospective & ILL Synthesis

## Overview

The retrospective skill is a **mandatory closing protocol** that combines two functions:

1. **Pipeline Lessons**: Extract what went right/wrong across the whole session
2. **Moment Captures**: Synthesize ILL (Iterative Learning Layer) captures into actionable patterns

**Without this skill, the system makes the same mistakes in session 50 that it made in session 1.**

**Announce at start:** "Running retrospective and ILL synthesis to capture lessons."

## When It Fires

- **MANDATORY** at every session close (not just Complex/Ultrathink)
- **Optionally** when user asks for lessons learned
- Runs **after** verification-before-completion, **before** dev-journey-log and memorybank Phase 2

---

## Section 1: Pipeline Lessons (ALWAYS runs)

### Step 1: Pipeline Review

Answer these questions about the pipeline that just completed:

1. **What was the original plan?** (stages, scope, estimated effort)
2. **What actually happened?** (stages completed, scope changes, actual effort)
3. **Where did plan ≠ reality?** (list every deviation)

### Step 2: Extract Lessons

For each deviation, classify:

| Category | Question | Example |
|---|---|---|
| **Estimation** | Did we underestimate complexity? | "Auth was Medium but should have been Large" |
| **Scope** | Did scope drift occur? How many times? | "3 scope expansions — task wasn't atomic" |
| **Tooling** | Did a tool or command behave unexpectedly? | "Build failed due to missing dependency" |
| **Pattern** | Did we discover a reusable pattern? | "All API routes need error middleware" |
| **Anti-pattern** | Did we do something we should never repeat? | "Edited shared config without checking consumers" |
| **Blocker** | What blocked progress? | "Waited on user for 2 hours for DB credentials" |

### Step 3: Write to JSON Knowledge Graph

- **Mistakes / Anti-patterns:** Append to `.memory/mistakes.json` (include error, cause, lesson, status="ACTIVE", category).
- **Patterns / Reusable Rules:** Append to `.memory/patterns.json` (include pattern, applies_to, prevention).

### Step 4: Check for Recurring Issues

Before finishing, scan previous entries in `mistakes.json`:

- **Same lesson appearing 2+ times?** → Escalate
- **Same file causing problems repeatedly?** → Flag
- **Same estimation error repeating?** → Adjust defaults

---

## Section 2: Moment Captures (if captures >= 1)

This section replaces the standalone `ill-synthesis` skill. It only runs if ILL captures exist.

### Check Prerequisites

```
Read .memory/ill/captures.md and .memory/ill/wins.md
Count entries. If 0 → skip this section, note in output.
If >= 1 → run the synthesis phases below.
```

**Threshold: captures >= 1** (NOT 3 — the old threshold of 3 was too high and meant most sessions skipped synthesis entirely).

### Synthesis Phases

1. **Gather**: Read all capture files. Extract entries with timestamps, tags, severity, descriptions.
2. **Group**: Group captures by ILL tag: [delegation], [prompt-quality], [scope-creep], [cache], [memory], [subagent], [protocol]
3. **Quantify**: For each group: sum time (minutes) and tokens (estimated). Calculate occurrence count.
4. **Generate**: Produce markdown synthesis with pattern → cost → fix structure per group.
5. **Promote**: For each pattern: evaluate if 3+ sessions across 2+ projects. If yes → flag for human approval.
6. **Archive**: Move processed captures to `.memory/ill/history/`. Retain wins permanently.

### Synthesis Output

Write to `.memory/ill/synthesis.md`:

```markdown
# ILL Synthesis — YYYY-MM-DD

## Summary
- **Total captures**: N
- **Patterns identified**: N
- **Time cost**: N min
- **Promotion candidates**: N

## Patterns

### [PATTERN] Pattern Name
**Occurrences**: N sessions across M projects
**Root cause**: [derived from captures]
**Fix**: [specific, actionable — agent can execute directly]
```

---

## Combined Output Format

```
⚡ RETROSPECTIVE & ILL SYNTHESIS COMPLETE
  Pipeline    : [summary]
  Deviations  : [N] found
  Lessons     : [N] captured (mistakes + patterns)
  ILL Captures: [N] found, [N] patterns synthesized
  Recurring   : [N] patterns flagged
  Written to  : .memory/mistakes.json, .memory/patterns.json, .memory/ill/synthesis.md
```

---

## Integration

- **Conductor** includes retrospective in canonical order for Complex/Ultrathink
- **memorybank** Phase 2 runs after retrospective (retrospective feeds into memory)
- **JSON Knowledge Graph** is enforced via `harness.py gate --phase pre-task` on the next boot

## Anti-Rationalization

| Rationalization | Why It's Wrong |
|---|---|
| "The pipeline went smoothly, nothing to capture" | Smooth pipelines have patterns worth replicating. Capture what went right. |
| "I'll remember this for next time" | You won't. You're stateless. Write it down. |
| "This lesson is obvious" | If it's obvious, writing it takes 10 seconds. If it's not, you just proved why it needs writing. |
| "JSON files are getting long" | Long = lots of lessons = system improving. Trim only if entries are truly obsolete. |
| "Not enough captures to synthesize" | Even 1 capture has signal. The old threshold of 3 was too high. |
| "ILL synthesis is separate from retrospective" | Merged. One close ritual, two sections. Less friction = more compliance. |
