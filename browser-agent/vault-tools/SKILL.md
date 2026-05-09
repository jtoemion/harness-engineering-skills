---
name: vault-tools
description: Use when user asks to analyze or generate content from Obsidian football news vault.
---

# vault-tools — Runtime SKILL.md

## Overview

Two CLI tools for the football news Obsidian vault. Tools return structured JSON so the LLM can **reason** about findings, not just relay text.

**Core principle:** LLM parses --json output → reasons → proposes actions → user decides

## Workflow Pattern

```
LLM → runs command --json → gets structured data → reasons about it → proposes actions → user decides
```

Never relay raw human-readable output to user directly.

## vault-analyst.py

| User says | Command | LLM Action |
|-----------|---------|------------|
| "audit the vault" | `audit --json` | Parse findings, call suggest |
| "fix wikilinks" | `fix --dry-run` | Show preview, confirm, run |
| "find red threads" | `threads --json` | Parse co-occurrence matrix |
| "what's hot" | `heat --json` | Parse entity frequency |
| "suggest actions" | `suggest --from audit.json` | Get prioritized action list |
| "show story arc" | `story <id>` | Reconstruct timeline |
| "rumor accuracy" | `retrospective --json` | Parse source performance |

## Adaptive Workflow (MANDATORY)

After any audit or analysis command, the LLM MUST:

1. **Parse --json output** — do not relay raw text
2. **Call suggest** to get prioritized action list
3. **Categorize findings:**
   - `fixable: true, risk: low` → offer to run now
   - `fixable: true, risk: medium` → show dry-run first
   - `fixable: false` → surface clearly as human_required
   - `category: opportunity` → propose as follow-up
4. **Present conversationally:**
   - BAD: "Here is the audit output: [wall of text]"
   - GOOD: "Found 44 files missing frontmatter fields that need your review, plus 1 auto-fixable duplicate. Want me to fix the duplicate first?"
5. **Track health_score** — report delta after fixes: "Health score improved from 87 → 92"

## Chain Rules

```
audit --json → suggest → (fix dry-run → confirm → fix) → audit again
threads --json → identify top unlinked pair → propose story-arc
heat --json → identify top entity → propose vault-writer entity
```

## Rules

1. **audit before fix** — always
2. **dry-run before write** — preview first, confirm, then write
3. **LLM parses JSON** — not raw text
4. **suggest generates proposals** — LLM presents conversationally
5. **health_score tracks progress** — report deltas

## vault-writer.py

| User says | Command |
|-----------|---------|
| "update entity" | `entity <name> --dry-run` |
| "generate digest" | `digest --days 7 --dry-run` |
| "compile story arc" | `story-arc <id> --dry-run` |

## Error Handling

- Missing registry → warn + continue with empty
- Malformed frontmatter → warn + skip
- score.py missing → abort with clear error
- BOM in JSON files → use utf-8-sig encoding