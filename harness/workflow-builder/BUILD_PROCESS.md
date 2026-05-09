# Build Process

6-phase conversational discovery for building workflow skills.

## Phase 1: Discover Intent

**Goal:** Understand what outcome this skill produces and who needs it.

Ask these questions in conversation:

1. **What outcome should this skill produce?**
   - Not "what should it do" — what END STATE does the user want?
   - Example: "A deployable skill that guides agents through code review" not "A skill about code review"

2. **Who is the user?**
   - What type of agent will use this skill?
   - What will they already know? What will they get wrong?

3. **What judgment calls will the agent face?**
   - Where would an LLM default to the wrong behavior?
   - What decisions require explicit guidance vs. what they'd figure out?

4. **What existing skills or processes relate to this?**
   - Avoid duplicating content from other skills
   - Identify cross-references worth including

**Output:** A clear intent statement — one sentence describing the specific outcome.

## Phase 2: Classify Skill Type

**Goal:** Determine the right structural complexity for the skill.

Present the three types and classify:

| Type | Signals | Structure |
|------|---------|-----------|
| **Simple utility** | Single clear action, no branching, obvious steps | Flat SKILL.md, inline examples |
| **Simple workflow** | Sequential steps, light branching, some judgment needed | SKILL.md + optional reference file |
| **Complex workflow** | Multi-phase, conditional logic, significant judgment calls | SKILL.md + supporting docs per phase |

**Decision rule:** When in doubt, start simpler. You can always add complexity. You cannot easily remove it.

**Confirm with user:** "Based on our discussion, this looks like a [type]. Confirm or adjust?"

## Phase 3: Gather Requirements

**Goal:** Capture the specifics that will shape the skill content.

Gather through conversation:

| Field | Description |
|-------|-------------|
| **Name** | Active voice, verb-first (e.g., `systematic-debugging` not `debug-guide`) |
| **Description** | "Use when..." triggering conditions, NOT a workflow summary |
| **Overview** | Core principle in 1-2 sentences |
| **Role guidance** | What role should the agent adopt? What mindset? |
| **Design rationale** | Why this approach? What alternatives were considered? |

**Key rule for description:** The description triggers the skill to load. It must describe WHEN to use it, not WHAT it does. Summarizing workflow in the description causes agents to shortcut the full skill content.

## Phase 4: Draft & Refine

**Goal:** Write the skill content, then prune relentlessly.

### Draft

Write the initial skill content based on requirements gathered in Phase 3. Include:
- Frontmatter (name, description)
- Overview
- Core content (phases, steps, or reference)
- Quick reference table
- Common mistakes section

### The Pruning Check

For every instruction, ask:

> **"Would an LLM do this correctly WITHOUT being told?"**

| If yes | → Cut it. It's noise that dilutes the signal. |
| If no | → Keep it. This is the content that matters. |
| Unsure | → Keep for now, mark for testing. Remove if tests show it's unnecessary. |

**Pruning targets:**

- Obvious steps ("read the file before editing it")
- Common knowledge ("use git to version control")
- Redundant repetitions ("remember to check errors" in 3 places)
- Boilerplate the LLM generates correctly by default

**What NOT to prune:**

- Judgment calls where LLMs default to the wrong behavior
- Non-obvious ordering or priority decisions
- Counter-intuitive rules
- Edge cases the LLM would miss

## Phase 5: Build

**Goal:** Generate the final skill structure with progressive disclosure.

### Progressive Disclosure Structure

Organize content so the most important information is first:

```
1. Frontmatter (name + trigger-only description)
2. Overview (core principle, 1-2 sentences)
3. When to Use (triggering conditions)
4. Core Content (the skill itself)
5. Quick Reference (table for scanning)
6. Common Mistakes (what goes wrong)
7. Supporting files (only if heavy reference needed)
```

### File Organization

Based on classification from Phase 2:

**Simple utility:** Single `SKILL.md`
**Simple workflow:** `SKILL.md` + optional reference file
**Complex workflow:** `SKILL.md` + supporting process docs

### Generation Checklist

- [ ] Frontmatter: name and description only (max 1024 chars)
- [ ] Description: "Use when..." format, triggering conditions, NO workflow summary
- [ ] Overview: core principle in 1-2 sentences
- [ ] All instructions state WHAT outcome, not HOW steps (unless HOW is non-obvious)
- [ ] Pruning check completed for every section
- [ ] Supporting files exist only when content is too heavy for inline
- [ ] Cross-references use skill name only, no forced loading

## Phase 6: Summary

**Goal:** Present what was built and confirm completion.

### Summary Template

```
## Build Summary

**Name:** [skill-name]
**Type:** [simple utility | simple workflow | complex workflow]
**Intent:** [one-sentence outcome statement from Phase 1]

### Structure
[List files created with brief description of each]

### Key Decisions
- [Decision 1]: [Why]
- [Decision 2]: [Why]

### Pruning Applied
- [Instruction removed]: [Reason — "LLM would do this correctly without guidance"]

### Cross-References
- [Related skill]: [Relationship]

### Next Steps
- [ ] Test with subagent (use writing-skills for TDD validation)
- [ ] Commit to skill directory
- [ ] Update relevant documentation
```

**Confirm with user before considering build complete.**