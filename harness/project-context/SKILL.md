---
name: project-context
description: Generate and maintain project-context.md - persistent AI rules and patterns for this codebase.
quick_ref:
  purpose: "Capture unobvious rules/gotchas that AI agents need to remember"
  trigger: "User says 'project context' or 'generate context' or '.context'"
  update_trigger: "Onboarding new project, significant architectural decision, pattern discovery"
---

# Project Context Generator

**Purpose:** Create and maintain `project-context.md` — a persistent file containing critical rules, patterns, and gotchas that AI agents need to follow when working in this codebase.

**Why:** Unlike session memory (which resets), project-context persists across sessions and captures institutional knowledge about the codebase.

## FILES

| File | Purpose |
|------|---------|
| `SKILL.md` | This index |
| `project-context.yaml` | Quick reference |
| `GENERATE.md` | Generation workflow |
| `UPDATE.md` | Update workflow |
| `project-context-template.md` | Template structure |

## OBSIDIAN MIRROR

```
Project: project-context.md → 00_HUMAN/02_Projects/[NAME]/Context/project-context.md
```

---

## TRIGGERS

| Trigger | Action |
|---------|--------|
| User says "project context" / "generate context" / ".context" | Generate or show existing |
| New project onboarding | Generate |
| Significant architectural decision | Update |
| Pattern discovery (gotcha found) | Update |

---

## PROJECT CONTEXT FILE STRUCTURE

```markdown
# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow.
Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

_Version info that affects implementation_

---

## Critical Implementation Rules

_Gotchas, must-follow patterns, forbidden patterns_

---

## Naming Conventions

_File naming, function naming, etc._

---

## Common Patterns

_Code patterns used in this codebase_

---

## Architecture Decisions

_ADRs, key decisions with rationale_

---

## API Conventions

_How API calls, requests, responses are structured_

---

## Testing Requirements

_Test coverage minimums, testing patterns_

---

## Known Gotchas

_Things that have caused bugs before_
```

---

## OBSIDIAN FOOTBALL NEWS VAULT — ENFORCED RULES

**Applies to:** `C:\Users\jtoem\Assets\News\football\`

When working with this vault, the following rules are MANDATORY and cannot be overridden:

### 1. FLAT STRUCTURE — NO PREFIXES
- Directory IS the category. No `NATION-`, `CLUB-`, `LEAGUE-`, `COMP-`, `PLAYER-` prefixes.
- ✅ Correct: `Nations/Argentina.md`, `Clubs/Arsenal-FC.md`, `Leagues/Premier-League.md`
- ❌ Wrong: `Nations/NATION-Argentina.md`, `Clubs/CLUB-Arsenal-FC.md`

### 2. WIKILINKS BARE
- Wikilinks reference bare names, not paths. The directory context is self-evident.
- ✅ Correct: `[[Manchester-City]]`, `[[Arsenal-FC]]`, `[[Argentina]]`
- ❌ Wrong: `[[Clubs/Manchester-City]]`, `[[Nations/Argentina]]`

### 3. FRONTMATTER ORDER: WIKILINKS FIRST, TAGS SECOND
- `entities:` array BEFORE `tags:` array in ALL notes.
- ✅ Correct:
  ```yaml
  entities:
    - "[[Arsenal-FC]]"
    - "[[Eddie-Howe]]"
  tags: [news, arsenal, premier-league]
  ```
- ❌ Wrong: `tags:` before `entities:`

### 4. NEW ENTITY → DEDICATED FOLDER
- If an entity (person, player, concept, club, league) does not exist in the vault, create it in the appropriate folder immediately. Do NOT skip or leave dangling wikilinks.
- Folder map:
  - `Persons/` — managers, coaches, pundits, owners, referees
  - `Players/` — footballers (active players)
  - `Concepts/` — abstract: Title-Race, Relegation, Transfer, Racism, Injury, etc.
  - `Nations/` — country/national team
  - `Clubs/` — football clubs
  - `Leagues/` — domestic leagues
  - `Competitions/` — cups, tournaments

### 5. NEWS NOTE STRUCTURE (mandatory for all inbox/scraped articles)
```markdown
---
type: news
date: YYYY-MM-DD
source: {Source}
url: {URL}
processed: true
entities:
  - "[[Entity1]]"
  - "[[Entity2]]"
tags: [news, tag1, tag2, tag3]
---

## Summary
{3-4 sentence summary with wikilinks inline to EVERY entity mentioned}
```

### 6. SCRAPE ARTICLES — FULL CONTENT + URL
- ALWAYS fetch FULL article text, not just headlines or summaries.
- ALWAYS include the `url:` field with source URL.
- ALWAYS wikilink every named entity in the summary body.
- If entity is new (not in vault) → create the entity file first, THEN use in news note.

---

## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "I already know the project rules" | You don't after session reset. Context file prevents repeat mistakes. |
| "Skip project context, I'll remember" | You won't. That's the point. |
| "Just use common sense" | Common sense varies. Explicit rules prevent drift. |
| "Tags first is fine" | No — entities come first, tags second. Hardcoded rule. |
| "I'll add the entity later" | Create it NOW. No dangling wikilinks. |
| "Just headline is enough" | Full article, full URL, full wikilinks. Every time. |