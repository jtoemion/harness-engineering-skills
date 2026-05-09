# Atomic Session Close

## Problem

Session close has up to 12 steps. If the agent fails mid-close (e.g. step 5 of 12), half the vault graph is written and half is missing. This creates corrupt state — some notes reference [[links]] to notes that don't exist, frontmatter is inconsistent, and the next boot may load partial data.

## Solution: Write-to-Temp-then-Move

All session close writes go to a staging directory first. Only after validation are they moved atomically to their final vault locations.

## Staging Pattern

### Directory Structure

```
00_Memory/.session-close-staging/
├── 00_Memory/
│   ├── activeContext.md      (updated)
│   ├── progress.md            (updated)
│   ├── SESSIONS.md            (updated)
│   └── systemPatterns.md      (updated, if changed)
├── 01_Sessions/
│   └── YYYY-MM-DD-slug.md     (new)
├── 02_Mistakes/
│   └── CODE-M###-slug.md      (new, if any)
├── 03_Patterns/
│   └── CODE-P###-slug.md      (new or updated, if any)
├── 04_Index/
│   └── Dashboard.md           (updated)
└── 00_Global/                  (for sync to global vault only)
    ├── Mistakes/
    └── Patterns/
```

### Steps

1. **CREATE** staging directory: `00_Memory/.session-close-staging/`
2. **WRITE** all new/updated notes to staging directory (not to vault locations yet):
   - Session note → `.session-close-staging/01_Sessions/`
   - Mistake notes → `.session-close-staging/02_Mistakes/`
   - Pattern notes → `.session-close-staging/03_Patterns/`
   - Updated activeContext → `.session-close-staging/00_Memory/`
   - Updated progress → `.session-close-staging/00_Memory/`
   - Updated SESSIONS → `.session-close-staging/00_Memory/`
   - Updated Dashboard → `.session-close-staging/04_Index/`
3. **VALIDATE** all staged notes:
   - Every file has valid YAML frontmatter (parseable, required fields present)
   - All `[[_links]]` reference files that exist in the vault OR are being created in this staging batch
   - No malformed IDs (format: `{CODE}-{TYPE}###-{slug}`)
   - No duplicate IDs within the staging batch
4. **MOVE** staged files to vault locations (atomic per file):
   - Copy each file from staging to its final vault location
   - Overwrite existing files (activeContext, progress, etc.)
   - Create new files (session note, mistake notes, etc.)
5. **SYNC** to global vault (project → global):
   - Copy cross-cutting mistakes to `{ANTIGRAVITY_GLOBAL_VAULT}/00_Global/Mistakes/`
   - Create/update patterns in `{ANTIGRAVITY_GLOBAL_VAULT}/00_Global/Patterns/`
   - Update `{ANTIGRAVITY_GLOBAL_VAULT}/02_Index/Projects.md`
6. **CLEANUP**: `rm -rf .session-close-staging/`
7. **GIT COMMIT** (if in repo):
   ```
   git add 00_Memory/ 01_Sessions/ 02_Mistakes/ 03_Patterns/ 04_Index/
   git commit -m "chore: session close YYYY-MM-DD HH:MM"
   ```

### Validation Rules

| Check | Method |
|-------|--------|
| YAML parseable | Parse frontmatter with YAML parser, verify no syntax errors |
| Required fields | Each type has required fields (see VAULT_SCHEMA.md frontmatter table) |
| Link integrity | For each `[[link]]`, check that target file exists in vault OR staging |
| ID format | Regex: `^[A-Z]{2,3}-[MPD]\d{3}-[a-z0-9-]+$` |
| ID uniqueness | No duplicate IDs within staging batch |
| Status values | Mistake status: ACTIVE, RESOLVED. Decision status: active, superseded, deprecated |
| Outcome values | Session outcome: SUCCESS, PARTIAL, BLOCKED, FAILED |

## Recovery

If `.session-close-staging/` exists at boot, the previous session close was interrupted.

### Detection

During boot, after loading vault:

```
IF exists 00_Memory/.session-close-staging/:
  WARN: "Incomplete session close detected"
  OFFER options:
    1. RESUME: Validate staged files, complete close from step 4
    2. DISCARD: Delete staging directory, continue boot
    3. INSPECT: Show staged files for manual review
```

### Resume Close

If user chooses RESUME:

1. VALIDATE all staged notes (same rules as step 3 above)
2. If validation passes: continue from step 4 (move)
3. If validation fails: show errors, offer to fix or discard

### Discard Close

If user chooses DISCARD:

1. `rm -rf 00_Memory/.session-close-staging/`
2. Continue normal boot

## Agent Instructions

When performing session close, the agent MUST:

1. Always use the staging directory pattern — never write directly to vault locations during close
2. Always validate before moving
3. Always clean up the staging directory after successful move
4. Always check for staging directory at boot (recovery)

### What NOT to Do

| Anti-Pattern | Why |
|-------------|-----|
| Write directly to vault locations during close | If interrupted, partial state corrupts vault |
| Skip validation | Malformed frontmatter or broken links corrupt the graph |
| Leave staging directory after successful close | Next boot will incorrectly detect incomplete close |
| Skip cleanup step | Same as above |