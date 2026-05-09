# Phase 1 — Bootstrap (Session Start)

Execute in order:

```
1. READ {SKILLS_ROOT}\harness\SKILL.md
2. READ {SKILLS_ROOT}\harness\MISTAKES.md
3. READ {SKILLS_ROOT}\superpowers\skills\memorybank\SKILL.md  ← you are here
4. LOAD memory per steps below
5. READ {SKILLS_ROOT}\superpowers\skills\karpathy-guidelines\SKILL.md
6. OUTPUT Boot Status Report
```

## Memory Loading Steps

```
a. DETECT vault type:
   i.   Check for .obsidian/ at project root
        - If FOUND → this is an Obsidian vault project
        - If NOT FOUND → check for .memory/ (legacy mode)
   ii.  Check for ANTIGRAVITY_GLOBAL_VAULT env variable
        - If SET → probe global vault via REST API (if OBSIDIAN_REST_KEY available)
        - If NOT SET → global vault unavailable, local-only mode
b. CHECK for incomplete session close:
   i.   Look for 00_Memory/.session-close-staging/
   ii.  If FOUND → see harness/ATOMIC_CLOSE.md Recovery section
   iii. Offer RESUME / DISCARD / INSPECT
c. CHECK if vault exists:
   - If 00_Memory/ MISSING → step d
   - If 00_Memory/ EXISTS → step f
d. CHECK Obsidian Mirror:
   i.   Look for 00_HUMAN/02_Projects/[PROJECT]/Memory/ (legacy)
   ii.  IF found → recover from Obsidian
   iii. IF not found → step e
e. Execute COLD START → see COLD_START.md
f. READ all 5 canonical files from vault:
   - 00_Memory/projectbrief.md
   - 00_Memory/activeContext.md
   - 00_Memory/progress.md
   - 00_Memory/techContext.md
   - 00_Memory/systemPatterns.md
g. LOAD mistakes from 02_Mistakes/:
   - Filter: status != RESOLVED
   - Surface active mistakes relevant to current task
h. PROBE global vault (if REST API available):
   - Query {ANTIGRAVITY_GLOBAL_VAULT}/00_Global/Mistakes/ for cross-project patterns
   - Query {ANTIGRAVITY_GLOBAL_VAULT}/00_Global/Patterns/ for applicable patterns
i. Proceed to output Boot Status Report
```

## Boot Status Report

```
⚡ ONLINE
  Agent    : Antigravity [tool]
  Time     : [YYYY-MM-DD HH:MM]
  Vault    : [VAULT | LEGACY .memory/ | COLD START]
  Memory   : [LOADED | PARTIAL: missing X | COLD START]
  Harness  : [LOADED ✓]
  Mistakes : [N] active found
  Patterns : [N] global patterns loaded
  Project  : [from projectbrief.md]
  Task     : [from activeContext.md]
  Next     : [from progress.md]
  Skills   : CORE ✓ | MEMORY ✓ | KARPATHY ✓ | HARNESS ARMED ✓
```

## Cold Start

If vault structure does not exist → see `COLD_START.md`