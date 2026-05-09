# Phase 2: Group

Group captures by ILL tag to identify recurring patterns.

## Tag Categories

| Tag | Signals |
|-----|---------|
| `[delegation]` | Subagent brief issues, wrong subagent type, context blowup |
| `[prompt-quality]` | Unclear requirements, missing context, wrong scope in prompt |
| `[scope-creep]` | Task expanded beyond original, unexpected scope changes |
| `[cache]` | Repeated work, missed context reuse, no caching strategy |
| `[memory]` | Forgot to update memory, stale memory, missing memory writes |
| `[subagent]` | Subagent execution failures, wrong output format, communication breakdown |
| `[protocol]` | Missed steps, skipped validations, wrong workflow |

## Grouping Rules

1. Each capture has one **primary tag** (the most relevant category)
2. Captures may have multiple tags — group by primary only for pattern analysis
3. Wins are grouped separately — they represent what worked, not what failed

## Output

```json
{
  "groups": {
    "delegation": [entry, entry, ...],
    "prompt-quality": [...],
    "scope-creep": [...],
    "cache": [...],
    "memory": [...],
    "subagent": [...],
    "protocol": [...]
  },
  "wins": [win_entry, ...]
}
```

## Next Phase

Pass groups + wins to Phase 3 (Quantify).