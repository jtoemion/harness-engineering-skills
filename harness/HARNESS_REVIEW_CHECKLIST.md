# Harness Review Checklist

Trigger: Model upgrade OR every 10 sessions

## Components to Review

| Component | Assumption Encoded | Review Trigger | Last Review |
|-----------|-------------------| ---------------|------------|
| Sprint contract | Agent cannot self-evaluate | Model upgrade | TBD |
| Evaluator prompts | Skeptical evaluation needed | Model upgrade | TBD |
| Init scripts | App requires X startup | Architecture change | TBD |
| Subagent routing | Subagents act as context firewalls | Model upgrade | TBD |
| Mistake tracking | Errors repeat without tracking | Every 10 sessions | TBD |
| Memory schemas | Memory files provide orientation | Model upgrade | TBD |

## Review Process

1. Load `MISTAKES.md` and identify patterns
2. Check each component's tagged assumption
3. Test each component with current model
4. Strip or replace non-load-bearing components
5. Update `HARNESS_STATE.md` with review date

## Staleness Indicators

- Component produces errors it didn't before
- Subagent briefs no longer effective
- Memory format causes confusion
- Sprint contract rejected by agent
