# Step 1 — Analyze Project Architecture

Before generating any code, analyze the project to detect architecture. All generated infrastructure depends on this analysis being correct.

## PREFLIGHT VALIDATION

Run these checks **in order**. Stop on first failure.

### Check 1: Test Framework Exists
```
Search for:
- package.json → jest, vitest, mocha, playwright, cypress, detox
- requirements.txt / pyproject.toml → pytest
- *.csproj → NUnit, Xunit
- *.xcodeproj → XCTest
- CMakeLists.txt / Makefile → catch2, gtest
- engine-specific → Unity Test Framework, Unreal Automation, Godot GUT
```

**FAIL:** "No test framework detected. Install a test framework first, then re-run."

### Check 2: State Manager Identified
```
Search for:
- package.json → redux, zustand, mobx, pinia, vuex, effector
- Source code → Context providers, store patterns, state classes
- Python → dataclasses, pydantic models, state modules
- Game → GameState, GameManager, Scene management patterns
- API → Database state, session state, cache state
```

**FAIL:** "No application state management detected. Identify or create a state management pattern first."

### Check 3: No Existing E2E Infrastructure
```
Search for:
- e2e/ directory with test files
- Tests/PlayMode/ (Unity)
- cypress/ directory
- playwright/ directory
- __e2e__/ directory
- Files matching pattern: *.e2e.test.*, *.e2e.spec.*
```

**WARN (not fail):** "Existing E2E infrastructure found at [path]. Scaffold will create new infrastructure alongside. Confirm with user if they want to replace."

## ARCHITECTURE ANALYSIS

### 1. Detect Project Type

| Signal | Project Type |
|--------|-------------|
| `package.json` + react/vue/svelte/next/nuxt | web-app |
| Express/FastAPI/Flask/Spring + routes/controllers + no UI framework | api |
| react-native/flutter/expo + mobile manifest | mobile |
| electron/tauri + desktop manifest | desktop |
| Unity/Unreal/Godot project files | game |
| Cargo.toml + no web framework | desktop (Rust) |
| None of above | Ask user to specify |

### 2. Detect Test Framework & Patterns

Determine:
- **Framework name and version**
- **Test file location convention** (`__tests__/`, `tests/`, `spec/`, `Tests/`)
- **Test file naming convention** (`*.test.js`, `*_test.py`, `*Tests.cs`)
- **Config file location** (`jest.config.*`, `vitest.config.*`, `pytest.ini`)
- **Async pattern** (async/await, callbacks, coroutines, promises)

### 3. Detect State Management

Determine:
- **State manager type** (store, context, service, manager class, database)
- **State shape** (read key source files to identify top-level state structure)
- **State mutation method** (dispatch, setters, methods, API calls)
- **State observation method** (selectors, subscriptions, getters, hooks)

### 4. Detect Domain Entities

Identify the top 3-5 domain entities by:
- Reading models/entities/types directories
- Reading API route handlers or controller files
- Reading state shape keys
- Reading main feature module names

### 5. Detect Input/UI System

| Project Type | What to detect |
|-------------|---------------|
| web-app | Component library, form handling, routing library |
| api | HTTP client library, auth mechanism, content type |
| mobile | Navigation library, component toolkit, gesture handler |
| desktop | Window manager, menu system, IPC mechanism |
| game | Input system, scene/loader, UI framework |

## ANALYSIS OUTPUT

After analysis, produce this structured result (in-memory, not written to disk):

```
Project Analysis:
  type: [web-app | api | mobile | desktop | game]
  framework: [name + version]
  test_framework: [name + version]
  test_pattern: [glob pattern for test files]
  test_dir: [conventional test directory]
  state_manager: [type + name]
  state_shape: [top-level keys/structure]
  state_mutate: [how state changes]
  state_observe: [how state is read]
  domain_entities: [list of 3-5 entities]
  input_system: [detected UI/input approach]
  async_pattern: [async/await | callbacks | etc]
  language: [primary language]
  e2e_dir: [recommended E2E test directory path]
```

Pass this result to GENERATE.md.

## FAILURE HANDLING

| Failure | Action |
|---------|--------|
| No test framework | Tell user to install one. Suggest common options for project type. |
| No state manager | Ask user to identify state management. Offer to scan more broadly. |
| Ambiguous project type | Present detected signals. Ask user to confirm type. |
| Multiple test frameworks | Ask user which to target for E2E. Prefer the one with E2E support. |
