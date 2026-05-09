# Deep Dive Workflow

Exhaustive documentation of a specific project area. Not a scan mode — a focused deep-dive that produces detailed understanding of one subsystem, feature area, or architectural concern.

## When to Use

- User asks to "document the auth system", "deep dive on the API layer", "explain the data pipeline"
- A specific area needs more detail than the full scan provided
- Preparing to modify a complex subsystem (brownfield PRD preparation)

## Process

### Step 1: Target Area Selection

Identify what to deep-dive on. Confirm with user if ambiguous.

**Area examples**:
- A subsystem (authentication, payment processing, data pipeline)
- A layer (API layer, data access layer, UI layer)
- A feature area (user management, reporting, notifications)
- A cross-cutting concern (error handling, logging, caching, security)
- A module/package (a specific directory or set of related files)

**Output**: Define scope in writing — which directories, files, and concepts are in scope.

---

### Step 2: File Inventory

List every file in scope. No sampling.

1. Use glob patterns to find all relevant files
2. Categorize by type: source, test, config, documentation
3. Note file sizes and modification recency
4. Exclude generated files, vendor directories, build output

**Output**: Complete file list with categories.

---

### Step 3: Exhaustive File Review

Read every file in scope. No shortcuts.

**For each file**:
1. Read the complete file (no truncation, no skipping)
2. Document:
   - Purpose (what it does, not just what it claims to do)
   - Exports/API surface
   - Dependencies (what it imports/uses)
   - Dependents (what imports/uses it)
   - Key functions/classes and their responsibilities
   - State management patterns
   - Error handling patterns
   - Configuration dependencies
   - Test coverage status (if test file exists alongside)

**Rules**:
- NO sampling — read every file completely
- NO guessing — if code is unclear, read related files to understand
- NO placeholders — document what you actually find
- NO TODOs — complete the documentation in this session

**Write-as-you-go**: Write documentation for each file or logical group as you complete it. Do not accumulate.

---

### Step 4: Dependency Mapping

Trace how the target area connects to the rest of the project.

1. **Internal dependencies**: What this area imports from other project modules
2. **Internal dependents**: What other project modules import from this area
3. **External dependencies**: Third-party packages used
4. **Data dependencies**: What data flows in, through, and out of this area
5. **Configuration dependencies**: What config this area requires
6. **Runtime dependencies**: Services, databases, APIs this area connects to

**Output**: Dependency map (text-based diagram or structured list).

---

### Step 5: Pattern Documentation

Identify and document recurring patterns within the area.

1. **Code patterns**: Repeated structures, conventions, idioms
2. **Data patterns**: How data is created, transformed, stored, retrieved
3. **Error patterns**: How errors are raised, caught, and handled
4. **Testing patterns**: How tests are structured, what's tested, what's not
5. **Configuration patterns**: How config is managed within the area

**Output**: Pattern catalog with examples from actual code.

---

### Step 6: Implementation Guidance

Produce actionable guidance for working with this area.

1. **Modification guide**: Where to make common changes and what to update
2. **Extension points**: Where new functionality can be added
3. **Constraints**: Invariants, rules, or assumptions that must be maintained
4. **Testing guidance**: How to test changes in this area
5. **Common pitfalls**: Non-obvious gotchas based on actual code patterns

**Output**: Practical guide section.

---

## Output Format

Deep-dive output goes to `.docs/deep-dives/<area>.md`:

```markdown
# Deep Dive: <Area Name>

## Scope
<What's covered and why>

## File Inventory
<Complete list of files in scope>

## Architecture
<How this area is structured internally>

## Detailed Documentation
<File-by-file or module-by-module documentation>

## Dependency Map
<Internal, external, data, config, runtime dependencies>

## Patterns
<Code, data, error, testing, configuration patterns>

## Implementation Guidance
<Modification guide, extension points, constraints, testing, pitfalls>
```

## State Tracking

Update `.docs/.scan-state.json` with:

```json
{
  "mode": "deep_dive",
  "deep_dive_area": "<area>",
  "phase": "<current step>",
  "files_in_scope": ["<list>"],
  "started": "<timestamp>",
  "updated": "<timestamp>",
  "completed_steps": ["target_selection", "file_inventory"]
}
```

## Multiple Deep Dives

If user requests documentation of multiple areas:
- Run each as a separate deep-dive
- Each produces its own `.docs/deep-dives/<area>.md`
- Update `CONTEXT.md` (## Deep Dives Available section) to reference all deep-dive docs
- Shared dependencies between areas should be noted but not duplicated
