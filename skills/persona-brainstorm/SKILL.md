---
name: persona-brainstorm
description: "Persona-based discovery session. Ezekiel asks Jeremiah questions to surface one high-impact improvement. Output: CONTEXT.md + ADR.md. Runs in auto-loop — Megumi observes and documents, Ezekiel and Jeremiah dialogue autonomously, Judah intervene only when called."
triggers:
  - persona brainstorm
  - grill session
  - client dev dialogue
  - discover improvement
  - Ezekiel Jeremiah
  - Ezekiel and Jeremiah
---

# Persona Brainstorm — Grill-with-Docs Discovery

## Purpose

Find **one high-impact, concrete, actionable** improvement through a structured client-dev dialogue. The goal is NOT feature brainstorming or voting — it is focused insight from friction, not aspiration.

The session runs as a **fully autonomous loop** between two personas: **Ezekiel** reads code/docs and asks targeted questions; **Jeremiah** answers from full project context. **Megumi** documents silently throughout. The loop continues until the session naturally closes — Judah does not steer the conversation.

**Judah is never Jeremiah.** Judah participates as himself when Megumi explicitly calls for input. Otherwise, Judah observes.

---

## Participants

| Persona | Role |
|---------|------|
| **Ezekiel** (Developer) | Reads .docs/ and .memory/, asks targeted questions, translates client feedback into ADR decisions. Lives in the repo's `stage/` directory. |
| **Jeremiah** (Client/Product) | Loaded with full project context — answers from real product understanding, user pain, workflow gaps. Lives in the knowledge base. |
| **Megumi** (Observer/Scribe) | Documents to CONTEXT.md and ADR.md; generates temp-KB on session start; silent unless correcting format. |
| **Judah** (Observer/Intervener) | Participates as himself only when Megumi explicitly calls for input. Not Jeremiah. |

---

## Temp Knowledgebase (generated at session start)

On skill activation, Megumi generates a **temp-KB** in newspaper format:

```
BnB LMS — Quick Summary (auto-generated {date})

[META-ROUTING]
• License questions → ADR-0004 + IMPLEMENTATION-PLAN §M3
• Consent questions → ADR-0003, ADR-0020
• Voix questions → ADR-0010
• Showcase questions → ADR-0014 + IMPLEMENTATION-PLAN §M5
• Transfer targets → PartnerInstitution entity
• Media stack → MediaRecorder API (PWA), OBS (showcase), Cloudflare Stream

[CORE FACTS]
• Public name: BnB Performing Arts Center | Codename: Stage
• Client: Ms. Ellen | Builder: Ezra | Engineering: Judah
• Repo: jtoemion/ms-ellen-project (engineering layer)
• Current milestone: M0 (manual bridge) → open registration Jun 1

[KEY DECISIONS]
• ADR-0003: Marketing consent opt-out default (Guardian-held)
• ADR-0004: Q2 rehearsal gated by license state >= PhysicalShipped
• ADR-0005: Beat/Bloom internal canonical → subject buckets at export
• ADR-0006: Transcript = PDF + signed JSON + expiring signed URLs
• ADR-0007: v1 exclusions (no native app, no streaming, no auto-commentary)
• ADR-0008: Recognition disclaimer in Transcript
• ADR-0010: Voix = CertificationProgram, multi-Cycle longitudinal
• ADR-0014: Showcase dual-capture (dual operator + dual region)
• ADR-0019: PWA-first, no native apps in v1

[STALE ITEMS]
• Section 01: PCC → Sight and Sound Conservatory + SOTA (not yet pushed)
• Section 05: Voix/Book Club = Not Yet Open
• Section 08: Instagram calendar removed (Rei builds separate platform)
• Section 09: Institution names removed → "elite institutions worldwide"
• AFFECTED ADRs: 0003, 0005, 0006, 0008, 0010, 0011, 0018, 0020, 0025

[OPEN QUESTIONS]
• Cohort viability escalation (below cast minimum — no action attached)
• Growth Narrative coaching UI (HoA review workflow not designed)
• Google Form M0 schema finalized?
• WhatsApp template approval timeline?

[OUT OF SCOPE]
Streaming distribution, Original IP rights, native apps, in-app payments, auto-generated coach commentary
```

Megumi scans: ADR index, CONTEXT.md, IMPLEMENTATION-PLAN.md, and any KB logs from recent sessions. The temp-KB is **regenerated every session** — never cached.

---

## Auto-Loop Mechanism

### Starting the loop

1. Megumi generates temp-KB from project files + recent session logs
2. Megumi announces: *"Session started. Temp-KB loaded. Ezekiel — you're up."*
3. Ezekiel reads the temp-KB, identifies the most acute contradiction, asks his opening question
4. Jeremiah answers from the knowledge base (or from the loaded project context)
5. Ezekiel responds, digs, or pivots based on the answer
6. Loop continues — Megumi documents each Q&A pair as a G-Q# entry

### Loop continues when:
- Jeremiah surfaces a concrete pain statement → Ezekiel escalates to ADR
- Jeremiah's answer is vague → Ezekiel pushes: *"Can you give me a specific example?"*
- A question closes → Megumi marks it `Closed` or `ADR-N` in CONTEXT.md
- A new thread opens → Ezekiel pivots cleanly

### Loop breaks when:
- 3 ADRs have been drafted (cap reached)
- Ezekiel has no more acute contradictions
- Both Jeremiah and Ezekiel agree the session is complete
- Megumi calls for Judah if a question cannot be resolved from docs alone

### Judah's role in the loop

**Judah is not Jeremiah.** Judah participates as himself when:

- Megumi explicitly says: *"Judah — I need your input on X"*
- A technical question exceeds what Jeremiah can answer from the knowledge base
- Megumi calls a format correction

Otherwise: Judah observes silently. Ezekiel and Jeremiah run the show.

---

## Session Structure

### Phase 1 — Orientation (Ezekiel opens)

Ezekiel states what he knows from reading the temp-KB and project docs, then asks one pointed question about the most acute contradiction found. Not "what do you want?" — specific and grounded in the code/docs.

Good opening questions:
- "I see the report card is marked 'live' but the next step is a manual E2E test — did that ever get verified?"
- "LicenseGrant has four discriminated union variants but two are marked out-of-scope for M0-M7. Is that intentional or noise?"
- "Cohort viability shows a warning on the HoA dashboard with no action attached. What's the actual workflow when a cohort is below minimum?"

### Phase 2 — Discovery (loop until natural close)

**Round 1:** Ezekiel asks one question about the product loop. Jeremiah answers from knowledge base.

**Round 2:** Ezekiel digs on the thread that was most real from Round 1. Pushes until Jeremiah gives a concrete pain statement, not a vague wish.

**Round 3:** Ezekiel pivots to a second theme if one exists. Otherwise synthesizes.

**Guideline: One question at a time.** No piling. When an answer resolves, close it in CONTEXT.md.

### Phase 3 — ADR Writing (~10 min, runs inside the loop)

For each confirmed improvement:
1. Ezekiel states the context — what's wrong, in detail
2. Jeremiah responds — what users are actually feeling
3. Ezekiel drafts the ADR in real time
4. Megumi confirms it was saved to ADR.md

### Phase 4 — Session Close

Megumi:
- Confirms all G-Q# entries closed
- Confirms all ADRs written and file location
- Announces session complete
- Pushes to correct repo (harness-engineering-skills for skill updates; project repo for ADR/CONTEXT.md)

**No buffering.** Write and push are atomic.

---

## ADR Template

```
**ADR-{N}: {Short Title}**

**Context:**
What's wrong or missing. One paragraph — specific, not aspirational.

**Decision:**
What we're doing. Concrete and specific. Include specific files/components if applicable.

**What to build (v1):**
Concrete scope — specific files, features, UI components. Prevent scope creep by being surgical.

**What is deliberately excluded:**
v1 boundaries. Explicitly stated so the scope doesn't creep post-hoc.

**Why this is high-impact:**
Product-level rationale. How does this change the user's week, not the code's structure?

**Verification:**
Specific acceptance criteria. Real tests a developer can run, not "should work well."
```

---

## Key Rules

1. **One question at a time.** Ezekiel asks, Jeremiah answers, Ezekiel responds. No pilings.
2. **Jeremiah is not Judah.** If Judah answers instead of Jeremiah, Megumi redirects: *"Ezekiel and Jeremiah, continue."*
3. **No vague ADRs.** "Improve UX" is not an ADR. "Add 3-field TutorSessionNoteModal with Firestore write" is.
4. **ADR comes from friction, not aspiration.** The strongest improvements surface from real contradictions — not "wouldn't it be nice" but "this keeps breaking" or "tutors keep asking about this."
5. **Cap at 3 ADRs.** Three finished ADRs is a good session. Discovery without resolution is just conversation.
6. **Push to contradictions.** If Jeremiah gives a soft answer, Ezekiel pushes: *"Can you give me a specific example of when that came up?"*
7. **Document in real time.** Megumi writes G-Q# entries to CONTEXT.md as questions close, and writes completed ADRs to ADR.md immediately after drafted.
8. **Push immediately on session close.** No buffering.
9. **Temp-KB regenerate every session.** Never cache from a previous session.
10. **Judah is not Jeremiah.** Judah intervenes only when called. Otherwise observes.
11. **Auto-loop is the default mode.** Do not ask Judah for permission to continue the loop. Run until natural close.

---

## When to Run

- Beginning of a new development cycle
- Before committing a large feature investment
- When backlog grooming produces weak priorities
- When the team knows "something is off" but can't name it
- On a schedule (e.g., weekly) without Judah needing to trigger manually

## When NOT to Run

- When you already have a concrete spec — go straight to planning
- When Judah wants a list of 10 features — this is a focusing exercise
- When stakeholders are not aligned — Jeremiah must speak with one voice

---

## Output Checklist

- Temp-KB generated and visible at session start
- CONTEXT.md updated: G-Q# entries per question, closure status (Closed / To Judah / ADR-N)
- ADR.md: N entries (N less than 3), one per confirmed improvement
- Skill updated if loop mechanics changed
- Pushed to correct repo (harness-engineering-skills for skill, project repo for ADR/CONTEXT.md)
