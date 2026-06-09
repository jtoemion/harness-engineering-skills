---
name: opencode-build/references/identity-field-completeness
description: Field-completeness checklist for identity/RBAC tasks — prevents silent undefined values in identity blocks.
---

# Identity / RBAC Field-Completeness Checklist

When a task involves identity objects, auth tokens, or optional parameters on public functions, run this checklist BEFORE writing implementation.

## Why

Optional parameters on public functions silently accept `undefined` fields. If `studentIdentity.name` is `null`, the output renders as `"Student: null (STU-001)"` — silently wrong, no crash, no test failure on existing suite.

## Checklist

```
1. Identify the identity/auth object shape
   - List every field: studentId, name, class, role, authToken, scopes, etc.
   - Which fields are required vs optional?

2. Audit call sites
   - For each call site, which fields are guaranteed populated?
   - Which fields come from userProfile (may be null)?

3. Missing-field simulation
   - If name is null → what does the identity block look like?
   - If class is null → what does the output look like?
   - Is the result silently wrong or does it crash?

4. Safe defaults or validation
   - Add ?? 'Unknown' defaults for display fields
   - Add validation that logs a warning if critical fields are absent
   - Never silently render "null" or "undefined" in output

5. Explicit test for missing-field path
   - At least one test per identity field that verifies behavior when field is absent
   - e.g., buildChatSystemPrompt('student', { studentId: 'X', name: null, class: '9A', role: 'student' })
   - Assert the output handles null gracefully (not "Student: null")
```

## Real Example (Track B — studentIdentity)

```
Problem: studentIdentity.name sourced from displayName ?? nickname ?? 'Unknown'
         studentIdentity.class sourced from studentDetails?.grade ?? 'Unknown'
         No test verified what happens when both are null.

Fix applied:
- Default fallback to 'Unknown' in FAB (already safe)
- Added explicit identity-block test asserting 'STU-001' / 'Andi' / '9A' present
- But: still no test for the null path — future gap
```

## Anti-Pattern (never do this)

```ts
// Silent null rendering — no crash, no test fails, wrong output
const identityBlock = `[Identity] Student: ${studentIdentity.name} (${studentIdentity.studentId})`;

// Wrong output when name is null:
// [Identity] Student: null (STU-001)
```

## Correct Pattern

```ts
const name = studentIdentity.name ?? 'Unknown';
const className = studentIdentity.class ?? 'Unknown';
const identityBlock = `[Identity] Student: ${name} (${studentIdentity.studentId}), Class: ${className}`;
```

## When to Apply

- Task adds `StudentIdentity` or similar identity object
- Task adds optional parameter to a public function that affects output
- Task touches auth tokens, RBAC roles, or session context
- Task involves `userProfile` extraction in a UI component