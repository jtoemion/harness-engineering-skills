# Full Scan Workflow

For `initial_scan` and `full_rescan` modes. Produces complete project documentation.

## Quick Start

1. **Start enforcement**: `python enforce.py start --mode <mode> --level <level>`
2. Complete each phase per the steps below
3. After each phase: `python enforce.py done <phase>`
4. After phase 6: `python enforce.py validate && python enforce.py anchor-check`

## Newspaper Logic (Required for ALL Output Files)

Every output file must follow these principles:

| Principle | Meaning |
|-----------|---------|
| **Lede first** | First 3 lines tell an AI what it MUST know. No preamble. |
| **Inverse pyramid** | Most critical info first. Details deeper. |
| **Scannable** | Dense tables, short anchors, bold leads. No prose paragraphs. |
| **Non-linear** | Each section independently actionable. AI can drop in at any anchor. |
| **Inline the hard stuff** | The most violated rule should appear verbatim in the file — not behind a link. |

**Zero-tolerance rules:**
- No `TODO`, `TBD`, `placeholder`, or unfilled content
- No flat lists where tables would serve better
- No prose where a table serves better
- Technology classifications must be `core | infrastructure | inactive | planned` — not just listed
- Constraints go at the top, not buried mid-file

---

## Phases

Execute sequentially. Write each output file immediately after its phase completes (write-as-you-go).

### Phase 1: Project Detection

**Goal**: Identify project type, purpose, and boundaries.

**Steps**:
1. Read top-level files: README, package.json, Cargo.toml, pyproject.toml, go.mod, etc.
2. Scan directory structure (top two levels only)
3. Apply detection rules in priority order:
   - **Mobile**: Look for `android/`, `ios/`, `app.json` (Expo), `pubspec.yaml` (Flutter), `.xcodeproj`
   - **Desktop**: Look for Electron (`electron` in package.json), Tauri (`src-tauri/`), Qt (`.pro` files)
   - **Game**: Look for Unity (`Assets/`, `ProjectSettings/`), Unreal (`.uproject`), Godot (`project.godot`)
   - **Web App**: Look for HTML templates, React/Vue/Angular, `next.config`, `vite.config`, CSS frameworks
   - **API**: Look for Express/FastAPI/gRPC, OpenAPI/Swagger specs, no frontend templates
   - **Library**: Look for `exports`/`main` in package.json, `setup.py`/`pyproject.toml` with no entry point, lib-only structure
4. Determine scan level from user request (default: `deep`)
5. Write state file with detected type and scan level

**Output**: Write `project-overview.md`

**Newspaper format**:
```markdown
# Project Overview

## Lede
[3 lines: identity + primary stack + core purpose]
```

**After phase completes**: `python enforce.py done phase_1`

---

### Phase 2: Technology Stack

**Goal**: Catalog every technology, framework, and tool in use.

**Steps**:
1. Read dependency files (package.json, requirements.txt, go.sum, Gemfile, etc.)
2. Read config files (tsconfig, webpack, vite, docker, CI configs)
3. Classify each as: `core | infrastructure | development | testing | services | inactive | planned`
4. Structure as classified tables — NOT a flat list

**Output**: Append to `project-overview.md`

**Newspaper format**:
```markdown
## Tech Stack

**Core runtime**
- [bullet list]

**UI / interaction**
- [bullet list]

**Inactive / planned**
- [bullet list — explicitly mark inactive, explain why]
```

**Classification rules:**
- `core` = runtime dependencies the app cannot function without
- `infrastructure` = persistence, messaging, serverless
- `inactive` = declared in config but not wired to app logic (e.g., Docker services not yet used)
- `planned` = in the codebase but not yet active

**After phase completes**: `python enforce.py done phase_2`

---

### Phase 3: Architecture

**Goal**: Document the project's architectural patterns and data flow.

**Steps**:
1. Identify entry points (main files, server files, index files)
2. Trace request/data flow from entry to response/output
3. Identify architectural pattern (MVC, microservices, monolith, layered, event-driven, etc.)
4. Map key modules and their responsibilities
5. Document inter-module communication
6. Note architectural decisions and their rationale
7. Document error handling patterns
8. Document authentication/authorization patterns

**Output**: Write `architecture.md`

**Newspaper format** — structure MUST be:
```markdown
# Architecture

## Lede
[3 lines: project type + 2 hardest architectural rules]

---

## Layer Reference (inline)
[layer diagram — inline, not behind a link]

---

## Entry Points
[main.tsx → App.tsx flow + compact routes table]

---

## Data Flow

---

## Authentication Patterns
### Google OAuth
### PIN Login
### Anonymous Proxy Pattern
[getRealUserId() rule verbatim if applicable]

---

## Key Modules

---

## Error Handling

---

## Architectural Decisions
```

**Section anchors required**: `#overview`, `#entry-points`, `#data-flow`, `#authentication-patterns`, `#anonymous-proxy-pattern`, `#key-modules`, `#error-handling`, `#architectural-decisions`

**After phase completes**: `python enforce.py done phase_3`

---

### Phase 4: Source Tree

**Goal**: Produce an annotated directory structure showing what each directory and key file contains.

**Steps**:
1. Generate full directory tree (respect .gitignore)
2. Annotate each directory with its purpose
3. Annotate key files (entry points, configs, main modules)
4. For quick scan: top 3 levels + key files
5. For deep scan: full tree + annotations on all source dirs
6. For exhaustive scan: full tree + annotation on every source file

**Output**: Write `source-tree.md`

**Newspaper format**: Tree with dense annotations, not prose descriptions. Summary table at bottom.

**After phase completes**: `python enforce.py done phase_4`

---

### Phase 5: Development Guide

**Goal**: Document how to set up, build, test, and deploy the project.

**Steps**:
1. Read setup instructions (README, CONTRIBUTING, Makefile, scripts/)
2. Document prerequisites, env setup, build, test, lint, deploy commands
3. Document common development workflows
4. **Gotchas MUST be in a table** — not buried at the bottom

**Output**: Write `dev-guide.md`

**Newspaper format**:
```markdown
# Development Guide

## Lede
[2-3 lines: what it is + prereqs + the ONE command to get running]

---

## Prerequisites
## Setup
### Environment Variables
### Firebase Setup
## Commands
[code blocks]
## Testing
## Deployment
## Adding New Code
### New Page/Route
### New Service/DAL
## Gotchas
[Table: gotcha | what it means | don't do this]
```

**Gotchas table MUST be present** — if you found no gotchas during scan, document that explicitly ("No unexpected gotchas found during scan").

**After phase completes**: `python enforce.py done phase_5`

---

### Phase 6: Context Root

**Goal**: Generate `CONTEXT.md` at project root — the single AI entry point.

**Prerequisite**: All other docs must exist before this phase runs.

**Steps**:
1. Verify all Phase 1-5 output files exist
2. Read a summary of each (not full content)
3. Generate `CONTEXT.md` with the **newspaper-lede template** below
4. Budget: ≤4,000 tokens total
5. Use section anchors (`#anchor`), not line numbers
6. Extract any section >1,000 tokens to `deep-dives/` and link to it instead

**Output**: Write `CONTEXT.md` at project root

**CONTEXT.md newspaper-lede template**:
```markdown
# PROJECT CONTEXT

> [Line 1: What it is + type]
> HARD RULE: [Line 2: The single hardest architectural rule]
> HARD RULE: [Line 3: The second hardest rule — or the auth/data quirk]

---

## Critical Constraints (read before writing any code)

| Constraint | What it means |
|---|---|
| [constraint] | [what it means — one actionable row per constraint] |

---

## Tech Stack

**Core runtime**
[bullet list]

**UI / interaction**
[bullet list]

**Inactive / planned**
[bullet list — explicitly mark inactive]

---

## Entry Points (one per topic)

| Topic | Go to |
|---|---|
| [topic] | [path → #anchor] |

---

## Layer Reference (inline)

[layer diagram inline]
```

**Rules for CONTEXT.md:**
- Ledé = 3 lines: identity + 2 HARD rules. These are the rules most likely to cause bugs if violated.
- Constraints table: one row per constraint, independently actionable
- Tech stack: classified (`core | UI | inactive | planned`), not flat
- Entry points: ONE link per topic, each pointing to the most specific doc. NO 8 links to the same file.
- Remove "Deep Dives Available" section — it adds nothing new.
- Layer diagram: inline, not behind a link. The most-violated rule should not require opening another file.

**After phase completes**: `python enforce.py done phase_6 && python enforce.py validate && python enforce.py anchor-check`

---

## Write-As-You-Go Architecture

**Rule**: After completing each phase, immediately write its output file. Do NOT accumulate context.

**Rationale**: Large projects generate more context than can fit in a single session. Writing as you go:
- Prevents context overflow
- Creates natural checkpoint points
- Enables resumability if session is interrupted
- Keeps each phase's context window clean

**Pattern**:
```
For each phase:
  1. Read only what's needed for this phase
  2. Process and analyze
  3. Write output file immediately
  4. Update state file
  5. Proceed to next phase (previous context can be released)

Phase 6 (CONTEXT.md) runs last, after all other docs exist.
```

---

## Resumability

State file (`.docs/.scan-state.json`) tracks progress:

- `phase`: Current phase name
- `completed_phases`: Phases with output files written
- `files_written`: Output files that exist on disk
- `scan_level`: Quick/Deep/Exhaustive
- `project_type`: Detected type

**To resume**:
1. Read state file
2. Verify completed phases by checking files exist on disk
3. Resume from the next incomplete phase
4. Continue write-as-you-go pattern

---

## Full Rescan Differences

When mode is `full_rescan`:
1. Read existing `.docs/` files and `CONTEXT.md` first
2. Note what changed since last scan (check file timestamps)
3. Re-run all phases (apply newspaper logic to all files, not just CONTEXT.md)
4. Phase 6 regenerates `CONTEXT.md` from updated docs
5. Preserve deep-dive docs — they still apply unless user says otherwise
6. Verify all anchors in regenerated `CONTEXT.md` resolve to actual section headers
7. Update state file status to `complete` and save timestamp
