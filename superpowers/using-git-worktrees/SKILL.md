---
name: using-git-worktrees
description: Use when starting feature work that needs isolation - creates isolated git worktrees.
quick_ref:
  directory_priority: ".worktrees > CLAUDE.md > ask user"
  verify_ignored: "git check-ignore before creating project-local worktree"
  auto_setup: "Detect package.json/Cargo.toml/etc and install"
  verify_baseline: "Run tests before declaring ready"
---

# Using Git Worktrees

**Core principle:** Systematic directory selection + safety verification = reliable isolation.

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

## FILES

| File | Purpose |
|------|---------|
| `SKILL.md` | This index |
| `using-git-worktrees.yaml` | Quick reference |
| `DIRECTORY_SELECTION.md` | Priority-based directory finding |
| `CREATION_STEPS.md` | How to create + verify |
| `SETUP_AUTO_DETECT.md` | Auto-detect project setup |

---

## QUICK REF

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check CLAUDE.md → Ask user |
| Directory not ignored | Add to .gitignore + commit |
| Tests fail during baseline | Report failures + ask |

---

## INTEGRATION

**Called by:**
- brainstorming (Phase 4) - REQUIRED when design approved
- subagent-driven-development - REQUIRED before tasks
- executing-plans - REQUIRED before tasks

**Pairs with:**
- finishing-a-development-branch - REQUIRED for cleanup

---

## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Skip ignore check" | Worktree contents get tracked, pollute git |
| "Proceed with failing tests" | Can't distinguish new bugs from pre-existing |
| "Assume directory location" | Creates inconsistency, violates conventions |