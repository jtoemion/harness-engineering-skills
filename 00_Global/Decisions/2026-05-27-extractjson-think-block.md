# ADR-002: JSON Extraction Strategy for Thinking-Model LLM Output

**Date:** 2026-05-27
**Project:** PastPaper Student Portal (pastpapr)
**Status:** ACCEPTED

## Context

The LLM quiz generation pipeline was failing for MiniMax-M2.7 (and potentially DeepSeek-R1/QwQ) because `extractJSON()` assumed JSON would be the first content in the response. However, thinking models emit a `<think>…` block BEFORE the actual JSON, and the think block itself may contain example JSON with matched braces.

The old extraction used `indexOf('{')` + `lastIndexOf('}')`:
- `indexOf('{')` found the first `{` inside the think block's example JSON — wrong
- `lastIndexOf('}')` found a `}` somewhere early in the think block — also wrong

## Decision

Replace indexOf/lastIndexOf with a 3-step strategy:

1. **Strip thinking tags** before scanning. Handle unclosed tags gracefully (truncated streams).
2. **Brace-counting scan** to find ALL complete `{...}` or `[...]` blocks. This correctly handles nested braces inside the thinking block.
3. **Smart selection**: prefer objects with `'questions'` or `'issues'` root key → last candidate dict → last resort (last item).

## Rationale

Thinking models emit the actual answer at the END of the response, after the think block. The first complete JSON found (via indexOf) is always the example inside the think block. Brace-counting + selecting the last valid JSON that has the expected root key reliably gets the real answer.

## Consequences

**Pros:**
- Works correctly with MiniMax-M2.7, DeepSeek-R1, QwQ thinking models
- Handles truncated streams gracefully (doesn't crash)
- More robust overall — scans all complete JSON instead of assuming position

**Cons:**
- Slightly more complex than indexOf/lastIndexOf
- If the model returns bare array `[...]` without wrapper, it won't be selected by root-key heuristic (but will fall through to last-resort selection)
- Performance: O(n) scan vs O(1) indexOf — negligible for typical response sizes

## Alternative Considered

**Option A — Strip only when `<think>` is at start:**
- Problem: MiniMax sometimes emits `<think>` mid-text, and the JSON is still after it
- Would miss the actual JSON in those cases

**Option B — Use model-specific parsing flags:**
- Problem: Couples code to specific model behavior
- More fragile when models update

**Option C — Force non-thinking models:**
- Rejected: MiniMax-M2.7 is the best free option for Indonesian curriculum content

---

**Supersedes:** (none — new feature)
**Reviewed-by:** (none — Megumi Kato solo session)