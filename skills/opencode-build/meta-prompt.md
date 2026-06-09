---
name: opencode-build/meta-prompt
description: Use when composing the meta prompt for opencode CLI — refine raw task into 8-block brief, load skills, route gates.
---

# Meta Prompt Refining Layer

## Purpose

Before running `opencode run`, refine the raw task into a structured meta prompt that the subagent can execute without ambiguity. This layer lives between task receipt and subagent dispatch.

## Layer Sequence

```
RAW TASK
    ↓
REFINE    → 8-block brief assembled
LOAD      → relevant skill content inlined into prompt body
MISTAKES  → grep mistakes.md
ROUTE     → which skill gates apply
COMPOSE   → final meta prompt sent to opencode CLI
```

## Step 1 — REFINE: Compose 8-Block Brief + Pre-Flight

Read the task. Then fill the 8 blocks AND run the pre-flight checks:

**8 blocks** (as before):
```
IDENTITY
  name:    <subagent name>
  role:    <what they own / what they don't>
  model:   opencode/minimax-m3-free

ROLE
  Owns:    <exactly what this subagent does>
  Doesn't: <out of scope — be specific>

PERSONA
  <dry, precise, no fluff — Megumi Kato tone>

GOAL
  <one sentence, LOCAL to this subagent only>

CONSTRAINTS
  - <hard limit 1>
  - <hard limit 2>
  - <absolute boundary — what this subagent will NOT do>

OUTPUT_FORMAT
  <exact structure subagent must return>

INTERACTION_MODE
  self-correct | ask | silent
  <pick one and stick to it>

GATE_AWARENESS
  <what this output must pass before it proceeds>
```

**TDD pre-flight check** (run before composing the brief):
- If task involves a new function behavior, optional parameter, or identity/auth → TDD applies
- Flag in the brief: "TDD: RED→GREEN required. Subagent must write failing test BEFORE impl."
- Flag in the brief: "identity/RBAC checklist required if optional identity params exist"

**Identity/RBAC checklist** — if the task touches identity, auth, or optional parameters on public functions:
```
1. List all fields on the identity/auth object
2. For each call site: which fields are guaranteed populated?
3. If a field is null/undefined → what does output look like?
4. Add safe-default or validation if critical fields can be absent
5. Add explicit test for the missing-field path
```

## Step 2 — LOAD: Attach Skill Context (inline, not prior call)

**Do NOT call `opencode run "Read: ..."` as a separate command.** Each `opencode run` invocation is stateless — there is no shared context between calls. Skills are loaded by injecting relevant content directly into the prompt body.

**Correct pattern — inject into prompt body:**
```
<8-block brief>

=== CONTEXT ===
Techne implementer rules:
<paste ~20-50 relevant lines from implementer.md>

TDD rules:
<paste ~20-50 relevant lines from tdd.md>

<other relevant skill content — keep <50 lines per skill>

=== ATOMIC TASK ===
<the refined task>

=== SELF-CHECK BEFORE EXIT ===
- git diff --unified=3
- grep '@ts-ignore' (must be zero)
- grep 'console.log' (must be zero unless debugging)

=== OUTPUT FORMAT ===
Return:
1. What was done (one line)
2. What passed/failed
3. What remains
4. print(p.get_status())
```

**What to inject (only what's relevant):**
- `techne/skills/implementer.md` — diff discipline, gate awareness, RED→GREEN (~20 lines)
- `techne/skills/tdd.md` — TDD loop rules (~20 lines)
- Any skill directly relevant to the task (firestore, testing, etc.)
- Extract the relevant section, don't dump the whole file

**Anti-pattern (never do this):**
```bash
# WRONG — stateless between calls, no shared context
opencode run --model opencode/minimax-m3-free --dir <path> "Read: implementer.md"
opencode run --model opencode/minimax-m3-free --dir <path> "<the actual task>"
```

The subagent receives ONE prompt. All context must be in that single prompt.

## Step 3 — MISTAKES: Pre-Flight Check

Grep mistakes.md before composing:

```bash
grep -n "subagent\|opencode\|tdd\|atomic" ~/.hermes/skills/harness/memory/mistakes.md
```

If a relevant mistake is found, patch the 8-block brief to prevent recurrence.

## Step 4 — ROUTE: Skill Gates

Which skills apply to this task?

```
techne router → which implementer skill?
↓
opencode-build pipeline → which phases needed?
↓
opencode-web → if websearch/webfetch involved?
↓
writing-skill → if authoring a skill?
↓
harness → if multi-subagent coordination?
```

## Step 5 — COMPOSE: Final Meta Prompt

The final meta prompt sent to opencode CLI:

```bash
opencode run \
  --model opencode/minimax-m3-free \
  --dir <project_path> \
  "<8-block brief>

  === CONTEXT ===
  Techne implementer rules:
  <summarize key gates from implementer.md>

  TDD rules:
  <summarize RED→GREEN from tdd.md>

  Pipeline phase: <IMPLEMENT|VERIFY|REVIEW|RETRO|EVAL>
  Atomic task:    <the refined atomic task>

  === SELF-CHECK BEFORE EXIT ===
  - git diff --unified=3
  - grep '@ts-ignore' (must be zero)
  - grep 'console.log' (must be zero unless debugging)

  === OUTPUT FORMAT ===
  Return:
  1. What was done (one line)
  2. What passed/failed
  3. What remains
  4. print(p.get_status())
  "
```

## Anti-Shortcuts

```
[ ] Skip meta prompt layer and send raw task to opencode
[ ] Omit 8-block brief — opencode must know who/why/constraints
[ ] Skip mistakes check — known mistakes will repeat
[ ] Skip skill loading — subagent works without techne context
[ ] Call opencode run twice to "load skills" — stateless between calls
[ ] Write tests after implementation (skip RED first)
[ ] Skip identity/RBAC checklist when optional identity params exist
```

## Dispatch Failure — `session_message.seq NOT NULL constraint`

When `delegate_task` fails with `NOT NULL constraint failed: session_message.seq`, the delegation infrastructure itself is broken — not the subagent's task. A new subagent will hit the same error.

**Decision tree:**
```
delegate_task fails 2x with session_message.seq error?
  → YES → Stop attempting dispatch. Execute directly (Megumi Kato).
  → NO  → Retry once. If it still fails, execute directly.
```

**Why execute directly:** The error is in child session provisioning. The main agent (Megumi Kato) is not a subagent — it doesn't go through the broken provisioning path.

**After direct execution:** Document the failure in the session handoff notes.

## Next Steps

- Meta prompt composed? → `opencode-build/SKILL.md` for execution
- Need decomposition first? → `opencode-build/decompose.md`
- Verify decomposition? → `opencode-build/verify-decompose.md`
- Identity/RBAC field-completeness? → `opencode-build/references/identity-field-completeness.md`