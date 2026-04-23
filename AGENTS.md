# ⚡ ANTIGRAVITY — UNIVERSAL AGENT CONFIG
# Tool-agnostic. Works for OpenCode, Claude Code, Cursor, and others.

## CONFIG
```
SKILLS_ROOT     = C:\Users\jtoem\.config\opencode\skills
MASTER_PROTOCOL = C:\Users\jtoem\.config\opencode\AGENTS.md
SKILL_ROUTER    = C:\Users\jtoem\.config\opencode\skills\skill-router.yaml
DETECT_MODE     = C:\Users\jtoem\.config\opencode\skills\detect-mode.bat (Win) / detect-mode.sh (Unix)
```

---

## SKILL ROUTING

**CRITICAL: Never browse skill folders to find a skill.** Read `{SKILL_ROUTER}` first.
It contains every skill's trigger condition, weight, mode requirement, and disambiguation rules.
First match on condition wins. Use weight to resolve ties. Use disambiguation table for similar skills.

---

## TWO-MODE SYSTEM

Detect mode by running `{DETECT_MODE}` from project root, or checking for `.memory/` directory.

### QUICK MODE (no .memory/ exists)
Fast, minimal boot — for simple questions.
```
1. READ {MASTER_PROTOCOL}
2. READ {SKILL_ROUTER}
3. READ {SKILLS_ROOT}\karpathy-guidelines\SKILL.md
4. ANSWER
```

### FULL MODE (.memory/ exists)
Full harness — for project work.
```
1. READ {MASTER_PROTOCOL}
2. READ {SKILL_ROUTER}
3. READ {SKILLS_ROOT}\harness\SKILL.md
4. READ {SKILLS_ROOT}\harness\MISTAKES.md
4e. LOAD VAULT_MISTAKES/ (status != RESOLVED)
4f. PROBE REST API (enhanced vs file-only mode)
4g. CHECK .session-close-staging/ (atomic close recovery)
5. READ {SKILLS_ROOT}\superpowers\memorybank\SKILL.md
6. LOAD .memory/ per memorybank Phase 1
7. READ {SKILLS_ROOT}\karpathy-guidelines\SKILL.md
8. LOAD GLOBAL_VAULT (cross-project mistakes, patterns)
9. OUTPUT Boot Status Report
```

---

## ENVIRONMENT VARIABLES

| Variable | Purpose | Default |
|----------|---------|---------|
| `ANTIGRAVITY_GLOBAL_VAULT` | Path to global Obsidian vault | `C:\Users\jtoem\Obsidian\AntigravityV\` |
| `OBSIDIAN_REST_KEY` | Local REST API key (gitignored) | (none) |

---

## BOOT STATUS REPORT

```
⚡ ONLINE
  Agent   : Antigravity [tool]
  Time    : [YYYY-MM-DD HH:MM]
  Mode    : [QUICK | FULL]
  Memory  : [N/A | WARM | PARTIAL: missing X | COLD START]
  Harness : [N/A | LOADED ✓]
  Mistakes: [N/A | N] relevant found
  Project : [from projectbrief.md or N/A]
  Task    : [from activeContext.md or N/A]
  Next    : [from progress.md or N/A]
```

---

## SKILL LIBRARY

Full path map: See `{SKILLS_ROOT}\SKILLS.yaml`

| Skill | Path |
|---|---|
| harness | `{SKILLS_ROOT}\harness\SKILL.md` |
| project-context | `{SKILLS_ROOT}\harness\project-context\SKILL.md` |
| e2e-scaffold | `{SKILLS_ROOT}\harness\e2e-scaffold\SKILL.md` |
| test-review | `{SKILLS_ROOT}\harness\test-review\SKILL.md` |
| workflow-builder | `{SKILLS_ROOT}\harness\workflow-builder\SKILL.md` |
| document-project | `{SKILLS_ROOT}\harness\document-project\SKILL.md` |
| karpathy-guidelines | `{SKILLS_ROOT}\karpathy-guidelines\SKILL.md` |
| browser-agent | `{SKILLS_ROOT}\browser-agent\SKILL.md` |
| memorybank | `{SKILLS_ROOT}\superpowers\memorybank\SKILL.md` |
| conductor | `{SKILLS_ROOT}\superpowers\conductor\SKILL.md` |
| subagent-driven-development | `{SKILLS_ROOT}\superpowers\subagent-driven-development\SKILL.md` |
| test-driven-development | `{SKILLS_ROOT}\superpowers\test-driven-development\SKILL.md` |
| systematic-debugging | `{SKILLS_ROOT}\superpowers\systematic-debugging\SKILL.md` |
| receiving-code-review | `{SKILLS_ROOT}\superpowers\receiving-code-review\SKILL.md` |
| using-git-worktrees | `{SKILLS_ROOT}\superpowers\using-git-worktrees\SKILL.md` |
| finishing-a-development-branch | `{SKILLS_ROOT}\superpowers\finishing-a-development-branch\SKILL.md` |
| verification-before-completion | `{SKILLS_ROOT}\superpowers\verification-before-completion\SKILL.md` |
| requesting-code-review | `{SKILLS_ROOT}\superpowers\requesting-code-review\SKILL.md` |
| brainstorming | `{SKILLS_ROOT}\superpowers\brainstorming\SKILL.md` |
| writing-plans | `{SKILLS_ROOT}\superpowers\writing-plans\SKILL.md` |
| executing-plans | `{SKILLS_ROOT}\superpowers\executing-plans\SKILL.md` |
| architectural-impact | `{SKILLS_ROOT}\superpowers\architectural-impact\SKILL.md` |
| frontend-avant-garde | `{SKILLS_ROOT}\superpowers\frontend-avant-garde\SKILL.md` |
| ultrathink-mode | `{SKILLS_ROOT}\superpowers\ultrathink-mode\SKILL.md` |
| dispatching-parallel-agents | `{SKILLS_ROOT}\superpowers\dispatching-parallel-agents\SKILL.md` |
| dev-journey-log | `{SKILLS_ROOT}\superpowers\dev-journey-log\SKILL.md` |
| scope-guard | `{SKILLS_ROOT}\superpowers\scope-guard\SKILL.md` |
| retrospective | `{SKILLS_ROOT}\superpowers\retrospective\SKILL.md` |
| using-superpowers | `{SKILLS_ROOT}\superpowers\using-superpowers\SKILL.md` |
| writing-skills | `{SKILLS_ROOT}\superpowers\writing-skills\SKILL.md` |
| vault-ops | `{SKILLS_ROOT}\superpowers\vault-ops\SKILL.md` |
| knowledge-graph | `{SKILLS_ROOT}\superpowers\knowledge-graph\SKILL.md` |
| session-graph | `{SKILLS_ROOT}\superpowers\session-graph\SKILL.md` |

---

## HARNESS ENGINEERING (FULL MODE ONLY)

See `harness/SKILL.md`

### Mistakes Tracking
- Check `harness/MISTAKES.md` BEFORE writing code
- Surface: "Previously, X caused Y. This time I will..."
- If same failed approach → STOP → ask user
- Log failures to `harness/MISTAKES.md` after any failure

### Subagent Protocol
- Delegate if: 5+ files, 3+ files implementation, >2000 lines read
- CREATE `SUBAGENT_BRIEF.md` → dispatch → READ `SUBAGENT_RESULT.md` only
- See `harness/SUBAGENT_PROTOCOL.md`

### Session Close (FULL MODE — MANDATORY)
**Trigger:** "close session" or equivalent
- See `harness/SESSION_CLOSE.md`

---

## COLD START (FULL MODE)

Trigger: No `.memory/` exists and project work is requested.

1. Announce: "⚡ COLD START — initializing project memory"
2. Check Obsidian mirror
3. Ask user: project name, tech stack, priority
4. Create `.memory/` with 5 canonical files
5. Mirror to Obsidian
6. Re-run FULL boot

See `harness/COLD_START.md`

---

## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "QUICK mode is for any question" | QUICK mode is for simple questions with no project context. |
| "Skip session close in FULL mode" | MANDATORY. No exceptions. |
| "Raw subagent files OK" | SUBAGENT_RESULT.md only. |
| "Skip checkpoint in FULL mode" | Every task needs checkpoint. |
| "Memory doesn't need update" | Stale memory = useless. Update every task. |