# Cold Start Procedure

Trigger: Vault structure does not exist locally or in Obsidian.

## Steps

```
1. ANNOUNCE: "⚡ COLD START — no vault found. Initializing."
2. CHECK {SKILLS_ROOT}\harness\MISTAKES.md for project hints
3. CHECK global vault (if available):
   a. Probe {ANTIGRAVITY_GLOBAL_VAULT}/00_Global/ for related projects
   b. IF found similar project → copy relevant patterns/mistakes
4. CHECK Obsidian mirror (legacy):
   a. Look for 00_HUMAN/02_Projects/[PROJECT]/Memory/
   b. IF found → recover from Obsidian
   c. IF not found → proceed to init
5. ASK user (one at a time):
   a. "Project name and one-sentence description?"
   b. "Project code? (2-3 uppercase letters, e.g. FW, BMW)"
   c. "Tech stack? (frontend, backend, database)"
   d. "Current priority — what should we work on first?"
6. CREATE vault directory structure:
   - 00_Memory/
   - 01_Sessions/
   - 02_Mistakes/
   - 03_Patterns/
   - 04_Index/
   - 05_Templates/
7. COPY templates from {SKILLS_ROOT}\harness\MEMORY_TEMPLATE\:
   - T-projectbrief.md → 00_Memory/projectbrief.md
   - T-activeContext.md → 00_Memory/activeContext.md
   - T-progress.md → 00_Memory/progress.md
   - T-techContext.md → 00_Memory/techContext.md
   - T-systemPatterns.md → 00_Memory/systemPatterns.md
   - T-session.md → 05_Templates/
   - T-mistake.md → 05_Templates/
   - T-pattern.md → 05_Templates/
   - T-decision.md → 05_Templates/
   - T-dashboard.md → 04_Index/Dashboard.md
8. POPULATE templates with user-provided data:
   - projectbrief.md: name, description, project_code, priority
   - activeContext.md: current task
   - progress.md: first task as `[ ] [task from user]`
   - techContext.md: tech stack details
   - systemPatterns.md: architecture stub
9. CREATE 00_Memory/SESSIONS.md (sessions-index stub)
10. SYNC to global vault (if available):
    - Add project entry to {ANTIGRAVITY_GLOBAL_VAULT}/02_Index/Projects.md
11. RE-RUN Phase 1 Boot
12. OUTPUT Boot Status Report
```

## Vault Directory Structure

```
{PROJECT_ROOT}/
├── 00_Memory/
│   ├── projectbrief.md
│   ├── activeContext.md
│   ├── progress.md
│   ├── techContext.md
│   ├── systemPatterns.md
│   └── SESSIONS.md
├── 01_Sessions/
├── 02_Mistakes/
├── 03_Patterns/
├── 04_Index/
│   └── Dashboard.md
├── 05_Templates/
│   ├── T-session.md
│   ├── T-mistake.md
│   ├── T-pattern.md
│   └── T-decision.md
└── .obsidian/
```

## Template Field Mapping

| Template | User Input | Fields to Fill |
|----------|-----------|----------------|
| `T-projectbrief.md` | name, description, code, priority | project, project_code, description, status, priority |
| `T-activeContext.md` | current task | task, blockers, last_agent |
| `T-progress.md` | first task | total, completed, first task item |
| `T-techContext.md` | tech stack | frontend, backend, database, infra |
| `T-systemPatterns.md` | (stub) | architectural_style, conventions |

## Obsidian Mirror (Legacy)

Project: `00_Memory/` ↔ `00_HUMAN/02_Projects/[NAME]/Memory/` (legacy projects only)
Global: `02_Mistakes/` + `03_Patterns/` → `{ANTIGRAVITY_GLOBAL_VAULT}/00_Global/`