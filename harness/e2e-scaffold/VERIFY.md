# Step 3 — Verify Infrastructure Works

Generate an example E2E test and prove the infrastructure is functional.

## INPUT

- Generated infrastructure files from Step 2
- Analysis result from Step 1

## 1. GENERATE EXAMPLE TEST

Create `<e2e_dir>/tests/example.e2e.test.<ext>` that exercises every piece of generated infrastructure:

### What the example test must demonstrate:

| Component | Must Verify |
|-----------|-------------|
| BaseTestFixture | Setup runs, state is initialized, teardown cleans up |
| ScenarioBuilder | Fluent chaining works, `build()` applies state correctly |
| TestHelpers | At least one helper function executes without error |
| AsyncAssert | `until` or `untilState` resolves correctly for a known condition |
| Config | Config values are loaded and accessible |

### Example test structure:

```
1. Import BaseTestFixture (or extend it per framework convention)
2. Test: "E2E infrastructure smoke test"
   a. Create scenario using ScenarioBuilder with at least 2 chained calls
   b. Use a TestHelper to perform an action
   c. Use AsyncAssert to wait for a state condition
   d. Assert the final state matches expected
3. Test: "BaseFixture setup and teardown"
   a. Verify fixture.state is initialized
   a. Verify fixture.helpers is functional
   a. Verify fixture.scenario can be created
4. Test: "AsyncAssert timeout behavior"
   a. Verify that a never-resolving condition throws within configured timeout
```

The test must use **real imports** from the generated files and the project's actual test framework. No stubs.

### Language-specific naming:

| Language | File Pattern |
|----------|-------------|
| JS/TS | `example.e2e.test.ts` or `example.e2e.spec.ts` |
| Python | `test_example_e2e.py` |
| C# | `ExampleE2eTests.cs` |
| Swift | `ExampleE2eTests.swift` |
| Kotlin | `ExampleE2eTest.kt` |

## 2. GENERATE RUN SCRIPT (if needed)

If the project doesn't have an easy way to run just E2E tests, generate a run script or document the command:

```
<e2e_dir>/run-e2e.sh (or .ps1 on Windows)
- Sets any required environment variables
- Runs the test framework targeting e2e directory
- Reports pass/fail clearly
```

Only generate if no existing E2E test command exists in package.json / Makefile / etc.

## 3. VERIFICATION CHECKLIST

Run through this checklist. All items must pass.

### Pre-Run Checks

- [ ] All generated files exist at expected paths
- [ ] All generated files are syntactically valid (run linter if available)
- [ ] Imports in generated files resolve to real modules
- [ ] Test framework configuration includes E2E directory
- [ ] No type errors (run typecheck if available)

### Runtime Checks

- [ ] Example test discovered by test framework (appears in test list)
- [ ] Example test runs without import/module errors
- [ ] BaseTestFixture setup executes successfully
- [ ] BaseTestFixture teardown executes successfully
- [ ] ScenarioBuilder chaining produces expected state
- [ ] At least one TestHelper function works
- [ ] AsyncAssert resolves for a passing condition
- [ ] AsyncAssert times out correctly for a failing condition

### Post-Run Checks

- [ ] Test exits cleanly (no hung processes, no leaked resources)
- [ ] Test result is clearly reported (pass/fail)
- [ ] README.md exists and documents all generated files
- [ ] Run command documented in README

## 4. FAILURE PROTOCOL

| Failure | Action |
|---------|--------|
| Import errors | Fix import paths. Check module resolution. Re-generate affected file. |
| Setup/teardown errors | Check state manager initialization. May need mock/test doubles. |
| Test not discovered | Check test framework config. Add e2e dir to includes. |
| Helper function error | Check that helper uses correct library API for project. Fix and re-write. |
| AsyncAssert never resolves | Check timeout config. Ensure condition function is correct. |
| Hung process | Check for missing cleanup. Add timeout wrapper to test. |

After fixing any failure, re-run the full verification checklist from the top.

## 5. COMPLETION REPORT

When all checklist items pass, output:

```
✅ E2E Infrastructure Scaffolded Successfully

Project Type:    [type]
Test Framework:  [framework]
E2E Directory:   [e2e_dir]

Generated Files:
  - [path] — [purpose]
  - [path] — [purpose]
  - [path] — [purpose]
  - [path] — [purpose]
  - [path] — [purpose]
  - [path] — [purpose]
  - [path] — [purpose]

Example Test:    [pass/fail]
Run Command:     [command]

Next Steps:
  1. Write domain-specific scenarios using ScenarioBuilder
  2. Add project-specific helpers to TestHelpers
  3. Add E2E tests for critical user flows
  4. Integrate E2E runs into CI pipeline
```
