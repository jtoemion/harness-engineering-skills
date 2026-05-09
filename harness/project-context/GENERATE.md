# Generate Project Context

**Trigger:** User says "project context" and no project-context.md exists

## Process

```
1. CHECK if project-context.md already exists
   - IF exists → show location and prompt to update or view
   - IF not exists → continue

2. DISCOVER project structure
   - Tech stack detection (package.json, requirements.txt, Cargo.toml, etc.)
   - Key directories (src/, lib/, components/, etc.)
   - Framework conventions

3. ASK discovery questions (one at a time):
   a. "What tech stack and versions should I know about?"
   b. "What are the MUST-do rules for this codebase?"
   c. "What are the MUST-NOT-do rules?"
   d. "What naming conventions should I follow?"
   e. "What common patterns are used?"
   f. "What architectural decisions should I know about?"
   g. "What API conventions exist?"
   h. "What testing requirements exist?"
   i. "What gotchas or pitfalls should I avoid?"

4. GENERATE project-context.md from answers

5. SAVE to project root

6. MIRROR to Obsidian:
   - 00_HUMAN/02_Projects/[NAME]/Context/project-context.md

7. OUTPUT location + confirmation
```

---

## Discovery Questions (if user needs prompting)

```
1. Tech Stack:
   "What technologies and versions does this project use?
    (e.g., React 19, TypeScript 5, Node 20, PostgreSQL 15)"

2. Critical Rules:
   "What are 3-5 rules AI agents MUST follow in this codebase?
    (e.g., 'Always use TypeScript types', 'Never use console.log')"

3. Gotchas:
   "What common mistakes should AI agents avoid?
    (e.g., 'API returns null for empty arrays', 'Auth token expires in 1hr')"

4. Patterns:
   "What code patterns are used here?
    (e.g., 'Repository pattern for data access', 'Custom hooks for state')"

5. Architecture:
   "What are the key architectural decisions?
    (e.g., 'Firebase for auth', 'Microservices via REST')"
```

---

## Output Location

- Primary: `{project_root}/project-context.md`
- Mirror: `Obsidian: 00_HUMAN/02_Projects/[NAME]/Context/project-context.md`

---

## Success Confirmation

```
⚡ PROJECT CONTEXT GENERATED
  Location: {project_root}/project-context.md
  Obsidian: Synced ✓
  Sections: [N] completed
  Next: To use, run "project context" to view or update
```