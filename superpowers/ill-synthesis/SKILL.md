---
name: ill-synthesis
description: "Use when: user says 'synthesize' with 3+ captures logged, OR at session close when captures >= 3. Transforms raw ILL captures into structured pattern analysis with actionable fixes."
quick_ref:
  trigger: "'synthesize' command OR session close with captures >= 3"
  phases: "Gather → Group → Quantify → Generate → Promote → Archive"
  inputs: ".memory/ill/captures.md, .global/ill/captures.md, .memory/ill/wins.md"
  outputs: ".memory/ill/synthesis.md + global vault copy"
---

# ILL Synthesis

Transforms raw ILL captures into structured pattern analysis with quantified costs and actionable fixes.

**Trigger:** `synthesize` command (3+ captures) OR session close (captures >= 3)

**Core principle:** Patterns are worthless without cost quantification and concrete fixes. Generate documents that agents can actually use.

---

## When to Use

| Condition | Action |
|-----------|--------|
| User says "synthesize" | Run full 6-phase synthesis |
| Session close with captures >= 3 | Prompt: "N captures since last synthesis — run synthesis?" |
| Fewer than 3 captures | Acknowledge: "Need 3+ captures to synthesize. Current: N" |

---

## Inputs

```
.memory/ill/captures.md     # Project-level captures (inefficiency: / efficiency win:)
.global/ill/captures.md     # Cross-project captures
.memory/ill/wins.md         # Project wins (inform prevention)
```

---

## Outputs

```
.memory/ill/synthesis.md                    # Project synthesis (overwrites with latest)
{GLOBAL_VAULT}/00_Global/Synthesis/        # Global vault path from env or default
  └── synthesis-[YYYY-MM-DD].md             # Global archive (append-only)
.memory/ill/history/
  └── captures-[YYYY-MM-DD].md             # Project captures archived
.global/ill/history/
  └── captures-[YYYY-MM-DD].md            # Global captures archived (Phase 6)
.memory/ill/wins.md                         # Retained permanently (never archived)
```

---

## Phases

### Phase 1: Gather
Read all input files. Extract entries with timestamps, tags, severity, descriptions.

### Phase 2: Group
Group captures by ILL tag: [delegation], [prompt-quality], [scope-creep], [cache], [memory], [subagent], [protocol]

### Phase 3: Quantify
For each group: sum time (minutes) and tokens (estimated). Calculate occurrence count.

### Phase 4: Generate
Produce markdown synthesis with pattern → cost → fix structure per group.

### Phase 5: Promote
For each pattern: evaluate if 3+ sessions across 2+ projects. If yes → flag for human approval.

### Phase 6: Archive
Move processed captures to history. Retain wins permanently.

---

## Synthesis Document Structure

```markdown
# ILL Synthesis — YYYY-MM-DD

## Summary
- **Total captures**: N
- **Patterns identified**: N
- **Total time cost**: N min
- **Total token cost**: N tokens
- **Promotion candidates**: N

## Patterns

### [PATTERN] Pattern Name

**Occurrences**: N sessions across M projects
**Time cost**: N min
**Token cost**: N tokens
**Root cause**: [derived from captures]
**Fix**: [specific, actionable — agent can execute directly]

---

## Promotion Candidates

| Pattern | Sessions | Projects | Status |
|---------|----------|----------|--------|
| [pattern] | N | M | FLAG: needs approval |
```

---

## Quick Reference

| Tag | Description |
|-----|-------------|
| [delegation] | Subagent routing, brief issues |
| [prompt-quality] | Unclear requirements, missing context |
| [scope-creep] | Task expansion beyond scope |
| [cache] | Repeated work, missed context reuse |
| [memory] | Memory management failures |
| [subagent] | Subagent execution issues |
| [protocol] | Protocol violations, missed steps |

---

## Common Mistakes

| What goes wrong | Prevention |
|-----------------|------------|
| Synthesizing fewer than 3 captures | Check count before running |
| Forgetting wins in analysis | Wins inform prevention strategy |
| Auto-flagging promotion without judgment | Agent must assess if pattern truly generalizes |
| Overwriting without archiving | Archive captures before generating new synthesis |
| Writing only to project, missing global | Always write to both locations |

---

## Phase Files

- `PHASES/01_gather.md` — Input reading and extraction
- `PHASES/02_group.md` — Tag-based grouping
- `PHASES/03_quantify.md` — Time and token aggregation
- `PHASES/04_generate.md` — Synthesis document generation
- `PHASES/05_promote.md` — Promotion evaluation with full agent judgment
- `PHASES/06_archive.md` — Cleanup and history management