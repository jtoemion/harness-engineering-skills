# Phase 3: Quantify

Calculate operational impact per group.

## Metrics

| Metric | How Calculated | Unit |
|--------|-----------------|------|
| **Time cost** | Sum of time estimates from captures | minutes |
| **Token cost** | Sum of token estimates from captures | tokens |
| **Occurrences** | Count of captures in group | sessions |
| **Projects** | Count of unique projects (from global captures) | projects |

## Time Estimation Heuristics

| Severity | Estimated Time |
|----------|----------------|
| `FRICTION` | 5-15 min |
| `BLOCKER` | 30-120 min |

## Token Estimation Heuristics

| Severity | Estimated Token Overspend |
|----------|---------------------------|
| `FRICTION` | 1,000-5,000 tokens |
| `BLOCKER` | 10,000-50,000 tokens |

## Calculation per Group

```json
{
  "delegation": {
    "count": 5,
    "time_min": 45,
    "tokens": 15000,
    "sessions": 3,
    "projects": 1
  }
}
```

## Next Phase

Pass quantified groups to Phase 4 (Generate).