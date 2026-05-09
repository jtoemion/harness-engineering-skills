# Phase 1: Gather

Read all ILL input files and extract entries with full metadata.

## Inputs

| File | Location | Content |
|------|----------|---------|
| `captures.md` | `.memory/ill/` | Project-level inefficiency captures |
| `wins.md` | `.memory/ill/` | Project-level efficiency wins |
| `captures.md` | `.global/ill/` | Cross-project captures |

## Extraction

For each capture entry, extract:
- **Timestamp**: When captured (YYYY-MM-DD HH:MM)
- **Type**: `inefficiency:` or `efficiency win:`
- **Description**: What happened (free text)
- **Tags**: One or more: [delegation], [prompt-quality], [scope-creep], [cache], [memory], [subagent], [protocol]
- **Severity**: `FRICTION` (minor) or `BLOCKER` (major)

## Output

Build a unified list of all entries with structure:

```json
{
  "entries": [
    {
      "source": "project" | "global",
      "type": "capture" | "win",
      "timestamp": "YYYY-MM-DD HH:MM",
      "description": "...",
      "tags": ["delegation"],
      "severity": "FRICTION"
    }
  ]
}
```

## Validation

- If fewer than 3 captures exist → STOP, report "Need 3+ captures"
- If no captures at all → STOP, report "No captures to synthesize"
- Wins are informational only — no minimum required

## Next Phase

Pass unified entry list to Phase 2 (Group).