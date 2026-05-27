---
name: LLM-P001-think-block-json-extraction
category: llm
applies_to: [openaiCompat, structuredOutput, quiz generation]
status: ACTIVE
date: 2026-05-27
project: pastpapr
---

## Think-Block-First JSON Extraction Pattern

### What

When parsing LLM output from thinking models (MiniMax-M2.7, DeepSeek-R1, QwQ), the actual JSON answer is always at the END of the response, after the `<think>…` think block. The think block may contain example JSON with matched braces that would be falsely captured by naive indexOf extraction.

### When to use

Any time you're parsing structured JSON output from a model that emits `<think>…` tags.

### How

```
1. Strip think tags (with unclosed-tag guard)
   cleaned = text.replace(/<think>[\s\S]*?<\/think>/gi, '').trim()

2. Brace-counting scan finds ALL complete {...} blocks
   → returns list of all complete JSON objects/arrays

3. Smart selection:
   if any object has 'questions' or 'issues' key → select the LAST such object
   else if any dict object → select the LAST dict
   else → select the last item in the list
```

### Why it works

Thinking models reason step-by-step inside the think block. The actual answer is produced AFTER the reasoning, so it's at the end of the response. Brace-counting correctly handles nested braces inside the think block. Selecting by root key disambiguates example JSON from real output.

### Examples

**MiniMax-M2.7 quiz generation:**
```
<think>
The user wants questions. Example: {"questions":[{"id_q":"Q1",...}]}
Now let me generate the actual 5 questions:
{"questions":[{"id_q":"Q1","en_q":"What is 2+2?","options":[...],"ans":2}]}

{"questions":[actual questions]}
```
Result: correctly extracts the last `{"questions":[...]}` block.

**DeepSeek-R1 code generation:**
Similar pattern — reasoning block contains example code with braces, actual code at end.

### Trade-offs

**Pros:** Works reliably with all thinking models. Handles truncated streams gracefully. More robust than position-based extraction.

**Cons:** O(n) scan instead of O(1) indexOf. If model returns bare array without wrapper, won't be selected by root-key heuristic (falls through to last-resort). Slightly more code to maintain.

### Related mistakes

- [LLM-001-thinking-model-json-extraction](./llm-001-thinking-model-json-extraction.md)