---
name: harness
description: Universal harness engineering. Mistake tracking, subagent routing, mandatory session close.
quick_ref:
  mode: "FULL MODE ONLY (QUICK mode has no harness)"
  boot: "harness SKILL → MISTAKES.md → memorybank → karpathy → Status"
  mistakes: "Check MISTAKES.md BEFORE code. Log failures AFTER."
  subagent: "CREATE SUBAGENT_BRIEF.md → dispatch → READ SUBAGENT_RESULT.md only"
  session_close: '"close session" → SESSION_CLOSE.md → mirror → git commit'
  commander: "MAIN=PLAN ONLY | SUBAGENTS=EXPLORE/BUILD/REVIEW | NEVER touch implementation files"
---

# HARNESS ENGINEERING — FULL MODE ONLY

**QUICK MODE:** No harness. No memory. Just answer.

**FULL MODE:** See files below.

## FILES

| File | Purpose |
|------|---------|
| `SKILL.md` | This index |
| `harness.yaml` | Quick reference schema |
| `BOOT_SEQUENCE.md` | Detailed boot procedure |
| `SUBAGENT_PROTOCOL.md` | Context blowup prevention |
| `SESSION_CLOSE.md` | Mandatory session close |
| `MISTAKES_TRACKING.md` | Anti-repeat error log |
| `COLD_START.md` | No-memory initialization |
| `MEMORY_LIFECYCLE.md` | Memory file schemas |
| `ATOMIC_CLOSE.md` | Atomic staging pattern for session close |
| `ITERATIVE_LEARNING.md` | Self-learning capture-and-synthesize protocol |
| `MEMORY_LIFECYCLE.md` | Memory file schemas and lifecycle |
| `COLD_START.md` | Cold start procedure for new projects |
| `project-context/SKILL.md` | Generate project-context.md (persistent AI rules) |

## RUNTIME (Live Enforcement)

The harness runtime implements live gates, state transitions, and classifier verdicts.
Every rule in these documents becomes a physical gate the agent cannot bypass.

**Location:** `skills/harness/runtime/`

| File | Purpose |
|------|---------|
| `harness.py` | Master CLI entry point — all commands route through here |
| `state.py` | Pydantic state model + transitions |
| `conductor.py` | Routing engine (YAML + Qwen) |
| `bridge.py` | Python ↔ Transformers.js subprocess bridge |
| `mistakes.py` | Auto read/write MISTAKES.md |
| `memory_watch.py` | .memory/ staleness + schema validator |
| `checkpoint.py` | 12-step checkpoint pipeline |
| `session_close.py` | 12-step session close state machine |
| `flow-watcher/` | Qwen2.5-0.5B overseer |
| `hooks/pre-commit` | Git hook: block commit if session open |

---

## QUICK REF

### Full Boot Sequence (in order)
```
1. READ {SKILLS_ROOT}\harness\SKILL.md
2. READ {SKILLS_ROOT}\harness\MISTAKES.md
3. READ {SKILLS_ROOT}\superpowers\skills\memorybank\SKILL.md
4. LOAD .memory/ per memorybank Phase 1
5. READ {SKILLS_ROOT}\superpowers\skills\karpathy-guidelines\SKILL.md
6. OUTPUT Boot Status Report
```

### Boot Status Report
```
⚡ ONLINE
  Agent   : Antigravity [tool]
  Time    : [YYYY-MM-DD HH:MM]
  Mode    : FULL
  Memory  : [WARM | PARTIAL: missing X | COLD START]
  Harness : [LOADED ✓]
  Mistakes: [N] relevant found
  Project : [from projectbrief.md]
  Task    : [from activeContext.md]
  Next    : [from progress.md]
```

---

## DELEGATION RULES — MANDATORY

**MAIN AGENT: PLAN ONLY. Never read implementation files.**

### Hard Constraints
| DO | DON'T |
|----|--------|
| Plan tasks | Read implementation files |
| Create SUBAGENT_BRIEF.md | Touch .ts/.js/.py files directly |
| Review SUBAGENT_RESULT.md | Read raw subagent work files |
| Manage memory | Implement anything |

### Always Delegate To Subagent
| Task | Subagent Type |
|------|---------------|
| Explore (read files, search) | `explore` |
| Build (write/edit code) | `build` |
| Review (verify, test, audit) | `review` |

**Exception:** Single-file reads under 50 lines for configuration only.

---

### Subagent Types
| Type | Role | Input | Output |
|------|------|-------|--------|
| `explore` | Research, read files, find patterns | Brief with file paths | SUBAGENT_RESULT.md |
| `build` | Implement, write code, edit files | Brief with specs | SUBAGENT_RESULT.md + files modified |
| `review` | Verify, test, audit, validate | Brief with criteria | SUBAGENT_RESULT.md |

---

### Commander Pattern Flow
```
USER INPUT
    ↓
MAIN AGENT (Plan only)
    ↓ Creates SUBAGENT_BRIEF.md
    ↓
┌────────────────────────────────────┐
│ explore subagent → finds context  │
│ build subagent → implements        │ (can run parallel)
│ review subagent → verifies         │
└────────────────────────────────────┘
    ↓
MAIN AGENT (compile results from SUBAGENT_RESULT.md only)
    ↓
PRESENT TO USER
```

---

## SESSION CLOSE TRIGGER

**"close session"** or equivalent → MANDATORY.

See `SESSION_CLOSE.md` for full procedure.

---

## ILL (Iterative Learning Layer)
- Capture: `inefficiency: [desc]` or `efficiency win: [desc]`
- Tags: [delegation] [prompt-quality] [scope-creep] [cache] [memory] [subagent] [protocol]
- Severity: FRICTION | BLOCKER
- Synthesize: On-command + nudge at SESSION_CLOSE
- Scope: .global/ill/ (global) | .memory/ill/ (project)

---

## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Harness applies in QUICK mode" | QUICK mode = no harness. That's the point. |
| "Skip session close" | MANDATORY in FULL mode. No exceptions. |
| "Raw subagent files OK" | SUBAGENT_RESULT.md only. Contract. |
| "Main agent can read files directly" | MUST dispatch explore subagent. Rule. |
| "Skip mistake check" | Check MISTAKES.md first — always. |
| "Subagent can return raw content" | REJECT — return summary only. |