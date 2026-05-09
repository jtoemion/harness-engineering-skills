# Step 2 — Generate E2E Infrastructure

Generate all E2E infrastructure files based on the analysis from ANALYZE.md. Write each file to disk as it is generated (write-as-you-go).

## INPUT

Receives the analysis result from Step 1:
```
type, framework, test_framework, test_pattern, test_dir,
state_manager, state_shape, state_mutate, state_observe,
domain_entities, input_system, async_pattern, language, e2e_dir
```

## DIRECTORY STRUCTURE

Create the E2E directory structure. Adapt to project type conventions:

| Project Type | E2E Directory |
|-------------|---------------|
| web-app | `e2e/` at project root |
| api | `e2e/` at project root |
| mobile | `e2e/` at project root |
| desktop | `e2e/` at project root |
| game (Unity) | `Assets/Tests/PlayMode/` |
| game (Unreal) | `Tests/E2E/` |
| game (Godot) | `tests/e2e/` |

### Standard Structure
```
<e2e_dir>/
├── fixtures/
│   └── BaseTestFixture.<ext>
├── builders/
│   └── ScenarioBuilder.<ext>
├── helpers/
│   ├── TestHelpers.<ext>
│   └── AsyncAssert.<ext>
├── config/
│   └── e2e.config.<ext>
└── tests/
    └── (example test generated in VERIFY.md)
```

Language extension `<ext>` determined by analysis: `.ts`, `.js`, `.py`, `.cs`, `.swift`, `.kt`, `.rs`

## FILE GENERATION

Generate files in this order. Write each to disk before starting the next.

### 1. Config — `config/e2e.config.<ext>`

Generate configuration based on project type:

```
Contents must include:
- Default timeout values (adapt per project type)
  - web-app/api: 30000ms (browser/HTTP)
  - mobile: 60000ms (device interaction)
  - desktop: 15000ms (app interaction)
  - game: 10000ms (frame-based, faster)
- Environment configuration (base URL, API endpoint, app path)
- Feature flags for E2E (mock external services, skip auth, etc.)
- Retry configuration
- Screenshot/capture on failure settings (if applicable)
```

### 2. BaseTestFixture — `fixtures/BaseTestFixture.<ext>`

Generate base test fixture that:

- **Imports** the test framework's describe/it/test/setup/teardown primitives
- **Setup** (beforeAll/beforeEach): Initializes application state to a known baseline
  - Uses detected state manager to reset state
  - For APIs: starts test server or configures test client
  - For web: launches browser/page context (if playwright/cypress)
  - For games: loads empty/initial scene
  - For mobile: launches app on device/simulator
- **Teardown** (afterAll/afterEach): Cleans up state, closes connections
- **Exposes** convenience properties: `state` (current app state), `helpers` (TestHelpers instance), `scenario` (ScenarioBuilder instance)
- **Loads** config from e2e.config

The fixture must use the project's actual test framework API — not a generic abstraction that doesn't compile.

### 3. AsyncAssert — `helpers/AsyncAssert.<ext>`

Generate async assertion utilities:

```
Core functions (adapt names to language convention):
- until(conditionFn, timeout?, interval?) → poll until condition returns truthy
- untilEqual(actualFn, expected, timeout?, interval?) → poll until value equals expected
- untilMatch(actualFn, regex, timeout?, interval?) → poll until value matches pattern
- untilNotNull(actualFn, timeout?, interval?) → poll until value is not null/undefined
- untilState(selector, expected, timeout?) → poll until state selector returns expected
- rejects(fn, timeout?) → assert function throws/rejects within timeout
- eventually(fn, timeout?) → assert function succeeds within timeout (retry on error)

Behavior:
- Default interval: 100ms (50ms for games, 200ms for mobile)
- Default timeout: from e2e.config
- On timeout: throw descriptive error with last actual value
- On success: return the satisfying value
- Language-appropriate async pattern (Promise for JS, async/await for Python, etc.)
```

### 4. TestHelpers — `helpers/TestHelpers.<ext>`

Generate test helpers appropriate to project type:

| Project Type | Helper Functions |
|-------------|-----------------|
| web-app | `navigate(path)`, `click(selector)`, `fill(selector, value)`, `selectOption(selector, value)`, `waitForSelector(selector)`, `takeScreenshot(name)` |
| api | `request(method, path, body?, headers?)`, `authenticate(credentials)`, `get(path)`, `post(path, body)`, `put(path, body)`, `delete(path)`, `assertStatus(response, expected)` |
| mobile | `tap(element)`, `typeText(element, text)`, `scroll(direction, distance)`, `swipe(start, end)`, `navigateTo(screen)`, `waitForElement(element)` |
| desktop | `launchApp()`, `clickMenu(path)`, `pressShortcut(keys)`, `typeInto(field, text)`, `waitForWindow(title)`, `closeDialog()` |
| game | `pressKey(key)`, `clickAt(x, y)`, `loadScene(name)`, `advanceFrames(n)`, `getEntity(id)`, `simulateInput(action, params)` |

All helpers must:
- Use the project's actual UI/input/api libraries (detected in analysis)
- Return values or promises appropriate to async_pattern
- Include error messages with context (what was attempted, what failed)

### 5. ScenarioBuilder — `builders/ScenarioBuilder.<ext>`

Generate a fluent API builder for constructing test scenarios:

```
Structure:
- Constructor takes BaseTestFixture reference
- Each method returns `this` for chaining (except terminal `build()`)
- Domain-specific methods generated from detected domain_entities

For each domain entity, generate:
- `with<Entity>(params)` — creates/sets up entity with given params
- `without<Entity>(id)` — ensures entity does not exist
- `having<Entity>State(id, state)` — sets entity to specific state

General methods:
- `withState(partialState)` — merge partial state into app state
- `withConfig(overrides)` — override E2E config for this scenario
- `withUser(role)` — authenticate as user with given role
- `build()` — apply all accumulated setup, return fixture reference

Example (web-app with entities: Cart, Product, User):
  scenario
    .withUser({ role: 'customer' })
    .withProduct({ id: 'p1', name: 'Widget', price: 9.99 })
    .withCart({ items: ['p1'] })
    .build()
```

### 6. README — `README.md`

Generate a README at `<e2e_dir>/README.md` with:
- Overview of generated infrastructure
- File descriptions
- How to write a new E2E test (using BaseTestFixture)
- How to use ScenarioBuilder (with example)
- How to use TestHelpers (with examples per project type)
- How to use AsyncAssert (with examples)
- How to run E2E tests (command)
- Configuration options

## GENERATION RULES

1. **Use actual imports** — Import real modules from the project's dependencies, not invented ones
2. **Match language conventions** — Python: snake_case, JS: camelCase, C#: PascalCase
3. **Match framework API** — Use the actual test framework's assertion/style API
4. **Every file must compile** — Generated code must be syntactically valid for the detected language/framework
5. **Write to disk immediately** — After generating each file, write it. Do not batch.
6. **Track generated files** — Maintain a list of all files written with their paths
