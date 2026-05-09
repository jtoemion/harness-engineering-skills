# Convert Process

Convert existing skills to outcome-driven format by rebuilding from intent, not structure.

## Overview

Conversion is NOT restructuring — it's rebuilding. The original structure is a guide for what to cover, not a template for the new format.

**Key principle:** Rebuild from the intent, not from the existing structure. If you start by editing the existing file, you'll preserve structure that should be cut.

## Step 1: Capture Original

**Goal:** Document the existing skill before any changes.

1. **Read the full skill** — every file, every section
2. **Extract the intent** — What outcome is this skill supposed to produce?
3. **List all content categories** — What topics does it cover?
4. **Note structural choices** — How is it organized? Why?
5. **Record what works** — Which sections produce correct agent behavior?
6. **Record what doesn't** — Which sections do agents ignore or misinterpret?

**Output:** A capture document:

```
## Original Capture: [skill-name]

**Intent:** [stated or inferred outcome]

**Content Categories:**
- [Category 1]
- [Category 2]
- ...

**What works:**
- [Section/behavior that produces correct outcomes]

**What doesn't:**
- [Section/behavior that agents ignore or misinterpret]

**Structural choices:**
- [Why it's organized this way — if known]
```

## Step 2: Rebuild from Intent

**Goal:** Create the new skill starting from the outcome, not the old structure.

1. **State the outcome** — One sentence: what should this skill produce?
2. **Classify the type** — Simple utility, simple workflow, or complex workflow?
3. **Run the pruning check** — For each piece of original content:
   > "Would an LLM do this correctly WITHOUT being told?"
4. **Draft new structure** — Based on classification, not original structure
5. **Write new content** — Outcome-driven instructions (WHAT not HOW)

**Key rule:** Do NOT start by editing the existing file. Start from a blank page with the intent in mind. Only consult the original capture when you need specific details.

### Rebuild Checklist

- [ ] Outcome statement written
- [ ] Skill type classified
- [ ] Pruning check run against ALL original content
- [ ] New structure matches classification (not original structure)
- [ ] Instructions state WHAT outcome, not HOW steps
- [ ] Description uses "Use when..." triggering conditions only
- [ ] Cross-references reference by skill name, not path

## Step 3: Categorize Changes

**Goal:** Document what changed and why, distinguishing content decisions from structural ones.

### Categories

| Category | Description | Example |
|----------|-------------|---------|
| **Removed — Obvious** | LLM would do this correctly unsupervised | "Read the file before editing" |
| **Removed — Redundant** | Said the same thing in 3 places | Repeated compliance checks |
| **Removed — Out of scope** | Didn't serve the core intent | Tangential tips |
| **Restructured — Progressive disclosure** | Moved important content up | Key principle from bottom to top |
| **Restructured — Type fit** | Changed structure to match classification | Flat file → multi-phase docs |
| **Rewritten — Outcome-driven** | Changed HOW instructions to WHAT outcomes | "Step 1, 2, 3" → "Achieve X, then Y" |
| **Rewritten — Description** | Fixed description to triggering conditions | Workflow summary → "Use when..." |
| **Kept — Judgment call** | LLM would get this wrong without guidance | Non-obvious ordering or priority |
| **Kept — Edge case** | Critical exception to common behavior | "Always X except when Y" |
| **Added — Missing judgment** | New content for a decision the original missed | "Choose X when Y, Z otherwise" |

### Change Categorization Template

```
## Change Log: [skill-name]

### Removed
| Content | Reason | Category |
|---------|--------|----------|
| [what was removed] | [why] | Obvious/Redundant/Out of scope |

### Restructured
| Content | Change | Reason | Category |
|---------|--------|--------|----------|
| [what moved] | [from → to] | [why] | Progressive disclosure/Type fit |

### Rewritten
| Content | Before | After | Category |
|---------|--------|-------|----------|
| [what changed] | [old text] | [new text] | Outcome-driven/Description |

### Kept Unchanged
| Content | Reason | Category |
|---------|--------|----------|
| [what stayed] | [why it still matters] | Judgment call/Edge case |
```

## Step 4: Generate Comparison Report

**Goal:** Present what changed and confirm the conversion is complete.

### Report Template

```
## Conversion Report: [skill-name]

**Original intent:** [from Step 1]
**Rebuilt intent:** [from Step 2]
**Skill type:** [classification]

### Summary Statistics
- Sections removed: [N] ([N] obvious, [N] redundant, [N] out of scope)
- Sections restructured: [N]
- Sections rewritten: [N]
- Sections kept: [N]
- Sections added: [N]

### Pruning Impact
- Original token count (approx): [N]
- New token count (approx): [N]
- Reduction: [N]% or [+N]% increase

### Key Changes
1. [Most significant change and why]
2. [Second most significant]
3. [Third most significant]

### Verification Checklist
- [ ] New skill produces same outcome as original
- [ ] All judgment calls preserved or improved
- [ ] No content removed that agents need
- [ ] Description is "Use when..." triggering conditions
- [ ] Progressive disclosure: important info first
- [ ] Cross-references are skill names, not paths
```

**Present report to user. Confirm conversion is complete before replacing original.**