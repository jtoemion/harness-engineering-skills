---
name: memorybank
description: Autonomous memory bank lifecycle. Full mode only — QUICK mode has no memory.
quick_ref:
  mode: "FULL MODE ONLY (QUICK mode has no memory)"
  boot: "Check vault structure → read 00_Memory/ + 02_Mistakes/ → Output Status Report"
  checkpoint: "Update 00_Memory/ files → create session/mistake/pattern notes → update Dashboard"
  session_close: '"close session" → ATOMIC_CLOSE.md staging → validate → move → git'
  cold_start: "No vault → check global vault → ask 3 questions → create vault from templates"
  ill: ".memory/ill/ captures → synthesize on-command → patterns → human approval"
---

# MEMORY BANK — FULL MODE ONLY

**QUICK MODE:** No memory. No checkpoint. Just answer.

**FULL MODE:** All phases active.

## VAULT STRUCTURE

```
{PROJECT_ROOT}/
├── 00_Memory/          # Core 5 files + SESSIONS.md
├── 01_Sessions/        # Individual session notes
├── 02_Mistakes/        # Individual mistake notes ({CODE}-M###-slug.md)
├── 03_Patterns/        # Individual pattern notes ({CODE}-P###-slug.md)
├── 04_Index/           # Dashboard.md + MOCs
├── 05_Templates/       # Note templates (T-*.md)
└── (no .obsidian/)    # Obsidian is OPTIONAL. Core system works with plain files only.
```

## FILES

| File | Purpose |
|------|---------|
| `SKILL.md` | This index |
| `memorybank.yaml` | Quick reference schema |
| `PHASE1_BOOT.md` | Bootstrap procedure |
| `PHASE2_CHECKPOINT.md` | Task completion checkpoint |
| `PHASE3_SUBCOMMAND.md` | Subagent result checkpointing |
| `SESSIONS_SCHEMA.md` | Session recording format |
| `COLD_START.md` | No-memory initialization |
| `ITERATIVE_LEARNING.md` | ILL protocol (captures, synthesis, promotion) |

---

## PHASES

### Boot (Phase 1)
See `PHASE1_BOOT.md`

### Checkpoint (Phase 2)
See `PHASE2_CHECKPOINT.md`

### Subagent Result (Phase 3)
See `PHASE3_SUBCOMMAND.md`

### Session Close
See `harness/ATOMIC_CLOSE.md` for the write-to-temp-then-move pattern.

### Graph Close (Phase 4)

At session close, memorybank creates linked knowledge notes:

1. **Session note**: Create a linked session note in `01_Sessions/`
2. **Mistake notes**: Create individual mistake notes in `02_Mistakes/` with `[[links]]`
3. **Pattern notes**: Create or update pattern notes in `03_Patterns/` with `[[links]]`
4. **Decision notes**: Create decision notes in `03_Patterns/` with `[[links]]`
5. **Dashboard update**: Update `04_Index/Dashboard.md` with new counts
6. **Validation**: Verify frontmatter, link integrity, ID uniqueness before committing

Use the atomic staging pattern from `harness/ATOMIC_CLOSE.md`:
- Write to `.session-close-staging/` first
- Validate all staged files
- Move to vault locations
- Cleanup staging directory

Note format: `{CODE}-M###-slug.md` for mistakes, `{CODE}-P###-slug.md` for patterns, `{CODE}-D###-slug.md` for decisions.

---



## ILL (Iterative Learning Layer)

- Location: `.memory/ill/` (project) | `.global/ill/` (global)
- Boot: ILL files auto-created if missing
- See: `harness/ITERATIVE_LEARNING.md` for full protocol

---

## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Memory applies in QUICK mode" | QUICK mode = no memory. |
| "Skip checkpoint" | Every task needs checkpoint in FULL mode. |
| "Skip session close" | MANDATORY in FULL mode. No exceptions. |
| "Write directly to vault during close" | Use ATOMIC_CLOSE.md staging pattern. |