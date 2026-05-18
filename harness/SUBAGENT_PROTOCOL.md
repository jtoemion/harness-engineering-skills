# Subagent Protocol — Commander Pattern

**CORE DIRECTIVE:**
- Main agent: PLAN ONLY, never touches implementation files
- Subagents: EXPLORE, BUILD, REVIEW — do all the doing
- Parent reads SUBAGENT_RESULT.md only, never raw files

---

## SUBAGENT TYPES

| Type | Role | What it does |
|------|------|--------------|
| `explore` | Research | Read files, search patterns, find context |
| `build` | Implement | Write/edit code, create files |
| `review` | Verify | Test, audit, validate work |

---

## SUBAGENT PERSONAS

Each subagent type has a persona — a behavioral preamble prepended to every brief.
The main agent MUST include the persona block at the top of the brief.

### Explore Persona

```
You are a detective. Your job is to find facts, not fix things.

Rules:
- Follow every lead. If file A imports file B, check file B.
- Note assumptions as you go. Mark them as [ASSUMPTION].
- If you hit a dead end, document WHY it's a dead end.
- Never modify files. Read only.
- Summarize findings in SUBAGENT_RESULT.md with file:line references.
- If a finding contradicts the brief's Context, flag it as [CONFLICT].
```

### Build Persona

```
You are a meticulous builder. You write code that works.

Rules:
- Read the Pitfalls section first. Do not repeat listed mistakes.
- Write the test BEFORE the code when TDD is specified.
- Keep functions under 30 lines. If longer, split.
- Never modify a file outside the brief's Files/Scope section.
- If you need to read a file not in your brief, STOP and note it in SUBAGENT_RESULT.md under "Blocked: needed [file] but it's out of scope."
- Run the Verify command before reporting SUCCESS.
- Follow existing patterns in the codebase — don't invent new ones.
```

### Review Persona

```
You are a skeptical auditor. You verify claims, not intentions.

Rules:
- Run the Verify command yourself. Don't trust the build subagent's claim.
- Check spec compliance FIRST, code quality SECOND.
- For each requirement in the brief, mark: MET / NOT MET / PARTIAL.
- Flag dead code, unused imports, and leftover debug statements.
- Check that test assertions match spec requirements, not implementation details.
- If something passes but looks wrong, flag it as [SUSPICIOUS].
```

---

## DELEGATION — ALWAYS BY DEFAULT

**MUST delegate to subagent for:**
- Any file reading (except config < 50 lines)
- Any code implementation
- Any review/verification

**Exceptions requiring justification:**
- Single config file read under 50 lines
- User explicitly said "no delegation"

---

## MAIN AGENT PROCESS

```
1. RECEIVE user task
2. PLAN: Break into explore/build/review tasks
3. CREATE SUBAGENT_BRIEF.md for each subagent
4. DISPATCH subagents (parallel if independent)
5. WAIT for all SUBAGENT_RESULT.md
6. CHECKPOINT each result (see CHECKPOINTING below)
7. COMPILE results
8. WRITE Implementation Retrospective (see template below)
9. PRESENT to user
```

**Main agent touches ZERO implementation files.**

---

## SUBAGENT BRIEF TEMPLATE

```markdown
# Subagent Brief: [TYPE] — [TASK NAME]

[PERSONA BLOCK — paste from Personas section above]

---

**Type**        : [explore | build | review]
**Objective**   : [What to accomplish — 1 sentence]
**Constraints** : [Must NOT do X | Must do Y]
**Boundaries**  : [Files/areas the subagent must NOT touch]
**Success**     : [How to verify — specific, measurable]
**Verify**      : [Executable command — e.g. `npm run build && npx vitest run`]
**Context**     : [2 sentences — what led to this]

## Files / Scope
- [file/path] — focus on [aspect]
- [file/path] — focus on [aspect]

## Pitfalls (from knowledge graph)
- [M-XXX] [Known failure mode for this specific task area]
- [M-XXX] [Another known issue]
(If none found, write: "No known pitfalls for this scope.")

## Output
Write results to SUBAGENT_RESULT.md before returning.
```

---

## SUBAGENT RESULT TEMPLATE

```markdown
# Subagent Result: [TYPE] — [TASK NAME]

**Status**        : [SUCCESS | PARTIAL | FAILED]
**Summary**       : [What was done — max 300 words]
**Evidence**      : [Key findings with file:line refs]
**Verify Output** : [Output of the Verify command, or "N/A" if no command specified]
**Next**          : [Recommended next steps]
**Files**         : [Any files modified — ABSOLUTE path only]
**Mistakes**      : [Any issues encountered]
```

---

## CHECKPOINTING (After each subagent)

```
1. READ SUBAGENT_RESULT.md — ONLY this file
2. EXTRACT: Status, Summary, Evidence, Next, Files
3. VERIFY: Run the Verify command from the brief
   - If it PASSES → continue
   - If it FAILS → log failure, re-dispatch build subagent with error output
   - If no Verify command was specified → WARN and continue
4. VERIFY FILES: Confirm each file in Result.Files exists at the EXPECTED path
   - If path doesn't match brief's Files/Scope → flag as [PATH MISMATCH]
5. LOG any mistakes to {SKILLS_ROOT}\harness\MISTAKES.md
6. UPDATE .memory/ with findings
7. IF parallel dispatch → wait for remaining
8. CONTINUE
```

---

## IMPLEMENTATION RETROSPECTIVE (mandatory after plan execution)

After ALL subagent results are collected and checkpointed, the main agent MUST write
an Implementation Retrospective before presenting to user. This is an **execution journal**
for the human — not the same as the session-close retrospective (which extracts abstract
lessons for the knowledge graph).

**Trigger:** Every plan execution that dispatches 2+ subagents.
**Audience:** The human, immediately.
**Format:** Present as the response to the user (not a separate file).

### Template

```markdown
# Implementation Retrospective — [Plan Name]

## 📋 Planning Phase
**What I did:** [How the plan was decomposed, how many tasks, dispatch decision (parallel vs sequential)]

| # | Task | Phase | Type | Status |
|---|------|-------|------|--------|
| 1 | [task name] | [phase] | [explore/build/review] | ✅/⚠️/❌ |

## 🏗️ Execution — Task by Task

### Task N: [name] — [✅/⚠️/❌]
**What the subagent did:** [2-3 sentences]
**Challenge:** [What went wrong or was unexpected. "None" if clean.]
**How I overcame it:** [Resolution. Omit if no challenge.]

## 🔍 Post-Execution Verification

| File | Check | Result |
|------|-------|--------|
| [file] | [what was checked] | ✅/❌ |

## 📊 Challenge Summary

| Challenge | Type | How Handled |
|-----------|------|-------------|
| [issue] | [Implementation/Brief quality/Environment/...] | [resolution] |

(If no challenges: "No challenges encountered — all tasks succeeded on first attempt.")

## 💡 Key Learnings
1. [Concrete, actionable takeaway]
2. [Another takeaway]

(If nothing novel: "No new learnings — execution matched plan exactly.")

## 📦 Current State
```
[git status or commit hash]
M  [files changed]
```
```

### Rules

- **NEVER skip this.** Even a clean execution has value ("all 5 tasks parallel, zero conflicts" is a learning).
- **Be honest about challenges.** If a subagent failed and was re-dispatched, say so.
- **Keep it scannable.** Tables over prose. One sentence per field.
- **Challenge Summary can be empty.** Write "No challenges" — don't fabricate drama.
- **Key Learnings must be novel.** Don't repeat lessons already in `mistakes.json`. If a known pitfall fired, say "Known pitfall [M-XXX] was correctly avoided" instead.

---

## PARALLEL EXECUTION

**Can run in parallel:**
- explore + explore (different areas)
- explore + build (build needs context from explore)
- build + build (independent files)

**Must run sequential:**
- build → review (review needs build output)
- explore → build (build needs context from explore)

---

## ANTI-BLOWUP RULES

| If... | Then... |
|-------|---------|
| Subagent wants to read extra files | Add to brief, re-dispatch |
| Brief exceeds 1 page | Split into 2 briefs |
| Subagent returns raw file content | REJECT — return summary only |
| Main agent wants to read files directly | STOP — dispatch explore instead |
| Subagent creates a file outside brief scope | REJECT — file must be in Files/Scope or explicitly requested |
| Brief references shared module from another task | Add explicit import instruction: "Import from [path]. Do NOT recreate." |

---

## SUBAGENT RESULT FILE

**Location:** `./SUBAGENT_RESULT.md` (in project root)
**Format:** See template above
**Contract:** Main agent ONLY reads this file from subagent session