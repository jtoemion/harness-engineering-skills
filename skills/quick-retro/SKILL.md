---
name: quick-retro
description: Run a lightweight retrospective at session close — 7 structural questions, outputs to 00_Memory, syncs to global vault
quick_ref:
  start: "retro(task, outcome) — open the 7-question sequence"
  done: "retro_done() — write session note, update memory, sync global"
  snapshot: "retro_snapshot() — print current memory state for handoff"
---

# QUICK-RETRO — Session Retrospective Playbook

## When to Use

After completing a task. Run `retro(task, outcome)` at session close, or whenever you want to capture what happened before moving on.

Use this instead of a full retrospective when:
- The task was ≤2 hours of work
- The fix was straightforward (root cause found, solution applied, verified)
- You need to move on but want to capture the lesson

Use a full retrospective instead when:
- The task took multiple sessions
- The problem was ambiguous or had no clear root cause
- You made architectural decisions with long-term trade-offs

## The 7-Question Sequence

Answer these in order. Keep each answer to 1-3 sentences.

### GOAL
What was the task, in one line?

### DONE
What actually got shipped? (Be specific — file changed, test added, API verified)

### ROOM OF IMPROVEMENT
What would you do differently if you started over?

### FLAWS TO FLAG
What was wrong with your process? (Not the code — the approach)

### WHAT I DO BETTER
What behavior/technique improved since last time?

### HOW I DO BETTER
What did you actually change in your workflow?

### PATTERNS
What is now a known pattern? (Something that will apply to future work)

### MISTAKES
What mistake did you make that others should avoid?

---

## Output Format

Write outputs to `00_Memory/` canonical files:

### session note → `01_Sessions/{YYYY-MM-DD}-{slug}.md`
```
---
name: {slug}
project: {project_code}
session_close: {ISO timestamp}
tags: [retro]
---

## {Session Title}

### GOAL
{task one-liner}

### DONE
{what shipped}

### ROOM OF IMPROVEMENT
{answer}

### FLAWS TO FLAG
{answer}

### WHAT I DO BETTER
{answer}

### HOW I DO BETTER
{answer}

### PATTERNS
{answer}

### MISTAKES
{answer}
```

### activeContext.md → append checkpoint entry
```markdown
## [{ISO timestamp}] Checkpoint
- Task: {task one-liner}
- Status: {DONE|PARTIAL|ABANDONED}
- Lesson: {one-line takeaway}
```

### progress.md → append progress entry
```markdown
## [{ISO timestamp}] Checkpoint: {task one-liner}
```

---

## Session Sync (cross-project global vault)

After writing all session files to `00_Memory/`, sync relevant entries to the global vault at `{ANTIGRAVITY_GLOBAL_VAULT}/`:

- Mistakes → `00_Global/Mistakes/{project}-{slug}.md`
- Patterns → `00_Global/Patterns/{project}-{slug}.md`
- Decisions → `00_Global/Decisions/{YYYY-MM-DD}-{slug}.md` (only if architectural)

Use the `graph_decisions()` format for ADRs. Use the `graph_mistakes()` format for mistake notes.

---

## retro(task, outcome)

```python
def retro(task: str, outcome: str) -> dict:
    """
    Open the 7-question sequence. Call retro_done() to close.
    Returns context dict with GOAL, DONE, ROOM, FLAWS, BETTER, HOW, PATTERNS, MISTAKES.
    """
    return {
        "status": "OPEN",
        "task": task,
        "outcome": outcome,
        "questions": {
            "goal": None,
            "done": None,
            "room": None,
            "flaws": None,
            "better": None,
            "how": None,
            "patterns": None,
            "mistakes": None,
        }
    }
```

## retro_done()

```python
def retro_done(ctx: dict) -> None:
    """
    Close the retro — write session note, update activeContext, update progress,
    sync mistakes/patterns to global vault.
    """
    session_id = ctx.get("session_id") or timestamp_now()
    write_session_note(ctx, session_id)
    update_active_context(ctx)
    update_progress(ctx)
    if ctx["questions"]["mistakes"]:
        write_mistake_note(ctx)
    if ctx["questions"]["patterns"]:
        write_pattern_note(ctx)
    sync_to_global_vault(ctx)
```

## retro_snapshot()

```python
def retro_snapshot() -> str:
    """
    Print current memory state for handoff — used before context compaction
    or when delegating to a subagent.
    """
    # Returns formatted string of all 7 answers + open questions
    pass
```