---
name: knowledge-graph
description: Graph intelligence — surface mistakes, patterns, decisions across projects using [[wiki-links]] and YAML frontmatter
quick_ref:
  boot: "graph_surface(project, context) → relevant knowledge at boot"
  mistakes: "graph_mistakes(project, category) → find relevant mistakes"
  patterns: "graph_patterns(stack) → find patterns for tech stack"
  decisions: "graph_decisions(domain) → find past decisions"
  related: "graph_related(note_id) → follow all [[links]]"
  cluster: "graph_cluster(project) → show knowledge clusters"
---

# KNOWLEDGE-GRAPH — Graph Intelligence

## Overview

Navigate the Obsidian knowledge graph for cross-project intelligence. Works by following `[[wiki-links]]` and filtering YAML frontmatter.

**Dependency:** Uses `vault-ops` for all file operations. Knowledge-graph adds intelligence on top — it knows WHERE to look and WHAT to surface.

**See also:** `harness/VAULT_SCHEMA.md` for note types and folder structure.

## When to Use

- **At boot:** Call `graph_surface()` to surface relevant knowledge before starting work
- **Before implementing:** Call `graph_mistakes()` to check if similar mistakes have occurred
- **When encountering a pattern:** Call `graph_patterns()` to see if it's been observed before
- **When making a decision:** Call `graph_decisions()` to find precedent
- **When debugging:** Call `graph_related()` to trace the full graph around a mistake or pattern

---

## Operations

### graph_surface(project, context)

Called during boot (Phase 1, after vault load). Returns prioritized knowledge for the current session.

**graph_surface:** Define the EXACT boot-time knowledge surfacing sequence.

**Sequence (executed in order):**
1. **Load local active mistakes** — `vault_query(VAULT_MISTAKES, "mistake", {status: "ACTIVE"})`
2. **Load global matching mistakes** — `vault_query(GLOBAL_VAULT, "mistake", {category: project.category})` — all categories first, then filter by slug similarity
3. **Load global matching patterns** — `vault_query(GLOBAL_VAULT, "pattern", {applies_to: project.stack})` — any stack item match counts
4. **Load latest session** — `vault_query(VAULT_SESSIONS, "session", {})` sorted by date DESC, limit 1
5. **Rank results** — category match (+3), stack match (+2), recency bonus (+1 if <7 days)
6. **Limit output** — top 5 mistakes, top 5 patterns, latest session

**Ranking formula:** `score = (category_match ? 3 : 0) + (stack_match ? 2 : 0) + (recency_bonus ? 1 : 0)`

**Presentation format:**
```
📊 SURFACED KNOWLEDGE
  Mistakes (local): 2 ACTIVE
    - BMW-M003: CORS per-route assumption
    - BMW-M001: Express middleware ordering
  Mistakes (global): 1 relevant
    - N8-M002: Similar CORS issue in n8n setup
  Patterns (global): 2 relevant
    - BMW-P001 → FW-P002: Middleware scope pattern
  Recent session: 2026-04-23-auth-middleware (PARTIAL)
```

### graph_mistakes(project, category)

Find relevant mistakes locally and globally.

**graph_mistakes:** Define the category matching table and slug deduplication.

**Category matching table:**
| Project Category | Global Mistake Categories Matched |
|------------------|-----------------------------------|
| `backend` | `backend`, `api`, `database`, `auth` |
| `frontend` | `frontend`, `ui`, `css`, `state` |
| `infra` | `infra`, `docker`, `cloud`, `cicd` |
| `fullstack` | all categories |
| `script` | `script`, `automation`, `cli` |
| `ml` | `ml`, `data`, `model`, `training` |

**Slug similarity algorithm (for deduplication):**
1. Extract slug from note ID (e.g., `BMW-M003` → `m003`)
2. Normalize: lowercase, strip prefix
3. Compute Levenshtein distance between slugs
4. If distance ≤ 3 AND same category: mark as duplicate
5. Prefer local note over global (local = authoritative for project)

**Steps:**
1. `vault_query(VAULT_ROOT, "mistake", {status: "ACTIVE"})` — all active in project
2. If category specified: filter by `category` frontmatter field (see matching table above)
3. `vault_query(GLOBAL_VAULT, "mistake", {category: category})` — global
4. Merge results, deduplicate by slug similarity
5. For each mistake, extract `[[links]]` from body
6. Return: array of `{ id, error, cause, lesson, related_notes }`

### graph_patterns(stack)

Find patterns relevant to the project's tech stack.

**graph_patterns:** Document how applies_to matching works.

**applies_to matching algorithm:**
- `applies_to` is a list (YAML array) of stack items, e.g., `["React", "Node", "MongoDB"]`
- If project has multiple stack items, pattern MATCHES if ANY stack item appears in applies_to
- Matching is case-insensitive substring match
- Pattern score = number of stack items matched (higher = more valuable)

**Examples:**
| Project Stack | Pattern applies_to | Match? |
|---------------|---------------------|--------|
| `["React"]` | `["React", "TypeScript"]` | YES (1 match) |
| `["React", "Node"]` | `["React", "TypeScript"]` | YES (1 match) |
| `["React", "Node"]` | `["Node", "MongoDB"]` | YES (1 match) |
| `["Python"]` | `["React", "TypeScript"]` | NO |

**Steps:**
1. `vault_query(VAULT_ROOT, "pattern", {})` — all local patterns
2. `vault_query(GLOBAL_VAULT, "pattern", {applies_to: stack})` — global
3. Sort by `length(applies_to)` — patterns observed in more projects are more valuable
4. For each pattern, extract `[[links]]` from body
5. Return: array of `{ id, pattern, observed_in, prevention, related_notes }`

### graph_decisions(domain)

Find past decisions for a similar problem domain.

**Steps:**
1. `vault_query(VAULT_ROOT, "decision", {domain: domain, status: "active"})` — local active
2. `vault_query(GLOBAL_VAULT, "decision", {domain: domain})` — global
3. Sort by recency
4. Return: array of `{ id, context, decision, rationale, alternatives }`

### graph_related(note_id)

Follow all `[[wiki-links]]` from a note, 2 levels deep. Builds a neighborhood subgraph.

**graph_related:** Document the traversal algorithm.

**Traversal algorithm:**
```
LEVEL 0 (center):  note_id
LEVEL 1 (direct): all notes linked from center
LEVEL 2 (indirect): all notes linked from level1 notes (excluding center)

visited = Set(center)          // prevent loops at level 2
level1 = []
level2 = []

FOR each link IN center.body.links:
    level1.append(link)         // direct links

FOR each note IN level1:
    visited.add(note.id)
    FOR each link IN note.body.links:
        IF link NOT IN visited: // avoid infinite loops
            level2.append(link)

RETURN { center, level1, level2 }
```

**Infinite loop prevention:** Track visited IDs in a Set. Level 2 only includes notes NOT already visited.

**Steps:**
1. Locate note by ID in vault (scan all folders for matching `id` frontmatter)
2. Read note, extract all `[[links]]` from body
3. For each linked note, read and extract its `[[links]]`
4. Stop at 2 levels deep (avoid infinite traversal)
5. Return: graph neighborhood as `{ center, level1: [], level2: [] }`

### graph_cluster(project)

Show all knowledge clusters in a project vault. For Obsidian visualization.

**graph_cluster:** Document the Obsidian visualization output format.

**Output format for Obsidian visualization:**
```
KNOWLEDGE_CLUSTER: {project_code}
  nodes:
    - id: BMW-M001
      type: mistake
      category: backend
      label: "Express middleware ordering"
    - id: BMW-P001
      type: pattern
      category: backend
      label: "Middleware scope pattern"
    - id: BMW-D003
      type: decision
      domain: auth
      label: "JWT vs Session decision"
    - id: 2026-04-23-auth
      type: session
      label: "Auth middleware session"
  edges:
    - from: BMW-M001
      to: BMW-P001
      rel: leads_to
    - from: BMW-M001
      to: BMW-D003
      rel: resolved_by
    - from: 2026-04-23-auth
      to: BMW-M001
      rel: encountered
```

**Steps:**
1. `vault_query(VAULT_ROOT, "mistake", {})` — all mistakes
2. `vault_query(VAULT_ROOT, "pattern", {})` — all patterns
3. `vault_query(VAULT_ROOT, "decision", {})` — all decisions
4. `vault_query(VAULT_ROOT, "session", {})` — all sessions
5. Group by type, then by category
6. Return: `{ mistakes_by_category, patterns_by_category, decisions_by_domain }`

---

## Integration Points

| Boot Phase | Operation | Purpose |
|-----------|-----------|---------|
| Boot → `graph_surface` | Boot Phase 1 | Surface relevant knowledge at boot |
| Pre-implementation → `graph_mistakes` | Pre-implementation | Check for past failures |
| Post-implementation → `graph_patterns` | Post-implementation | Record observed patterns |
| Decision point → `graph_decisions` | Decision point | Find precedent |
| Debugging → `graph_related` | Debugging | Trace failure chains |
| Session close | — | session-graph creates the notes that knowledge-graph reads |

---

## Anti-Rationalization

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Just grep for it" | Knowledge-graph follows [[links]] to build neighborhoods, not just text search |
| "Only check local mistakes" | Cross-project patterns are the whole point of the global vault |
| "Skip graph_surface at boot" | Surfaces critical context — mistakes, patterns, recent sessions |
| "Resolved mistakes don't matter" | They prevent repeating the same mistake see tombstone pattern in VAULT_SCHEMA |