# AGENTS.md — document-project skill constraints

> Paste this block into your GEMINI.md, CLAUDE.md, .cursorrules, or any agent harness
> config when activating the document-project skill. These rules are NON-NEGOTIABLE.

---

## document-project Protocol Rules

When the document-project skill is active, the following rules override all other behavior:

### HARD RULE 1 — enforce.py is the sole instruction source

You MUST call `python enforce.py start ...` before doing any documentation work.
You MUST get your phase instructions from `enforce.py` output — not from FULL_SCAN.md,
DEEP_DIVE.md, or any other file. Reading those files for instructions bypasses the
enforcement chain and produces unverified output.

### HARD RULE 2 — Sequential phases, no skipping

You MUST complete phases in order: phase_1 → phase_2 → phase_3 → phase_4 → phase_5 → phase_6.
You MUST NOT call `enforce.py done phase_N` unless all phases before N have passed.
The enforcer blocks out-of-order calls (exit 2), but attempting them wastes time.

### HARD RULE 3 — done means actually done

You MUST NOT call `enforce.py done <phase>` unless:
  a. The required output file exists on disk and is non-empty
  b. The required sections are present in that file
  c. The file contains no TODO, TBD, or placeholder content
  d. You have personally verified the above before calling done

Calling done before the work is complete will fail validation (exit 1) and require a fix-retry loop.

### HARD RULE 4 — Exit 1 means fix and retry

If `enforce.py done <phase>` exits with code 1:
  1. Read the FAIL lines in the output
  2. Fix exactly the reported issue in the output file
  3. Call `enforce.py done <phase>` again
  4. Do NOT proceed to the next phase until exit 0

### HARD RULE 5 — Never touch .scan-state.json

`.docs/.scan-state.json` is owned by the enforcer. You MUST NOT read it to infer
phase status (use `enforce.py status` instead). You MUST NOT write to it directly.
The enforcer detects state tampering via integrity hash.

### HARD RULE 6 — Write-as-you-go

You MUST write each phase's output file immediately upon completing that phase's work.
You MUST NOT batch output across multiple phases. Context window pressure is not an
excuse to skip this rule — reduce scan depth instead.

### HARD RULE 7 — agent flag in automated context

If you are running in a non-interactive context (subagent, orchestrated pipeline, CI):
You MUST pass `--agent` to all enforce.py calls. This disables stdin prompts and
enables JSON output that your orchestrator can parse.

---

## Compliance verification (for orchestrators)

After each agent invocation, verify compliance by checking:

```bash
python enforce.py status --agent
```

Parse the JSON output. If `current_phase` has not advanced from before the agent ran,
the agent did not call `enforce.py done`. Re-invoke with the following injection:

```
COMPLIANCE FAILURE: You completed work but did not call enforce.py done <phase>.
This is required. Call it now before doing anything else:
  python enforce.py done <current_phase> --agent
```

---

## Quick reference for common harnesses

### OpenCode (AGENTS.md / skill system)
```markdown
## document-project skill
Active protocol. The skill tool must be invoked before any documentation work:
  Skill: document-project

When active:
- NEVER proceed to next phase without calling `python enforce.py done <phase> --agent`
- NEVER read FULL_SCAN.md for instructions — instructions come from enforce.py output only
- If enforce.py exits 1: fix the reported issue, retry the same phase
- If enforce.py exits 2: run `enforce.py status --agent` to diagnose
- State file integrity is verified via hash — do not edit .docs/.scan-state.json directly
```

### Gemini CLI (GEMINI.md)
```markdown
## document-project constraints
See AGENTS.md for full rules. Summary:
- NEVER proceed to next phase without calling `python enforce.py done <phase>`
- NEVER read FULL_SCAN.md for instructions — instructions come from enforce.py output only
- If enforce.py exits 1: fix the reported issue, retry the same phase
- If enforce.py exits 2: run `enforce.py status --agent` to diagnose
```

### Claude Code (CLAUDE.md)
```markdown
## document-project skill
Active protocol. enforce.py is mandatory at every phase boundary.
Read SKILL.md before starting. Never skip phases. Never call done before work is verified.
```

### Cursor / Windsurf (.cursorrules)
```
# document-project: enforce.py must be called after every phase
# FULL_SCAN.md is reference-only — get instructions from enforce.py output
# exit 1 = fix and retry | exit 2 = check enforce.py status
```
