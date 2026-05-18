---
name: context-handoff
description: "Generates an ultra-dense forensic handoff document for transferring project context, active bugs, and diagnostic payload to another AI agent or reasoning model. Deploys subagents for context gathering when .memory/.docs are absent."
quick_ref:
  trigger: "User says 'handoff', 'context transfer', 'brief another model', 'prepare for [model name]', or 'diagnostic payload'"
  output: "Standalone markdown document (handoff payload) presented to user"
  subagents: "Deploys explore subagents if .memory/ or .docs/ don't exist"
---

# Context Handoff — Forensic Diagnostic Payload Generator

## Overview

This skill generates a **Context Handoff and Diagnostic Payload** — a single, ultra-dense document designed for a 1M+ token reasoning model to ingest and immediately produce deep architectural insights, root-cause analysis, or production-ready fixes.

**The receiving model should be able to act on this document alone, with zero follow-up questions.**

**Announce at start:** "Generating context handoff payload. Ingesting project state..."

## When It Fires

- User explicitly requests a handoff, context transfer, or diagnostic payload
- User says "prepare context for [Claude/Gemini/GPT/etc.]"
- User says "I need another model to look at this"
- User says "make a handoff document"

---

## Phase 0: Mandatory Context Ingestion

Before writing ANYTHING, you MUST build complete situational awareness.

### Path A: Memory Exists (`.memory/` or `.docs/` present)

```
1. READ all files in .memory/ — especially:
   - activeContext.md (current state)
   - progress.md (what's done, what's next)
   - mistakes.json (known failure modes)
   - patterns.json (discovered patterns)
   - variables.json (project-specific constants)
   - projectbrief.md (project purpose and scope)
2. READ all files in .docs/ (if exists)
3. CROSS-REFERENCE with active chat history
4. CROSS-REFERENCE with active code buffer / open files
5. IDENTIFY the specific problem or context being handed off
```

### Path B: No Memory — Deploy Subagents

If `.memory/` and `.docs/` do NOT exist, you cannot write a forensic handoff from thin air.

```
1. ANNOUNCE: "No .memory/ or .docs/ found. Deploying explore subagents to gather context."
2. DISPATCH explore subagents (parallel):
   - Subagent 1: Project structure — read package.json/pyproject.toml, folder tree, entry points
   - Subagent 2: Architecture — read main config files, routing, database schemas, auth flow
   - Subagent 3: Recent changes — read git log -20, git diff HEAD~5, identify active area of work
   - Subagent 4: Error state — read build output, test results, console errors, open issues
3. COLLECT all SUBAGENT_RESULT.md files
4. SYNTHESIZE into working context
5. PROCEED to Phase 1
```

**Rule:** If subagents return insufficient context (e.g., no package.json, no git history), ask the user to describe the project before proceeding. Do NOT fabricate context.

---

## Phase 1: Generate the Handoff Document

Structure the payload into these **exact sections**, in this order. Every section is mandatory — if a section has no content, write "No data available — receiving model should investigate."

---

### Section 1: Architectural Blueprint & Environment Fingerprint

**Purpose:** Give the receiving model a complete mental model of the system in under 60 seconds.

```markdown
## 1. Architectural Blueprint & Environment Fingerprint

### Stack
- Runtime: [exact versions — e.g., Node 22.1.0, Python 3.13.2]
- Framework: [e.g., Next.js 15.2, FastAPI 0.115]
- Database: [e.g., Firestore, PostgreSQL 16, SQLite]
- Auth: [e.g., Firebase Auth with anonymous proxy, JWT]
- Hosting: [e.g., Vercel, Cloud Run, self-hosted]
- OS: [e.g., Windows 11, Ubuntu 24.04]

### Architecture
[2-3 paragraph description of system design, data flow, and key abstractions.
Draw from .memory/projectbrief.md and .memory/activeContext.md.]

### Key Schemas / State Machines
[Exact TypeScript interfaces, database schemas, state machine definitions.
Include the FULL schema, not a summary.]

### Dependency Map
[Which modules depend on which. Entry points → core logic → data layer → external services.
Use a simple list or mermaid diagram.]
```

---

### Section 2: The Forensic State of Play

**Purpose:** What works, what's broken, what's in between.

```markdown
## 2. The Forensic State of Play

### Fully Operational
- [Component A] — verified via [test/manual check], last touched [date]
- [Component B] — verified via [test/manual check], last touched [date]

### Partially Functional
- [Component C] — works for [case X] but fails for [case Y]
  - Evidence: [error log, test output, or behavioral description]

### Broken / Failing
- [Component D] — fails at [file:line] with [exact error]
  - Full error output:
    ```
    [paste complete error, not truncated]
    ```
  - Reproduction: [exact steps to reproduce]
```

---

### Section 3: What Was Already Tried

**Purpose:** Prevent the receiving model from suggesting things that already failed. This is the #1 reason handoffs waste tokens.

```markdown
## 3. What Was Already Tried

| # | Approach | Result | Why It Failed |
|---|----------|--------|---------------|
| 1 | [what was attempted] | [outcome] | [root cause of failure] |
| 2 | [what was attempted] | [outcome] | [root cause of failure] |

### Hypotheses Eliminated
- [Hypothesis A] — disproven because [evidence]
- [Hypothesis B] — disproven because [evidence]
```

---

### Section 4: The Chaos Delta (Exact Friction Point)

**Purpose:** Isolate the precise technical challenge. This is where the receiving model should focus 80% of its attention.

```markdown
## 4. The Chaos Delta

### The Core Problem (1 sentence)
[State the problem in exactly one sentence.]

### Why This Is Hard
[2-3 paragraphs explaining why simple fixes fail, where the logic breaks
under edge conditions, or what architectural constraint prevents the obvious solution.]

### Reproduction Steps
1. [Exact step]
2. [Exact step]
3. [Expected: X. Actual: Y.]

### Flagged Flaws
| # | Flaw | Location | Impact |
|---|------|----------|--------|
| 1 | [description] | [file:line] | [what breaks] |
| 2 | [description] | [file:line] | [what breaks] |
```

---

### Section 5: Isolated Code Sandboxes (Blast Radius Only)

**Purpose:** Give the receiving model the exact code that's causing the problem — nothing more, nothing less.

```markdown
## 5. Isolated Code Sandboxes

### [Component Name] — [file path]
Lines [start]-[end] | Last modified: [date]
```[language]
[COMPLETE, UNMODIFIED code block — no truncation]
```

### [Related Component] — [file path]
Lines [start]-[end] | Last modified: [date]
```[language]
[COMPLETE, UNMODIFIED code block — no truncation]
```
```

**Rules for this section:**
- Every code block MUST have: file path, line range, language tag
- Include ONLY files within the blast radius — strip everything unrelated
- If a file is >200 lines, include only the relevant function/class with 10 lines of surrounding context
- Never paraphrase code — paste it verbatim

---

### Section 6: Targeted Diagnostic Prompts

**Purpose:** Tell the receiving model exactly what questions to answer and how to answer them.

```markdown
## 6. Diagnostic Prompts for Receiving Model

**Instructions to receiving model:**
You are receiving a forensic handoff. Do NOT provide high-level advice.
Every response must include:
- Exact file paths and line numbers
- Complete replacement code blocks (not diffs, not pseudocode)
- Verification commands to confirm the fix works

**Questions:**

### Q1: Architecture (structural)
[Ask about the system's structural integrity — e.g., "Is the dependency
between X and Y creating a circular reference that explains the Z behavior?"]

### Q2: Data Flow (behavioral)
[Ask about data flow — e.g., "Trace the user ID from login through to
the Firestore write at file:line. Where does the value mutate?"]

### Q3: Edge Case (adversarial)
[Ask about edge cases — e.g., "What happens when X is null/undefined
at file:line? The schema says required but the runtime allows it."]

### Q4: Blind Spot (meta)
[Ask what you might be missing — e.g., "Given this architecture, what
failure mode are we not seeing? What assumption are we making that
could be wrong?"]
```

---

## Phase 2: Quality Gate

Before presenting the handoff to the user, self-check:

| Check | Pass Criteria |
|-------|--------------|
| **Completeness** | All 6 sections are filled (no "TODO" or "TBD") |
| **Specificity** | Every code reference has file:line, every error has full output |
| **No Summarization** | Code blocks are verbatim, errors are complete, not truncated |
| **Already Tried** | Section 3 has at least 1 entry (if debugging), or "N/A — this is a greenfield handoff" |
| **Diagnostic Prompts** | All 4 questions are specific to THIS problem, not generic |
| **Stack Versions** | Section 1 has exact version numbers, not "latest" or "recent" |

If any check fails, fix it before presenting.

---

## Output Format

```
⚡ CONTEXT HANDOFF GENERATED
  Sections    : 6/6 complete
  Code blocks : [N] files embedded
  Blast radius: [list of files in scope]
  Target      : [receiving model or "general"]
  Context from: [.memory/ | subagent exploration | chat history]
```

Then present the full handoff document.

---

## Anti-Rationalization

| Rationalization | Why It's Wrong |
|---|---|
| "The receiving model can figure out the stack" | No. Version differences cause 80% of wrong suggestions. Be explicit. |
| "I'll summarize the code to save tokens" | The target has 1M+ tokens. Verbatim code costs nothing. Summarized code loses the bug. |
| "Section 3 is empty because nothing was tried" | Then say "Greenfield investigation — no prior attempts." Don't omit the section. |
| "I don't have enough context for a full handoff" | Then deploy subagents (Path B) or ask the user. Never write a partial handoff. |
| "The diagnostic prompts are obvious" | If they're obvious, the receiving model will answer them in 10 seconds. If they're not, you just proved why they need writing. |

---

## Integration

- **Conductor** can include this as a terminal step when the user asks for help from another model
- **SUBAGENT_PROTOCOL.md** explore personas are used for Path B context gathering
- **memorybank** Phase 1 data is the primary input for Path A
- This skill does NOT modify any files — it is read-only and produces a document
