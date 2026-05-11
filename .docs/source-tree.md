# Source Tree

## Root level (configs and docs)

```
├── .docs/                          # Generated documentation output (gitignored)
│   ├── .scan-state.json            # Enforcer state (harness-owned)
│   ├── .scan-state.lock             # Lock file for enforcer
│   ├── project-overview.md         # Phase 1-2 output: type, purpose, tech stack
│   └── architecture.md             # Phase 3 output: patterns, data flow, decisions
├── .gitignore                       # Git ignore rules (transient files, cache)
├── AGENTS.md                        # Personal Antigravity master config (gitignored)
├── detect-mode.bat / detect-mode.sh # Mode detector (QUICK vs FULL)
├── document-project-OPENCODE.md     # document-project skill integration for OpenCode
├── INSTALL.md                       # Human and AI agent install guide
├── INTEGRATION_GUIDE.md             # How to add harness to any AGENTS.md
├── README.md                        # Architecture overview, commands, flow-watcher docs
├── SKILLS.yaml                      # Skills address map with categories
├── skill-router.yaml                # Single source of truth for routing decisions
└── SUBAGENT_BRIEF.md                # Transient subagent brief (gitignored)
```

## browser-agent/ — Browser automation skill

Browser automation via Playwright + Chrome DevTools. Main use: scraping football news and social media (Twitter/X, Bluesky) into Obsidian vault.

```
browser-agent/
├── SKILL.md                         # Main browser-agent skill definition
├── ASSETS_SCRAPING.md              # Football asset scraping workflow
├── DESIGN.md                        # Design decisions and architecture
├── INFRASTRUCTURE.md                # Infrastructure reference (Docker, etc.)
├── _global-failures.yaml            # Known failure modes and recovery patterns
├── extract_images.py                # Image extraction utility
├── final_post.py, post_final.py    # Posting scripts (deprecated versions)
├── post_liverpool.py, post_v2.py, post_v3.py, post_working.py  # Iteration history
├── social_post.py                   # Social media posting entry point
├── _debug_*.png                     # Debug screenshots (transient, gitignored)
├── .env, .env.example               # Secrets (gitignored), template
├── _backends/                       # Browser automation backends
│   ├── chrome_backend.py           # Chrome CDP-based backend
│   ├── playwright_backend.py       # Playwright backend (in progress)
│   ├── selector_parser.py          # CSS selector parsing utilities
│   └── CHROME_BACKEND.md / CHROME_BACKEND_TEST.md
├── _tools/                          # Browser tools / recipes
│   ├── heal.py                      # Self-healing selector recovery
│   ├── map_site.py                 # Site mapping tool
│   ├── run_recipe.py               # Recipe runner
│   ├── scrape_articles.py           # Article scraping tool
│   ├── self_test.py                 # Self-test / health check
│   ├── demo_chrome_backend.py       # Demo script for Chrome backend
│   ├── fetch_tweets.py              # Tweet fetching utility
│   └── news_signals.yaml           # Football news signal sources
├── domain-skills/                   # Per-site skill definitions (40+ football news sites)
│   ├── football-news-sources.md     # Master list of all sources
│   ├── 90min/, abola/, ap-sports/, as-spain/, bbc-sport/, bleacher-report/,
│   ├── corriere-dellosport/, de-telegraaf/, espn-fc/, espn-soccer/, fbref/,
│   ├── fifa/, football-italia/, football365/, fotbollskanalen/,
│   ├── gazzetta-dello-sport/, goal/, guardian-football/, kicker/, lequipe/,
│   ├── marca/, nos-sport/, opta/, planet-football/, record-pt/, reuters-sports/,
│   ├── sky-sports/, sofascore/, sport-bild/, sport-spain/, sportsmole/,
│   ├── squawka/, statsbomb/, the-athletic/, thesetpieces/, transfermarkt/,
│   ├── tuttosport/, uefa/, whoscored/, x-com/, students-ezralms-com/
│   └── (each contains nav.md + _meta.yaml; some have selectors.md)
├── entities/                        # Named entity management for football content
│   ├── entity_manager.py           # Entity registry manager
│   ├── registry.yaml               # Known entities (players, clubs, competitions)
│   ├── scan_news.py                 # News scanner for entity mentions
│   └── check_missing.py            # Find missing entity data
├── football-news/                   # Football news scraping skill
│   ├── SKILL.md, INFRASTRUCTURE.md, FUTURE_IMPROVEMENTS.md
│   ├── news-tracker.py / news-tracker.json   # News tracking state
│   ├── init-tracker.py             # Tracker initialization
│   ├── score-cache.yaml            # Live score caching
│   ├── news-value.yaml             # News value scoring matrix
│   ├── tools.py                    # News scraping tools
│   ├── _AGENT_GUIDE.md             # Agent guidance for this skill
│   └── docs/                       # Plans and design docs
├── social-automation/               # Social media posting skill
│   └── SKILL.md
├── vault-tools/                     # Obsidian vault tooling
│   └── SKILL.md
├── Knowledgebase/                   # Reference knowledge (Obsidian notes)
│   ├── football-news-scraping-workflow.md
│   ├── obsidian-*-templates.md      # Obsidian template files
│   └── tpl-*.md                     # Template files
└── docs/                            # Implementation plans
    └── plans/
```

## harness/ — Core enforcement system

The main runtime enforcement ecosystem. All Python code is in harness/runtime/.

```
harness/
├── SKILL.md                         # Harness skill index
├── SESSION_CLOSE.md                 # Session close documentation
├── MISTAKES.md                      # Cross-project mistake tracking
├── SUBAGENT_PROTOCOL.md            # Subagent delegation rules
├── ATOMIC_CLOSE.md                  # Atomic session close design
├── BOOT_SEQUENCE.md                # Full boot sequence reference
├── COLD_START.md                    # Full mode cold start procedure
├── HARNESS_REVIEW_CHECKLIST.md     # Self-review checklist
├── HARNESS_STATE.md                 # State machine documentation
├── MEMORY_LIFECYCLE.md             # .memory/ lifecycle management
├── ITERATIVE_LEARNING.md            # ILL capture → synthesis → promotion
├── MISTAKES_TRACKING.md            # Mistake tracking protocol
├── OBSIDIAN_GITIGNORE              # Obsidian vault .gitignore template
├── VAULT_SCHEMA.md                  # Memory vault schema
├── harness.yaml                     # Harness runtime configuration
├── runtime/                        # ★ LIVE ENFORCEMENT CODE ★
│   ├── __init__.py                # Exports: detect_mode, init_state, read_state, write_state
│   ├── harness.py                  # ★ Master CLI entry point (9 commands)
│   ├── state.py                    # Pydantic state model, atomic writes, mode detection
│   ├── conductor.py               # YAML routing engine (skill-router.yaml)
│   ├── bridge.py                   # Python↔Node.js subprocess (WatchBridge)
│   ├── mistakes.py                 # MISTAKES.md auto-read/write
│   ├── memory_watch.py             # .memory/ staleness checker
│   ├── checkpoint.py               # 12-step checkpoint pipeline
│   ├── session_close.py           # 13-step resumable session close
│   ├── .gitignore                  # Runtime gitignore (state file, etc.)
│   ├── .harness-state.json        # Live state (gitignored)
│   ├── temp/                       # Temp working directory (gitignored)
│   ├── flow-watcher/              # NLI pattern watcher
│   │   ├── flow-watcher.js         # ★ 12-pattern NLI watcher (Transformers.js)
│   │   ├── package.json            # @huggingface/transformers, @xenova/transformers
│   │   ├── package-lock.json
│   │   ├── node_modules/           # (not tracked by root .gitignore)
│   │   └── .cache/                 # ONNX model cache (gitignored)
│   └── hooks/                     # Git enforcement
│       ├── pre-commit              # Block commit if session not closed
│       └── install_hooks.py        # Hook installer
├── document-project/               # Project documentation skill
│   ├── SKILL.md                    # Skill protocol (enforce.py is mandatory)
│   ├── enforce.py                  # Phase enforcer with state machine + integrity hash
│   ├── conductor.py               # Phase conductor orchestrator
│   ├── document-project.yaml       # Skill configuration
│   ├── FULL_SCAN.md               # Human reference: full scan phases
│   ├── DEEP_DIVE.md               # Human reference: deep dive phases
│   ├── CHECKLIST.md               # Human reference: validate checklist
│   └── AGENTS.md                  # Agent constraints for this skill
├── e2e-scaffold/                   # End-to-end test scaffolding skill
│   ├── SKILL.md, ANALYZE.md, GENERATE.md, VERIFY.md
│   └── e2e-scaffold.yaml
├── project-context/                # project-context.md generator skill
│   ├── SKILL.md, GENERATE.md, UPDATE.md
│   ├── project-context.yaml
│   └── project-context-template.md
├── test-review/                     # Test quality review skill
│   ├── SKILL.md, REVIEW_DIMENSIONS.md, REVIEW_PROCESS.md
│   ├── FINDINGS_TEMPLATE.md
│   └── test-review.yaml
├── workflow-builder/               # Workflow skill builder / converter
│   ├── SKILL.md, BUILD_PROCESS.md, CONVERT_PROCESS.md, QUALITY_ANALYSIS.md
│   └── workflow-builder.yaml
└── MEMORY_TEMPLATE/               # .memory/ file templates
    ├── T-activeContext.md, T-dashboard.md, T-decision.md,
    ├── T-mistake.md, T-pattern.md, T-progress.md,
    ├── T-projectbrief.md, T-session.md, T-systemPatterns.md, T-techContext.md
```

## karpathy-guidelines/ — Coding guidelines skill

Single skill file for reducing common LLM coding mistakes.

```
karpathy-guidelines/
└── SKILL.md                         # Behavioral guidelines for writing/refactoring code
```

## superpowers/ — 35 skill directories

Imported from the superpowers project (github.com/obra/superpowers). Each is a self-contained skill.

```
superpowers/
├── architectural-impact/            # Architectural impact analysis before changes
│   └── SKILL.md
├── brainstorming/                   # Creative work before implementation
│   └── SKILL.md
├── building-vault-cli-tools/        # Python CLI tools for Obsidian vault
│   └── SKILL.md
├── conductor/                       # Multi-skill orchestration router
│   ├── SKILL.md, conductor.yaml
│   └── PHASE1_INTENT.md, PHASE2_PIPELINE.md, PHASE3_PROPOSAL.md, PHASE5_EXECUTION.md
├── dev-journey-log/                 # DEVELOPMENT_JOURNEY.md + FEATURE_MAP.md logging
│   ├── SKILL.md
│   ├── DEVELOPMENT_JOURNEY.example.md
│   └── FEATURE_MAP.example.md
├── dispatching-parallel-agents/     # Parallel subagent dispatch
│   └── SKILL.md
├── executing-plans/                 # Execute written implementation plans
│   └── SKILL.md
├── finishing-a-development-branch/  # Merge, PR, or cleanup decisions
│   └── SKILL.md
├── frontend-avant-garde/            # Senior frontend architect persona
│   └── SKILL.md
├── ill-synthesis/                   # ILL captures → pattern analysis → promotion
│   ├── SKILL.md
│   └── PHASES/ (01_gather.md through 06_archive.md)
├── knowledge-graph/                 # Cross-project pattern analysis
│   ├── SKILL.md
│   └── knowledge-graph.yaml
├── memorybank/                      # Autonomous memory bank lifecycle (FULL mode)
│   ├── SKILL.md, memorybank.yaml
│   ├── COLD_START.md, SESSIONS_SCHEMA.md
│   └── PHASE1_BOOT.md, PHASE2_CHECKPOINT.md, PHASE3_SUBCOMMAND.md
├── receiving-code-review/           # Process incoming code review feedback
│   ├── SKILL.md, EXAMPLES.md, PUSHBACK.md, RESPONSE_PATTERN.md
│   └── receiving-code-review.yaml
├── requesting-code-review/          # Submit work for review
│   ├── SKILL.md
│   └── code-reviewer.md
├── retrospective/                   # Post-pipeline learning extraction
│   └── SKILL.md
├── scope-guard/                    # Scope creep detection
│   └── SKILL.md
├── session-graph/                   # Session close with graph awareness
│   ├── SKILL.md
│   └── session-graph.yaml
├── subagent-driven-development/    # Subagent delegation with two-stage review
│   ├── SKILL.md, subagent-driven-development.yaml
│   ├── spec-reviewer-prompt.md, implementer-prompt.md, code-quality-reviewer-prompt.md
│   └── SUBAGENT_PROTOCOL.md
├── systematic-debugging/            # Root-cause-first debugging protocol
│   ├── SKILL.md, systematic-debugging.yaml
│   ├── PHASE1_ROOT_CAUSE.md through SUPPORTING.md
│   └── test-pressure-*.md, CREATION-LOG.md, defense-in-depth.md, etc.
├── test-driven-development/        # Write tests before implementation
│   ├── SKILL.md, test-driven-development.yaml
│   ├── RED_GREEN_REFACTOR.md, RATIONALIZATIONS.md, testing-anti-patterns.md
├── ultrathink-mode/                 # Exhaustive multi-dimensional reasoning trigger
│   └── SKILL.md
├── using-git-worktrees/            # Isolated git worktree creation
│   ├── SKILL.md, using-git-worktrees.yaml
│   └── CREATION_STEPS.md, DIRECTORY_SELECTION.md, SETUP_AUTO_DETECT.md
├── using-superpowers/              # How to find and use skills
│   └── SKILL.md
├── vault-ops/                      # Core Obsidian vault operations
│   ├── SKILL.md
│   └── vault-ops.yaml
├── verification-before-completion/  # Evidence-based completion verification
│   └── SKILL.md
├── writing-plans/                  # Write spec before multi-step tasks
│   └── SKILL.md
└── writing-skills/                  # TDD process for creating new skills
    ├── SKILL.md, testing-skills-with-subagents.md
    ├── anthropic-best-practices.md, persuasion-principles.md
    ├── render-graphs.js, graphviz-conventions.dot
    └── examples/CLAUDE_MD_TESTING.md
```

## Key entry points

| File | Role |
|---|---|
| `harness/runtime/harness.py` | Master CLI: boot, gate, verify-done, checkpoint, close, mistakes, status |
| `harness/runtime/state.py` | State model (Pydantic), atomic writes, mode detection |
| `harness/runtime/bridge.py` | WatchBridge: Python↔Node.js subprocess for NLI watcher |
| `harness/runtime/flow-watcher/flow-watcher.js` | 12-pattern NLI watcher via Transformers.js ONNX |
| `harness/document-project/enforce.py` | Phase enforcer with integrity hash validation |
| `browser-agent/social_post.py` | Social media posting entry point |
| `browser-agent/entities/entity_manager.py` | Named entity management |
| `browser-agent/football-news/news-tracker.py` | Football news tracking state |