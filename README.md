# ⚡ Harness Engineering Skills

**Universal agent enforcement ecosystem** — transforms documented protocols into live gates, state machines, and classifier verdicts.

> Every rule that currently lives in Markdown becomes a gate. The agent cannot proceed by ignoring the harness. The harness physically blocks it.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         AGENT BOOT                              │
│                                                                 │
│  python harness.py boot                                         │
│         ↓                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  1. Detect mode (QUICK vs FULL)                         │    │
│  │  2. Load skill-router.yaml → parse routes               │    │
│  │  3. Check .memory/ staleness (memory_watch.py)          │    │
│  │  4. Check relevant mistakes (mistakes.py)                │    │
│  │  5. Start Qwen bridge (flow-watcher.js)                 │    │
│  │  6. Boot Status Report printed                           │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PRE-TASK GATE                                 │
│                                                                 │
│  python harness.py gate --phase pre-task --input "..."          │
│         ↓                                                        │
│  1. Load + validate HarnessState (state.py)                    │
│  2. Check .memory/ staleness (memory_watch.py)                  │
│  3. Check MISTAKES.md for relevant entries (mistakes.py)        │
│  4. Mode guard check (conductor.py)                             │
│  5. Qwen route classification (flow-watcher.js via bridge.py)    │
│  6. YAML keyword fallback if confidence < 0.65                 │
│  7. Disambiguation if skills within 10 weight points           │
│  8. Print: skill path to load, any warnings                    │
│         ↓                                                        │
│  GATE = BLOCK → exit(1) | GATE = PASS → continue               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        TASK EXECUTION                            │
│                         (Agent works)                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       CHECKPOINT                                │
│                                                                 │
│  python harness.py checkpoint --task "..."                       │
│         ↓                                                        │
│  1. Transition state: ACTIVE → CHECKPOINTING                    │
│  2. Run 12-step pipeline (checkpoint.py):                       │
│     [1] update_active_context    [7] process_mistakes          │
│     [2] update_progress           [8] process_patterns           │
│     [3] update_tech_context*     [9] process_decisions          │
│     [4] update_system_patterns* [10] update_dashboard           │
│     [5] create_session_note      [11] sync_global              │
│     [6] append_sessions_log      [12] output_confirmation       │
│     (* conditional based on state flags)                       │
│  3. Transition state: CHECKPOINTING → ACTIVE                    │
│  4. Reset: verification_logged=False                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  PRE-COMPLETE GATE                               │
│                                                                 │
│  python harness.py gate --phase pre-complete                    │
│         ↓                                                        │
│  1. verification_logged must be TRUE (via verify-done)          │
│  2. checkpoint_complete must be TRUE                            │
│  Both required → PASS                                           │
│  Either missing → BLOCK with exact command to run              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     SESSION CLOSE                               │
│                                                                 │
│  python harness.py close                                         │
│  python harness.py close --resume  (after crash)               │
│         ↓                                                        │
│  1. ILL check: warn if ≥3 captures since last synthesis        │
│  2. Run 12-step pipeline (session_close.py):                   │
│     [0]  ill_check                                               │
│     [1]  create_staging                                         │
│     [2]  write_session                                          │
│     [3]  update_memory                                          │
│     [4]  write_mistakes                                         │
│     [5]  write_patterns                                         │
│     [6]  write_decisions                                        │
│     [7]  validate_staging (HARD GATE)                          │
│     [8]  atomic_move                                            │
│     [9]  sync_global                                            │
│     [10] update_dashboard                                       │
│     [11] git_commit (best-effort)                              │
│     [12] output_summary                                        │
│  3. Resumable: state.close_step persisted after each step       │
│  4. Transition state: CLOSING → CLOSED                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## State Machine

```
BOOTING → ACTIVE ↔ CHECKPOINTING → CLOSING → CLOSED
```

| State | Valid Transitions |
|-------|-----------------|
| `BOOTING` | `ACTIVE` |
| `ACTIVE` | `CHECKPOINTING`, `CLOSING` |
| `CHECKPOINTING` | `ACTIVE`, `CLOSING` |
| `CLOSING` | `CLOSED` |
| `CLOSED` | *(terminal)* |

Invalid transitions raise `InvalidTransitionError` — never written to disk.

---

## Directory Structure

```
harness/
├── runtime/                          # Live enforcement (Python + JS)
│   ├── state.py                      # Pydantic state model + transitions
│   ├── conductor.py                  # Routing engine (YAML + Qwen)
│   ├── bridge.py                     # Python ↔ Transformers.js subprocess
│   ├── mistakes.py                   # Auto read/write MISTAKES.md
│   ├── memory_watch.py               # .memory/ staleness + schema validator
│   ├── harness.py                    # Master CLI entry point
│   ├── checkpoint.py                 # 12-step checkpoint pipeline
│   ├── session_close.py             # 12-step session close (resumable)
│   ├── flow-watcher/                # Qwen2.5-0.5B overseer
│   │   ├── flow-watcher.js          # stdin/stdout JSON, two modes
│   │   ├── package.json
│   │   └── prompts/
│   │       ├── router.txt            # Routing classification prompt
│   │       └── validator.txt         # Flow sequence validation prompt
│   └── hooks/
│       ├── pre-commit                # Git hook: block if session open
│       └── install_hooks.py          # Hook installer
├── SKILL.md                          # Harness skill index
├── SESSION_CLOSE.md                  # Session close documentation
├── MISTAKES.md                       # Anti-repeat error log
├── SUBAGENT_PROTOCOL.md             # Subagent delegation rules
└── ...                               # Other harness documentation
```

---

## Live Commands

| Command | Purpose |
|---------|---------|
| `python harness.py boot` | Initialize session (FULL mode) |
| `python harness.py gate --phase pre-task --input "..."` | Pre-task gate |
| `python harness.py gate --phase pre-complete` | Pre-complete gate |
| `python harness.py verify-done` | Acknowledge verification complete |
| `python harness.py checkpoint --task "..."` | Run 12-step checkpoint |
| `python harness.py close` | Run 12-step session close |
| `python harness.py close --resume` | Resume interrupted close |
| `python harness.py status` | Print Boot Status Report |
| `python harness.py mistakes list` | List active mistakes |
| `python harness.py mistakes resolve "YYYY-MM-DD"` | Mark resolved |
| `python harness.py _hook-check-session` | (internal) Git hook check |

---

## Flow-Watcher (Qwen2.5-0.5B)

The only component that calls the LLM. Answers exactly two questions:

### `--route` Mode
```bash
node flow-watcher.js --route "there's a bug in the auth flow"
```
```json
{"skill_id": "systematic-debugging", "confidence": 0.72, "gate": "PASS", "reason": "bug encountered"}
```

### `--validate` Mode
```bash
node flow-watcher.js --validate '{"state":"ACTIVE","skills_loaded":["systematic-debugging"]}'
```
```json
{"valid": true, "sequence": "pre-task → skill → checkpoint → ...", "gate": "PASS"}
```

**Confidence threshold:** If `confidence < 0.65` → fall back to YAML keyword match (Python, no LLM).

---

## Boot Status Report

```
⚡ ONLINE
  Agent   : Antigravity [tool]
  Time    : 2026-05-09 20:15
  Mode    : FULL
  Memory  : WARM (activeContext.md: 12m ago)
  Harness : LOADED ✓
  Skills  : systematic-debugging, verification-before-completion
  Mistakes: 2 checked, 0 new
  ILL     : 4 captures (consider: synthesize)
  Gate    : mistakes_checked=✓  verification_logged=✗  checkpoint=✓
```

---

## Key Files

| File | Purpose |
|------|---------|
| `skill-router.yaml` | Single source of truth for routing decisions |
| `AGENTS.md` | Master protocol — mode detection, boot sequence |
| `harness/runtime/state.py` | Pydantic-validated state with atomic writes |
| `harness/runtime/harness.py` | All CLI commands in one entry point |
| `harness/MISTAKES.md` | Cross-project mistake tracking |

---

## Stack

| Layer | Technology |
|-------|------------|
| State contract | Python + Pydantic v2 |
| Gate CLI | Python (`harness.py`) |
| Intent + flow classifier | Qwen2.5-0.5B via Transformers.js |
| Python ↔ JS bridge | subprocess (stdin/stdout JSON) |
| Session close pipeline | Python state machine |
| Memory validation | Python file watcher |
| Git enforcement | pre-commit hook (Python) |

---

## Setup

```bash
# Install flow-watcher dependencies (downloads Qwen on first run)
cd harness/runtime/flow-watcher
npm install

# Install git hooks (optional, runs on boot too)
python harness/runtime/hooks/install_hooks.py

# Run boot
python harness/runtime/harness.py boot
```

---

## License

MIT — contribute freely.