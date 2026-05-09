---
name: dev-journey-log
description: >
  Maintains two living documents after every code change — DEVELOPMENT_JOURNEY.md (an append-only
  changelog of every modification made to the codebase) and FEATURE_MAP.md (a user interaction
  and hierarchy map showing how users move through the app and what happens at each step, e.g.
  "User clicks button → API is called → result rendered"). Use this skill every time any file is
  touched, any feature is added or removed, any route/component/schema/config/dependency changes.
  Trigger keywords: feature, fix, refactor, update, add, remove, route, component, button, form,
  endpoint, schema, config, dependency, page, screen, modal, flow, user can, user sees, user clicks,
  deploy, migrate, integrate.
---

# Development Journey Log

Every time you make a change to the codebase, you must update **three files**:

| File | Purpose | How it's written |
|------|---------|-----------------|
| `DEVELOPMENT_JOURNEY.md` | What changed and when — the audit trail | Append-only. Never edit past entries. |
| `FEATURE_MAP.md` | How users interact with the app — the living map | Edited in-place. Always reflects current state. |
| `.memory/SESSIONS.md` | Chronological session audit for cross-tool sync | Append-only. Mirrored to Obsidian. |

---

## File 3 — .memory/SESSIONS.md

A chronological log for agent-to-agent synchronization (Antigravity <-> opencode <-> Claude Code).

### If the file doesn't exist yet, create it with this header:

```markdown
# Session Log

> Chronological log of agent sessions. Used for synchronization between local tools and Claude Code (web).

---
```

### Then add an entry at the BOTTOM, using this format:

```markdown
### [YYYY-MM-DD HH:mm] — [Agent Name]
**Intent:** [Brief description of user request]
**Outcome:** [Brief description of what was achieved]
**Files Changed:** [Comma-separated list]
**Git Commit:** [Hash or "N/A"]
---
```

---

## File 1 — DEVELOPMENT_JOURNEY.md

An append-only changelog. Think of it like a commit history written in plain English.

### If the file doesn't exist yet, create it with this header:

```markdown
# Development Journey

> Append-only log of every meaningful change to this project.
> Never edit or delete past entries — only append. Newest entries go at the top.

---

## Changelog
```

### Then add an entry at the TOP of the Changelog, using this format:

```markdown
### [YYYY-MM-DD] — <Short descriptive title>

**Type:** feature | fix | refactor | config | dependency | schema | removal | docs
**Status:** completed | in-progress | reverted
**Files Changed:**
- `path/to/file.ext` — one line describing what changed in this file and why

**Summary:**
2–4 plain-English sentences. What was built or changed, why, and what problem it solves.

**Impact:**
Which parts of the app are now affected. Write BREAKING: in caps if something existing breaks.

**Trace:**
Link to a related past entry if this builds on or reverts one. Write N/A if standalone.

---
```

### Rules
- One entry per task. If multiple unrelated things changed, write one entry per change.
- Always list every file individually — never write "various files".
- Never go back and edit a past entry. If something was wrong, write a new `fix` entry.

---

## File 2 — FEATURE_MAP.md

A living map of every user-facing feature. Organized by page or module, then by feature, showing exactly what a user does and what the system does in response.

### If the file doesn't exist yet, create it with this header:

```markdown
# Feature Map

> Living map of every user-facing feature and interaction flow.
> Updated in-place whenever features change. Mark removed features [REMOVED] — never delete them.

---
```

### Then add or update a Feature Block using this format:

```markdown
## [Page or Module Name]
> One sentence describing what this section of the app does.
> Route: `/path` | Component: `FileName.jsx`

### [Feature Name]
> One sentence describing what this feature does.

**Component Hierarchy:**
- [Page] `PageName`
  - [Component] `ComponentName`
    - [Element] Button / Form / Input / Modal / Link / etc.

**Interaction Flow:**
```
User → does something
     → [system validates / calls / renders / redirects]
          ✓ success path → outcome
          ✗ failure path → outcome
```

**Connected To:**
- API: `METHOD /endpoint` — what it does
- State: what gets read or written
- Side Effects: redirects, toasts, emails, events fired

**Added:** YYYY-MM-DD | **Updated:** YYYY-MM-DD | **Status:** active | in-progress | [REMOVED]

---
```

### Flow Notation Guide

| Symbol | Meaning |
|--------|---------|
| `User →` | User takes an action (click, type, submit) |
| `→` | System moves to the next step |
| `↓ (if X)` | A conditional branch |
| `[validates]` | System checks something |
| `[calls]` | An API or function is invoked |
| `[renders]` | The UI updates |
| `[redirects]` | The user is sent to another page |
| `[emits]` | An event or side effect fires |
| `✓` | The success / happy path |
| `✗` | The error / failure path |

### Rules
- **Update in-place** — find the existing block and edit it. Don't add a duplicate.
- **Never delete a feature block.** If removed, set `Status: [REMOVED]` and add a removal date.
- **Add new pages/modules** as top-level `##` sections.
- **Backend-only changes** with no user-facing impact: note "No user-facing interaction" in the block.

---

## Workflow — Run After Every Change

1. **List** every file you modified, added, or deleted.
2. **Append** a new entry to the top of `DEVELOPMENT_JOURNEY.md`.
3. **Update** the relevant feature block(s) in `FEATURE_MAP.md` (or add new ones).
4. **End your reply** with a short confirmation like:
   > 📋 Journey logged: `[2025-06-10] — Add Login Route`
   > 🗺️ Feature map updated: `Authentication > Login`

---

## Reference Examples

For complete, realistic examples of both output files, read:
- `examples/DEVELOPMENT_JOURNEY.example.md`
- `examples/FEATURE_MAP.example.md`
