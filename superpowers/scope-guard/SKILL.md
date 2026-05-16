---
name: scope-guard
description: Detects and flags scope creep during implementation — fires automatically when a task is about to touch files outside its declared scope
compliance_rules:
  - "Task stays within its declared file scope"
  - "Any scope deviation is flagged before implementation continues"
  - "User approves scope changes before work continues on new files"
---

# Scope Guard

## Overview

Scope Guard is a lightweight inline check that runs during any implementation stage. It detects when a task is drifting outside its declared file scope and surfaces the deviation without blocking.

**This skill is NOT a pipeline stage.** It runs *inside* other stages, intercepting file operations.

## How It Works

### Before any file edit during an implementation stage:

1. **Check**: Is this file in the task's declared scope?
2. **If YES** → proceed, no output needed
3. **If NO** → surface immediately:

```
⚠ SCOPE DRIFT DETECTED
  Task scope : [declared files]
  Now touching: [new file]
  Options:
    A) Add to scope (confirm this file is in scope)
    B) Create new atomic task for this file
    C) Abort this edit
```

### Scope Expansion Tally

Track how many times scope has expanded in the current session:

- **1st expansion** → surface, allow with approval
- **2nd expansion** → surface with warning: "Scope has expanded twice. Consider splitting."
- **3rd expansion** → **force pause**: "3+ scope expansions. This task is no longer atomic. Split required."

## What Counts as Scope

Scope is defined at pipeline approval time (Conductor Phase 3):
- Each stage declares `Scope: [files]`
- Files listed = in scope
- Everything else = out of scope
- Adding a test file for an in-scope implementation file = always in scope (testing doesn't count as drift)

## Integration

- **Conductor** references scope-guard in its Atomic Task Rules
- **executing-plans** should check scope before each file edit
- **architectural-impact** should pre-declare all affected files as scope

## Anti-Rationalization

| Rationalization | Why It's Wrong |
|---|---|
| "It's just one more file" | That's how scope creep starts. Surface it. |
| "The test file is out of scope" | Test files for in-scope code are always in scope. |
| "I'll add it to scope myself" | Scope changes require user approval or explicit confirmation. |
| "This file is obviously needed" | If it was obvious, it should have been in the original scope. |
