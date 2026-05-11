# Architecture

## lede

Agent enforcement ecosystem with three layers: Python CLI commands (harness.py), Python enforcement modules (state, routing, mistakes, memory), and a JavaScript NLI watcher subprocess (flow-watcher.js). The flow-watcher is a secondary watcher — routing is handled by YAML keyword matching in skill-router.yaml, not by the NLI.

**Two hardest architectural rules:**
1. Routing must be deterministic and fast — keyword match first, NLI only as secondary watcher
2. State transitions are validated by Pydantic and never written to disk if invalid

## overview

See lede above.

## entry points

| Entry point | Language | Purpose |
|---|---|---|
| `harness/runtime/harness.py` | Python | Master CLI — routes all commands to submodules |
| `harness/runtime/state.py` | Python | Pydantic state model + atomic write |
| `harness/runtime/bridge.py` | Python | Subprocess bridge to Node.js flow-watcher |
| `harness/document-project/enforce.py` | Python | Phase enforcer for project documentation |
| `harness/runtime/flow-watcher/flow-watcher.js` | JavaScript | NLI pattern watcher via Transformers.js |

## data flow

**Routing flow (primary):**
```
user input → conductor.route() → skill-router.yaml keyword match → skill .md
                                              ↓
                               If FULL mode required but QUICK → BLOCK
```

**Watcher flow (secondary):**
```
user input → WatchBridge.watch() → flow-watcher.js → nli-deberta-v3-base
                                         ↓
                          12 watch patterns (multi_label: true)
                          confidence ≥ 0.5 → alert → WARN gate
                          confidence < 0.5 → PASS gate
                          timeout 10s → keyword fallback in bridge.py
```

**Session lifecycle:**
```
boot (state=BOOTING→ACTIVE) → gate pre-task → task → checkpoint → gate pre-complete → close (state=ACTIVE→CLOSING→CLOSED)
```

## architectural patterns

**Layered pipeline** — each harness command is a discrete pipeline (12-step checkpoint, 13-step session close)

**State machine** — HarnessState uses Pydantic with transition validation. State persisted as JSON with atomic write (temp file + os.replace). Valid transitions: BOOTING→ACTIVE↔CHECKPOINTING↔CLOSING→CLOSED

**Subprocess bridge** — Python spawns Node.js as long-lived subprocess. JSON over stdin/stdout. Process survives between calls. Auto-restart on timeout.

**Keyword-first routing** — skill-router.yaml is source of truth. NLI is secondary watcher for harness violations.

## key modules

| Module | Responsibility |
|---|---|
| `state.py` | Pydantic model, mode detection, atomic file writes |
| `conductor.py` | YAML routing, auto-fire skills, disambiguation |
| `bridge.py` | Python↔Node.js subprocess, WatchBridge, keyword fallback |
| `flow-watcher.js` | NLI zero-shot classification against 12 watch patterns |
| `mistakes.py` | Auto-load MISTAKES.md, check relevant entries at pre-task gate |
| `memory_watch.py` | Check .memory/ staleness, schema validation |
| `checkpoint.py` | 12-step checkpoint pipeline (subprocess from harness.py) |
| `session_close.py` | 13-step session close pipeline (resumable) |
| `hooks/install_hooks.py` | Installs pre-commit hook blocking commits if session not closed |

## error handling

- **State file corruption**: read_state() wraps in try/except, falls back to empty dict
- **Bridge timeout (10s)**: WatchBridge._read_response falls back to keyword matching in bridge.py
- **NLI import error**: classify_with_qwen = None in conductor.py, falls back to YAML
- **Invalid state transition**: raises InvalidTransitionError — never written to disk
- **enforce.py integrity check**: .scan-state.json has SHA256 hash, tampering detected

## authentication

Not applicable — no user authentication. This is a local tool running in the agent's own environment.

## architectural decisions

1. **Keyword routing over NLI for primary routing** — skill-router.yaml provides fast, deterministic, zero-dependency routing. NLI added as secondary watcher only.

2. **Subprocess over in-process LLM** — Node.js process lives separately from Python. Can be swapped or killed independently. No Python LLM dependency.

3. **Transformers.js over Ollama** — User constraint: no Ollama. Transformers.js runs ONNX models in-browser/Node without GPU requirements.

4. **Pydantic v2 over dataclasses** — Type validation on state transitions prevents invalid states from being persisted.

5. **Atomic JSON writes** — All state writes go through tempfile + os.replace to prevent corruption on crash.

6. **12-step pipeline over single call** — Checkpoint and session close broken into discrete steps with state persistence. Each step is individually resumable.

7. **nli-deberta-v3-base over smaller models** — Upgraded from xsmall (90MB) to base (250MB) after testing showed confidence of 0.99 vs 0.56 for correct classification with 3 skills.

8. **Import mismatch between conductor.py and bridge.py** — conductor.py imports `classify_with_qwen` but bridge.py no longer exports it (renamed to WatchBridge.watch()). Caught by ImportError in conductor.py → falls back to YAML routing. harness.py imports `QwenBridge` but bridge.py now has `WatchBridge` → import failure caught silently, bridge not started. Resolved by graceful fallback.

## section anchors

Required anchors: #overview #entry-points #data-flow #architectural-patterns #key-modules #error-handling #authentication #architectural-decisions