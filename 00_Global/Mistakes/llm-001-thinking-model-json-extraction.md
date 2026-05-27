---
name: LLM-001-thinking-model-json-extraction
category: llm
applies_to: [openaiCompat, structuredOutput, MiniMax-M2.7, DeepSeek-R1, QwQ]
status: ACTIVE
date: 2026-05-27
project: pastpapr
---

## Thinking-Model JSON Extraction Fails with indexOf/lastIndexOf

### What happened

Quiz generation failed for MiniMax-M2.7 (thinking model). The `extractJSON()` function in `openaiCompat.ts` used `indexOf('{')` + `lastIndexOf('}')` to find JSON in the response.

MiniMax-M2.7 emits `<think>…` BEFORE the JSON:
```
<think>
The user wants questions. Example JSON: {"questions":[...]}
Now let me produce actual questions:
{"questions":[...actual 5 questions...]}

{"questions":[...]}
```

`indexOf('{')` found the `{` in the example JSON inside the think block. `lastIndexOf('}')` found a `}` somewhere early (inside the think block text). The extracted string was garbage.

### Why it happened

indexOf/lastIndexOf assumes JSON is the first thing in the response. Thinking models put preamble and example JSON in the think block BEFORE the actual answer. The first complete `{...}` found is never the answer.

### Lesson

For thinking-model output: strip think tags → brace-counting scan → select by root key. Never assume JSON position.

### How to avoid

When implementing structured output parsing for a model you haven't tested with, validate against actual API output before shipping. Synthetic test data doesn't catch model-specific output format quirks.

### Evidence

- `student-portal/src/lib/llm/openaiCompat.ts` — extractJSON function
- `claude/xenodochial-ramanujan-b1605c` commit: `f71afe0`
- Live API test: 5 quiz questions successfully extracted from MiniMax-M2.7 thinking output