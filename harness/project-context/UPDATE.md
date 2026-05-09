# Update Project Context

**Trigger:** User says "update project context" or significant change occurred

## When to Update

| Event | Update Action |
|-------|---------------|
| New architectural decision | Add to Architecture Decisions |
| Bug discovered (gotcha) | Add to Known Gotchas |
| Pattern established | Add to Common Patterns |
| Naming convention change | Update Naming Conventions |
| Tech stack upgrade | Update Technology Stack |
| New API endpoint pattern | Update API Conventions |
| Testing requirement change | Update Testing Requirements |

---

## Process

```
1. CHECK if project-context.md exists
   - IF not → generate instead (see GENERATE.md)
   - IF exists → continue

2. SHOW current project-context.md sections

3. ASK what section to update:
   "Which section needs updating?
    1. Technology Stack & Versions
    2. Critical Implementation Rules
    3. Naming Conventions
    4. Common Patterns
    5. Architecture Decisions
    6. API Conventions
    7. Testing Requirements
    8. Known Gotchas"

4. PROMPT for specific change:
   "What should be added/changed in [section]?"

5. UPDATE the section

6. SAVE project-context.md

7. MIRROR to Obsidian

8. OUTPUT confirmation
```

---

## Compact Update (Single Gotcha)

If user discovered a bug pattern:

```
1. ASK: "What gotcha should I know about?"
2. ASK: "Why does this cause problems?"
3. ADD to Known Gotchas section:
   - **Gotcha**: [description]
   - **Problem**: [why it's an issue]
   - **Workaround**: [how to avoid it]
4. SAVE + MIRROR
5. OUTPUT: "Gotcha added to project-context.md"
```

---

## Migration from Another Tool

If onboarding from Claude/Cursor/Gemini:

```
1. EXPORT context from existing tool (if possible)
2. MERGE with project-context.md sections
3. FOCUS on:
   - Tech stack (verify still accurate)
   - Critical rules (transcribe)
   - Gotchas (transcribe from lessons learned)
   - Patterns (transcribe from codebase examples)
4. VALIDATE with user
5. SAVE + MIRROR
```