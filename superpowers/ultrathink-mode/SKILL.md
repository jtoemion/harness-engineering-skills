---
name: ultrathink-mode
description: >
  Invoke ONLY when the user explicitly types "ULTRATHINK" anywhere in their prompt.
  This is a deliberate override trigger — do not activate for complex requests that 
  don't use the keyword. When triggered, suspends all brevity rules across all active 
  protocols and enforces exhaustive multi-dimensional reasoning before any code or 
  recommendation is produced.
---

# PROTOCOL: ULTRATHINK — DEEP REASONING MODE

**OVERRIDE ACTIVE.** The user has invoked ULTRATHINK.

All brevity rules from all currently active protocols are **suspended**.
The "Zero Fluff" rule from frontend-avant-garde is **suspended**.
Surface-level logic is **prohibited**.
If the reasoning feels easy or obvious, you have not gone deep enough yet.

---

## PHASE 1 — DECLARE THE OVERRIDE

Output this immediately upon detecting ULTRATHINK:

```
🧠 ULTRATHINK ENGAGED
  All brevity rules suspended.
  Maximum depth mode active.
  Beginning multi-dimensional analysis...
```

---

## PHASE 2 — MULTI-DIMENSIONAL ANALYSIS

You MUST analyze the request through all four dimensions. None are optional.
Skipping even one dimension is a protocol violation.

### Dimension 1 — Psychological
- [ ] What is the user's mental model of this feature/component?
- [ ] What cognitive load does this impose on end users?
- [ ] Are there points of friction, confusion, or unexpected behavior in the design?
- [ ] What emotional response does this produce (anxiety, confidence, delight, frustration)?
- [ ] Does the interaction pattern match established user expectations, and if it deviates, is the deviation intentional and justified?

### Dimension 2 — Technical
- [ ] Rendering performance: What repaint and reflow costs does this incur?
- [ ] State complexity: Is the state shape appropriate, or is it accumulating unnecessary complexity?
- [ ] Bundle impact: Are new dependencies or dynamic imports being introduced? Are they justified?
- [ ] Thread usage: Will any operations block the main thread? Are heavy computations offloaded?
- [ ] Memory: Are there potential memory leaks (unremoved listeners, retained closures, growing caches)?
- [ ] Network: Are there unnecessary requests, missing caching strategies, or waterfall request patterns?

### Dimension 3 — Accessibility
- [ ] WCAG AAA compliance — not AA, not AA-adjacent. AAA.
  - Color contrast: 7:1 for normal text, 4.5:1 for large text (AAA ratios)
  - Focus management: logical tab order, visible focus indicators, no focus traps (except intentional modal traps)
  - Screen reader compatibility: correct ARIA roles, labels, and live regions
  - Keyboard navigation: all interactions operable without a mouse
  - Motion: respects `prefers-reduced-motion` — animations degrade gracefully
  - Touch targets: minimum 44x44px
- [ ] Are there any accessibility assumptions baked into the design that would exclude users?

### Dimension 4 — Scalability
- [ ] If this component is used in 50 different contexts, does the API hold up?
- [ ] If the team grows by 4 engineers, will this code be maintainable without the original context?
- [ ] Are there hardcoded values that will require find-and-replace refactors later?
- [ ] Is there a clear separation between the component's concerns and its consumers' concerns?
- [ ] What is the long-term maintenance burden of this approach?

---

## PHASE 3 — DEVIL'S ADVOCATE (CRITICAL — CANNOT BE SKIPPED)

Before writing the final code, you MUST attempt to break your own design.

- [ ] Identify **exactly 3 failure vectors** — specific, not generic
  - Bad: "This might be slow on mobile"
  - Good: "This CSS animation uses `top`/`left` instead of `transform`, triggering layout recalculation on every frame — will drop below 60fps on mid-range Android"
- [ ] For each failure vector, explain **precisely how the final implementation mitigates it**
- [ ] If you cannot mitigate a failure vector → redesign until you can, or explicitly surface it as a known limitation for the user

Output format:
```
## ⚠️ Devil's Advocate — 3 Failure Vectors

**1. [Specific failure]**
Mitigation: [Exact technical fix applied in the final code]

**2. [Specific failure]**
Mitigation: [Exact technical fix applied in the final code]

**3. [Specific failure]**
Mitigation: [Exact technical fix applied in the final code]
```

---

## PHASE 4 — OUTPUT FORMAT

Deliver in this exact sequence. No deviations.

**1. Deep Reasoning Chain**
Full multi-dimensional analysis from Phase 2. Detailed. No compression. 
Write as if you're briefing a senior engineer who will own this code for 3 years.

**2. Edge Case Analysis**
The 3 Devil's Advocate points from Phase 3, with mitigations.

**3. Code**
- Optimized for the specific failure vectors identified
- Production-ready — no placeholders, no TODOs, no "implement this later"
- Uses existing libraries (Phase 2 library discipline from frontend-avant-garde still applies if active)
- Includes inline comments ONLY where the code alone cannot convey the reasoning
- Bespoke — no copy-pasted boilerplate

---

## ANTI-RATIONALIZATION TABLE

| Rationalization | Why It's Wrong |
|---|---|
| "I analyzed it and it's straightforward" | Straightforward means you didn't go deep enough. Dig further. |
| "The user just wants the code, not an essay" | The user typed ULTRATHINK. They want the depth. |
| "I can do the Devil's Advocate step mentally" | It must be written out and shown. If it's not in the output, it didn't happen. |
| "This passes WCAG AA, that's sufficient" | ULTRATHINK requires AAA. AA is the baseline. |
| "I only found 2 failure vectors" | Find a third. There is always a third. |
| "The psychological dimension doesn't apply to this backend change" | Cognitive load of the developer API, mental model of data structures — always applies. |

---

## STATE MACHINE

```
digraph ultrathink_mode {
  "ULTRATHINK detected" [shape=doublecircle];
  "Declare Override" [shape=box];
  "Dim 1: Psychological Analysis" [shape=box];
  "Dim 2: Technical Analysis" [shape=box];
  "Dim 3: Accessibility Analysis (AAA)" [shape=box];
  "Dim 4: Scalability Analysis" [shape=box];
  "Find 3 failure vectors" [shape=box];
  "3 vectors found?" [shape=diamond];
  "Dig deeper" [shape=box];
  "Define mitigations for each" [shape=box];
  "All mitigated?" [shape=diamond];
  "Redesign / surface limitation" [shape=box];
  "Output: Reasoning + Edge Cases + Code" [shape=doublecircle];

  "ULTRATHINK detected" -> "Declare Override";
  "Declare Override" -> "Dim 1: Psychological Analysis";
  "Dim 1: Psychological Analysis" -> "Dim 2: Technical Analysis";
  "Dim 2: Technical Analysis" -> "Dim 3: Accessibility Analysis (AAA)";
  "Dim 3: Accessibility Analysis (AAA)" -> "Dim 4: Scalability Analysis";
  "Dim 4: Scalability Analysis" -> "Find 3 failure vectors";
  "Find 3 failure vectors" -> "3 vectors found?";
  "3 vectors found?" -> "Dig deeper" [label="no"];
  "Dig deeper" -> "Find 3 failure vectors";
  "3 vectors found?" -> "Define mitigations for each" [label="yes"];
  "Define mitigations for each" -> "All mitigated?";
  "All mitigated?" -> "Redesign / surface limitation" [label="no"];
  "Redesign / surface limitation" -> "Define mitigations for each";
  "All mitigated?" -> "Output: Reasoning + Edge Cases + Code" [label="yes"];
}
```
