# document-project — OpenCode Integration

## Overview

`document-project` is a protocol skill that generates comprehensive project documentation for AI agent context. It uses a mandatory enforcement chain to ensure agents follow a strict phased workflow.

## Quick Start

```
1. Skill: document-project
2. python enforce.py start --mode initial_scan --level deep --agent --force
3. python enforce.py done <phase> --agent  (repeat for phase_1 through phase_6)
4. python enforce.py validate
5. python enforce.py anchor-check
```

## Core Files

| File | Purpose |
|------|---------|
| `enforce.py` | Phase validator + state tracker + integrity hash |
| `conductor.py` | Orchestrator for multi-agent pipelines |
| `AGENTS.md` | Binding rules for any invoking agent |
| `SKILL.md` | Agent quick-ref (get instructions from enforce.py) |
| `FULL_SCAN.md` | Phase reference (human use) |

## Protocol (Mandatory)

### The Problem
Agents skip phases, fake completion, and read FULL_SCAN.md for instructions instead of following the enforcement chain. This produces undocumented or incomplete output.

### The Solution
`enforce.py` is the **sole instruction source**. It validates file content, phase order, and maintains an integrity hash on the state file. State tampering is detectable.

### Enforcement Chain

```
enforce.py start --mode <mode> --level <level> --agent --force
    ↓ creates .docs/.scan-state.json (phase_1, in_progress)

enforce.py done phase_1
    ↓ validates project-overview.md exists + required sections + no placeholders
    ↓ on fail: exit 1 (agent fixes, retries)
    ↓ on pass: marks phase_1 done, outputs phase_2 instructions

enforce.py done phase_2
    ↓ blocks if phase_1 not done first (required_previous check)
    ↓ ...
```

### Exit Codes

| Code | Meaning | Agent action |
|------|---------|-------------|
| `0` | Pass | Proceed to next phase |
| `1` | Validation failure | Fix issue, retry same phase |
| `2` | Protocol/sequence error | Run `enforce.py status` to diagnose |
| `3` | Fatal/unexpected | Check environment |

## Output Files

```
project-root/
├── CONTEXT.md                   # AI entry point — ≤4,000 tokens
└── .docs/
    ├── project-overview.md      # Type, purpose, classified tech stack
    ├── architecture.md          # Patterns, data flow, key decisions
    ├── source-tree.md           # Annotated directory structure
    ├── dev-guide.md            # Setup, build, test, deploy, gotchas
    ├── deep-dives/             # Sections >1,000 tokens
    └── .scan-state.json         # Enforcer-owned (hash-verified)
```

## Newspaper-Lede Output Format

All output files follow inverted-pyramid (newspaper) structure:

- **Ledé first**: First 3 lines tell the AI what it MUST know
- **Inverse pyramid**: Most critical info first, details deeper
- **Scannable tables**: Constraints, modules, gotchas in tables — not prose
- **Non-linear**: Each section independently actionable
- **Inline hard stuff**: Most-violated rules appear verbatim, not behind a link

Example ledé (CONTEXT.md):
```
> React 19 SPA student portal (Firestore-backed).
> HARD RULE: Components/Pages → Hooks → Services → DAL → Firestore. No layer skipping.
> HARD RULE: Students log in as Firebase Anonymous users proxied via sessions/{uid}.actualUserId.
```

## Hard Rules (for any invoking agent)

| Rule | What it means |
|------|---------------|
| **enforce.py is the ONLY instruction source** | Instructions come from `enforce.py` output, not FULL_SCAN.md |
| **Never skip a phase** | phase_1 → phase_2 → ... → phase_6. Enforcer blocks out-of-order |
| **Never fake completion** | File must exist + sections present + no placeholders before calling `done` |
| **Never edit state directly** | `.scan-state.json` is enforcer-owned with tamper detection |
| **Write-as-you-go** | Write each phase's output immediately. No batching. |
| **Retry on exit 1** | Fix the reported issue, retry the same phase. Do not advance. |
| **Exit 2 = protocol error** | Run `enforce.py status --agent` to diagnose |

## For Orchestrators

After each agent invocation, verify compliance:

```bash
python enforce.py status --agent
```

Parse JSON output. If `current_phase` has not advanced, the agent did not call `enforce.py done`. Re-invoke with:

```
COMPLIANCE FAILURE: You did not call enforce.py done <phase>.
Call it now before doing anything else.
```

## Skill Path

```
SKILLS_ROOT/harness/document-project/
├── enforce.py          # v2.0 — hash integrity, --agent mode, conductor-aware
├── conductor.py       # Orchestrator (monitor + orchestrate modes)
├── AGENTS.md           # Binding agent rules
├── SKILL.md            # Agent quick-ref
├── FULL_SCAN.md        # Phase reference (human)
├── DEEP_DIVE.md        # Deep dive reference (human)
├── CHECKLIST.md        # Validation checklist (human)
└── document-project.yaml
```
