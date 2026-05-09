---
name: e2e-scaffold
description: Use when setting up E2E testing infrastructure or scaffolding end-to-end tests for any project type
quick_ref:
  purpose: "Scaffold complete E2E testing infrastructure tailored to project architecture"
  trigger: "e2e scaffold | set up e2e testing | e2e infrastructure"
  requires: "Existing test framework (run test-framework workflow first)"
  produces: "Test fixture, ScenarioBuilder, TestHelpers, AsyncAssert, example test, README"
---

# E2E Test Infrastructure Scaffold

Scaffold complete E2E testing infrastructure tailored to any project's architecture — web apps, APIs, mobile, desktop, games.

## TRIGGERS

- "e2e scaffold"
- "set up e2e testing"
- "e2e infrastructure"
- "scaffold e2e"
- User mentions needing end-to-end tests with no existing infrastructure

## PREREQUISITES

1. Test framework must exist in project (jest, vitest, pytest, xcode, etc.)
2. Application state management must be identifiable
3. No existing E2E infrastructure at target directory

If prerequisites fail → **STOP** → tell user what's missing.

## WORKFLOW

```
Step 1: ANALYZE.md  → Detect project type, state mgmt, test framework, domain entities
Step 2: GENERATE.md → Create E2E infrastructure files (write each to disk as generated)
Step 3: VERIFY.md   → Generate example test, run verification, confirm infrastructure works
```

Execute steps **sequentially**. Do not skip ahead.

## FILE INDEX

| File | Purpose |
|------|---------|
| `SKILL.md` | This entry point |
| `e2e-scaffold.yaml` | Quick reference schema |
| `ANALYZE.md` | Step 1 — Project architecture analysis |
| `GENERATE.md` | Step 2 — Infrastructure code generation |
| `VERIFY.md` | Step 3 — Example test + verification checklist |

## KEY CONCEPTS

- **Preflight validation** — Check framework exists, state manager identified, no existing E2E infra
- **Architecture-driven generation** — All generated code adapts to detected project type
- **ScenarioBuilder** — Fluent API for domain-specific test setup
- **TestHelpers** — UI interaction, API calls, input simulation (project-type appropriate)
- **AsyncAssert** — Condition waiting utilities for async state convergence
- **Write-as-you-go** — Each file written to disk as generated, not batched at end
- **Verification proof** — Must demonstrate infrastructure actually works

## PROJECT TYPES SUPPORTED

| Type | Examples |
|------|----------|
| web-app | React, Vue, Svelte, Next.js, Nuxt |
| api | Express, FastAPI, Spring Boot, Django REST |
| mobile | React Native, Flutter, Swift, Kotlin |
| desktop | Electron, Tauri, WPF, Qt |
| game | Unity, Unreal, Godot, custom engine |

## ANTI-RATIONALIZATION

| If you think... | You are wrong because... |
|-----------------|--------------------------|
| "Skip preflight validation" | Missing framework or state mgr = broken infrastructure. Always validate first. |
| "Generate code before analysis" | Architecture analysis drives all generation. Wrong detection = wrong code. |
| "Batch all file writes at end" | Write-as-you-go catches issues early. One broken file ≠ total redo. |
| "Skip verification step" | Unverified infrastructure is faith, not engineering. Run the test. |
| "Hardcode directory structure" | Structure adapts to project type. Unity ≠ Next.js ≠ Flutter. |
| "Use InputSimulator name" | TestHelpers is the generic name. Covers UI, API, input — not just input. |
| "Copy game-dev patterns verbatim" | This is generalized. Game-specific patterns replaced with project-type patterns. |
| "One ScenarioBuilder fits all" | Domain entities drive the fluent API. Different projects = different builders. |
