# Documentation Validation Checklist

Run after any documentation mode (initial_scan, full_rescan, deep_dive). Every item must pass.

## Newspaper Logic Compliance (All Output Files)

| Check | What it means | Fail if |
|-------|---------------|---------|
| **Ledé first** | First 3 lines of each file tell the AI what it MUST know | File opens with prose preamble |
| **Constraints at top** | Critical constraints appear before mid-file, not buried | Constraints only appear after long prose |
| **Tech stack classified** | Not a flat list — must be `core \| UI \| infrastructure \| inactive \| planned` | Flat bullet list with no classification |
| **Scannable tables** | Tables used for constraints, modules, gotchas — not prose paragraphs | Prose lists where tables would serve |
| **One link per topic** | Entry points point to most specific doc per topic — not N links to same file | Multiple links to same file with different anchors |
| **Inline hard stuff** | Most violated rules appear verbatim inline — not behind a link | Layer diagram, getRealUserId() requires opening another doc |
| **No "Deep Dives Available"** | CONTEXT.md does not repeat links from Entry Points | Section duplicates links already in Key Entry Points |

## Scan Level Completeness

- [ ] Scan level was explicitly chosen (quick/deep/exhaustive) or defaulted with user awareness
- [ ] All phases appropriate for the scan level were executed
- [ ] Quick scan: phases 1-3 completed (detection, stack, architecture at top-level)
- [ ] Deep scan: phases 1-6 completed (all phases, moderate depth)
- [ ] Exhaustive scan: phases 1-6 completed at full depth (every file reviewed)
- [ ] No phase was skipped due to time/context pressure (reduce scope instead)

## Write-As-You-Go Compliance

- [ ] Each output file was written immediately after its phase completed
- [ ] No phase accumulated context that wasn't written to disk
- [ ] State file was updated after each phase completion
- [ ] If session was interrupted, resumability was verified on restart
- [ ] No phase required re-reading files that were already documented

## Project Detection Accuracy

- [ ] Project type was determined using the detection rule order (mobile → desktop → game → web_app → api → library)
- [ ] Detection was based on actual file/directory evidence, not assumption
- [ ] If project spans multiple types, the primary type is noted and secondary types are documented
- [ ] Project purpose is described in terms of what the software does for its users, not just its technology

## Technology Stack Documentation

- [ ] All languages used in the project are listed with versions
- [ ] All frameworks are listed with versions and their role
- [ ] Classification is explicit: `core | infrastructure | development | testing | services | inactive | planned`
- [ ] `inactive` deps are explicitly marked — not mixed into active lists
- [ ] Build tools are documented
- [ ] CI/CD systems are documented
- [ ] Database systems are documented (if applicable)
- [ ] Third-party services are documented (if applicable)
- [ ] No dependency listed without a clear role/classification
- [ ] Version numbers come from actual config files, not guessing

## Architecture Quality

- [ ] Ledé is 3 lines: project type + 2 hardest architectural rules
- [ ] Entry points are identified and documented
- [ ] Architectural pattern is named (MVC, microservices, monolith, layered, event-driven, etc.)
- [ ] Data flow is documented from entry to output
- [ ] Inter-module communication patterns are documented
- [ ] Error handling patterns are documented
- [ ] Authentication/authorization patterns are documented (if applicable)
- [ ] Architectural decisions include rationale where discoverable
- [ ] Architecture doc matches the actual code (not the idealized version)
- [ ] `getRealUserId()` or equivalent is shown verbatim (not just described)
- [ ] All section anchors are present: `#overview`, `#entry-points`, `#data-flow`, `#authentication-patterns`, `#key-modules`, `#error-handling`, `#architectural-decisions`

## Source Tree Accuracy

- [ ] Directory tree reflects actual current state (not stale)
- [ ] Every source directory has a purpose annotation
- [ ] Key files are annotated (entry points, configs, main modules)
- [ ] Generated/vendor/build directories are excluded or clearly marked
- [ ] Tree depth matches scan level (quick: 3 levels, deep: full + source annotations, exhaustive: every file)

## Output File Completeness

- [ ] `CONTEXT.md` exists at project root (not inside `.docs/`)
- [ ] `CONTEXT.md` ledé is 3 lines with 2 HARD rules
- [ ] `CONTEXT.md` constraints in table format, one row per constraint
- [ ] `CONTEXT.md` has no "Deep Dives Available" section
- [ ] `CONTEXT.md` layer diagram is inline (not behind a link)
- [ ] `CONTEXT.md` entry points: one per topic, no redundant links to same file
- [ ] `project-overview.md` exists with ledé and classified tech stack
- [ ] `architecture.md` exists with newspaper-lede structure
- [ ] `source-tree.md` exists with annotated directory structure
- [ ] `dev-guide.md` exists with ledé and gotchas table
- [ ] `.scan-state.json` exists and reflects final completed state
- [ ] For deep_dive: `deep-dives/<area>.md` exists with all required sections
- [ ] `index.md` is removed or marked deprecated (replaced by CONTEXT.md)

## Anchor Validation

Every `#anchor` referenced in `CONTEXT.md` must resolve to an actual section header in its target doc.

**Check**: For each anchor link in `CONTEXT.md`:
1. Parse the target file path and anchor (e.g., `.docs/architecture.md#overview`)
2. Verify the target file exists
3. Verify the section header (`## Header Name`) exists in that file

**Fail mode**: If a human edits a doc and renames/removed a section header, `CONTEXT.md` links break silently. On regeneration (full_rescan), all anchors are re-validated automatically.

## Content Quality — Zero Tolerance

- [ ] NO placeholder text (e.g., "TBD", "fill in later", "TODO")
- [ ] NO vague descriptions that could apply to any project
- [ ] NO guessed content — everything is based on actual file reads
- [ ] NO sample/guess patterns — full file review only, especially in deep dives
- [ ] NO content copied from other projects or templates
- [ ] Every statement about the codebase is verifiable against actual files
- [ ] Technology versions come from actual config files
- [ ] Commands (build, test, deploy) are verified to exist in actual config

## CONTEXT.md Token Budget

- [ ] `CONTEXT.md` ≤4,000 tokens total
- [ ] Sections >1,000 tokens extracted to `deep-dives/` and linked

## Brownfield PRD Readiness

- [ ] Documentation provides enough context for an AI agent to understand the project structure
- [ ] Documentation identifies extension points where new features could be added
- [ ] Documentation notes constraints and invariants that must be maintained
- [ ] Documentation identifies areas of complexity that require careful modification
- [ ] A developer unfamiliar with the project could use this documentation to make informed changes
- [ ] Architecture documentation clearly shows where new modules would fit
- [ ] Dependency mapping supports impact analysis for proposed changes

## Final Sign-Off

After all items pass:

1. Update `.scan-state.json` with `"status": "complete"`
2. Add completion timestamp
3. Report completion to user with list of output files and their locations
