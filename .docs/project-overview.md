# Project Overview

## Project Type
tool-platform

## Purpose
Universal agent enforcement ecosystem that transforms documented agent protocols into live gates, state machines, and NLI-powered pattern watchers. Tool-agnostic — works with any LLM-based coding agent (OpenCode, Claude Code, Cursor).

## Primary Language
Python 3.10+

## Lede (3 lines)
```
Universal agent enforcement framework that transforms documentation into live gates.
Python state machine + NLI pattern watcher catch agent protocol violations.
Tool-agnostic — works with any LLM-based agent via YAML routing and subprocess bridges.
```

## Secondary Languages
JavaScript (Node.js 18+), YAML, Markdown

## Primary Stack
Python 3.10+ (runtime enforcement), Node.js 18+ / Transformers.js (flow-watcher NLI watcher), YAML (skill routing config), Pydantic v2 (state validation)

## Repo Identity
Public GitHub: **jtoemion/harness-engineering-skills**

## Root Config Files
- `skill-router.yaml` — Single source of truth for all skill routing decisions
- `SKILLS.yaml` — Skills address map with categories
- `INSTALL.md` — Human and AI agent installation guide
- `INTEGRATION_GUIDE.md` — How to add harness to any AGENTS.md
- `README.md` — Architecture overview, commands, flow-watcher docs
- `AGENTS.md` — Personal Antigravity config (gitignored, not public)

## Key Directories
- `harness/` — Core enforcement: SKILL.md, MISTAKES.md, SESSION_CLOSE.md, SUBAGENT_PROTOCOL.md, document-project/
- `harness/runtime/` — Live enforcement code: state.py, harness.py, conductor.py, bridge.py, mistakes.py, memory_watch.py, checkpoint.py, session_close.py, flow-watcher/, hooks/
- `browser-agent/` — Browser automation skill with football-news/, social-automation/, vault-tools/ sub-skills
- `superpowers/` — 35 skill directories including memorybank, conductor, systematic-debugging, dev-journey-log, etc.
- `karpathy-guidelines/` — Coding guidelines skill

## Classification
Multi-language tool-platform — not a web app, not a library, not an API. A framework/tool for enforcing agent workflow protocols.

## tech stack

See [technology stack](#technology-stack) above.

## technology stack

**Core runtime**
- Python 3.10+ (runtime enforcement)
- Pydantic v2 (state validation)
- PyYAML (skill routing config parsing)

**Flow-watcher (NLI pattern watcher)**
- Node.js 18+ (runtime)
- @huggingface/transformers ^4.2.0 (ONNX NLI classifier)
- Xenova/nli-deberta-v3-base (zero-shot classification model, ~250MB, downloads on first use)

**Configuration**
- YAML (skill-router.yaml, SKILLS.yaml, harness.yaml, document-project.yaml)
- Markdown (documentation, skill files)

**Testing / verification**
- Python (test scripts, post_final.py, post_v3.py, etc.)
- Playwright (browser-agent automation)
- Chrome DevTools Protocol (browser-backend)

**Inactive**
- @xenova/transformers ^2.17.1 (package listed but superseded by @huggingface/transformers)
- Chrome CDP (browser-agent backend, configured but not actively wired in flow)
- Docker (browser-agent INFRASTRUCTURE.md references it but not actively used)

**Not applicable** (no package manager lock file)
- pip/poetry/requirements.txt — no dependency lock file in repo (Python dependencies installed system-wide)
- npm/yarn/pnpm lock — no package-lock.json for the skill repo itself (only flow-watcher's own package-lock.json)