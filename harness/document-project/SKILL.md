---
name: document-project
description: Use when documenting brownfield projects for AI context — comprehensive project documentation with scan modes
quick_ref:
  purpose: "Generate comprehensive project documentation enabling AI agents to work with existing codebases"
  trigger: "document project | generate project docs | project documentation | scan this codebase"
  modes: "initial_scan | full_rescan | deep_dive"
  produces: "CONTEXT.md (root), project overview, architecture doc, source tree, dev guide, deep-dives"
  enforce: "python enforce.py start --mode <mode> --level <level> [--agent]"
---

# Document Project

> **This is a PROTOCOL skill. Phase instructions come exclusively from `enforce.py` output — not from this file or any other doc.**

---

## ⛔ HARD RULES — Read before anything else

| Rule | What it means |
|------|---------------|
| **enforce.py is the ONLY instruction source** | Do NOT read `FULL_SCAN.md` or `DEEP_DIVE.md` for phase-by-phase instructions. Those are human reference docs. Your instructions come from `enforce.py` output only. |
| **Never skip a phase** | Do not call `enforce.py done phase_3` without first completing and passing phases 1 and 2. The enforcer blocks this, but attempting it wastes cycles. |
| **Never fake completion** | Do not call `enforce.py done <phase>` before you have actually written the required output file. The enforcer checks file existence, required sections, and placeholder patterns. |
| **Never edit state directly** | `.docs/.scan-state.json` is enforcer-owned. Writing to it manually breaks integrity checks and is detectable. |
| **Write-as-you-go** | Write each output file immediately after completing its phase. Do not accumulate context across phases. |
| **Retry on exit 1** | If `enforce.py done <phase>` exits 1, read the FAIL output, fix the specific issue, and retry. Do not proceed to the next phase. |
| **Exit 2 = protocol error** | If enforce.py exits 2, you called phases out of order or skipped a prerequisite. Re-read current state: `python enforce.py status` |

---

## How to Start

**Step 1 — Determine mode:**

| Situation | Mode |
|-----------|------|
| First time documenting this project | `initial_scan` |
| Project has changed since last scan | `full_rescan` |
| Need depth on one specific subsystem | `deep_dive` |

**Step 2 — Start the enforcer:**

```bash
# Standard
python enforce.py start --mode initial_scan --level deep

# In agent/automated context (no prompts, JSON output)
python enforce.py start --mode initial_scan --level deep --agent --force

# Deep dive
python enforce.py start --mode deep_dive --level exhaustive --area auth --agent --force
```

**Step 3 — Read the output. Do exactly what it says. Nothing else.**

The enforcer output contains your Phase 1 instructions. Complete that work, then call:

```bash
python enforce.py done phase_1
```

Read that output. It contains Phase 2 instructions if Phase 1 passed, or the exact failure reason if it didn't.

**Repeat until all phases pass, then:**

```bash
python enforce.py validate
python enforce.py anchor-check
```

---

## Output Files

```
project-root/
├── CONTEXT.md                   # AI agent entry point — ≤4,000 tokens (phase 6)
└── .docs/
    ├── project-overview.md      # Type, purpose, classified tech stack (phases 1-2)
    ├── architecture.md          # Patterns, data flow, key decisions (phase 3)
    ├── source-tree.md           # Annotated directory structure (phase 4)
    ├── dev-guide.md             # Setup, build, test, deploy, gotchas (phase 5)
    ├── deep-dives/              # Sections >1,000 tokens + deep_dive outputs
    │   └── <area>.md
    └── .scan-state.json         # Enforcer-owned — do not edit
```

---

## Newspaper Logic (MANDATORY for all output)

All output files MUST follow the Newspaper Logic format from `harness/NEWSPAPER_LOGIC.md`:

- **At scan time**: Read `.memory/insights.md` and `.memory/variables.json` to enrich context
- **At output time**: Enforce headline-first structure in every section
- **Maximum 3 key facts** per collapsed section
- **Cross-reference** instead of duplicate — use `See [Section Name]` links
- **No preamble** — start with the headline, not "In this section..."

Example output section:
```
## HEADLINE: Authentication uses anonymous proxy with UID resolution

> SUMMARY: PIN login creates anonymous Firebase sessions; getRealUserId() resolves to real UID in security rules.

<details>
<summary>Details</summary>

- Anonymous auth: `authService.ts:88-107`
- UID resolution: `firestore.rules` uses `getRealUserId()`
- Gotcha: All writes must pass `actualUserId || uid` — NOT bare `uid`
- Cross-reference: See [Security Rules section]

</details>
```

---

## Scan Levels

| Level | Scope | Use when |
|-------|-------|----------|
| `quick` | Config, README, entry points | Rapid onboarding |
| `deep` | + source dirs, key modules, tests | Standard documentation |
| `exhaustive` | + every source file | Migration, critical system docs |

---

## Exit Codes (enforce.py)

| Code | Meaning | Agent action |
|------|---------|-------------|
| `0` | Pass | Proceed to next phase |
| `1` | Validation failure | Fix specific issue, retry same phase |
| `2` | Protocol/sequence error | Run `enforce.py status`, correct order |
| `3` | Fatal/unexpected | Check environment, report error |

---

## Reference Docs (human use only)

These files describe *what* each phase does. They exist for human understanding and skill maintenance — not as action instructions for the agent.

- `FULL_SCAN.md` — Phase reference for `initial_scan` / `full_rescan`
- `DEEP_DIVE.md` — Phase reference for `deep_dive`
- `CHECKLIST.md` — What `enforce.py validate` checks

> **Agent: you have already read these by reading this sentence. Stop. Your instructions come from `enforce.py` output only.**
