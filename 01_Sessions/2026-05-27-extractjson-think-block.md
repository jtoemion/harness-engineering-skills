---
name: 2026-05-27-extractjson-think-block
project: pastpapr
session_close: 2026-05-27T18:45:00Z
tags: [retro]
---

## LLM extractJSON — thinking model compatibility fix

### GOAL
Fix quiz question generation failing for MiniMax-M2.7 (thinking model) due to broken JSON extraction from <think>… block output.

### DONE
Rewrote `extractJSON()` in `student-portal/src/lib/llm/openaiCompat.ts`:
- Strip `` tags before scanning (with unclosed-tag guard)
- Brace-counting scan finds ALL complete {...} blocks
- Smart selection: prefer objects with 'questions'/'issues' key, else last candidate dict
- Deleted dead `candidates` variable that was shadowing Step 3 logic

17/17 tests pass. Live API call verified: 5 valid quiz questions extracted from MiniMax M2.7 thinking output. Committed to `claude/xenodochial-ramanujan-b1605c`.

### ROOM OF IMPROVEMENT
Should have caught this with a test that uses the actual MiniMax API output format earlier. Unit tests used simulated think blocks but didn't cover the case where `<think>` appears mid-text (not at start).

### FLAWS TO FLAG
Used `indexOf('{')` + `lastIndexOf('}')` without considering thinking-model output. Assumed JSON would be the first thing in the response.

### WHAT I DO BETTER
When fixing a parser, validate against actual API output first — not just synthetic test data.

### HOW I DO BETTER
For thinking models (DeepSeek-R1, QwQ, MiniMax-M2.7), the real JSON is always at the END, after the think block. Should scan all complete JSON objects and select the one with the right root key.

### PATTERNS
Thinking-model JSON extraction: strip tags → brace-counting scan → smart selection by root key ('questions' or 'issues').

### MISTAKES
Using `indexOf`/`lastIndexOf` for structured extraction when the model emits thinking tags. The first `{` inside the think block is never the answer.