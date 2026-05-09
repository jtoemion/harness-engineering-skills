# Iterative Learning Layer (ILL) Protocol

## Overview

Self-learning ecosystem built on harness infrastructure. Capture inefficiencies/wins during work. Synthesize on-command into actionable protocol changes.

## Two-Tier Scope

| Scope | Location | Purpose |
|-------|----------|---------|
| Global | `.global/ill/` | Harness-level patterns (cross-project) |
| Project | `.memory/ill/` | Project-specific captures |

## Tag Taxonomy

`[delegation]` `[prompt-quality]` `[scope-creep]` `[cache]` `[memory]` `[subagent]` `[protocol]`

## Severity

| Level | Meaning | Synthesis Weight |
|-------|---------|-----------------|
| `FRICTION` | Minor, recurring annoyance | Normal |
| `BLOCKER` | Session failure or major rework | 3x |

## Capture Format

**Inefficiency:**
```markdown
## [YYYY-MM-DD HH:MM] | [TAG] | [FRICTION | BLOCKER]
**Capture**: [What was inefficient]
**Context**: [Task/feature]
**Pattern**: [What it suggests]
**Project**: [Project or GLOBAL]
```

**Win:**
```markdown
## [YYYY-MM-DD HH:MM] | [TAG]
**Win**: [What worked well]
**Context**: [Task/feature]
**Pattern**: [What it reinforces]
**Project**: [Project or GLOBAL]
```

## Synthesis

**Trigger**: On-command via `synthesize` + nudge at SESSION_CLOSE

**Process:**
1. Load captures since last synthesis
2. Cluster by tag (3x in same project = candidate)
3. Cross-project check (2+ projects = global candidate)
4. Draft proposed changes to patterns.md
5. Report: "X patterns found, Y proposed changes ready"

## Promotion Mechanic

Project pattern (3x in Project A) → seen in 2+ projects → GLOBAL_PATTERN

Agent flags promotion opportunity. Human approves.

## Pattern Lifecycle

```
CAPTURE → PROJECT_PATTERN (3x) → GLOBAL_PATTERN (2+ projects)
       → APPROVED (human) → changelog.md → file updated
       → REJECTED (human) → archived
       → STALE (10 sessions inactive) → archived
```

## Decay

Pattern inactive 10+ sessions → marked STALE → archived (not deleted)

## Files

| File | Purpose |
|------|---------|
| `captures.md` | Raw inefficiency logs |
| `wins.md` | Efficiency wins |
| `patterns.md` | Synthesized patterns |
| `changelog.md` | Approved changes |