# Integration Guide

This document explains how to integrate **Harness Engineering Skills** into your agent configuration (`AGENTS.md` or equivalent).

---

## What is Harness Engineering?

Harness Engineering transforms documented agent protocols into **live enforcement** — state machines, gates, and classifier verdicts that physically block the agent from bypassing rules.

It's **tool-agnostic**: works with OpenCode, Claude Code, Cursor, or any LLM-based agent.

---

## Quick Integration

Add this to your agent config file:

```markdown
## CONFIG
```
SKILLS_ROOT     = /path/to/harness-engineering-skills
MASTER_PROTOCOL = /path/to/AGENTS.md
SKILL_ROUTER    = /path/to/harness-engineering-skills/skill-router.yaml
DETECT_MODE     = /path/to/detect-mode.sh  # or .bat on Windows
```

---

## Required Additions to AGENTS.md

### 1. Harness Engineering Section

Add this section under **HARNESS ENGINEERING (FULL MODE ONLY)**:

```markdown
## HARNESS ENGINEERING (FULL MODE ONLY)

See `harness/SKILL.md` and `harness/runtime/harness.py`

### Live Commands
```
python harness.py boot                    # Initialize session (FULL mode)
python harness.py gate --phase pre-task --input "..."   # Pre-task gate
python harness.py gate --phase pre-complete              # Pre-complete gate
python harness.py verify-done            # Acknowledge verification
python harness.py checkpoint --task "..."   # 12-step checkpoint
python harness.py close                  # 12-step session close
python harness.py close --resume         # Resume interrupted close
python harness.py status                 # Boot Status Report
```

### State Machine
`BOOTING → ACTIVE ↔ CHECKPOINTING → CLOSING → CLOSED`
```

### 2. Skill Router Reference

Replace any hardcoded skill paths with the router:

```markdown
**CRITICAL: Never browse skill folders to find a skill.** Read `{SKILL_ROUTER}` first.
It contains every skill's trigger condition, weight, mode requirement, and disambiguation rules.
First match on condition wins. Use weight to resolve ties. Use disambiguation table for similar skills.
```

### 3. Two-Mode Boot Sequence

Update your FULL MODE boot to include runtime initialization:

```markdown
### FULL MODE (.memory/ exists)
Full harness — for project work.
```
1. READ {MASTER_PROTOCOL}
2. READ {SKILL_ROUTER}
3. READ {SKILLS_ROOT}\harness\SKILL.md
4. READ {SKILLS_ROOT}\harness\MISTAKES.md
4e. LOAD VAULT_MISTAKES/ (status != RESOLVED)
4f. RUN: python {SKILLS_ROOT}\harness\runtime\harness.py boot
5. OUTPUT Boot Status Report
```
```

---

## Environment Variables

Add these to your config:

| Variable | Purpose | Example |
|----------|---------|---------|
| `ANTIGRAVITY_GLOBAL_VAULT` | Cross-project vault | `/Obsidian/AntigravityV/` |
| `OBSIDIAN_REST_KEY` | Local API key (gitignored) | `(none by default)` |

---

## Anti-Rationalization Table

Add this to prevent common bypass attempts:

```markdown
## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "QUICK mode is for any question" | QUICK mode is for simple questions with no project context. |
| "Skip session close in FULL mode" | MANDATORY. No exceptions. |
| "Raw subagent files OK" | SUBAGENT_RESULT.md only. |
| "Skip checkpoint in FULL mode" | Every task needs checkpoint. |
| "Memory doesn't need update" | Stale memory = useless. Update every task. |
```

---

## Boot Status Report Format

Your agent should output this format after boot:

```
⚡ ONLINE
  Agent   : [Your agent name]
  Time    : [YYYY-MM-DD HH:MM]
  Mode    : [QUICK | FULL]
  Memory  : [N/A | WARM | PARTIAL: missing X | COLD START]
  Harness : [N/A | LOADED ✓]
  Mistakes: [N/A | N] relevant found
  Project : [from projectbrief.md or N/A]
  Task    : [from activeContext.md or N/A]
  Next    : [from progress.md or N/A]
```

---

## What the Harness Adds

| Without Harness | With Harness |
|-----------------|--------------|
| Skill routing via keyword match | Routing via YAML + Qwen classifier |
| Session close is optional | Session close is mandatory + resumable |
| Mistakes check is manual | Mistakes checked automatically at pre-task gate |
| Checkpoint is documentation | Checkpoint is a 12-step enforced pipeline |
| State stored in Markdown | State stored in Pydantic-validated JSON |
| Git commit without session close | pre-commit hook blocks if session open |

---

## Files You Need

| File | Location | Purpose |
|------|----------|---------|
| `harness/runtime/harness.py` | `SKILLS_ROOT/harness/runtime/` | Master CLI |
| `harness/runtime/state.py` | `SKILLS_ROOT/harness/runtime/` | State model |
| `harness/runtime/conductor.py` | `SKILLS_ROOT/harness/runtime/` | Routing engine |
| `skill-router.yaml` | `SKILLS_ROOT/` | All skill routes |
| `AGENTS.md` | Your agent root | Your config |

---

## Minimal Example

For a new agent, start with this minimal `AGENTS.md`:

```markdown
# AGENT CONFIG

## CONFIG
```
SKILLS_ROOT     = /path/to/harness-engineering-skills
MASTER_PROTOCOL = /path/to/AGENTS.md
SKILL_ROUTER    = /path/to/harness-engineering-skills/skill-router.yaml
DETECT_MODE     = /path/to/detect-mode.sh
```

---

## Skill Router (Single Source of Truth)

The `skill-router.yaml` contains every skill with:
- `id` — unique identifier
- `condition` — when to load (evaluated top-to-bottom, first match wins)
- `skill_path` — path to the skill
- `mode_required` — quick | full | both
- `weight` — priority when multiple matches
- `disambiguation` — rules for similar skills

**Never browse skill folders.** Route through `skill-router.yaml` only.

---

## Full Documentation

See the main [README.md](./README.md) for complete architecture diagrams and command reference.