---
name: svelte
description: Svelte/SvelteKit conventions, known bugs, and fix patterns. Always load when working in any Svelte project.
version: 1.0.0
author: Megumi Kato
license: MIT
metadata:
  hermes:
    tags: [svelte, sveltekit, css, layout, known-bugs]
    related_skills: [techne, typescript, diagnose]
---

# Svelte / SvelteKit — Global

## Conventions

- **adapter-static (SPA mode):** SSR=false on all routes, no prerender unless explicitly needed
- **Dev server:** `pnpm dev --host 0.0.0.0 --port <port>` for LAN/tailnet access
- **TypeScript strict:** enabled; `@ts-check` on `.svelte` files via `svelte2tsx`
- **Svelte 5 runes:** `$state`, `$derived`, `$effect` — not the old `export let` / reactive store patterns

---

## Known Bugs

### 🔴 H-1: Gap at bottom of page (recurring)

**Symptom:** Unwanted blank space / gap at the bottom of the page. Persists after multiple CSS fixes.

**Root cause:** Svelte's SSR → client hydration transition can leave remnant margins or whitespace from removed/relocated elements. Also triggered by:
- Collapsing margins on block elements inside flex/grid containers
- `min-height: 100vh` on `<html>`/`<body>` not propagating to children
- Sticky/fixed elements with margins that overflow their container

**Fix pattern (always apply in this order):**

1. Set `min-height: 100dvh` on the root layout element — `dvh` (dynamic viewport height) handles mobile address bar correctly:
   ```css
   :global(html) { min-height: 100dvh; }
   :global(body) { min-height: 100dvh; margin: 0; }
   ```

2. On the page wrapper, prevent margin collapse:
   ```css
   .page-wrapper {
     display: flex;
     flex-direction: column;
     min-height: 100dvh;
     overflow: hidden; /* kills margin collapse */
   }
   ```

3. If the gap is from a bottom-most element with margin-bottom inside a flex child:
   ```css
   .page-wrapper > *:last-child { margin-bottom: 0; }
   ```

4. Check for `padding-bottom` on scrollable containers bleeding into layout:
   ```css
   main { padding-bottom: env(safe-area-inset-bottom); }
   ```

**Why it keeps coming back:** Each new page/component added to the layout introduces its own margin stack. The fix must be in the root layout once, not per-page.

---

## Svelte 5 Patterns

### `$state` array + helper mutation

When passing a `$state` array to a helper that mutates it, the helper must receive the updater function:

```ts
// Broken — splice mutates local copy, not $state
function removeTag(tags: string[], index: number) {
  tags.splice(index, 1);
}

// Correct — functional update
function removeTag(tags: string[], index: number, setTags: (t: string[]) => void) {
  const updated = [...tags];
  updated.splice(index, 1);
  setTags(updated);
}

// In component:
<button onclick={() => removeTag(myTags, i, (t) => myTags = t)}>×</button>
```

### `$state` object spread

```ts
// Correct — always create new reference
let item = $state({ ...originalItem });
item.name = 'new name'; // triggers reactivity
```

### `$derived` with complex logic

```ts
const filtered = $derived.by(() => {
  return items.filter(item => item.active);
});
```

---

## SvelteKit Route Guard (dev-only routes)

For routes that should only be accessible in development:

```ts
import { dev } from '$app/environment';
import { goto } from '$app/navigation';

if (!dev) goto('/');
```

Place at the top of `<script>` in `+page.svelte`.

---

## Skills to Load Alongside

| Task | Skill |
|---|---|
| Bug diagnosis | `software-development/diagnose` |
| TypeScript errors | `techne` → `skills/typescript.md` |
| Architecture review | `software-development/codebase-deep-audit` |
| Test review | `harness/test-review` |

---

## Changelog

- **v1.0.0** — Initial. Gap-at-bottom fix pattern, $state array mutation, dev-only route guard.
