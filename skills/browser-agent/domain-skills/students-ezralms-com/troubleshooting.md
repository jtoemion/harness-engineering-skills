# Troubleshooting

## login recipe

### Wrong PIN field selector

**First seen:** 2026-04-23
**Recipe:** login
**Failed step:** `[wait] input[name=pin]`

**Symptom:** `input[name=pin]` returns null. The PIN field does not have a `name` attribute.

**Root cause:** Site uses `#pin` (id attribute) not `input[name=pin]`.

**Fix:** Use `#pin` as selector instead.

**Status:** Verified fixed

---

### PIN modal overlay blocks button click

**First seen:** 2026-04-23
**Recipe:** login
**Failed step:** `[click] button[type=submit]` (after typing PIN)

**Symptom:** A modal overlay with "Enter the 6-digit PIN provided by your tutor" appears after PIN entry. The modal intercepts pointer events and blocks button clicks.

**Root cause:** After typing PIN, a modal dialog opens rather than a direct form submission. The form submit button is behind the overlay.

**Fix:** After typing PIN, use `[press_enter] #pin` to submit instead of clicking a button. The PIN field fires form submit on Enter key.

**Status:** Verified fixed

---

### Login is two-step (username -> PIN)

**Quirk:** The login flow is two separate pages rendered in a modal overlay:
1. First modal: enter username/identifier field
2. After submit: PIN field appears in the same/different modal
3. Press Enter on PIN field completes login

**Selector for username:** `#identifier`
**Selector for PIN:** `#pin` (id, not name)

**No fix needed** — just documented for future recipes.

---

### Framework: React + Tailwind

The site uses React with Tailwind CSS classes. React hydration means elements may not be immediately available after page load — always use `[wait]` before interacting.

---

## General Quirks

### Unicode encoding issues on Windows

Recipe files must use ASCII ` -> ` as the step separator (not Unicode `→`). The Windows console (cp1252) crashes on Unicode output.

**Fix:** Always use ` -> ` in recipe files.

### wait_url uses target (not value)

The `[wait_url]` step format is `[wait_url] <url-substring>`. The URL substring goes in the target position, value is unused.

Example: `[wait_url] students.ezralms.com` — waits until URL contains "students.ezralms.com"

---

## Status

| Issue | Status |
|-------|--------|
| PIN selector wrong | Fixed |
| PIN modal blocks click | Fixed |
| Unicode `->` crash | Fixed |
| `wait_url` param bug | Fixed |
| heal import path | Fixed |
