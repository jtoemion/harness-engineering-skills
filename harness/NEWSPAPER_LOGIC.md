# Newspaper Logic — Document Format Standard

**Purpose**: Every document section follows headline-first structure to maximize scanability and reduce context bloat.

## Template

Every document section MUST follow this format:

```markdown
## HEADLINE: [One-line description]

> SUMMARY: [One sentence with the essential takeaway]

<details>
<summary>Details</summary>

- Specific fact 1
- Specific fact 2
- Specific fact 3 (maximum 3 key facts per collapsed section)
- Cross-reference: See [Other Section]

</details>
```

## Rules

1. **HEADLINE first**: Every section starts with a one-line headline that tells you everything essential
2. **SUMMARY second**: One sentence. If you read nothing else, read the summary
3. **Details collapsed**: Specifics go in `<details>` blocks — expandable on demand
4. **Max 3 facts per section**: If you need more, split into sub-sections
5. **Cross-reference, don't duplicate**: Link to other sections instead of repeating content
6. **No preamble**: Start with the headline, not "In this section we will..."

## When to Apply

- `systemPatterns.md` retrospective entries
- `document-project` output files
- `.memory/insights.md` entries
- Any file that grows past 500 lines

## Anti-Rationalization

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "This makes docs too terse" | Terse > bloated. Agents lose context on long docs. |
| "I need 10 bullet points" | Split into 3 sub-sections of 3 each. |
| "Details blocks are annoying" | They save 80% of context window. That's the point. |
| "This doesn't apply to code" | Correct. This is for DOCUMENTS and KNOWLEDGE files only. |
