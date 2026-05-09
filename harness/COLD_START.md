# Cold Start Procedure

Trigger: `.memory/` and vault structure do not exist locally or in Obsidian.

## Steps

```
1. ANNOUNCE: "⚡ COLD START — no memory state found"
2. CHECK {SKILLS_ROOT}\harness\MISTAKES.md for project hints
3. CHECK Obsidian mirror:
   a. Look for 00_HUMAN/02_Projects/[PROJECT]/Memory/
   b. IF found → recover from Obsidian
   c. IF not found → proceed to init
4. ASK user (one at a time):
   a. "Project name and one-sentence description?"
   b. "Tech stack? (frontend, backend, database)"
   c. "Current priority — what should we work on first?"
5. CREATE project vault structure:
   00_Memory/projectbrief.md (from MEMORY_TEMPLATE/T-projectbrief.md)
   00_Memory/activeContext.md (from MEMORY_TEMPLATE/T-activeContext.md)
   00_Memory/progress.md (from MEMORY_TEMPLATE/T-progress.md)
   00_Memory/techContext.md (from MEMORY_TEMPLATE/T-techContext.md)
   00_Memory/systemPatterns.md (from MEMORY_TEMPLATE/T-systemPatterns.md)
   00_Memory/SESSIONS.md (stub with type: sessions-index)
   01_Sessions/ (empty directory)
   02_Mistakes/ (empty directory)
   03_Patterns/ (empty directory)
   04_Index/Dashboard.md (from MEMORY_TEMPLATE/T-dashboard.md)
   05_Templates/ (copy from harness/MEMORY_TEMPLATE/)
   .obsidian/ (copy app.json + appearance.json)
   .gitignore (copy from harness/OBSIDIAN_GITIGNORE)
6. RE-RUN boot sequence
7. OUTPUT Boot Status Report
```

## Vault Directory Structure

| Directory | Purpose |
|-----------|---------|
| `00_Memory/` | Canonical memory files (projectbrief, activeContext, progress, techContext, systemPatterns, SESSIONS) |
| `01_Sessions/` | Individual session notes |
| `02_Mistakes/` | Individual mistake notes |
| `03_Patterns/` | Individual pattern notes |
| `04_Index/` | Dashboard and index notes |
| `05_Templates/` | Note templates (copied from harness/MEMORY_TEMPLATE/) |
| `.obsidian/` | Obsidian config (app.json + appearance.json) |

## Obsidian Mirror

Project: `.memory/` → `00_Memory/` inside project vault
Global: `{GLOBAL_VAULT}/` for cross-project knowledge