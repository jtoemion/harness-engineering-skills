# PROJECT CONTEXT

> Universal agent enforcement ecosystem that transforms documentation into live gates. Python state machine + NLI pattern watcher catch agent protocol violations. Public GitHub: jtoemion/harness-engineering-skills.
> HARD RULE: Routing is keyword-first via skill-router.yaml — NLI is only a secondary watcher, never the primary router.
> HARD RULE: State transitions are validated by Pydantic and never written to disk if invalid.

## Critical constraints

| Constraint | What it means | Don't do this |
|------------|---------------|---------------|
| skill-router.yaml paths are Windows-specific | `skills_root: "C:\\Users\\jtoem\\...` — personal paths | Use as-is on non-Windows or non-AntiGravity setups |
| AGENTS.md is gitignored | Contains personal local paths and secrets | Commit AGENTS.md |
| conductor.py/bridge.py import mismatch | conductor.py imports `classify_with_qwen`, but bridge.py exports `WatchBridge` | Expect LLM-assisted routing to work — it falls back to YAML |
| harness.py imports `QwenBridge` | bridge.py now has `WatchBridge` | Expect bridge to warm up on boot — it silently fails |
| .memory/ controls mode | `.memory/` in project root = FULL mode, absence = QUICK | Need FULL mode but forgot `.memory/` |
| Session close is mandatory in FULL mode | pre-commit hook blocks if state != CLOSED | Skip close and try to commit |
| No Python dependency lock file | pip install pydantic pyyaml required manually | Expect `pip install` or `requirements.txt` |
|conductor.py reads `ROUTES` key from skill-router.yaml | But skill-router.yaml uses `routing:` key | Rename either key — routing breaks |

## tech stack

**Core runtime**
- Python 3.10+ (runtime enforcement)
- Pydantic v2 (state validation)
- PyYAML (skill routing config parsing)

**Flow-watcher (NLI pattern watcher)**
- Node.js 18+ (runtime)
- @huggingface/transformers ^4.2.0 (ONNX NLI classifier)
- Xenova/nli-deberta-v3-base (zero-shot classification model, ~250MB, downloads on first use)

**Configuration**
- YAML (skill-router.yaml, SKILLS.yaml, harness.yaml, document-project.yaml)
- Markdown (documentation, skill files)

**Testing / verification**
- Python (test scripts, post_final.py, post_v3.py, etc.)
- Playwright (browser-agent automation)
- Chrome DevTools Protocol (browser-backend)

**Inactive**
- @xenova/transformers ^2.17.1 (package listed but superseded by @huggingface/transformers)
- Chrome CDP (browser-agent backend, configured but not actively wired)
- Docker (mentioned in INFRASTRUCTURE.md but not actively used)

## Entry points

| Topic | Most specific doc |
|-------|------------------|
| Full architecture | [.docs/architecture.md](.docs/architecture.md) |
| Directory tree | [.docs/source-tree.md](.docs/source-tree.md) |
| Setup and gotchas | [.docs/dev-guide.md](.docs/dev-guide.md#running) |
| Project overview | [.docs/project-overview.md](.docs/project-overview.md) |
| Flow-watcher patterns | [README.md](README.md) |
| Routing config | [skill-router.yaml](skill-router.yaml) |
| Installation guide | [INSTALL.md](INSTALL.md) |

## Layer reference

```
Agent prompt
     ↓
skill-router.yaml (keyword routing)  +  flow-watcher.js (NLI pattern watcher)
     ↓                                           ↓
conductor.py (YAML engine)              bridge.py (subprocess)
     ↓                                           ↓
  skill .md files                    nli-deberta-v3-base (Transformers.js ONNX)
                                                    ↓
                                           12 watch patterns → WARN/PASS
harness.py (master CLI: boot, gate, checkpoint, close, mistakes, status)
     ↓
state.py (Pydantic model, atomic JSON writes)
     ↓
.harness-state.json (gitignored)
```

## Live commands

```bash
python harness/runtime/harness.py boot                    # Initialize session (FULL)
python harness/runtime/harness.py gate --phase pre-task --input "..."
python harness/runtime/harness.py verify-done
python harness/runtime/harness.py checkpoint --task "..."
python harness/runtime/harness.py close
python harness/runtime/harness.py close --resume
python harness/runtime/harness.py status
python harness/runtime/harness.py mistakes list
```