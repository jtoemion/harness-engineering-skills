# Boot Sequence (Detailed)

Run these steps in order BEFORE any response:

```
1. READ {SKILLS_ROOT}\harness\SKILL.md          ← harness index
2. READ {SKILLS_ROOT}\harness\MISTAKES.md       ← check past mistakes
   → SURFACE relevant mistakes before proceeding
   → If attempting same failed approach → STOP → ask user
3. READ {SKILLS_ROOT}\superpowers\skills\memorybank\SKILL.md
4. LOAD memory per memorybank Phase 1:
   a. Check .memory/ at project root
   b. If missing → check Obsidian mirror
   c. If both missing → COLD START
   d. Read all 5 canonical files:
      - .memory/projectbrief.md
      - .memory/activeContext.md
      - .memory/progress.md
      - .memory/techContext.md
      - .memory/systemPatterns.md
   e. LOAD VAULT_MISTAKES/ (all ACTIVE notes, filter status != RESOLVED)
   f. PROBE REST API (optional enhancement)
      curl -k -s https://127.0.0.1:27124/ -H "Authorization: Bearer $OBSIDIAN_REST_KEY"
      IF 200 → ENHANCED MODE (rest_api=true)
      IF timeout → FILE-ONLY MODE (rest_api=false)
   g. CHECK 00_Memory/.session-close-staging/ (atomic close recovery)
      IF exists → WARN: incomplete session close, offer RESUME or DISCARD
5. LOAD GLOBAL_VAULT (cross-project)
   a. {GLOBAL_VAULT}/00_Global/Mistakes/ (matching category)
   b. {GLOBAL_VAULT}/00_Global/Patterns/ (matching stack)
6. READ {SKILLS_ROOT}\superpowers\skills\karpathy-guidelines\SKILL.md
7. OUTPUT Boot Status Report
```

## Boot Status Report
```
⚡ ONLINE
  Agent   : Antigravity [tool]
  Time    : [YYYY-MM-DD HH:MM]
  Mode    : FULL
  Memory  : [WARM | PARTIAL: missing X | COLD START]
  Harness : [LOADED ✓]
  Pattern : COMMANDER (Plan → Subagent → Review)
  Mistakes: [N] relevant found
  Project : [from projectbrief.md]
  Task    : [from activeContext.md]
  Next    : [from progress.md]
  Skills  : CORE ✓ | MEMORY ✓ | KARPATHY ✓ | HARNESS ARMED ✓
  Rules   : MAIN=PLAN ONLY | SUBAGENTS=EXPLORE/BUILD/REVIEW
```

## Cold Start Detection

If `.memory/` does not exist:
→ See `COLD_START.md` for full procedure