---
name: workflow-builder
description: Use when building, analyzing, or converting workflow skills — outcome-driven design through conversational discovery
quick_ref:
  purpose: "Build, analyze, or convert workflow/skill structures through outcome-driven design"
  trigger: "build a workflow | create a skill | quality check workflow | convert a skill"
  modes: "build | analyze | convert"
---

# Workflow & Skill Builder

Outcome-driven design for workflow skills through conversational discovery.

**Core principle:** Every instruction describes WHAT outcome to achieve, not HOW to achieve it. If an LLM would do it correctly without being told — cut it.

## When to Use

- Building a new workflow or skill from scratch
- Analyzing an existing skill for quality gaps
- Converting a skill to outcome-driven format
- Modifying a workflow that isn't performing well

**NOT for:** TDD-based skill creation (use `writing-skills` for that).

## Modes

| Mode | Command | Reference |
|------|---------|-----------|
| **Build** | "build a workflow" / "create a skill" | BUILD_PROCESS.md |
| **Analyze** | "quality check workflow" / "analyze skill" | QUALITY_ANALYSIS.md |
| **Convert** | "convert a skill" | CONVERT_PROCESS.md |

## Routing

```
User request → Identify intent → Load reference → Execute phase-by-phase
   │                │                  │                │
   │                ├── "build"    → BUILD_PROCESS.md  → Phase 1-6
   │                ├── "analyze"  → QUALITY_ANALYSIS.md → Lint + Judge
   │                └── "convert"  → CONVERT_PROCESS.md → Capture → Rebuild
   │
   └── Ambiguous? Ask: "Build new, analyze existing, or convert?"
```

## Key Principles

1. **Outcome over instruction** — Describe the destination, not every turn
2. **Pruning** — "Would the LLM do this correctly without being told?" If yes, cut it
3. **Conversational discovery** — Build through dialogue, not assumptions
4. **Progressive disclosure** — Front-load what matters, bury what doesn't
5. **Judgment calls** — Focus skill content on decisions the LLM would get wrong

## Skill Type Classification

| Type | Signals | Structure |
|------|---------|-----------|
| **Simple utility** | Single clear action, no branching | Flat SKILL.md, inline examples |
| **Simple workflow** | Sequential steps, light branching | SKILL.md + optional reference |
| **Complex workflow** | Multi-phase, conditional logic, judgment calls | SKILL.md + BUILD_PROCESS.md-style phases |

## Relationship to writing-skills

- **writing-skills** = TDD for skills (test → write → close loopholes)
- **workflow-builder** = Outcome-driven DESIGN (discover → classify → draft → prune → build)
- Use workflow-builder FIRST to design, then writing-skills to validate

## Anti-Patterns

- Writing HOW instructions when WHAT outcomes suffice
- Including steps an LLM already does correctly
- Skipping conversational discovery and guessing requirements
- Copying structure without rebuilding from intent