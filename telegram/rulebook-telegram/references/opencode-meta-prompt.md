# OpenCode Meta-Prompt Reference

## Meta-Prompt Composition (Telegram context)

When a task requires websearch or webfetch, compose the meta-prompt for opencode like this:

```markdown
[Identity block]
You are [agent role]. Task: [concrete goal].

[Constraints block]
- Only use web search/fetch if the task requires real-time info
- Return findings as structured markdown
- Do NOT add commentary beyond what's requested

[Task block]
[Full task description from user, verbatim where possible]

[Context block]
Project: [project name]
Repo: [github.com/jtoemion/X]
Stack: [relevant stack if known]
```

## opencode CLI invocation

```bash
opencode --prompt "..."
# or for multi-line:
opencode <<'EOF'
[paste meta-prompt]
EOF
```

## Return handling

OpenCode returns stdout. Parse it, strip excessive whitespace, present to user. If the output is long (> 5 paragraphs), offer as file attachment rather than inline.

## Anti-patterns

- Don't wrap the entire Telegram message as the prompt — extract the actual task, drop conversational filler
- Don't use opencode for local file operations — only for web search/fetch
- Don't chain opencode calls without presenting the first result to the user first