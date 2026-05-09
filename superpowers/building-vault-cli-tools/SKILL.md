---
name: building-vault-cli-tools
description: Use when you need to build Python CLI tools that consume an Obsidian vault.
---

# Building Vault CLI Tools

## Overview

Turn a build spec into working Python CLI tools using a coding agent, then document runtime usage with a SKILL.md.

## Critical Requirements (Non-Negotiable)

### vault_utils.py — write_frontmatter is the most dangerous function

**Handle three distinct cases:**
1. File has frontmatter → preserve body
2. File has no frontmatter → create new frontmatter + body
3. File is empty → create frontmatter only

Test this function in isolation before anything else. Every other function depends on it being bulletproof.

### vault_utils.py — Registry lookup

- Build `{alias_lower: canonical}` flat dict once at load time
- Case-insensitive lookup at call time
- Missing registry → empty dict + warning, never crash

---

## vault-analyst.py Requirements

### audit — purely read-only, zero side effects

Audit functions return data structures only. Never call `write_frontmatter`. Never modify files. If audit touches anything it becomes untrustworthy as a diagnostic.

### Duplicate detection — similarity threshold

Duplicate candidates = same source + same date + 2+ overlapping entities. Normalize entity strings before comparing (strip brackets, lowercase, canonical form).

### threads — exclude trivially common entities

Entities appearing in >60% of files in the window are noise. Exclude them from co-occurrence analysis. Stoplist = signal quality.

### fix — transaction-like pattern

1. Read all files first
2. Compute all changes into `(path, old_fm, new_fm)` tuples
3. Either print (dry-run) or apply (live)

Print summary: "12 files modified, 3 skipped, 0 errors."

---

## vault-writer.py Requirements

### entity — auto-generated section boundary is sacred

- `<!-- auto-generated: do not edit below this line -->` is the overwrite boundary
- Everything below gets overwritten every run
- Everything above is untouched
- If marker doesn't exist, append it at end — never assume position

### digest — import score.py, don't reimplement

Import scoring from `score.py` directly. If import fails, abort with clear error. Reimplemented scoring diverges over time.

### story-arc — honest source table

For each source involved:
- Filed rumor_id file → "Yes (rumor YYYY-MM-DD)"
- Covered without rumor_id → "covered — no rumor filed"
- Didn't cover → don't appear in table

---

## Cross-Cutting Rules

### --json flag on ALL commands
```bash
python vault-analyst.py audit --json
python vault-analyst.py threads --json
python vault-analyst.py suggest --from audit.json
```
LLM parses JSON, never relays raw text to user.

### suggest command
Reads audit JSON, returns prioritized action list:
```json
{
  "suggestions": [
    {
      "priority": 1,
      "category": "data_quality|stale_data|human_required|opportunity",
      "finding": "12 wikilink mismatches",
      "action": "fix --dry-run",
      "impact": "high",
      "risk": "low|medium|high",
      "command": "python vault-analyst.py fix --dry-run"
    }
  ]
}
```

### Dry-run must be first-class
```python
changes = []  # list of (path, old_fm, new_fm) tuples
if dry_run:
    for c in changes: print(c)
else:
    apply_all(changes)
```

### Warn and skip, never raise

Pattern:
```python
changes = []  # list of (path, old_fm, new_fm) tuples
# compute all changes first
if dry_run:
    for c in changes: print(c)
else:
    apply_all(changes)
```

Never build write logic inline. Dry-run must be reliable and complete.

### Every file scan — dotfile exclusion

```python
if f.name.startswith("."):
    continue
```

Obsidian creates `.obsidian/` that breaks frontmatter parsing.

### Warn and skip, never raise

Malformed frontmatter, missing files, broken YAML → one-line warning + continue. Vault will always have dirty data. Crash on one bad file = worse than skipping it.

---

## Build Spec Template

```
## Tool Purpose
Two CLI tools for maintaining and generating content in the Obsidian vault.

## Shared Utilities (vault_utils.py)
- read_frontmatter(path) -> dict - YAML between ---, {} on failure
- write_frontmatter(path, fm, body=None) - PRESERVES body, handles 3 cases
- load_registry() -> dict - flat {alias_lower: canonical}, load once
- normalize_entity(raw_name, registry) -> [[canonical]] or None
- get_all_news_files() -> list[Path] - skip dotfiles
- get_entity_folder(entity_type) -> Path

## vault-analyst.py (READ-ONLY analysis + safe fixes)
- audit → read-only, returns data structures, ZERO writes
- fix [--dry-run] → transaction pattern, safe auto-fixes only
- threads [--min-mentions 3] [--days 90] → exclude >60% common entities
- heat [--days 30] [--top 20]
- story <id>
- retrospective [--source]

## vault-writer.py (Content generation)
- entity <name> [--dry-run] → auto-generated boundary sacred
- digest [--days 7] [--dry-run] → import score.py only
- story-arc <id> [--dry-run] → honest source table

## Technical Requirements
- Python 3.10+, pyyaml, pathlib
- VAULT_ROOT: C:/Users/jtoem/Assets/News/football/
- ALL write ops support --dry-run
- warn/skip on errors, never raise
- dotfile exclusion on all globs
```

## Generating the Code

```python
task(description="Build vault CLI tools", prompt="Build SPEC FROM FILE: C:\\Users\\jtoem\\Downloads\\prompt_vault.txt

Output three Python files in C:\\Users\\jtoem\\Assets\\News\\football\\
1. vault_utils.py - shared utilities per build spec
2. vault-analyst.py - audit (read-only), fix, threads, heat, story, retrospective
3. vault-writer.py - entity, digest, story-arc

CRITICAL REQUIREMENTS FROM SKILL:
- write_frontmatter handles 3 cases: has fm, no fm, empty
- audit is PURELY read-only, zero side effects
- fix uses transaction pattern: read all, compute changes, then write
- threads excludes entities in >60% of files
- dry-run is first-class: compute changes first, print OR apply
- digest MUST import score.py, not reimplement
- entity auto-generated boundary is sacred
- story-arc source table is honest (no rumor = don't list)
- dotfile exclusion on all globs
- warn/skip errors, never raise
"")
```

## Testing Commands

```bash
python vault-analyst.py audit
python vault-analyst.py fix --dry-run
python vault-analyst.py threads --min-mentions 3
python vault-analyst.py heat --days 30
python vault-analyst.py story <story_id>
python vault-analyst.py retrospective

python vault-writer.py entity <EntityName> --dry-run
python vault-writer.py digest --days 7 --dry-run
python vault-writer.py story-arc <story_id> --dry-run
```