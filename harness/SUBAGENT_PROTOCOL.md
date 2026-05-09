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
6. COMPILE results
7. PRESENT to user
```

**Main agent touches ZERO implementation files.**

---

## SUBAGENT BRIEF TEMPLATE

```markdown
# Subagent Brief: [TYPE] — [TASK NAME]

**Type**      : [explore | build | review]
**Objective** : [What to accomplish — 1 sentence]
**Constraints**: [Must NOT do X | Must do Y]
**Success**   : [How to verify — specific, measurable]
**Context**   : [2 sentences — what led to this]

## Files / Scope
- [file/path] — focus on [aspect]
- [file/path] — focus on [aspect]

## Output
Write results to SUBAGENT_RESULT.md before returning.
```

---

## SUBAGENT RESULT TEMPLATE

```markdown
# Subagent Result: [TYPE] — [TASK NAME]

**Status**   : [SUCCESS | PARTIAL | FAILED]
**Summary**  : [What was done — max 300 words]
**Evidence** : [Key findings with file:line refs]
**Next**     : [Recommended next steps]
**Files**    : [Any files modified — path only]
**Mistakes** : [Any issues encountered]
```

---

## CHECKPOINTING (After each subagent)

```
1. READ SUBAGENT_RESULT.md — ONLY this file
2. EXTRACT: Status, Summary, Evidence, Next, Files
3. LOG any mistakes to {SKILLS_ROOT}\harness\MISTAKES.md
4. UPDATE .memory/ with findings
5. IF parallel dispatch → wait for remaining
6. CONTINUE
```

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

---

## SUBAGENT RESULT FILE

**Location:** `./SUBAGENT_RESULT.md` (in project root)
**Format:** See template above
**Contract:** Main agent ONLY reads this file from subagent session