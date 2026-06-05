# Techne Setup Reference

Techne = Judah's remote skill library. Lives at `github.com/jtoemion/techne`.

## Setup

```bash
git clone https://github.com/jtoemion/techne.git ~/techne
ln -s ~/techne/skills/writing-skill ~/.hermes/skills/writing-skill
```

## What's in techne

```
techne/
  SKILL.md                    ← main entry
  skills/
    writing-skill/            ← symlinked to ~/.hermes/skills/writing-skill
      template.md             ← copy-paste scaffold
      checklist.md            ← pre-publish validation
    tdd.md / tdd/
    diagnose.md / diagnose/
    grill.md
    persona-brainstorm.md / persona-brainstorm/
    implementer.md
    nextjs.md / typescript.md
    ...
  harness/                    ← runtime enforcement
  memory/
  docs/
```

## Key skill: writing-skill

Newspaper inverted pyramid:
- **HEADLINE** → frontmatter (name, description, triggers)
- **LEAD** → most critical rule or quick-start (first section)
- **BODY** → examples, patterns, soft rules
- **TAIL** → `## Next Steps` chain (mandatory last)

Line limits: entry card ≤ 100 lines, sub-skill ≤ 150 lines.

## Techne vs superpowers/writing-skills

Techne's writing-skill is the canonical one for this agent. `superpowers/writing-skills` is the TDD-flavored version (RED-GREEN-REFACTOR for documentation). Use techne's for new skill authoring; superpowers version is historical reference.