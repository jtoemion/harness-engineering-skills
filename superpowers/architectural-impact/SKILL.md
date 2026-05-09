---
name: architectural-impact
description: >
  Invoke before ANY change involving data, databases, new features, business logic, 
  API endpoints, or modifications that touch more than one layer. Use when the user 
  asks to add a feature, change a schema, create a service, build an API, or refactor 
  logic. Do NOT skip this for "small" changes — small changes cause cascading breakage 
  precisely because impact analysis was skipped.
---

# PROTOCOL: ARCHITECTURAL IMPACT & DEPENDENCY MAPPING

**CORE PHILOSOPHY — THE RESTAURANT ANALOGY:**
This application is a strict multi-tiered system. Every file has exactly one job.
Cross-contamination between layers is a bug, not a shortcut.

| Layer | Analogy | Responsibility | What It NEVER Does |
|---|---|---|---|
| **View** | Waiter / Menu | React components, HTML, rendering | Business logic, direct DB calls |
| **Controller / ViewModel** | Ticket Window | Routing, state management, orchestration | Raw data access, complex calculations |
| **Service Layer** | Chef | Business logic, calculations, rules | Direct DB calls, UI concerns |
| **DAL** | Stockroom Worker | API calls, SQL queries, DB reads/writes | Business logic, UI concerns |
| **Database** | The Shelves | Firebase, Postgres, etc. — passive storage | Nothing active |

---

## PHASE 1 — RIPPLE EFFECT ANALYSIS (MANDATORY BEFORE WRITING CODE)

You MUST complete this phase before writing a single line of implementation code.
Showing the analysis is not optional — it must be output to the user.

- [ ] Identify the request type: Schema change / New feature / Business logic / UI-only / Refactor
- [ ] For each layer, determine: Is it affected? What specifically must change?
- [ ] Output the Impact Table:

```
## ⚡ RIPPLE EFFECT ANALYSIS

| Layer              | Affected | Change Required                          |
|--------------------|----------|------------------------------------------|
| Database           | YES / NO | [specific schema, index, or collection change]  |
| DAL                | YES / NO | [specific function, query, or endpoint change]  |
| Service Layer      | YES / NO | [specific business logic change]                |
| Controller / VM    | YES / NO | [specific state or routing change]              |
| View (UI)          | YES / NO | [specific component or rendering change]        |

Execution Order: [list only the YES layers in bottom-up order]
Estimated Risk: [LOW / MEDIUM / HIGH] — [one sentence rationale]
```

- [ ] If risk is HIGH → pause and ask user to confirm before proceeding
- [ ] If upstream change detected (e.g., schema change) → flag ALL downstream layers as requiring verification even if not obviously affected

---

## PHASE 2 — EXECUTION (STRICT SEQUENCING)

Execute changes in this order. Never deviate. Never work top-down.

- [ ] **Step 1 — Database / DAL** (always first)
  - Schema migrations, index changes, new collections/tables
  - New DAL functions with dependency injection (no hardcoded connections)
  - Verify DAL is fully functional in isolation before moving up
- [ ] **Step 2 — Service Layer** (second)
  - Business logic that consumes the updated DAL
  - Pass all dependencies in from outside — never import DB clients directly
  - Verify service functions are correct before moving up
- [ ] **Step 3 — Controller / ViewModel** (third)
  - Routing, state management updates that consume the updated service
  - Verify controller handles all new states/actions before moving up
- [ ] **Step 4 — View (UI)** (always last)
  - Only UI changes that expose what the layers below now support
  - Never add UI for data that doesn't exist in the layer below yet

**Non-negotiable rule:** Do not leave the system in a broken intermediate state. 
Each layer must compile, pass its tests, and be self-consistent before the next 
layer is touched.

---

## PHASE 3 — DOCUMENTATION (MANDATORY AFTER EXECUTION)

- [ ] Open `.memory/techContext.md`
- [ ] Append a log entry:
```markdown
## [YYYY-MM-DD] [Feature/Change Name]
- Layers modified: [list]
- Schema changes: [describe or "none"]
- New data flow: [describe the path from trigger to storage]
- Dependencies introduced: [packages, services, or modules]
- Breaking changes: [describe or "none"]
```
- [ ] Open `.memory/activeContext.md` and update current state
- [ ] Trigger memorybank Phase 2 checkpoint

---

## DEPENDENCY INJECTION RULES

These apply to every Service and DAL module created or modified:

- [ ] Database connections MUST be passed in as constructor/function arguments
- [ ] API clients MUST be passed in — never instantiated inside the module
- [ ] Configuration MUST come from environment or config injection — never hardcoded
- [ ] Test doubles (mocks/stubs) MUST be substitutable via the injection interface

```typescript
// ✅ CORRECT — dependency injected
export function createUserService(db: DatabaseClient, mailer: MailerClient) {
  return {
    async createUser(data: UserInput) { ... }
  }
}

// ❌ WRONG — hardcoded dependency
export function createUser(data: UserInput) {
  const db = new FirebaseClient(process.env.FB_URL) // never do this inside a service
}
```

---

## ANTI-RATIONALIZATION TABLE

| Rationalization | Why It's Wrong |
|---|---|
| "It's just a small UI change, no analysis needed" | UI changes often need new data. Find out first. |
| "I'll just add the field to the database and update the UI" | You skipped Service and Controller. Don't. |
| "The service already handles this roughly" | "Roughly" breaks production. Verify exactly. |
| "I'll document it later" | Later never comes. Document before checkpoint. |
| "Dependency injection is overkill for this" | It's never overkill. It's the rule. |
| "I can write the View first since I know what it needs" | The View gets built last. Always. |

---

## STATE MACHINE

```
digraph architectural_impact {
  "User requests change" [shape=doublecircle];
  "Perform Ripple Effect Analysis" [shape=box];
  "Output Impact Table" [shape=box];
  "Risk HIGH?" [shape=diamond];
  "Pause: confirm with user" [shape=box];
  "Execute: DB / DAL" [shape=box];
  "Execute: Service Layer" [shape=box];
  "Execute: Controller / VM" [shape=box];
  "Execute: View (UI)" [shape=box];
  "Document in techContext.md" [shape=box];
  "Trigger memorybank checkpoint" [shape=doublecircle];

  "User requests change" -> "Perform Ripple Effect Analysis";
  "Perform Ripple Effect Analysis" -> "Output Impact Table";
  "Output Impact Table" -> "Risk HIGH?";
  "Risk HIGH?" -> "Pause: confirm with user" [label="yes"];
  "Risk HIGH?" -> "Execute: DB / DAL" [label="no"];
  "Pause: confirm with user" -> "Execute: DB / DAL" [label="confirmed"];
  "Execute: DB / DAL" -> "Execute: Service Layer";
  "Execute: Service Layer" -> "Execute: Controller / VM";
  "Execute: Controller / VM" -> "Execute: View (UI)";
  "Execute: View (UI)" -> "Document in techContext.md";
  "Document in techContext.md" -> "Trigger memorybank checkpoint";
}
```
