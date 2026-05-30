---
name: persona-brainstorm
description: "Persona-based discovery session. Ezekiel asks Jeremiah questions to surface one high-impact improvement. Output: CONTEXT.md + ADR.md."
triggers:
  - persona brainstorm
  - grill session
  - client dev dialogue
  - discover improvement
  - Ezekiel Jeremiah
---

# Persona Brainstorm — Grill-with-Docs Discovery

## Purpose

Find **one high-impact, concrete, actionable** improvement through a structured client-dev dialogue. The goal is NOT feature brainstorming or voting — it is focused insight from friction, not aspiration.

The session is run as a roleplay between two personas: **Ezekiel** reads code/docs and asks questions; **Jeremiah** answers from full project context. **Megumi** documents silently.

Output: 3 documented ADRs, updated CONTEXT.md, and the method saved as a reusable skill.

---

## Participants

| Persona | Role |
|---------|------|
| **Ezekiel** (Developer) | Reads .docs/ and .memory/, asks targeted questions, translates client feedback into ADR decisions |
| **Jeremiah** (Client) | Loaded with full project context — answers from real product understanding, user pain, workflow gaps |
| **Megumi** (Observer/Scribe) | Documents to CONTEXT.md and ADR.md; silent unless correcting format |

**Jeremiah is NOT Judah.** Jeremiah is a persona representing the client with full product knowledge. Judah should not answer as Jeremiah — redirection required if Judah answers directly.

---

## Preparation

### Before starting
1. Load the project's full context:
   ```
   .docs/             → project-overview.md, architecture.md, dev-guide.md, source-tree.md
   .memory/           → feature_list.json, projectbrief.md, decisions.json,
                        activeContext.md, context-handoff.md, progress.txt, mistakes.json
   ```
2. Identify 2-3 specific contradictions or unfinished states from reading the docs:
   - "Implementation complete & LIVE" but next step is manual E2E test?
   - Feature marked "in_progress" for months with no movement?
   - Two code paths for the same feature with different constants?
   - Deprecated system still live in production?
3. Prepare Ezekiel's opening question from the most acute contradiction found.

---

## Session Structure

### Phase 1 — Orientation (5 min)

Ezekiel opens with: what he knows from reading the docs, then one pointed question about the contradiction he found. Not "what do you want?" — specific and grounded in the code.

Examples of good opening questions:
- "I see the report card is marked 'live' but the next step is a manual E2E test — did that ever get verified?"
- "League reset is manual only, and the Firebase functions still live with old thresholds. Is dual-write a real risk, or are those functions completely parked?"
- "EPIC-1 is still 'in_progress' after months. Is the data still split across two curriculum models, or did tutors settle on one?"

### Phase 2 — Discovery (3 rounds, ~20 min)

**Round 1:** Ezekiel asks one question about the product loop — how users actually engage daily vs periodically. Closes surface-level questions fast.

**Round 2:** Ezekiel digs on the thread that seemed most real from Round 1. Pushes until Jeremiah gives a concrete pain statement, not a vague wish.

**Round 3:** Ezekiel pivots to a second theme if one exists. Otherwise, synthesizes.

Guideline: **One question at a time.** No piling. When an answer resolves, close it in CONTEXT.md and document with G-Q#.

### Phase 3 — ADR Writing (~10 min)

For each confirmed improvement, Ezekiel:
1. States the context — what's wrong, in more detail
2. Jeremiah responds — what users are actually feeling
3. Ezekiel writes the ADR in real time using the template below
4. Megumi confirms it was saved

### Phase 4 — Skill Save

After the session, offer to save the method as a reusable skill.

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
2. **Jeremiah first.** If Judah answers instead of Jeremiah, redirect: "Let's keep Jeremiah in character."
3. **No vague ADRs.** "Improve UX" is not an ADR. "Add 3-field TutorSessionNoteModal with Firestore write" is.
4. **ADR comes from friction, not aspiration.** The strongest improvements surface from real contradictions — not "wouldn't it be nice" but "this keeps breaking in production" or "tutors keep asking us about this."
5. **Cap at 3 ADRs.** Three finished ADRs is a good session. Discovery without resolution is just conversation.
6. **Push to contradictions.** If Jeremiah gives a soft answer, Ezekiel pushes: "Can you give me a specific example of when that came up?"
7. **Document in real time.** Megumi writes G-Q# entries to CONTEXT.md as questions close, and writes completed ADRs to ADR.md immediately after they're drafted.
8. **Push to correct repo immediately.** File was written during session — push immediately after session ends. No buffering.

---

## When to Run

- Beginning of a new development cycle
- Before committing a large feature investment
- When backlog grooming produces weak priorities
- When the team knows "something is off" but can't name it

## When NOT to Run

- When you already have a concrete spec — go straight to planning
- When the user wants a list of 10 features — this is a focusing exercise
- When stakeholders are not aligned — Jeremiah must speak with one voice

---

## Output Checklist

- CONTEXT.md updated: G-Q# entries per question, closure status (Closed / To Jeremiah / ADR-N)
- ADR.md: N entries (N less than 3), one per confirmed improvement
- Skill saved to `~/.hermes/skills/persona-brainstorm/SKILL.md`
- Pushed to correct repo (harness-engineering-skills for skill, project repo for ADR/CONTEXT.md)

---

## Example — Pastpapr LMS (transcript excerpt)

**Ezekiel:** Looking at your history, one thing jumps out: the report card generator is marked LIVE but the next immediate step is a manual E2E test. Did that ever get verified?

**Jeremiah:** Report card generator is fine.

**Ezekiel:** Two more things. One — the curriculum model migration (EPIC-1) is still in_progress after months. Is the live data split across both models, or did tutors settle on one? Two — what keeps students returning daily vs monthly?

**Jeremiah (on curriculum):** They've settled on the new model. The old one is dead in practice. But the code still has both. That's noise. I want the old model excised, not migrated.

**Jeremiah (on engagement):** The product is a quiz wrapper with a roster. Students come in, do quizzes, earn XP, move up a league — that loop works. But it doesn't connect to what the tutor is doing all week. No real-time observation capture. No notes. The product is looking backward.

**Ezekiel → ADR-001:** Session observation capture (TutorSessionNoteModal — 3 fields, linked to student profile, visible in next session).

**Ezekiel → ADR-002:** Curriculum model excision — remove old Topic/SubjectMatter paths from DAL, Service, Types, Rules.

**Ezekiel → ADR-003:** Spaced review widget — system uses its own quiz pass/fail data to proactively signal which topics a student should revisit before they forget it.
