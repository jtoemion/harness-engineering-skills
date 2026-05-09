# Phase 6: Archive

Clean up processed captures and maintain system hygiene.

## Archive Rules

| File Type | Action |
|-----------|--------|
| Processed captures | Move to `.memory/ill/history/captures-YYYY-MM-DD.md` |
| Wins | RETAIN permanently in `.memory/ill/wins.md` (never archive) |
| Previous synthesis | Overwrite (latest is always current) |

## Archive Process

1. Create `.memory/ill/history/` if not exists
2. Read current `.memory/ill/captures.md`
3. Write to `.memory/ill/history/captures-YYYY-MM-DD.md` with timestamp
4. Clear `.memory/ill/captures.md` (or archive and start fresh)

## Output Locations

```
.memory/ill/synthesis.md                    # Latest synthesis (overwrite)
.memory/ill/history/captures-YYYY-MM-DD.md  # Archived captures
.memory/ill/wins.md                         # Retained permanently
{GLOBAL_VAULT}/00_Global/Synthesis/
  └── synthesis-[YYYY-MM-DD].md             # Global archive (append-only)
.memory/ill/promotion-queue/               # Pending promotion notes (if any)
```

## Write Order

1. Write project synthesis `.memory/ill/synthesis.md`
2. Write global archive copy
3. Archive captures
4. Update wins if any new wins were captured (wins accumulate, never clear)

## Final Validation

Confirm:
- [ ] Synthesis written to `.memory/ill/synthesis.md`
- [ ] Synthesis copied to global vault
- [ ] Captures archived (source cleared)
- [ ] Wins retained (source intact)
- [ ] Promotion notes created if any flagged