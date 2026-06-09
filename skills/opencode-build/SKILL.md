---
name: opencode-build
description: "Use when building a feature or fixing a bug with strict atomic tasks, TDD loop, and subagent orchestration. Mirrors techne pipeline: IMPLEMENT gated, VERIFY, REVIEW, RETRO, EVAL. Always show status after every phase."
triggers:
  - build this
  - implement this
  - fix this bug
  - make this feature
  - atomic task
  - tdd loop
  - opencode build
---

# OpenCode Build

## Lead — One Rule

**PLAN first → Strict atomic task → TDD loop (RED→GREEN) → subagent per phase → `p.get_status()` after every phase.** No shortcuts. The subagent follows techne's implementer skill literally.

### Pre-Execution Gate (mandatory before any subagent dispatch)

Before running `opencode run`, produce and push:

1. **`PLAN-IMPLEMENTATION.md`** — atomic task list with one diff = one behavior per task, organized in phases. Each task must have: owner, atomic behavior, RED test description, and files to produce.
2. **Todo list** — `todo` tool with one item per task, linked to plan.
3. **Push to GitHub** — `gh api repos/jtoemion/.../contents/PLAN-IMPLEMENTATION.md --method PUT` (HTTPS, not SSH). Confirm the SHA in the response.

Only after (1)+(2)+(3) are done, proceed to subagent dispatch. This prevents running opencode on work that hasn't been scoped and committed.

## Pipeline Phases

```
ATOMIC TASK
    ↓
IMPLEMENT  ← subagent writes test (RED) → impl (GREEN)
VERIFY     ← subagent runs tests
REVIEW     ← subagent reviews diff
RETRO      ← subagent answers 7 questions
EVAL       ← status + eval preview shown
```

**After every phase: call `print(p.get_status())`.** Display checkpoint + eval preview.

## 8-Block Subagent Brief (mandatory)

Every subagent dispatch MUST use this structure:

```
IDENTITY   — name, role, model (opencode/minimax-m3-free)
ROLE       — what they own, what they don't
PERSONA    — dry, precise, no fluff
GOAL       — one sentence, LOCAL to this subagent
CONSTRAINTS — hard limits, specific, absolute
OUTPUT_FORMAT — exact structure
INTERACTION_MODE — self-correct? ask? silent?
GATE_AWARENESS — what this output must pass
```

## TDD Loop

```
RED  → write ONE failing test for ONE behavior
GREEN → minimal code to pass it
REPEAT → until all tests pass
```

Never write multiple tests before implementing. One cycle at a time.

## Atomic Task Rule

One task = one diff = one behavior. If the task is too large, decompose first. A task that takes more than 3 TDD cycles is too large.

## Meta Prompt Layer (mandatory — always runs first)

**Before any subagent dispatch: `opencode-build/meta-prompt.md`**

```
RAW TASK
    ↓
REFINE    → 8-block brief assembled ← MANDATORY
LOAD      → techne implementer + tdd skill loaded by opencode
MISTAKES  → grep mistakes.md
ROUTE     → which skill gates apply
COMPOSE   → final meta prompt sent to opencode CLI
```

Never send a raw task directly to opencode. The subagent must receive the 8-block brief + skill context + mistakes awareness + gate routing — all composed into the meta prompt.

**See: `opencode-build/meta-prompt.md`**

## Phase Execution

### IMPLEMENT — subagent "build"

```bash
opencode run --model opencode/minimax-m3-free --dir <project_path> "<8-block brief>"
```

**TDD enforcement (mandatory — do not skip):**

The subagent must complete these steps in order before marking IMPLEMENT done:

1. **Write RED test** — create one failing test asserting the new behavior
2. **Run test in isolation** — confirm it fails (red). Do not proceed to impl until test fails.
3. **Write GREEN impl** — minimal code to pass the test
4. **Run test again** — confirm it passes (green)
5. **Run full test file** — confirm no regressions on existing tests
6. **Self-check** — `git diff --unified=3`, `grep '@ts-ignore'`, `grep 'console.log'`

**Identity/RBAC field-completeness checklist** (run before writing impl when task involves identity, auth, or optional parameters on public functions):

```bash
# Audit which fields must be present for this feature to work
grep -n "studentIdentity\|userProfile\|authToken\|identity" src/ -r --include="*.ts" --include="*.tsx"
# For each call site: which fields of the identity object must be populated?
# If a field is missing (null/undefined), what does the output look like?
# Add a safe-default or validation if critical fields can be absent
```

**New-feature test requirement:** Any new parameter, optional or not, that changes function output MUST have at least one explicit test in the same PR. Do not rely on existing test suite coverage to "catch" the new behavior.

Brief includes:
- The atomic task
- Techne implementer rules (diff discipline, gate awareness)
- TDD rules (RED first, GREEN minimal)
- Self-check: `git diff --unified=3`, `grep '@ts-ignore'`, `grep 'console.log'`

### VERIFY — subagent "verify"

Runs test suite. Returns stdout. Must show real pass/fail indicators.

### REVIEW — subagent "review"

Reviews diff. Returns PASS / SOFT_FAIL / HARD_FAIL + findings.

### RETRO — subagent "retro"

Answers 7 retro questions. Returns proposals if any.

## Status Display (after every phase)

```python
print(p.get_status())
```

Output:
```
PIPELINE #N STATUS
PHASE RESULTS:  implement → PASS, verify → PASS, ...
CHECKPOINT:     gates passed/failed, verified YES/NO
EVAL PREVIEW:   5 dimensions scored, TOTAL, trend
```

### Subagent Timeout — Continue from Partial, Don't Re-Delegate

Subagent timeouts (600s limit) often happen AFTER files were written — the subagent was writing when the limit hit, not before it started.

**Decision tree on timeout:**
```
Files written + coherent state? → continue directly (don't re-delegate)
Files written + incoherent state? → discard, implement directly
Zero files written? → implement directly
```

**Why not re-delegate:** The subagent's isolated context is gone. It restarts from scratch with no memory of what it had already read or written. If files exist, the new subagent has no way to know what the timed-out one already did — it may duplicate work or conflict.

**Continue pattern:**
```bash
# 1. Check what landed
ls /path/to/expected/files/

# 2. If files exist — assess quality
head -5 /path/to/file
# If coherent (correct imports, valid syntax), continue from there

# 3. If incomplete — read what exists, finish the job directly
#    Then git add + commit as normal
```

**Real example (Phase 4b — products admin):**
- Subagent timed out at 600s
- `ls src/routes/products/new/` → `+page.svelte` EXISTS (written at 19:50, timeout at 19:52)
- Assessed: file was complete ✅
- Moved files to correct location (`src/routes/admin/products/`) to fix route conflict
- Continued to Phase 4c and 4a in parallel instead of re-delegating 4b

### Subagent Test Fix Pattern — Root-to-Leaf

For large test-fix tasks (10+ failing files with cascade pollution):

1. **Find root polluter first.** Run failing files in isolation to identify which passes alone but fails in suite:
   ```bash
   npx vitest run src/components/PolluterFile.test.tsx
   ```
   The first file that shows failures IN ISOLATION is the polluter. Fix it first.

2. **Fix root first, then cascade clears automatically.** Many downstream failures are cascade, not root causes.

3. **For each remaining isolated failure:** Apply the `afterEach` cleanup pattern from `test-driven-development` skill.

4. **Subagent iteration limit:** OpenCode subagents hit iteration limits on tasks with 10+ test files. For test-fix sprints, prefer direct agent (Megumi Kato) over subagent dispatch — the iterative diagnose→fix→verify loop benefits from full context continuity that subagent delegation loses after ~3 iterations.

### Dispatch Failure — `session_message.seq NOT NULL constraint`

When `delegate_task` fails with `NOT NULL constraint failed: session_message.seq`, the delegation infrastructure itself is broken — not the subagent's task.

**Decision tree:**
```
delegate_task fails 2x with session_message.seq error?
  → YES → Stop attempting dispatch. Execute directly (Megumi Kato).
  → NO  → Retry once. If it still fails, execute directly.
```

**Why execute directly:** The error is in child session provisioning, not the task. A new subagent will hit the same error. The main agent (Megumi Kato) is not a subagent — it doesn't go through the broken provisioning path.

**After direct execution:** Document the failure in the session handoff notes. The subagent dispatch path is blocked until the root cause (session DB seq collision or missing default) is fixed.

**Real example (2026-06-07):**
- 3 parallel `delegate_task` calls → all 3 failed with `session_message.seq NOT NULL constraint failed`
- Phase 3 execution deferred to a future session
- All 8 Phase 3 tasks remained unimplemented despite a complete impl plan

## Skill Authoring (when output IS a skill)

**When opencode-build produces a skill, follow techne/skills/writing-skill.md exactly.** Subagent reads it first, then composes.

```bash
opencode run --model opencode/minimax-m3-free --dir <techne_path> \
  "Read: techne/skills/writing-skill.md"

## Next Steps

- Need Svelte 5 component patterns? → opencode-build/references/svelte5-component-patterns.md
- Need to adopt/migrate design from old-next reference? → opencode-build/references/design-adoption-pattern.md
- Multi-file phase delivery (parallel subagents → verify → one commit)? → opencode-build/references/phase-delivery-pattern.md
- SvelteKit [id] + [slug] route conflict → opencode-build/references/sveltekit-route-conflict.md
- Adapter-static + Netlify Blobs (client-side only)? → opencode-build/references/netlify-blob-upload-pattern.md
- Offline-first sync + LLM-CRD pattern? → opencode-build/references/offline-first-sync-pattern.md
- Vitest + jsdom + fake-indexeddb setup (for IndexedDB tests in Node.js)? → opencode-build/references/vitest-jsdom-fake-indexeddb.md
- Identity/RBAC field-completeness? → opencode-build/references/identity-field-completeness.md
- Need to compose meta prompt first? → opencode-build/meta-prompt.md (mandatory)
- Need strict task decomposition? → opencode-build/decompose.md
- Need to verify decomposition? → opencode-build/verify-decompose.md
- Git + GitHub patterns (PLAN push via gh api, rebase blocks)? → opencode-build/references/git-helpers.md
- Skill authoring? → opencode-build/references/writing-skill-notes.md (key rules from techne writing-skill)
- Need web search/fetch? → opencode-web/SKILL.md (chained)
- Need full writing-skill format? → techne/skills/writing-skill.md

## Common Mistakes

**For existing (non-empty) directory:** See `references/sveltekit-scaffold-commands.md` for the exact working command. Key flag: `--no-dir-check` skips the interactive prompt that times out subagents.

```bash
cd ~/soap-perfume-website
npx sv create . --template minimal --types ts --no-add-ons --no-dir-check --install pnpm
```

Key flags:
- `--no-dir-check` — skips "Directory not empty" interactive prompt (the subagent killer)
- `--no-add-ons` — no prettier/eslint/vitest/playwright prompts
- `--install pnpm` — auto-installs deps with pnpm

`npm create svelte` is deprecated. `sv create` is the current CLI.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `npm create svelte` | Use `npx sv create` instead |
| Non-empty dir without `--no-dir-check` | Subagent hangs on interactive prompt |
| Multiple tests before impl | One RED, one GREEN only |
| Subagent not given 8-block brief | Never dispatch without it |
| Skipping p.get_status() | Mandatory after every phase |
| Task too large | Decompose first |
| No pre-flight mistakes check | Grep mistakes.md first |
| Skill authored without reading writing-skill.md | Read techne/skills/writing-skill.md first |
| Tests written after implementation (not RED first) | TDD loop requires RED test BEFORE impl — subagents routinely add tests post-hoc; verify test was written and failed BEFORE the subagent wrote any implementation code |
| Using `createEventDispatcher` in Svelte 5 | Use `$props()` + callback props (`onsave`, `oncancel`) — `createEventDispatcher` is deprecated and causes parse errors |
| bcryptjs throws on malformed hash | Wrap `bcrypt.compare()` in try/catch returning false — `bcrypt.verify()` does not exist in bcryptjs |
| Identity fields missing at runtime | Use `?? 'Unknown'` safe defaults; add explicit test for null-field path |

### Three-Fix Pattern — Test Infra + CI Without Re-Running Subagent

When CI fails due to missing test infra (vitest config, setup files, scripts), fix locally without re-delegating:

```
1. Create vitest.config.ts (jsdom env + SvelteKit plugin + fake-indexeddb/auto setup)
2. Create vitest-setup.ts with: import 'fake-indexeddb/auto'
3. Add "test": "vitest run" to package.json scripts
4. Fix .github/workflows/ci.yml: remove continue-on-error, add pnpm test step
5. Run npm run test locally to confirm 15/15 green
6. Commit and push
```

Real example: tests existed (`src/lib/db/*.test.ts`) but vitest.config.ts and vitest-setup.ts were missing → all 14 tests failed with `IndexedDB API missing`. Three files fixed it. The subagent was not re-run — the main agent fixed directly and pushed.

## Session Patterns Observed

### bcryptjs try/catch pattern (2026-06-05)
`bcrypt.compare()` throws on malformed hash — it does NOT return false. Pattern:

```ts
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
    try {
        return await bcrypt.compare(password, hash);
    } catch {
        return false;
    }
}
```

Never use `bcrypt.verify()` — it doesn't exist in bcryptjs. Always use `bcrypt.compare()` with try/catch.

### Phase 0 task delegation via parallel subagents (2026-06-05)
Three Phase 0 tasks delegated in parallel (db-builder, auth-builder, css-builder). Subagent completed or hit iteration limit. Auth fix task dispatched separately. Pattern: parallel dispatch → check results → fix needed → dispatch fix task. Works well.

### TDD violation — tests added post-hoc (Track B, 2026-06-09)
Subagent added tests after writing implementation, not RED first. Root cause: IMPLEMENT phase lacked explicit step-by-step TDD enforcement. Fix: Added mandatory RED→GREEN steps to IMPLEMENT phase description. Identity/RBAC checklist added for optional-parameter tasks.

## Next Steps

- Need to compose meta prompt first? → opencode-build/meta-prompt.md (mandatory)
- Need strict task decomposition? → opencode-build/decompose.md
- Need to verify decomposition? → opencode-build/verify-decompose.md
- Skill authoring? → opencode-build/references/writing-skill-notes.md (key rules from techne writing-skill)
- Need web search/fetch? → opencode-web/SKILL.md (chained)
- Need full writing-skill format? → techne/skills/writing-skill.md