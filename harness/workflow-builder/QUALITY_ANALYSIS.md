# Quality Analysis

Two-track analysis of existing skills: lint checks (structural) and judgment-based dimensions.

## Track 1: Lint Checks

Automated structural validation.

### Structural Checks

| Check | Rule | Fix |
|-------|------|-----|
| SKILL.md exists | Every skill must have a `SKILL.md` | Create it |
| Frontmatter present | YAML frontmatter at top of SKILL.md | Add `---` delimited block |
| Required fields | `name` and `description` must exist | Add missing fields |
| No extra frontmatter | Only `name` and `description` in frontmatter | Remove extras |
| Orphan files | Every non-SKILL.md file is referenced in SKILL.md | Add reference or remove file |
| Dead references | Every referenced file exists | Create file or remove reference |

### Naming Checks

| Check | Rule | Fix |
|-------|------|-----|
| Skill directory name | Lowercase, hyphens only, verb-first preferred | Rename |
| frontmatter name | Matches directory name | Align them |
| Description format | Starts with "Use when..." | Rewrite |
| Description length | Under 500 chars recommended, 1024 max | Trim |
| No workflow in description | Description must NOT summarize the skill's process | Rewrite to triggering conditions |

### Frontmatter Checks

| Check | Rule | Fix |
|-------|------|-----|
| Valid YAML | Must parse without errors | Fix syntax |
| name format | Letters, numbers, hyphens only | Fix characters |
| description voice | Third person | Rewrite to third person |
| description content | Triggering conditions only | Remove workflow summary |

## Track 2: Judgment-Based Analysis

Five dimensions that require human judgment and agent testing.

### 1. Workflow Integrity

**Question:** Does the skill produce the intended outcome when followed?

| Aspect | Test |
|--------|------|
| Completeness | Can an agent achieve the stated outcome using only this skill? |
| Ordering | Are steps in the right order? Does each step depend on previous? |
| Branching | Are conditional paths clear? Can agents decide correctly? |
| Termination | Does the skill clearly signal when the workflow is complete? |
| Error paths | What happens when things go wrong? Are recovery paths defined? |

**Scoring:**
- **Strong** — All paths complete and terminate correctly
- **Adequate** — Main path works, edge cases may diverge
- **Weak** — Agents regularly get lost or produce incomplete results

### 2. Prompt Craft

**Question:** Are instructions written to produce correct behavior?

| Aspect | Test |
|--------|------|
| Outcome-driven | Do instructions state WHAT to achieve, not HOW? |
| Unambiguous | Can instructions be interpreted in multiple ways? |
| Specificity | Are examples and criteria concrete? |
| Tone | Does language match the skill's purpose (directive vs. guidance)? |
| Pruning ratio | What % of content could an LLM figure out without guidance? |

**Scoring:**
- **Strong** — Clear, outcome-driven, minimal redundancy
- **Adequate** — Mostly clear, some HOW instructions that could be WHAT
- **Weak** — Ambiguous, over-specified, or contradicts itself

### 3. Execution Efficiency

**Question:** Does the skill minimize wasted context while maximizing signal?

| Aspect | Test |
|--------|------|
| Progressive disclosure | Is the most important info first? |
| Token economy | Could any sections be trimmed without losing value? |
| Reference vs. inline | Are heavy details in separate files with brief inline references? |
| Cross-references | Does it reference other skills instead of duplicating? |
| Redundancy | Are the same instructions repeated in multiple places? |

**Scoring:**
- **Strong** — Every token earns its place
- **Adequate** — Minor redundancy, mostly efficient
- **Weak** — Significant redundancy, key info buried

### 4. Skill Cohesion

**Question:** Does every part of the skill serve the core intent?

| Aspect | Test |
|--------|------|
| Scope alignment | Would removing any section weaken the outcome? |
| Consistent voice | Is tone and terminology consistent throughout? |
| Single purpose | Does the skill do one thing well vs. many things poorly? |
| Structural fit | Does file organization match classification (utility/workflow/complex)? |

**Scoring:**
- **Strong** — Tight focus, everything serves the outcome
- **Adequate** — Minor scope creep, mostly focused
- **Weak** — Multiple purposes, structural mismatch

### 5. Enhancement Opportunities

**Question:** What specific improvements would have the highest impact?

| Category | Look For |
|----------|----------|
| Missing judgment calls | Decisions where agent would default wrong without guidance |
| Unnecessary content | Steps an LLM would do correctly unsupervised |
| Structural improvements | Reordering, progressive disclosure, quick reference tables |
| Cross-reference gaps | Skills that should reference each other |
| Discovery improvements | Better name, description, or keywords for searchability |

## Track 3: Report Synthesis

Combine lint and judgment findings into an actionable report.

### Report Template

```
## Quality Analysis: [skill-name]

### Lint Results
[PASS/FAIL for each check, with specifics]

### Judgment Dimensions
| Dimension | Score | Top Issue |
|-----------|-------|-----------|
| Workflow Integrity | [Strong/Adequate/Weak] | [biggest problem] |
| Prompt Craft | [Strong/Adequate/Weak] | [biggest problem] |
| Execution Efficiency | [Strong/Adequate/Weak] | [biggest problem] |
| Skill Cohesion | [Strong/Adequate/Weak] | [biggest problem] |

### Themes
[2-3 recurring patterns across dimensions]

### Top 3 Actions (highest impact first)
1. [Action] — [Expected improvement]
2. [Action] — [Expected improvement]
3. [Action] — [Expected improvement]
```

**Present report to user. Discuss priorities. Offer to implement changes.**