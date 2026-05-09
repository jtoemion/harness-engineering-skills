# Phase 1 — Intent Analysis

**BEFORE anything else. Do not write code. Do not load skills yet.**

## Steps

```
1. Read full request without acting on it
2. Identify PRIMARY INTENT and SECONDARY CONCERNS
3. Check for ULTRATHINK keyword → flag for prepend
4. Classify against Intent Matrix
5. Assign Complexity Tier
6. If ambiguous → ask exactly ONE clarifying question, then re-analyze
```

## Intent Matrix

| Signal | Antigravity Skill | Superpowers Skill |
|--------|-------------------|-------------------|
| Vague idea, undefined requirements | — | `brainstorming` |
| Approved spec needs a plan | — | `writing-plans` |
| Plan ready, "Go" | — | `executing-plans` |
| New feature, schema, API, cross-layer | `architectural-impact` | `writing-plans` + `test-driven-development` |
| UI, component, layout, styling | `frontend-avant-garde` / `frontend-design` | `test-driven-development` |
| Bug, regression, not working | — | `systematic-debugging` + `verification-before-completion` |
| Multiple independent sub-tasks | — | `subagent-driven-development` |
| Before merge / PR | — | `requesting-code-review` |
| Feedback received on code | — | `receiving-code-review` |
| New or risky branch | — | `using-git-worktrees` |
| Branch complete | — | `finishing-a-development-branch` |
| Session start | `memorybank` Phase 1 | — |
| Task complete | `memorybank` Phase 2 | — |
| Any file touched | — | `dev-journey-log` |
| ULTRATHINK keyword | `ultrathink-mode` (prepend) | — |
| Multi-concern or complex | `conductor` (this file) | builds full pipeline |

## Complexity Tiers

| Tier | Definition | Conductor Behavior |
|------|------------|-------------------|
| **Simple** | Single concern, 1–2 skills | Skip pipeline, announce skill, execute directly |
| **Moderate** | 2–3 skills, clear sequence | Build pipeline, present for approval |
| **Complex** | 4+ skills or multi-layer | Full pipeline with **mandatory session splitting** |
| **Ultrathink** | ULTRATHINK + any concern | Prepend ultrathink-mode, present for approval |