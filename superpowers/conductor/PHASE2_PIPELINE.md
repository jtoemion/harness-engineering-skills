# Phase 2 — Pipeline Construction

## Canonical Skill Order

```
1.  memorybank Phase 1          ← always leads
2.  ultrathink-mode             ← if ULTRATHINK triggered
3.  brainstorming               ← before code if spec undefined
4.  writing-plans               ← after spec approved
5.  using-git-worktrees         ← before implementation
6.  architectural-impact        ← before cross-layer code
7.  test-driven-development     ← runs INSIDE implementation stages
8.  subagent-driven-development ← if parallel tasks
9.  frontend-avant-garde        ← after architecture exists
10. frontend-design             ← for distinctive UI execution
11. requesting-code-review      ← after implementation
12. verification-before-completion ← before declaring done
13. retrospective               ← after Complex/Ultrathink pipelines
14. finishing-a-development-branch ← closing branch
15. dev-journey-log             ← after file touches
16. memorybank Phase 2          ← always closes
```

**Notes:**
- `test-driven-development` runs *inside* implementation stages, not standalone
- `ultrathink-mode` modifies depth of subsequent analysis, not a replacement
- `scope-guard` runs *inline* during any implementation stage — not a separate stage

---

## Context Budget Rules

> **These rules exist to prevent context window overflow. Non-negotiable.**

```
1. Max 3 execution stages per session (memorybank bookends don't count)
2. Max 3 skill files loaded per session (don't re-read a skill already loaded)
3. If a pipeline has >3 execution stages → auto-split into sessions
4. Each stage has an estimated context cost:
   - Small: single-file edit, test run, config change
   - Medium: multi-file feature, refactor, new component
   - Large: cross-layer change, new system, major redesign
5. If 2+ Large stages exist in one pipeline → mandatory split
```

---

## Atomic Task Rules

> **Every task must be small, testable, and scope-locked.**

```
1. Every task touches ≤3 files. More files = split into separate tasks.
2. Every task has a verification step — a command, test, or observable output.
3. Every task is describable in 2 sentences. If not → split it.
4. Scope lock: once pipeline is approved, touching new files requires explicit pause + approval.
5. scope-guard fires automatically if a task drifts outside declared scope.
```