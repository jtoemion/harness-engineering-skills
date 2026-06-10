---
name: thread-context
description: Use when starting any session — verifies thread identity, enforces cross-thread boundaries, and maintains Honcho knowledge base. Mandatory for every conversation turn.
---

# Thread Context

## Purpose

Enforce strict thread isolation. Prevent context bleed between threads. Maintain auditable proof that thread boundaries are respected.

## Core Rule

**Every response must begin with thread verification.** No exceptions.

---

## Thread Verification Protocol (Every Turn)

### Turn N where N % 2 == 1 (turn 1, 3, 5...): Full Check

1. **Read context.md** for current thread
2. **Quote proof:** Reproduce one specific line verbatim from context.md in response
3. **Call honcho_context()** — verify current thread context
4. **Call honcho_conclude()** — update Honcho KB with session decisions
5. **Append to session.log** — `[THREAD-VERIFIED]` marker

### Turn N where N % 2 == 0 (turn 2, 4, 6...): Light Check

1. **Read context.md** for current thread (verify nothing changed)
2. **Quote proof** — different line than previous turn
3. **Append to session.log** — `[THREAD-VERIFIED]` marker

---

## Quote Proof Format

Every response must include:

```
[THREAD-VERIFIED] judah/context.md line N:
> "exact text from the file, verbatim"
```

The quote must be from the current session's context.md. You cannot quote from a different thread's file.

**If you cannot find a meaningful line to quote:**
→ Write to context.md first to populate it, then quote.

---

## Cross-thread Data Requests

When user asks for data from another thread:

1. **Read that thread's permissions.md** — check if access is allowed
2. **If ALLOWED:** Read context.md, note access in session.log
3. **If BLOCKED:** Tell user "I don't have access to that thread's data. Explicit user routing required."

Never access another thread's context.md without checking permissions.md first.

---

## Session Log Format

Append to `~/.hermes/threads/<thread>/session.log` each turn:

```
[YYYY-MM-DDTHH:MM:SSZ] [T<N>] [THREAD-VERIFIED] Read <thread>/context.md — "quoted line"
[YYYY-MM-DDTHH:MM:SSZ] [T<N>] [HONCHO-CALLED] honcho_context() + honcho_conclude()
```

---

## Thread Identification

Current threads (name-based, not thread-number based):

| Thread | Owner | Thread IDs | Purpose |
|---|---|---|---|
| ezra-personal | Ezra Theodores | 1501 + DM 6575927128 | Personal workspace — curriculums, content. STERILE. |
| studentportal | Ezra Theodores | 1 (group -5218220874:6575927128) | EzraLMS/studentportal codebase — engineering |
| judah | Judah Zebaoth | 495 (group -1003966031884:495) | harness-engineering-skills / SoaPure |
| soapure | SoaPure | 641 (group -1003966031884:641) | soap-perfume-website / cosmic graph |
| kanban | Kanban workers | N/A | Kanban task orchestration |

---

## Verification Checklist (Per Response)

- [ ] Quote proof included from current thread's context.md?
- [ ] Session log updated with [THREAD-VERIFIED] marker?
- [ ] If cross-thread request: permissions.md checked first?
- [ ] Honcho called (odd turns only)?

If any item missing: do it before responding.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Skipping quote proof "because it's obvious" | Always quote. Trust but verify. |
| Reading another thread's context.md without permissions check | Check permissions.md first |
| Forgetting to update session.log | Append immediately after quote proof |
| Using stale context.md data | Re-read at start of each turn |

---

## Example Turn

**User:** "build the thing"

**Agent response:**

```
[THREAD-VERIFIED] judah/context.md line 7:
> "Active Project: harness-engineering-skills / thread-context architecture"

Building the thread directory system now.
...
[SESSION-LOGGED] judah/session.log updated.
```