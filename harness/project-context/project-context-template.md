# Project Context Template

```markdown
# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when
implementing code in this project. Focus on unobvious details that agents might
otherwise miss. Update this file when architectural decisions change or new
patterns are discovered._

---

## Technology Stack & Versions

| Component | Version | Notes |
|-----------|---------|-------|
| [e.g., React] | [version] | [any notes] |
| [e.g., Node] | [version] | [any notes] |
| [e.g., PostgreSQL] | [version] | [any notes] |

---

## Critical Implementation Rules

### MUST DO
- [Rule 1]
- [Rule 2]
- [Rule 3]

### MUST NOT DO
- [Forbidden pattern 1]
- [Forbidden pattern 2]
- [Forbidden pattern 3]

---

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | [e.g., PascalCase.tsx] | `UserProfile.tsx` |
| Functions | [e.g., camelCase] | `getUserData()` |
| Variables | [e.g., camelCase] | `userName` |
| Constants | [e.g., UPPER_SNAKE] | `MAX_RETRIES` |
| Components | [e.g., PascalCase] | `DashboardCard` |
| Hooks | [e.g., use prefix] | `useAuth()` |

---

## Common Patterns

### [Pattern Name 1]
**Usage:** When [situation]
**Code:**
\`\`\`[language]
[example code]
\`\`\`

### [Pattern Name 2]
**Usage:** When [situation]
**Code:**
\`\`\`[language]
[example code]
\`\`\`

---

## Architecture Decisions

### [ADR-001]: [Title]
**Date:** [YYYY-MM-DD]
**Decision:** [What was decided]
**Rationale:** [Why this approach]
**Alternatives Considered:** [What else was considered]

### [ADR-002]: [Title]
...

---

## API Conventions

### Request Format
\`\`\`[format]
[example request structure]
\`\`\`

### Response Format
\`\`\`[format]
[example response structure]
\`\`\`

### Error Handling
[How errors are returned and handled]

### Authentication
[Auth mechanism and headers]

---

## Testing Requirements

| Type | Coverage Minimum | Location |
|------|-----------------|----------|
| Unit Tests | [e.g., 80%] | `./tests/unit/` |
| Integration Tests | [e.g., 50%] | `./tests/integration/` |
| E2E Tests | [e.g., critical paths] | `./tests/e2e/` |

**Testing Commands:**
\`\`\`bash
[npm test / pytest / cargo test]
\`\`\`

---

## Known Gotchas

### [Gotcha Title]
**Problem:** [What goes wrong]
**Cause:** [Why it happens]
**Workaround:** [How to avoid/fix]
**References:** [file:line if applicable]

### [Gotcha Title]
**Problem:** [What goes wrong]
**Cause:** [Why it happens]
**Workaround:** [How to avoid/fix]

---

## Project-Specific Notes

[Any additional context that doesn't fit above sections]

---

_Last Updated: [YYYY-MM-DD]_
_Maintained By: [name/role]_
```